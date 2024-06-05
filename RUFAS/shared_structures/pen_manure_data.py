from dataclasses import dataclass
from .animal_combinations import AnimalCombination
from .animal_manure_excretions import AnimalManureExcretions


@dataclass
class PenManureData:
    """
    Packages manure data for a single pen.

    Attributes
    ----------
    id : int
        Pen id.
    num_animals : int
        The number of animals in this pen.
    num_lactating_cows : int
        The number of lactating cows in this pen.
    classes_in_pen : Set[str]
        Set of unique animal classes in this pen.
    animal_combination : AnimalCombination
        An AnimalCombination enum that describes the current animal makeup in this pen.
    housing_type : str
        The type of housing used for this pen.
    pen_type : str
        The type of pen used for this pen.
    bedding_type : str
        The type of bedding used for this pen.
    manure_handler : str
        The type of manure handler used for this pen.
    manure_separator : str
        The type of manure separator used for this pen.
    manure_separator_after_digestion : str
        The second manure separator used on manure generated from this pen.
    manure_treatment : str
        The type of manure treatment(s) used for this pen.
    manure : dict[float, int] | AnimalManureExcretions | None
        The manure data extracted from the animal module and converted to usable form for the manure module.
    num_lactating_cows : int
        The number of lactating cows held in this pen.
    num_stalls : int
        The number of stalls in this pen.

    """

    id: int
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
