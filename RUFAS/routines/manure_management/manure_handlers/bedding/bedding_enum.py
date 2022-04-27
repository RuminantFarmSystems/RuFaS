from __future__ import annotations

from enum import auto

from RUFAS.routines.manure_management.helpers.enum_helpers import ExtendedEnum


class BeddingEnum(ExtendedEnum):
    ORGANIC = auto
    SAND = auto

    DEFAULT = SAND
