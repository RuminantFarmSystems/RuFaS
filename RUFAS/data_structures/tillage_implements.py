from enum import Enum


class EnumWithStrOverride(Enum):
    def __str__(self):
        return self.value


class TillageImplement(EnumWithStrOverride):
    SUBSOILER = "subsoiler"
    MOLDBOARD_PLOW = "moldboard-plow"
    COULTER_CHISEL_PLOW = "coulter-chisel-plow"
    DISK_HARROW = "disk-harrow"
    CULTIVATOR = "cultivator"
    SEEDBED_CONDITIONER = "seedbed-conditioner"


class TractorSize(EnumWithStrOverride):
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"


class OperationType(EnumWithStrOverride):
    PLANTING = "Planting"
    TILLING = "Tilling"
    LIQUID_MANURE_APPLICATION_SURFACE = "Liquid Manure Application - Surface"
    LIQUID_MANURE_APPLICATION_BELOW_SURFACE = "Liquid Manure Application - Below Surface"
    FERTILIZER_APPLICATION_SURFACE = "Fertilizer Application - Surface"
    FERTILIZER_APPLICATION_BELOW_SURFACE = "Fertilizer Application - Below Surface"
    MOWING = "Mowing"
    COLLECTION = "Collection"
    WINDROWING = "Windrowing"


class FieldOperationEvent(EnumWithStrOverride):
    HARVEST = "Harvest"
    FERTILIZER_APPLICATION = "Fertilizer Application"
    MANURE_APPLICATION = "Manure Application"
    PLANTING = "Planting"
    TILLING = "Tilling"
