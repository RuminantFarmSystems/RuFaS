from .base_reception_pit import BaseReceptionPit
from .reception_pit_init_data import ReceptionPitInitData
from ..data_models.simple_pen import SimplePen
from ..manure_handlers.manure_handler_classes.base_manure_handler import BaseManureHandler


class NullReceptionPit(BaseReceptionPit):
    def __init__(self,
                 pen: SimplePen,
                 manure_handler: BaseManureHandler,
                 reception_pit_init_data: ReceptionPitInitData):
        super().__init__(pen, manure_handler, reception_pit_init_data)

    def update(self, pen: SimplePen):
        # TODO: this will need to be changed when improvements are made to the base reception pit class
        super().update(pen)
