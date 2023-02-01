from .base_crop import BaseCrop
from RUFAS.output_manager import OutputManager

om = OutputManager()


class TallFescue(BaseCrop):

    def __init__(self, crop_name, data):
        super().__init__()

        """GENERAL PLANT INFO"""
        tall_fescue_data = data
        self.plant_years = tall_fescue_data['plant_years']
        self.repeat = tall_fescue_data['repeat']
        self.planting_day = tall_fescue_data['planting_day']
        self.harvest_day = tall_fescue_data['harvest_day']

        info_map = {"class": self.__class__.__name__,
                    "function": self.__init__.__name__,
                    "crop_name": crop_name, 
                    "tall_fescue_data": vars(data), }

        if tall_fescue_data['harvest_type'] != 'optimal':
            harvest_type_warning = "Perennial crops are always optimally harvested"
            info_map["harvest_type"] = tall_fescue_data["harvest_type"]
            om.add_warning("harvest_type", harvest_type_warning, info_map)

        self.harvest_type = 'optimal'

        self.crop_name = crop_name
        self.crop_type = 'perennial'
        self.harvest_quality = 'null'

        self.feed_id = '56g'
        self.raw_id = 56

        self.kill_day = -1
        self.kill_year = False
        self.planted = False
        self.growing = False

        self.fix_nitrogen = False

        # ===================================================================
        ''' HEAT UNIT DATA '''

        # input
        self.T_base_min = 10  # unknown
        self.T_base_max = 40
        self.PHU = 648

        # Internally calculated input
        self.accumulated_HU = 0.0
        self.prev_accumulated_HU = 0.0
        self.fr_PHU_harvest_min = 0.9

        # output
        self.fr_PHU = 0.0
        self.prev_fr_PHU = 0.0

        # ===================================================================
        ''' LEAF AREA INDEX (LAI) DATA '''

        # input
        self.fr_PHU_1 = 0.15
        self.fr_PHU_2 = 0.5
        self.fr_LAI_1 = 0.01
        self.fr_LAI_2 = 0.95
        self.fr_PHU_sen = 0.8
        self.fr_PHU_harvest = 0.3
        self.LAI_max = 4
        self.LAI_min = 0.75

        # Internally calculated input
        self.prev_fr_LAI_max = 0
        self.fr_LAI_max = 0

        # output
        self.prev_LAI_actual = 0
        self.LAI_actual = 0

        # ===================================================================
        ''' ROOT DEPTH DATA '''

        # input
        self.z_root_max = 2000  # maximum depth of root development

        # Internally calculated input
        self.fr_root = 0

        # output
        self.z_root = 0

        # ===================================================================
        ''' BIOMASS DATA '''

        # input
        self.kl = 0.65
        self.RUE = 30
        self.T_opt = 15

        # Internally calculated input
        self.gamma_reg = 0
        self.d_biomass_max = 0
        self.d_biomass_actual = 0.0

        # output
        self.biomass_actual = 0
        self.prev_biomass_actual = 0

        # ===================================================================
        ''' Soil Water Uptake Data '''

        self.beta_w = 10  # water-use distribution parameter  # corn  # unknown
        self.epco = 0.5

        self.water_actual_up = 0
        self.water_uptake_each_layer = []

        # ===================================================================
        ''' Nitrogen Uptake Data '''

        self.N_fix = 0.0

        self.beta_n = 10

        self.bio_N_opt = 0
        self.bio_N = 0

        self.fr_n1 = 0.0560
        self.fr_n2 = 0.0210
        self.fr_n3 = 0.0120
        self.fr_n3ish = 0.0121

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
        self.fr_p1 = 0.0099
        self.fr_p2 = 0.0022
        self.fr_p3 = 0.0019
        self.fr_p3ish = 0.00191

        self.fr_P = 0
        self.P_up = 0
        self.act_P_up_each_layer = []
        self.P_act_up = 0

        # ===================================================================
        ''' Yields Data '''

        self.HI_max = 0
        self.HI_min = 0.9
        self.HI_actual = 0
        self.HI_opt = 0.9

        self.harvest_eff = 0.9

        self.gamma_wu = 0

        self.biomass_dry_down_percent = 0.0
        self.DM_harvest_percent = 0.0001  # TODO: Hard coded dry matter percent at harvest
        self.NDF_harvest_percent = 0.416

        self.bio_AG = 0
        self.yield_max = 0
        self.yield_actual = 0
        self.NDF_yield = 0.0
        self.N_yield = 0
        self.P_yield = 0

        self.N_yield_annual = 0.0
        self.P_yield_annual = 0.0
        self.NDF_yield_annual = 0.0
        self.yield_annual = 0
