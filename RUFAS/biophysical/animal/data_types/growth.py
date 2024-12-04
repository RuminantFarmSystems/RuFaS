from dataclasses import dataclass

from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType


@dataclass
class GrowthInputs:
    days_in_pregnancy: int
    animal_type: AnimalType
    body_weight: float
    mature_body_weight: float
    birth_weight: float
    days_born: int
    days_in_milk: int

    conceptus_weight: float
    gestation_length: int
    calf_birth_weight: float
    calves: int
    calving_interval: float

    @property
    def is_pregnant(self) -> bool:
        return self.days_in_pregnancy > 0

    @property
    def is_milking(self) -> bool:
        return self.days_in_milk > 0


@dataclass
class GrowthOutputs:
    body_weight: float
    conceptus_weight: float
    events: AnimalEvents
