"""
RUFAS: Ruminant Farm Systems Model

File name: storage_pond.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu 
            Yunus Mohammed, ymm26@cornell.edu
"""


class BaseStorage:
    """
        Description
        ------------

        Attributes
        ----------

    """

    def __init__(self, storage, storage_data):
        """
        Description:
            An instance of this class represents an storage receptacle.
            It is primarily used by the emissions sub-module

        Args:
            storage
            storage_data
        """
        self.storage_name = storage

        self.sludge_accumulation_volume = storage_data['sludge_accumulation_volume'] if \
            'sludge_accumulation_volume' in storage_data else 0.00251
        self.hydraulic_retention_time = storage_data['hydraulic_retention_time'] if \
            'hydraulic_retention_time' in storage_data else 180
        self.sludge_accumulation_period = storage_data['sludge_accumulation_period'] if \
            'sludge_accumulation_period' in storage_data else 5.0

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

        self.WIP = 0
        self.WOP = 0

        self.WOP_frac = 0
        self.WIP_frac = 0

        self.CH4 = 0

    def reset_daily_variables(self):
        pass

    def reset_annual_variables(self):
        pass

    def update_all(self, manure):
        self.methane(manure)
        self.WIP_WOP_frac()

    def methane(self, manure):
        manure.CH4_emissions = self.VS * manure.Bo * manure.MCF * manure.MS * manure.m3

    def WIP_WOP_frac(self):
        self.WIP_frac = 0 if (self.TS + self.VS == 0) else (self.WIP / (self.TS + self.VS))
        self.WOP_frac = 0 if (self.TS + self.VS == 0) else (self.WOP / (self.TS + self.VS))
