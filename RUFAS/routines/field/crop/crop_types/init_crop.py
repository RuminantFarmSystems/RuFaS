from .base_crop import BaseCrop


class InitCrop(BaseCrop):
    def __init__(self, data):
        """A base crop class used when no crop is grown"""
        super().__init__()
        """GENERAL PLANT INFO"""

        self.data = data
        self.grow_years = []
        self.repeat = 0
        self.planting_date = 0
        self.harvest_date = 0
        self.harvest_type = ''

        self.crop_name = 'null'
        self.crop_type = ''
        self.harvest_quality = ''

        self.kill_day = -1
        self.kill_year = True
        self.planted = False
        self.growing = False

        self.fix_nitrogen = False

        """ HEAT UNIT DATA """

        # Args
        self.T_base_min = 0
        self.T_base_max = 0
        self.PHU = 0

        # Internally calculated inputs
        self.accumulated_HU = 0
        self.prev_accumulated_HU = 0
        self.fr_PHU_harvest_min = 0.7

        # Outputs
        self.fr_PHU = 0
        self.prev_fr_PHU = 0

        """ LEAF AREA INDEX (LAI) DATA """

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

        """ ROOT DEPTH DATA """

        # Inputs
        self.z_root_max = 0  # maximum depth of root development

        # Internally calculated inputs
        self.fr_root = 0

        # Outputs
        self.z_root = 0

        """ BIOMASS DATA """

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

        """ Soil Water Uptake Data """

        self.beta_w = 0
        self.epco = 0

        self.water_actual_up = 0
        self.water_uptake_each_layer = []

        """ Nitrogen Uptake Data """

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

        self.N_fix = 0.0

        """ Phosphorus Uptake Data """

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
        self.pot_N_up_each_layer = []
        self.P_act_up = 0

        """ Yields Data """

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

        self.yield_annual = 0
