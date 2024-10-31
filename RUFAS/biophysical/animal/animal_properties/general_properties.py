import math
from dataclasses import dataclass
from enum import Enum

from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType


class Breed(Enum):
    """Enum indicating the breed of the animal."""

    HO = "Holstein"
    JE = "Jersey"


class Sex(Enum):
    """Enum indicating the sex of the animal."""

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
    daily_milk_produced : float
        Milk production of the animal on a single day (kg).
    is_milking

    """

    animal_type: AnimalType
    birth_date: str
    birth_weight: float
    body_weight: float
    breed: Breed
    sex: Sex
    id: int
    mature_body_weight: float
    nutrients: dict[str, float]
    nutrient_concentrations: dict[str, float]
    culled: bool = False
    dead: bool = False
    daily_growth: float = 0.0
    days_born: int = 0
    days_in_preg: int = 0
    events: AnimalEvents = AnimalEvents()
    days_in_milk: int = 0
    dry_off_day_of_pregnancy: int = 0
    daily_milk_produced: float = 0.0
    future_cull_date: int = int(math.inf)
    future_death_date: int = int(math.inf)
    ration_formulation = {"objective": 0.00}
    sold: bool = False
    sold_at_day: int = int(math.inf)
    wean_weight: float = 0.0
    metabolizable_energy_intake: float = 0.0

    @property
    def is_milking(self) -> bool:
        """True if the animal is currently lactating, else False."""
        return self.days_in_milk > 0

    @property
    def is_pregnant(self) -> bool:
        """True if the animal is currently pregnant, else False."""
        return self.days_in_preg > 0
