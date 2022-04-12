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
       
    def __init__(self, pen, storage_option_init_data):
        super().__init__(pen, storage_option_init_data)
