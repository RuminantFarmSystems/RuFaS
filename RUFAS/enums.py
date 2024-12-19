from enum import Enum


class AnimalCombination(Enum):
    """
    Enumeration that represents the valid combinations of animals in a pen.

    Attributes
    ----------
    CALF: int
        Represents a calf-only pen.
    GROWING: int
        Represents a pen with growing heiferI and heiferII only.
    CLOSE_UP: int
        Represents a pen with heiferIII and dry cows only.
    LAC_COW: int
        Represents a pen with lactating cows only.

    """

    CALF = "calf"
    GROWING = "growing"
    CLOSE_UP = "close_up"
    LAC_COW = "lactating"
