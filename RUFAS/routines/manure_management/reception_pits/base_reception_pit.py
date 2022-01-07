class BaseReceptionPit:
    def __init__(self, reception_pit, reception_pit_data, separator):
        self.pit_name = reception_pit
        self.separator = separator

        self.TS = 0
        self.VS = 0

        self.N = 0
        self.P = 0
        self.K = 0
        self.CH4 = 0
        self.WIP = 0
        self.WOP = 0

        self.flush_water_volume = 0

    def reset_daily_variables(self):
        self.TS = 0
        self.VS = 0

        self.N = 0
        self.P = 0
        self.K = 0
        self.CH4 = 0
        self.WIP = 0
        self.WOP = 0

        self.flush_water_volume = 0

    def reset_annual_variables(self):
        pass

    def update_all(self):
        self.flush_water()
        self.N_effluent()
        self.P_effluent()
        self.K_effluent()
        self.effluent_solids()
        self.CH4_effluent()
        self.WIP_WOP()

    def flush_water(self):
        self.separator.flush_water_volume += self.flush_water_volume

    def N_effluent(self):
        self.separator.N += self.N

    def P_effluent(self):
        self.separator.P += self.P

    def K_effluent(self):
        self.separator.K += self.K

    def effluent_solids(self):
        self.separator.TS += self.TS
        self.separator.VS += self.VS

    def CH4_effluent(self):
        self.separator.CH4 += self.CH4

    def WIP_WOP(self):
        self.separator.WIP += self.WIP
        self.separator.WOP += self.WOP
