from typing import List

from RUFAS.routines.animal import AnimalManagement
from .simple_pen import SimplePen


class SimpleAnimalManagement:
    """
    A simplified AnimalManagement class that extracts only relevant information from the
    original AnimalManagement class in the animal module.

    """

    def __init__(self, animal_management: AnimalManagement):
        """
        Initializes a SimpleAnimalManagement object.

        Args:
            animal_management: An AnimalManagement object from the animal module.

        """

        self._all_pens = [SimplePen(pen) for pen in animal_management.all_pens]
        self._sim_day = animal_management.simulation_day

    @property
    def all_pens(self) -> List[SimplePen]:
        """
        Returns a list of SimplePen objects extracted from the animal module.
        This would be helpful when handling output data.

        Returns:
            A list of SimplePen objects.

        """

        return self._all_pens

    @property
    def sim_day(self) -> int:
        """
        Returns the simulation day when this SimpleAnimalManagement was created.

        Returns:
            The simulation day when this SimpleAnimalManagement was created.

        """

        return self._sim_day
