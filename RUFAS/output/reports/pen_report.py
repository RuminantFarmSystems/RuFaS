"""
RUFAS: Ruminant Farm Systems Model
File name: pen_report.py
Description:
Author(s): William Donovan, wmdonovan@wisc.edu
"""
from pathlib import Path

from RUFAS.output.reports import BaseReport
from .. import graphics


class PenReport:
    def __init__(self, data, pen_id):

        self.diagnostic_dir = Path
        self.csv_dir = Path
        self.report_name = data['report_name']
        self.produce_csv = data['produce_csv']
        self.produce_graphics = data['produce_graphics']
        self.pen_reports = {
            'ration_report': self.RationReport(data['ration_report'], pen_id),
            'growth_report': self.GrowthReport(data['growth_report'], pen_id),
            'manure_report': self.ManureReport(data['manure_report'], pen_id)
        }

    def initialize(self):
        if self.produce_csv:
            for report in self.pen_reports.values():
                if not report.produce_csv and report.produce_graphics:
                    print("Warning: Cannot produce graphics for inactive report:", report.report_name,
                          ". Setting produce_graphics to False")
                    report.produce_graphics = False
                if report.produce_csv:
                    report.initialize()

    def initialize_pen_csv_dir(self, pen_dir):
        for report_name in self.pen_reports:
            csv_dir = pen_dir / report_name
            csv_dir.mkdir(exist_ok=True, parents=False)
            self.pen_reports[report_name].csv_dir = csv_dir

    def initialize_pen_diagnostic_dir(self, pen_dir):
        for report_name in self.pen_reports:
            diagnostic_dir = pen_dir / report_name
            diagnostic_dir.mkdir(exist_ok=True, parents=False)
            self.pen_reports[report_name].diagnostic_dir = diagnostic_dir

    def daily_update(self, state, weather, time):
        if self.produce_csv:
            for report in self.pen_reports.values():
                if report.produce_csv:
                    report.daily_update(state, weather, time)

    def annual_update(self, state, weather, time):
        if self.produce_csv:
            for report in self.pen_reports.values():
                if report.produce_csv:
                    report.annual_update(state, weather, time)

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

    def produce_report_graphics(self):
        if self.produce_graphics:
            for report in self.pen_reports.values():
                report.produce_report_graphics()

    class BasePenReport(BaseReport):
        def __init__(self, data, pen_id):
            super().__init__(data)
            self.pen_id = pen_id

        def daily_update(self, state, weather, time):
            soil = state.soil
            crop_type = state.crop.current_crop
            animal_management = state.animal_management
            feed = state.feed

            pen = state.animal_management.all_pens[self.pen_id]

            for variable in self.daily_variables:
                self.daily_variables[variable][2].append(
                    eval(self.daily_variables[variable][0], globals(), locals()))

    class GrowthReport(BasePenReport):
        def __init__(self, data, pen_id):
            super().__init__(data, pen_id)

            self.daily_variables = {'year': ['time.cal_year', '', []],
                                    'j_day': ['time.day', '', []],
                                    'num_animals_in_pen': ['len(pen.animals_in_pen)', '', []],
                                    'average_growth': ['pen.avg_growth', 'kg', []],
                                    'average_milk': ['pen.avg_milk', 'kg', []]
                                    }

            self.annual_variables = {'year': ['time.cal_year', '', 0]
                                     }

    class ManureReport(BasePenReport):
        def __init__(self, data, pen_id):
            super().__init__(data, pen_id)

            self.daily_variables = {'year': ['time.cal_year', '', []],
                                    'j_day': ['time.day', '', []],
                                    'num_animals': ['len(pen.animals_in_pen)', '', []]
                                    }
            self.annual_variables = {'year': ['time.cal_year', '', 0]}

            self.manure_info = {}

    class RationReport(BasePenReport):
        def __init__(self, data, pen_id):
            super().__init__(data, pen_id)
            self.ration_interval = data['ration_interval']

            self.daily_variables = {'year': ['time.cal_year', '', []],
                                    'j_day': ['time.day', '', []],
                                    'num_animals': ['len(pen.animals_in_pen)', '', []],
                                    'achieved_price': ['pen.ration[\'objective\'] if pen.pen_populated else 0', '', []]
                                    }

            self.annual_variables = {
                'year': ['time.cal_year', '', 0]
            }

        def produce_report_graphics(self):
            super().produce_report_graphics()
            graphics.ration_graphics(self)
