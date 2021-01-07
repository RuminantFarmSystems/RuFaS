"""
RUFAS: Ruminant Farm Systems Model

File name: storage_pond.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu 
            Yunus Mohammed, ymm26@cornell.edu
"""


from .base_storage import BaseStorage


class StoragePond(BaseStorage):
     """
    Description
    ------------

    Attributes
    ----------

    """
    
    def __init__(self, storage_data, pen):
        super().__init__(storage_data, pen)
        if self.default: self.set_defaults()

    def set_defaults(self):
        self.sludge_accumulation_volume = 0.00251
        self.hydraulic_retention_time = 180
        self.sludge_accumulation_period = 5.0
