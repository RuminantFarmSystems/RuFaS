from RUFAS.routines.manure.default_enum.default_enum import DefaultEnum


class ManureTreatmentType(DefaultEnum):
    """Enumerates the different types of manure treatments.

    Attributes
    ----------
    SLURRY_STORAGE_UNDERFLOOR : str
        Slurry storage underfloor.
    SLURRY_STORAGE_OUTDOOR : str
        Slurry storage outdoor.
    ANAEROBIC_LAGOON : str
        Anaerobic lagoon.
    ANAEROBIC_DIGESTION : str
        Anaerobic digestion.
    ANAEROBIC_DIGESTION_AND_LAGOON : str
        Anaerobic digestion and lagoon.
    ANAEROBIC_DIGESTION_AND_LAGOON_WITH_SEPARATOR : str
        Anaerobic digestion and lagoon with separator.
    COMPOSTING : str
        Composting.
    COMPOST_BEDDED_PACK_BARN : str
        Compost bedded pack barn.
    OPEN_LOTS : str
        Open lots.
    SEPARATED_SOLIDS_STORAGE : str
        Separated solids storage.

    Notes
    -----
    The DEFAULT manure treatmenet type is SLURRY_STORAGE_UNDERFLOOR
    """

    SLURRY_STORAGE_UNDERFLOOR = "slurry storage underfloor"
    SLURRY_STORAGE_OUTDOOR = "slurry storage outdoor"
    ANAEROBIC_LAGOON = "anaerobic lagoon"
    ANAEROBIC_DIGESTION = "anaerobic digestion"
    ANAEROBIC_DIGESTION_AND_LAGOON = "anaerobic digestion and lagoon"
    ANAEROBIC_DIGESTION_AND_LAGOON_WITH_SEPARATOR = (
        "anaerobic digestion and lagoon with separator"
    )
    COMPOSTING = "composting"
    COMPOST_BEDDED_PACK_BARN = "compost bedded pack barn"
    OPEN_LOTS = "open lots"
    SEPARATED_SOLIDS_STORAGE = "separated solids storage"
    DEFAULT = SLURRY_STORAGE_UNDERFLOOR
