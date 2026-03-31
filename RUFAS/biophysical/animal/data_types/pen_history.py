from typing import TypedDict

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType


class PenHistory(TypedDict):
    """
    A class to represent the history of a pen on a farm.

    This class tracks the usage of a pen including the start and end dates, the specific pen, and the classes
    of animals that have been in the pen.

    Attributes
    ----------
    start_date : int
        The start date of the pen's usage.
    end_date : int
        The end date of the pen's usage.
    pen : int
        The id of the pen that the animal is in.
    animal_types_in_pen : list[AnimalType]
        The types of animals that have been in the pen.

    """

    start_date: int
    end_date: int
    pen: int
    animal_types_in_pen: list[AnimalType]
