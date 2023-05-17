from math import exp
from typing import Optional
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData

"""
This module is based off of the 'Soil Water Evaporation' (2:2.3.3.2) section of the SWAT Theoretical documentation.
"""


class Evaporation:
    def __init__(self, soil_data: Optional[SoilData], field_size: Optional[float] = None):
        """This method initializes the SoilData object that this module will work with, or create one if none provided.

        Parameters
        ----------
        soil_data : SoilData, optional
            The SoilData object used by this module to track evaporation and transpiration from the soil profile,
            creates new one if one is not provided.
        field_size : float, optional
            Used to initialize a SoilData object for this module to work with, if a pre-configured SoilData object is
            not provided (ha)

        """
        self.data = soil_data or SoilData(field_size=field_size)

    # --- main routine ---
    def evaporate(self, maximum_soil_water_evaporation: float) -> float:
        """Evaporates water from the soil profile.

        Parameters
        ----------
        maximum_soil_water_evaporation : float
            Maximum amount of water allowed to be evaporated from the soil profile on the current day (mm)

        Returns
        -------
        float
            Actual amount of water evaporated from the soil on a given day (mm)

        """
        amount_available_for_evaporation = maximum_soil_water_evaporation
        for layer in self.data.soil_layers:
            evaporative_demand = self._determine_layer_evaporative_demand(
                maximum_soil_water_evaporation, layer.top_depth, layer.bottom_depth,
                layer.soil_evaporation_compensation_coefficient)
            evaporative_demand_reduced = self._determine_evaporative_demand_reduced(
                evaporative_demand, layer.water_content, layer.field_capacity_content, layer.wilting_point_content)
            amount_water_removed = self._determine_amount_water_removed(
                evaporative_demand_reduced, layer.water_content, layer.wilting_point_content)

            no_more_soil_water_evaporated = amount_available_for_evaporation <= amount_water_removed
            if no_more_soil_water_evaporated:
                amount_water_removed = amount_available_for_evaporation
            layer.water_content -= amount_water_removed
            amount_available_for_evaporation -= amount_water_removed
            if no_more_soil_water_evaporated:
                break

        total_evaporation_from_soil = maximum_soil_water_evaporation - amount_available_for_evaporation
        self.data.annual_soil_evaporation_total += total_evaporation_from_soil
        return total_evaporation_from_soil

    # TODO - this method should be moved to field.py and used there when sublimation is implemented #317
    @staticmethod
    def _determine_maximum_soil_evaporation(soil_evaporation_adj: float, snow_water_content: float) -> float:
        """Calculates the maximum amount of evaporation from soil in a given day

        Args:
            soil_evaporation_adj: maximum soil evaporation adjusted for plant water use on a given day (mm)
            snow_water_content: amount of water in the snow pack on a given day prior to accounting for sublimation
            (mm)
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
        top_evaporative_demand = Evaporation._determine_depth_evaporative_demand(max_soil_water_evaporation,
                                                                                 top_depth)
        # Calculate evaporative demand at bottom of layer
        bottom_evaporative_demand = Evaporation._determine_depth_evaporative_demand(max_soil_water_evaporation,
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
