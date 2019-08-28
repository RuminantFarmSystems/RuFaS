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

        self.crop_report = CropSummary(data['crop_summary'])
        self.soil_report = SoilSummary(data['soil_summary'])

        self.soil_nitrogen = SoilNitrogen(data['soil_nitrogen'])
        self.soil_phosphorus = SoilPhosphorus(data['soil_phosphorus'])

        self.water_balance = WaterBalance(data['water_balance'])

    def initialize(self, state):
        self.crop_report.initialize(state)
        self.soil_report.initialize(state)

        self.soil_nitrogen.initialize(state)
        self.soil_phosphorus.initialize(state)

        self.water_balance.initialize(state)

    def daily_update(self, state, weather, time):
        for field in state.fields:
            if self.report_name == field.field_name:
                self.crop_report.daily_update(field, weather, time)
                self.soil_report.daily_update(field, weather, time)

                self.soil_nitrogen.daily_update(field, weather, time)
                self.soil_phosphorus.daily_update(field, weather, time)

                self.water_balance.daily_update(field, weather, time)

    def annual_update(self, state, weather, time):
        for field in state.fields:
            if self.report_name == field.field_name:
                self.crop_report.annual_update(field, weather, time)
                self.soil_report.annual_update(field, weather, time)

                self.soil_nitrogen.annual_update(field, weather, time)
                self.soil_phosphorus.annual_update(field, weather, time)

                self.water_balance.annual_update(field, weather, time)

    def write_annual_report(self):
        self.crop_report.write_annual_report()
        self.soil_report.write_annual_report()

        self.soil_nitrogen.write_annual_report()
        self.soil_phosphorus.write_annual_report()

        self.water_balance.write_annual_report()

    def annual_flush(self):
        self.crop_report.annual_flush()
        self.soil_report.annual_flush()

        self.soil_nitrogen.annual_flush()
        self.soil_phosphorus.annual_flush()

        self.water_balance.annual_flush()

    def produce_data_analysis(self, is_final):
        self.crop_report.produce_data_analysis(is_final)
        self.soil_report.produce_data_analysis(is_final)

        self.soil_nitrogen.produce_data_analysis(is_final)
        self.soil_phosphorus.produce_data_analysis(is_final)

        self.water_balance.annual_flush()
