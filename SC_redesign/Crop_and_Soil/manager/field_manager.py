from SC_redesign.Crop_and_Soil.field.field import Field
from RUFAS.classes import Time, Weather, is_leap_year
from SC_redesign.Crop_and_Soil.manager.current_weather import CurrentWeather
from SC_redesign.Crop_and_Soil.manager.output_gatherer import OutputGatherer
from typing import List, Dict, Optional

"""
This module is responsible for initializing the `Field` instances that will be simulated and providing an interface to
the `SimulationEngine` for executing daily and annual routines in the field module.
"""


class FieldManager:
    def __init__(self, _fields_config: Optional[List[Dict[str, str]]] = None):
        self.fields: List[Field] = []
        self.output_gatherer = OutputGatherer(fields=self.fields)

    def daily_update_routine(self, weather: Weather, time: Time) -> None:
        """
        This method will run the daily routine in the field, which will be calling the manage field method on each
        field.

        Parameters
        ----------
        weather: Weather
            A weather object that contains infos to be transformed to current weather
        time: Time
            Object containing the current year and day of the simulation.

        Notes
        -----
        Because different fields can have different latitudes, the day length has to be recalculated for each field.

        """
        for field in self.fields:
            month = FieldManager._date_conversion_month(time)
            current_weather = CurrentWeather.check_current_weather(weather=weather, month=month)
            field.manage_field(time, current_weather=current_weather)
        self.output_gatherer.send_daily_variables()

    def annual_update_routine(self) -> None:
        """
        This method will run the annual routine in the field, which will be calling the perform_annual_reset() method
        on each field.
        """
        for field in self.fields:
            field.perform_annual_reset()
        self.output_gatherer.send_annual_variables()

    @staticmethod
    def _date_conversion_month(time: Time) -> int:
        """
        Converts the day number into the corresponding month of the year.

        Parameters
        ----------
        time: Time
            Object containing the current year and day of the simulation.

        Returns
        -------
        int
            The corresponding month of the year.

        """
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
        """
        Converts the day number into the corresponding day of the month.
        Parameters
        ----------
        time:
            Object containing the current year and day of the simulation.

        Returns
        -------
        int
        Corresponding day of the month.

        """
        days = [31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
        leap_days = [31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366]

        if is_leap_year(time.calendar_year):
            return time.day - leap_days[FieldManager._date_conversion_month(time) - 2]
        else:
            return time.day - days[FieldManager._date_conversion_month(time) - 2]
