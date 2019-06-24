################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: crop.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Andy Achenreiner, achenreiner@wisc.edu

This module needs the following inputs in order to operate correctly:

    These are attributes of a crop type that need to be specified in the json input
    file. The values on the right are just examples from a corn crop type.
        "crop_name": "corn",
        "crop_type": "annual",
        "fix_nitrogen": false,

        "planting_date": 121,
        "harvest_date": 319,

        "harvest_index": 0.65,
        "harvest_eff": 0.9,
        "HI_opt": 0.6,
        "HI_min": 0.3,

        "min_temp_for_growth": 10,
        "max_temp_for_growth": 30,
        "opt_temp_for_growth": 25,
        "HU_for_maturity": 1200,

        "fr_PHU_50" : 0.5,
        "fr_PHU_100" : 1.0,
        "fr_PHU_sen": 0.90,
        "fr_PHU_1": 0.15,
        "fr_PHU_2": 0.50,
        "fr_LAI_1": 0.05,
        "fr_LAI_2": 0.95,

        "LAI_max": 3,
        "radiation_use_efficiency": 39,
        "light extinction coefficient": 0.65,

        "z_root_max": 2000,

        "fr,n1": 0.047,
        "fr,n2": 0.0177,
        "fr,n3": 0.0138,
        "fr,n~3": 0.01381,
        "beta_n": 10,

        "beta_w": 10,
        "epco": 0.5,

        "fr,p1": 0.0048,
        "fr,p2": 0.0018,
        "fr,p3": 0.0014,
        "fr,p~3": 0.00141,
        "beta_p": 10

    From the weather class, the following will be needed:
        T_min
        T_max
        radiation
        T_avg

    From the soil class, the following will be needed:
        listOfSoilLayers

        And the following attributes of a soil layer:
            bottomDepth
            Eo_sum = Sum of the Eo values leading up to today
            Et_max
            NO3
            labileP
            currentSoilWaterMM
            fcWater
            wiltingWater
