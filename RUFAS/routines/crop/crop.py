################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: crop.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
'''
################################################################################

from math import exp, log, floor
from . import heat_units, leaf_area_index, root_development, biomass, yields, \
    phosphorus_uptake, nitrogen_uptake

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

        '''
        Load in input value to represent input from other modules
        These will have to be updated to get this information from the other
        modules instead of from an input file.
        '''
        timeIndex = (time.year -1)*365 + time.day -1
        crop_type.Et = crop_type.test_Et[timeIndex]
        crop_type.water_actual_up = crop_type.test_water_actual_up[timeIndex]

        crop_type.bio_N = crop_type.test_bio_N[timeIndex]
        crop_type.bio_N_opt = crop_type.test_bio_N_opt[timeIndex]
        crop_type.bio_P = crop_type.test_bio_P[timeIndex]
        crop_type.bio_P_opt = crop_type.test_bio_P_opt[timeIndex]

        crop_type.Ea_sum = crop_type.test_Ea_sum[time.year-1]
        crop_type.Eo_sum = crop_type.test_Eo_sum[time.year-1]

        #
        # Run calculations
        #
        heat_units.update_all(crop_type, T_min, T_max, time)

        biomass.update_all(crop_type, time, weather)

        leaf_area_index.update_all(crop_type, time)

        root_development.update_all(crop_type, time)

        phosphorus_uptake.update_all(crop_type, time)

        nitrogen_uptake.update_all(crop_type, time)

        yields.update_all(crop_type, time)
       
        # Other daily calculations to be made

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

            self.line = 16

            #
            # CONSTANTS
            #
            self.crop_name = data['crop_name']
            self.crop_type = data['crop_type']
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
            
            self.E_t = data['E_t']         # maximum plant transpiration on a given day
            self.beta_w = data['beta_w']   # water-use distribution parameter
            self.epco = data['epco']

            #===================================================================
            ''' Nitrogen Fixation Data '''
            
            #===================================================================
            ''' Nitrogen Uptake Data '''
            
            self.bio_N_opt = 0
            self.bio_N = 0

            self.fr_n1 = data["fr_p1"]
            self.fr_n2 = data["fr_p2"]
            self.fr_n3 = data["fr_p3"]
            self.fr_n3ish = data["fr_p3ish"]

            self.fr_N = 0
            self.fr_N_up = 0
            #===================================================================
            ''' Phosphorus Uptake Data '''
            
            self.bio_P_opt = 0
            self.bio_P = 0

            self.fr_PHU_50 = data["fr_PHU_50"]
            self.fr_PHU_100 = data["fr_PHU_100"]
            self.fr_p1 = data["fr_p1"]
            self.fr_p2 = data["fr_p2"]
            self.fr_p3 = data["fr_p3"]
            self.fr_p3ish = data["fr_p3ish"]

            self.fr_P = 0
            self.P_up = 0

            #===================================================================
            ''' Hydrology Data '''
            
            self.water_actual_up = 0
            self.Et = 0

            self.Ea = 0
            self.Ea_sum = 0

            self.Eo = 0
            self.Eo_sum = 0

            #===================================================================
            ''' Yields Data '''

            self.HI_max = 0
            self.HI_min = data["HI_min"]
            self.HI_actual = 0
            self.HI_opt = data["HI_opt"]

            self.harvest_eff = data["harvest_eff"]

            # Note that currently gamma wu is only accurate on harvest date because
            # hard coded inputs for Ea_sum and Eo_sum are set for those days
            self.gamma_wu = 0

            self.bio_AG = 0
            self.yield_max = 0
            self.yield_actual = 0

            #===================================================================
            ''' Testing Data '''

            self.test_water_actual_up = data["TESTING_water_up"]
            self.test_Et = data["TESTING_Et"]

            self.test_bio_P = data["TESTING_bioP"]
            self.test_bio_P_opt = data["TESTING_bioP_opt"]
            self.test_bio_N = data["TESTING_bioN"]
            self.test_bio_N_opt = data["TESTING_bioN_opt"]

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


        #-----------------------------------------------------------------------
        # Method: calculate_water_uptake
        #-----------------------------------------------------------------------
        ''' Maybe add Soil as an arg because we will need the soil layer information
            for this function
        '''
        def calculate_water_uptake(self, T_min, T_max, H_radiation, soil):
            ''' '''

            #
            # 1) Root development in Soil
            #
            fr_root = 0.4 - 0.2*self.fr_PHU

            if ((self.crop_type == "perennial") or
                (self.crop_type == "annual" and self.fr_PHU > 0.4)):
                z_root = self.z_root_max
            else: #crop_type == "annual" and self.fr_PHU <= 0.4
                z_root = 2.5 * self.fr_PHU * self.z_root_max


            #
            # 2) Maximum potential water uptake
            #
            def max_pos_water_uptake(z):
                w_up_z = ((self.E_t / (1.0 - exp(-self.beta_w))) *
                      floor(1.0 - exp(-self.beta_w * z/z_root)))
                return w_up_z
            
            def max_pos_water_uptake_layer(upper_boundary, lower_boundary):
                w_up_zu = max_pos_water_uptake(upper_boundary)
                w_up_zl = max_pos_water_uptake(lower_boundary)
                return w_up_zl - w_up_zu


            #
            # 3) Impact of low soil water content on potential water uptake
            #
            sum_adj_w_up = 0 
            pos_uptake_overlying_layers = 0
            sum_avail_soil_water_overlying = 0
            first_layer = True
            prev_ly_depth = 0
            for ly in soil.listOfSoilLayers:
                if first_layer:
                    sum_adj_w_up = max_pos_water_uptake_layer(prev_ly_depth, ly.bottomDepth)
                    
                    first_layer = False
                else:
                    pos_uptake_overlying_layers = sum_adj_w_up
                    w_demand = pos_uptake_overlying_layers - sum_avail_soil_water_overlying
                    if w_demand < 0:
                        w_demand = 0
                    adj_w_up = max_pos_water_uptake_layer(
                        prev_ly_depth, ly.bottomDepth) + w_demand * self.epco
                    
                    sum_adj_w_up += adj_w_up
                    
                sum_avail_soil_water_overlying += ly.currentSoilWaterMM
                prev_ly_depth = ly.bottomDepth
            

            #
            # 4) Actual water uptake by a plant
            #


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


