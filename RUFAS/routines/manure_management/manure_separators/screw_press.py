"""
RUFAS: Ruminant Farm Systems Model

File name: screw_press.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu 
"""

from .base_separator import BaseSeparator


class ScrewPress(BaseSeparator):
    """
    Description
    ------------

    Attributes
    ----------

    """

    def __init__(self, separator, separator_data, treatment):
        super().__init__(separator, separator_data, treatment)
