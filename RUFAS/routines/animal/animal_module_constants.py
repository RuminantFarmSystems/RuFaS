class AnimalModuleConstants:
    """
    A class used to store constants related to the animal module.
    """

    DEFAULT_MAX_STOCKING_DENSITY: float = 1.2
    """The default maximum stocking density for a pen. This value is used when a pen is created dynamically during the
    simulation."""

    DEFAULT_NUM_STALLS: int = 100
    """The default number of stalls to be created in a new pen if no specific value is provided."""

    DEFAULT_NUM_STALLS_FOR_CALF_PEN: int = 110
    """The default number of stalls to be created in a calf pen."""

    DEFAULT_NUM_STALLS_FOR_GROWING_PEN: int = 800
    """The default number of stalls to be created in a growing pen."""

    DEFAULT_NUM_STALLS_FOR_CLOSE_UP_PEN: int = 200
    """The default number of stalls to be created in a close-up pen."""

    DEFAULT_NUM_STALLS_FOR_LAC_COW_PEN: int = 850
    """The default number of stalls to be created in a lactating cow pen."""

    DEFAULT_NUM_STALLS_FOR_GROWING_AND_CLOSE_UP_PEN: int = 500
    """The default number of stalls to be created in a combined growing and close-up pen."""

    VERTICAL_DIST_TO_MILKING_PARLOR: float = 0.1
    """The default vertical distance from the animal pens to the milking parlor."""

    HORIZONTAL_DIST_TO_MILKING_PARLOR: float = 1.6
    """The default horizontal distance from the animal pens to the milking parlor."""

    DEFAULT_HOUSING_TYPE: str = "open air barn"
    """The default housing type for animals in the simulation."""

    DEFAULT_BEDDING_TYPE: str = "sawdust"
    """The default bedding material used in the pens."""

    DEFAULT_PEN_TYPE: str = "freestall"
    """The default type of pen to be created in the simulation."""

    DEFAULT_MANURE_HANDLER: str = "manual scraping"
    """The default method of manure handling used in those pens created dynamically during the simulation."""

    DEFAULT_MANURE_SEPARATOR: str = "screw press"
    """The default manure separator system used in those pens created dynamically during the simulation."""

    DEFAULT_MANURE_STORAGE: str = "slurry storage outdoor"
    """The default type of manure storage system used in those pens created dynamically during the simulation."""

    URINE_UREA_NITROGEN_CONCENTRATION_LOWER_BOUND: float = 2
    """The lower bound of the urine urea nitrogen concentration."""

    URINE_UREA_NITROGEN_CONCENTRATION_UPPER_BOUND: float = 12
    """The upper bound of the urine urea nitrogen concentration."""

    DAILY_MILK_VARIATION_MEAN: float = 0
    """Mean of the daily milk production variation from the estimated milk production, kg/day"""

    DAILY_MILK_VARIATION_STD_DEV: float = 1.0
    """Standard deviation of the daily milk production variation from the estimated milk production, kg/day"""

    MILK_CRUDE_PROTEIN: float = 3.2
    """Milk crude protein content, percentage."""

    MILK_LACTOSE: float = 4.85
    """Milk lactose content, percentage."""

    DMI_CONSTRAINT_PERCENT: float = 0.20
    """The +/- percentage of DMI estimated allowed for ration formulation"""

    MINIMUM_DMI: float = 1.0
    """Minimum estimated DMI instituted for all animals, kg/day"""

    MINIMUM_DAILY_DMI_RATIO: float = 0.01
    """Minimum estimated DMI (kg/day), as a percentage of body_weight in kg"""

    MINIMUM_DMI_LACT: float = 2.0
    """Minimum estimated DMI instituted for lactating cows, kg/day. Note that the mimimum intake in the dataset used to generate the equation is 3.94 kg/day (Reed et al. 2015)"""

    MINIMUM_DMI_DRY: float = 2.0
    """Minimum estimated DMI instituted for dry cows, kg/day. Note that the minimum intake in the dataset used to generate the equation is 7.1 kg/day (Appuhamy 2018)"""

    MINIMUM_PHOSPHORUS: float = 0.0
    """Minimum phosphorus estimate, g/day"""

    MINIMUM_CALCIUM: float = 0.0
    """Minimum calcium estimate, g/day"""

    MILK_REDUCTION_KG: float = 0.25
    """Milk reduction amount for each failed ration optimization attempt, kg"""

    MINIMUM_HEIFER_DAILY_GROWTH_RATE: float = 0.5
    """Minimum daily growth for heifers, kg."""
