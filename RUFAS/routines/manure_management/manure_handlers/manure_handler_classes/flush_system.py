"""
RUFAS: Ruminant Farm Systems Model

File name: flush_system.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu 
"""

from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes.base_manure_handler import BaseManureHandler


class FlushSystem(BaseManureHandler):
    """
    Description
    ------------

    Attributes
    ----------

    """

    def __init__(self, pen, handler_data, reception_pit):
        super().__init__(pen, handler_data, reception_pit)
