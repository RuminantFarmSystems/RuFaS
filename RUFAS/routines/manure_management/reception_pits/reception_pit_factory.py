from RUFAS.routines.manure_management.data_models.simple_pen import SimplePen
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes.base_manure_handler import \
    BaseManureHandler
from RUFAS.routines.manure_management.manure_handlers.manure_handler_enum import ManureHandlerEnum
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes.base_separator import BaseSeparator
from RUFAS.routines.manure_management.reception_pits.base_reception_pit import BaseReceptionPit
from RUFAS.routines.manure_management.reception_pits.reception_pit_enum import ReceptionPitEnum
from RUFAS.routines.manure_management.reception_pits.reception_pit_init_data import ReceptionPitInitData


class ReceptionPitFactory:
    # TODO: Add criteria for each kind of reception pit
    @classmethod
    def get_instance(cls, pen: SimplePen, manure_separator: BaseSeparator) -> BaseReceptionPit:
        params = {
            'pen': pen,
            'manure_separator': manure_separator,
            'reception_pit_init_data': cls.get_reception_pit_init_data()
        }
        return BaseReceptionPit(**params)

    # TODO: Add data for each kind of reception pit
    @classmethod
    def get_reception_pit_init_data(cls) -> ReceptionPitInitData:
        return ReceptionPitInitData()
