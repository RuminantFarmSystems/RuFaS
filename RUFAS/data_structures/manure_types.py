from enum import Enum


class ManureType(Enum):
    """
    This is an Enum class that represents different types of manure.

    Attributes
    ----------
    LIQUID : str
        Represents liquid manure.
    SOLID : str
        Represents manure in solid form.
    """

    LIQUID = "liquid"
    SOLID = "solid"
