from dataclasses import dataclass
from typing import Optional


@dataclass
class SoilData:
    # ---- evapotranspiration
    potential_evapotranspiration: Optional[float] = None
    """potential evapotranspiration for a given day (mm per day)"""
    potential_evapotranspiration_adjusted: Optional[float] = None
    """amount of evapotranspiration adjusted for water in canopy (mm)
        SWAT Reference: 2:2.3.1"""
    transpiration: float = 0.5      # TODO: better default
    """amount of transpiration on a given day (mm)"""
    soil_evaporation: Optional[float] = None
    """maximum amount of evaporation from soil on a given day (mm)"""
