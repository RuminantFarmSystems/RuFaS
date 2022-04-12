from __future__ import annotations

from enum import auto

from RUFAS.routines.manure_management.helpers.enum_helpers import ExtendedEnum


class StorageOptionEnum(ExtendedEnum):
    STORAGE_POND = auto()
    ANAEROBIC_LAGOON = auto()
    CUSTOM_STORAGE = auto()

    DEFAULT = STORAGE_POND
