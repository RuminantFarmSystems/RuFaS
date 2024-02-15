from enum import Enum


class TractorSize(Enum):
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"


class OperationType(Enum):
    PLANTING = "Planting"
    TILLING = "Tilling"
    LIQUID_MANURE_APPLICATION_SURFACE = "Liquid Manure Application: Surface"
    LIQUID_MANURE_APPLICATION_BELOW_SURFACE = "Liquid Manure Application: Below Surface"
    FERTILIZER_APPLICATION_SURFACE = "Fertilizer Application: Surface"
    FERTILIZER_APPLICATION_BELOW_SURFACE = "Fertilizer Application: Below Surface"
    MOWING = "Mowing"
    COLLECTION = "Collection"
    WINDROWING = "windrowing"


class CropType(Enum):
    ALFALFA_HAY = "alfalfa_hay"
    ALFALFA_SILAGE = "alfalfa_silage"
    ALFALFA_BALEAGE = "alfalfa_baleage"
    TALL_FESCUE_HAY = "tall_fescue_hay"
    TALL_FESCUE_SILAGE = "tall_fescue_silage"
    TALL_FESCUE_BALEAGE = "tall_fescue_baleage"


class FieldOperationEvent(Enum):
    HARVEST = "harvest"
    FERTILIZER_APPLICATION = "Fertilizer Application"
    MANURE_APPLICATION = "Manure Application"
    PLANTING = "planting"
    TILLING = "tilling"


class TillageImplement(Enum):
    """
    Defines the supported tillage implements for RuFaS.

    Attributes
    ----------
    SUBSOILER : str
        Subsoiler.
    MOLDBOARD_PLOW : str
        Moldboard plow.
    COULTER_CHISEL_PLOW : str
        Coulter-chisel plow.
    DISK_HARROW : str
        Disk harrow.
    CULTIVATOR : str
        Cultivator.
    SEEDBED_CONDITIONER : str
        Seedbed conditioner.

    """

    SUBSOILER = "subsoiler"
    MOLDBOARD_PLOW = "moldboard-plow"
    COULTER_CHISEL_PLOW = "coulter-chisel-plow"
    DISK_HARROW = "disk-harrow"
    CULTIVATOR = "cultivator"
    SEEDBED_CONDITIONER = "seedbed-conditioner"

    def __str__(self):
        return self.value

    def __repr__(self):
        return repr(self.value)
