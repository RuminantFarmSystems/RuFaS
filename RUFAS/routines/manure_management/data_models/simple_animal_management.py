from RUFAS.routines.animal import AnimalManagement
from simple_pen import SimplePen


class SimpleAnimalManagement:
    """
    A simplified AnimalManagement class that extracts only relevant information from the
    original AnimalManagement class in the AnimalManagement module.

    Args:
        all_pens: A list of SimplePen objects extracted from the AnimalManagement object argument

    """

    def __init__(self, animal_management: AnimalManagement):
        self.all_pens = [SimplePen(pen) for pen in animal_management.all_pens]
