"""
RUFAS: Ruminant Farm Systems Model

File name: base_separator.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu 
"""
from RUFAS.routines.manure_management.data_models.simple_pen import SimplePen
from RUFAS.routines.manure_management.manure_separators.manure_separator_init_data import ManureSeparatorInitData
from RUFAS.routines.manure_management.manure_separators.manure_separator_variables import ManureSeparatorVariables
from RUFAS.routines.manure_management.storage_options.storage_option_classes.base_storage import BaseStorage


class BaseSeparator:
    """
    Description
    ------------

    Attributes
    ----------

    """

    def __init__(self,
                 pen: SimplePen,
                 separator_data: ManureSeparatorInitData,
                 storage_option: BaseStorage):
        """
        Description:
            An instance of this class represents an manure separator method.
            It is primarily used by the manure separator sub-module

        Args:
        """
        self.pen = pen
        self.separator_init_data = separator_data
        self.storage_option = storage_option

        self.daily_vars = ManureSeparatorVariables()

    def reset_daily_variables(self):
        self.daily_vars = ManureSeparatorVariables()

    def update(self, pen: SimplePen):
        """
        Description:
            Calls functions to calculate nutrient losses and transformations during
            manure separation.
            "pseudocode_manure_management" MS.4

        """

        self.effluent_liquid()
        self.effluent_solid()
        self.update_storage_option_variables()

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

    def update_storage_option_variables(self):
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
