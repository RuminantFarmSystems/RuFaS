"""
RUFAS: Ruminant Farm Systems Model

File name: storage_pond.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu 
            Yunus Mohammed, ymm26@cornell.edu
"""
from RUFAS.routines.manure_management.treatments.constants import TreatmentConstants as Constants
from RUFAS.routines.manure_management.data_models.simple_pen import SimplePen
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes.base_manure_handler import \
    BaseManureHandler
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes.base_separator import BaseSeparator
from RUFAS.routines.manure_management.treatments.treatment_init_data import TreatmentInitData
from RUFAS.routines.manure_management.treatments.treatment_variables import TreatmentVariables


class BaseTreatment:
    """
        Description
        ------------

        Attributes
        ----------

    """

    def __init__(self,
                 pen: SimplePen,
                 manure_handler: BaseManureHandler,
                 manure_separator: BaseSeparator,
                 treatment_init_data: TreatmentInitData):
        """
        Description:
            An instance of this class represents an storage receptacle.
            It is primarily used by the emissions sub-module

        Args:
            pen
            treatment_init_data
        """
        self.pen = pen
        self.manure_handler = manure_handler
        self.manure_separator = manure_separator
        self.treatment_init_data = treatment_init_data

        self.daily_vars = TreatmentVariables()

    def reset_daily_variables(self):
        self.daily_vars = TreatmentVariables()

    def update(self):
        # self.methane(pen.manure)
        # self.WIP_WOP_frac()
        pass

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
