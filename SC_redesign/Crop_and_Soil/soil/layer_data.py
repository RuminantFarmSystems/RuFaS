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
    """nitrate level of the layer ()"""  # TODO: units?
    soil_water_content: float = 1.3  # arbitrary
    """soil water content of the layer (mm)"""
    field_capacity_water_content: float = 1.5  # arbitrary
    """water content of soil layer at field capacity (mm)"""
    wilting_point_water_content: float = 0.2  # arbitrary
    """water content of soil layer at wilting point (mm)"""
    esco: float = 1
    """coefficient that allows user to modify depth distribution used to meet the soil evaporative demand (2:2.3.17)"""
