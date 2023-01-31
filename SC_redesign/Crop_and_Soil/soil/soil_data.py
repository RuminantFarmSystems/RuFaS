from dataclasses import dataclass
from typing import List, Optional
from SC_redesign.Crop_and_Soil.soil.layer_data import LayerData


@dataclass
class SoilData:
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
    soil_layers: Optional[List[LayerData]] = None
    """list of soil layer data objects, top layer is 0th, bottom is nth"""

    # ---- infiltration
    curve_number_2: float = 40  # arbitrary
    """Part of SCS Curve Number Procedure for runoff (SWAT 2:1.1)"""

