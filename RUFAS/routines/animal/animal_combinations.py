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
    GROWING_AND_CLOSE_UP: int
        Represents a pen with all heifers and dry cows only.
    """

    CALF = 0  # calves
    GROWING = 1  # heiferIs, heiferIIs
    CLOSE_UP = 2  # heiferIIIs, dry cows
    LAC_COW = 3  # lactating cows
    GROWING_AND_CLOSE_UP = 4  # all heifers and dry cows
