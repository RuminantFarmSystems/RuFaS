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


    def __init__(self, storage_data):
        """
        Description:
            An instance of this class represents an storage receptacle.
            It is primarily used by the emissions sub-module

        Args:
            storage_data
        """
        self.default = None

        if storage_data is None or storage_data['default']:
            self.default = True
            self.set_defaults()
        else:
            self.sludge_accumulation_volume = storage_data["sludge_accumulation_volume"]
            self.hydraulic_retention_time = storage_data["hydraulic_retention_time"]
            self.sludge_accumulation_period = storage_data["sludge_accumulation_period"]

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

        self.WOP_frac = 0
        self.WIP_frac = 0

    def set_defaults(self):
        self.sludge_accumulation_volume = 0.00251
        self.hydraulic_retention_time = 180
        self.sludge_accumulation_period = 5.0

    def update_all(self, manure):
        self.methane(manure)

    def methane(self, manure):
        manure.CH4_emissions = self.VS * manure.Bo * manure.MCF * manure.MS * \
                               manure.m3 * manure.CH4_collection_efficiency
