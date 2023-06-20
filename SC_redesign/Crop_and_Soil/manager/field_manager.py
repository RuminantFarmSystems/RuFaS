from SC_redesign.Crop_and_Soil.field.field import Field
from RUFAS.classes import Time
from SC_redesign.Crop_and_Soil.manager.current_weather import CurrentWeather
from SC_redesign.Crop_and_Soil.manager.output_gatherer import OutputGatherer
from typing import List
from SC_redesign.Crop_and_Soil.crop.harvest_operations import HarvestOperation

om = OutputGatherer()


class FieldManager:
    def __init__(self, fields: List[Field]):
        self.fields = fields

    def daily_update_routine(self, current_weather: CurrentWeather, time: Time):
        for field in self.fields:
            field.manage_field(time, current_weather)
            om.send_daily_variables()

    def annual_update_routine(self, operation: HarvestOperation, time: Time):
        year = time.calendar_year
        day = time.day
        for field in self.fields:
            for crop in field.crops:
                crop.crop_management.manage_harvest(harvest_op=operation, field_name=field.field_data.name,
                                                    field_size=field.field_data.field_size, year=year, day=day,
                                                    soil_data=field.soil.data)
                om.send_annual_variables()




