import math
from dataclasses import dataclass
from typing import Optional

from RUFAS.general_constants import GeneralConstants
from RUFAS.util import Utility


@dataclass
class CurrentDayConditions:
    """
    The purpose of this class is to combine and covert infos from weather data and field data and creates a
    current weather class that have all the needed attributes to allow field and field manager to work properly.

    Attributes
    ----------
    incoming_light: float
        Incoming light radiation energy (MJ/m^2).
    min_air_temperature: float
        Minimum air temperature for the day (C).
    mean_air_temperature: float
        Average air temperature for the day (C).
    max_air_temperature: float
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

    incoming_light: float
    min_air_temperature: float
    mean_air_temperature: float
    max_air_temperature: float
    daylength: Optional[float] = None
    annual_mean_air_temperature: Optional[float] = None
    snowfall: float = 0.0
    rainfall: float = 0.0
    irrigation: float = 0.0
    precipitation: float = 0.0

    def __post_init__(self) -> None:
        """Sets precipitation as snow_fall or rainfall depending on mean air temperature"""
        is_freezing = self.mean_air_temperature < 0.0
        if is_freezing:
            self.snowfall = self.precipitation
        else:
            self.rainfall = self.precipitation

    @staticmethod
    def determine_daylength(day_number: int, geographic_latitude: float, year: int) -> float:
        """
        Calculates the day length for the field based on its day and latitude.

        Parameters
        ----------
        day_number : int
            Calendar day number of the year.
        geographic_latitude : float
            Geographic latitude (degrees).
        year : int
            Calendar year of the current simulation.

        Returns
        -------
        float
            The length of the current day (hours).

        References
        ----------
        SWAT 1:1.1.6
        """
        geographic_latitude = math.radians(geographic_latitude)
        solar_declination_radians = CurrentDayConditions.calculate_solar_declination_radians(day_number)
        tangent_product = -math.tan(solar_declination_radians) * math.tan(geographic_latitude)
        is_polar_solstice = abs(tangent_product) > 1
        if is_polar_solstice:
            date = Utility.convert_ordinal_date_to_month_date(year, day_number)
            month = date.month
            is_summer = 6 <= month <= 9
            in_northern_hemisphere = geographic_latitude > 0
            if is_summer and in_northern_hemisphere:
                return 24
            elif not is_summer and in_northern_hemisphere:
                return 0
            elif is_summer and not in_northern_hemisphere:
                return 0
            else:
                return 24
        else:
            return (2 * math.acos(tangent_product)) / GeneralConstants.EARTH_ANGULAR_VELOCITY

    @staticmethod
    def calculate_solar_declination_radians(day_number: int) -> float:
        """
        Helper method to determine the solar declination in radians.

        Parameters
        ----------
        day_number : int
            Calendar day number of the year.

        Returns
        -------
        float
            Solar declination (radians).

        References
        ----------
        SWAT 1:1.1.2
        """
        return math.asin(0.4 * (math.sin((2 * math.pi / 365) * (day_number - 82))))
