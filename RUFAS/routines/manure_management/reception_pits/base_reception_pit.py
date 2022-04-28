from RUFAS.routines.manure_management.data_models.simple_pen import SimplePen
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes.base_manure_handler import \
    BaseManureHandler
from RUFAS.routines.manure_management.reception_pits.reception_pit_init_data import ReceptionPitInitData
from RUFAS.routines.manure_management.reception_pits.reception_pit_variables import ReceptionPitVariables


class BaseReceptionPit:
    def __init__(self,
                 pen: SimplePen,
                 manure_handler: BaseManureHandler,
                 reception_pit_init_data: ReceptionPitInitData):
        self.flush_water_volume = 0.0
        self.pen = pen
        self.manure_handler = manure_handler
        self.reception_pit_init_data = reception_pit_init_data
        self.daily_vars = ReceptionPitVariables()

    def reset_daily_variables(self):
        self.daily_vars = ReceptionPitVariables()

    # TODO: Check logic
    # Should rely on the variables from the manure handler
    def update(self):
        d = self.daily_vars
        # self.manure_separator.daily_vars += ManureSeparatorVariables(
        #         flush_water_volume=d.flush_water_volume,
        #         N=d.N,
        #         P=d.P,
        #         K=d.K,
        #         TS=d.TS,
        #         VS=d.VS,
        #         CH4=d.CH4,
        #         WIP=d.WIP,
        #         WOP=d.WOP
        # )

    def flush_water(self):
        # self.separator.flush_water_volume += self.flush_water_volume
        pass

    def N_effluent(self):
        # self.separator.N += self.N
        pass

    def P_effluent(self):
        # self.separator.P += self.P
        pass

    def K_effluent(self):
        # self.separator.K += self.K
        pass

    def effluent_solids(self):
        # self.separator.TS += self.TS
        # self.separator.VS += self.VS
        pass

    def CH4_effluent(self):
        # self.separator.CH4 += self.CH4
        pass

    def WIP_WOP(self):
        # self.separator.WIP += self.WIP
        # self.separator.WOP += self.WOP
        pass
