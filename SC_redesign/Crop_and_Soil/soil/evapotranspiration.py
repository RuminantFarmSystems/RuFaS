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

    # --- main routine ---
    def evapotranspirate(self, extraterrestrial_radiation: float, max_air_temp: float, min_air_temp: float,
                         avg_air_temp: float, above_ground_biomass: float, residue: float, snow_water_content: float) \
            -> None:
        """does the evapotranspiration of the soil on a given day

        Details: calculates and stores the potential evapotranspiration, soil evaporation in the SoilData object
        """
        self.data.potential_evapotranspiration = self._determine_potential_evapotranspiration(
            extraterrestrial_radiation,
            max_air_temp,
            min_air_temp,
            avg_air_temp)
        self.data.soil_evaporation = self._determine_soil_evaporation(
            above_ground_biomass,
            residue,
            snow_water_content,
            self.data.potential_evapotranspiration_adjusted,
            self.data.transpiration)

    # --- static methods ---
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
            @TODO: potential evapotranspiration adjusted will need to implemented at a later point, issue #313
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
