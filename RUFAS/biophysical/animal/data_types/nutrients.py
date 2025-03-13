from dataclasses import dataclass

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType


@dataclass
class NutrientsInputs:
    animal_type: AnimalType
    body_weight: float
    mature_body_weight: float
    daily_growth: float
    days_in_pregnancy: int
    days_in_milk: int
    daily_milk_produced: float

    @property
    def is_pregnant(self) -> bool:
        return self.days_in_pregnancy > 0

    @property
    def is_milking(self) -> bool:
        return self.days_in_milk > 0
