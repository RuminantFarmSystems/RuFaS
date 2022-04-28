from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes.base_manure_handler import \
    BaseManureHandler


# TODO: Check logic
class NullManureHandler(BaseManureHandler):
    def __init__(self, pen, reception_pit, handler_data=None):
        super().__init__(pen, handler_data)

    def update_all(self, pen):
        # self.update_handler(pen)
        # self.update_reception_pit()
        pass

    def update_reception_pit(self):
        # self.reception_pit.N += self.N_excreted
        # self.reception_pit.P += self.P_excreted
        # self.reception_pit.K += self.K_excreted
        # self.reception_pit.TS += self.TS_loss
        # self.reception_pit.VS += self.VS_loss
        # self.reception_pit.CH4 += self.CH4
        # self.reception_pit.WIP += self.WIP
        # self.reception_pit.WOP += self.WOP
        # self.reception_pit.flush_water_volume += self.raw_manure
        pass
