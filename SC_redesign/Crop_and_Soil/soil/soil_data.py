from dataclasses import dataclass
from typing import Optional


@dataclass
class SoilData:
    # ---- evapotranspiration
    extraterrestrial_radiation: float = 100  # TODO: better default
    """extraterrestrial radiation (MJ per meter^(2) per day)"""
    max_air_temp: float = 38
    """maximum air temperature (degrees C)"""
    min_air_temp: float = 15
    """minimum air temperature (degrees C)"""
    avg_air_temp: float = 26.5
    """average air temperature (degrees C)"""
    above_ground_biomass: Optional[float] = None
    """biomass stored in the above ground portion of the plant; plant biomass excluding roots (kg/ha)"""
    residue: Optional[float] = None
    """biomass separated from plant that is on top of soil (kg/ha)"""
    snow_water_content: float = 0
    """amount of water content from snow (mm)"""
    potential_evapotranspiration_adjusted: float = 3  # TODO: better default or write method to calculate this
    """amount of evapotranspiration adjusted for water in canopy (mm)
        SWAT Reference: 2:2.3.1"""
    transpiration: float = 0.5      # TODO: better default
    """amount of transpiration on a given day (mm)"""