from typing import Dict, Type

from RUFAS.routines.manure_management.data_models.simple_pen import SimplePen
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes.alley_scraper import AlleyScraper
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes.base_manure_handler import \
    BaseManureHandler
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes.custom_manure_handler import \
    CustomManureHandler
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes.flush_system import FlushSystem
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes.manual_scraping import ManualScraping
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes.null_manure_handler import \
    NullManureHandler
from RUFAS.routines.manure_management.manure_handlers.manure_handler_enum import ManureHandlerEnum
from RUFAS.routines.manure_management.manure_handlers.manure_handler_init_data import ManureHandlerInitData


class ManureHandlerFactory:
    @classmethod
    def get_instance(cls, pen: SimplePen) -> BaseManureHandler:
        manure_handler_enum = ManureHandlerEnum.get_enum(pen.manure_handler)

        params = {
            'pen': pen,
            'handler_data': cls.get_manure_handler_init_data(manure_handler_enum)
        }

        enum_to_class: Dict[ManureHandlerEnum, Type[BaseManureHandler]] = {
            ManureHandlerEnum.FLUSH_SYSTEM: FlushSystem,
            ManureHandlerEnum.ALLEY_SCRAPER: AlleyScraper,
            ManureHandlerEnum.MANUAL_SCRAPING: ManualScraping,
            ManureHandlerEnum.NULL_MANURE_HANDLER: NullManureHandler,
            ManureHandlerEnum.CUSTOM_MANURE_HANDLER: CustomManureHandler
        }

        return enum_to_class[manure_handler_enum](**params)

    @classmethod
    def get_manure_handler_init_data(cls, manure_handler_enum: ManureHandlerEnum) -> ManureHandlerInitData:
        init_data = ManureHandlerInitData()
        enum_to_water_use_rate: Dict[ManureHandlerEnum, int] = {
            ManureHandlerEnum.FLUSH_SYSTEM: 757,
            ManureHandlerEnum.MANUAL_SCRAPING: 10,
            ManureHandlerEnum.ALLEY_SCRAPER: 10
        }
        if manure_handler_enum in enum_to_water_use_rate:
            init_data.water_use_rate = enum_to_water_use_rate[manure_handler_enum]
        return init_data
