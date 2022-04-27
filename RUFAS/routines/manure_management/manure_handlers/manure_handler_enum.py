from __future__ import annotations

from enum import auto

from RUFAS.routines.manure_management.helpers.enum_helpers import ExtendedEnum


class ManureHandlerEnum(ExtendedEnum):
    FLUSH_SYSTEM = auto
    MANUAL_SCRAPING = auto
    ALLEY_SCRAPER = auto
    NULL_MANURE_HANDLER = auto
    CUSTOM_MANURE_HANDLER = auto

    DEFAULT = FLUSH_SYSTEM
