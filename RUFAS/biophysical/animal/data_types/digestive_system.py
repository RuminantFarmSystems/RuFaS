from dataclasses import dataclass

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionSupply


@dataclass
class DigestiveSystemInputs:
    animal_type: AnimalType
    body_weight: float
    nutrients: NutritionSupply
    days_in_milk: int
    metabolizable_energy_intake: float

    fecal_phosphorus: float
    urine_phosphorus_required: float

    daily_milk_produced: float
    fat_content: float
    crude_protein_content: float

    @property
    def is_milking(self) -> bool:
        return self.days_in_milk > 0
