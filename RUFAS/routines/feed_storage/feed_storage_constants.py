class FeedStorageConstants:
    """
    A class used to store constants related to the Feed Storage module.

    Attributes
    ----------
    ALFALFA_GASEOUS_LOSS_LOWER_TEMP_THRESHOLD : float
        Temperature below which ensiled alfalfa does not lose dry matter to fermentation (degrees C).
    ALFALFA_GASEOUS_LOSS_UPPER_TEMP_THRESHOLD : float
        Temperature above which ensiled alfalfa does not lose dry matter to fermentation (degrees C).
    NON_ALFALFA_GASEOUS_LOSS_LOWER_TEMP_THRESHOLD : float
        Temperature below which ensiled non-alfalfa crops does not lose dry matter to fermentation (degrees C).
    NON_ALFALFA_GASEOUS_LOSS_UPPER_TEMP_THRESHOLD : float
        Temperature above which ensiled non-alfalfa crops does not lose dry matter to fermentation (degrees C).
    ALFALFA_GASEOUS_LOSS_LOWER_DRY_MATTER_THRESHOLD : float
        Dry matter percentage below which ensiled alfalfa does not lose dry matter to fermentation.
    NON_ALFALFA_GASEOUS_LOSS_LOWER_DRY_MATTER_THRESHOLD : float
        Dry matter percentage below which ensiled non-alfalfa crops does not lose dry matter to fermentation.
    GASEOUS_LOSS_UPPER_DRY_MATTER_THRESHOLD : float
        Dry matter percentage below which ensiled crops do not lose dry matter to fermentation.

    """
    ALFALFA_GASEOUS_LOSS_LOWER_TEMP_THRESHOLD = 5.0
    ALFALFA_GASEOUS_LOSS_UPPER_TEMP_THRESHOLD = 45.0
    NON_ALFALFA_GASEOUS_LOSS_LOWER_TEMP_THRESHOLD = 0.0
    NON_ALFALFA_GASEOUS_LOSS_UPPER_TEMP_THRESHOLD = 40.0
    ALFALFA_GASEOUS_LOSS_LOWER_DRY_MATTER_THRESHOLD = 20.0
    NON_ALFALFA_GASEOUS_LOSS_LOWER_DRY_MATTER_THRESHOLD = 15.0
    GASEOUS_LOSS_UPPER_DRY_MATTER_THRESHOLD = 60.0

