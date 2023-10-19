import math
from typing import Optional

from RUFAS.routines.field.soil.soil_data import SoilData
from RUFAS.routines.field.manager.current_weather import CurrentWeather


class Snow:
    """
    Class representing snow-related calculations and data management.

    This class provides methods for calculating snow pack temperature, snow melting, and
    updating snow-related data based on the Soil and Water Assessment Tool (SWAT) documentation.

    Methods
    -------
    _calc_snow_temp(current_day_weather: CurrentWeather) -> float:
        Calculate the snow pack temperature for the current day.

    _melt_snow(current_day_weather: CurrentWeather, day: int):
        Calculate the snow melt for the current day.

    _melt_factor(day: int) -> float:
        Calculate the snow melt factor for a given day, b_mlt.

    sublimation():
        Placeholder function for sublimation calculations.

    update_snow(current_day_weather: CurrentWeather, day: int) -> None:
        Update snow-related data including snow content and temperatures.
    """

    def __init__(self, soil_data: Optional[SoilData] = None, field_size: Optional[float] = None):
        self.soil_data = soil_data or SoilData(field_size=field_size)
        """object that tracks all soil variable throughout the simulation"""

    @staticmethod
    def _calc_snow_temp(soil_data: SoilData, current_day_weather: CurrentWeather) -> float | None:
        """
        Calculate the snow pack temperature for the current day.

        Parameters
        ----------
        current_day_weather :CurrentWeather
            The current day weather data.

        Returns
        -------
        float
            The calculated snow pack temperature for the current day in Celsius.
            
        References
        ----------
        SWAT Theoretical Documentation eqn. 1:2.5.1
        
        """
        return (soil_data.previous_day_snow_temperature * (1 - soil_data.snow_lag_factor)) + \
               (current_day_weather.mean_air_temperature * soil_data.snow_lag_factor)

    @staticmethod
    def _melt_snow(soil_data: SoilData, current_day_weather: CurrentWeather, day: int):
        """
        Calculate snow melting for the current day.

        This function calculates the amount of snow melting for the current day based
        on Equation 1:2.5.2 in SWAT 2009 Theoretical Documentation. According to the equation:

            SNO_mlt = b_mlt * sno_cov * ((T_snow + T_mx) / 2 - T_mlt)

        Where:
        - b_mlt is the melt factor of the current day.
        - sno_cov is the snow coverage fraction. It can be assumed that it is equal to 1.0 whenever there is snow on the
          ground.
        - T_snow is the snow pack temperature of the current day.
        - T_mx is the maximum air temperature of the current day.
        - T_mlt is the base temperature above which snow melt is allowed.

        Parameters
        ----------
        current_day_weather : CurrentWeather
            The current day weather data
        day :int
            The day number of the year.

        Returns
        -------
        float
            The amount of snow melting for the current day.
        """
        melt_factor = Snow._melt_factor(soil_data=soil_data, day=day)
        snow_coverage_fraction = soil_data.snow_coverage_fraction
        snow_temperature = soil_data.current_day_snow_temperature
        max_air_temperature = current_day_weather.max_air_temperature
        snow_melt_base_temperature = soil_data.snow_melt_base_temperature

        return melt_factor * snow_coverage_fraction * ((snow_temperature + max_air_temperature) / 2 -
                                                       snow_melt_base_temperature)

    @staticmethod
    def _melt_factor(soil_data: SoilData, day: int) -> float:
        """
        Calculate the snow melt factor for the current day.

        This function calculates the snow melt factor based on Equation 1:2.5.3 in SWAT
        2009 Theoretical Documentation. According to the equation:

            b_mlt = (b_mlt6 + b_mlt12) / 2 + (b_mlt6 - b_mlt12) / 2 * sin((2*pi/365) * (d_n - 81))

        Where:
        - b_mlt6 is the melt factor for June 21 (mm H2O/°C-day)
        - b_mlt12 is the melt factor for December 21 (mm H2O/°C-day)
        - d_n is the day number of the year

        Parameters
        ----------
        day : int
            The day number of the year.

        Returns
        -------
        float
            The calculated snow melt factor for the current day.
        """
        mlt6 = soil_data.snow_melt_factor_maximum
        mlt12 = soil_data.snow_melt_factor_minimum
        return (mlt6 + mlt12) / 2 + ((mlt6 - mlt12) / 2 * (math.sin(2 * math.pi / 365) * (day - 81)))

    def sublimation(self):
        pass

    def update_snow(self, current_day_weather: CurrentWeather, day: int) -> None:
        """
        Update snow-related data for the current day.

        This function updates various snow-related data, including snow content, snow
        temperatures, and snow melting, based on the provided current day weather data
        and day of the simulation.

        MAKE A NOTE ABOUT SOIL TEMP

        Parameters
        ----------
        current_day_weather : CurrentWeather
            The current day weather data.
        day : int
            The day number of the year.

        Returns
        -------
        None
        """
        self.soil_data.snow_content += current_day_weather.snow_fall
        """Update snow content with precipitation"""
        if self.soil_data.snow_content <= 0.0:
            self.soil_data.current_day_snow_temperature, self.soil_data.previous_day_snow_temperature = None, None
            self.soil_data.snow_content, self.soil_data.snow_melt_amount = 0.0, 0.0
        else:
            self.soil_data.previous_day_snow_temperature = self.soil_data.current_day_snow_temperature if \
                self.soil_data.current_day_snow_temperature is not None else current_day_weather.mean_air_temperature
            """Update previous day snow temperature"""
            self.soil_data.current_day_snow_temperature = self._calc_snow_temp(self.soil_data, current_day_weather)
            """Update current day snow temperature"""
            self.soil_data.snow_melt_amount = self._melt_snow(self.soil_data, current_day_weather, day)
            self.soil_data.snow_content -= self.soil_data.snow_melt_amount
            """Update snow content with melted snow"""
