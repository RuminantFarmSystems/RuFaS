from RUFAS.routines.manure.default_enum.default_enum import DefaultEnum


class CompostingType(DefaultEnum):
    """
    This is an Enum class that represents different types of composting.

    Attribute
    ----------
    INTENSIVE_WINDROW : str
        Intensive windrow.
    PASSIVE_WINDROW : str
        Passive windrow.
    STATIC_PILE: str
        Static pile.

    """
    INTENSIVE_WINDROW = "intensive windrow"
    PASSIVE_WINDROW = "passive windrow"
    STATIC_PILE = "static pile"
