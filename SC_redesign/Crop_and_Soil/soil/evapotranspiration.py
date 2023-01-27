"""
RUFAS: Ruminant Farm Systems Model

File name: evapotranspiration.py

Author(s): William Donovan, wmdonovan@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating water evapotranspiration on a given day by calculating:
                1. Potential evapotranspiration
                2. Crop transpiration
                3. Sublimation and Soil Evaporation.
                4. Soil Evaporation by soil layer
             Currently the only function meant to be used outside of this file
             is the update_all() function. The other functions are meant to
             serve as helper functions within this file.

Soil attribute definitions

    LHV = latent heat of vaporization (MJ kg^-1)

    ET_max = potential evapotranspiration a.k.a PET (mm d^-1)

    H0 = extraterrestrial radiation (mm m^-2d^-1)

    T_max = maximum air temperature for a given day (ºC)

    T_min = minimum air temperature for a given day (ºC)

    T_avg = mean air temperature for a given day (ºC)

    trans_max = maximum transpiration on a given day (mm H2O)

    LAI = Leaf Area Index (calculated in Crop Routine)

    evap = maximum soil evaporation/sublimation on a given day (mm H2O)

    soil_cov = soil cover index

    bio_mass = above ground biomass and residue (kg/ha)

    evap_z = evaporation demand at depth z (mm H2O)

    z = depth below soil surface (mm)

    SW = soil water content of entire profile, excluding water held at wilting
            point (mm H2O)

    WP = soil water content held at wilting point (mm H2O)

    FC = field capacity (mm H2O)
"""

from math import exp
from typing import Optional
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData


