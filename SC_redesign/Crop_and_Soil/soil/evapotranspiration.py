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

from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData


class Evapotranspiration:
    def __init__(self, soil_data: Optional[SoilData] = None):
        self.data = soil_data or SoilData()  # initialize with defaults, if not given

    # --- main routine ---
    def evapotranspirate(self, extraterrestrial_radiation: float, max_air_temp: float, min_air_temp: float,
                         avg_air_temp: float, above_ground_biomass: float, residue: float, snow_water_content: float,
                         initial_canopy_free_water: float) \
            -> None:
        """does the evapotranspiration of the soil on a given day

        Details: calculates and stores the potential evapotranspiration, soil evaporation in the SoilData object
        """
        self.data.potential_evapotranspiration = self._determine_potential_evapotranspiration(
            extraterrestrial_radiation,
            max_air_temp,
            min_air_temp,
            avg_air_temp)
        self.data.potential_evapotranspiration_adjusted = self._determine_potential_evapotranspiration_adjusted(
            initial_canopy_free_water)
        # TODO: add field (in CropData?) to track amount of free water in canopy as it gets adjusted - issue #316
        self.data.soil_evaporation_adjusted = self._determine_soil_evaporation_adjusted(
            above_ground_biomass,
            residue,
            snow_water_content,
            self.data.potential_evapotranspiration_adjusted,
            self.data.transpiration)
        self.data.maximum_soil_evaporation = self._determine_maximum_soil_evaporation(
            self.data.soil_evaporation_adjusted,
            snow_water_content)
        # TODO: snow water content needs to be tracked and adjusted as time goes by (in SoilData or by a weather
        #  monitor?) - issue #317
        self.evaporate_from_soil()

    def _determine_potential_evapotranspiration_adjusted(self, initial_canopy_free_water: float) -> float:
        """Calculates the potential evapotranspiration adjusted for evaporation of free water in the canopy

        Args:
            initial_canopy_free_water: initial amount of free water held in canopy on a given day

        Returns:
            potential evapotranspiration adjusted for evaporation of free water in canopy in mm

        SWAT Reference: 2:2.3.1 (Whole section)
        """
        if self.data.potential_evapotranspiration < initial_canopy_free_water:
            """
            Evaporation from free water in canopy on a given day is set equal to potential evapotranspiration on a given
            day (2:2.3.1), and the potential evapotranspiration adjusted for evaporation of free water in 
            canopy is equal to their difference (E'_0 = E_0 - E_CAN = 0)
            """
            return 0  # 2:2.3.1
        else:
            """
            Evaporation from free water in canopy on given day is set equal to initial free water in the canopy 
            (2:2.3.3), and the potential evapotranspiration adjusted for evaporation of free water in copy is equal to 
            difference between potential evapotranspiration and evaporation from free water in canopy 
            (E'_0 = E_0 - E_CAN)
            """
            return self.data.potential_evapotranspiration - initial_canopy_free_water

    def evaporate_from_soil(self) -> None:
        """
        Evaporates water from each layer of soil

        SWAT Reference: 2:2.3.18, 19, 20
        """
        for layer in self.data.soil_layers:
            evaporative_demand = self._determine_evaporative_demand(self.data.maximum_soil_evaporation, layer)

            # calculate adjusted evaporative demand
            if layer.soil_water_content < layer.field_capacity_water_content:
                # 2:2.3.18
                quotient = (2.5 * (layer.soil_water_content - layer.field_capacity_water_content)) / \
                           (layer.field_capacity_water_content - layer.wilting_point_water_content)
                evaporative_demand_adjusted = evaporative_demand * exp(quotient)
            else:
                # 2:2.3.19
                evaporative_demand_adjusted = evaporative_demand

            # calculate water removed from layer by evaporation
            amount_water_removed = min(evaporative_demand_adjusted,
                                       0.8 * (layer.soil_water_content - layer.wilting_point_water_content))

            # remove water from soil water content
            layer.soil_water_content -= amount_water_removed

    # --- static methods ---
    @staticmethod
    def _determine_potential_evapotranspiration(extra_terrestrial_radiation: float, max_air_temp: float,
                                                min_air_temp: float,
                                                avg_air_temp: float) -> float:
        """calculates the potential evapotranspiration for a given day

        Args:
            extra_terrestrial_radiation: radiation from the aliens, in MJ m^(-2) d^(-1) TODO: better description
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
    def _determine_soil_evaporation_adjusted(above_ground_biomass: float, residue: float, snow_water_content: float,
                                             potential_evapotranspiration_adjusted: float,
                                             transpiration: float) -> float:
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
            maximum soil evaporation in the day adjusted for plant water use

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

    @staticmethod
    def _determine_maximum_soil_evaporation(soil_evaporation_adj: float, snow_water_content: float) -> float:
        """Calculates the maximum amount of evaporation from soil in a given day

        Args:
            soil_evaporation_adj: maximum soil evaporation adjusted for plant water use on a given day in mm
            snow_water_content: amount of water in the snow pack on a given day prior to accounting for sublimation, in
            mm TODO: verify that "amount of water in the snow pack on a given day" (2:2.3.3.1) and "snow water content"
                (2:2.3.3) mean the same thing

        Returns:
            maximum soil water evaporation on a given day in mm

        SWAT Reference: 2:2.3.3.1
        """
        if soil_evaporation_adj < snow_water_content:
            return 0  # 2:2.3.10
        else:
            return soil_evaporation_adj - snow_water_content  # 2:2.3.15

    @staticmethod
    def _determine_evaporative_demand(max_soil_water_evaporation: float, layer_data: LayerData) -> float:
        """calculates the evaporative demand for a given layer of soil

        Args:
            max_soil_water_evaporation: maximum water evaporation from soil on given day in mm
            layer_data: LayerData object of the soil layer to be analyzed

        Returns:
            evaporative demand for given layer of soil in mm

        SWAT Reference: 2:2.3.17
        """
        # Calculate top evaporative demand
        top_depth = layer_data.top_depth
        top_quotient = top_depth / (top_depth + exp(2.374 - (0.00713 * top_depth)))
        top_evaporative_demand = max_soil_water_evaporation * top_quotient

        # Calculate bottom evaporative demand
        bottom_depth = layer_data.bottom_depth
        bottom_quotient = bottom_depth / (bottom_depth + exp(2.374 - (0.00713 * bottom_depth)))
        bottom_evaporative_demand = max_soil_water_evaporation * bottom_quotient

        return bottom_evaporative_demand - (top_evaporative_demand * layer_data.esco)

