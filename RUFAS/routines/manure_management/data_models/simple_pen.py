from typing import Set, Type

from RUFAS.routines.animal.pen import Pen
from .manure import Manure
from ...animal.life_cycle.animal_base import AnimalBase


class SimplePen:
    """
    A simplified Pen class that extracts only relevant information from the
    original Pen class in the AnimalManagement module.

    Attributes:
        manure: A Manure object that captures the manure data from the `pen` object argument

    Args:
        pen: A Pen object from the AnimalManagement module

    """

    def __init__(self, pen: Pen):
        self.manure = Manure(**pen.manure)

        self.id: int = pen.id
        self.animals_in_pen: [AnimalBase] = pen.animals_in_pen
        self.classes_in_pen: Set[Type[AnimalBase]] = pen.classes_in_pen

        self.housing_type: str = pen.housing_type
        self.bedding_type: str = pen.bedding_type

        self.manure_handler: str = pen.manure_handling
        self.manure_separator: str = pen.manure_separator
        self.manure_storage: str = pen.manure_storage

        self.manure_density: float = 990.0  # kg/m^3

    def __str__(self) -> str:
        s = ['SimplePen data:']

        for var in vars(self):
            if var == 'animals_in_pen':
                s.append(f'animals_in_pen: {[animal.__class__.__name__ for animal in self.animals_in_pen]}')
            elif var == 'classes_in_pen':
                s.append(f'classes_in_pen: {[klass.__name__ for klass in self.classes_in_pen]}')
            else:
                s.append(f'{var}: {getattr(self, var)}')

        return '\n'.join(s)
