from typing import List, NamedTuple, Set, Type

from RUFAS.routines.animal.pen import Pen
from .manure import Manure
from ...animal.life_cycle.animal_base import AnimalBase


class SimplePen:
    """
    A simplified Pen class that extracts only relevant information from the
    original Pen class in the animal module.

    Attributes
    ----------
    manure: A Manure object that captures the manure data from the `pen` object argument
    id:
    animals_in_pen:
    num_animals:
    classes_in_pen:
    housing_type:
    bedding_type:
    manure_handler:
    manure_separator:
    manure_storage:
    manure_density:

    Args
    ----
    pen: A Pen object from the animal module

    """

    def __init__(self, pen: Pen):
        self.manure = Manure(**pen.manure)

        self.id: int = pen.id
        self.animals_in_pen: [AnimalBase] = pen.animals_in_pen
        self.num_animals = len(pen.animals_in_pen)
        self.classes_in_pen: Set[Type[AnimalBase]] = pen.classes_in_pen

        self.housing_type: str = pen.housing_type
        self.bedding_type: str = pen.bedding_type
        self.pen_type: str = pen.get_pen_type()

        self.manure_handler: str = pen.manure_handling
        self.manure_separator: str = pen.manure_separator
        self.manure_storage: str = pen.manure_storage

        self.manure_density = 990.0  # kg/m^3

    @property
    def manure_mass(self) -> float:
        """
        Calculates the manure volume of this pen.

        Returns
        -------
        Manure mass of this pen. Units: kg.

        """
        return self.manure.Mkg  # kg

    @property
    def manure_volume(self) -> float:
        """
        Calculates the manure volume of this pen.

        Returns
        -------
        Manure volume of this pen. Units: m^3.

        """
        return self.manure_mass / self.manure_density  # m^3

    @property
    def housing_area_for_NH3_emission(self) -> float:
        """
        Returns housing area used for calculating NH3 housing emission.

        Returns
        -------
        NH3 housing area. Units: m^2/animal.

        """
        if 'Cow' in self.classes_in_pen:
            return 3.5
        elif 'HeiferII' in self.classes_in_pen:
            return 2.5
        else:
            return 2.0

    @property
    def barn_area(self) -> float:
        """
        Calculates the barn area for this pen depending on its housing type.

        Returns
        -------
        Barn area. Units: m^2/animal.

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
        area = housing_type_to_barn_area.get(self.housing_type, default)

        if 'Cow' in self.classes_in_pen:
            return area.has_cows
        else:
            return area.no_cows


    @property
    def barn_area_from_pen_type(self) -> float:
        """
        Calculates the barn area for this pen depending on its housing type.

        Returns
        -------
        Barn area. Units: m^2/animal.

        """
        BarnArea = NamedTuple('BarnArea', [('has_cows', float), ('no_cows', float)])
        tie_stall = BarnArea(has_cows=1.5, no_cows=1.0)
        free_stall = BarnArea(has_cows=3.5, no_cows=2.5)
        default = free_stall

        pen_type_to_barn_area = {
            'tiestall': tie_stall,
            'freestall': free_stall
        }
        area = pen_type_to_barn_area.get(self.pen_type, default)

        return area.has_cows
