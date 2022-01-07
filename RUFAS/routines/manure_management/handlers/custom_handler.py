from .base_handler import BaseHandler


class CustomHandler(BaseHandler):
    def __init__(self, pen, handler, handler_data, reception_pit):
        super().__init__(pen, handler, handler_data, reception_pit)
        self.water_use_rate = handler_data['water_use_rate']
        self.time_per_cleaning = handler_data['time_per_cleaning']
        self.cleanings_per_day = handler_data['cleanings_per_day']
