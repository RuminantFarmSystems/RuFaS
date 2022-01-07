"""
RUFAS: Ruminant Farm Systems Model

File name: base_separator.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu 
"""


class BaseSeparator:
    """
    Description
    ------------

    Attributes
    ----------

    """ 

    def __init__(self, separator, separator_data, treatment):
        """
        Description:
            An instance of this class represents an manure separator method.
            It is primarily used by the manure separator sub-module

        Args:
        """
        self.separator_name = separator
        self.treatment = treatment

        self.TS_removal_efficiency = separator_data['TS_removal_efficiency'] if \
            'TS_removal_efficiency' in separator_data else 0.3
        self.VS_removal_efficiency = separator_data['VS_removal_efficiency'] if \
            'VS_removal_efficiency' in separator_data else 0.55
        self.N_removal_efficiency = separator_data['N_removal_efficiency'] if \
            'N_removal_efficiency' in separator_data else 0.3
        self.P_removal_efficiency = separator_data['P_removal_efficiency'] if \
            'P_removal_efficiency' in separator_data else 0.4
        self.K_removal_efficiency = separator_data['K_removal_efficiency'] if \
            'K_removal_efficiency' in separator_data else 0.15
        self.TS_DM_effluent_rate = separator_data['TS_DM_effluent_rate'] if \
            'TS_DM_effluent_rate' in separator_data else 0.2

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

        self.WIP = 0
        self.WOP = 0
        self.CH4 = 0

    def reset_daily_variables(self):
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

        self.WIP = 0
        self.WOP = 0
        self.CH4 = 0

    def reset_annual_variables(self):
        pass

    def update_all(self):
        """
        Description:
            Calls functions to calculate nutrient losses and transformations during
            manure separation.
            "pseudocode_manure_management" MS.4

        Args:
            self: an instance of the Separator class defined in
                manure_management.py
            manure: an instance of the ManureManagement class defined in
                manure_management.py
        """
        self.effluent_liquid()
        self.effluent_solid()
        self.update_treatment()

    def effluent_liquid(self):
        """
        Description:
            Calculate liquid nutrient content of the separator
            "pseudocode_manure_management" MS.4.A
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
            "pseudocode_manure_management" MS.4.B
        """

        self.TS -= self.TS_liquid
        self.TS_DM_effluent = self.TS * self.TS_DM_effluent_rate
        self.TS -= self.TS_DM_effluent

        self.VS -= self.VS_liquid
        self.N -= self.N_liquid
        self.P -= self.P_liquid
        self.K -= self.K_liquid

    def update_treatment(self):
        """
        Description:
            Update solid and liquid nutrient contents of the treatment receptacle
            "pseudocode_manure_management" MS.4.C
        """

        self.treatment.TS += self.TS
        self.treatment.TS_liquid += self.TS_liquid

        self.treatment.VS += self.VS
        self.treatment.VS_liquid += self.VS_liquid

        self.treatment.N += self.N
        self.treatment.N_liquid += self.N_liquid

        self.treatment.P += self.P
        self.treatment.P_liquid += self.P_liquid

        self.treatment.K += self.K
        self.treatment.K_liquid += self.K_liquid

        self.treatment.CH4 += self.CH4

        self.treatment.WIP += self.WIP
        self.treatment.WOP += self.WOP
