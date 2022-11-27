from RUFAS.routines.manure.default_enum.default_enum import DefaultEnum


class ManureTreatmentType(DefaultEnum):
    """Enumerates the different types of manure treatments."""
    SLURRY_STORAGE_UNDERFLOOR = 'slurry storage underfloor'
    SLURRY_STORAGE_OUTDOOR = 'slurry storage outdoor'
    ANAEROBIC_LAGOON = 'anaerobic lagoon'
    ANAEROBIC_DIGESTION = 'anaerobic digestion'
    DEFAULT = SLURRY_STORAGE_UNDERFLOOR
