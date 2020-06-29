from pathlib import Path

from RUFAS.output_handler.reports import BaseReport
from .. import graphics


class LifeCycleReport:
    def __init__(self, data):

        # self.graphic_dir = Path
        self.csv_dir = Path
        self.report_name = data['report_name']
        self.produce_csv = data['produce_csv']
        self.produce_graphics = data['produce_graphics']
        self.life_cycle_reports = {
            'individual_animal_report': self.IndividualAnimalReport(data['individual_animal_report']),
            'herd_report': self.HerdReport(data['herd_report'])
        }

    def initialize(self):
        if self.produce_csv:
            for report in self.life_cycle_reports.values():
                if not report.produce_csv and report.produce_graphics:
                    print("Warning: Cannot produce graphics_1 for inactive report:", report.report_name,
                          ". Setting produce_graphics to False")
                    report.produce_graphics = False
                if report.produce_csv:
                    report.initialize()

    def daily_update(self, state, weather, time):
        if self.produce_csv:
            for report in self.life_cycle_reports.values():
                if report.produce_csv:
                    report.daily_update(state, weather, time)

    def annual_update(self, state, weather, time):
        if self.produce_csv:
            for report in self.life_cycle_reports.values():
                if report.produce_csv:
                    report.annual_update(state, weather, time)

    def write_annual_report(self):
        if self.produce_csv:
            for report in self.life_cycle_reports.values():
                if report.produce_csv:
                    report.write_annual_report()

    def annual_flush(self):
        if self.produce_csv:
            for report in self.life_cycle_reports.values():
                if report.produce_csv:
                    report.annual_flush()

    def initialize_life_cycle_csv_dir(self):
        for report_name in self.life_cycle_reports:
            self.life_cycle_reports[report_name].csv_dir = Path(str(self.csv_dir) + '/' + report_name)
            self.life_cycle_reports[report_name].csv_dir.mkdir(exist_ok=True, parents=False)

    # def produce_report_graphics(self):
    #     if self.produce_graphics:
    #         for report in self.life_cycle_reports.values():
    #             report.produce_report_graphics()

    class IndividualAnimalReport(BaseReport):
        def __init__(self, data):
            super().__init__(data)

            self.daily_variables = {}
            self.annual_variables = {}

    class HerdReport(BaseReport):
        def __init__(self, data):
            super().__init__(data)

            self.daily_variables = {}
            self.annual_variables = {}
