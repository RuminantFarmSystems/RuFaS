# """
# RUFAS: Ruminant Farm Systems Model
#
# File name: soil_temp.py
#
# Author(s): William Donovan, wmdonovan@wisc.edu
#
# Description: This module contains the necessary functions for calculating and
#              updating the soil temperature on a given day. Currently the only
#              function meant to be used outside of this file is the update_all()
#              function. The other functions are meant to serve as helper
#              functions within this file.
#
# Soil attribute definitions
#
#     T_soil = soil temperature (ºC) at depth z (mm)
#
#     L = lag coefficient, set to 0.8
#
#     T_soil_prev_day = soil temperature (ºC) at depth z (mm) on the previous day
#
#     df = depth factor
#
#     T_a_air = average annual air temperature (ºC)
#
#     T_surf = Daily soil surface temperature (ºC)
#
#     zd = ratio of depth at the center of soil layer to damping depth
#
#     dd = damping depth (mm)
#
#     z = depth at the center of the soil layer
#
#     dd_max = maximum damping depth (mm)
#
#     scale = scaling factor for soil water
#
#     bd = soil bulk density (g/cm^3)
#
#     SW = total soil water in the profile (mm)
#
#     Z_tot = total soil profile depth
#
#     T_bare = Temperature of bare soil surface (ºC)
#
#     T_av = Average daily temperature (ºC)
#
#     radiate = radiation term
#
#     H_day = daily solar radiation (MJ/m^2)
#
#     albedo = daily albedo
#
#     albedo_soil = soil albedo constant
#
#     cover = soil cover index
#
#     CV = above ground biomass and residue (kg/ha)
#
#     bcv = weighting factor of ground cover
#
#     snow = snow water content on the current day (mm)
# """
#
# from math import exp, log
#
#
# def update_all(soil, crop, weather, time):
#     """
#     Description:
#         This function updates all soil temperature information.
#
#     Args:
#         soil: instance of the Soil class specified in soil.py
#         crop: instance of the Crop class specified in crop.py
#         weather: instance of the Weather class specified in classes.py
#         time: instance of the Time class specified in classes.py
#     """
#     for crop_types in crop.current_crop.values():
#         calc_T_surf(soil, crop_types, weather, time)
#
#     calc_T_soil(soil, weather, time)
#
#
# def calc_T_soil(soil, weather, time):
#     """
#     Description:
#         Calculates the soil temperature for each layer given average annual air
#         temperature. "pseudocode_soil" S.1.A.1-3
#
#     Args:
#         soil: an instance of the Soil class
#         weather: an instance of the Weather class
#         time: an instance of the Time class
#     """
#
#     L = 0.8
#     T_a_air = weather.T_avg_annual[time.year - 1]
#     dd = calc_dd(soil)
#
#     for x in range(len(soil.soil_layers)):
#
#         if x == 0:
#             z = soil.soil_layers[x].bottom_depth / 2
#         else:
#             z = (soil.soil_layers[x].bottom_depth +
#                  soil.soil_layers[x - 1].bottom_depth) / 2
#
#         # soil temperature (C) at depth z (mm) on previous day
#         T_soil_prev_day = soil.soil_layers[x].temperature
#
#         # "pseudocode_soil" S.1.A.3
#         zd = z / dd
#
#         # "pseudocode_soil" S.1.A.2
#         df_exp = exp(-0.867 - 2.078 * zd)
#         df = zd / (zd + df_exp)
#
#         # "pseudocode_soil" S.1.A.1
#         T_soil = (L * T_soil_prev_day) + (1 - L) * \
#                  (df * (T_a_air - soil.T_surf) + soil.T_surf)
#         soil.soil_layers[x].temperature = T_soil
#
#
# def calc_dd(soil):
#     """
#     Description:
#         Calculates damping depth of a given soil profile as a function of soil
#         water and dd_max.
#         "pseudocode_soil" S.1.A.4
#
#     Args:
#         soil: an instance of the Soil class
#
#     Returns:
#         int: dd, damping depth of the profile (mm)
#     """
#
#     scale = calc_scale(soil)
#     dd_max = calc_dd_max(soil)
#
#     part_1 = log(500 / dd_max)
#     part_2 = ((1 - scale) / (1 + scale)) ** 2
#     exp_part = exp(part_1 * part_2)
#
#     return dd_max * exp_part
#
#
# def calc_scale(soil):
#     """
#     Description:
#          Calculates the scaling factor for soil water in a given soil profile.
#         "pseudocode_soil" S.1.A.5
#
#     Args:
#         soil: an instance of the Soil class
#
#     Returns:
#         int: soil water scaling factor for the profile
#     """
#
#     SW = sum_soil_water(soil)
#     Z_tot = soil.profile_depth
#     bd = soil.profile_bulk_density
#
#     return SW / ((0.356 - 0.144 * bd) * Z_tot)
#
#
# def calc_dd_max(soil):
#     """
#     Description:
#         Calculates maximum damping depth for a given soil profile.
#         "pseudocode_soil" S.1.A.6
#
#     Args:
#         soil: an instance of the Soil class
#
#     Returns:
#         int: dd_max, the maximum damping depth fro the profile (mm)
#     """
#
#     bd = soil.profile_bulk_density
#     exp_part = exp(-5.63 * bd)
#     return 1000 + (2500 * bd) / (bd + 686 * exp_part)
#
#
# def sum_soil_water(soil):
#     """
#     Description:
#        Helper method to calculates the sum of soil water in the profile.
#
#     Args:
#         soil: an instance of the Soil claass
#
#     Returns:
#         int: total_soil_water (mm)
#     """
#
#     total_soil_water = 0.0
#
#     for layer in soil.soil_layers:
#         total_soil_water += layer.soil_water
#
#     return total_soil_water
#
#
# def calc_T_surf(soil, crop_type, weather, time):
#     """
#     Description:
#         Calculates the surface temperature as a function of the previous day's
#         temperature, the amount of ground cover, and the temperature of a bare
#         soil surface.
#         "pseudocode_soil" S.1.A.13
#
#     Args:
#         soil: an instance of the Soil class
#         crop: an instance of the Crop class
#         weather: an instance of the Weather class
#         time: an instance of the Time class
#     """
#
#     T_bare = calc_T_bare(soil, crop_type, weather, time)
#     bcv = calc_bcv(crop_type, time)
#
#     soil.T_surf = (bcv * soil.soil_layers[0].temperature) + ((1 - bcv) * T_bare)
#
#
# def calc_T_bare(soil, crop_type, weather, time):
#     """
#     Description:
#         Calculates the temperature of a bare soil.
#         "pseudocode_soil" S.1.A.7
#
#     Args:
#         soil: an instance of the Soil class
#         crop: an instance of the Crop class
#         weather: an instance of the Weather class
#         time: an instance of the Time class
#
#     Returns:
#         int: T_bare, the theoretical temperature of the bare soil (ºC)
#     """
#     T_av = weather.T_avg[time.year - 1][time.day - 1]
#     radiate = calc_radiate(soil, crop_type, weather, time)
#
#     return T_av + radiate * T_av
#
#
# def calc_radiate(soil, crop_type, weather, time):
#     """
#     Description:
#         Calculates the radiation term for the temperature of bare soil.
#         "pseudocode_soil" S.1.A.8
#
#     Args:
#         soil: an instance of the Soil class
#         crop: an instance of the Crop class
#         weather: an instance of the Weather class
#         time: an instance of the Time class
#
#     Returns:
#         int: radiate, the radiation term for the temperature of bare soil
#     """
#
#     H_day = weather.radiation[time.year - 1][time.day - 1]
#     albedo = calc_albedo(soil, crop_type)
#
#     return (H_day * (1 - albedo) - 14) / 20
#
#
# def calc_albedo(soil, crop_type):
#     """
#     Description:
#         Calculates the daily albedo as a function of soil type, plant cover,
#         and snow cover.
#         "pseudocode_soil" S.1.A.9/10
#
#     Args:
#         soil: an instance of the Soil class
#         crop: an instance of the Crop class
#
#     Returns:
#         int: soil albedo
#     """
#
#     CV = crop_type.bio_AG
#
#     # "pseudocode_soil" S.1.A.10
#     cover = exp(-0.00005 * CV)
#
#     # "pseudocode_soil" S.1.A.9
#     return 0.23 * (1 - cover) + soil.soil_albedo * cover
#
#
# def calc_bcv(crop_type, time):
#     """
#     Description:
#         Calculates the weighting factor for ground cover
#         "pseudocode_soil" S.1.A.11/12
#
#     Args:
#         crop: an instance of the Crop class
#         time: an instance of the Time class
#
#     Returns:
#         int: bcv, the bio-cover weighting factor for ground cover
#     """
#
#     CV = crop_type.bio_AG
#     exp_part = exp(7.563 - 0.0001297 * (-CV))
#
#     bcv = CV / (CV + exp_part)
#
#     snow = 0
#     # TODO: arbitrary snow flag - GitHub Issue #164
#     if time.day > 335 or time.day < 59:
#         albedo_snow = 0.8
#         snow = 10 * albedo_snow
#
#     bcv_snow = (snow / (snow + exp(6.055 - 0.3002 * snow)))
#
#     return max(bcv, bcv_snow)
from typing import Optional
from math import exp, log

