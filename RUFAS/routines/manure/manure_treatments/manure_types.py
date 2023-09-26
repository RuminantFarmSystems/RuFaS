from enum import Enum


class ManureType(Enum):
    """
    This is an Enum class that represents different types of manure.

    The Enum class contains the following members:
    LIQUID: Represents liquid manure.
    SLURRY: Represents manure in a semi-liquid, slurry state.
    SOLID: Represents manure in solid form.

    """

    LIQUID = "liquid"
    SLURRY = "slurry"
    SOLID = "solid"
