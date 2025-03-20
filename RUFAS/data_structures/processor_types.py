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
    PARLOR_CLEANING = "parlor_cleaning"

    ROTARY_SCREEN = "rotary_screen"
    SCREW_PRESS = "screw_press"

    ANAEROBIC_DIGESTER = "anaerobic_digester"

    ANAEROBIC_LAGOON = "anaerobic_lagoon"
    SLURRY_STORAGE_OUTDOOR = "slurry_storage_outdoor"
    SLURRY_STORAGE_UNDERFLOOR = "slurry_storage_underfloor"
    COMPOST_BEDDED_PACK_BARN = "compost_bedded_pack_barn"
    OPEN_LOT = "open_lot"
    COMPOSTING = "composting"
