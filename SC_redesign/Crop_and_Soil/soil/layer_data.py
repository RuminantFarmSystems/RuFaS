from dataclasses import dataclass, field
from typing import Optional


"""
Each instance of this class represents a layer of soil. Each SoilData object should contain a list of LayerData objects 
to represent its soil
"""


@dataclass
class LayerData:
    top_depth: Optional[float] = None
    """top depth of the layer (mm)"""
    bottom_depth: Optional[float] = None
    """bottom depth of the layer (mm)"""
    nitrate: float = 1.5
    """nitrate level of the layer (kg/ha)"""
    phosphate: float = 0.05
    """phosphate content of the layer (kg/ha)"""
    soil_water_concentration: float = 0.25  # arbitrary
    """soil water concentration of the layer (mm)"""
    water_content:  Optional[float] = None
    """water present in the layer (mm)"""
    field_capacity_water_concentration: float = 0.3  # arbitrary
    """water concentration of soil layer at field capacity (mm water / mm soil)"""
    wilting_point_water_concentration: float = 0.2  # arbitrary
    """water concentration of soil layer at wilting point (mm water / mm soil)"""
    saturation_point_water_concentration: float = 0.5
    """water concentration of soil layer at saturation point (mm water / mm soil)"""
    soil_evaporation_compensation_coefficient: float = 1
    """coefficient that allows user to modify depth distribution used to meet the soil evaporative demand (unitless) 
        (SWAT 2:2.3.17)"""

    # --- Percolation
    temperature: float = 15.05
    """current temperature of this soil layer (degrees Celsius)"""
    saturated_hydraulic_conductivity: float = 9.5
    """saturated hydraulic conductivity for this layer of soil (mm per hour)"""

    # --- Temperature
    bulk_density: float = 1.4
    """bulk density of the soil layer (Mg per cubic meter) (provided by user, but SWAT 2:3.1.1 has an equation for 
        calculating this field as well)"""
    previous_day_temperature: Optional[float] = None
    """temperature of soil layer on the previous day (degrees C)"""

    def __post_init__(self):
        """Initialize all attributes in the dataclass that depend on other attributes"""
        self.water_content = self.soil_water_concentration * self.layer_thickness

    @property
    def layer_thickness(self) -> float:
        """thickness of soil layer (mm)"""
        return self.bottom_depth - self.top_depth

    @property
    def depth_of_layer_center(self) -> float:
        """depth beneath the surface of the center this layer (mm)"""
        return self.top_depth + (self.layer_thickness / 2)

    @property
    def field_capacity_content(self) -> float:
        """volume of water in layer when at field capacity (mm)"""
        return self.field_capacity_water_concentration * self.layer_thickness

    @property
    def wilting_point_content(self) -> float:
        """amount of water in layer when at wilting point (mm)"""
        return self.wilting_point_water_concentration * self.layer_thickness

    @property
    def excess_water_available(self) -> float:
        """volume of water available for percolation in the soil layer (mm)

        SWAT Reference: 2:3.2.1, 2
        """
        return max(0, self.water_content - self.field_capacity_content)

    @property
    def saturation_content(self) -> float:
        """volume of water in layer when saturated (mm)"""
        return self.saturation_point_water_concentration * self.layer_thickness

    @property
    def acceptable_percolation_amount(self) -> float:
        """volume of water that can be accepted by layer before reaching saturation (mm)"""
        return max(0, self.saturation_content - self.water_content)
