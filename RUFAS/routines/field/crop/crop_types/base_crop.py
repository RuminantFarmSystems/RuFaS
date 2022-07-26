class BaseCrop:
    """BaseCrop is the parent class of all Crop type objects
       and their respective classes. Crop attributes are initialized here first
       and eventually overridden by the instantiation of a specific Crop object.
       Further description of each attribute is provided beneath the attribute's
       initialization if clarification is needed.
    """
    def __init__(self):
        """create an instance of BaseCrop class"""
        ##  id variables
        self.crop_name = 'null'
        """str: name of the crop: alfalfa, corn, etc."""
        self.crop_type = ''  # ToDo: What strings are accepted? - GitHub Issue #174
        """str: the growing type of the crop: perennial, annual ..."""
        self.harvest_quality = 'null'  # ToDo: don't know what harvest quality is - GitHub Issue #168
        self.feed_id = 'null'
        """str: the ID of the feed to be modified, ending in 'g' if it is a grown feed"""
        self.raw_id = 'null'
        """str: the raw ID of the feed to be modified"""

        ## planting information
        """create an instance of ``BaseCrop``"""
        self.plant_years = []
        """:obj:`list` of :obj:`float`: a list of years in which the crop will be grown"""
        self.repeat = 0
        """float: the number of years between each grow year for the crop"""
        self.planting_day = 0
        """float: the day of the year that the crop will be first planted (Julian calendar)"""
        self.harvest_day = 0
        """float: the day of the year that the crop will be harvested (Julian calendar)"""
        self.harvest_type = ''  # ToDo: What strings are accepted? - GitHub Issue #174
        """str: the harvest schedule that the crop will be on: scheduled, optimal..."""
        self.planting_order = ''  # ToDo: What strings are accepted? - GitHub Issue #174
        """str: in the case of double cropping, the order in which the crop will be planted"""

        ## starting points for crop status
        self.planted = False
        """bool: has the crop been planted or not?"""
        self.growing = False
        """bool: is the crop is currently growing?"""
        self.killed = False
        """bool: has been killed?"""
        self.kill_year = False
        """bool: is this the year the crop is killed?"""
        self.kill_day = -1
        """float: Julian_day on which the crop will be killed"""
        self.extracted = False
        """bool: was the crop extracted from the field or not? 
             This is independent of whether or not the crop was killed.
        """

        ## heat units
        self.T_base_min = 10  # pseudocode C.2.A.3
        """minimum temperature required for growth (Celsius)"""
        self.T_base_max = 30  # pseudocode C.2.A.4
        """maximum temperature required to sustain growth (Celsius)"""
        self.PHU = 800  # psuedocode C.2.B.1
        """crop-specific total heat units required for maturity"""

        self.accumulated_HU = 0  # pseudocode C.2.B.1
        """Heat units accumulated including the current day of the simulation"""
        self.prev_accumulated_HU = 0  # pseudocode C.2.B.1
        """Heat units accumulated excluding the current day of the simulation"""
        self.fr_PHU = 0  # pseudocode C.2.B.1
        """float: fraction of Potential Heat Units"""
        self.prev_fr_PHU = 0  # pseudocode C.2.B.1
        """Fraction of PHU accumulated excluding current day of simulation"""

        ## LAI
        self.fr_PHU_1 = 0.15  # psuedocode C.8.A
        """first PHU shape coefficient, used in LAI calculations"""
        self.fr_PHU_2 = 0.50  # psuedocode C.8.A
        """second PHU shape coefficient, used in LAI calculations"""
        self.fr_LAI_1 = 0.01  # psuedocode C.8.A.2
        """first LAI shape coefficient, used in LAI calculations"""
        self.fr_LAI_2 = 0.95  # psuedocode C.8.A.1
        """second LAI shape coefficient, used in LAI calculations"""
        self.fr_PHU_sen = 0.90  # psuedocode C.8.A.6
        """crop-specific fraction of PHU, at which senescence becomes dominant growth process"""
        self.fr_PHU_harvest = 1  # psuedocode C.10.A.1
        """fraction of PHU at harvest"""
        self.fr_PHU_harvest_min = 0.7  # psuedocode C.11.C.2
        """minimum fraction of PHU acquired to warrant harvest"""
        self.LAI_max = 3  # psuedocode C.8.A.4
        """crop-specific maximum LAI"""
        self.LAI_min = 0  # ToDo: missing psuedocode - GitHub Issue #168
        """crop-specific minimum possible LAI"""
        self.prev_fr_LAI_max = 0  # psuedocode C.8.A.3
        """accumulated LAI fraction for the previous day"""
        self.fr_LAI_max = 0  # psuedocode C.8.A.3
        """accumulated LAI fraction for the current day"""
        self.prev_LAI_actual = 0  # psuedocode C.8.A.4
        """calculated LAI for the previous day"""
        self.LAI_actual = 0
        """float: calculated LAI for the current day"""

        ## root depth
        self.z_root_max = 1500  # pseudocode C.3.A.2
        """maximum depth of root development (mm)"""
        self.fr_root = 0  # pseudocode C.3.A.1
        """fraction of total biomass partitioned to roots on current day"""
        self.z_root = 0  # pseudocode C.3.A.2
        """depth of root development (mm)"""

        ## biomass
        self.kl = 0.65  # psuedocode C.9.A.2
        """light extinction coefficient"""
        self.RUE = 20  # psuedocode C.9.A.2
        """crop-specific radiation use efficiency"""
        self.T_opt = 25  # psuedocode C.7.B.2
        """crop-specific optimal temperature for growth"""
        self.gamma_reg = 0  # psuedocode C.9.A.3
        """plant growth factor (0-1)"""
        self.d_biomass_max = 0  # psuedocode C.9.A.3
        """maximum potential increase in biomass for a given day"""
        self.d_biomass_actual = 0 # psuedocode C.9.A.3
        """calculated increase in biomass"""
        self.biomass_actual = 0  # psuedocode C.9.A.3 # ToDo: What are the units? - GitHub Issue #174
        """calculated biomass for the current day"""
        self.prev_biomass_actual = 0  # psuedocode C.9.A.3
        """calculated biomass for the previous day"""

        ## water uptake
        self.epco = 0  # psuedocode C.4.B.2
        """float: plant uptake compensation factor, a value between 0.01 and 1.00"""
        self.beta_w = 0  # psuedocode C.4.A.1  # TODO: taken from corn - Github issue #154
        """water-use distribution parameter"""
        self.water_actual_up = 0  # psuedocode C.4.A.2
        """water uptake (mm)"""
        self.water_uptake_each_layer = []  # psuedocode C.4.A.2
        """water uptake from each layer (mm)"""

        ## nitrogen uptake
        self.beta_n = 10
        self.fr_n1 = 0.04
        self.fr_n2 = 0.03
        self.fr_n3 = 0.02
        self.fr_n3ish = 0.02
        self.N_fix = 0
        """float: Amount of nitrogen added to the plant biomass by fixation (kg/ha)"""
        self.bio_N_opt = 0
        self.bio_N = 0
        """float: Actual mass of nitrogen stored in plant material (kg/ha)"""
        self.fr_N = 0
        "float: Fraction of Nitrogen"
        self.N_up = 0
        self.act_N_up_each_layer = []
        self.N_actual_up = 0

        ## phosphorus uptake
        self.beta_p = 10
        self.fr_PHU_50 = 0.5
        self.fr_PHU_100 = 1.0
        self.fr_p1 = 0.004
        self.fr_p2 = 0.003
        self.fr_p3 = 0.002
        self.fr_p3ish = 0.002
        self.bio_P_opt = 0
        self.bio_P = 0
        """float: Actual mass of phosphorus stored in plant material (kg/ha)"""
        self.fr_P = 0
        self.P_up = 0
        self.act_P_up_each_layer = []
        self.P_act_up = 0

        ## yield
        self.HI_max = 0  # ToDo: what is HI_max, and why is it 0?
        """float: Maximum harvest index"""
        self.HI_min = 0
        """float: harvest index for the plant in drought conditions"""
        self.HI_actual = 0
        """float: Actual harvest index"""
        self.HI_opt = 0.9
        self.harvest_eff = 0.9
        self.gamma_wu = 0
        self.biomass_dry_down_percent = 0
        self.DM_harvest_percent = 0.15
        self.NDF_harvest_percent = 0.42
        self.bio_AG = 0
        """float: Above ground biomass (kg/ha)"""
        self.bio_BG = 0
        """float: Below ground biomass (kg/ha)"""
        self.yield_max = 0
        self.yield_actual = 0
        """float: Actual crop yield at harvest (kg/ha)"""
        self.NDF_yield = 0
        self.N_yield = 0
        self.P_yield = 0
        self.N_yield_annual = 0
        self.P_yield_annual = 0
        self.NDF_yield_annual = 0
        self.yield_annual = 0
        """float: Annual crop yield (kg/ha)"""










