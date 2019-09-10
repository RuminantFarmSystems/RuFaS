from .soil_summary import SoilSummary
from .crop_summary import CropSummary
from .soil_nitrogen import SoilNitrogen
from .soil_phosphorus import SoilPhosphorus
from .water_balance import WaterBalance


class FieldSummary:
    def __init__(self, field_name, data):

        self.report_name = field_name
        self.active = data['active']
        self.produce_diagnostics = data['produce_diagnostics']

        self.field_reports = {'crop_summary': CropSummary(data['crop_summary'], field_name),
                              'soil_summary': SoilSummary(data['soil_summary'], field_name),
                              'soil_nitrogen': SoilNitrogen(data['soil_nitrogen'], field_name),
                              'soil_phosphorus': SoilPhosphorus(data['soil_phosphorus'], field_name),
                              'water_balance': WaterBalance(data['water_balance'], field_name)
                              }

    def initialize(self, state):
        for report in self.field_reports.values():
            report.initialize(state)

    def initialize_field_dir(self, field_dir):
        for report in self.field_reports:
            report_dir = field_dir / report
            report_dir.mkdir(exist_ok=True, parents=False)

    def daily_update(self, state, weather, time):
        for field in state.fields:
            if self.report_name == field.field_name:
                for report in self.field_reports.values():
                    report.daily_update(field, weather, time)

    def annual_update(self, state, weather, time):
        for field in state.fields:
            if self.report_name == field.field_name:
                for report in self.field_reports.values():
                    report.annual_update(field, weather, time)

    def write_annual_report(self):
        for report in self.field_reports.values():
            report.write_annual_report()

    def annual_flush(self):
        for report in self.field_reports.values():
            report.annual_flush()

    def produce_data_analysis(self, is_final):
        for report in self.field_reports.values():
            report.produce_data_analysis(is_final)
