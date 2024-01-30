from enum import Enum


class AnimalCombination(Enum):
    """
    Enumeration that represents the valid combinations of animals in a pen.
    """
    CALF = 0  # calves
    GROWING = 1  # heiferIs, heiferIIs
    CLOSE_UP = 2  # heiferIIIs, dry cows
    LAC_COW = 3  # lactating cows
    GROWING_AND_CLOSE_UP = 4  # all heifers and dry cows
