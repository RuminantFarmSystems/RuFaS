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
        self.TS_removal_efficiency = 0.3
        self.VS_removal_efficiency = 0.55
        self.N_removal_efficiency = 0.3
        self.P_removal_efficiency = 0.4
        self.K_removal_efficiency = 0.15
        self.TS_DM_effluent_rate = 0.2

    def update_all(self, manure):
        """
        Description:
            Calls functions to calculate nutrient losses and transformations during
            manure separation.
            "pseudocode_manure_storage" MS.4

        Args:
            self: an instance of the Separator class defined in
                manure_management.py
            manure: an instance of the ManureStorage class defined in
                manure_management.py
        """
        self.effluent_liquid()
        self.effluent_solid()
        self.update_storage(manure)

    def effluent_liquid(self):
        """
        Description:
            Calculate liquid nutrient content of the separator
            "pseudocode_manure_storage" MS.4.A
        """

        self.TS_liquid = self.TS - (self.TS * self.TS_removal_efficiency)
        self.VS_liquid = self.VS - (self.VS * self.VS_removal_efficiency)
        self.N_liquid = self.N - self.N * self.N_removal_efficiency
        self.P_liquid = self.P - self.P * self.P_removal_efficiency
        self.K_liquid = self.K - self.K * self.K_removal_efficiency

    def effluent_solid(self):
        """
        Description:
            Update solid nutrient content of the separator
            "pseudocode_manure_storage" MS.4.B
        """

        self.TS -= self.TS_liquid
        self.TS_DM_effluent = self.TS * self.TS_DM_effluent_rate
        self.TS -= self.TS_DM_effluent

        self.VS -= self.VS_liquid
        self.N -= self.N_liquid
        self.P -= self.P_liquid
        self.K -= self.K_liquid

    def update_storage(self, manure):
        """
        Description:
            Update solid and liquid nutrient contents of the storage receptacle
            "pseudocode_manure_storage" MS.4.C

        Args:
            self
            manure
        """

        manure.storage[self.storage].TS += self.TS
        manure.storage[self.storage].TS_liquid += self.TS_liquid

        manure.storage[self.storage].VS += self.VS
        manure.storage[self.storage].VS_liquid += self.VS_liquid

        manure.storage[self.storage].N += self.N
        manure.storage[self.storage].N_liquid += self.N_liquid

        manure.storage[self.storage].P += self.P
        manure.storage[self.storage].P_liquid += self.P_liquid

        manure.storage[self.storage].K += self.K
        manure.storage[self.storage].K_liquid += self.K_liquid
