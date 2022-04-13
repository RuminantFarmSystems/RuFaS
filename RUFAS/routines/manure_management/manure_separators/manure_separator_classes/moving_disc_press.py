"""
RUFAS: Ruminant Farm Systems Model

File name: moving_dic_press.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu 
"""

from .base_separator import BaseSeparator
from ..manure_separator_init_data import ManureSeparatorInitData
from ...data_models.simple_pen import SimplePen
from ...storage_options.storage_option_classes.base_storage import BaseStorage


class MovingDiscPress(BaseSeparator):
    """
    Description
    ------------

    Attributes
    ----------

    """

    def __init__(self,
                 pen: SimplePen,
                 storage_option: BaseStorage,
                 separator_data: ManureSeparatorInitData):
        super().__init__(pen, storage_option, separator_data)
