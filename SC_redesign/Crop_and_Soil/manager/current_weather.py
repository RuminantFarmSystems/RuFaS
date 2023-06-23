from dataclasses import dataclass
from typing import Optional
from juliandate import juliandate
import numpy


from RUFAS.classes import Weather

"""
The purpose of this class is to combine and covert infos from weather data and field data and creates a
current weather class that have all the needed attributes to allow field and field manager to work properly.

Notes
-------
_deg_trig and _determine_daylength are more of temporary methods that approximately estimates the day length, this will
be revisited for a more accurate implementation post v1
"""


@dataclass
class CurrentWeather:
    """class containing the current day's weather, used by the crop class"""  # TODO: useful for entire RUFAS model?
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
    snow_fall: float = 0    # TODO: make this better integrated with Soil module
    """amount of snow that falls on the day (mm)"""
    rainfall: float = 0
    """amount of rainfall that occurs on the day (mm)"""
    irrigation: float = 0

    @classmethod
    def check_current_weather(cls, weather: Weather, month: int) -> 'CurrentWeather':
        """creates a CurrentWeather object by extracting the relevant values for the current day from a Weather
        object"""
        cls.incoming_light = weather.radiation
        cls.min_air_temperature = weather.T_min
        cls.mean_air_temperature = weather.T_avg
        cls.max_air_temperature = weather.T_max
        cls.annual_mean_air_temperature = weather.T_avg_annual
        cls.rainfall = weather.rainfall
        cls.irrigation = weather.irrigation
        cls.daylength = CurrentWeather._determine_daylength(month=month)
        return CurrentWeather()  # TODO: placeholder for typing, needs implementation

    @staticmethod
    def _determine_daylength(month: int) -> int:
        """
        Approximate day length of the month by using data from Madison, WI
        Parameters
        ----------
        month: int
            Month of the eyar

        Returns
        -------
            day length of the month (hour)

        References
        -------
        https://sunrise.maplogs.com/dane_county_wi_usa.15449.html
        """
        daylength = [9, 10, 11, 13, 14, 15, 15, 15, 13, 12, 10, 9]
        return daylength[month-1]



