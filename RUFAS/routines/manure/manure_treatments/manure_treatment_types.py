from RUFAS.routines.manure.default_enum.default_enum import DefaultEnum


class ManureTreatmentType(DefaultEnum):
    """Enumerates the different types of manure treatments."""

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
