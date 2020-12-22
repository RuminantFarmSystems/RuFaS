class BaseSeparator:
    def __init__(self, separator_data, pen):
        """
        Description:
            An instance of this class represents an manure separator method.
            It is primarily used by the manure separator sub-module

        Args:
        """
        self.storage = pen.storage

        self.default = separator_data['default'] or separator_data is None

        if self.default:
            self.set_defaults()

        else:
            self.TS_removal_efficiency = separator_data['TS_removal_efficiency']
            self.VS_removal_efficiency = separator_data['TS_removal_efficiency']
            self.N_removal_efficiency = separator_data["N_removal_efficiency"]
            self.P_removal_efficiency = separator_data["P_removal_efficiency"]
            self.K_removal_efficiency = separator_data["K_removal_efficiency"]
            self.TS_DM_effluent_rate = separator_data["TS_DM_effluent_rate"]

        self.flush_water_volume = 0

        self.TS = 0
        self.VS = 0
        self.N = 0
        self.P = 0
        self.K = 0

        self.TS_liquid = 0
        self.VS_liquid = 0
        self.N_liquid = 0
        self.P_liquid = 0
        self.K_liquid = 0

        self.TS_DM_effluent = 0

    def set_defaults(self):
        pass