from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData

"""
This module is based on the "Soil Temperature" section of SWAT (1:1.3.3)
"""
class SoilTemp:

    def __init__(self, soil_data: Optional[SoilData] = None):
        self.data = soil_data or SoilData()

    def daily_soil_temperature_update(self, solar_radiation: float, avg_temp: float, min_temp: float, max_temp: float,
                                      plant_cover: float, snow_cover: float, avg_annual_air_temp: float) -> None:
        """this is the main routine that updates the soil temperature

        Args:
            solar_radiation: solar radiation reaching the ground on a given day (MJ per square meter per day)
            avg_temp: average temperature of a given day (degrees C)
            min_temp: minimum temperature of a given day (degrees C)
            max_temp: maximum temperature of a given day (degrees C)
            plant_cover: total aboveground plant biomass and residue on a given day (kg per hectare)
            snow_cover: water content of the snow cover on a given day (mm)
            avg_annual_air_temp: average annual air temperature (degrees C)

        Important: SWAT does not specify how to start the simulation i.e. it does not specify what to do on day 0, when
            there is no previous day's temperature. Currently, the implementation just uses the temperature that the
            soil starts (it sets the previous days temperature equal to the current day's temperature)

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
        if self.data.soil_layers[0].previous_day_temperature is not None:
            actual_soil_surface_temp = self._determine_soil_surface_temp(cover_factor,
                                                                         self.data.soil_layers[0].previous_day_temperature,
                                                                         bare_soil_surface_temp)
        else:
            actual_soil_surface_temp = self._determine_soil_surface_temp(cover_factor,
                                                                         self.data.soil_layers[0].temperature,
                                                                         bare_soil_surface_temp)
        for layer in self.data.soil_layers:
            new_previous_temperature = layer.temperature
            layer_depth_factor = self._determine_depth_factor(layer.depth_of_layer_center, damping_depth)
            if layer.previous_day_temperature is not None:
                layer.temperature = self._determine_average_soil_temperature(self.data.lag_coefficient,
                                                                             layer.previous_day_temperature,
                                                                             layer_depth_factor,
                                                                             avg_annual_air_temp,
                                                                             actual_soil_surface_temp)
            else:
                layer.temperature = self._determine_average_soil_temperature(self.data.lag_coefficient,
                                                                             layer.temperature,
                                                                             layer_depth_factor,
                                                                             avg_annual_air_temp,
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

        SWAT Reference: 1:1.3.7
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
            solar_radiation: solar radiation reaching the ground on a given day (MJ per square meter per day)
            albedo: the albedo of the soil (Google says "ratio of reflected to incident solar radiation") (unitless?)

        Returns:
            the radiation factor for the day (unitless)

        SWAT Reference: 1:1.3.10
        """
        return ((solar_radiation * (1 - albedo)) - 14) / 20

    @staticmethod
    def _determine_bare_soil_surface_temp(radiation_factor: float, avg_temp: float, min_temp: float,
                                          max_temp: float) -> float:
        """calculates the temperature of the soil surface if it were bare

        Args:
            radiation_factor: radiation factor for a given day (unitless)
            avg_temp: average temperature of a given day (degrees C)
            min_temp: minimum temperature of a given day (degrees C)
            max_temp: maximum temperature of a given day (degrees C)

        Returns:
            the temperature of the surface soil if it were bare (degrees C)

        SWAT Reference: 1:1.3.9
        """
        return avg_temp + (radiation_factor * ((max_temp - min_temp) / 2))

    @staticmethod
    def _determine_cover_weighting_factor(plant_cover: float, snow_cover: float) -> float:
        """calculates the weighting factor for use in calculating the soil surface temperature

        Args:
            plant_cover: total aboveground plant biomass and residue on a given day (kg per hectare)
            snow_cover: water content of the snow cover on a given day (mm)

        Returns:
            weighting factor based either snow or plant matter soil cover (unitless)

        SWAT Reference: 1:1.3.11
        """
        plant_factor = plant_cover / (plant_cover + exp(7.563 - ((1.297 * 10 ** (-4)) * plant_cover)))
        snow_factor = snow_cover / (snow_cover + exp(6.055 - (0.3002 * snow_cover)))
        return max(plant_factor, snow_factor)

    @staticmethod
    def _determine_soil_surface_temp(cover_weighting_factor: float, previous_top_soil_layer_temp: float,
                                     bare_soil_surface_temp: float) -> float:
        """calculates the soil surface temperature for a given day

        Args:
            cover_weighting_factor: weighting factor for soil cover impacts (unitless)
            previous_top_soil_layer_temp: temperature of the first layer of soil on the previous day (degrees C)
            bare_soil_surface_temp: temperature of the bare soil surface (degrees C)

        Returns:
            soil surface temperature for a given day (degrees C)

        SWAT Reference: 1:1.3.12
        """
        return cover_weighting_factor * previous_top_soil_layer_temp + \
            (1 - cover_weighting_factor) * bare_soil_surface_temp

    @staticmethod
    def _determine_average_soil_temperature(lag_coefficient: float, previous_day_soil_temp: float, depth_factor: float,
                                            avg_annual_air_temp: float, soil_surface_temp: float) -> float:
        """calculates daily average soil temperature at center of a given soil layer

        Args:
            lag_coefficient: coefficient that controls influence of previous day's temp on current day's temp (degrees C)
            previous_day_soil_temp: soil temperature in the layer from the previous day (degrees C)
            depth_factor: factor that quantifies the influence of depth below surface on soil temp (unitless)
            avg_annual_air_temp: average annual air temperature (degrees C)
            soil_surface_temp: soil surface temp on current day (degrees C)

        Returns:
            soil temperature at given depth on given day (degrees C)

        SWAT Reference: 1:1.3.3
        """
        first_term = lag_coefficient * previous_day_soil_temp
        second_term = (1 - lag_coefficient) * (depth_factor * (avg_annual_air_temp - soil_surface_temp)
                                               + soil_surface_temp)
        return first_term + second_term
