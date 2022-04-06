"""
RUFAS: Ruminant Farm Systems Model

File name: flush_system.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu 
"""

from .base_manure_handler import BaseManureHandler


class FlushSystem(BaseManureHandler):
    """
    Description
    ------------

    Attributes
    ----------

    """ 

    def __init__(self, pen, handler, handler_data, reception_pit):
        super().__init__(pen, handler, handler_data, reception_pit)
        self.water_use_rate = handler_data['water_use_rate'] if 'water_use_rate' in handler_data else 500
