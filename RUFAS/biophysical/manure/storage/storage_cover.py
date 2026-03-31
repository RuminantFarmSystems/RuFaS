from enum import Enum


class StorageCover(Enum):
    """
    Types of covers supported for manure storage systems.

    Attributes
    ----------
    COVER : str
        Impermeable, human-made cover.
    CRUST : str
        Naturally-formed crust in the manure.
    NO_COVER : str
        No covering or crust of any kind.
    COVER_AND_FLARE : str
        Human-made cover that burns off methane produced by stored manure.

    """

    COVER = "cover"
    CRUST = "crust"
    NO_COVER = "no_crust_or_cover"
    COVER_AND_FLARE = "cover_and_flare"
