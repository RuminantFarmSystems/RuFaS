from typing import List, Optional
from math import exp

from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData
from SC_redesign.Crop_and_Soil.soil.soil_data import SoilData

"""
This module is based on the section 'Percolation' (2:3.2) in SWAT
"""


class Percolation:
    def __init__(self, soil_data: Optional[SoilData] = None):
        self.data = soil_data or SoilData()

    def percolate(self, has_seasonal_high_water_table: bool) -> None:
        """executes percolation of excess water in each layer of soil profile to the layer directly beneath it

        Args:
            has_seasonal_high_water_table: if the HRU has a seasonal high water table (true/false)

        SWAT Reference: sections 2:3.1 and 2
        """
        for i in range(len(self.data.soil_layers)):
            """iterate through each layer of soil in the soil profile"""
            upper_layer = self.data.soil_layers[i]
            if i != (len(self.data.soil_layers) - 1):
                """upper layer is not the bottom layer of the soil profile"""
                lower_layer = self.data.soil_layers[i + 1]
                if upper_layer.temperature > 0 and self._determine_if_percolation_allowed(
                        lower_layer.soil_water_content,
                        lower_layer.field_capacity_content,
                        lower_layer.saturation_content,
                        has_seasonal_high_water_table):
                    """percolation is allowed from upper to lower layer"""
                    amount_to_percolate = self._percolate_between_layers(self.data.time_step, upper_layer, lower_layer)
                else:
                    """percolation not allowed from upper to lower layer"""
                    continue
            else:
                """upper layer is the bottom layer of the soil profile, percolation goes into vadose zone which can 
                    accept infinite amount of water
                """
                if upper_layer.temperature > 0:
                    """percolation is allowed from upper to lower layer"""
                    lower_layer = self.data.vadose_zone_layer
                    if upper_layer.temperature > 0:
                        amount_to_percolate = self._percolate_between_layers(self.data.time_step, upper_layer,
                                                                             lower_layer)
                else:
                    """percolation not allowed from upper to lower layer"""
                    break
            if amount_to_percolate > 0:
                upper_layer.soil_water_content -= amount_to_percolate
                lower_layer.soil_water_content += amount_to_percolate

    # --- Static methods ---
    @staticmethod
    def _determine_percolation_travel_time(saturation: float, field_capacity_content: float,
                                           saturated_hydraulic_conductivity: float) -> float:
        """calculates the travel time for percolation

        Args:
            saturation: amount of water in soil layer when completely saturated in mm
            field_capacity_content: water content of the soil layer at field capacity in mm
            saturated_hydraulic_conductivity: saturated hydraulic conductivity of the layer in mm per hour

        Returns:
            travel time for percolation in hours

        SWAT Reference: 2:3.2.4
        """
        if saturated_hydraulic_conductivity <= 0:
            raise ValueError("Saturated hydraulic conductivity must be greater than 0")
        return (saturation - field_capacity_content) / saturated_hydraulic_conductivity

    @staticmethod
    def _determine_percolation_to_next_layer(drainable_volume_water: float, time_step: float,
                                             travel_time: float) -> float:
        """calculates amount of water that percolates to soil layer below it on a given day

        Args:
            drainable_volume_water: drainable volume of water in soil layer on a given day in mm
            time_step: length of time step over which percolation occurs in hours
            travel_time: travel time for percolation in hours

        Returns:
            amount of water percolating to the underlying soil layer on a given day in mm

        SWAT Reference: 2:3.2.3
        """
        return drainable_volume_water * (1 - exp((-1 * time_step) / travel_time))

    @staticmethod
    def _determine_if_percolation_allowed(soil_water_content: float, field_capacity_content: float,
                                          saturated_capacity_content: float,
                                          is_seasonal_high_water_table: bool) -> bool:
        """determines if a layer of soil has enough available capacity to accept more water via percolation

        Args:
            soil_water_content: water content of given soil layer in mm
            field_capacity_content: water content of given soil layer at field capacity in mm
            saturated_capacity_content: water content of given soil layer when completely saturated in mm
            is_seasonal_high_water_table: if HRU has a seasonal high water table (true/false)

        Returns:
            True if soil layer can accept more water from percolation, False if not

        SWAT Reference: paragraph in between equations 2:3.2.3, 4
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
        """determines actual amount of water that will percolate from the given upper layer to the given lower layer
            over the provided time step

        Args:
            upper_layer: given layer of soil to percolate from (LayerData object)
            lower_layer: given layer of soil to percolate to (LayerData object)
            time_step: length of time over which percolation occurs in hours

        SWAT Reference: 2:3.2 (section)
        """
        if upper_layer.excess_water_available <= 0:
            return 0
        else:
            percolation_time = Percolation._determine_percolation_travel_time(upper_layer.saturation_content,
                                                                              upper_layer.field_capacity_content,
                                                                              upper_layer.saturated_hydraulic_conductivity)
            amount_to_percolate = Percolation._determine_percolation_to_next_layer(upper_layer.excess_water_available,
                                                                                   time_step, percolation_time)

            #  Limit the maximum amount of water allowed to percolate so that lower layer cannot become overly saturated
            if amount_to_percolate > lower_layer.acceptable_percolation_amount:
                amount_to_percolate = lower_layer.acceptable_percolation_amount

            # move water from upper layer to lower layer
            return amount_to_percolate
