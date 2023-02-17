from math import exp
from typing import Optional

from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData

"""
This module is based off of the 'Actual Evapotranspiration' (2:2.3) section of the SWAT model documentation
"""


class Evapotranspiration:
    def __init__(self, soil_data: Optional[SoilData] = None):
        self.data = soil_data or SoilData()  # initialize with defaults, if not given

    # --- main routine ---
    def evapotranspirate(self, extraterrestrial_radiation: float, max_air_temp: float, min_air_temp: float,
                         avg_air_temp: float, above_ground_biomass: float, residue: float, snow_water_content: float,
                         initial_canopy_free_water: float) -> None:
        """executes evapotranspiration processes on nh the soil on a given day

        Details: calculates and stores the potential evapotranspiration, soil evaporation in the SoilData object

        Args:
            extraterrestrial_radiation: radiation from the aliens, in MJ per square meter per day
                TODO: better description
            max_air_temp: maximum air temperature (degrees C)
            min_air_temp: minimum air temperature (degrees C)
            avg_air_temp: average air temperature (degrees C)
            above_ground_biomass: mass of plant above ground (kg per hectare)
            residue: biomass separated from plant on the ground (kg per hectare)
            snow_water_content: amount of water from snow (mm)
            initial_canopy_free_water: initial amount of free water held in canopy on a given day (mm)

        """
        self.data.potential_evapotranspiration = self._determine_potential_evapotranspiration(
            extraterrestrial_radiation,
            max_air_temp,
            min_air_temp,
            avg_air_temp)
        self.data.potential_evapotranspiration_adjusted = self._determine_potential_evapotranspiration_adjusted(
            initial_canopy_free_water)
        # TODO: add attribute (in CropData?) to track amount of free water in canopy as it gets adjusted - issue #316
        self.data.soil_evaporation_adjusted = self._determine_soil_evaporation_adjusted(
            above_ground_biomass,
            residue,
            snow_water_content,
            self.data.potential_evapotranspiration_adjusted,
            self.data.transpiration)
        self.data.annual_adjusted_soil_evaporation_total += self.data.soil_evaporation_adjusted
        self.data.maximum_soil_evaporation = self._determine_maximum_soil_evaporation(
            self.data.soil_evaporation_adjusted,
            snow_water_content)
        self.data.annual_maximum_soil_evaporation_total += self.data.maximum_soil_evaporation
        # TODO: snow water content needs to be tracked and adjusted as time goes by (in SoilData or by a weather
        #  monitor?) - issue #317
        self._evaporate_from_soil()

        # Update annual totals
        self.data.annual_potential_evapotranspiration_total += self.data.potential_evapotranspiration
        self.data.annual_adjusted_potential_evapotranspiration_total += \
                                                            self.data.annual_adjusted_potential_evapotranspiration_total
        self.data.annual_adjusted_soil_evaporation_total += self.data.soil_evaporation_adjusted
        self.data.annual_maximum_soil_evaporation_total += self.data.maximum_soil_evaporation

    def _determine_potential_evapotranspiration_adjusted(self, initial_canopy_free_water: float) -> float:
        """Calculates the potential evapotranspiration adjusted for evaporation of free water in the canopy

        Args:
            initial_canopy_free_water: initial amount of free water held in canopy on a given day (mm)

        Returns:
            potential evapotranspiration adjusted for evaporation of free water in canopy (mm)

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

    def _evaporate_from_soil(self) -> None:
        """
        Evaporates water from each layer of soil

        SWAT Reference: 2:2.3.3.2
        """
        for layer in self.data.soil_layers:
            evaporative_demand = self._determine_layer_evaporative_demand(self.data.maximum_soil_evaporation,
                                                                          layer.top_depth, layer.bottom_depth,
                                                                          layer.soil_evaporation_compensation_coefficient)
            evaporative_demand_reduced = self._determine_evaporative_demand_reduced(evaporative_demand,
                                                                                    layer.water_content,
                                                                                    layer.field_capacity_content,
                                                                                    layer.wilting_point_content)
            amount_water_removed = self._determine_amount_water_removed(evaporative_demand_reduced,
                                                                        layer.water_content,
                                                                        layer.wilting_point_content)

            # remove water from soil water content
            layer.water_content -= amount_water_removed

    # --- static methods ---
    @staticmethod
    def _determine_potential_evapotranspiration(extra_terrestrial_radiation: float, max_air_temp: float,
                                                min_air_temp: float,
                                                avg_air_temp: float) -> float:
        """calculates the potential evapotranspiration for a given day

        Args:
            extra_terrestrial_radiation: radiation from the aliens (MJ per square meter per day)
                TODO: better description
            max_air_temp: maximum air temperature (degrees C)
            min_air_temp: minimum air temperature (degrees C)
            avg_air_temp: average air temperature (degrees C)

        Returns:
            potential evapotranspiration (mm per day)

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
            avg_air_temp: average air temperature (degrees C)

        Returns:
            latent heat of vaporization (MJ per kg)

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
            above_ground_biomass: mass of plant above ground (kg per hectare)
            residue: biomass separated from plant on the ground (kg per hectare)
            snow_water_content: amount of water from snow (mm)
            potential_evapotranspiration_adjusted: potential evapotranspiration adjusted for evaporation of free water
                in canopy (mm)
            transpiration: transpiration for a given day (mm)
        Returns:
            maximum soil evaporation in the day adjusted for plant water use (mm)

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
            above_ground_biomass: mass of plant above ground (kg per hectare)
            residue: biomass separated from plant on the ground (kg per hectare)
            snow_water_content: amount of water from snow (mm)

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
            soil_evaporation_adj: maximum soil evaporation adjusted for plant water use on a given day (mm)
            snow_water_content: amount of water in the snow pack on a given day prior to accounting for sublimation (mm)
                TODO: verify that "amount of water in the snow pack on a given day" (2:2.3.3.1) and "snow water content"
                    (2:2.3.3) mean the same thing

        Returns:
            maximum soil water evaporation on a given day (mm)

        SWAT Reference: 2:2.3.3.1
        """
        if soil_evaporation_adj < snow_water_content:
            return 0  # 2:2.3.10
        else:
            return soil_evaporation_adj - snow_water_content  # 2:2.3.15

    @staticmethod
    def _determine_depth_evaporative_demand(max_soil_water_evaporation: float, depth: float) -> float:
        """calculates evaporative demand

        Args:
            max_soil_water_evaporation: maximum soil water evaporation on a given day (mm)
            depth: depth below the surface (mm)
                TODO: check that it is actually in mm, SWAT page 137 does not explicitly say so

        Returns:
            evaporative demand at the given depth (mm)

        SWAT Reference: 2:2.3.16
        """
        return max_soil_water_evaporation * (depth / (depth + exp(2.374 - (0.00713 * depth))))

    @staticmethod
    def _determine_layer_evaporative_demand(max_soil_water_evaporation: float, top_depth: float, bottom_depth: float,
                                            compensation: float) -> float:
        """calculates the evaporative demand for a given layer of soil

        Args:
            max_soil_water_evaporation: maximum water evaporation from soil on given day (mm)
            top_depth: depth of top of layer to be analyzed (mm)
            bottom_depth: depth of bottom of layer to be analyzed (mm)
            compensation: soil evaporative compensation coefficient (unitless)

        Returns:
            evaporative demand for given layer of soil (mm)

        SWAT Reference: 2:2.3.16, 17
        """
        # Check layer integrity
        if top_depth is None or \
                top_depth < 0 or \
                bottom_depth is None or \
                bottom_depth < 0 or \
                (bottom_depth <= top_depth):
            raise ValueError("Missing or illegal values for top or bottom depths")

        # Calculate evaporative demand at top of layer
        top_evaporative_demand = Evapotranspiration._determine_depth_evaporative_demand(max_soil_water_evaporation,
                                                                                        top_depth)
        # Calculate evaporative demand at bottom of layer
        bottom_evaporative_demand = Evapotranspiration._determine_depth_evaporative_demand(max_soil_water_evaporation,
                                                                                           bottom_depth)
        return bottom_evaporative_demand - (top_evaporative_demand * compensation)

    @staticmethod
    def _determine_evaporative_demand_reduced(evaporative_demand: float, soil_water_content: float,
                                              field_water_content: float, wilting_water_content: float) -> float:
        """calculates evaporative demand reduced for water content and field capacity

        Args:
            evaporative_demand: evaporative demand for current soil layer (mm)
            soil_water_content: soil water content of given layer (mm)
            field_water_content: field capacity water content of given layer (mm)
            wilting_water_content: wilting point water content of given layer (mm)

        Returns:
            reduced evaporative demand for current layer based on how much water is in layer (mm)

        SWAT Reference: 2:2.3.18, 19
        """
        # calculate adjusted evaporative demand
        if soil_water_content < field_water_content:
            # 2:2.3.18
            quotient = (2.5 * (soil_water_content - field_water_content)) / (
                    field_water_content - wilting_water_content)
            evaporative_demand_reduced = evaporative_demand * exp(quotient)
        else:
            # 2:2.3.19
            evaporative_demand_reduced = evaporative_demand

        return evaporative_demand_reduced

    @staticmethod
    def _determine_amount_water_removed(reduced_evaporative_demand, soil_water_content: float,
                                        wilting_water_content: float) -> float:
        """calculates amount of water lost from soil layer from evaporation

        Args:
            reduced_evaporative_demand: evaporative demand reduced for water content and field capacity (mm)
            soil_water_content: soil water content of given layer (mm)
            wilting_water_content: wilting point water content of given layer (mm)

        Returns:
            amount of water removed from soil layer by evaporation (mm)

        SWAT Reference: 2:2.3.20
        """
        return min(reduced_evaporative_demand, 0.8 * (soil_water_content - wilting_water_content))
