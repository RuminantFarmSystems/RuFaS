from .base_handler import BaseHandler


class ManualScraping(BaseHandler):
    def __init__(self, manure_management_data, handler_data, pen):
        super().__init__(manure_management_data, handler_data, pen)
        if self.default: self.set_defaults()

    def set_defaults(self):
        super().set_defaults()
        self.water_use_rate = 200
        self.time_per_cleaning = 8
        self.cleanings_per_day = 2
