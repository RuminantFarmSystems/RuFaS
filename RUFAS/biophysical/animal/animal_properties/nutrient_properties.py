from dataclasses import dataclass
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType


@dataclass
class NutrientProperties:
    """
    Dataclass representing the phosphorus status of the animal.

    Attributes
    ----------
    fecal_phosphorus : float
        Amount of fecal phosphorus excreted by the current animal, g.
    urine_phosphorus_required : float
        Amount of phosphorus required for urine production, g.

    """
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
    fecal_phosphorus: float
    urine_phosphorus_required: float
