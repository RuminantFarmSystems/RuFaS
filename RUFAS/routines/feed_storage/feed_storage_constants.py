class FeedStorageConstants:
    """
    A class used to store constants related to the Feed Storage module.

    Attributes
    ----------
    ALFALFA_GASEOUS_LOSS_LOWER_TEMP_LIMIT : float
        Temperature below which ensiled alfalfa does not lose dry matter to fermentation (degrees C).
    ALFALFA_GASEOUS_LOSS_UPPER_TEMP_LIMIT : float
        Temperature above which ensiled alfalfa does not lose dry matter to fermentation (degrees C).
    NON_ALFALFA_GASEOUS_LOSS_LOWER_TEMP_LIMIT : float
        Temperature below which ensiled non-alfalfa crops does not lose dry matter to fermentation (degrees C).
    NON_ALFALFA_GASEOUS_LOSS_UPPER_TEMP_LIMIT : float
        Temperature above which ensiled non-alfalfa crops does not lose dry matter to fermentation (degrees C).
    ALFALFA_GASEOUS_LOSS_LOWER_DRY_MATTER_LIMIT : float
        Dry matter percentage of fresh mass below which ensiled alfalfa does not lose dry matter to fermentation.
    ALFALFA_GASEOUS_LOSS_UPPER_DRY_MATTER_LIMIT : float
        Dry matter percentage of fresh mass above which ensiled alfalfa does not lose dry matter to fermentation.
    NON_ALFALFA_GASEOUS_LOSS_LOWER_DRY_MATTER_LIMIT : float
        Dry matter percentage of fresh mass below which ensiled non-alfalfa crops does not lose dry matter to
        fermentation.
    NON_ALFALFA_GASEOUS_LOSS_UPPER_DRY_MATTER_LIMIT : float
        Dry matter percentage of fresh mass above which ensiled non-alfalfa crops do not lose dry matter to
        fermentation.

    """

    ALFALFA_GASEOUS_LOSS_LOWER_TEMP_LIMIT = 5.0
    ALFALFA_GASEOUS_LOSS_UPPER_TEMP_LIMIT = 45.0
    NON_ALFALFA_GASEOUS_LOSS_LOWER_TEMP_LIMIT = 0.0
    NON_ALFALFA_GASEOUS_LOSS_UPPER_TEMP_LIMIT = 40.0
    ALFALFA_GASEOUS_LOSS_LOWER_DRY_MATTER_LIMIT = 20.0
    ALFALFA_GASEOUS_LOSS_UPPER_DRY_MATTER_LIMIT = 60.0
    NON_ALFALFA_GASEOUS_LOSS_LOWER_DRY_MATTER_LIMIT = 15.0
    NON_ALFALFA_GASEOUS_LOSS_UPPER_DRY_MATTER_LIMIT = 60.0
