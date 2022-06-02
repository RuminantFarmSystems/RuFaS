from RUFAS.routines.manure_management.data_models.simple_pen import SimplePen
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes import \
    BaseManureHandler
from RUFAS.routines.manure_management.reception_pits.base_reception_pit import BaseReceptionPit
from RUFAS.routines.manure_management.reception_pits.reception_pit_init_data import ReceptionPitInitData


class ReceptionPitFactory:
    # TODO: Add criteria for each kind of reception pit
    @classmethod
    def get_instance(cls, pen: SimplePen, manure_handler: BaseManureHandler) -> BaseReceptionPit:
        params = {
            'pen': pen,
            'manure_handler': manure_handler,
            'reception_pit_init_data': cls.get_reception_pit_init_data()
        }
        return BaseReceptionPit(**params)

    # TODO: Add data for each kind of reception pit
    @classmethod
    def get_reception_pit_init_data(cls) -> ReceptionPitInitData:
        return ReceptionPitInitData()
