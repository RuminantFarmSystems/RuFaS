from enum import Enum


class ManureSupplementMethod(Enum):
    """
    This is an Enum class that represents different methods of manure nutrient deficiencies supplement.

    Attributes
    ----------
    NONE : str
        Represents no supplements.
    SYNTHETIC_FERTILIZER : str
        Represents the usage of synthetic fertilizer supplements.
    MANURE : str
        Represents the usage of manure supplements.

    """

    NONE = "none"
    SYNTHETIC_FERTILIZER = "synthetic fertilizer"
    MANURE = "manure"
    SYNTHETIC_FERTILIZER_AND_MANURE = "synthetic fertilizer and manure"
