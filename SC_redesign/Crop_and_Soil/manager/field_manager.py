from SC_redesign.Crop_and_Soil.field.field import Field
from RUFAS.classes import Time, Weather
from SC_redesign.Crop_and_Soil.manager.current_weather import CurrentWeather
from SC_redesign.Crop_and_Soil.manager.output_gatherer import OutputGatherer
from typing import List


class FieldManager:
    def __init__(self, fields: List[Field]):
        self.fields = fields
        self.om - OutputGatherer()

    def daily_update_routine(self, weather: CurrentWeather, time: Time):
        for field in self.fields:
            field.manage_field(time, weather)
        self.om.send_daily_variables()

    def annual_update_routine(self):
        for field in self.fields:
            field.perform_annual_reset()
        self.om.send_annual_variables()
