from typing import Dict, Type

from RUFAS.routines.manure_management.manure_handlers.alley_scraper import AlleyScraper
from RUFAS.routines.manure_management.manure_handlers.base_manure_handler import BaseManureHandler
from RUFAS.routines.manure_management.manure_handlers.custom_manure_handler import CustomManureHandler
from RUFAS.routines.manure_management.manure_handlers.flush_system import FlushSystem
from RUFAS.routines.manure_management.manure_handlers.manual_scraping import ManualScraping
from RUFAS.routines.manure_management.manure_handlers.manure_handler_enum import ManureHandlerEnum
from RUFAS.routines.manure_management.manure_handlers.null_manure_handler import NullManureHandler


class ManureHandlerFactory:
    @classmethod
    def get_manure_handler(cls, manure_handler: str, pen, handler, handler_data, reception_pit) -> BaseManureHandler:
        manure_handler_enum = ManureHandlerEnum.get_enum(manure_handler)

        params = {
            'pen': pen,
            'handler': handler,
            'handler_data': handler_data,
            'reception_pit': reception_pit
        }

        manure_handler_enum_to_class: Dict[ManureHandlerEnum: Type[BaseManureHandler]] = {
            ManureHandlerEnum.FLUSH_SYSTEM: FlushSystem,
            ManureHandlerEnum.ALLEY_SCRAPER: AlleyScraper,
            ManureHandlerEnum.MANUAL_SCRAPING: ManualScraping,
            ManureHandlerEnum.NULL_MANURE_HANDLER: NullManureHandler,
            ManureHandlerEnum.CUSTOM_MANURE_HANDLER: CustomManureHandler
        }

        if manure_handler_enum in manure_handler_enum_to_class:
            return manure_handler_enum_to_class[manure_handler_enum](**params)

        raise NotImplementedError(f'Class for type {manure_handler_enum} is not currently implemented.')
