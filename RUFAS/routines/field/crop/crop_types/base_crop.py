class BaseCrop:

    """
        Description: 
            BaseCrop is the parent class of all Crop type objects
            and their respective classes. Crop attributes are initialized here first
            and eventually overriden by the instantiation of a specific Crop object.
            Further description of each attribute is provided beneath the attribute's 
            initialization if clarification is needed.
        """

    def __init__(self):

        self.plant_years = []
        """List of years that the crop will be grown"""

        self.repeat = 0
        """The number of years between each grow year for the crop"""

        self.planting_day = 0
        """The day of the year that the crop will be first planted (Julian calendar)"""

        self.harvest_day = 0
        """The day of the year that the crop will be harvested (Julian calendar)"""

        self.harvest_type = ''
        """The harvest schedule that the crop will be on: scheduled, optimal..."""

        self.planting_order = ''
        """In the case of double cropping, the order in which the crop will be planted"""

        self.extracted = False
        # TODO: figure out what this means. 
        #   Guess is that it is biomass extracted (or not) into the residue.

        self.crop_name = 'null'
        """name of the crop: alfalfa, corn, etc."""
        self.crop_type = ''
        """the growing type of the crop: perennial, annual ..."""
        self.harvest_quality = 'null'
        #TODO: don't know what harvest quality is
        self.feed_id = 'null'
        """the ID of the feed to be modified, ending in 'g' if it is a grown feed"""
        self.raw_id = 'null'
        """the raw ID of the feed to be modified"""

        self.planted = False
        """boolean denoting whether crop has been planted or not"""
        self.growing = False
        """boolean denoting whether the crop is growing or not"""
        self.killed = False
        """boolean denoting whether the crop has been killed or not"""
        

        # Necessary variables for a null crop to run
        # These variables are used within the soil module and must
        # be declared and initialized even when a crop is not growing
        self.fr_PHU = 0
        """Fraction of Potential Heat Units"""
        self.fr_N = 0
        "Fraction of Nitrogen"
        self.LAI_actual = 0
        """Actual Leaf Area Index"""
        self.z_root = 0
        """depth of root development in the soil (mm)"""
        self.biomass_actual = 0
        """total plant biomass on a given day"""
        self.epco = 0
        """plant uptake compensation factor, a value between 0.01 and 1.00"""
        self.N_fix = 0.0
        """Amount of nitrogen added to the plant biomass by fixation (kgN/ha)"""
        self.bio_N = 0
        """Actual mass of nitrogen stored in plant material (kg N/ha)"""
        self.bio_P = 0
        """Actual mass of phosphorus stored in plant material (kg P/ha)"""
        self.bio_AG = 0
        """Above ground biomass (kg/ha)"""
        self.bio_BG = 0
        """Below ground biomass (kg/ha)"""
        self.HI_actual = 0
        """Actual harvest index"""
        self.yield_actual = 0
        """Actual crop yield at harvest (kg/ha)"""
        self.yield_annual = 0
        """Annual crop yield""" 
        self.HI_min = 0
        """harvest index for the plant in drought conditions"""
        self.HI_max = 0
        """Maximum harvest index"""
