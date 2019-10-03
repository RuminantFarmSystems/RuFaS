################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: crop_summary.py
Description:
Author(s): William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com
"""
###############################################################################

from .ration_report import RationReport
from .growth_report import GrowthReport
from .manure_report import ManureReport


class PenReport:
    def __init__(self, pen_id, data):

        self.report_name = 'pen_' + str(pen_id)
        self.pen_id = pen_id
        self.active = data['active']
        self.produce_graphics = data['produce_graphics']

        self.pen_reports = {'ration_report': RationReport(data['ration_report'], pen_id),
                            'growth_report': GrowthReport(data['growth_report'], pen_id),
                            'manure_report': ManureReport(data['manure_report'], pen_id)
                            }

    def initialize(self, state):
        for report in self.pen_reports.values():
            report.initialize(state)

    def initialize_pen_dir(self, pen_dir):
        for report in self.pen_reports:
            report_dir = pen_dir / report
            report_dir.mkdir(exist_ok=True, parents=False)

    def daily_update(self, state, weather, time):
        if state.animal_management.end_ration_interval():
            for pen in state.animal_management.all_pens:
                if self.pen_id == pen.id:
                    for report in self.pen_reports.values():
                        report.annual_update(pen, weather, time)

    def annual_update(self, state, weather, time):
        for pen in state.animal_management.all_pens:
            if self.pen_id == pen.id:
                for report in self.pen_reports.values():
                    report.annual_update(pen, weather, time)

    def write_annual_report(self):
        for report in self.pen_reports.values():
            report.write_annual_report()

    def annual_flush(self):
        for report in self.pen_reports.values():
            report.annual_flush()

    def produce_report_graphics(self, is_final):
        for report in self.pen_reports.values():
            report.produce_report_graphics(is_final)