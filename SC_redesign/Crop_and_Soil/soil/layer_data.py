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
    soil_water_content: float = field(init=False)
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
    bulk_density: float = 1.4
    """density of the soil layer (milligrams per meter cubed)"""
    percent_clay_content: float = 25
    """percentage of soil layer content that is clay"""
    saturated_hydraulic_conductivity: float = 9.5
    """saturated hydraulic conductivity for this layer of soil (mm per hour)"""
    available_water_capacity: float = 0.2
    """available water capacity expressed as fraction of total soil volume"""

    def __post_init__(self):
        """This function initializes all attributes in the dataclass that depend on """
        self.soil_water_content = self.soil_water_concentration * self.layer_thickness
        """initializes volume of soil water in the layer in mm"""

    @property
    def layer_thickness(self) -> float:
        """thickness of soil layer in mm"""
        return self.bottom_depth - self.top_depth

    # @property
    # def initial_soil_water_content(self) -> float:
    #     """volume of soil water in the layer in mm"""
    #     return self.soil_water_concentration * self.layer_thickness

    @property
    def field_capacity_content(self) -> float:
        """volume of water in layer when at field capacity in mm"""
        return self.field_capacity_water_concentration * self.layer_thickness

    @property
    def wilting_point_content(self) -> float:
        """volume of water in layer when at wilting point"""
        return self.wilting_point_water_concentration * self.layer_thickness

    # TODO: figure out which of these wilting point equations we need or which should be used where

    @property
    def volumetric_wilting_point_content_as_fraction(self) -> float:
        """permanent wilting point volumetric water content expressed as fraction of total soil volume

        SWAT Reference: 2:3.1.5
        """
        return 0.40 * ((self.percent_clay_content * self.bulk_density) / 100)

    @property
    def field_capacity_content_as_volume_fraction(self):
        """water content at field capacity expressed as fraction of total soil volume

        SWAT Reference: 2:3.1.6
        """
        return self.volumetric_wilting_point_content_as_fraction + self.available_water_capacity

    @property
    def excess_water_available(self):
        """volume of water available for percolation in the soil layer in mm

        SWAT Reference: 2:3.2.1, 2
        """
        return min(0, self.soil_water_content - self.field_capacity_content)

    @property
    def saturation_content(self) -> float:
        """volume of water in layer when saturated in mm"""
        return self.saturation_point_water_concentration * self.layer_thickness
