"""
RUFAS: Ruminant Farm Systems Model

File name: alley_scraper.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu 
"""


from .base_handler import BaseHandler


class AlleyScraper(BaseHandler):
    """
    Description
    ------------

    Attributes
    ----------

    """ 

    def __init__(self, manure_management_data, handler_data, pen):
        super().__init__(manure_management_data, handler_data, pen)
        if self.default: self.set_defaults()

    def set_defaults(self):
        super().set_defaults()
        self.water_use_rate = 100
        self.time_per_cleaning = 8
        self.cleanings_per_day = 2
