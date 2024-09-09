from dataclasses import dataclass
from RUFAS.routines.animal.animal_types import AnimalType
from RUFAS.routines.animal.general_properties import GeneralProperties


@dataclass
class AnimalPhosphorusStatus:
    """Dataclass representing the phosphorus status of the animal."""

    animal_type: AnimalType
    body_weight: float
    mature_body_weight: float
    daily_growth: float
    days_in_preg: int
    milking: bool
    estimated_daily_milk_produced: float
    phosphorus_excess_in_diet: float
    phosphorus_intake: float
    phosphorus_requirement: float
    phosphorus_reserves: float
    total_phosphorus_in_animal: float
    phosphorus_for_growth: float
    phosphorus_endogenous_loss: float
    ration_phosphorus_concentration: float
    phosphorus_for_gestation: float
    phosphorus_for_gestation_required_for_calf: float

    def get_phosphorus_data(self, general_properties: GeneralProperties, animal) -> None:
        """Gets the animal's current phosphorus-related attributes."""
        self.animal_type = general_properties.animal_type
        self.body_weight = general_properties.body_weight
        self.mature_body_weight = general_properties.mature_body_weight
        self.daily_growth = general_properties.daily_growth
        self.days_in_preg = general_properties.days_in_preg
        self.milking = general_properties.milking
        self.estimated_daily_milk_produced = general_properties.estimated_daily_milk_produced
        self.phosphorus_excess_in_diet = animal.phosphorus_excess_in_diet
        self.phosphorus_intake = animal.phosphorus_intake
        self.phosphorus_requirement = animal.phosphorus_requirement
        self.phosphorus_reserves = animal.phosphorus_reserves
        self.total_phosphorus_in_animal = animal.total_phosphorus_in_animal
        self.phosphorus_for_growth = animal.phosphorus_for_growth
        self.phosphorus_endogenous_loss = animal.phosphorus_endogenous_loss
        self.ration_phosphorus_concentration = animal.ration_phosphorus_concentration
        self.phosphorus_for_gestation = animal.phosphorus_for_gestation
        self.phosphorus_for_gestation_required_for_calf = animal.phosphorus_for_gestation_required_for_calf

    def _update_animal(self, animal) -> None:
        """Updates the animal's phosphorus-related attributes after the daily routine."""
        animal.phosphorus_endogenous_loss = self.phosphorus_endogenous_loss
        animal.phosphorus_for_growth = self.phosphorus_for_growth
        animal.phosphorus_requirement = self.phosphorus_requirement
        animal.phosphorus_for_gestation = self.phosphorus_for_gestation
        animal.phosphorus_for_gestation_required_for_calf = self.phosphorus_for_gestation_required_for_calf
        animal.phosphorus_excess_in_diet = self.phosphorus_excess_in_diet
        animal.phosphorus_reserves = self.phosphorus_reserves
        animal.total_phosphorus_in_animal = self.total_phosphorus_in_animal
