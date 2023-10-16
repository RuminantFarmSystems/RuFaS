from dataclasses import dataclass
from typing import Optional

from RUFAS.classes.time import Time
from RUFAS.classes.config import is_leap_year


@dataclass
class CurrentWeather:
    """
    The purpose of this class is to combine and covert infos from weather data and field data and creates a
    current weather class that have all the needed attributes to allow field and field manager to work properly.

    Notes
    -------
    _deg_trig and _determine_daylength are more of temporary methods that approximately estimates the day length, this
    will be revisited for a more accurate implementation post v1
    """
    incoming_light: Optional[float] = None
    """incoming light radiation energy (MJ/m)"""
    min_air_temperature: Optional[float] = None
    """minimum air temperature for the day (C)"""
    mean_air_temperature: Optional[float] = None
    """average air temperature for the day (C)"""
    max_air_temperature: Optional[float] = None
    """maximum air temperature for the day (C)"""
    daylength: Optional[float] = None
    """Length of time from sunup to sundown on the day (hours)"""
    annual_mean_air_temperature: Optional[float] = None
    """average annual air temperature for the year (C)"""
    snow_fall: float = 0.0    # TODO: make this better integrated with Soil module
    """amount of snow that falls on the day (mm)"""
    rainfall: float = 0.0
    """amount of rainfall that occurs on the day (mm)"""
    irrigation: float = 0.0
    """amount of irrigation that is applied to the field on that day (mm)"""
    precipitation: float = 0.0
    """amount of precipitation that occurs on the day (mm)"""

    def __post_init__(self):
        """Sets precipitation as snow_fall or rainfall depending on mean air temperature"""
        if self.mean_air_temperature >= 0:
            self.rainfall = self.precipitation
        else:
            self.snow_fall = self.precipitation

    @staticmethod
    def determine_daylength(month: int) -> int:
        """
        Approximate day length of the month by using data from Madison, WI
        Parameters
        ----------
        month: int
            Month of the year

        Returns
        -------
            Day length of the month (hour)

        References
        -------
        https://sunrise.maplogs.com/dane_county_wi_usa.15449.html
        """
        daylength = [9, 10, 11, 13, 14, 15, 15, 15, 13, 12, 10, 9]
        return daylength[month-1]

    @staticmethod
    def date_conversion_month(time: Time) -> int:
        """
        Converts the day number into the corresponding month of the year.

        Parameters
        ----------
        time: Time
            Time object containing the current time of the simulation.

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
    def date_conversion_day(time: Time) -> int:
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
            return time.day - leap_days[CurrentWeather.date_conversion_month(time) - 2]
        else:
            return time.day - days[CurrentWeather.date_conversion_month(time) - 2]
