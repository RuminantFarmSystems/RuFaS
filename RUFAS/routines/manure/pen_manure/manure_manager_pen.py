from typing import List, NamedTuple
from typing import Set

from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.manure.pen_manure.pen_manure import PenManure
from RUFAS.routines.animal.animal_combinations import AnimalCombination


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

    def __init__(self, pen: Pen):
        """Initializes a pen object.

        The newly created object does not store any reference to the passed-in argument
        and only performs a read on it.

        Parameters
        ----------
        pen : Pen
            A Pen object from the animal module.

        """
        self.id: int = pen.id
        self.animals_in_pen = pen.animals_in_pen
        self.num_animals = len(pen.animals_in_pen)
        self.classes_in_pen: Set[str] = pen.classes_in_pen
        self.animal_combination: Pen.AnimalCombination = pen.animal_combination

        self.housing_type: str = pen.housing_type
        self.pen_type: str = pen.pen_type
        self.bedding_type: str = pen.bedding_type

        self.manure_handler: str = pen.manure_handling
        self.manure_separator: str = pen.manure_separator
        self.manure_separator_after_digestion: str = pen.manure_separator_after_digestion
        self.manure_treatment: str = pen.manure_storage

        self.manure = PenManure.get_instance(pen.manure, self.num_animals)
        self.num_lactating_cows = self.count_lactating_cows(pen.animal_combination, pen.animals_in_pen)
        self.num_stalls = pen.num_stalls

    @classmethod
    def count_lactating_cows(cls, animal_combination: AnimalCombination, animals_in_pen: List[AnimalBase]) -> int:
        """Counts the number of lactating cows in the pen.

        Parameters
        ----------
        animal_combination : AnimalCombination
            An AnimalCombination enum that describes the current animal makeup in this pen.
        animals_in_pen : List[AnimalBase]
            A list of animal objects in this pen.

        Returns
        -------
        int
            The number of lactating cows in the pen.

        """
        num_lac_cows = 0
        if animal_combination is AnimalCombination.LAC_COW:
            for animal in animals_in_pen:
                if type(animal) is Cow:
                    num_lac_cows += 1
        return num_lac_cows

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

        if "LacCow" in self.classes_in_pen:
            return barn_area.has_cows * self.num_stalls
        return barn_area.no_cows * self.num_stalls
