from dataclasses import dataclass
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
    field_capacity_water_concentration: float = 0.3  # arbitrary
    """water concentration of soil layer at field capacity (mm)"""
    wilting_point_water_concentration: float = 0.2  # arbitrary
    """water concentration of soil layer at wilting point (mm)"""
    saturation_point_water_concentration: float = 0.5
    """water concentration of soil layer at saturation point (mm)"""
    soil_evaporation_compensation_coefficient: float = 1
    """coefficient that allows user to modify depth distribution used to meet the soil evaporative demand (2:2.3.17)"""

    @property
    def layer_thickness(self):
        """thickness of soil layer in mm"""
        return self.bottom_depth - self.top_depth

    @property
    def soil_water_content(self):
        """volume of soil water in the layer in mm"""
        return self.soil_water_concentration / self.layer_thickness

    @property
    def field_capacity_content(self):
        """volume of water in layer when at field capacity in mm"""
        return self.field_capacity_water_concentration / self.layer_thickness

    @property
    def wilting_point_content(self):
        """volume of water in layer when at wilting point"""
        return self.wilting_point_water_concentration / self.layer_thickness

    @property
    def saturation_content(self):
        """volume of water in layer when saturated in mm"""
        return self.saturation_point_water_concentration / self.layer_thickness
