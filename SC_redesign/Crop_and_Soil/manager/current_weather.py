from dataclasses import dataclass
from typing import Optional

from RUFAS.classes import Weather


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

    @classmethod
    def check_current_weather(cls, weather: Weather):  # NOTE: How to specify the correct return type?
        """creates a CurrentWeather object by extracting the relevant values for the current day from a Weather
        object"""
        return CurrentWeather()  # TODO: placeholder for typing, needs implementation
