from typing import Optional
from math import exp, log

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData

"""
This module is based on the "Soil Temperature" section of SWAT (1:1.3.3)
"""


class SoilTemp:

    def __init__(self, soil_data: Optional[SoilData] = None):
        self.data = soil_data or SoilData()     # Initialize with defaults, if not given

    def daily_soil_temperature_update(self, solar_radiation: float, avg_temp: float, min_temp: float, max_temp: float,
                                      plant_cover: float, snow_cover: float, avg_annual_air_temp: float) -> None:
        """this is the main routine that updates the soil temperature

        Args:
            solar_radiation: solar radiation reaching the ground on the current day (MJ per square meter per day)
            avg_temp: average temperature of the current day (degrees C)
            min_temp: minimum temperature of the current day (degrees C)
            max_temp: maximum temperature of the current day (degrees C)
            plant_cover: total aboveground plant biomass and residue on the current day (kg per hectare)
            snow_cover: water content of the snow cover on the current day (mm)
            avg_annual_air_temp: average annual air temperature (degrees C)

        Notes:
            SWAT does not specify how to start the simulation i.e. it does not specify what to do on day 0, when
            there is no previous day's temperature. Currently, the implementation just uses the temperature that the
            soil starts (it sets the previous days temperature equal to the current day's temperature). This assumption
            is fairly reasonable due to temporal auto-correlation, but does not account for the random fluctuations
            that can occur throughout the year.

            Because this model now simulates the top 20 mm of the soil profile as its own layer for the purpose of
            tracking phosphorus runoff, this module first performs operations specifically on the top 2 layers of soil.
            The result is that this module treats the top two layers of soil as if they were 1, i.e. both layers are set
            to be the same temperature every day. For every day of the of simulation besides potentially the first, the
            top two layers of soil will have the same temperature.

        SWAT Reference: section 1:1.3.3
        """
        max_damping_depth = self._determine_maximum_damping_depth(self.data.profile_bulk_density)
        scaling_factor = self._determine_scaling_factor(self.data.profile_soil_water_content,
                                                        self.data.profile_bulk_density,
                                                        self.data.soil_layers[-1].bottom_depth)
        damping_depth = self._determine_damping_depth(max_damping_depth, scaling_factor)
        radiation_factor = self._determine_radiation_factor(solar_radiation, self.data.albedo)
        bare_soil_surface_temp = self._determine_bare_soil_surface_temp(radiation_factor, avg_temp, min_temp, max_temp)
        cover_factor = self._determine_cover_weighting_factor(plant_cover, snow_cover)
        if self.data.soil_layers[0].previous_day_temperature is None:
            self.data.soil_layers[0].previous_day_temperature = self.data.soil_layers[0].temperature
            self.data.soil_layers[1].previous_day_temperature = self.data.soil_layers[1].temperature
        combined_previous_top_soil_layer_temp = self._determine_weighted_average_temperature(
            self.data.soil_layers[0].previous_day_temperature, self.data.soil_layers[0].layer_thickness,
            self.data.soil_layers[1].previous_day_temperature, self.data.soil_layers[1].layer_thickness)
        actual_soil_surface_temp = self._determine_soil_surface_temp(cover_factor,
                                                                     combined_previous_top_soil_layer_temp,
                                                                     bare_soil_surface_temp)

        new_combined_previous_top_soil_temperature = self._determine_weighted_average_temperature(
            self.data.soil_layers[0].temperature, self.data.soil_layers[0].layer_thickness,
            self.data.soil_layers[1].temperature, self.data.soil_layers[1].layer_thickness
        )
        combined_top_layer_center_depth = self.data.soil_layers[1].bottom_depth / 2
        depth_factor = self._determine_depth_factor(combined_top_layer_center_depth, damping_depth)
        new_combined_top_soil_temperature = self._determine_average_soil_temperature(
            self.data.previous_temperature_effect, new_combined_previous_top_soil_temperature, depth_factor,
            avg_annual_air_temp, actual_soil_surface_temp)
        for layer in self.data.soil_layers[:2]:
            layer.previous_day_temperature = combined_previous_top_soil_layer_temp
            layer.temperature = new_combined_top_soil_temperature

        for layer in self.data.soil_layers[2:]:
            new_previous_temperature = layer.temperature
            layer_depth_factor = self._determine_depth_factor(layer.depth_of_layer_center, damping_depth)
            if layer.previous_day_temperature is None:
                layer.previous_day_temperature = layer.temperature
            layer.temperature = self._determine_average_soil_temperature(self.data.previous_temperature_effect,
                                                                         layer.previous_day_temperature,
                                                                         layer_depth_factor, avg_annual_air_temp,
                                                                         actual_soil_surface_temp)
            layer.previous_day_temperature = new_previous_temperature

    # --- Static methods ---
    @staticmethod
    def _determine_maximum_damping_depth(bulk_density: float) -> float:
        """calculates maximum damping depth of a soil profile based on bulk density

        Args:
            bulk_density: the soil profile bulk density (Mg per cubic meter)

        Returns:
            the maximum damping depth (mm)

        SWAT Reference: 1:1.3.6
        """
        top_term = 2500 * bulk_density
        bottom_term = bulk_density + (686 * exp(-5.63 * bulk_density))
        return 1000 + (top_term / bottom_term)

    @staticmethod
    def _determine_scaling_factor(soil_water_content: float, bulk_density: float, bottom_depth: float) -> float:
        """calculates the scaling factor for use in calculating the damping depth

        Args:
            soil_water_content: amount of water in soil profile expressed as depth of water in profile (mm)
            bulk_density: bulk density of the soil profile (Mg per cubic meter)
            bottom_depth: depth from the soil surface of the bottom of the soil profile (mm)

        Returns:
            the scaling factor for calculating damping depth (unitless)

        SWAT Reference: 1:1.3.7
        """
        return soil_water_content / ((0.356 - (0.144 * bulk_density)) * bottom_depth)

    @staticmethod
    def _determine_damping_depth(max_damping_depth: float, scaling_factor: float) -> float:
        """calculates the daily value for the damping depth

        Args:
            max_damping_depth: maximum_damping_depth (mm)
            scaling_factor: scaling factor for soil water (unitless)

        Returns:
            damping depth for the day (mm)

        SWAT Reference: 1:1.3.8
        """
        first_term = log(500 / max_damping_depth)
        second_term = ((1 - scaling_factor) / (1 + scaling_factor)) ** 2
        return max_damping_depth * exp(first_term * second_term)

    @staticmethod
    def _determine_depth_factor(center_depth: float, damping_depth: float) -> float:
        """calculates the depth factor for a given layer of soil

        Args:
            center_depth: depth of the center of a given soil layer (mm)
            damping_depth: damping depth of soil profile (mm)

        Returns:
            the depth factor for this layer of soil (unitless)

        SWAT Reference: 1:1.3.4, 5
        """
        # calculate ratio of center depth to damping depth (SWAT 1:1.3.5)
        ratio = center_depth / damping_depth

        return ratio / (ratio + exp(-0.867 - (2.078 * ratio)))

    @staticmethod
    def _determine_radiation_factor(solar_radiation: float, albedo: float) -> float:
        """calculates the radiation term for use in calculating the bare soil surface temp

        Args:
            solar_radiation: solar radiation reaching the ground on the current day (MJ per square meter per day)
            albedo: proportion of solar radiation that is reflected by the soil surface (unitless)

        Returns:
            the radiation factor for the day (unitless)

        SWAT Reference: 1:1.3.10
        """
        return ((solar_radiation * (1 - albedo)) - 14) / 20

    @staticmethod
    def _determine_bare_soil_surface_temp(radiation_factor: float, avg_temp: float, min_temp: float,
                                          max_temp: float) -> float:
        """calculates the temperature at the surface of bare soil.

        Args:
            radiation_factor: radiation factor for a given day (unitless)
            avg_temp: average temperature of the current day (degrees C)
            min_temp: minimum temperature of the current day (degrees C)
            max_temp: maximum temperature of the current day (degrees C)

        Returns:
            bare soil surface temperature (degrees C)

        SWAT Reference: 1:1.3.9
        """
        return avg_temp + (radiation_factor * ((max_temp - min_temp) / 2))

    @staticmethod
    def _determine_cover_weighting_factor(plant_cover: float, snow_cover: float) -> float:
        """calculates the weighting factor for use in calculating the soil surface temperature

        Args:
            plant_cover: total aboveground plant biomass and residue on the current day (kg per hectare)
            snow_cover: water content of the snow cover on the current day (mm)

        Returns:
            weighting factor based either snow or plant matter soil cover (unitless)

        SWAT Reference: 1:1.3.11
        """
        plant_factor = plant_cover / (plant_cover + exp(7.563 - ((1.297 * 10 ** (-4)) * plant_cover)))
        snow_factor = snow_cover / (snow_cover + exp(6.055 - (0.3002 * snow_cover)))
        return max(plant_factor, snow_factor)

    @staticmethod
    def _determine_weighted_average_temperature(first_layer_temp: float, first_layer_thickness: float,
                                                second_layer_temp: float, second_layer_thickness: float) -> float:
        """This method determines a weighted average temperature of two soil layers based on their thicknesses.

        Parameters
        ----------
        first_layer_temp : float
            Temperature of the first layer (degrees C)
        first_layer_thickness : float
            Thickness of the first layer (mm)
        second_layer_temp : float
            Temperature of the second layer (degrees C)
        second_layer_thickness : float
            Thickness of the second layer (mm)

        Returns
        -------
        float
            The weighted average temperature of the two soil layers passed (degrees C)

        """
        weighted_top_temp = first_layer_temp * first_layer_thickness
        weighted_bottom_temp = second_layer_temp * second_layer_thickness
        return (weighted_top_temp + weighted_bottom_temp) / (first_layer_thickness + second_layer_thickness)

    @staticmethod
    def _determine_soil_surface_temp(cover_weighting_factor: float, previous_top_soil_layer_temp: float,
                                     bare_soil_surface_temp: float) -> float:
        """calculates the soil surface temperature for a given day

        Args:
            cover_weighting_factor: weighting factor for soil cover impacts (unitless)
            previous_top_soil_layer_temp: temperature of the first layer of soil on the previous day (degrees C)
            bare_soil_surface_temp: temperature of the bare soil surface (degrees C)

        Returns:
            soil surface temperature for the current day (degrees C)

        SWAT Reference: 1:1.3.12
        """
        return cover_weighting_factor * previous_top_soil_layer_temp + \
            (1 - cover_weighting_factor) * bare_soil_surface_temp

    @staticmethod
    def _determine_average_soil_temperature(prev_temperature_effect: float, previous_day_soil_temp: float,
                                            depth_factor: float, avg_annual_air_temp: float,
                                            soil_surface_temp: float) -> float:
        """calculates daily average soil temperature at center of a given soil layer

        Args:
            prev_temperature_effect: coefficient that controls influence of previous day's temp on the current day's
                temp (unitless)
            previous_day_soil_temp: soil temperature in the layer from the previous day (degrees C)
            depth_factor: factor that quantifies the influence of depth below surface on soil temperature (unitless)
            avg_annual_air_temp: average annual air temperature (degrees C)
            soil_surface_temp: soil surface temp on the current day (degrees C)

        Returns:
            soil temperature at given depth on the current day (degrees C)

        SWAT Reference: 1:1.3.3
        """
        first_term = prev_temperature_effect * previous_day_soil_temp
        second_term = (1 - prev_temperature_effect) * (depth_factor * (avg_annual_air_temp - soil_surface_temp)
                                                       + soil_surface_temp)
        return first_term + second_term
