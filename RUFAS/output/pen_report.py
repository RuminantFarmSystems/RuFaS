"""
RUFAS: Ruminant Farm Systems Model
File name: crop_report.py

Author(s): William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com

Description: Output handler for animal growth reports.
"""

from .ration_report import RationReport
from .growth_report import GrowthReport
from .manure_report import ManureReport


class PenReport:

    def __init__(self, pen_id, data):

        self.report_name = 'pen_' + str(pen_id)
        self.pen_id = pen_id
        self.produce_csv = data['produce_csv']
        self.produce_graphics = data['produce_graphics']
        self.output_dir = ''
        self.report_dir = ''

        self.pen_reports = {'ration_report': RationReport(data['ration_report'], pen_id),
                            'growth_report': GrowthReport(data['growth_report'], pen_id),
                            'manure_report': ManureReport(data['manure_report'], pen_id)
                            }

    def initialize(self, state):
        """
        Description:
            Call initialize for each of the pen's active reports.
        """

        if self.produce_csv:
            for report in self.pen_reports.values():
                if not report.produce_csv and report.produce_graphics:
                    print("Warning: Cannot produce graphics for inactive report:", report.report_name,
                          ". Setting produce_graphics to False")
                    report.produce_graphics = False
                if report.produce_csv:
                    report.initialize(state)

    def initialize_pen_output_dir(self, pen_dir):
        """
        Description:
            Creates an output directory in the outputs folder for the pen
        """

        pen_dir = pen_dir / self.report_name
        pen_dir.mkdir(exist_ok=True, parents=False)
        
        for report_name in self.pen_reports:
            report = self.pen_reports[report_name]
            report_dir = pen_dir / report_name
            report_dir.mkdir(exist_ok=True, parents=False)
            report.output_dir = report_dir

    def initialize_pen_diagnostic_dir(self, pen_dir):
        """
        Description:
            Creates a diagnostic directory in the outputs folder for the pen
        """

        for report_name in self.pen_reports:
            report = self.pen_reports[report_name]
            report_dir = pen_dir / report_name
            report_dir.mkdir(exist_ok=True, parents=False)
            report.diagnostic_dir = report_dir

    def daily_update(self, state, weather, time):
        """
        Description:
            Called from output_handler for each day in the simulation.
            Calls daily_update for each of the pen's active reports.
        """

        if self.produce_csv:
            if state.animal_management.end_ration_interval():
                for pen in state.animal_management.all_pens:
                    if self.pen_id == pen.id:
                        for report in self.pen_reports.values():
                            if report.produce_csv:
                                report.daily_update(pen, weather, time)

    def annual_update(self, state, weather, time):
        """
        Description:
            Called from output_handler at the end of each simulation year.
            Calls annual_update for each of the pen's active reports.
        """

        if self.produce_csv:
            for pen in state.animal_management.all_pens:
                if self.pen_id == pen.id:
                    for report in self.pen_reports.values():
                        if report.produce_csv:
                            report.annual_update(pen, weather, time)

    def write_annual_report(self):
        """
        Description:
            Called from output_handler at the end of each simulation year.
            Calls write_annual_report for each of the pen's active reports.
        """

        if self.produce_csv:
            for report in self.pen_reports.values():
                if report.produce_csv:
                    report.write_annual_report()

    def annual_flush(self):
        """
        Description:
            Called from output_handler at the end of each simulation year.
            Calls annual_flush for each of the pen's active reports.
        """

        if self.produce_csv:
            for report in self.pen_reports.values():
                if report.produce_csv:
                    report.annual_flush()

    def produce_report_graphics(self):
        """
        Description:
            Called from output_handler at the end of the simulation.
            Calls produce_report_graphics for each of the pen's active reports.
        """

        if self.produce_graphics:
            for report in self.pen_reports.values():
                report.produce_report_graphics()
