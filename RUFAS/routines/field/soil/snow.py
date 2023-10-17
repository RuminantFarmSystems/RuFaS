import math
from typing import Optional

from RUFAS.routines.field.soil.soil_data import SoilData
from RUFAS.routines.field.manager.current_weather import CurrentWeather

from RUFAS.output_manager import OutputManager

om = OutputManager()


class Snow:
    """
        Class representing snow-related calculations and data management.

        This class provides methods for calculating snow pack temperature, snow melting, snow coverage fraction, and
        updating snow-related data based on the Soil and Water Assessment Tool (SWAT) documentation.

        Args:
            soil_data : Optional[SoilData]
                An optional SoilData object that tracks soil variables.
            field_size : Optional[float]
                An optional field size parameter used for initializing SoilData if not provided.

        Methods:
            _calc_snow_temp(current_day_weather: CurrentWeather) -> float:
                Calculate the snow pack temperature for the current day.

            _melt_snow(current_day_weather: CurrentWeather, day: int):
                Calculate the snow melt for the current day.

            _snow_coverage_fraction():
                Calculate the snow coverage fraction, sno_cov.

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

    def _calc_snow_temp(self, current_day_weather: CurrentWeather) -> float:
        """
        Calculate the snow pack temperature for the current day.

        This function calculates the snow pack temperature based on Equation 1:2.5.1
        in SWAT 2009 Theoretical Documentation. According to the equation:

            T_snow_day_n = T_snow_day_(n-1) * (1 - l_sno) + T_av * l_sno

        Where:
        - T_snow_day_n is the snow pack temperature of the current day.
        - T_snow_day_(n-1) is the snow pack temperature of the previous day.
        - T_av is the mean air temperature on the current day in Celsius.
        - l_sno is a lagging factor that accounts for snow pack density, snow pack
          depth, exposure, and other factors affecting snow pack temperature.

        Parameters:
            current_day_weather :CurrentWeather
                The current day weather data.

        Returns:
            float: The calculated snow pack temperature for the current day in Celsius.
        """
        if self.soil_data.snow_content is not None and self.soil_data.snow_content > 0.0:
            return (self.soil_data.previous_day_snow_temperature * (1 - self.soil_data.snow_lag_factor)) + \
                   (current_day_weather.mean_air_temperature * self.soil_data.snow_lag_factor)
        else:
            return current_day_weather.mean_air_temperature

    def _melt_snow(self, current_day_weather: CurrentWeather, day: int):
        """
        Calculate snow melting for the current day.

        This function calculates the amount of snow melting for the current day based
        on Equation 1:2.5.2 in SWAT 2009 Theoretical Documentation. According to the equation:

            SNO_mlt = b_mlt * sno_cov * ((T_snow + T_mx) / 2 - T_mlt)

        Where:
        - b_mlt is the melt factor of the current day.
        - sno_cov is the snow coverage fraction
        - T_snow is the snow pack temperature of the current day.
        - T_mx is the maximum air temperature of the current day.
        - T_mlt is the base temperature above which snow melt is allowed.

        Parameters:
            current_day_weather : CurrentWeather
                The current day weather data
            day :int
                The day number of the year.

        Returns:
            float: The amount of snow melting for the current day.
        """
        melt_factor = self._melt_factor(day=day)
        snow_coverage_fraction = self._snow_coverage_fraction()
        snow_temperature = self.soil_data.current_day_snow_temperature
        max_air_temperature = current_day_weather.max_air_temperature
        snow_melt_base_temperature = self.soil_data.snow_melt_base_temperature

        return melt_factor * snow_coverage_fraction * ((snow_temperature + max_air_temperature) / 2 -
                                                       snow_melt_base_temperature)

    def _snow_coverage_fraction(self):
        """
        Calculate the snow coverage fraction for the current day.

        This function calculates the snow coverage fraction based on Equation 1:2.4.2
        in SWAT 2009 Theoretical Documentation.  According to the equation:

        The snow coverage fraction represents the fraction of the ground covered by snow
        and is influenced by various factors, including snow content (sno), snow coverage
        at 50% (sno50), and maximum snow coverage (sno100). The function solves for
        'cov1' and 'cov2' in terms of sno50 and uses these values to calculate the
        snow coverage fraction.

        Returns:
            float: The snow coverage fraction for the current day.
        """
        sno = self.soil_data.snow_content
        sno50 = self.soil_data.snow_50_coverage
        sno100 = self.soil_data.snow_coverage_maximum

        # solving for cov1 and cov2 in terms of sno50
        cov2 = (math.log((10 * 1 - sno50), math.e)) / 0.45
        cov1 = math.log(0.05, math.e) + (0.95 * math.log(cov2, math.e))

        sno_ratio = sno / sno100

        return sno_ratio * (sno_ratio + math.exp(cov1 - cov2 * sno_ratio)) ** -1

    def _melt_factor(self, day: int) -> float:
        """
        Calculate the snow melt factor for the current day.

        This function calculates the snow melt factor based on Equation 1:2.5.3 in SWAT
        2009 Theoretical Documentation. According to the equation:

        The snow melt factor represents the rate at which snow melts and is influenced by
        factors such as the day of the year (day), maximum snow melt factor (mlt6), and
        minimum snow melt factor (mlt12). The function computes the snow melt factor
        based on these factors and a sinusoidal function.

        Parameters:
            day (int): The day number of the year.

        Returns:
            float: The calculated snow melt factor for the current day.
        """
        mlt6 = self.soil_data.snow_melt_factor_maximum
        mlt12 = self.soil_data.snow_melt_factor_minimum
        return (mlt6 + mlt12) / 2 + ((mlt6 - mlt12) / 2 * (math.sin(2 * math.pi / 365) * (day - 81)))

    def sublimation(self):
        pass

    def update_snow(self, current_day_weather: CurrentWeather, day: int) -> None:
        self.soil_data.snow_content += current_day_weather.snow_fall
        """Update snow content"""
        self.soil_data.previous_day_snow_temperature = self.soil_data.current_day_snow_temperature if \
            self.soil_data.snow_content > 0.0 else None
        """Update previous day snow temperature"""
        self.soil_data.current_day_snow_temperature = self._calc_snow_temp(current_day_weather)
        """Update current day snow temperature"""
        self.soil_data.snow_content -= self._melt_snow(current_day_weather, day)
        """Update snow content with melted snow"""
