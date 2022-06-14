"""
RUFAS: Ruminant Farm Systems Model

File name: mechanical_separator.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu
"""


from .base_treatment import BaseTreatment


class AnaerobicDigester(BaseTreatment):
    """
    Description
    ------------

    Attributes
    ----------

    """
    
    def __init__(self, treatment, treatment_data, storage):
        super().__init__(treatment, treatment_data, storage)
