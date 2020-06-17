

class Soybean:

    def __init__(self, data):
        """GENERAL PLANT INFO"""

        soy_data = data['soybean']
        self.grow_years = soy_data['grow_years']
        self.repeat = soy_data['repeat']
        self.planting_date = soy_data['planting_date']
        self.harvest_date = soy_data['harvest_date']
        self.harvest_type = soy_data['harvest_type']

        self.crop_name = 'soybean'
        self.crop_type = 'annual'

        self.kill_day = -1
        self.kill_year = True
        self.planted = False
        self.growing = False

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
        self.fr_PHU_harvest = 1.0  # TODO: If soybean has drydown, this is 1.2
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
        self.d_biomass_max = 0
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
        self.bio_BG = 0
        self.bio_BG_DM = 0
        self.yield_max = 0
        self.yield_actual = 0
        self.yield_N = 0
        self.yield_P = 0

        self.yield_annual = 0
