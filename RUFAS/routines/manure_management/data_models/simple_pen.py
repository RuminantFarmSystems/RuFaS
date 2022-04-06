from RUFAS.routines.animal.pen import Pen
from .manure import Manure


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
        self.animals_in_pen = pen.animals_in_pen
        self.classes_in_pen = pen.classes_in_pen

        self.housing_type: str = pen.housing_type
        self.bedding_type: str = pen.bedding_type

        self.manure_handler: str = pen.manure_handling
        self.manure_separator: str = pen.manure_separator
        self.manure_storage: str = pen.manure_storage

    def __str__(self) -> str:
        s = 'SimplePen data: \n'

        for v in vars(self):
            s += f'{v}: {getattr(self, v)} \n'

        return s
