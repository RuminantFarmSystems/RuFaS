from .base_crop import BaseCrop

# Define global variables containing corn parameters
# Keeping them separate from the Class definitions allows for them to be changed before running
# RUFAS. This is important for the validation module.
# ToDo: Check that the only manually initiated attributes in Corn are "internally calculated" and "output" variables
# ToDo: Also, check that only values that actually make sense to change be includied in this dictionary
CornConfigData = {"T_base_min": 10, # Heat Unit Data ----v
                  "T_base_max": 30,
                  "PHU": 1200,
                  "fr_PHU_1": 0.15,  # LAI data ----v
                  "fr_PHU_2": 0.50,
                  "fr_LAI_1": 0.05,
                  "fr_LAI_2": 0.95,
                  "fr_PHU_sen": 0.90,
                  "fr_PHU_harvest": 1.2,
                  "fr_PHU_harvest_min": 0.7,
                  "LAI_max": 3,
                  "LAI_min": 0,
                  "z_root_max": 2000,  # root depth data ----v
                  "kl": 0.65,  # biomass data ----v
                  "RUE": 39,
                  "T_opt": 25,
                  "beta_w": 10,  # water use data ----v
                  "epco": 0.5,
                  "N_fix": 0.0,  # nitrogen uptake data ----v
                  "beta_n": 10,
                  "fr_n1": 0.047,
                  "fr_n2": 0.0177,
                  "fr_n3": 0.0138,
                  "fr_n3ish": 0.01381,
                  "beta_p": 10,  # phosphorus uptake data ----v
                  "fr_PHU_50": 0.5,
                  "fr_PHU_100": 1.0,
                  "fr_p1": 0.0048,
                  "fr_p2": 0.0018,
                  "fr_p3": 0.0014,
                  "fr_p3ish": 0.00141,
                  "HI_max": 0,  # yields data ----v
                  "HI_min": 0.3,
                  "HI_actual": 0,
                  "HI_opt": 0.6,
                  "harvest_eff": 0.9,
                  "DM_harvest_percent": 0.35,  # TODO: Hard coded dry matter percent at harvest
                  "gamma_wu": 0,
                  "biomass_dry_down_percent": 0.0,
                  "NDF_harvest_percent": 0.0}


class Corn(BaseCrop):
    def __init__(self, crop_name, data):
        super().__init__()

        """GENERAL PLANT INFO"""

        corn_data = data
        self.plant_years = corn_data['plant_years']
        self.repeat = corn_data['repeat']
        self.planting_day = corn_data['planting_day']
        self.harvest_day = corn_data['harvest_day']
        self.harvest_type = corn_data['harvest_type']
        self.planting_order = corn_data['planting_order'].lower()
        self.extracted = corn_data['extracted']

        self.crop_name = crop_name
        self.crop_type = 'annual'
        self.harvest_quality = 'null'
        self.raw_id = 34
        self.feed_id = '34g'

        self.kill_day = -1
        self.kill_year = True
        self.planted = False
        self.growing = False
        self.killed = False

        self.fix_nitrogen = False

        # input config data - set an attribute for each key-value pair
        for key, val in CornConfigData.items():
            setattr(self, key, val)

        # initialize other variables
        ''' HEAT UNIT DATA '''
        # Internally calculated input
        self.accumulated_HU = 0.0
        self.prev_accumulated_HU = 0.0
        # output
        self.fr_PHU = 0.0
        self.prev_fr_PHU = 0.0

        ''' LEAF AREA INDEX (LAI) DATA '''
        # Internally calculated input
        self.prev_fr_LAI_max = 0
        self.fr_LAI_max = 0
        # output
        self.prev_LAI_actual = 0
        self.LAI_actual = 0

        ''' ROOT DEPTH DATA '''
        # Internally calculated input
        self.fr_root = 0

        # output
        self.z_root = 0

        ''' BIOMASS DATA '''
        # Internally calculated input
        self.gamma_reg = 0
        self.d_biomass_max = 0
        self.d_biomass_actual = 0.0
        # output
        self.biomass_actual = 0
        self.prev_biomass_actual = 0

        ''' Soil Water Uptake Data '''
        self.water_actual_up = 0
        self.water_uptake_each_layer = []

        ''' Nitrogen Uptake Data '''
        self.bio_N_opt = 0
        self.bio_N = 0

        self.fr_N = 0
        self.N_up = 0
        self.act_N_up_each_layer = []
        self.N_actual_up = 0

        ''' Phosphorus Uptake Data '''
        self.bio_P_opt = 0
        self.bio_P = 0

        self.fr_P = 0
        self.P_up = 0
        self.act_P_up_each_layer = []
        self.P_act_up = 0

        ''' Yields Data '''
        self.bio_AG = 0
        self.bio_BG = 0
        self.yield_max = 0
        self.yield_actual = 0
        self.NDF_yield = 0.0
        self.N_yield = 0
        self.P_yield = 0

        self.N_yield_annual = 0.0
        self.P_yield_annual = 0.0
        self.NDF_yield_annual = 0.0
        self.yield_annual = 0
