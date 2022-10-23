from typing import NamedTuple, Set, Type

from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.manure.manure.pen_manure import PenManure


class ManureManagementPen:
    """
    A modified version of the Pen class in the animal module. This class extracts
    some relevant information from the  original Pen class and then adds some
    extra attributes that can be used in the gas emissions equations.

    Attributes
        id: Pen id.
        animals_in_pen: A list of animal objects in this pen.
        num_animals: The number of animals in this pen.
        num_cows: The number of cows in this pen.
        classes_in_pen: Set of unique animal classes in this pen.
        animal_combination: An AnimalCombination enum that describes the current
            animal makeup in this pen.
        housing_type: The type of housing used for this pen.
        bedding_type: The type of bedding used for this pen.
        manure_handler: The type of manure handler used for this pen.
        manure_separator: The type of manure separator used for this pen.
        manure_treatment: The type of manure treatment(s) used for this pen.
        manure_density: The manure density used for calculating manure volume, kg/m^3.
        manure: The manure data extracted from the animal module.

    """

    def __init__(self, pen: Pen):
        """Initializes a pen object.

        The newly created object does not store any reference to the passed-in argument
        and only performs a read on it.

        Args
            pen: A Pen object from the animal module.

        """

        self.id: int = pen.id
        self.animals_in_pen: [AnimalBase] = pen.animals_in_pen
        self.num_animals = len(pen.animals_in_pen)
        self.classes_in_pen: Set[Type[AnimalBase]] = pen.classes_in_pen
        self.animal_combination: Pen.AnimalCombination = pen.animal_combination

        self.housing_type: str = pen.housing_type
        self.bedding_type: str = pen.bedding_type

        self.manure_handler: str = pen.manure_handling
        self.manure_separator: str = pen.manure_separator
        self.manure_treatment: str = pen.manure_storage

        self.manure_density = 990.0  # TODO: Add this to manure config file
        self.manure = PenManure.get_instance(pen.manure, self.num_animals)

        self.num_cows = 0
        for animal in self.animals_in_pen:
            if type(animal) is Cow:
                self.num_cows += 1

    @property
    def manure_mass(self) -> float:
        """Calculates the manure mass of this pen.

        Returns
            Manure mass of this pen, kg.

        """
        return self.manure.manure_mass

    @property
    def manure_volume(self) -> float:
        """Calculates the manure volume of this pen.

        Returns
            Manure volume of this pen, m^3.

        """
        return self.manure_mass / self.manure_density

    @property
    def housing_area_for_NH3_emission(self) -> float:
        """Returns housing area used for calculating NH3 housing emission.

        Returns
            NH3 housing area, m^2/animal.

        """
        if 'Cow' in self.classes_in_pen:
            return 3.5
        elif 'HeiferII' in self.classes_in_pen:
            return 2.5
        else:
            return 2.0

    @property
    def barn_area(self) -> float:
        """Calculates the barn area for this pen based on its housing type.

        Returns
            Barn area, m^2/animal.

        """
        BarnArea = NamedTuple('BarnArea', [('has_cows', float), ('no_cows', float)])
        tie_stall = BarnArea(has_cows=1.2, no_cows=1.0)
        bedded_pack = BarnArea(has_cows=5.0, no_cows=3.0)
        free_stall = BarnArea(has_cows=3.5, no_cows=2.5)
        default = free_stall

        housing_type_to_barn_area = {
            'tie stall': tie_stall,
            'bedded pack': bedded_pack,
            'free stall': free_stall
        }
        barn_area = housing_type_to_barn_area.get(self.housing_type, default)

        if 'Cow' in self.classes_in_pen:
            return barn_area.has_cows
        else:
            return barn_area.no_cows
