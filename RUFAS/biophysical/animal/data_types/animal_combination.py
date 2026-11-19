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
    FEEDLOT_FINISHING : str
        Represents a feedlot finishing pen with steers and/or heifers.
    BEEF_COW_CALF_PAIR : str
        A pen with lactating beef cows and their nursing calves at side.
    BEEF_GESTATING : str
        A pen with gestating beef cows that are dry (no calf at side).
    BEEF_REPLACEMENT : str
        A pen with beef replacement heifers growing toward first calving.
    BEEF_BULL_BATTERY : str
        A pen with bulls outside the breeding season.
    BEEF_STOCKER : str
        A pen with stocker/backgrounding animals.

    """

    CALF = "calf"
    GROWING = "growing"
    CLOSE_UP = "close_up"
    LAC_COW = "lac_cow"
    GROWING_AND_CLOSE_UP = "growing and close_up"
    FEEDLOT_FINISHING = "feedlot_finishing"
    """Represents a feedlot finishing pen with steers and/or heifers."""
    BEEF_COW_CALF_PAIR = "beef_cow_calf_pair"
    BEEF_GESTATING = "beef_gestating"
    BEEF_REPLACEMENT = "beef_replacement"
    BEEF_BULL_BATTERY = "beef_bull_battery"
    BEEF_STOCKER = "beef_stocker"
