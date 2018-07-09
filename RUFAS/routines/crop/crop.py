################################################################################
'''
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
        "init_residue": 8000,

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
            Ea_sum = Sum of the Ea values leading up to today
            Eo_sum = Sum of the Eo values leading up to today
            Etrans
            NO3
            labileP
            currentSoilWaterMM
            fcWater
            wiltingWater
'''
################################################################################

from . import heat_units, leaf_area_index, root_development, biomass, yields, \
    phosphorus_uptake, nitrogen_uptake, soil_water_uptake
from RUFAS import util

#-------------------------------------------------------------------------------
# Function: daily_crop_routine
#-------------------------------------------------------------------------------
def daily_crop_routine(crop, weather, time, soil):
    '''
    TODO: Add DocString
    '''

    T_min = weather.T_min[time.year-1][time.day-1]
    T_max = weather.T_max[time.year-1][time.day-1]

    for _,crop_type in crop.crops_list.items():

#------------------------------------------------------------------------------
        '''
        Load input values to represent input from other modules.
        This will need to be removed eventually because the crop module will
        get this information from the other modules instead of from an input file. 
        This is just for isolating and testing the calculations of the crop module.
        '''
        timeIndex = (time.year -1)*365 + time.day -1

        soil.Etrans = crop_type.test_Et[timeIndex]

        soil.Ea_sum = crop_type.test_Ea_sum[time.year-1]
        soil.Eo_sum = crop_type.test_Eo_sum[time.year-1]

        soil.listOfSoilLayers[0].NO3 = crop_type.test_NO3_l1[timeIndex]
        soil.listOfSoilLayers[1].NO3 = crop_type.test_NO3_l2[timeIndex]
        soil.listOfSoilLayers[2].NO3 = crop_type.test_NO3_l3[timeIndex]

        soil.listOfSoilLayers[0].currentSoilWaterMM = crop_type.test_soil_water1[timeIndex]
        soil.listOfSoilLayers[1].currentSoilWaterMM = crop_type.test_soil_water2[timeIndex]
        soil.listOfSoilLayers[2].currentSoilWaterMM = crop_type.test_soil_water3[timeIndex]

#------------------------------------------------------------------------------

        #
        # Run calculations
        # The order in which these are called matters because some of the later
        # update_all calls depend on values calculated earlier.
        #
        heat_units.update_all(crop_type, T_min, T_max, time)

        soil_water_uptake.update_all(crop_type, soil, time)

        biomass.update_all(crop_type, time, weather, soil)

        leaf_area_index.update_all(crop_type, time)

        phosphorus_uptake.update_all(crop_type, soil, time)

        nitrogen_uptake.update_all(crop_type, soil, time)

        root_development.update_all(crop_type, time)

        yields.update_all(crop_type, time, soil)


#-------------------------------------------------------------------------------
# Function: annual_crop_routine
#-------------------------------------------------------------------------------
def annual_crop_routine(crop, weather, time):
    '''
    TODO: Add DocString
    '''

    for _,crop_type in crop.crops_list.items():
        crop_type.calculate_start_growth_day(weather.T_avg[time.year-1])

