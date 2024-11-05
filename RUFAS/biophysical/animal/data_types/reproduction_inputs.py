from dataclasses import dataclass

from RUFAS.biophysical.animal.data_types.animal_enums import Breed
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType


@dataclass
class ReproductionInputs:
    animal_type: AnimalType
    body_weight: float
    breed: Breed
    cull_reason: str
    days_born: int
    days_in_pregnancy: int
    days_in_milking: int
    events: AnimalEvents
    future_cull_date: int
    future_death_date: int

    @property
    def is_pregnant(self) -> bool:
        return self.days_in_pregnancy > 0

