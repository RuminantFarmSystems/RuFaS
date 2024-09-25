from dataclasses import dataclass


@dataclass
class ReproductionProperties:
    """
    Collection of animal properties that are related to reproduction.

    Attributes
    ----------
    gestation_length: int
    concpeptus_weight: float
    calf_birth_weight:float
    calves: int
    calving_interval: float
    """

    gestation_length: int
    conceptus_weight: float
    calf_birth_weight: float
    calves: int
    calving_interval: float
