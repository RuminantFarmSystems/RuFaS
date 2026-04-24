from typing import TypedDict

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType


class GeneticHistory(TypedDict):
    """
    A class to represent the genetic history of an individual animal on a farm.

    This class is used to track the genetic attributes of an animal over the course of a simulation.
    It contains information about the simulation day, the age of the animal in days, and its genetic attributes.

    Attributes
    ----------
    start_day : int
        The simulation day corresponding to the start of the genetic record of the animal.
    end_day : int
        The simulation day corresponding to the end of the genetic record of the animal.
    id : int
        The unique identifier of the animal.
    animal_type : AnimalType
        The type of animal.
    genetics: dict[str, float]
        Dictionary containing the genetic attributes of the animal.
    """

    start_day: int
    end_day: int

    id: int
    animal_type: AnimalType

    genetics: dict[str, float]
