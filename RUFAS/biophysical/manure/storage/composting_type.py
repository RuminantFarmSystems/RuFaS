from enum import Enum


class CompostingType(Enum):
    """
    This is an Enum class that represents different types of composting.

    Attribute
    ----------
    INTENSIVE_WINDROW : str
        Intensive windrow.
    PASSIVE_WINDROW : str
        Passive windrow.
    STATIC_PILE : str
        Static pile.
    IN_VESSEL : str
        In vessel.
    """

    INTENSIVE_WINDROW = "intensive windrow"
    PASSIVE_WINDROW = "passive windrow"
    STATIC_PILE = "static pile"
    IN_VESSEL = "in vessel"
