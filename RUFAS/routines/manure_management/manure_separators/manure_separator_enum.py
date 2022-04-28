from __future__ import annotations

from enum import auto

from RUFAS.routines.manure_management.helpers.enum_helpers import ExtendedEnum


class ManureSeparatorEnum(ExtendedEnum):
    BASE_SEPARATOR = auto
    BELT_PRESS = auto
    CUSTOM_SEPARATOR = auto
    DECANTING_CENTRIFUGE = auto
    MECHANICAL_SEPARATOR = auto
    MOVING_DISC_PRESS = auto
    NULL_SEPARATOR = auto
    ROTARY_SCREEN = auto
    SCREW_PRESS = auto
    SEDIMENTATION = auto
    SLOPE_SCREEN = auto

    DEFAULT = SEDIMENTATION