"""
################################################################################

from . import heat_units, leaf_area_index, root_development, biomass, yields, \
    phosphorus_uptake, nitrogen_uptake, water_uptake, growth_constraints
from RUFAS import util


# -------------------------------------------------------------------------------
# Function: daily_crop_routine
# -------------------------------------------------------------------------------
def daily_crop_routine(crop, weather, time, soil):
    T_min = weather.T_min[time.year - 1][time.day - 1]
    T_max = weather.T_max[time.year - 1][time.day - 1]

    crop_type = crop.current_crop

    #
    # Run calculations
    # The order in which these are called matters because some of the later
    # update_all calls depend on values calculated earlier.
    #

    if crop.current_crop.crop_name != 'null':

        heat_units.update_all(crop_type, T_min, T_max, time)

        root_development.update_all(crop_type, time)

        water_uptake.update_all(crop_type, soil, time)

        nitrogen_uptake.update_all(crop_type, soil)

        phosphorus_uptake.update_all(crop_type, soil)

        growth_constraints.update_all(crop_type, time, weather, soil)

        leaf_area_index.update_all(crop_type, time)

        biomass.update_all(crop_type, time, weather)

        yields.update_all(crop_type, time, soil)


# -------------------------------------------------------------------------------
# Function: annual_crop_routine
# -------------------------------------------------------------------------------
def annual_crop_routine(crop, weather, time):

    crop.current_crop = crop.init_crop

    for crop_type in crop.crops_list:
        for year in crop_type.grow_years:
            if year == time.cal_year:
                calculate_start_growth_date(crop_type, weather, time)
                crop.current_crop = crop_type
                break


# -------------------------------------------------------------------------------
# Class: Crop
# -------------------------------------------------------------------------------
class Crop:
    def __init__(self, data):
        self.init_crop = init_crop(data)
        self.alfalfa = Alfalfa(data)
        self.corn = Corn(data)
        self.soy = Soybean(data)

        self.crops_list = [self.alfalfa, self.corn, self.soy]
        self.current_crop = self.init_crop

    # ---------------------------------------------------------------------------
    # Method: annual_reset
    # ---------------------------------------------------------------------------
    def annual_reset(self):
        for crop_type in self.crops_list:
            crop_type.accumulated_HU = 0
            crop_type.prev_accumulated_HU = 0

            crop_type.fr_PHU = 0
            crop_type.prev_fr_PHU = 0

            crop_type.biomass_actual = 0
            crop_type.prev_biomass_actual = 0

            crop_type.bio_P = 0
            crop_type.bio_N = 0

            crop_type.Ea_sum = 0

class init_crop:
    def __init__(self, data):

        self.data = data
        self.crop_name = 'null'
        self.crop_type = ''
        self.fix_nitrogen = False

        self.grow_years = []
        self.planting_date = 0
        self.harvest_date = 0
        self.start_date = 0

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
        self.prev_z_root = 0

        # ===================================================================
        ''' BIOMASS DATA '''

        # Inputs
        self.kl = 0  # TODO: possibly a constant for every crop
        self.RUE = 0  # TODO: possibly a constant for every crop
        self.T_opt = 0

        # Internally calculated inputs
        self.gamma_reg = 0
        self.dBiomass_max = 0
        self.dBiomass_actual = 0

        # Outputs
        self.biomass_actual = 0
        self.prev_biomass_actual = 0

        # ===================================================================
        ''' Soil Water Uptake Data '''

        self.beta_w = 0  # TODO: possibly a constant for every crop
        self.epco = 0  # TODO: possibly a constant for every crop

        self.water_actual_up = 0
        self.water_uptake_each_layer = []

        # ===================================================================
        ''' Nitrogen Uptake Data '''

        self.beta_n = 0  # TODO: possibly a constant for every crop

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

        self.beta_p = 0  # TODO: possibly a constant for every crop

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

        self.harvest_eff = 0 # TODO: possibly a non-crop specific user input

        self.gamma_wu = 0

        self.bio_AG = 0
        self.yield_max = 0
        self.yield_actual = 0
        self.yield_N = 0
        self.yield_P = 0


class Corn:

    def __init__(self, data):

        """GENERAL PLANT INFO"""

        corn_data = data['corn']
        self.grow_years = corn_data['grow_years']
        self.planting_date = corn_data['planting_date']
        self.harvest_date = corn_data['harvest_date']

        self.crop_name = 'corn'
        self.crop_type = 'annual'
        self.start_date = 0

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
        self.prev_z_root = 0

        # ===================================================================
        ''' BIOMASS DATA '''

        # Inputs
        self.kl = 0.65
        self.RUE = 39
        self.T_opt = 25

        # Internally calculated inputs
        self.gamma_reg = 0
        self.dBiomass_max = 0
        self.dBiomass_actual = 0.0

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


class Soybean:

    def __init__(self, data):

        soy_data = data['soybean']
        self.grow_years = soy_data['grow_years']
        self.planting_date = soy_data['planting_date']
        self.harvest_date = soy_data['harvest_date']
        """GENERAL PLANT INFO"""
        self.crop_name = 'soybean'
        self.crop_type = 'perennial'
        self.start_date = 0

        self.fix_nitrogen = True
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
        self.prev_z_root = 0

        # ===================================================================
        ''' BIOMASS DATA '''

        # Inputs
        self.kl = 0.65
        self.RUE = 39
        self.T_opt = 25

        # Internally calculated inputs
        self.gamma_reg = 0
        self.dBiomass_max = 0
        self.dBiomass_actual = 0.0

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


class Alfalfa:

    def __init__(self, data):
        alfalfa_data = data['alfalfa']
        self.grow_years = alfalfa_data['grow_years']
        self.planting_date = alfalfa_data['planting_date']
        self.harvest_date = alfalfa_data['harvest_date']
        """GENERAL PLANT INFO"""
        self.crop_name = 'alfalfa'
        self.crop_type = 'annual'
        self.start_date = 0

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
        self.prev_z_root = 0

        # ===================================================================
        ''' BIOMASS DATA '''

        # Inputs
        self.kl = 0.65
        self.RUE = 39
        self.T_opt = 25

        # Internally calculated inputs
        self.gamma_reg = 0
        self.dBiomass_max = 0
        self.dBiomass_actual = 0.0

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

# -----------------------------------------------------------------------
# Method: calculate_start_growth_day
# "pseudocode_crop" section C.1.A
# -----------------------------------------------------------------------
def calculate_start_growth_date(crop_type, weather, time):
    yearly_T_avg = weather.T_avg[time.year - 1]
    if time.year == 1 and time.day > crop_type.planting_date:
        crop_type.start_date = crop_type.harvest_date + 1

    elif crop_type.crop_type == "annual":
        crop_type.start_date = crop_type.planting_date

    else:
        for d in range(len(yearly_T_avg)):
            if yearly_T_avg[d] > crop_type.T_base_min:
                crop_type.start_date = d
                break
