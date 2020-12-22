from .base_storage import BaseStorage


class FacultativeLagoon(BaseStorage):
    def __init__(self, storage_data, pen):
        super().__init__(storage_data, pen)
        if self.default: self.set_defaults()

    def set_defaults(self):
        self.sludge_accumulation_volume = 0.00251
        self.hydraulic_retention_time = 180
        self.sludge_accumulation_period = 5.0
