################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: crop.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Andy Achenreiner, achenreiner@wisc.edu
           William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com

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
            ET_annual = Sum of the ET_act values leading up to today
            trans_max
            NO3
            labile_P
            soil_water
            fc_water
            wilting_water
"""
################################################################################

from math import acos, asin, sin, tan, pi
from .crop_types import alfalfa, corn, soybean
from . import heat_units, leaf_area_index, root_development, biomass, yields, \
    phosphorus_uptake, nitrogen_uptake, growth_constraints


# -------------------------------------------------------------------------------
# Function: daily_crop_routine
# -------------------------------------------------------------------------------
def daily_crop_routine(crop, weather, time, soil):
    T_min = weather.T_min[time.year - 1][time.day - 1]
    T_max = weather.T_max[time.year - 1][time.day - 1]

    # Current crop is set at the beginning of the year in annual_crop_routine
    crop_type = crop.current_crop

    # If there is no crop in rotation this year, current crop will be named
    # 'null'. The routine is skipped in this case
    if crop_type.crop_name != 'null':

        # yield is reset to 0 at the beginning of the next day so it can be
        # accessed by the output handler.
        crop_type.yield_actual = 0
        crop_type.yield_N = 0
        crop_type.yield_P = 0

        # If the crop is not planted yet, determine whether it is planted today
        if not crop_type.planted:
            calculate_start(crop, weather, time)

        # Once the crop is planted:
        else:
            # If the crop is growing, run the routines
            if crop_type.growing:
                heat_units.update_all(crop_type, T_min, T_max)

                root_development.update_all(crop_type)

                # transpiration.update_all(crop_type, soil, time)

                nitrogen_uptake.update_all(crop_type, soil)

                phosphorus_uptake.update_all(crop_type, soil)

                growth_constraints.update_all(crop_type, time, weather, soil)

                leaf_area_index.update_all(crop_type, time)

                biomass.update_all(crop_type, soil, time, weather)

                # "pseudocode_crop" C.10.A.1/2
                if crop_type.harvest_type == 'scheduled':
                    if time.day == crop_type.kill_day:
                        yields.update_all(crop_type, time, soil)

                elif crop_type.harvest_type == 'optimal':
                    if crop_type.fr_PHU >= crop_type.fr_PHU_harvest:
                        yields.update_all(crop_type, time, soil)

                else:
                    print('"' + crop_type.harvest_type + '"', 'is not a recognized harvest type.'
                                                              ' Harvesting on optimal date.')
                    crop_type.harvest_type = 'optimal'

            # If the crop is perennial, determine whether it is dormant
            if crop_type.crop_type == 'perennial':
                # If it is, run the dormancy routine and set growing to false
                # (This method is only called once on the first day when crop
                # enters dormancy)
                if in_dormancy(crop, time) and crop_type.growing:
                    dormancy_routine(crop_type, time, soil)
                    crop_type.growing = False
                elif not in_dormancy(crop, time):
                    crop_type.growing = True

        annual_variable_update(crop_type)


def annual_variable_update(crop_type):

    crop_type.yield_annual += crop_type.yield_actual
    crop_type.yield_N_annual += crop_type.yield_N
    crop_type.yield_P_annual += crop_type.yield_P
    crop_type.DM_yield_annual += crop_type.DM_yield


# -------------------------------------------------------------------------------
# Function: annual_crop_routine determines the current crop and whether it is
# a kill year for that crop
# -------------------------------------------------------------------------------
def annual_crop_routine(crop, time):
    # current crop is set to the next crop in the regimen
    crop.current_crop = crop.grow_regimen[time.year - 1]

    crop.current_crop.kill_year = is_kill_year(crop, time)


#
# dormancy_routine runs on the first day of dormancy if there is a crop growing.
# LAI is set to minimum LAI, 10% of biomass is added to residue, and the crop
# is signalled to be dormant
#
def dormancy_routine(crop_type, time, soil):
    if crop_type.kill_year:
        crop_type.kill_day = time.day
        yields.update_all(crop_type, time, soil)
    else:
        if crop_type.fr_PHU > crop_type.fr_PHU_harvest_min:
            yields.update_all(crop_type, time, soil)
        crop_type.LAI_actual = max(0, min(crop_type.LAI_min, crop_type.LAI_actual))
        crop_type.fr_LAI_max = 0

        soil.residue += crop_type.biomass_actual * 0.1
        crop_type.biomass_actual -= crop_type.biomass_actual * 0.1
        crop_type.bio_N -= crop_type.bio_N * 0.1
        crop_type.bio_P -= crop_type.bio_P * 0.1

        crop_type.accumulated_HU = 0
        crop_type.fr_PHU = 0


#
# Determines whether the crop is killed at harvest
#
def is_kill_year(crop, time):
    if len(crop.grow_regimen) == time.year or \
            crop.current_crop.crop_name != crop.grow_regimen[time.year].crop_name or \
            crop.current_crop.crop_type == 'annual':
        crop.current_crop.kill_day = crop.current_crop.harvest_date
        return True
    return False


# -------------------------------------------------------------------------------
# Class: Crop
# -------------------------------------------------------------------------------
class Crop:
    def __init__(self, data, time):
        self.init_crop = InitCrop(data)
        self.alfalfa = alfalfa.Alfalfa(data)
        self.corn = corn.Corn(data)
        self.soy = soybean.Soybean(data)

        # Dormancy for perennial crops
        self.latitude = abs(data['latitude'])
        self.T_dl_min = calculate_minimum_day_length(self.latitude)
        self.t_dorm = calculate_t_dorm(self.latitude)
        self.solar_declination = 0.0

        self.crops_list = [self.alfalfa, self.corn, self.soy]
        self.current_crop = self.init_crop

        self.grow_regimen = [self.init_crop for _ in range(0, len(time.years))]

        # Each crop in crops_list has a list of grow years. This loop iterates
        # through those lists and populates a grow regimen with the crop grown
        # in each year
        for crop_type in self.crops_list:
            for year in crop_type.grow_years:
                if year - time.start_year >= len(self.grow_regimen) or year - time.start_year < 0:
                    print('\nCannot grow', crop_type.crop_name, 'in year', year,
                          'because', year, '\nis outside of the scope of the simulation.')
                else:
                    # has priority for populating grow regimen over crop cycles
                    if crop_type.repeat == 0:
                        x = year - time.start_year
                        self.grow_regimen[x] = crop_type
                    # populates grow regimen based on crop cycles if
                    # another crop is not set for those years
                    else:
                        x = year - time.start_year
                        while x < len(self.grow_regimen):
                            if self.grow_regimen[x].crop_name == 'null':
                                self.grow_regimen[x] = crop_type
                            else:
                                print('Cannot grow', crop_type.crop_name, 'in', str(year + x) + ',',
                                      self.grow_regimen[x].crop_name, 'is already growing.')
                            x += crop_type.repeat

    def annual_reset(self):
        self.current_crop.yield_N_annual = 0.0
        self.current_crop.yield_P_annual = 0.0
        self.current_crop.DM_yield_annual = 0.0
        self.current_crop.yield_annual = 0.0


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
        self.harvest_type = ''
        self.fr_PHU_harvest_min = 0

        self.crop_name = 'null'
        self.crop_type = ''
        self.harvest_quality = 'null'
        self.feed_id = 'null'

        self.kill_day = -1
        self.kill_year = True
        self.planted = False
        self.growing = False

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
        self.fr_PHU_harvest = 0
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
        self.d_biomass_max = 0
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

        self.DM_perc_harvest = 0.15  # TODO: Hard coded dry matter percent at harvest

        self.bio_AG = 0
        self.yield_max = 0
        self.yield_actual = 0
        self.DM_yield = 0.0
        self.yield_N = 0
        self.yield_P = 0

        self.yield_N_annual = 0.0
        self.yield_P_annual = 0.0
        self.DM_yield_annual = 0.0
        self.yield_annual = 0


# -----------------------------------------------------------------------
# Method: calculate_start_growth_day
# "pseudocode_crop" section C.1.A
# -----------------------------------------------------------------------
def calculate_start(crop, weather, time):
    crop_type = crop.current_crop
    yearly_T_avg = weather.T_avg[time.year - 1]
    if crop_type.crop_type == 'annual':
        if time.day == crop_type.planting_date:
            crop_type.planted = True
            crop_type.growing = True
    else:
        if time.year == 1 and time.day > crop_type.planting_date:
            pass
        elif not in_dormancy(crop, time) and yearly_T_avg[time.day - 1] > crop_type.T_base_min:
            crop_type.planted = True
            crop_type.growing = True

    crop.current_crop = crop_type


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
    year_length = get_year_length(time.cal_year)

    # C.11.B.2
    solar_declination = asin(0.4 * sin(2 * pi / year_length * (time.day - 82)))

    angular_velocity = 0.2618
    latitude_radians = crop.latitude * pi / 180

    T_dl = 2 * acos(-tan(solar_declination) * tan(latitude_radians)) / angular_velocity

    T_dl_thr = crop.T_dl_min + crop.t_dorm

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
