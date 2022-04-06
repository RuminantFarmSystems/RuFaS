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

    def __str__(self) -> str:
        return f'SimplePen data: \n' \
               f'manure = {self.manure} \n' \
               f'id = {self.id} \n' \
               f'classes in pen = {self.classes_in_pen} \n' \
               f'housing type = {self.housing_type} \n' \
               f'bedding type = {self.bedding_type}'
