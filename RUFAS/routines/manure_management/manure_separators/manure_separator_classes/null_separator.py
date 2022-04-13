from .base_separator import BaseSeparator
from ..manure_separator_init_data import ManureSeparatorInitData
from ...data_models.simple_pen import SimplePen
from ...storage_options.storage_option_classes.base_storage import BaseStorage


class NullSeparator(BaseSeparator):
    def __init__(self,
                 pen: SimplePen,
                 storage_option: BaseStorage,
                 separator_data: ManureSeparatorInitData):
        super().__init__(pen, storage_option, separator_data)

    def update(self, pen: SimplePen):
        super().update_storage_option_variables()
