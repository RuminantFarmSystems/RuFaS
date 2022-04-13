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
from RUFAS.routines.manure_management.storage_options.storage_option_variables import StorageOptionVariables


class BaseSeparator:
    """
    Description
    ------------

    Attributes
    ----------

    """

    def __init__(self,
                 pen: SimplePen,
                 storage_option: BaseStorage,
                 separator_data: ManureSeparatorInitData):
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

    # TODO: Check logic
    def effluent_liquid(self):
        """
        Description:
            Calculate liquid nutrient content of the separator
            "pseudocode_manure_management" MS.4.A
        """
        d = self.daily_vars
        d.TS_liquid = d.TS - (d.TS * self.separator_init_data.TS_removal_efficiency)
        d.VS_liquid = d.VS - (d.VS * self.separator_init_data.VS_removal_efficiency)
        d.N_liquid = d.N - (d.N * self.separator_init_data.N_removal_efficiency)
        d.P_liquid = d.P - (d.P * self.separator_init_data.P_removal_efficiency)
        d.K_liquid = d.K - (d.K * self.separator_init_data.K_removal_efficiency)

    # TODO: Check logic
    def effluent_solid(self):
        """
        Description:
            Update solid nutrient content of the separator
            "pseudocode_manure_management" MS.4.B
        """
        d = self.daily_vars
        d.TS -= d.TS_liquid
        d.TS_DM_effluent = d.TS * self.separator_init_data.TS_DM_effluent_rate
        d.TS -= d.TS_DM_effluent

        d.VS -= d.VS_liquid
        d.N -= d.N_liquid
        d.P -= d.P_liquid
        d.K -= d.K_liquid

    # TODO: Check logic
    def update_storage_option_variables(self):
        """
        Description:
            Update solid and liquid nutrient contents of the treatment receptacle
            "pseudocode_manure_management" MS.4.C
        """
        d = self.daily_vars
        self.storage_option.daily_vars += StorageOptionVariables(
                TS=d.TS,
                TS_liquid=d.TS_liquid,
                VS=d.VS,
                VS_liquid=d.VS_liquid,
                N=d.N,
                N_liquid=d.N_liquid,
                P=d.P,
                P_liquid=d.P_liquid,
                K=d.K,
                K_liquid=d.K_liquid,
                CH4=d.CH4,
                WIP=d.WIP,
                WOP=d.WOP
        )
