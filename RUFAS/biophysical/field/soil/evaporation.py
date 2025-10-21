from math import exp
from typing import Optional

from RUFAS.biophysical.field.soil.soil_data import SoilData


class Evaporation:
    """
    Simulates the evaporation and transpiration from the soil profile as described in the 'Soil Water Evaporation'
    section (2:2.3.3.2) of the SWAT (Soil and Water Assessment Tool) Theoretical documentation.

    Parameters
    ----------
    soil_data : SoilData, optional
        An instance of SoilData for tracking the evaporation and transpiration from the soil profile. If not provided, a
        new instance will be created with the specified field size.
    field_size : float, optional
        The size of the field (ha).

    Attributes
    ----------
    data : SoilData
        The SoilData object that stores and manages the water data within the soil profile.

    """

    def __init__(self, soil_data: Optional[SoilData], field_size: Optional[float] = None):
        self.data = soil_data or SoilData(field_size=field_size)

    def evaporate(self, maximum_soil_water_evaporation: float) -> None:
        """
        Evaporates water from the soil profile.

        Parameters
        ----------
        maximum_soil_water_evaporation : float
            Maximum amount of water allowed to be evaporated from the soil profile on the current day (mm).

        Notes
        -----
        This method takes in a maximum amount of water that may be evaporated from the soil profile, then iterates over
        the layers in the soil profile and determines how much to evaporate from that layer. If the amount determined to
        be evaporated would put the total amount of evaporation over the limit, the amount is reduced to meet the limit
        exactly and the loop is exited after evaporating the reduced amount from the current layer.

        """
        amount_available_for_evaporation = maximum_soil_water_evaporation
        self.data.set_vectorized_layer_attribute("evaporated_water_content", [0.0] * len(self.data.soil_layers))
        for layer in self.data.soil_layers:
            evaporative_demand = self._determine_layer_evaporative_demand(
                maximum_soil_water_evaporation,
                layer.top_depth,
                layer.bottom_depth,
                layer.soil_evaporation_compensation_coefficient,
            )
            evaporative_demand_reduced = self._determine_evaporative_demand_reduced(
                evaporative_demand,
                layer.water_content,
                layer.field_capacity_content,
                layer.wilting_point_content,
            )
            amount_water_removed = self._determine_amount_water_removed(
                evaporative_demand_reduced,
                layer.water_content,
                layer.wilting_point_content,
            )

            amount_water_removed = min(amount_water_removed, amount_available_for_evaporation)
            layer.water_content -= amount_water_removed
            layer.evaporated_water_content = amount_water_removed
            amount_available_for_evaporation -= amount_water_removed
            if amount_available_for_evaporation == 0:
                break

        total_evaporation_from_soil = maximum_soil_water_evaporation - amount_available_for_evaporation
        self.data.water_evaporated = total_evaporation_from_soil
        self.data.annual_soil_evaporation_total += total_evaporation_from_soil

    @staticmethod
    def _determine_depth_evaporative_demand(max_soil_water_evaporation: float, depth: float) -> float:
        """
        Calculates evaporative demand.

        Parameters
        ----------
        max_soil_water_evaporation : float
            Maximum soil water evaporation on a given day (mm).
        depth : float
            Depth below the surface (mm).

        Returns
        -------
        float
            Evaporative demand at the given depth (mm).

        References
        ----------
        SWAT Theoretical documentation 2:2.3.16

        """
        return max_soil_water_evaporation * (depth / (depth + exp(2.374 - (0.00713 * depth))))

    @staticmethod
    def _determine_layer_evaporative_demand(
        max_soil_water_evaporation: float,
        top_depth: float,
        bottom_depth: float,
        compensation: float,
    ) -> float:
        """
        Calculates the evaporative demand for a given layer of soil.

        Parameters
        ----------
        max_soil_water_evaporation : float
            Maximum water evaporation from soil on given day (mm).
        top_depth : float
            Depth of top of layer to be analyzed (mm).
        bottom_depth : float
            Depth of bottom of layer to be analyzed (mm).
        compensation : float
            Soil evaporative compensation coefficient (unitless).

        Returns
        -------
        float
            Evaporative demand for given layer of soil (mm).

        References
        ----------
        SWAT Theoretical documentation 2:2.3.16, 17

        """
        # Check layer integrity
        if (
            top_depth is None
            or top_depth < 0
            or bottom_depth is None
            or bottom_depth < 0
            or (bottom_depth <= top_depth)
        ):
            raise ValueError("Missing or illegal values for top or bottom depths")

        # Calculate evaporative demand at top of layer
        top_evaporative_demand = Evaporation._determine_depth_evaporative_demand(max_soil_water_evaporation, top_depth)
        # Calculate evaporative demand at bottom of layer
        bottom_evaporative_demand = Evaporation._determine_depth_evaporative_demand(
            max_soil_water_evaporation, bottom_depth
        )
        return bottom_evaporative_demand - (top_evaporative_demand * compensation)

    @staticmethod
    def _determine_evaporative_demand_reduced(
        evaporative_demand: float,
        soil_water_content: float,
        field_water_content: float,
        wilting_water_content: float,
    ) -> float:
        """
        Calculates evaporative demand reduced for water content and field capacity.

        Parameters
        ----------
        evaporative_demand : float
            Evaporative demand for current soil layer (mm).
        soil_water_content : float
            Soil water content of given layer (mm).
        field_water_content : float
            Field capacity water content of given layer (mm).
        wilting_water_content : float
            Wilting point water content of given layer (mm).

        Returns
        -------
        float
            Reduced evaporative demand for current layer based on how much water is in layer (mm).

        References
        ----------
        SWAT Theoretical documentation 2:2.3.18, 19
        """
        # calculate adjusted evaporative demand
        if soil_water_content < field_water_content:
            # 2:2.3.18
            quotient = (2.5 * (soil_water_content - field_water_content)) / (
                field_water_content - wilting_water_content
            )
            evaporative_demand_reduced = evaporative_demand * exp(quotient)
        else:
            # 2:2.3.19
            evaporative_demand_reduced = evaporative_demand

        return evaporative_demand_reduced

    @staticmethod
    def _determine_amount_water_removed(
        reduced_evaporative_demand,
        soil_water_content: float,
        wilting_water_content: float,
    ) -> float:
        """
        Calculates amount of water lost from soil layer from evaporation.

        Parameters
        ----------
        reduced_evaporative_demand : float
            Evaporative demand reduced for water content and field capacity (mm).
        soil_water_content : float
            Soil water content of given layer (mm).
        wilting_water_content : float
            Wilting point water content of given layer (mm).

        Returns
        -------
        float
            Amount of water removed from soil layer by evaporation (mm).

        References
        ----------
        SWAT Theoretical documentation 2:2.3.20

        """
        return min(
            reduced_evaporative_demand,
            0.8 * (soil_water_content - wilting_water_content),
        )
