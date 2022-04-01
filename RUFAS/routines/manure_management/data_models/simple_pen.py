from RUFAS.routines.animal.pen import Pen
from .manure import Manure


class SimplePen:
    """
    A simplified Pen class that extracts only relevant information from the
    original Pen class in the AnimalManagement module.

    Attributes:
        manure: A Manure object that captures the manure data from the `pen` object argument

    Args:
        pen: A Pen object that has a `manure` attribute

    """

    def __init__(self, pen: Pen):
        self.manure = Manure(**pen.manure)

    def __str__(self) -> str:
        return f'SimplePen manure data: {str(self.manure)}'
