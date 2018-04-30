################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: crop.py
Description:
Author(s): Kass Chupongstimun, kass_c@hotmail.com
'''
################################################################################

from numpy import exp, log, floor

#-------------------------------------------------------------------------------
# Function: daily_crop_routine
#-------------------------------------------------------------------------------
def daily_crop_routine(crop, weather, time):
    '''
    TODO: Add DocString
    '''

    for _,crop_type in crop.crops_list.items():
        crop_type.calculate_max_dBiomass(
            weather.T_min[day], weather.T_max[day], weather.radiation[day]
        )

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
            self.T_base_min = data['min_temp_for_growth']
            self.T_base_max = data['max_temp_for_growth']
            self.PHU = data['HU_for_maturity']
            self.fr_PHU_sen = data['fr_PHU_sen']
            self.fr_PHU_1 = data['fr_PHU_1']
            self.fr_PHU_2 = data['fr_PHU_2']
            self.fr_LAI_1 = data['fr_LAI_1']
            self.fr_LAI_2 = data['fr_LAI_2']
            self.LAI_max = data['LAI_max']
            self.kl = data['kl']
            self.RUE = data['radiation_use_efficiency']
            self.T_base = (self.T_base_min + self.T_base_max) / 2.0

            #
            # "Static" values
            #
            self.start_day = 0
            self.accumulated_HU = 0.0
            self.fr_LAI_max = 0.0

            #
            # Daily Output Values
            #
            self.LAI = 0.0
            self.dBiomass_max = 0.0


        #-----------------------------------------------------------------------
        # Method: calculate_start_growth_day
        #-----------------------------------------------------------------------
        def calculate_start_growth_day(self, T_min, T_max, T_avg):
            '''
            TODO: Add DocString
            '''

            if self.crop_type == "annual":
                self.start_day = planting_date
            else: # crop_type == "perennial"
                for d in range(len(T_avg)):
                    if T_avg > self.T_base_min:
                        self.start_day = d

        #-----------------------------------------------------------------------
        # Method: calculate_max_dBiomass
        #-----------------------------------------------------------------------
        def calculate_max_dBiomass(self, T_min, T_max, H_radiation):
            '''Calculates the maximum potential biomass increase.

            Calculates the maximum potential biomass increase on the day. The
            value is saved in the variable dBiomass_max.

            Args:
                T_min (float): Minimum temperature of the day
                T_max (float): Maximum temperature of the day
                H_radiation (float): Incident solar radiation

            Internally Saved Values:
                accumulated_HU (float): Accumulated Heat Units upto current day
                prev_LAI (float): LAI from previous simulation cycle

            Daily Outputs Calculated:
                LAI (float): Leaf Area Index
                dBiomass_max (float): Maximum potential biomass increase
            '''

            #
            # 1) Calculate Heat Units
            #
            if T_min < T_base_min:
                T_HU_min = T_base_min
            else:
                T_HU_min = T_min

            if T_max > T_base_max:
                T_HU_max = T_base_max
            else:
                T_HU_max = T_max

            T_HU = (T_HU_min + T_HU_max) / 2.0

            # ASSUMED T_base is AVG of T_base_min and T_base_max????
            if T_HU < self.T_base:
                HU = 0.0
            else:
                HU = T_HU - self.T_base

            self.accumulated_HU += HU
            # UPTO and INCLUDING current day??????

            #
            # 2) Calculate accumulated fraction of potential Heat Units
            #
            fr_PHU = self.accumulated_HU / self.PHU
            self.fr_PHU = fr_PHU

            #
            # 3) Calculate Leaf Area Index (LAI)
            #

            # At this point, self.LAI contains the LAI for the previous day
            # preserve it in this variable
            prev_LAI = self.LAI
            prev_fr_LAI_max = self.fr_LAI_max

            l2 = ( (log(abs((self.fr_PHU_1 / self.fr_LAI_1) - self.fr_PHU_1)) -
                    log(abs((self.fr_PHU_2 / self.fr_LAI_2) - self.fr_PHU_2)))
                 / (self.fr_PHU_2 - self.fr_PHU_1) )
            l1 = ( log(abs((self.fr_PHU_1 / self.fr_LAI_1) - self.fr_PHU_1)) +
                    (l2 * self.fr_PHU_1) )

            self.fr_LAI_max = fr_PHU / (fr_PHU + exp(l1 - l2 * fr_PHU))

            dLAI = ( (self.fr_LAI_max - prev_fr_LAI_max) *
                      self.LAI_max *
                      (1.0 - exp(5.0 * (prev_LAI - self.LAI_max))) )

            if fr_PHU < self.fr_PHU_sen:
                self.LAI = prev_LAI + dLAI
            else:
                self.LAI = self.LAI_max * ((1.0 - fr_PHU) /
                           (1.0 - self.fr_PHU_sen))

            #
            # 4) Calculate maximum potential Biomass Accumulation
            #
            H_phosyn = 0.5 * H_radiation * (1.0 - exp(-self.kl * self.LAI))
            self.dBiomass_max = self.RUE * H_phosyn

        #-----------------------------------------------------------------------
        # Method: calculate_water_uptake
        #-----------------------------------------------------------------------
        def calculate_water_uptake(self, T_min, T_max, H_radiation):
            ''' '''

            #
            # 1) Root development in Soil
            #
            fr_root = 0.4 - 0.2*self.fr_PHU

            if ((self.crop_type == "perennial") or
                (self.crop_type == "annual" and self.fr_PHU > 0.4)):
                z_root = z_root_max
            else: #crop_type == "annual" and self.fr_PHU <= 0.4
                z_root = 2.5 * self.fr_PHU * z_root_max


            #
            # 2) Maximum potential water uptake
            #
            w_up_z = ((E_t / (1.0 - exp(-beta_w))) *
                      floor(1.0 - exp(-beta_w * z/z_root)))
            w_up_ly = w_up_zl - w_up_zu


            #
            # 3) Impact of low soil water content on potential water uptake
            #

            #
            # 4) Actual water uptake
            #


    #---------------------------------------------------------------------------
    # Method: annual_reset
    #---------------------------------------------------------------------------
    def annual_reset(self):
        '''
        TODO: Add DocString
        '''
        pass

