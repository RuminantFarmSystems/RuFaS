"""
RUFAS: Ruminant Farm Systems Model
File name: field_report.py

Author(s): William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com

Description: Each field is comprised of multiple reports, handled within this
                shell.
"""

from .soil_report import SoilSummary
from .crop_report import CropSummary
from .soil_nitrogen_report import SoilNitrogen
from .soil_phosphorus_report import SoilPhosphorus
from .water_balance import WaterBalance
from .custom_report import CustomReport


class FieldSummary:
    def __init__(self, field_name, data):

        self.report_name = field_name
        self.produce_csv = data['produce_csv']
        self.produce_graphics = data['produce_graphics']

        self.field_reports = {'crop_summary': CropSummary(data['crop_summary'], field_name),
                              'soil_summary': SoilSummary(data['soil_summary'], field_name),
                              'soil_nitrogen': SoilNitrogen(data['soil_nitrogen'], field_name),
                              'soil_phosphorus': SoilPhosphorus(data['soil_phosphorus'], field_name),
                              'water_balance': WaterBalance(data['water_balance'], field_name),
                              'custom_report': CustomReport(data['custom_report'], field_name)
                              }

    def initialize(self, state):
        """
        Description:
            Call initialize for each active report in the field
        """

        for report in self.field_reports.values():
            report.initialize(state)

    def initialize_field_dir(self, field_dir):
        """
        Description:
            Creates a directory in the outputs folder for the field
        """

        for report in self.field_reports:
            report_dir = field_dir / report
            report_dir.mkdir(exist_ok=True, parents=False)

    def daily_update(self, state, weather, time):
        """
        Description:
            Called from output_handler for each day in the simulation.
            Calls daily_update for each active report in the field.
        """

        for field in state.fields:
            if self.report_name == field.field_name:
                for report in self.field_reports.values():
                    report.daily_update(field, weather, time)

    def annual_update(self, state, weather, time):
        """
        Description:
            Called from output_handler at the end of each simulation year.
            Calls annual_update for each active report in the field.
        """

        for field in state.fields:
            if self.report_name == field.field_name:
                for report in self.field_reports.values():
                    report.annual_update(field, weather, time)

    def write_annual_report(self):
        """
        Description:
            Called from output_handler at the end of each simulation year.
            Calls write_annual_report for each active report in the field.
        """

        for report in self.field_reports.values():
            report.write_annual_report()

    def annual_flush(self):
        """
        Description:
            Called from output_handler at the end of each simulation year.
            Calls annual_flush for each active report in the field.
        """

        for report in self.field_reports.values():
            report.annual_flush()

    def produce_report_graphics(self, is_final):
        """
        Description:
            Called from output_handler at the end of the simulation.
            Calls produce_report_graphics for each active report in the field.
        Inputs:
            is_final: boolean value indicating whether this is the final report
        """

        for report in self.field_reports.values():
            report.produce_report_graphics(is_final)
