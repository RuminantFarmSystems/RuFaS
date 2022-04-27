from dataclasses import dataclass


@dataclass
class ManureHandlerInitData:
    """
    A data class that contains information used in the
    creation of a ManureHandler object.

    """

    water_use_rate: int = 0  # liters/animal/day
    time_per_cleaning: int = 8
    cleanings_per_day: int = 2
