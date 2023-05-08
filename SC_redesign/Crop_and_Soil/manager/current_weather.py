from dataclasses import dataclass
from typing import Optional

from RUFAS.classes import Weather


# TODO: this object needs to be created from the `Weather` class.
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

    @classmethod
    def check_current_weather(cls, weather: Weather):  # NOTE: How to specify the correct return type?
        """creates a CurrentWeather object by extracting the relevant values for the current day from a Weather
        object"""
        return CurrentWeather()  # TODO: placeholder for typing, needs implementation
