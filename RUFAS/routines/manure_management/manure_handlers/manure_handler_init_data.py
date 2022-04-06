from dataclasses import dataclass


@dataclass
class ManureHandlerInitData:
    """
    A data class that contains information used in the
    creation of a ManureHandler object.

    """

    water_use_rate: int = 0
    time_per_cleaning: int = 0
    cleanings_per_day: int = 0
