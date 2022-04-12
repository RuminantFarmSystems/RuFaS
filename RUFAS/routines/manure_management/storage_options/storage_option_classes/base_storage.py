"""
RUFAS: Ruminant Farm Systems Model

File name: storage_pond.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu 
            Yunus Mohammed, ymm26@cornell.edu
"""
from RUFAS.routines.manure_management.data_models.constants import ManureManagementConstants as Constants
from RUFAS.routines.manure_management.data_models.simple_pen import SimplePen
from RUFAS.routines.manure_management.storage_options.storage_option_init_data import StorageOptionInitData
from RUFAS.routines.manure_management.storage_options.storage_option_variables import StorageOptionVariables


class BaseStorage:
    """
        Description
        ------------

        Attributes
        ----------

    """

    def __init__(self, pen: SimplePen, storage_option_init_data: StorageOptionInitData):
        """
        Description:
            An instance of this class represents an storage receptacle.
            It is primarily used by the emissions sub-module

        Args:
            pen
            storage_option_init_data
        """
        self.pen = pen
        self.storage_option_init_data = storage_option_init_data

        self.daily_vars = StorageOptionVariables()
        self.annual_vars = StorageOptionVariables()

    def reset_daily_variables(self):
        self.daily_vars = StorageOptionVariables()

    def reset_annual_variables(self):
        self.annual_vars = StorageOptionVariables()

    def update(self, pen: SimplePen):
        self.methane(pen.manure)
        self.WIP_WOP_frac()

    # TODO: Check logic
    def methane(self, manure):
        # manure.CH4_emissions = self.VS * manure.Bo * manure.MCF * manure.MS * manure.m3
        self.daily_vars.CH4 = self.daily_vars.VS * Constants.Bo * Constants.MCF * Constants.MS * Constants.m3

    def WIP_WOP_frac(self):
        daily = self.daily_vars
        if daily.TS + daily.VS == 0:
            daily.WIP_frac = 0.0
            daily.WOP_frac = 0.0
        else:
            daily.WIP_frac = daily.WIP / (daily.TS + daily.VS)
            daily.WOP_frac = daily.WOP / (daily.TS + daily.VS)
