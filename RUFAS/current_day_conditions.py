from dataclasses import dataclass
from typing import Optional


@dataclass
class CurrentDayConditions:
    """
    The purpose of this class is to combine and covert infos from weather data and field data and creates a
    current weather class that have all the needed attributes to allow field and field manager to work properly.

    Attributes
    ----------
    incoming_light: float, optional, default=None
        Incoming light radiation energy (MJ/m^2).
    min_air_temperature: float, optional, default=None
        Minimum air temperature for the day (C).
    mean_air_temperature: float, optional, default=None
        Average air temperature for the day (C).
    max_air_temperature: float, optional, default=None
        Maximum air temperature for the day (C).
    daylength: float, optional, default=None
        Length of time from sunup to sundown on the day (hours).
    annual_mean_air_temperature: float, optional, default=None
        Average annual air temperature for the year (C).
    snowfall: float, default=0.0
        Amount of snow that falls on the day (mm).
    rainfall: float, default=0.0
        Amount of rainfall that occurs on the day (mm).
    irrigation: float, default=0.0
        Amount of irrigation that is applied to the field on that day (mm).
    precipitation: float, default=0.0
        Amount of precipitation that occurs on the day (mm).

    Notes
    -------
    _deg_trig and _determine_daylength are more of temporary methods that approximately estimates the day length, this
    will be revisited for a more accurate implementation post v1

    """
    incoming_light: Optional[float] = None
    min_air_temperature: Optional[float] = None
    mean_air_temperature: Optional[float] = None
    max_air_temperature: Optional[float] = None
    daylength: Optional[float] = None
    annual_mean_air_temperature: Optional[float] = None
    snowfall: float = 0.0
    rainfall: float = 0.0
    irrigation: float = 0.0
    precipitation: float = 0.0

    def __post_init__(self):
        """Sets precipitation as snow_fall or rainfall depending on mean air temperature"""
        is_freezing = self.mean_air_temperature < 0.0
        if is_freezing:
            self.snowfall = self.precipitation
        else:
            self.rainfall = self.precipitation

    @staticmethod
    def determine_daylength(month: int) -> int:
        """
        Approximate day length of the month by using data from Madison, WI.

        Parameters
        ----------
        month: int
            Month of the year.

        Returns
        -------
        int
            Day length of the month (hour).

        References
        ----------
        https://sunrise.maplogs.com/dane_county_wi_usa.15449.html
        """
        daylength = [9, 10, 11, 13, 14, 15, 15, 15, 13, 12, 10, 9]
        return daylength[month-1]
