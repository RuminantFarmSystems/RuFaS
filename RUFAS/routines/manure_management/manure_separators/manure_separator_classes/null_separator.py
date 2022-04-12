from .base_separator import BaseSeparator
from ..manure_separator_init_data import ManureSeparatorInitData
from ...data_models.simple_pen import SimplePen
from ...storage_options.storage_option_classes.base_storage import BaseStorage


class NullSeparator(BaseSeparator):
    def __init__(self,
                 pen: SimplePen,
                 separator_data: ManureSeparatorInitData,
                 storage_option: BaseStorage):
        super().__init__(pen, separator_data, storage_option)

    def update(self):
        super().update_storage_option_variables()
