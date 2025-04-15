from enum import Enum


class AnimalCombination(Enum):
    """
    Enumeration that represents the valid combinations of animals in a pen.

    Attributes
    ----------
    CALF : str
        Represents a calf-only pen.
    GROWING : str
        Represents a pen with growing heiferI and heiferII only.
    CLOSE_UP : str
        Represents a pen with heiferIII and dry cows only.
    LAC_COW : str
        Represents a pen with lactating cows only.
    GROWING_AND_CLOSE_UP : str
        Represents a pen with heifer Is, IIs, IIIs and dry cows.

    """

    CALF = "calf"
    GROWING = "growing"
    CLOSE_UP = "close_up"
    LAC_COW = "lac_cow"
    GROWING_AND_CLOSE_UP = "growing and close_up"
