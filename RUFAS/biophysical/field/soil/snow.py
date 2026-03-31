import math
from typing import Optional

from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.biophysical.field.soil.soil_data import SoilData


class Snow:
    """
    Class representing snow-related calculations and data management.

    This class provides methods for calculating snow pack temperature, snow melting, and
    updating snow-related data based on the Soil and Water Assessment Tool (SWAT) documentation.

    Attributes
    ----------
    soil_data : Optional[SoilData]
        The object that tracks all soil variables throughout the simulation.
    field_size : Optional[float]
        The field size (ha).

    Methods
    -------
    _calc_snow_temp(current_day_conditions: CurrentDayConditions) -> float:
        Calculate the snow pack temperature for the current day.

    _melt_snow(current_day_conditions: CurrentDayConditions, day: int) -> float:
        Calculate the snow melt for the current day.

    _melt_factor(day: int) -> float:
        Calculate the snow melt factor for a given day, b_mlt.

    sublimation():
        Placeholder function for sublimation calculations.

    update_snow(current_day_conditions: CurrentDayConditions, day: int) -> None:
        Update snow-related data including snow content and temperatures.
    """

    def __init__(self, soil_data: Optional[SoilData] = None, field_size: Optional[float] = None):
        """object that tracks all soil variable throughout the simulation"""
        self.soil_data = soil_data or SoilData(field_size=field_size)

    @staticmethod
    def _calc_snow_temp(soil_data: SoilData, current_day_conditions: CurrentDayConditions) -> float:
        """
        This function calculates the snow pack temperature for the current day.

        Parameters
        ----------
        soil_data : SoilData
            The object that tracks all soil variables throughout the simulation.
        current_day_conditions : CurrentDayConditions
            The current day weather data.

        Returns
        -------
        float
            The calculated snow pack temperature for the current day (Celsius).

        References
        ----------
        Equation 1:2.5.1 in SWAT 2009 Theoretical Documentation.

        """
        return (soil_data.previous_day_snow_temperature * (1 - soil_data.snow_lag_factor)) + (
            current_day_conditions.mean_air_temperature * soil_data.snow_lag_factor
        )

    @staticmethod
    def _melt_snow(soil_data: SoilData, current_day_conditions: CurrentDayConditions, day: int) -> float:
        """
        This function calculates the amount of snow melting for the current day.

        Parameters
        ----------
        soil_data : SoilData
            The object that tracks all soil variables throughout the simulation.
        current_day_conditions : CurrentDayConditions
            The current day weather data.
        day :int
            The day number of the year.

        Returns
        -------
        float
            The amount of snow melting for the current day.

        References
        ----------
        Equation 1:2.5.2 in SWAT 2009 Theoretical Documentation.

        """

        melt_factor = Snow._melt_factor(soil_data=soil_data, day=day)
        snow_coverage_fraction = soil_data.snow_coverage_fraction
        snow_temperature = soil_data.current_day_snow_temperature
        max_air_temperature = current_day_conditions.max_air_temperature
        snow_melt_base_temperature = soil_data.snow_melt_base_temperature

        snow_melt_amount = (
            melt_factor
            * snow_coverage_fraction
            * ((snow_temperature + max_air_temperature) / 2 - snow_melt_base_temperature)
        )

        if snow_melt_amount > soil_data.snow_content:
            return soil_data.snow_content
        else:
            return max(snow_melt_amount, 0.0)

    @staticmethod
    def _melt_factor(soil_data: SoilData, day: int) -> float:
        """
        This function calculates the snow melt factor for the current day.

        Parameters
        ----------
        day : int
            The day number of the year.

        Returns
        -------
        float
            The calculated snow melt factor for the current day.

        References
        ----------
        Equation 1:2.5.3 in SWAT 2009 Theoretical Documentation.

        """
        mlt6 = soil_data.snow_melt_factor_maximum
        mlt12 = soil_data.snow_melt_factor_minimum
        return (mlt6 + mlt12) / 2 + ((mlt6 - mlt12) / 2 * (math.sin(2 * math.pi / 365) * (day - 81)))

    def update_snow(self, current_day_conditions: CurrentDayConditions, day: int) -> None:
        """
        Update snow-related data for the current day.

        This function updates various snow-related data, including snow content, snow
        temperatures, and snow melting, based on the provided current day weather data
        and day of the simulation.

        Notes
        -----
        - If the current snow content is negative, a ValueError is raised.
        - If the snow content is 0.0, 'previous_day_snow_temperature' and 'current_day_snow_temperature' are set to None
          and 'snow_content' and 'snow_melt_amount' is set to 0.0.
        - Before calculating the current day snow temperature, 'previous_day_snow_temperature' is set to the value of
          'current_day_snow_temperature' from the last iteration. If 'current_day_snow_temperature' is None,
          'previous_day_snow_temperature' is set to the average air temperature of the current day.


        Parameters
        ----------
        current_day_conditions : CurrentDayConditions
            The current day weather data.
        day : int
            The day number of the year.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If the snow_content is < 0.0.

        """
        if self.soil_data.snow_content < 0.0:
            raise ValueError("Snow Content should not be a negative number.")

        self.soil_data.snow_content += current_day_conditions.snowfall

        if self.soil_data.snow_content == 0.0:
            (
                self.soil_data.previous_day_snow_temperature,
                self.soil_data.current_day_snow_temperature,
            ) = (None, None)
            self.soil_data.snow_content, self.soil_data.snow_melt_amount = 0.0, 0.0
        else:
            self.soil_data.previous_day_snow_temperature = (
                self.soil_data.current_day_snow_temperature
                if self.soil_data.current_day_snow_temperature is not None
                else current_day_conditions.mean_air_temperature
            )
            self.soil_data.current_day_snow_temperature = self._calc_snow_temp(self.soil_data, current_day_conditions)

            self.soil_data.snow_melt_amount = self._melt_snow(self.soil_data, current_day_conditions, day)
            self.soil_data.snow_content -= self.soil_data.snow_melt_amount

    def sublimate(self, maximum_sublimation: float) -> None:
        """
        Performs sublimation on the snowpack.

        Parameters
        ----------
        maximum_sublimation : float
            The maximum amount of sublimation possible on the current day (mm).

        References
        ----------
        SWAT Theoretical documentation section 2:2.3.3.1

        """
        sublimation = min(maximum_sublimation, self.soil_data.snow_content)
        self.soil_data.water_sublimated = sublimation
        self.soil_data.snow_content -= sublimation
