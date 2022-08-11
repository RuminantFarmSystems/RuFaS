from typing import List

from RUFAS.routines.animal import AnimalManagement
from RUFAS.routines.manure.simple_pen.simple_pen import SimplePen


class SimpleAnimalManagement:
    """
    A simplified AnimalManagement class that extracts only relevant information from the
    original AnimalManagement class in the animal module. Since not every detail of the
    AnimalManagement class is relevant to the manure module, this abridged version also
    allows more flexibility via renaming or adding additional attributes and functions.

    """

    def __init__(self, animal_management: AnimalManagement):
        """
        Initializes a SimpleAnimalManagement object. This object does not store
        any reference to the passed-in argument and only performs a read on it.

        Args:
            animal_management: An AnimalManagement object from the animal module.

        Attributes:
            _all_pens: A list of SimplePen objects created based on their Pen counterparts.
            _sim_day: Keeps track of the simulation day on which this object was created.

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
        Returns the simulation day on which this object was created.

        Returns:
            The simulation day on which this object was created.

        """

        return self._sim_day
