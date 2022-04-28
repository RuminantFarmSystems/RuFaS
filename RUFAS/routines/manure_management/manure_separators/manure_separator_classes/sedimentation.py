"""
RUFAS: Ruminant Farm Systems Model

File name: sedimentation.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu 
"""

from .base_separator import BaseSeparator
from ..manure_separator_init_data import ManureSeparatorInitData
from ...data_models.simple_pen import SimplePen
from ...reception_pits.base_reception_pit import BaseReceptionPit


class Sedimentation(BaseSeparator):
    """
    Description
    ------------

    Attributes
    ----------

    """

    def __init__(self,
                 pen: SimplePen,
                 reception_pit: BaseReceptionPit,
                 separator_data: ManureSeparatorInitData):
        super().__init__(pen, reception_pit, separator_data)