class Evapotranspiration:
    def __init__(self, soil_data: Optional[SoilData] = None):
        self.data = soil_data or SoilData()  # initialize with defaults, if not given

    def update_all(soil, crop, weather, time):
        """
        Description:
            This function calls all the necessary functions to update information related
            to evapotranspiration
        Args:
            soil: instance of the Soil class specified in soil.py
            crop: instance of the Crop class specified in crop.py
            weather: instance of the Weather class specified in classes.py
            time: instance of the Time class specified in classes.py
        """
        for crop_types in crop.current_crop.values():
            calc_potential_evap(soil, weather, time)

            calc_crop_transpiration(soil, crop_types)

            calc_soil_evap(soil, crop_types)

            update_evap_z(soil)

    # def calc_potential_evap(soil, weather, time):
    #     """
    #     Description:
    #         Calculates potential evapotranspiration ET_max using the Hargreaves method
    #         "pseudocode_soil" S.2.B.1
    #     Args:
    #         soil: instance of Soil class
    #         weather: instance of Weather class
    #         time: instance of Time class
    #     """
    #
    #     H0 = weather.radiation[time.year - 1][time.day - 1]
    #
    #     T_max = weather.T_max[time.year - 1][time.day - 1]
    #     T_min = weather.T_min[time.year - 1][time.day - 1]
    #     T_avg = weather.T_avg[time.year - 1][time.day - 1]
    #
    #     LHV = calc_LHV(T_avg)
    #
    #     ET_max = (0.0023 * H0 * ((T_max - T_min) ** 0.5) * (T_avg + 17.8)) / LHV
    #
    #     soil.ET_max = max(0.001, ET_max)
    @staticmethod
    def _determine_potential_evapotranspiration(extra_terrestrial_radiation: float, max_air_temp: float,
                                                min_air_temp: float,
                                                avg_air_temp: float) -> float:
        """calculates the potential evapotranspiration for a given day

        Args:
            extra_terrestrial_radiation: radiation from the aliens, in MJ m^(-2) d^(-1) @TODO: better description
            max_air_temp: maximum air temperature in degrees C
            min_air_temp: minimum air temperature in degrees C
            avg_air_temp: average air temperature in degrees C

        Returns:
            potential evapotranspiration in mm d^(-1)

        SWAT Reference: 2:2.2.24
        """
        if avg_air_temp is None:
            calculated_avg_air_temp = (max_air_temp + min_air_temp) / 2
            latent_heat_vaporization = Evapotranspiration._determine_latent_heat_vaporization(calculated_avg_air_temp)
            return (0.0023 * extra_terrestrial_radiation * ((max_air_temp - min_air_temp) ** (-0.5))
                    * (calculated_avg_air_temp + 17.8)) / latent_heat_vaporization
        else:
            latent_heat_vaporization = Evapotranspiration._determine_latent_heat_vaporization(avg_air_temp)
            return (0.0023 * extra_terrestrial_radiation * ((max_air_temp - min_air_temp) ** (-0.5))
                    * (avg_air_temp + 17.8)) / latent_heat_vaporization

    # def calc_LHV(T_avg):
    #     """
    #     Description:
    #         Calculates LHV (latent heat of vaporization (MJ kg^-1)) for use in
    #         determining potential evapotranspiration
    #         "pseudocode_soil" S.2.B.2
    #
    #     Args:
    #         T_avg: the average temperature on the current day
    #
    #     Returns:
    #         int: LHV, the latent heat of vaporization (MJ kg^-1)
    #     """
    #
    #     return 2.501 - (2.361 * (10 ** (-3)) * T_avg)

    @staticmethod
    def _determine_latent_heat_vaporization(avg_air_temp: float) -> float:
        """determine latent heat of vaporization for a given day

        Args:
            avg_air_temp: average air temperature in degrees C

        Returns:
            latent heat of vaporization in MJ kg^(-1)

        SWAT Reference: 1:2.3.6
        """
        return 2.501 - ((2.361 * (10 ** (-3))) * avg_air_temp)

    # @TODO: this should be in the crop module, not soil
    # def calc_crop_transpiration(soil, crop_type):
    #     """
    #     Description:
    #         Calculates crop transpiration as a function of maximum transpiration on a
    #         given day and Leaf Area Index (calculated in the Crop Routine file
    #         leaf_area_index.py)
    #         "pseudocode_soil" S.2.B.3
    #
    #     Args:
    #         soil: instance of Soil class
    #         crop: instance of Crop type class
    #     """
    #
    #     LAI = crop_type.LAI_actual
    #     # print(LAI)
    #     if 0 <= LAI <= 3.0:
    #         soil.trans_max = 0
    #         soil.trans_max = (soil.ET_max * LAI) / 3.0
    #     else:
    #         soil.trans_max = soil.ET_max

    # def calc_soil_evap(soil, crop_type):
    #     """
    #     Description:
    #         Calculates sublimation and soil evaporation
    #         "pseudocode_soil" S.2.B.4/6
    #
    #     Args:
    #         soil: instance of Soil class
    #         crop: instance of Crop type class
    #     """
    #
    #     soil_cov = calc_soil_cov(soil, crop_type)
    #
    #     # "pseudocode_soil" S.2.B.4
    #     evap_max = soil.ET_max * soil_cov
    #
    #     # "pseudocode_soil" S.2.B.6
    #     soil.evap_max = min(evap_max, ((evap_max * soil.ET_max) / (evap_max + soil.trans_max)))

    @staticmethod
    def _determine_soil_evaporation(above_ground_biomass: float, residue: float, snow_water_content: float,
                                    potential_evapotranspiration_adjusted: float, transpiration: float) -> float:
        """
        Calculate the maximum soil evaporation for this day

        Args:
            above_ground_biomass: mass of plant above ground in kg per hectare
            residue: biomass separated from plant on the ground in kg per hectare
            snow_water_content: amount of water from snow in mm
            potential_evapotranspiration_adjusted: potential evapotranspiration adjusted for evaporation of free water
                in canopy in mm
            transpiration: transpiration in mm for a given day
        Returns:
            maximum soil evaporation in the day

        SWAT Reference: 2:2.3.7, 9
        """
        soil_cover_index = Evapotranspiration._determine_soil_cover_index(above_ground_biomass, residue,
                                                                          snow_water_content)
        max_soil_evaporation = potential_evapotranspiration_adjusted * soil_cover_index  # 2:2.3.7
        actual_max_soil_evaporation = min(max_soil_evaporation,  # 2:2.3.9
                                          ((max_soil_evaporation * potential_evapotranspiration_adjusted) /
                                           (max_soil_evaporation + transpiration))
                                          )
        return actual_max_soil_evaporation

    # @TODO: function that calculates potential_evapotranspiration_adjusted (maybe)

    # def calc_soil_cov(soil, crop_type):
    #     """
    #     Description:
    #         Calculates soil cover for use in calculating soil evaporation
    #         "pseudocode_soil" S.2.B.5
    #
    #     Args:
    #         soil: instance of Soil class
    #         crop: instance of Crop type class
    #     """
    #
    #     bio_AG = crop_type.bio_AG
    #     residue = soil.residue
    #     bio_mass = bio_AG + residue
    #
    #     return exp(-5.0 * (10 ** -5) * bio_mass)

    @staticmethod
    def _determine_soil_cover_index(above_ground_biomass: float, residue: float, snow_water_content: float) -> float:
        """
        Calculate soil cover index

        Args:
            above_ground_biomass: mass of plant above ground in kg per hectare
            residue: biomass separated from plant on the ground in kg per hectare
            snow_water_content: amount of water from snow in mm

        Returns:
            soil cover index (unitless)

        SWAT Reference: 2:2.3.8
        """
        if snow_water_content > 0.5:
            return 0.5
        else:
            return exp((-5.0 * (10 ** (-5))) * (above_ground_biomass + residue))

    # def update_evap_z(soil):
    #     """
    #     Description:
    #         Calculates the evap for each layer of soil in a given profile as a function
    #         of the evaporation demand between the soil layers above and below.
    #         "pseudocode_soil" S.2.B.7-10
    #
    #     Args:
    #         soil: instance of Soil class
    #     """
    #
    #     for x in range(len(soil.soil_layers)):
    #         curr_layer = soil.soil_layers[x]
    #
    #         FC = curr_layer.fc_water
    #         SW = curr_layer.soil_water
    #         WP = curr_layer.wilting_water
    #
    #         # Calculate evap at a given depth
    #         # "pseudocode_soil" S.2.B.7
    #         if x == 0:
    #             curr_layer.top_evap = 0
    #             z = curr_layer.bottom_depth
    #             exp_part = exp(2.374 - 0.00713 * z)
    #
    #             curr_layer.bottom_evap = soil.evap_max * (z / (z + exp_part))
    #
    #         else:
    #             curr_layer.top_evap = soil.soil_layers[x - 1].bottom_evap
    #             z = curr_layer.bottom_depth
    #             exp_part = exp(2.374 - 0.00713 * z)
    #
    #             curr_layer.bottom_evap = soil.evap_max * (z / (z + exp_part))
    #
    #         # Evaporation demand for a given soil layer is the difference between
    #         # evaporation demands at the top and bottom of the layer
    #         # "pseudocode_soil" S.2.B.8
    #         layer_evap = curr_layer.bottom_evap - curr_layer.top_evap
    #
    #         # When the water content of a soil layer is below field capacity, the
    #         # evaporative demand for the layer is reduced
    #         # "pseudocode_soil" S.2.B.9
    #         if SW < FC:
    #             exp_part = exp(2.5 * (SW - FC) / (FC - WP))
    #             layer_evap *= exp_part
    #
    #         # In addition, the daily amount of water removed by evaporation is
    #         # limited to 80% of plant available water (SW - WP)
    #         # "pseudocode_soil" S.2.B.10
    #         curr_layer.evap = min(layer_evap, 0.8 * (SW - WP))
    #
    #         soil.soil_layers[x] = curr_layer
