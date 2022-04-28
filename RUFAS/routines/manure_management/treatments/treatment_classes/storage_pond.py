"""
RUFAS: Ruminant Farm Systems Model

File name: storage_pond.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu 
            Yunus Mohammed, ymm26@cornell.edu
"""


from .base_treatment import BaseTreatment


class StoragePond(BaseTreatment):
    """
    Description
    ------------

    Attributes
    ----------

    """
    
    def __init__(self, pen, treatment_init_data):
        super().__init__(pen, treatment_init_data)
