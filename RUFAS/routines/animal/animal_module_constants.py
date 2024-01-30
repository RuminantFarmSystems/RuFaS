class AnimalModuleConstants:
    """
    A class used to store constants related to the animal module.
    """

    DEFAULT_MAX_STOCKING_DENSITY = 1.2
    """The default maximum stocking density for a pen. This value is used when a pen is created dynamically during the
    simulation."""

    DEFAULT_NUM_STALLS = 100
    """The default number of stalls to be created in a new pen if no specific value is provided."""

    DEFAULT_NUM_STALLS_FOR_CALF_PEN = 110
    """The default number of stalls to be created in a calf pen."""

    DEFAULT_NUM_STALLS_FOR_GROWING_PEN = 800
    """The default number of stalls to be created in a growing pen."""

    DEFAULT_NUM_STALLS_FOR_CLOSE_UP_PEN = 200
    """The default number of stalls to be created in a close-up pen."""

    DEFAULT_NUM_STALLS_FOR_LAC_COW_PEN = 850
    """The default number of stalls to be created in a lactating cow pen."""

    DEFAULT_NUM_STALLS_FOR_GROWING_AND_CLOSE_UP_PEN = 500
    """The default number of stalls to be created in a combined growing and close-up pen."""

    VERTICAL_DIST_TO_MILKING_PARLOR = 0.1
    """The default vertical distance from the animal pens to the milking parlor."""

    HORIZONTAL_DIST_TO_MILKING_PARLOR = 1.6
    """The default horizontal distance from the animal pens to the milking parlor."""

    DEFAULT_HOUSING_TYPE = 'open air barn'
    """The default housing type for animals in the simulation."""

    DEFAULT_BEDDING_TYPE = 'sawdust'
    """The default bedding material used in the pens."""

    DEFAULT_PEN_TYPE = 'freestall'
    """The default type of pen to be created in the simulation."""

    DEFAULT_MANURE_HANDLER = 'manual scraping'
    """The default method of manure handling used in those pens created dynamically during the simulation."""

    DEFAULT_MANURE_SEPARATOR = 'screw press'
    """The default manure separator system used in those pens created dynamically during the simulation."""

    DEFAULT_MANURE_STORAGE = 'slurry storage outdoor'
    """The default type of manure storage system used in those pens created dynamically during the simulation."""

    MONENSIN_CP_LOWER_BOUND = 15
    """The lower bound of the dietary Crude Protein (CP) level (% Dry Matter) that should be considered when
    calculating the mitigation effects of monensin."""

    MONENSIN_CP_UPPER_BOUND = 19
    """The upper bound of the dietary Crude Protein (CP) level (% Dry Matter) that should be considered when
    calculating the mitigation effects of monensin."""

    URINE_UREA_NITROGEN_CONCENTRATION_LOWER_BOUND = 2
    """The lower bound of the urine urea nitrogen concentration."""

    URINE_UREA_NITROGEN_CONCENTRATION_UPPER_BOUND = 12
    """The upper bound of the urine urea nitrogen concentration."""

    DAILY_MILK_VARIATION_MEAN = 0
    """Mean of the daily milk production variation from the estimated milk production, kg/day"""

    DAILY_MILK_VARIATION_STD_DEV = 1.0
    """Standard deviation of the daily milk production variation from the estimated milk production, kg/day"""

    MILK_CRUDE_PROTEIN = 3.2
    """Milk crude protein content, percentage."""

    MILK_LACTOSE = 4.85
    """Milk lactose content, percentage."""

    DMI_CONSTRAINT_PERCENT = 0.20
    """The +/- percentage of DMI estimated allowed for ration formulation"""

    MINIMUM_DMI = 1.0
    """Minimum estimated DMI instituted for all animals, kg/day"""

    MINIMUM_DMI_PERCENTAGE = 0.01
    """Minimum estimated DMI (kg/day), as a percentage of body_weight in kg"""

    MINIMUM_PHOSPHORUS = 0.0
    """Minimum phosphorus estimate, g/day"""

    MINIMUM_CALCIUM = 0.0
    """Minimum calcium estimate, g/day"""

    MILK_REDUCTION_KG = 0.25
    """Milk reduction amount for each failed ration optimization attempt, kg"""
