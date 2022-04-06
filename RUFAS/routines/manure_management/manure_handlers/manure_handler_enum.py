from __future__ import annotations

from enum import Enum, auto
from typing import Dict

from RUFAS.routines.manure_management.helpers.misc_functions import format_enum_name


class ManureHandlerEnum(Enum):
    FLUSH_SYSTEM = auto()
    MANUAL_SCRAPING = auto()
    ALLEY_SCRAPER = auto()
    NULL_MANURE_HANDLER = auto()
    CUSTOM_MANURE_HANDLER = auto()

    @classmethod
    def get_enum(cls, manure_handling_method: str) -> ManureHandlerEnum:
        patternToEnum: Dict[str: ManureHandlerEnum] = {
            'flush_system': cls.FLUSH_SYSTEM,
            'alley_scrappers': cls.ALLEY_SCRAPER,
            'manual_scraping': cls.MANUAL_SCRAPING,
            'null': cls.NULL_MANURE_HANDLER,
            'custom': cls.CUSTOM_MANURE_HANDLER,
            'default': cls.FLUSH_SYSTEM
        }
        for pattern, enum_type in patternToEnum.items():
            if pattern in manure_handling_method.lower():
                return enum_type
        else:
            default = patternToEnum['default']
            print(f'{manure_handling_method} is not currently implemented as a handling method. '
                  f'Setting to {format_enum_name(default)}')
            return default
