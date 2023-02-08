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
    soil_water_concentration: float = 0.25  # arbitrary
    """soil water concentration of the layer (mm)"""
    soil_water_content:  Optional[float] = None  
    """volume of soil water in the layer (mm)"""
    field_capacity_water_concentration: float = 0.3  # arbitrary
    """water concentration of soil layer at field capacity (mm)"""
    wilting_point_water_concentration: float = 0.2  # arbitrary
    """water concentration of soil layer at wilting point (mm)"""
    saturation_point_water_concentration: float = 0.5
    """water concentration of soil layer at saturation point (mm)"""
    soil_evaporation_compensation_coefficient: float = 1
    """coefficient that allows user to modify depth distribution used to meet the soil evaporative demand (unitless) 
        (2:2.3.17)"""

    # --- Percolation
    temperature: float = 15.05
    """temperature of soil layer (degrees Celsius)"""
    saturated_hydraulic_conductivity: float = 9.5
    """saturated hydraulic conductivity for this layer of soil (mm per hour)"""
    available_water_capacity: float = 0.2
    """available water capacity expressed as fraction of total soil volume"""

    def __post_init__(self):
        """This function initializes all attributes in the dataclass that depend on"""
        self.soil_water_content = self.soil_water_concentration * self.layer_thickness

    @property
    def layer_thickness(self) -> float:
        """thickness of soil layer in mm"""
        return self.bottom_depth - self.top_depth

    @property
    def field_capacity_content(self) -> float:
        """volume of water in layer when at field capacity in mm"""
        return self.field_capacity_water_concentration * self.layer_thickness

    @property
    def wilting_point_content(self) -> float:
        """volume of water in layer when at wilting point"""
        return self.wilting_point_water_concentration * self.layer_thickness

    @property
    def excess_water_available(self):
        """volume of water available for percolation in the soil layer in mm

        SWAT Reference: 2:3.2.1, 2
        """
        return max(0, self.soil_water_content - self.field_capacity_content)

    @property
    def saturation_content(self) -> float:
        """volume of water in layer when saturated in mm"""
        return self.saturation_point_water_concentration * self.layer_thickness

    @property
    def acceptable_percolation_amount(self) -> float:
        """volume of water that can be accepted by layer before reaching saturation (in mm)"""
        return max(0, self.saturation_content - self.soil_water_content)
