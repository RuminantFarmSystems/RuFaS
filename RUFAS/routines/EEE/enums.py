from enum import Enum


class TillageImplement(Enum):
    SUBSOILER = "subsoiler"
    MOLDBOARD_PLOW = "moldboard-plow"
    COULTER_CHISEL_PLOW = "coulter-chisel-plow"
    DISK_HARROW = "disk-harrow"
    CULTIVATOR = "cultivator"
    SEEDBED_CONDITIONER = "seedbed-conditioner"

    def __str__(self):
        return self.value


class TractorSize(Enum):
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"


class OperationType(Enum):
    PLANTING = "Planting"
    TILLING = "Tilling"
    LIQUID_MANURE_APPLICATION_SURFACE = "Liquid Manure Application - Surface"
    LIQUID_MANURE_APPLICATION_BELOW_SURFACE = "Liquid Manure Application - Below Surface"
    FERTILIZER_APPLICATION_SURFACE = "Fertilizer Application - Surface"
    FERTILIZER_APPLICATION_BELOW_SURFACE = "Fertilizer Application - Below Surface"
    MOWING = "Mowing"
    COLLECTION = "Collection"
    WINDROWING = "Windrowing"


class FieldOperationEvent(Enum):
    HARVEST = "harvest"
    FERTILIZER_APPLICATION = "Fertilizer Application"
    MANURE_APPLICATION = "Manure Application"
    PLANTING = "planting"
    TILLING = "tilling"
