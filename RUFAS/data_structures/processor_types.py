from enum import Enum


class ProcessorTypes(Enum):
    """
    This is an Enum class that represents different types of manure processors.

    Attributes
    ----------
    ALLEY_SCRAPER : str
    MANUAL_SCRAPER : str
    FLUSH_SYSTEM : str
    PARLOR_CLEANING : str
    ROTARY_SCREEN : str
    SCREW_PRESS : str
    ANAEROBIC_DIGESTER : str
    ANAEROBIC_LAGOON : str
    SLURRY_STORAGE_OUTDOOR : str
    SLURRY_STORAGE_UNDERFLOOR : str
    COMPOST_BEDDED_PACK_BARN : str
    OPEN_LOT : str
    COMPOSTING : str

    """

    ALLEY_SCRAPER = "alley_scraper"
    MANUAL_SCRAPER = "manual_scraper"
    FLUSH_SYSTEM = "flush_system"
    PARLOR_CLEANING = "parlor cleaning"

    ROTARY_SCREEN = "rotary screen"
    SCREW_PRESS = "screw press"

    ANAEROBIC_DIGESTER = "anaerobic digester"

    ANAEROBIC_LAGOON = "anaerobic lagoon"
    SLURRY_STORAGE_OUTDOOR = "slurry storage outdoor"
    SLURRY_STORAGE_UNDERFLOOR = "slurry storage underfloor"
    COMPOST_BEDDED_PACK_BARN = "compost bedded pack barn"
    OPEN_LOT = "open lot"
    COMPOSTING = "composting"
