from dataclasses import dataclass

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType


@dataclass
class DigestiveSystemInputs:
    animal_type: AnimalType
    body_weight: float
    nutrients: dict[str, float]
    nutrient_concentrations: dict[str, float]
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
