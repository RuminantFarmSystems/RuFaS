from RUFAS.routines.animal import AnimalManagement
from .simple_pen import SimplePen


class SimpleAnimalManagement:
    """
    A simplified AnimalManagement class that extracts only relevant information from the
    original AnimalManagement class in the AnimalManagement module.

    Attributes:
        all_pens: A list of SimplePen objects extracted from the AnimalManagement object argument

    Args:
        animal_management: An AnimalManagement object that has an `all_pens` attribute

    """

    def __init__(self, animal_management: AnimalManagement):
        self.all_pens = [SimplePen(pen) for pen in animal_management.all_pens]
        self.sim_day = animal_management.simulation_day

    def __str__(self) -> str:
        s = ''
        for idx, pen in enumerate(self.all_pens):
            s += f'Pen {idx}: \n {str(pen)} \n'
        return s
