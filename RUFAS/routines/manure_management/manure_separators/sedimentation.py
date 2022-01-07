"""
RUFAS: Ruminant Farm Systems Model

File name: sedimentation.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu 
"""

from .base_separator import BaseSeparator


class Sedimentation(BaseSeparator):
    """
    Description
    ------------

    Attributes
    ----------

    """ 

    def __init__(self, separator, separator_data, treatment):
        super().__init__(separator, separator_data, treatment)
