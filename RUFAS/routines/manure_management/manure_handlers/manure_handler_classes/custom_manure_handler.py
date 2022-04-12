from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes.base_manure_handler import BaseManureHandler
from RUFAS.routines.manure_management.manure_handlers.manure_handler_init_data import ManureHandlerInitData
from RUFAS.routines.manure_management.data_models.simple_pen import SimplePen


class CustomManureHandler(BaseManureHandler):
    def __init__(self, pen: SimplePen, handler_data: ManureHandlerInitData, reception_pit):
        super().__init__(pen, handler_data, reception_pit)
