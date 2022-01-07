"""
RUFAS: Ruminant Farm Systems Model

File name: anaerobic_lagoon.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu 
            Yunus Mohammed, ymm26@cornell.edu
"""


from .base_storage import BaseStorage


class AnaerobicLagoon(BaseStorage):
    """
    Description
    ------------

    Attributes
    ----------

    """
       
    def __init__(self, storage, storage_data):
        super().__init__(storage, storage_data)
