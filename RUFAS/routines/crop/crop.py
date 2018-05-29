################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: crop.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
'''
################################################################################

from math import exp, log, floor
import heat_units, leaf_area_index, root_depth, biomass
#-------------------------------------------------------------------------------
# Function: daily_crop_routine
#-------------------------------------------------------------------------------
def daily_crop_routine(crop, weather, time, soil):
    '''
    TODO: Add DocString
    '''
    T_min = weather.tMin[time.year][time.day]
    T_max = weather.tMax[time.year][time.day]


    for _,crop_type in crop.crops_list.items():
        heat_units.calculate_frPHU(crop_type, T_min, T_max)
        leaf_area_index.calculate_LAI_actual(crop_type)
        root_depth.calculate_z_root(crop_type)
        biomass.calculate_actual_Biomass(crop_type, time, weather)

       
        # Other daily calculations to be made

#-------------------------------------------------------------------------------
# Function: annual_crop_routine
#-------------------------------------------------------------------------------
def annual_crop_routine(crop, weather, time):
    '''
    TODO: Add DocString
    '''

    for _,crop_type in crop.crops.items():
        crop_type.calculate_start_growth_day(
            weather.T_min, weather.T_max, weather.T_avg
        )

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

        self.crops_list = {crop: self.CropType(data[crop]) for crop in data.keys()}

    #---------------------------------------------------------------------------
    # Class: CropType
    #---------------------------------------------------------------------------
    class CropType():

        def __init__(self, data):
            '''
            TODO: Add DocString
            '''

            #
            # CONSTANTS
            #
            self.crop_name = data['crop_name']
            self.crop_type = data['crop_type']
            self.planting_date = data['planting_date']
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
            self.fr_PHU = 0
            self.prev_fr_PHU = 0
            
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
            self.prev_fr_LAI_max = 0 # Need to figure out what this should be on the first day - Andy
            self.fr_LAI_max = 0
            
            # Outputs
            self.prev_LAI_actual = 0
            self.LAI_actual = 0
            
            #===================================================================
            ''' ROOT DEPTH DATA '''
            
            # Inputs
            self.z_root_max = data['z_root_max'] # maximum depth of root development
            
            # Outputs
            self.z_root = 0
            
            #===================================================================
            ''' BIOMASS DATA '''
            
            # Inputs
            self.kl = data['light extinction coefficient']
            self.RUE = data['radiation_use_efficiency']
            self.T_opt = data['T_opt']

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
            self.prev_bio_N_opt = 0
            
            self.prev_bio_N = 0
            self.bio_N = 0

            #===================================================================
            ''' Phosphorus Uptake Data '''
            
            self.bio_P_opt = 0
            self.prev_bio_P_opt = 0
            
            self.prev_bio_P = 0
            self.bio_P = 0
            
            #===================================================================
            ''' Hydrology Data '''
            
            self.water_actual_up = 0
            self.Et = 0
            #===================================================================
            ''' Yield Data '''
            
            #===================================================================
        #-----------------------------------------------------------------------
        # Method: calculate_start_growth_day
        #-----------------------------------------------------------------------
        def calculate_start_growth_day(self, T_min, T_max, T_avg):
            '''
            TODO: Add DocString
            '''

            if self.crop_type == "annual":
                self.start_day = self.planting_date
            else: # crop_type == "perennial"
                for d in range(len(T_avg)): # ?? is T_avg a 2d list. Is this right. -Andy
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
        pass

