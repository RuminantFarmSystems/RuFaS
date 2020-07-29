"""
RUFAS: Ruminant Farm Systems Model
File name: mass_balance_report.py
Description:
Author(s): William Donovan, wmdonovan@wisc.edu
"""

from .. import graphics
from .base_report_driver import BaseReportDriver
from .base_report import BaseReport


class MassBalanceReport(BaseReportDriver):
    def __init__(self, data):
        super().__init__(data)
        self.reports = {}

    class BaseMassBalanceReport(BaseReport):
        def __init__(self, data):
            super().__init__(data)

        def produce_report_graphics(self):
            super().produce_report_graphics()
            graphics.annual_mass_balance_graphics(self)
