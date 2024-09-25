from dataclasses import dataclass
from enum import Enum

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents


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
    daily_milk_produced : float
        Milk production of the animal on a single day (kg).
    is_milking

    """

    animal_type: AnimalType
    birth_date: str
    birth_weight: float
    body_weight: float
    breed: "Breed"
    culled: bool
    days_born: int
    days_in_preg: int
    days_in_milk: int
    dry_off_day_of_pregnancy: int  # Old name: days_in_preg_when_dry, used to be in AnimalBase.config
    events: AnimalEvents
    days_in_milk: int
    dry_off_day_of_pregnancy: int
    daily_milk_produced: float
    future_cull_date: int
    future_death_date: int
    gender: "Gender"
    id: int
    is_pregnant: bool
    mature_body_weight: float
    nutrients: list[str]
    ration_formulation = {"objective": 0.00}
    sold: bool
    sold_at_day: int
    wean_weight: float

    @property
    def is_milking(self) -> bool:
        """True if the animal is currently lactating, else False."""
        return self.days_in_milk > 0


class Breed(Enum):
    HO = "Holstein"
    JE = "Jersey"


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
