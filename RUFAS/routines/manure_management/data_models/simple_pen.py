from RUFAS.routines import Pen
from manure import Manure


class SimplePen:
    """
    A simplified Pen class that extracts only relevant information from the
    original Pen class in the AnimalManagement module.

    Args:
        manure: A Manure object that captures the manure data from the Pen object argument

    """

    def __init__(self, pen: Pen):
        self.manure = Manure(**pen.manure)
