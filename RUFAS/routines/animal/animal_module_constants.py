class AnimalModuleConstants:
    """
    A class used to store constants related to an animal module.

    # TODO: Explain the attributes

    """

    DEFAULT_MAX_STOCKING_DENSITY = 1.2
    DEFAULT_NUM_STALLS = 100
    DEFAULT_NUM_STALLS_FOR_CALF_PEN = 110
    DEFAULT_NUM_STALLS_FOR_GROWING_PEN = 800
    DEFAULT_NUM_STALLS_FOR_CLOSE_UP_PEN = 200
    DEFAULT_NUM_STALLS_FOR_LAC_COW_PEN = 850
    DEFAULT_NUM_STALLS_FOR_GROWING_AND_CLOSE_UP_PEN = 500

    VERTICAL_DIST_TO_MILKING_PARLOR = 0.1
    HORIZONTAL_DIST_TO_MILKING_PARLOR = 1.6
    DEFAULT_HOUSING_TYPE = 'open air barn'
    DEFAULT_BEDDING_TYPE = 'sawdust'
    DEFAULT_PEN_TYPE = 'freestall'
    DEFAULT_MANURE_HANDLER = 'manual scraping'
    DEFAULT_MANURE_SEPARATOR = 'screw press'
    DEFAULT_MANURE_STORAGE = 'slurry storage outdoor'

    DMI_CONSTRAINT_PERCENT = 0.20

    DAILY_MILK_VARIATION_MEAN = 0
    DAILY_MILK_VARIATION_STD_DEV = 1.0

    MINIMUM_DMI = 1.0 # kg/day minimum instituted for all animals
    MINIMUM_DMI_PERCENTAGE = 0.01 # as a percentage of body_weight in kg
    MINIMUM_PHOSPHORUS = 0.0
    MINIMUM_CALCIUM = 0.0
