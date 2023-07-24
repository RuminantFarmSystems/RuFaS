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

    MONENSIN_CP_LOWER_BOUND = 15
    '''The lower bound of dietary CP(Crude Protein) level (%DM) that should be considered when using the CP equation to caculate the mitigation effects of monensin '''
    MONENSIN_CP_UPPER_BOUND = 19
    '''The upper bound of dietary CP(Crude Protein) level (%DM) that should be considered when using the CP equation to caculate the mitigation effects of monensin '''
    URINE_UREA_NITROGEN_CONCENTRATION_LOWER_BOUND = 2
    '''The lower bound of urine urea nitrogen concentration '''
    URINE_UREA_NITROGEN_CONCENTRATION_UPPER_BOUND = 12
    '''The upper bound of urine urea nitrogen concentration '''

   
    