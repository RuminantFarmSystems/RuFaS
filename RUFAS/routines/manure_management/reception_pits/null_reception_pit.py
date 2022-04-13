from .base_reception_pit import BaseReceptionPit
from .reception_pit_init_data import ReceptionPitInitData
from ..data_models.simple_pen import SimplePen
from ..manure_separators.manure_separator_classes.base_separator import BaseSeparator


class NullReceptionPit(BaseReceptionPit):
    def __init__(self,
                 pen: SimplePen,
                 manure_separator: BaseSeparator,
                 reception_pit_init_data: ReceptionPitInitData):
        super().__init__(pen, manure_separator, reception_pit_init_data)

    def update(self, pen: SimplePen):
        # TODO: this will need to be changed when improvements are made to the base reception pit class
        super().update(pen)
