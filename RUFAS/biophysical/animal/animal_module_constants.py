class AnimalModuleConstants:
    """
    A class used to store constants related to the animal module.
    """

    DEFAULT_BODY_CONDITION_SCORE_5: float = 3.0
    """
    Score on a scale of 1-5 indicating how fit an animal is. This default is used because the score is neither set nor
    calculated in the Animal module.
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

    DEFAULT_DRY_MATTER_INTAKE: float = 10.0
    """Default dry matter intake of a ration when this value is not known for an animal (kg)."""

    DEFAULT_NET_ENERGY_DIET_CONCENTRATION: float = 1.0
    """Default metabolizable energy density of a ration when this value is not known for an animal."""

    DEFAULT_NDF_PERCENTAGE: float = 0.3
    """Percentage of neutral detergent fiber in a ration when this value is not known for an animal."""

    DEFAULT_TDN_PERCENTAGE: float = 0.7
    """Percentage of total digestible nutrition in a ration when this value is not known for an animal."""

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

    MAXMIMUM_MANURE_DRY_MATTER_CONTENT: float = 0.20
    """The maximum dry matter content for manure produced by all animal classe, fraction."""

    DAILY_MILK_VARIATION_MEAN: float = 0
    """Mean of the daily milk production variation from the estimated milk production, kg/day"""

    DAILY_MILK_VARIATION_STD_DEV: float = 1.0
    """Standard deviation of the daily milk production variation from the estimated milk production, kg/day"""

    MILK_CRUDE_PROTEIN: float = 3.2
    """Milk crude protein content, percentage."""

    MILK_LACTOSE: float = 4.85
    """Milk lactose content, percentage."""

    DMI_CONSTRAINT_FRACTION: float = 0.30
    """The +/- fraction of DMI estimated allowed for ration formulation."""

    DMI_REQUIREMENT_BOOST: float = 1.1
    """The fraction of the dry matter intake requirement used as the basis for
    the inclusion rate bounds in user defined ration formulation method."""

    MINIMUM_DMI: float = 1.0
    """Minimum estimated DMI instituted for all animals, kg/day"""

    MINIMUM_DAILY_DMI_RATIO: float = 0.01
    """Minimum estimated DMI (kg/day), as a fraction of body_weight in kg"""

    MINIMUM_DMI_LACT: float = 2.0
    """Minimum estimated DMI for lactating cows, kg/day. Note that in the dataset used to generate the equation,
    the mimimum DMI is 3.94 kg/day (Reed et al. 2015)"""

    MINIMUM_DMI_DRY: float = 2.0
    """Minimum estimated DMI for dry cows, kg/day. Note that in the dataset used to generate the equation,
    the minimum DMI is 7.1 kg/day (Appuhamy 2018)"""

    MINIMUM_PHOSPHORUS: float = 0.0
    """Minimum phosphorus estimate, g/day"""

    MINIMUM_CALCIUM: float = 0.0
    """Minimum calcium estimate, g/day"""

    MINIMUM_RATION_NDF: float = 25.0
    """Minimum percentage of a pen's ration's dry matter that must be neutral detergent fiber (NDF) (percent)."""

    MAXIMUM_RATION_NDF: float = 45.0
    """Maximum percentage of a pen's ration's dry matter that must be NDF (percent)."""

    MINIMUM_RATION_FORAGE_NDF: float = 15.0
    """Minimum percentage of a pen's ration's dry matter that must be NDF from forages (percent)."""

    MAXIMUM_RATION_FAT: float = 7.0
    """Maximum percentage of a ration's dry matter that must be fat (percent)."""

    MILK_REDUCTION_KG: float = 0.25
    """Milk reduction amount for each failed ration optimization attempt, kg"""

    MINIMUM_HEIFER_DAILY_GROWTH_RATE: float = 0.5
    """Minimum daily growth for heifers, kg."""

    PROTEIN_UPPER_LIMIT_FACTOR: float = 1.5
    """Factor used to generate the upper limit for metabolizable protein content in ration formulation."""

    MINIMUM_AVG_PEN_MILK: float = 15
    """Minimum allowable average milk production, for a given pen, as used in ration formulation, kg/animal"""

    MINIMUM_TDN_DISCOUNT: float = 0.6
    """Minimum allowable TDN discount for use in energetic calculations, unitless."""

    EFF_OF_ME_USE: float = 0.66
    """Efficiency of metabolizable energy use, e.g. conversion rate of metabolizable energy to net energy, unitless."""
