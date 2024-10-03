from dataclasses import dataclass
from enum import Enum

from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType


class Breed(Enum):
    """Enum indicating the breed of the animal."""

    HO = "Holstein"
    JE = "Jersey"


class Sex(Enum):
    """Enum indicating the gender of the animal."""

    MALE = "male"
    FEMALE = "female"


@dataclass
class GeneralProperties:
    """
    Collection of animal attributes that determine outcomes.

    Attributes
    ----------
    days_in_milk : int
        Number of days the animal has been milking for in its current lactation.
    dry_off_day_of_pregnancy : int
        Number of days into pregnancy when a lactating cow stops milking.
    metabolizable_energy_intake : float
        Metabolizable energy intake, Mcal/kg dry matter.

    """

    animal_type: AnimalType
    birth_date: str
    birth_weight: float
    body_weight: float
    breed: Breed
    culled: bool
    daily_growth: float
    days_born: int
    days_in_preg: int
    events: AnimalEvents
    days_in_milk: int
    dry_off_day_of_pregnancy: int
    future_cull_date: int
    future_death_date: int
    sex: Sex
    id: int
    is_pregnant: bool
    mature_body_weight: float
    nutrients: dict[str, float]
    nutrient_concentrations: dict[str, float]
    ration_formulation = {"objective": 0.00}
    sold: bool
    sold_at_day: int
    wean_weight: float
    metabolizable_energy_intake: float

    @property
    def is_milking(self) -> bool:
        """True if the animal is currently lactating, else False."""
        return self.days_in_milk > 0
