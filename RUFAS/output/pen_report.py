"""
RUFAS: Ruminant Farm Systems Model
File name: crop_report.py
Description:
Author(s): William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com
"""

from RUFAS.output.graphics import show_figures
from .ration_report import RationReport
from .growth_report import GrowthReport
from .manure_report import ManureReport


class PenReport:
    def __init__(self, pen_id, data):

        self.report_name = 'pen_' + str(pen_id)
        self.pen_id = pen_id
        self.produce_csv = data['produce_csv']
        self.produce_graphics = data['produce_graphics']

        self.pen_reports = {'ration_report': RationReport(data['ration_report'], pen_id),
                            'growth_report': GrowthReport(data['growth_report'], pen_id),
                            'manure_report': ManureReport(data['manure_report'], pen_id)
                            }

    def initialize(self, state):
        if self.produce_csv:
            for report in self.pen_reports.values():
                if not report.produce_csv and report.produce_graphics:
                    print("Warning: Cannot produce graphics for inactive report:", report.report_name,
                          ". Setting produce_graphics to False")
                    report.produce_graphics = False
                if report.produce_csv:
                    report.initialize(state)

    def initialize_pen_dir(self, pen_dir):
        for report in self.pen_reports:
            report_dir = pen_dir / report
            report_dir.mkdir(exist_ok=True, parents=False)

    def daily_update(self, state, weather, time):
        if self.produce_csv:
            if state.animal_management.end_ration_interval():
                for pen in state.animal_management.all_pens:
                    if self.pen_id == pen.id:
                        for report in self.pen_reports.values():
                            if report.produce_csv:
                                report.daily_update(pen, weather, time)

    def annual_update(self, state, weather, time):
        if self.produce_csv:
            for pen in state.animal_management.all_pens:
                if self.pen_id == pen.id:
                    for report in self.pen_reports.values():
                        if report.produce_csv:
                            report.annual_update(pen, weather, time)

    def write_annual_report(self):
        if self.produce_csv:
            for report in self.pen_reports.values():
                if report.produce_csv:
                    report.write_annual_report()

    def annual_flush(self):
        if self.produce_csv:
            for report in self.pen_reports.values():
                if report.produce_csv:
                    report.annual_flush()

    def produce_report_graphics(self, is_final):
        if self.produce_graphics:
            for report in self.pen_reports.values():
                report.produce_report_graphics(is_final)
        else:
            show_figures(is_final)