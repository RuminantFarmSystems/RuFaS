from typing import Optional
from math import exp

from RUFAS.routines.field.soil.layer_data import LayerData
from RUFAS.routines.field.soil.soil_data import SoilData
from RUFAS.output_manager import OutputManager

"""
This module is based on the section 'Percolation' (2:3.2) in SWAT
"""

om = OutputManager()


class Percolation:
    def __init__(self, soil_data: Optional[SoilData], field_size: Optional[float] = None):
        """This method initializes the SoilData object that this module will work with, or create one if none provided.

        Parameters
        ----------
        soil_data : SoilData, optional
            The SoilData object used by this module to track percolation, creates new one if one is not provided.
        field_size : float, optional
            Used to initialize a SoilData object for this module to work with, if a pre-configured SoilData object is
            not provided (ha)

        """
        self.data = soil_data or SoilData(field_size=field_size)

    def percolate(self, has_seasonal_high_water_table: bool) -> None:
        """
        Execute percolation of excess water in each layer of soil profile to the layer directly beneath it.

        Parameters
        ----------
        has_seasonal_high_water_table : bool
            A flag indicating whether the HRU has a seasonal high water table (True/False).

        References
        ----------
        SWAT sections 2:3.1 and 2
        """
        layer_count = len(self.data.soil_layers)
        deepest_layer = layer_count - 1

        info_map = {"class": self.__class__.__name__, "function": self.percolate.__name__, "prefix": "Field"}
        om.add_variable("top_water_content_pre_percolation(mm)", self.data.soil_layers[0].water_content, info_map)

        percolation_ops = []
        for layer_number in range(layer_count):  # loop through each layer
            current_layer = self.data.soil_layers[layer_number]

            # get the appropriate underlying layer
            if layer_number < deepest_layer:
                layer_below = self.data.soil_layers[layer_number + 1]
            else:
                layer_below = self.data.vadose_zone_layer

            # check for percolation conditions
            can_percolate = self._determine_if_percolation_allowed(layer_below.water_content,
                                                                   layer_below.field_capacity_content,
                                                                   layer_below.saturation_content,
                                                                   has_seasonal_high_water_table)
            percolated_water = 0.0
            if can_percolate:
                percolated_water = self._percolate_between_layers(self.data.time_step, current_layer, layer_below)
                current_layer.water_content -= percolated_water
                current_layer.percolated_water = percolated_water
                # layer_below.water_content += percolated_water
            else:
                current_layer.percolated_water = 0
            percolation_ops.append((layer_below, percolated_water))

        for op in percolation_ops:
            op[0].water_content += op[1]

    # --- Static methods ---
    @staticmethod
    def _determine_percolation_travel_time(saturation: float, field_capacity_content: float,
                                           saturated_hydraulic_conductivity: float) -> float:
        """
        Calculate the travel time for percolation.

        Parameters
        ----------
        saturation : float
            Amount of water in the soil layer when completely saturated (mm).
        field_capacity_content : float
            Water content of the soil layer at field capacity (mm).
        saturated_hydraulic_conductivity : float
            Saturated hydraulic conductivity of the layer (mm per hour).

        Returns
        -------
        float
            Travel time for percolation (hours).

        References
        ----------
        SWAT 2:3.2.4
        """
        if saturated_hydraulic_conductivity <= 0:
            raise ValueError("Saturated hydraulic conductivity must be greater than 0")
        return (saturation - field_capacity_content) / saturated_hydraulic_conductivity

    @staticmethod
    def _determine_percolation_to_next_layer(drainable_volume_water: float, time_step: float,
                                             travel_time: float) -> float:
        """
        Calculate the amount of water that percolates to the soil layer below it on a given day.

        Parameters
        ----------
        drainable_volume_water : float
            Drainable volume of water in the soil layer on a given day (mm).
        time_step : float
            Length of the time step over which percolation occurs (hours).
        travel_time : float
            Travel time for percolation (hours).

        Returns
        -------
        float
            Amount of water percolating to the underlying soil layer on a given day (mm).

        References
        ----------
        SWAT 2:3.2.3
        """
        return drainable_volume_water * (1 - exp((-1 * time_step) / travel_time))

    @staticmethod
    def _determine_if_percolation_allowed(soil_water_content: float, field_capacity_content: float,
                                          saturated_capacity_content: float,
                                          is_seasonal_high_water_table: bool) -> bool:
        """
        Determine if a layer of soil has enough available capacity to accept more water via percolation.

        Parameters
        ----------
        soil_water_content : float
            Water content of the given soil layer (mm).
        field_capacity_content : float
            Water content of the given soil layer at field capacity (mm).
        saturated_capacity_content : float
            Water content of the given soil layer when completely saturated (mm).
        is_seasonal_high_water_table : bool
            Boolean indicating if HRU has a seasonal high water table (True/False).

        Returns
        -------
        bool
            True if the soil layer can accept more water from percolation, False if not.

        References
        ----------
        SWAT Paragraph in between equations 2:3.2.3, 4
        """
        if not is_seasonal_high_water_table:
            return True
        elif soil_water_content <= \
                (field_capacity_content + (0.5 * (saturated_capacity_content - field_capacity_content))):
            return False
        else:
            return True

    @staticmethod
    def _percolate_between_layers(time_step: float, upper_layer: LayerData, lower_layer: LayerData) -> float:
        """
        Determine the actual amount of water that will percolate from the given upper layer to the given lower layer
        over the provided time step.

        Parameters
        ----------
        upper_layer : LayerData
            Given layer of soil to percolate from (LayerData object).
        lower_layer : LayerData
            Given layer of soil to percolate to (LayerData object).
        time_step : float
            Length of time over which percolation occurs (hours).

        Returns
        -------
        float
            Amount of water that will actually be percolated from the upper layer to the lower layer (mm).

        References
        ----------
        SWAT Section 2:3.2
        """
        if upper_layer.excess_water_available <= 0:
            return 0
        else:
            percolation_time = Percolation._determine_percolation_travel_time(
                upper_layer.saturation_content, upper_layer.field_capacity_content,
                upper_layer.saturated_hydraulic_conductivity)
            amount_to_percolate = Percolation._determine_percolation_to_next_layer(
                upper_layer.excess_water_available, time_step, percolation_time)

            #  Limit the maximum amount of water allowed to percolate so that lower layer cannot become overly saturated
            if amount_to_percolate > lower_layer.acceptable_percolation_amount:
                amount_to_percolate = lower_layer.acceptable_percolation_amount

            # move water from upper layer to lower layer
            return max(0, amount_to_percolate)
