from .base_manure_handler import BaseManureHandler


class NullManureHandler(BaseManureHandler):
    def __init__(self, pen, reception_pit, handler='null_handler', handler_data=None):
        if handler_data is None:
            handler_data = {
                'time_per_cleaning': 0,
                'cleanings_per_day': 0,
                'water_use_rate': 0
            }
        super().__init__(pen, handler, handler_data, reception_pit)

    def update_all(self, pen):
        self.update_handler(pen)
        self.update_reception_pit()

    def update_reception_pit(self):
        self.reception_pit.N += self.N_excreted
        self.reception_pit.P += self.P_excreted
        self.reception_pit.K += self.K_excreted
        self.reception_pit.TS += self.TS_loss
        self.reception_pit.VS += self.VS_loss
        self.reception_pit.CH4 += self.CH4
        self.reception_pit.WIP += self.WIP
        self.reception_pit.WOP += self.WOP
        self.reception_pit.flush_water_volume += self.raw_manure
