from .base_crop import BaseCrop


# TODO: add overall description of Alfalfa class, along with 
#  description of attributes - GitHub Issue #170
class Alfalfa(BaseCrop):

    """``Alfalfa`` is a child of the ``BaseCrop`` class, and one of the main crop types.
       Attributes of ``Alfalfa`` are derived from data collected for the crop.
       Attributes and functions unique to Alfalfa are documented below.
       See the inherited class ``BaseCrop`` for all other attributes and member functions.
    """

    def __init__(self, crop_name, data):
        """create an instance of ``Alfalfa``"""
        super().__init__()
        # crop data: override BaseCrop attributes
        alfalfa_data = data
        self.plant_years = alfalfa_data['plant_years']
        self.repeat = alfalfa_data['repeat']
        self.planting_day = alfalfa_data['planting_day']
        self.harvest_day = alfalfa_data['harvest_day']
        self.planting_order = alfalfa_data['planting_order'].lower()
        self.extracted = alfalfa_data['extracted']
        self.crop_name = crop_name

        # alfalfa-specific values
        self.harvest_type = 'optimal'
        self.crop_type = 'perennial'
        self.harvest_quality = 'null'
        self.raw_id = 1
        self.feed_id = '1g'
        self.fix_nitrogen = True
        """boolean indicating whether the crop can fix nitrogen"""

        # starting state parameters
        self.kill_day = -1
        """Julian day on which the crop will be killed"""
        self.kill_year = False
        self.planted = False
        self.growing = False
        self.killed = False

        # ---- HEAT UNIT DATA ----
        # input data
        self.T_base_min = 4
        """minimum temperature required for growth (Celsius)"""
        self.T_base_max = 43.33
        """maximum temperature required to sustain growth (Celsius)"""
        self.PHU = 800  # TODO: Potential heat units unknown - GitHub Issue #154
        """total heat units required for maturity"""
        # internally calculated values
        self.accumulated_HU = 0.0
        """Heat units accumulated including the current day of the simulation"""
        self.prev_accumulated_HU = 0.0
        """Heat units accumulated excluding the current day of the simulation"""
        # output values
        self.fr_PHU = 0.0
        self.prev_fr_PHU = 0.0
        """Fraction of PHU accumulated excluding current day of simulation"""

        # ToDo: I (morrowcj) believe that all hard-coded crop-specific parameters (many of those below) should be exist
        #  separate from this class, so that they can be updated as more data becomes available. This should
        #  NOT extend to parameters that are internally calculated or incremented, that are initialized with a
        #  non-value or a default starting value.
        #  For example, a crop_config.py file could contain dictionaries containing crop-specific parameter
        #  values (e.g., ALFALFA_PARS, CORN_PARS, etc.) and then those values can be implemented as attributes
        #  a loop with: ``for key, val in ALFALFA_PARS.items(): setattr(self, key, val)`` and changed on the fly
        #  (e.g., with input overrides). See corn.py in the seqv3_morrowcj branch for implementation.
        #  The attributes, then should all be defined and documented in the BaseCrop class.

        # ---- LEAF AREA INDEX (LAI) DATA ----
        # input
        self.fr_PHU_1 = 0.15
        self.fr_PHU_2 = 0.50
        self.fr_LAI_1 = 0.01
        self.fr_LAI_2 = 0.95
        self.fr_PHU_sen = 0.90
        self.fr_PHU_harvest = 1.2
        self.fr_PHU_harvest_min = 0.9
        self.LAI_max = 4
        self.LAI_min = 0.75
        # Internally calculated values
        self.prev_fr_LAI_max = 0
        self.fr_LAI_max = 0
        # output
        self.prev_LAI_actual = 0
        self.LAI_actual = 0

        # ---- ROOT DEPTH DATA ----
        # input
        self.z_root_max = 3000  # maximum depth of root development
        # Internally calculated input
        self.fr_root = 0
        # output
        self.z_root = 0

        # ---- BIOMASS DATA ----
        # input
        self.kl = 0.65
        self.RUE = 20
        self.T_opt = 25
        # Internally calculated input
        self.gamma_reg = 0
        self.d_biomass_max = 0
        self.d_biomass_actual = 0.0
        # output
        self.biomass_actual = 0
        self.prev_biomass_actual = 0

        # ---- Soil Water Uptake Data ----
        self.beta_w = 10  # water-use distribution parameter  # TODO: taken from corn - Github issue #154
        self.epco = 1
        self.water_actual_up = 0
        self.water_uptake_each_layer = []

        # ---- Nitrogen Uptake Data ----
        self.N_fix = 0.0
        self.beta_n = 10
        self.bio_N_opt = 0
        self.bio_N = 0
        self.fr_n1 = 0.0417
        self.fr_n2 = 0.0290
        self.fr_n3 = 0.0200
        self.fr_n3ish = 0.02001
        self.fr_N = 0
        self.N_up = 0
        self.act_N_up_each_layer = []
        self.N_actual_up = 0

        # ---- Phosphorus Uptake Data ----
        self.beta_p = 10
        self.bio_P_opt = 0
        self.bio_P = 0
        self.fr_PHU_50 = 0.5
        self.fr_PHU_100 = 1.0
        self.fr_p1 = 0.0035
        self.fr_p2 = 0.0028
        self.fr_p3 = 0.0020
        self.fr_p3ish = 0.00201
        self.fr_P = 0
        self.P_up = 0
        self.act_P_up_each_layer = []
        self.P_act_up = 0

        #  ---- Yields Data ----
        self.HI_max = 0
        self.HI_min = 0.9
        self.HI_actual = 0
        self.HI_opt = 0.9
        self.harvest_eff = 0.9
        self.gamma_wu = 0
        self.biomass_dry_down_percent = 0.0
        self.DM_harvest_percent = 0.15  # TODO: Hard coded dry matter percent at harvest - GitHub Issue #155
        self.NDF_harvest_percent = 0.416
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
