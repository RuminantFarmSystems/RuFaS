from dataclasses import dataclass


@dataclass
class ReproductionProperties:
    """
    Collection of animal properties that are related to reproduction.

    Attributes
    ----------
    gestation_length: int
        The length of pregnancy (days).
    concpeptus_weight: float
        The body weight gain due to pregnancy (kg).
    calf_birth_weight:float
        The birth weight of the baby calf (kg).
    calves: int
        The number of baby calves that an animal has had throughout her life.
    calving_interval: float
        The calving interval (days).
    """

    gestation_length: int
    conceptus_weight: float
    calf_birth_weight: float
    calves: int
    calving_interval: float
