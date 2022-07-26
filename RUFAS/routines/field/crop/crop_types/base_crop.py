class BaseCrop:
    """BaseCrop is the parent class of all Crop type objects
       and their respective classes. Crop attributes are initialized here first
       and eventually overridden by the instantiation of a specific Crop object.
       Further description of each attribute is provided beneath the attribute's
       initialization if clarification is needed.
    """
    def __init__(self):
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
        self.extracted = False
        """bool: was the crop extracted from the field or not? 
             This is independent of whether or not the crop was killed.
        """
        self.crop_name = 'null'
        """str: name of the crop: alfalfa, corn, etc."""
        self.crop_type = ''  # ToDo: What strings are accepted? - GitHub Issue #174
        """str: the growing type of the crop: perennial, annual ..."""
        self.harvest_quality = 'null'  # ToDo: don't know what harvest quality is - GitHub Issue #168

        self.feed_id = 'null'
        """str: the ID of the feed to be modified, ending in 'g' if it is a grown feed"""
        self.raw_id = 'null'
        """str: the raw ID of the feed to be modified"""
        self.planted = False
        """bool: has the crop been planted or not?"""
        self.growing = False
        """bool: is the crop is currently growing?"""
        self.killed = False
        """bool: has been killed?"""
        
        # Necessary variables for a null crop to run
        # These variables are used within the soil module and must
        # be declared and initialized even when a crop is not growing
        self.fr_PHU = 0
        """float: fraction of Potential Heat Units"""
        self.fr_N = 0
        "float: Fraction of Nitrogen"
        self.LAI_actual = 0
        """float: Actual Leaf Area Index"""
        self.z_root = 0
        """float: depth of root development in the soil (mm)"""
        self.biomass_actual = 0  # ToDo: What are the units? - GitHub Issue #174
        """float: total plant biomass on a given day"""
        self.epco = 0
        """float: plant uptake compensation factor, a value between 0.01 and 1.00"""
        self.N_fix = 0.0
        """float: Amount of nitrogen added to the plant biomass by fixation (kg/ha)"""
        self.bio_N = 0
        """float: Actual mass of nitrogen stored in plant material (kg/ha)"""
        self.bio_P = 0
        """float: Actual mass of phosphorus stored in plant material (kg/ha)"""
        self.bio_AG = 0
        """float: Above ground biomass (kg/ha)"""
        self.bio_BG = 0
        """float: Below ground biomass (kg/ha)"""
        self.HI_actual = 0
        """float: Actual harvest index"""
        self.yield_actual = 0
        """float: Actual crop yield at harvest (kg/ha)"""
        self.yield_annual = 0  # ToDo: what are the units? - GitHub Issue #174
        """float: Annual crop yield (kg/ha)"""
        self.HI_min = 0
        """float: harvest index for the plant in drought conditions"""
        self.HI_max = 0
        """float: Maximum harvest index"""
