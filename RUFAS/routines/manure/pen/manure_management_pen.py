from typing import NamedTuple
from typing import Set

from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.manure.pen_manure.pen_manure import PenManure


class ManureManagementPen:
    """
    A modified version of the Pen class in the animal module. This class extracts
    some relevant information from the  original Pen class and then adds some
    extra attributes that can be used in the gas emissions equations.

    Attributes
        id: Pen id.
        animals_in_pen: A list of animal objects in this pen.
        num_animals: The number of animals in this pen.
        num_lactating_cows: The number of lactating cows in this pen.
        classes_in_pen: Set of unique animal classes in this pen.
        animal_combination: An AnimalCombination enum that describes the current
            animal makeup in this pen.
        housing_type: The type of housing used for this pen.
        bedding_type: The type of bedding used for this pen.
        pen_type: The type of pen used for this pen.
        manure_handler: The type of manure handler used for this pen.
        manure_separator: The type of manure separator used for this pen.
        manure_treatment: The type of manure treatment(s) used for this pen.
        manure_density: The manure density used for calculating manure volume, kg/m^3.
        manure: The manure data extracted from the animal module and converted to usable
            form for the manure module.

    """

    def __init__(self, pen: Pen):
        """Initializes a pen object.

        The newly created object does not store any reference to the passed-in argument
        and only performs a read on it.

        Args:
            pen: A Pen object from the animal module.

        """
        self.id: int = pen.id
        self.animals_in_pen: [AnimalBase] = pen.animals_in_pen
        self.num_animals = len(pen.animals_in_pen)
        self.classes_in_pen: Set[str] = pen.classes_in_pen

        self.housing_type: str = pen.housing_type
        self.pen_type: str = pen._pen_type
        self.bedding_type: str = pen.bedding_type

        self.manure_handler: str = pen.manure_handling
        self.manure_separator: str = pen.manure_separator
        self.manure_treatment: str = pen.manure_storage

        self.manure = PenManure.get_instance(pen.manure, self.num_animals)
        self.num_lactating_cows = self.count_lactating_cows(pen.animal_combination, pen.animals_in_pen)

    @classmethod
    def count_lactating_cows(cls, animal_combination: Pen.AnimalCombination, animals_in_pen: [AnimalBase]) -> int:
        """Counts the number of lactating cows in the pen.

        Args:
            animal_combination: An AnimalCombination enum that describes the current
                animal makeup in this pen.
            animals_in_pen: A list of animal objects in this pen.

        Returns:
            The number of lactating cows in the pen.

        """

        num_lac_cows = 0
        if animal_combination is Pen.AnimalCombination.LAC_COW:
            for animal in animals_in_pen:
                if type(animal) is Cow:
                    num_lac_cows += 1
        return num_lac_cows

    @property
    def barn_area_from_pen_type(self) -> float:
        """Calculates the barn area for this pen based on its housing type.

        Returns:
            Barn area, m^2/animal.

        """
        BarnArea = NamedTuple('BarnArea', [
            ('for_cow', float),
            ('for_calf_and_heiferI', float),
            ('for_heiferII_and_heiferIII', float),
        ])
        tiestall = BarnArea(for_cow=1.5, for_calf_and_heiferI=1.2, for_heiferII_and_heiferIII=1.2)
        bedded_pack = BarnArea(for_cow=5.0, for_calf_and_heiferI=3.0, for_heiferII_and_heiferIII=3.0)
        freestall = BarnArea(for_cow=3.5, for_calf_and_heiferI=2.0, for_heiferII_and_heiferIII=2.5)
        default = freestall

        barn_area_by_pen_type = {
            'tiestall': tiestall,
            'bedded pack': bedded_pack,
            'freestall': freestall
        }

        barn_area = barn_area_by_pen_type.get(self.pen_type, default)

        if 'Cow' in self.classes_in_pen:
            return barn_area.for_cow
        elif 'Calf' in self.classes_in_pen or 'HeiferI' in self.classes_in_pen:
            return barn_area.for_calf_and_heiferI
        else:
            return barn_area.for_heiferII_and_heiferIII
