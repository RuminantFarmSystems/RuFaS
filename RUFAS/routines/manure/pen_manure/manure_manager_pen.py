from typing import NamedTuple, Any
from typing import Set

from RUFAS.routines.manure.pen_manure.pen_manure import PenManure
from ....shared_structures.animal_combinations import AnimalCombination
from ....shared_structures.pen_manure_data import PenManureData


class ManureManagerPen:
    """
    A modified version of the Pen class in the animal module. This class extracts
    some relevant information from the original Pen class and then adds some
    extra attributes that can be used in the gas emissions equations.

    Attributes
    ----------
    id : int
        Pen id.
    animals_in_pen : Dict[int, AnimalBase]
        A dictionary of animal ids as the key and animal objects as the value in this pen
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
    bedding_type : str
        The type of bedding used for this pen.
    pen_type : str
        The type of pen used for this pen.
    manure_handler : str
        The type of manure handler used for this pen.
    manure_separator : str
        The type of manure separator used for this pen.
    manure_separator_after_digestion : str
        The second manure separator used on manure generated from this pen.
    manure_treatment : str
        The type of manure treatment(s) used for this pen.
    manure_density : float
        The manure density used for calculating manure volume, kg/m^3.
    manure : PenManure
        The manure data extracted from the animal module and converted to usable form for the manure module.

    """

    def __init__(self, pen: PenManureData) -> None:
        """Initializes a pen object.

        The newly created object does not store any reference to the passed-in argument
        and only performs a read on it.

        Parameters
        ----------
        pen : PenManureData
            A PenManureData instance containing all the manure information from a single pen.

        """
        self.id: int = pen.id
        self.animals_in_pen: dict[int, Any] = pen.animals_in_pen
        self.num_animals: int = pen.num_animals
        self.classes_in_pen: Set[str] = pen.classes_in_pen
        self.animal_combination: AnimalCombination = pen.animal_combination

        self.housing_type: str = pen.housing_type
        self.pen_type: str = pen.pen_type
        self.bedding_type: str = pen.bedding_type

        self.manure_handler: str = pen.manure_handler
        self.manure_separator: str = pen.manure_separator
        self.manure_separator_after_digestion: str = pen.manure_separator_after_digestion
        self.manure_treatment: str = pen.manure_treatment

        self.manure: PenManure = PenManure.get_instance(pen.manure, self.num_animals)
        self.num_lactating_cows: int = pen.num_lactating_cows
        self.num_stalls: int = pen.num_stalls

    @property
    def barn_area_from_pen_type(self) -> float:
        """
        Get the barn area based on the pen type and whether there are cows in the pen.

        Notes
        -----
        The barn area is looked up from the following table:

        +---------------------------+-------------------+-------------------+
        | Pen Type                  | Has Cows          | No Cows           |
        +===========================+===================+===================+
        | Freestall                 | 3.5               | 2.5               |
        +---------------------------+-------------------+-------------------+
        | Tiestall                  | 1.2               | 1.0               |
        +---------------------------+-------------------+-------------------+
        | Compost Bedded Pack Barn  | 5.0               | 3.0               |
        +---------------------------+-------------------+-------------------+
        | Open Lot                  | 5.0               | 3.0               |
        +---------------------------+-------------------+-------------------+

        Returns
        -------
        float
            Barn surface area (:math:`m^2`).

        Raises
        ------
        ValueError
            If the pen type is not one of the following: "freestall", "tiestall",
            "compost bedded pack barn", or "open lot".
        """

        BarnArea = NamedTuple("BarnArea", [("has_cows", float), ("no_cows", float)])
        freestall = BarnArea(has_cows=3.5, no_cows=2.5)
        tiestall = BarnArea(has_cows=1.2, no_cows=1.0)
        bedded_pack = BarnArea(has_cows=5.0, no_cows=3.0)
        open_lot = BarnArea(has_cows=5.0, no_cows=3.0)

        barn_area_by_pen_type = {
            "freestall": freestall,
            "tiestall": tiestall,
            "compost bedded pack barn": bedded_pack,
            "open lot": open_lot,
        }

        if self.pen_type not in barn_area_by_pen_type:
            raise ValueError(f"Invalid pen type: {self.pen_type}")

        barn_area = barn_area_by_pen_type[self.pen_type]

        if "Cow" in self.classes_in_pen:
            return barn_area.has_cows * self.num_stalls
        return barn_area.no_cows * self.num_stalls
