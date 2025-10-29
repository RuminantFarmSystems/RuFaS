from dataclasses import dataclass
from enum import Enum

from RUFAS.routines.animal.animal_types import AnimalType
from RUFAS.routines.animal.life_cycle.animal_events import AnimalEvents


@dataclass
class GeneralProperties:
    animal_type: AnimalType
    birth_date: str
    birth_weight: float
    body_weight: float
    breed: Enum
    culled: bool
    daily_growth: float
    days_born: int
    days_in_preg: int
    events: AnimalEvents
    estimated_daily_milk_produced: float
    future_cull_date: int
    future_death_date: int
    gender: Enum
    id: int
    is_dry: bool
    is_lactating: bool
    is_pregnant: bool
    mature_body_weight: float
    milking: bool
    nutrients: list[str]
    ration_formulation = {"objective": 0.00}
    sold: bool
    sold_at_day: int
    wean_weight: float
