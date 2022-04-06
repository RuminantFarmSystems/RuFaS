from __future__ import annotations

from enum import Enum


class ManureHandlerEnum(Enum):
    FLUSH_SYSTEM = 'flush_system'
    MANUAL_SCRAPING = 'manual_scraping'
    ALLEY_SCRAPER = 'alley_scraper'
    NULL_MANURE_HANDLER = 'null'
    CUSTOM_MANURE_HANDLER = 'custom'

    @classmethod
    def get_enum(cls, manure_handler: str, default='flush_system') -> ManureHandlerEnum:
        for e in cls:  # Iterate through each enum member
            if manure_handler.lower() in e.value.lower():
                return e
        else:
            print(f'{manure_handler} is not currently implemented as a handling method. '
                  f'Setting to {default}')
            return cls.get_enum(default)
