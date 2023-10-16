from typing import Optional

from RUFAS.routines.field.soil.soil_data import SoilData
from RUFAS.routines.field.manager.current_weather import CurrentWeather

from RUFAS.output_manager import OutputManager

om = OutputManager()


class Snow:
    snow_content = 0

    def __init__(self, soil_data: Optional[SoilData] = None, field_size: Optional[float] = None):
        self.soil_data = soil_data or SoilData(field_size=field_size)
        """object that tracks all soil variable throughout the simulation"""

    def _calc_snow_temp(self, current_day_weather: CurrentWeather) -> float:
        """
        This function calculates the snow pack temperature based on equation 1:2.5.1 in SWAT 2009 Theoretical
        Documentation. According to the equation, T_snow_day_n = T_snow_day_(n-1) * (1 - l_sno) + T_av * l_sno, where
        T_snow_day_(n-1) is the snow pack temperature of the previous day, T_av is the mean air temperature on the
        current day in Celsius, and l_sno is a lagging factor the accounts for snow pack density, snow pack depth,
        exposure and other factors affecting snow pack temperature. However, the l_sno term is set to a default value of
        1.0 as described in the SWAT 2012 Input/Output: .BSN documentation. This means that mathematically, the snow
        pack temperature on the current day is the same as the current day average air temperature.
        Parameters
        ----------
        current_day_weather: CurrentWeather
            The current day weather
        """
        if self.soil_data.snow_content is not None and self.soil_data.snow_content > 0.0:
            return (self.soil_data.previous_day_snow_temperature * (1 - self.soil_data.snow_lag_factor)) + \
                   (current_day_weather.mean_air_temperature * self.soil_data.snow_lag_factor)
        else:
            return current_day_weather.mean_air_temperature

    def _melt_snow(self):
        pass

    def sublimation(self):
        pass

    def update_snow(self, current_day_weather: CurrentWeather):
        self.soil_data.snow_content += current_day_weather.snow_fall
        """Update snow content"""
        self.soil_data.previous_day_snow_temperature = self.soil_data.current_day_snow_temperature if \
            self.soil_data.snow_content > 0.0 else None
        """Update previous day snow temperature"""
        self.soil_data.current_day_snow_temperature = self._calc_snow_temp(current_day_weather)
        """Update current day snow temperature"""
        self._melt_snow()
