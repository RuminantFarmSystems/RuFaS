from SC_redesign.Crop_and_Soil.field.field import Field
from RUFAS.classes import Time, Weather, is_leap_year
from SC_redesign.Crop_and_Soil.manager.current_weather import CurrentWeather
from SC_redesign.Crop_and_Soil.manager.output_gatherer import OutputGatherer
from typing import List, Dict, Optional

class FieldManager:
    def __init__(self, _fields_config: Optional[List[Dict[str, str]]] = None):
        self.fields: List[Field] = []
        self.om = OutputGatherer(fields=self.fields)

    def daily_update_routine(self, weather: Weather, time: Time):
        for field in self.fields:
            latitude = field.field_data.absolute_latitude
            year = time.calendar_year
            day = FieldManager.date_conversion_day(time)
            month = FieldManager.date_conversion_month(time)
            current_weather = CurrentWeather.check_current_weather(weather=weather, latitude=latitude, year=year,
                                                                   day=day, month=month)
            field.manage_field(time, current_weather=current_weather)
        self.om.send_daily_variables()

    def annual_update_routine(self):
        for field in self.fields:
            field.perform_annual_reset()
        self.om.send_annual_variables()

    @staticmethod
    def _date_conversion_month(time: Time) -> int:
        days = [31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
        leap_days = [31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]
        prev_month = 0
        if is_leap_year(time.calendar_year):
            for day in leap_days:
                if prev_month < time.day <= day:
                    return leap_days.index(day) + 1
                else:
                    prev_month = day
        else:
            for day in days:
                if prev_month < time.day <= day:
                    return days.index(day) + 1
                else:
                    prev_month = day

    @staticmethod
    def _date_conversion_day(time: Time) -> int:
        days = [31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
        leap_days = [31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]

        if is_leap_year(time.calendar_year):
            return time.day - leap_days[FieldManager._date_conversion_month(time) - 2]
        else:
            return time.day - days[FieldManager._date_conversion_month(time) - 2]
