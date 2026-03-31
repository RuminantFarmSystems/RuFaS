from math import exp
from typing import Optional

from RUFAS.biophysical.field.soil.layer_data import LayerData
from RUFAS.biophysical.field.soil.soil_data import SoilData


class Percolation:
    """
    This class is based on the 'Percolation' section (2:3.2) in SWAT, designed to manage and simulate soil percolation
    processes. It either accepts an existing SoilData object to work with or creates a new one based on the provided
    field size.

    Parameters
    ----------
    soil_data : Optional[SoilData]
        The SoilData object used by this module to track percolation. A new SoilData object is created if one is not
        provided.
    field_size : Optional[float], default=None
        The size of the field (ha).

    Attributes
    ----------
    data : SoilData
        The SoilData instance being used by the Percolation model.

    """

    def __init__(self, soil_data: Optional[SoilData], field_size: Optional[float] = None):
        self.data = soil_data or SoilData(field_size=field_size)

    def percolate(self, has_seasonal_high_water_table: bool) -> None:
        """
        Execute percolation of excess water in each layer of soil profile to the layer directly beneath it.

        Parameters
        ----------
        has_seasonal_high_water_table : bool
            A flag indicating whether the HRU has a seasonal high water table (True/False).

        Notes
        -----
        RuFaS allows percolation even when the temperature of the soil layer is below zero degrees Celsius.

        This routine calls the subroutine `_percolate_infiltrated_water` to handle percolating water from infiltration
        into the soil profile. If that routine percolates water out of any soil layers (which is the case when there are
        high or sustained amounts of infiltration), this routine will only percolate water out of the soil layers which
        have not had water percolated out of them on the current day.

        References
        ----------
        SWAT sections 2:3.1 and 2

        """

        self.data.set_vectorized_layer_attribute("percolated_water", [0.0] * len(self.data.soil_layers))
        layer_count = len(self.data.soil_layers)
        deepest_layer = layer_count - 1

        for layer_number in reversed(range(0, layer_count)):
            current_layer = self.data.soil_layers[layer_number]

            if layer_number < deepest_layer:
                layer_below = self.data.soil_layers[layer_number + 1]
            else:
                layer_below = self.data.vadose_zone_layer

            can_percolate = self._determine_if_percolation_allowed(
                layer_below.water_content,
                layer_below.field_capacity_content,
                layer_below.saturation_content,
                has_seasonal_high_water_table,
            )
            if can_percolate:
                percolated_water = self._percolate_between_layers(self.data.time_step, current_layer, layer_below)
                current_layer.water_content -= percolated_water
                current_layer.percolated_water += percolated_water
            else:
                current_layer.percolated_water = 0.0

        for layer_number in range(1, layer_count + 1):
            layer_above = self.data.soil_layers[layer_number - 1]
            percolated_water = layer_above.percolated_water
            if layer_number == deepest_layer + 1:
                self.data.vadose_zone_layer.water_content += percolated_water
            else:
                self.data.soil_layers[layer_number].water_content += percolated_water

    def percolate_infiltrated_water(self) -> None:
        """
        Percolates infiltrated water into the soil profile.

        Notes
        -----
        The amount of water allowed to infiltrate the soil on any given day is based on the available capacity of the
        entire soil profile. So when there is an extreme amount of infiltration or there are multiple days of high
        infiltration in a row, this method fills soil layers to their saturation point going top-down, and records water
        that is put below a layer as being percolated by it.

        """

        water_remaining_to_percolate = self.data.infiltrated_water
        for index, layer in enumerate(self.data.soil_layers):
            acceptable_percolation = layer.acceptable_percolation_amount
            if water_remaining_to_percolate > acceptable_percolation:
                layer.water_content += acceptable_percolation
                water_remaining_to_percolate -= acceptable_percolation
                layer.percolated_water += water_remaining_to_percolate
            else:
                layer.water_content += water_remaining_to_percolate
                water_remaining_to_percolate = 0.0
                break
        if water_remaining_to_percolate > 0.0:
            self.data.vadose_zone_layer.water_content += water_remaining_to_percolate

    # --- Static methods ---
    @staticmethod
    def _determine_percolation_travel_time(
        saturation: float,
        field_capacity_content: float,
        saturated_hydraulic_conductivity: float,
    ) -> float:
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
    def _determine_percolation_to_next_layer(
        drainable_volume_water: float, time_step: float, travel_time: float
    ) -> float:
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
    def _determine_if_percolation_allowed(
        soil_water_content: float,
        field_capacity_content: float,
        saturated_capacity_content: float,
        is_seasonal_high_water_table: bool,
    ) -> bool:
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
        elif soil_water_content <= (
            field_capacity_content + (0.5 * (saturated_capacity_content - field_capacity_content))
        ):
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
        if upper_layer.water_content <= upper_layer.field_capacity_content:
            return 0
        else:
            percolation_time = Percolation._determine_percolation_travel_time(
                upper_layer.saturation_content,
                upper_layer.field_capacity_content,
                upper_layer.saturated_hydraulic_conductivity,
            )
            water_to_percolate = upper_layer.excess_water_available
            amount_to_percolate = Percolation._determine_percolation_to_next_layer(
                water_to_percolate, time_step, percolation_time
            )
            #  Limit the maximum amount of water allowed to percolate so that lower layer cannot become overly saturated
            if amount_to_percolate > lower_layer.acceptable_percolation_amount:
                amount_to_percolate = lower_layer.acceptable_percolation_amount

            # move water from upper layer to lower layer
            return max(0, amount_to_percolate)
