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
from RUFAS.routines.manure_management.manure_handlers.manure_handler_factory import ManureHandlerFactory


def test_get_instance_should_return_correct_manure_handler_based_on_matching_str(simple_pen0: SimplePen) -> None:
    str_to_class: Dict[str, Type[BaseManureHandler]] = {
        'flush_system': FlushSystem,
        'manual_scraping': ManualScraping,
        'alley_scraper': AlleyScraper,
        'null': NullManureHandler,
        'custom': CustomManureHandler
    }
    for manure_handler_str, manure_handler_class in str_to_class.items():
        simple_pen0.manure_handler = manure_handler_str
        manure_handler = ManureHandlerFactory.get_instance(simple_pen0)
        assert type(manure_handler) is manure_handler_class
