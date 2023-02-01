from dataclasses import dataclass
from typing import List, Optional
from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData


@dataclass
class SoilData:
    soil_layers: Optional[List[LayerData]] = None
    """list of soil layer data objects, top layer is 0th element, bottom is nth element"""

    # ---- evapotranspiration
    potential_evapotranspiration: Optional[float] = None
    """potential evapotranspiration for a given day (mm per day)"""
    potential_evapotranspiration_adjusted: Optional[float] = None
    """amount of evapotranspiration adjusted for water in canopy (mm)
        SWAT Reference: 2:2.3.1"""
    transpiration: float = 0.5  # TODO: better default
    """amount of transpiration on a given day (mm)"""
    soil_evaporation_adjusted: Optional[float] = None
    """maximum amount of evaporation from soil on a given day adjusted for plant use (mm)"""
    maximum_soil_evaporation: Optional[float] = None
    """maximum amount of evaporation from soil on a given day (mm)"""

    # ---- infiltration
    previous_retention_parameter: Optional[float] = None
    """retention parameter for the previous day (mm) (used in SWAT 2:1.1.9)"""
    average_slope_fraction: float = 0.05
    """average slope fraction of the subbasin"""
    moisture_condition_parameter: Optional[float] = None
    """curve number value adjusted for moisture content (unitless) (SWAT 2:1.1.11)"""

    @property
    def profile_soil_water_content(self) -> float:
        """

        Returns: amount of water in the entire soil profile (excluding the amount of water held in the profile at the
            wilting point) in mm

        Details: this method for calculating total soil water content assumes the lower bound of water to be 0. It also
            calculates the soil water content per layer, meaning that if one layer has water content greater than its
            wilting water point and another layer has water content less than its wilting point, the first layer will
            not have to compensate for the deficit in the second layer.

        """
        if self.soil_layers is None:
            return 0
        else:
            water_sum = 0
            for layer in self.soil_layers:
                water_sum += min(0, (layer.soil_water_content - layer.wilting_point_water_content))
            return

    @property
    def profile_saturation(self) -> float:
        """

        Returns: amount of water in the soil profile when completely saturated in mm

        """
        if self.soil_layers is None:
            return 0
        else:
            saturation_sum = 0
            for layer in self.soil_layers:
                saturation_sum += layer.saturation
            return saturation_sum

    @property
    def profile_field_capacity(self) -> float:
        """

        Returns: total amount of water contained in the soil profile at field capacity (but not saturated) in mm

        """
        if self.soil_layers is None:
            return 0
        else:
            field_capacity_sum = 0
            for layer in self.soil_layers:
                field_capacity_sum += layer.field_capacity_water_content
            return field_capacity_sum