#-------------------------------------------------------------------------------
# Class: Crop
#-------------------------------------------------------------------------------
class Crop():
    '''
    TODO: Add DocString
    '''

    def __init__(self, data):
        '''
        TODO: Add DocString
        '''

        self.crops_list = {crop_type: self.CropType(data[crop_type]) for crop_type in data.keys()}

    #---------------------------------------------------------------------------
    # Class: CropType
    #---------------------------------------------------------------------------
    class CropType():

        def __init__(self, data):
            '''
            TODO: Add DocString
            '''

            '''GENERAL PLANT INFO'''

            self.crop_name = data['crop_name']

            self.crop_type = data['crop_type']
            self.fix_nitrogen = data['fix_nitrogen']

            self.planting_date = data['planting_date']
            self.harvest_date = data['harvest_date']
            self.start_day = 0

            #===================================================================
            ''' HEAT UNIT DATA '''
           
            # Inputs
            self.T_base_min = data['min_temp_for_growth']
            self.T_base_max = data['max_temp_for_growth']
            self.PHU = data['HU_for_maturity']

            # Internally calculated inputs
            self.accumulated_HU = 0.0
            self.prev_accumulated_HU = 0.0
            
            # Outputs
            self.fr_PHU = 0.0
            self.prev_fr_PHU = 0.0
            
            #===================================================================
            ''' LEAF AREA INDEX (LAI) DATA '''
            
            # Inputs
            self.fr_PHU_1 = data['fr_PHU_1']
            self.fr_PHU_2 = data['fr_PHU_2']
            self.fr_LAI_1 = data['fr_LAI_1']
            self.fr_LAI_2 = data['fr_LAI_2']
            self.fr_PHU_sen = data['fr_PHU_sen']
            self.LAI_max = data['LAI_max']
            
            # Internally calculated inputs
            self.prev_fr_LAI_max = 0
            self.fr_LAI_max = 0
            
            # Outputs
            self.prev_LAI_actual = 0
            self.LAI_actual = 0
            
            #===================================================================
            ''' ROOT DEPTH DATA '''
            
            # Inputs
            self.z_root_max = data['z_root_max'] # maximum depth of root development

            # Internally calculated inputs
            self.fr_root = 0
            
            # Outputs
            self.z_root = 0
            self.prev_z_root = 0
            
            #===================================================================
            ''' BIOMASS DATA '''
            
            # Inputs
            self.kl = data['light extinction coefficient']
            self.RUE = data['radiation_use_efficiency']
            self.T_opt = data['opt_temp_for_growth']

            # Internally calculated inputs
            self.gamma_reg = 0
            self.dBiomass_max = 0
            self.dBiomass_actual = 0.0
            
            # Outputs
            self.biomass_actual = 0
            self.prev_biomass_actual = 0
            
            #===================================================================
            ''' Soil Water Uptake Data '''

            self.beta_w = data['beta_w']   # water-use distribution parameter
            self.epco = data['epco']

            self.Et_actual = 0
            self.water_actual_up = 0
            self.water_uptake_each_layer = []

            #===================================================================
            ''' Nitrogen Uptake Data '''

            self.beta_n = data["beta_n"]

            self.bio_N_opt = 0
            self.bio_N = 0

            self.fr_n1 = data["fr,n1"]
            self.fr_n2 = data["fr,n2"]
            self.fr_n3 = data["fr,n3"]
            self.fr_n3ish = data["fr,n~3"]

            self.fr_N = 0
            self.fr_N_up = 0
            self.N_up = 0
            self.act_N_up_each_layer = []
            self.N_actual_up = 0

            #===================================================================
            ''' Phosphorus Uptake Data '''

            self.beta_p = data["beta_p"]

            self.bio_P_opt = 0
            self.bio_P = 0

            self.fr_PHU_50 = data["fr_PHU_50"]
            self.fr_PHU_100 = data["fr_PHU_100"]
            self.fr_p1 = data["fr,p1"]
            self.fr_p2 = data["fr,p2"]
            self.fr_p3 = data["fr,p3"]
            self.fr_p3ish = data["fr,p~3"]

            self.fr_P = 0
            self.P_up = 0
            self.act_P_up_each_layer = []
            self.P_act_up = 0

            #===================================================================
            ''' Yields Data '''

            self.HI_max = 0
            self.HI_min = data["HI_min"]
            self.HI_actual = 0
            self.HI_opt = data["HI_opt"]

            self.harvest_eff = data["harvest_eff"]

            self.gamma_wu = 0

            self.bio_AG = 0
            self.yield_max = 0
            self.yield_actual = 0
            self.yield_N = 0
            self.yield_P = 0
            self.residue = data["init_residue"]

            #===================================================================
            ''' Testing Data '''

            TEST_DATA = util.get_csv_columns(data["TEST_DATA"])


            self.test_Et = TEST_DATA[1][1:]

            self.test_water_actual_up = TEST_DATA[2][1:]

            self.test_bio_N_opt = TEST_DATA[3][1:]
            self.test_bio_N = TEST_DATA[4][1:]

            self.test_bio_P_opt = TEST_DATA[5][1:]
            self.test_bio_P = TEST_DATA[6][1:]

            self.test_NO3_l1 = TEST_DATA[7][1:]
            self.test_NO3_l2 = TEST_DATA[8][1:]
            self.test_NO3_l3 = TEST_DATA[9][1:]

            self.test_soil_water1 = TEST_DATA[10][1:]
            self.test_soil_water2 = TEST_DATA[11][1:]
            self.test_soil_water3 = TEST_DATA[12][1:]

            self.test_Ea_sum = data["TESTING_Ea_sum"]
            self.test_Eo_sum = data["TESTING_Eo_sum"]


        #-----------------------------------------------------------------------
        # Method: calculate_start_growth_day
        #-----------------------------------------------------------------------
        def calculate_start_growth_day(self, T_avg):
            '''
            TODO: Add DocString
            '''

            if self.crop_type == "annual":
                self.start_day = self.planting_date
            else: # crop_type == "perennial"
                for d in range(len(T_avg)):
                    if T_avg > self.T_base_min:
                        self.start_day = d


    #---------------------------------------------------------------------------
    # Method: annual_reset
    #---------------------------------------------------------------------------
    def annual_reset(self):
        '''
        TODO: Add DocString
        '''
        for _, crop_type in self.crops_list.items():
            crop_type.accumulated_HU = 0
            crop_type.prev_accumulated_HU = 0

            crop_type.fr_PHU = 0
            crop_type.prev_fr_PHU = 0

            crop_type.biomass_actual = 0
            crop_type.prev_biomass_actual = 0

            crop_type.bio_P = 0
            crop_type.bio_N = 0

