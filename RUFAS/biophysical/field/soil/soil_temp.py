from math import exp, log
from typing import Optional

from RUFAS.biophysical.field.soil.soil_data import SoilData


class SoilTemp:
    """
    Manages and simulates soil temperature based on the "Soil Temperature" section (1:1.3.3) of the Soil and Water
    Assessment Tool (SWAT) documentation.

    Parameters
    ----------
    soil_data : SoilData, optional
        The SoilData object used by this module to track the temperatures within the soil profile, creates new one
        if one is not provided.
    field_size : float, optional
        Used to initialize a SoilData object for this module to work with, if a pre-configured SoilData object is
        not provided (ha).

    """

    def __init__(self, soil_data: Optional[SoilData], field_size: Optional[float] = None):
        self.data = soil_data or SoilData(field_size=field_size)

    def daily_soil_temperature_update(
        self,
        solar_radiation: float,
        avg_temp: float,
        min_temp: float,
        max_temp: float,
        plant_cover: float,
        snow_cover: float,
        avg_annual_air_temp: float,
    ) -> None:
        """
        Update the soil temperature.

        Parameters
        ----------
        solar_radiation : float
            Solar radiation reaching the ground on the current day (MJ per square meter per day).
        avg_temp : float
            Average temperature of the current day (degrees C).
        min_temp : float
            Minimum temperature of the current day (degrees C).
        max_temp : float
            Maximum temperature of the current day (degrees C).
        plant_cover : float
            Total aboveground plant biomass and residue on the current day (kg per hectare).
        snow_cover : float
            Water content of the snow cover on the current day (mm).
        avg_annual_air_temp : float
            Average annual air temperature (degrees C).

        Notes
        -----
        SWAT does not specify how to start the simulation i.e. it does not specify what to do on day 0, when
        there is no previous day's temperature. Currently, the implementation just uses the temperature that the
        soil starts (it sets the previous day's temperature equal to the current day's temperature). This assumption
        is fairly reasonable due to temporal auto-correlation, but does not account for the random fluctuations
        that can occur throughout the year.

        References
        ----------
        SWAT Theoretical documentation eqn. 1:1.3.3

        """
        max_damping_depth = self._determine_maximum_damping_depth(self.data.profile_bulk_density)
        scaling_factor = self._determine_scaling_factor(
            self.data.profile_soil_water_content,
            self.data.profile_bulk_density,
            self.data.soil_layers[-1].bottom_depth,
        )
        damping_depth = self._determine_damping_depth(max_damping_depth, scaling_factor)
        radiation_factor = self._determine_radiation_factor(solar_radiation, self.data.albedo)
        bare_soil_surface_temp = self._determine_bare_soil_surface_temp(radiation_factor, avg_temp, min_temp, max_temp)
        cover_factor = self._determine_cover_weighting_factor(plant_cover, snow_cover)
        if self.data.soil_layers[0].previous_day_temperature is None:
            self.data.soil_layers[0].previous_day_temperature = self.data.soil_layers[0].temperature
        actual_soil_surface_temp = self._determine_soil_surface_temp(
            cover_factor,
            self.data.soil_layers[0].previous_day_temperature,
            bare_soil_surface_temp,
        )

        for layer in self.data.soil_layers:
            new_previous_temperature = layer.temperature
            layer_depth_factor = self._determine_depth_factor(layer.depth_of_layer_center, damping_depth)
            if layer.previous_day_temperature is None:
                layer.previous_day_temperature = layer.temperature
            layer.temperature = self._determine_average_soil_temperature(
                self.data.previous_temperature_effect,
                layer.previous_day_temperature,
                layer_depth_factor,
                avg_annual_air_temp,
                actual_soil_surface_temp,
            )
            layer.previous_day_temperature = new_previous_temperature

    # --- Static methods ---
    @staticmethod
    def _determine_maximum_damping_depth(bulk_density: float) -> float:
        """
        Calculate the maximum damping depth of a soil profile based on bulk density.

        Parameters
        ----------
        bulk_density : float
            The soil profile bulk density (Mg per cubic meter).

        Returns
        -------
        float
            The maximum damping depth (mm).

        References
        ----------
        SWAT Theoretical documentation eqn. 1:1.3.6

        """
        top_term = 2500 * bulk_density
        bottom_term = bulk_density + (686 * exp(-5.63 * bulk_density))
        return 1000 + (top_term / bottom_term)

    @staticmethod
    def _determine_scaling_factor(soil_water_content: float, bulk_density: float, bottom_depth: float) -> float:
        """
        Calculate the scaling factor for use in calculating the damping depth.

        Parameters
        ----------
        soil_water_content : float
            Amount of water in the soil profile expressed as depth of water in profile (mm).
        bulk_density : float
            Bulk density of the soil profile (Mg per cubic meter).
        bottom_depth : float
            Depth from the soil surface of the bottom of the soil profile (mm).

        Returns
        -------
        float
            The scaling factor for calculating damping depth (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 1:1.3.7

        """
        return soil_water_content / ((0.356 - (0.144 * bulk_density)) * bottom_depth)

    @staticmethod
    def _determine_damping_depth(max_damping_depth: float, scaling_factor: float) -> float:
        """
        Calculate the daily value for the damping depth.

        Parameters
        ----------
        max_damping_depth : float
            Maximum damping depth (mm).
        scaling_factor : float
            Scaling factor for soil water (unitless).

        Returns
        -------
        float
            Damping depth for the day (mm).

        References
        ----------
        SWAT Theoretical documentation eqn. 1:1.3.8

        """
        first_term = log(500 / max_damping_depth)
        second_term = ((1 - scaling_factor) / (1 + scaling_factor)) ** 2
        return max_damping_depth * exp(first_term * second_term)

    @staticmethod
    def _determine_depth_factor(center_depth: float, damping_depth: float) -> float:
        """
        Calculate the depth factor for a given layer of soil.

        Parameters
        ----------
        center_depth : float
            Depth of the center of a given soil layer (mm).
        damping_depth : float
            Damping depth of the soil profile (mm).

        Returns
        -------
        float
            The depth factor for this layer of soil (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 1:1.3.4, 5

        """
        # calculate ratio of center depth to damping depth (SWAT 1:1.3.5)
        ratio = center_depth / damping_depth

        return ratio / (ratio + exp(-0.867 - (2.078 * ratio)))

    @staticmethod
    def _determine_radiation_factor(solar_radiation: float, albedo: float) -> float:
        """
        Calculate the radiation term for use in calculating the bare soil surface temperature.

        Parameters
        ----------
        solar_radiation : float
            Solar radiation reaching the ground on the current day (MJ per square meter per day).
        albedo : float
            Proportion of solar radiation that is reflected by the soil surface (unitless).

        Returns
        -------
        float
            The radiation factor for the day (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 1:1.3.10

        """
        return ((solar_radiation * (1 - albedo)) - 14) / 20

    @staticmethod
    def _determine_bare_soil_surface_temp(
        radiation_factor: float, avg_temp: float, min_temp: float, max_temp: float
    ) -> float:
        """
        Calculate the temperature at the surface of bare soil.

        Parameters
        ----------
        radiation_factor : float
            Radiation factor for a given day (unitless).
        avg_temp : float
            Average temperature of the current day (degrees C).
        min_temp : float
            Minimum temperature of the current day (degrees C).
        max_temp : float
            Maximum temperature of the current day (degrees C).

        Returns
        -------
        float
            Bare soil surface temperature (degrees C).

        References
        ----------
        SWAT Theoretical documentation eqn. 1:1.3.9

        """
        return avg_temp + (radiation_factor * ((max_temp - min_temp) / 2))

    @staticmethod
    def _determine_cover_weighting_factor(plant_cover: float, snow_cover: float) -> float:
        """
        Calculate the weighting factor for use in calculating the soil surface temperature.

        Parameters
        ----------
        plant_cover : float
            Total aboveground plant biomass and residue on the current day (kg per hectare).
        snow_cover : float
            Water content of the snow cover on the current day (mm).

        Returns
        -------
        float
            Weighting factor based on either snow or plant matter soil cover (unitless).

        References
        ----------
        SWAT Theoretical documentation eqn. 1:1.3.11

        """
        plant_factor = plant_cover / (plant_cover + exp(7.563 - ((1.297 * 10 ** (-4)) * plant_cover)))
        snow_factor = snow_cover / (snow_cover + exp(6.055 - (0.3002 * snow_cover)))
        return max(plant_factor, snow_factor)

    @staticmethod
    def _determine_soil_surface_temp(
        cover_weighting_factor: float,
        previous_top_soil_layer_temp: float,
        bare_soil_surface_temp: float,
    ) -> float:
        """
        Calculate the soil surface temperature for a given day.

        Parameters
        ----------
        cover_weighting_factor : float
            Weighting factor for soil cover impacts (unitless).
        previous_top_soil_layer_temp : float
            Temperature of the first layer of soil on the previous day (degrees C).
        bare_soil_surface_temp : float
            Temperature of the bare soil surface (degrees C).

        Returns
        -------
        float
            Soil surface temperature for the current day (degrees C).

        References
        ----------
        SWAT Theoretical documentation eqn. 1:1.3.12

        """
        return (
            cover_weighting_factor * previous_top_soil_layer_temp
            + (1 - cover_weighting_factor) * bare_soil_surface_temp
        )

    @staticmethod
    def _determine_average_soil_temperature(
        prev_temperature_effect: float,
        previous_day_soil_temp: float,
        depth_factor: float,
        avg_annual_air_temp: float,
        soil_surface_temp: float,
    ) -> float:
        """
        Calculate the daily average soil temperature at the center of a given soil layer.

        Parameters
        ----------
        prev_temperature_effect : float
            Coefficient that controls the influence of the previous day's temperature on the current day's temperature
            (unitless).
        previous_day_soil_temp : float
            Soil temperature in the layer from the previous day (degrees C).
        depth_factor : float
            Factor that quantifies the influence of depth below the surface on soil temperature (unitless).
        avg_annual_air_temp : float
            Average annual air temperature (degrees C).
        soil_surface_temp : float
            Soil surface temperature on the current day (degrees C).

        Returns
        -------
        float
            Soil temperature at the given depth on the current day (degrees C).

        References
        ----------
        SWAT Theoretical documentation eqn. 1:1.3.3

        """
        first_term = prev_temperature_effect * previous_day_soil_temp
        second_term = (1 - prev_temperature_effect) * (
            depth_factor * (avg_annual_air_temp - soil_surface_temp) + soil_surface_temp
        )
        return first_term + second_term
