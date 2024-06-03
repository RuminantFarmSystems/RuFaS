from dataclasses import dataclass
from typing import Any
from .animal_combinations import AnimalCombination
from .animal_manure_excretions import AnimalManureExcretions


@dataclass
class PenManureData():
    """

    """
    id: int
    animals_in_pen: dict[int, Any]
    num_animals: int
    classes_in_pen: set[str]
    animal_combination: AnimalCombination
    housing_type: str
    pen_type: str
    bedding_type: str

    manure_handler: str
    manure_separator: str
    manure_separator_after_digestion: str
    manure_treatment: str

    manure: dict[float, int] | AnimalManureExcretions | None
    num_lactating_cows: int
    num_stalls: int
