################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: crop.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Andy Achenreiner, achenreiner@wisc.edu

This module needs the following inputs in order to operate correctly:

    "latitude": 43.332708

    These are attributes of a crop type that need to be specified in the json input
    file. The values on the right are just examples from a corn crop type.

        "grow_years": [2009],
        "repeat": 1,
        "planting_date": 121,
        "harvest_date": 319

    From the weather class, the following will be needed:
        T_min
        T_max
        radiation
        T_avg

    From the soil class, the following will be needed:
        soil_layers

        And the following attributes of a soil layer:
            bottomDepth
            Eo_sum = Sum of the Eo values leading up to today
            trans_max
            NO3
            labileP
            soil_water
            fcWater
            wiltingWater
"""
################################################################################

from math import acos, asin, sin, tan, pi
from . import heat_units, leaf_area_index, root_development, biomass, yields, \
    phosphorus_uptake, nitrogen_uptake, transpiration, growth_constraints
from RUFAS import util


# -------------------------------------------------------------------------------
# Function: daily_crop_routine
# -------------------------------------------------------------------------------
def daily_crop_routine(crop, weather, time, soil):
    T_min = weather.T_min[time.year - 1][time.day - 1]
    T_max = weather.T_max[time.year - 1][time.day - 1]

    # Current crop is set at the beginning of the year in annual_crop_routine
    crop_type = crop.current_crop

    # If no crop is being grown, current crop will be named 'null'. The routine
    # is skipped in this case
    if crop_type.crop_name != 'null':

        # in_dormancy is a method that determines whether the current date is
        # in the dormant period
        if not in_dormancy(crop, time):

            # This is different than the crop-specific is_dormant flag that
            # indicates whether the current crop is dormant. The only time
            # when this flag would be true when we are not in dormancy (the
            # previous check) is the first day outside of the dormant period.
            # In this case, we calculate when it will be warm enough for the
            # perennial to start growing
            if crop_type.is_dormant:
                calculate_start_growth_date(crop_type, weather, time)

            crop_type.is_dormant = False

            # Planted is a boolean that indicates the status of a present plant,
            # outside of the dormant period when it is warm enough to grow. It
            # helps us to determine whether there is a plant present when
            # dormancy is entered
            if crop_type.start_date <= time.day <= crop_type.harvest_date:
                crop_type.planted = True

            # Runs the crop growth routines
            # The order in which these are called matters because some of the later
            # update_all calls depend on values calculated earlier.

            if crop_type.planted and time.day >= crop_type.start_date:

                # print(time.year, time.day)

                heat_units.update_all(crop_type, T_min, T_max)

                root_development.update_all(crop_type)

                # transpiration.update_all(crop_type, soil, time)

                nitrogen_uptake.update_all(crop_type, soil)

                phosphorus_uptake.update_all(crop_type, soil)

                growth_constraints.update_all(crop_type, time, weather, soil)

                leaf_area_index.update_all(crop_type, time)

                biomass.update_all(crop_type, time, weather)

        # The dormancy_routine only occurs on the first day of dormancy if there
        # is a crop present. This is indicated by the first time in_dormancy is true
        # but is_dormant is false and there is a crop planted
        elif not crop_type.is_dormant and crop_type.planted:
            dormancy_routine(crop_type, soil)

        if crop_type.planted:
            yields.update_all(crop_type, time, soil)

        if time.day == crop_type.harvest_date + 1:
            crop_type.yield_actual = 0


# -------------------------------------------------------------------------------
# Function: annual_crop_routine determines the current crop and whether it is
# a kill year for that crop
# -------------------------------------------------------------------------------
def annual_crop_routine(crop, time):

    # current crop is set to the next crop in the regimen
    crop.current_crop = crop.grow_regimen[time.year - 1]

    crop.current_crop.kill_year = is_kill_year(crop, time)

    # If no crop is currently growing, is_dormant is set to true so that
    # calculate_start_date is called the first day out of dormancy L 111
    if not crop.current_crop.planted:
        crop.current_crop.is_dormant = True


#
# dormancy_routine runs on the first day of dormancy if there is a crop growing.
# LAI is set to minimum LAI, 10% of biomass is added to residue, and the crop
# is signalled to be dormant
#
def dormancy_routine(crop_type, soil):
    crop_type.LAI_actual = max(0, min(crop_type.LAI_min, crop_type.LAI_actual))
    crop_type.fr_LAI_max = crop_type.LAI_actual / crop_type.LAI_max
    crop_type.biomass_actual -= crop_type.biomass_actual * 0.1
    crop_type.accumulated_HU -= crop_type.accumulated_HU * 0.1

    soil.residue += crop_type.biomass_actual * 0.1

    crop_type.is_dormant = True


#
# Determines whether the crop is killed at harvest
#
def is_kill_year(crop, time):
    if len(crop.grow_regimen) == time.year or \
            crop.current_crop.crop_name != crop.grow_regimen[time.year].crop_name or \
            crop.current_crop.crop_type == 'annual':
        return True
    return False


# -------------------------------------------------------------------------------
# Class: Crop
# -------------------------------------------------------------------------------
class Crop:
    def __init__(self, data, time):
        self.init_crop = InitCrop(data)
        self.alfalfa = Alfalfa(data)
        self.corn = Corn(data)
        self.soy = Soybean(data)

        # Dormancy for perennial crops
        self.latitude = data['latitude']
        self.T_dl_min = calculate_minimum_day_length(self.latitude)
        self.t_dorm = calculate_t_dorm(self.latitude)
        self.solar_declination = 0.0

        self.crops_list = [self.alfalfa, self.corn, self.soy]
        self.current_crop = self.init_crop

        self.grow_regimen = [self.init_crop for x in range(0, len(time.years))]

        # Each crop in crops_list has a list of grow years. This loop iterates
        # through those lists and populates a grow regimen with the crop grown
        # in each year
        for crop_type in self.crops_list:
            for year in crop_type.grow_years:
                if year - time.start_year >= len(self.grow_regimen) or year - time.start_year < 0:
                    print('\nCannot grow ', crop_type.crop_name, ' in year ', year,
                          ' because ', year, '\nis outside of the scope of the simulation.')
                else:
                    # has priority for populating grow regimen over crop cycles
                    if crop_type.repeat == 0:
                        x = year - time.start_year
                        self.grow_regimen[x] = crop_type
                    # populates grow regimen based off of crop cycles if
                    # another crop is not set for those years
                    else:
                        x = year - time.start_year
                        while x < len(self.grow_regimen):
                            if self.grow_regimen[x].crop_name == 'null':
                                self.grow_regimen[x] = crop_type
                            else:
                                print("Cannot grow", crop_type.crop_name, "in", str(year + x) + ",",
                                      self.grow_regimen[x].crop_name, "is already growing.")
                            x += crop_type.repeat


#
# A base crop class used when no crop is grown
#
class InitCrop:
    def __init__(self, data):
        """GENERAL PLANT INFO"""

        self.data = data
        self.grow_years = []
        self.repeat = 0
        self.planting_date = 0
        self.harvest_date = 0

        self.crop_name = 'null'
        self.crop_type = ''
        self.start_date = 0
        self.kill_year = True
        self.planted = False
        self.is_dormant = True

        self.fix_nitrogen = False

        # ===================================================================
        ''' HEAT UNIT DATA '''

        # Inputs
        self.T_base_min = 0
        self.T_base_max = 0
        self.PHU = 0

        # Internally calculated inputs
        self.accumulated_HU = 0
        self.prev_accumulated_HU = 0

        # Outputs
        self.fr_PHU = 0
        self.prev_fr_PHU = 0

        # ===================================================================
        ''' LEAF AREA INDEX (LAI) DATA '''

        # Inputs
        self.fr_PHU_1 = 0
        self.fr_PHU_2 = 0
        self.fr_LAI_1 = 0
        self.fr_LAI_2 = 0
        self.fr_PHU_sen = 0
        self.LAI_max = 0
        self.LAI_min = 0

        # Internally calculated inputs
        self.prev_fr_LAI_max = 0
        self.fr_LAI_max = 0

        # Outputs
        self.prev_LAI_actual = 0
        self.LAI_actual = 0

        # ===================================================================
        ''' ROOT DEPTH DATA '''

        # Inputs
        self.z_root_max = 0  # maximum depth of root development

        # Internally calculated inputs
        self.fr_root = 0

        # Outputs
        self.z_root = 0

        # ===================================================================
        ''' BIOMASS DATA '''

        # Inputs
        self.kl = 0
        self.RUE = 0
        self.T_opt = 0

        # Internally calculated inputs
        self.gamma_reg = 0
        self.dBiomass_max = 0
        self.d_biomass_actual = 0

        # Outputs
        self.biomass_actual = 0
        self.prev_biomass_actual = 0

        # ===================================================================
        ''' Soil Water Uptake Data '''

        self.beta_w = 0
        self.epco = 0

        self.water_actual_up = 0
        self.water_uptake_each_layer = []

        # ===================================================================
        ''' Nitrogen Uptake Data '''

        self.beta_n = 0

        self.bio_N_opt = 0
        self.bio_N = 0

        self.fr_n1 = 0  
        self.fr_n2 = 0  
        self.fr_n3 = 0  
        self.fr_n3ish = 0  

        self.fr_N = 0
        self.fr_N_up = 0
        self.N_up = 0
        self.act_N_up_each_layer = []
        self.N_actual_up = 0

        # ===================================================================
        ''' Phosphorus Uptake Data '''

        self.beta_p = 0

        self.bio_P_opt = 0
        self.bio_P = 0

        self.fr_PHU_50 = 0
        self.fr_PHU_100 = 0
        self.fr_p1 = 0
        self.fr_p2 = 0
        self.fr_p3 = 0
        self.fr_p3ish = 0

        self.fr_P = 0
        self.P_up = 0
        self.act_P_up_each_layer = []
        self.P_act_up = 0

        # ===================================================================
        ''' Yields Data '''

        self.HI_max = 0
        self.HI_min = 0
        self.HI_actual = 0
        self.HI_opt = 0

        self.harvest_eff = 0

        self.gamma_wu = 0

        self.bio_AG = 0
        self.yield_max = 0
        self.yield_actual = 0
        self.yield_N = 0
        self.yield_P = 0


#
# Crop object populated with Corn data
#
class Corn:

    def __init__(self, data):
        """GENERAL PLANT INFO"""

        corn_data = data['corn']
        self.grow_years = corn_data['grow_years']
        self.repeat = corn_data['repeat']
        self.planting_date = corn_data['planting_date']
        self.harvest_date = corn_data['harvest_date']

        self.crop_name = 'corn'
        self.crop_type = 'annual'
        self.start_date = 0
        self.kill_year = False
        self.planted = False
        self.is_dormant = True

        self.fix_nitrogen = False

        # ===================================================================
        ''' HEAT UNIT DATA '''

        # Inputs
        self.T_base_min = 10
        self.T_base_max = 30
        self.PHU = 1200

        # Internally calculated inputs
        self.accumulated_HU = 0.0
        self.prev_accumulated_HU = 0.0

        # Outputs
        self.fr_PHU = 0.0
        self.prev_fr_PHU = 0.0

        # ===================================================================
        ''' LEAF AREA INDEX (LAI) DATA '''

        # Inputs
        self.fr_PHU_1 = 0.15
        self.fr_PHU_2 = 0.50
        self.fr_LAI_1 = 0.05
        self.fr_LAI_2 = 0.95
        self.fr_PHU_sen = 0.90
        self.LAI_max = 3
        self.LAI_min = 0

        # Internally calculated inputs
        self.prev_fr_LAI_max = 0
        self.fr_LAI_max = 0

        # Outputs
        self.prev_LAI_actual = 0
        self.LAI_actual = 0

        # ===================================================================
        ''' ROOT DEPTH DATA '''

        # Inputs
        self.z_root_max = 2000  # maximum depth of root development

        # Internally calculated inputs
        self.fr_root = 0

        # Outputs
        self.z_root = 0

        # ===================================================================
        ''' BIOMASS DATA '''

        # Inputs
        self.kl = 0.65
        self.RUE = 39
        self.T_opt = 25

        # Internally calculated inputs
        self.gamma_reg = 0
        self.dBiomass_max = 0
        self.d_biomass_actual = 0.0

        # Outputs
        self.biomass_actual = 0
        self.prev_biomass_actual = 0

        # ===================================================================
        ''' Soil Water Uptake Data '''

        self.beta_w = 10  # water-use distribution parameter
        self.epco = 0.5

        self.water_actual_up = 0
        self.water_uptake_each_layer = []

        # ===================================================================
        ''' Nitrogen Uptake Data '''

        self.beta_n = 10

        self.bio_N_opt = 0
        self.bio_N = 0

        self.fr_n1 = 0.047
        self.fr_n2 = 0.0177
        self.fr_n3 = 0.0138
        self.fr_n3ish = 0.01381

        self.fr_N = 0
        self.fr_N_up = 0
        self.N_up = 0
        self.act_N_up_each_layer = []
        self.N_actual_up = 0

        # ===================================================================
        ''' Phosphorus Uptake Data '''

        self.beta_p = 10

        self.bio_P_opt = 0
        self.bio_P = 0

        self.fr_PHU_50 = 0.5
        self.fr_PHU_100 = 1.0
        self.fr_p1 = 0.0048
        self.fr_p2 = 0.0018
        self.fr_p3 = 0.0014
        self.fr_p3ish = 0.00141

        self.fr_P = 0
        self.P_up = 0
        self.act_P_up_each_layer = []
        self.P_act_up = 0

        # ===================================================================
        ''' Yields Data '''

        self.HI_max = 0
        self.HI_min = 0.3
        self.HI_actual = 0
        self.HI_opt = 0.6

        self.harvest_eff = 0.9

        self.gamma_wu = 0

        self.bio_AG = 0
        self.yield_max = 0
        self.yield_actual = 0
        self.yield_N = 0
        self.yield_P = 0


#
# Crop object populated with Soybean data
#
class Soybean:

    def __init__(self, data):
        """GENERAL PLANT INFO"""

        soy_data = data['soybean']
        self.grow_years = soy_data['grow_years']
        self.repeat = soy_data['repeat']
        self.planting_date = soy_data['planting_date']
        self.harvest_date = soy_data['harvest_date']

        self.crop_name = 'soybean'
        self.crop_type = 'annual'
        self.start_date = 0
        self.kill_year = False
        self.planted = False
        self.is_dormant = True

        self.fix_nitrogen = True
        # ===================================================================
        ''' HEAT UNIT DATA '''

        # Inputs
        self.T_base_min = 10
        self.T_base_max = 30  # corn
        self.PHU = 1150

        # Internally calculated inputs
        self.accumulated_HU = 0.0
        self.prev_accumulated_HU = 0.0

        # Outputs
        self.fr_PHU = 0.0
        self.prev_fr_PHU = 0.0

        # ===================================================================
        ''' LEAF AREA INDEX (LAI) DATA '''

        # Inputs
        self.fr_PHU_1 = 0.15
        self.fr_PHU_2 = 0.50
        self.fr_LAI_1 = 0.05
        self.fr_LAI_2 = 0.95
        self.fr_PHU_sen = 0.9
        self.LAI_max = 3
        self.LAI_min = 0

        # Internally calculated inputs
        self.prev_fr_LAI_max = 0
        self.fr_LAI_max = 0

        # Outputs
        self.prev_LAI_actual = 0
        self.LAI_actual = 0

        # ===================================================================
        ''' ROOT DEPTH DATA '''

        # Inputs
        self.z_root_max = 1700  # maximum depth of root development

        # Internally calculated inputs
        self.fr_root = 0

        # Outputs
        self.z_root = 0

        # ===================================================================
        ''' BIOMASS DATA '''

        # Inputs
        self.kl = 0.45
        self.RUE = 25
        self.T_opt = 25

        # Internally calculated inputs
        self.gamma_reg = 0
        self.dBiomass_max = 0
        self.d_biomass_actual = 0.0

        # Outputs
        self.biomass_actual = 0
        self.prev_biomass_actual = 0

        # ===================================================================
        ''' Soil Water Uptake Data '''

        self.beta_w = 10  # water-use distribution parameter  # corn
        self.epco = 0.5  # corn

        # Outputs
        self.prev_LAI_actual = 0
        self.LAI_actual = 0

        # ===================================================================
        ''' Nitrogen Uptake Data '''

        self.beta_n = 10  # corn

        self.bio_N_opt = 0
        self.bio_N = 0

        self.fr_n1 = 0.0524
        self.fr_n2 = 0.0265
        self.fr_n3 = 0.0258
        self.fr_n3ish = 0.02581

        self.fr_N = 0
        self.fr_N_up = 0
        self.N_up = 0
        self.act_N_up_each_layer = []
        self.N_actual_up = 0

        # ===================================================================
        ''' Phosphorus Uptake Data '''

        self.beta_p = 10  # corn

        self.bio_P_opt = 0
        self.bio_P = 0

        self.fr_PHU_50 = 0.5
        self.fr_PHU_100 = 1.0
        self.fr_p1 = 0.0074
        self.fr_p2 = 0.0037
        self.fr_p3 = 0.0035
        self.fr_p3ish = 0.00351

        self.fr_P = 0
        self.P_up = 0
        self.act_P_up_each_layer = []
        self.P_act_up = 0

        # ===================================================================
        ''' Yields Data '''

        self.HI_max = 0
        self.HI_min = 0.01
        self.HI_actual = 0
        self.HI_opt = 0.31

        self.harvest_eff = 0.9

        self.gamma_wu = 0

        self.bio_AG = 0
        self.yield_max = 0
        self.yield_actual = 0
        self.yield_N = 0
        self.yield_P = 0


#
# Crop object populated with Alfalfa data
#
class Alfalfa:

    def __init__(self, data):
        """GENERAL PLANT INFO"""

        alfalfa_data = data['alfalfa']
        self.grow_years = alfalfa_data['grow_years']
        self.repeat = alfalfa_data['repeat']
        self.planting_date = alfalfa_data['planting_date']
        self.harvest_date = alfalfa_data['harvest_date']

        self.crop_name = 'alfalfa'
        self.crop_type = 'perennial'
        self.start_date = 0
        self.kill_year = False
        self.planted = False
        self.is_dormant = True

        self.fix_nitrogen = False
        # ===================================================================
        ''' HEAT UNIT DATA '''

        # Inputs
        self.T_base_min = 4
        self.T_base_max = 32  # until dormancy
        self.PHU = 2500  # corn, swat says 0

        # Internally calculated inputs
        self.accumulated_HU = 0.0
        self.prev_accumulated_HU = 0.0

        # Outputs
        self.fr_PHU = 0.0
        self.prev_fr_PHU = 0.0

        # ===================================================================
        ''' LEAF AREA INDEX (LAI) DATA '''

        # Inputs
        self.fr_PHU_1 = 0.15
        self.fr_PHU_2 = 0.50
        self.fr_LAI_1 = 0.01
        self.fr_LAI_2 = 0.95
        self.fr_PHU_sen = 0.90
        self.LAI_max = 4
        self.LAI_min = 0.75

        # Internally calculated inputs
        self.prev_fr_LAI_max = 0
        self.fr_LAI_max = 0

        # Outputs
        self.prev_LAI_actual = 0
        self.LAI_actual = 0

        # ===================================================================
        ''' ROOT DEPTH DATA '''

        # Inputs
        self.z_root_max = 3000  # maximum depth of root development

        # Internally calculated inputs
        self.fr_root = 0

        # Outputs
        self.z_root = 0

        # ===================================================================
        ''' BIOMASS DATA '''

        # Inputs
        self.kl = 0.65
        self.RUE = 20
        self.T_opt = 25

        # Internally calculated inputs
        self.gamma_reg = 0
        self.dBiomass_max = 0
        self.d_biomass_actual = 0.0

        # Outputs
        self.biomass_actual = 0
        self.prev_biomass_actual = 0

        # ===================================================================
        ''' Soil Water Uptake Data '''

        self.beta_w = 10  # water-use distribution parameter  # corn
        self.epco = 0.5  # corn

        self.water_actual_up = 0
        self.water_uptake_each_layer = []

        # ===================================================================
        ''' Nitrogen Uptake Data '''

        self.beta_n = 10  # corn

        self.bio_N_opt = 0
        self.bio_N = 0

        self.fr_n1 = 0.0417
        self.fr_n2 = 0.0290
        self.fr_n3 = 0.0200
        self.fr_n3ish = 0.02001

        self.fr_N = 0
        self.fr_N_up = 0
        self.N_up = 0
        self.act_N_up_each_layer = []
        self.N_actual_up = 0

        # ===================================================================
        ''' Phosphorus Uptake Data '''

        self.beta_p = 10  # corn

        self.bio_P_opt = 0
        self.bio_P = 0

        self.fr_PHU_50 = 0.5
        self.fr_PHU_100 = 1.0
        self.fr_p1 = 0.0035
        self.fr_p2 = 0.0028
        self.fr_p3 = 0.0020
        self.fr_p3ish = 0.00201

        self.fr_P = 0
        self.P_up = 0
        self.act_P_up_each_layer = []
        self.P_act_up = 0

        # ===================================================================
        ''' Yields Data '''

        self.HI_max = 0
        self.HI_min = 0.9
        self.HI_actual = 0
        self.HI_opt = 0.9

        self.harvest_eff = 0.9

        self.gamma_wu = 0

        self.bio_AG = 0
        self.yield_max = 0
        self.yield_actual = 0
        self.yield_N = 0
        self.yield_P = 0


# -----------------------------------------------------------------------
# Method: calculate_start_growth_day
# "pseudocode_crop" section C.1.A
# -----------------------------------------------------------------------
def calculate_start_growth_date(crop_type, weather, time):
    yearly_T_avg = weather.T_avg[time.year - 1]
    if time.year == 1 and time.day > crop_type.planting_date:
        crop_type.start_date = crop_type.harvest_date + 1
        crop_type.planted = False

    elif crop_type.crop_type == "annual":
        crop_type.start_date = crop_type.planting_date

    else:
        for d in range(time.day - 1, len(yearly_T_avg)):
            if yearly_T_avg[d] > crop_type.T_base_min:
                crop_type.start_date = d
                break


#
# Calculates minimum day length for the given watershed based on latitude and
# solar declination during the winter solstice
# "pseudocode_crop" C.11.B.1
#
def calculate_minimum_day_length(latitude):
    angular_velocity = 0.2618
    solar_declination = -0.4102
    latitude_radians = latitude * pi / 180

    T_dl_min = 2 * acos(-tan(solar_declination) * tan(latitude_radians)) / angular_velocity

    return T_dl_min


#
# Calculates the dormancy threshold given the latitude of the given watershed
# "pseudocode_crop" C.11.A.2
#
def calculate_t_dorm(latitude):
    if latitude > 40:
        return 1.0
    elif 20 <= latitude <= 40:
        return (latitude - 20) / 20
    else:
        return 0.0


#
# Returns a boolean indicating whether the given day is within the dormant
# period for the watershed.
# "pseudocode_crop" C.11.A.1/C.11.B.2
#
def in_dormancy(crop, time):

    # Annual crops will never be dormant
    if crop.current_crop.crop_type == 'annual':
        return False

    # if time.day < crop.current_crop.start_date and not crop.planted:
    #     return False

    year_length = get_year_length(time.cal_year)

    # C.11.B.2
    solar_declination = asin(0.4 * sin(2 * pi / year_length * (time.day - 82)))

    angular_velocity = 0.2618
    latitude_radians = crop.latitude * pi / 180

    T_dl = 2 * acos(-tan(solar_declination) * tan(latitude_radians)) / angular_velocity

    T_dl_thr = crop.T_dl_min + crop.t_dorm

    # A crop that is not planted cannot be dormant
    if not crop.current_crop.planted and not T_dl < T_dl_thr:
        return False

    # The current day length is less than the day length threshold for dormancy
    if T_dl < T_dl_thr:
        return True

    return False


#
# Helper method to determine year lengths accounting for leap years
#
def get_year_length(year):
    if year % 400 == 0:
        return 366
    elif year % 100 == 0:
        return 365
    elif year % 4 == 0:
        return 366
    else:
        return 365
