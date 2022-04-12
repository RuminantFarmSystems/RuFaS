from dataclasses import dataclass


@dataclass
class StorageOptionInitData:
    """
    A data class that contains information used in the
    creation of a ManureHandler object.

    """

    sludge_accumulation_volume: float = 0.00251
    hydraulic_retention_time: int = 180
    sludge_accumulation_period: float = 5.0
