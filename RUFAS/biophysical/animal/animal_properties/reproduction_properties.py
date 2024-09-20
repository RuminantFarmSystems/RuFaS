from dataclasses import dataclass


@dataclass
class ReproductionProperties:
    gestation_length: int
    conceptus_weight: float
    calf_birth_weight: float
    calves: int
    calving_interval: float
