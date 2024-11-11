from dataclasses import dataclass

from RUFAS.biophysical.animal.data_types.animal_enums import Breed
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType


@dataclass
class ReproductionInputs:
    animal_type: AnimalType
    body_weight: float
    breed: Breed
    days_born: int
    days_in_pregnancy: int
    days_in_milk: int
    net_merit: float
    phosphorus_for_gestation_required_for_calf: float

    @property
    def is_pregnant(self) -> bool:
        return self.days_in_pregnancy > 0

    @property
    def is_milking(self) -> bool:
        return self.days_in_milk > 0
