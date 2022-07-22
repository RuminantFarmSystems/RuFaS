from .base_crop import BaseCrop

# TODO: add overall description of Triticale class, along with 
#description of attributes - GitHub Issue #170
class Triticale(BaseCrop):

    def __init__(self, crop_name, data):
        super().__init__()

        """GENERAL PLANT INFO"""

        triticale_data = data
        self.plant_years = triticale_data['plant_years']
        self.repeat = triticale_data['repeat']
        self.planting_day = triticale_data['planting_day']
        self.harvest_day = triticale_data['harvest_day']
        self.harvest_type = triticale_data['harvest_type']
        self.planting_order = triticale_data['planting_order'].lower()
        self.extracted = triticale_data['extracted']

        self.crop_name = crop_name
        self.crop_type = 'annual'
        self.harvest_quality = 'null'
        self.feed_id = '125g'
        self.raw_id = 125

        self.kill_day = -1
        self.kill_year = True
        self.planted = False
        self.growing = False
        self.killed = False

        self.fix_nitrogen = False

        # ===================================================================
        ''' HEAT UNIT DATA '''

        # input
        self.T_base_min = 0
        self.T_base_max = 30  # TODO: GitHub Issue #157
        self.PHU = 1600  # 1550-1680  # TODO Potential heat units unknown - GitHub Issue #154

        # Internally calculated input
        self.accumulated_HU = 0.0
        self.prev_accumulated_HU = 0.0

        # output
        self.fr_PHU = 0.0
        self.prev_fr_PHU = 0.0

        # ===================================================================
        ''' LEAF AREA INDEX (LAI) DATA '''

        # input
        self.fr_PHU_1 = 0.05
        self.fr_PHU_2 = 0.45
        self.fr_LAI_1 = 0.05
        self.fr_LAI_2 = 0.95
        self.fr_PHU_sen = 0.90
        self.fr_PHU_harvest = 1.0
        self.fr_PHU_harvest_min = 0.7
        self.LAI_max = 4
        self.LAI_min = 0

        # Internally calculated input
        self.prev_fr_LAI_max = 0
        self.fr_LAI_max = 0

        # output
        self.prev_LAI_actual = 0
        self.LAI_actual = 0

        # ===================================================================
        ''' ROOT DEPTH DATA '''

        # input
        self.z_root_max = 1300

        # Internally calculated input
        self.fr_root = 0

        # output
        self.z_root = 0

        # ===================================================================
        ''' BIOMASS DATA '''

        # input
        self.kl = 0.65  # TODO: GitHub Issue #157
        self.RUE = 30
        self.T_opt = 18

        # Internally calculated input
        self.gamma_reg = 0
        self.d_biomass_max = 0
        self.d_biomass_actual = 0.0

        # output
        self.biomass_actual = 0
        self.prev_biomass_actual = 0

        # ===================================================================
        ''' Soil Water Uptake Data '''

        self.beta_w = 10  # TODO: water-use distribution parameter - GitHub Issue #157
        self.epco = 0.5  # TODO: GitHub Issue #157

        self.water_actual_up = 0
        self.water_uptake_each_layer = []

        # ===================================================================
        ''' Nitrogen Uptake Data '''

        self.N_fix = 0.0

        self.beta_n = 10

        self.bio_N_opt = 0
        self.bio_N = 0

        self.fr_n1 = 0.0663
        self.fr_n2 = 0.0255
        self.fr_n3 = 0.0148
        self.fr_n3ish = 0.01481

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
        self.fr_p1 = 0.0053
        self.fr_p2 = 0.0020
        self.fr_p3 = 0.0012
        self.fr_p3ish = 0.00121

        self.fr_P = 0
        self.P_up = 0
        self.act_P_up_each_layer = []
        self.P_act_up = 0

        # ===================================================================
        ''' Yields Data '''

        self.HI_max = 0
        self.HI_min = 0.2
        self.HI_actual = 0
        self.HI_opt = 0.4

        self.harvest_eff = 0.9

        self.gamma_wu = 0

        self.biomass_dry_down_percent = 0.0  # TODO: Hard coded total dry down until daily method is modeled - GitHub Issue #156
        self.DM_harvest_percent = 0.0001  # TODO: Hard coded dry matter percent at harvest - GitHub Issue #155
        self.NDF_harvest_percent = 0.416

        self.bio_AG = 0
        self.yield_max = 0
        self.yield_actual = 0
        self.NDF_yield = 0.0
        self.N_yield = 0
        self.P_yield = 0

        self.N_yield_annual = 0.0
        self.P_yield_annual = 0.0
        self.DM_yield_annual = 0.0
        self.NDF_yield_annual = 0.0
        self.yield_annual = 0
