"""
RUFAS: Ruminant Farm Systems Model

File name: moving_dic_press.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu 
"""


from .base_separator import BaseSeparator


class MovingDiscPress(BaseSeparator):
    """
    Description
    ------------

    Attributes
    ----------

    """ 
    
    def __init__(self, treatment_data, pen):
        super().__init__(treatment_data, pen)
        if self.default: self.set_defaults()

    def set_defaults(self):
        self.TS_removal_efficiency = 0.3
        self.VS_removal_efficiency = 0.55
        self.N_removal_efficiency = 0.3
        self.P_removal_efficiency = 0.4
        self.K_removal_efficiency = 0.15
        self.TS_DM_effluent_rate = 0.2
