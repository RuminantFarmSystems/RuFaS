from typing import Optional
from dataclasses import dataclass


@dataclass(kw_only=True)
class FieldData:
    """data object to track the field-specific variables"""

    # --- Soil Management Variables ---
    is_amendment_day: bool = False
    """should nutrients be added to the soil today?"""
    is_tillage_day: bool = False
    """should the soil be tilled today?"""

    # --- Crop management Variables ---
    is_planting_day: bool = False
    """is today the day to plant new crops?"""
    is_cutting_day: bool = False
    """is today the day to cut crops in the field?"""
    cut_fraction: float = 0.5
    """proportion of crop biomass present in the field that should be cut at the next/current cut (or harvest) event
    (unitless)"""
    harvest_proportion: float = 1.0
    """proportion of the cut biomass to be removed from the field after the next/current cut event (unitless)"""
    current_residue: float = 0
    """total amount of residue on the current day (kg per hectare)"""

    # --- Field-level Variables ---
    evaporation: Optional[float] = None
    """total water lost to evaporation in the field on the current day (mm)"""
    transpiration: Optional[float] = None
    """total amount of water lost to transpiration in the field on the current day (mm)"""
    max_transpiration: Optional[float] = None  # TODO: should probably not default to None
    """maximum possible amount of water that could be lost to transpiration in the field for the current day (mm)"""
    max_evapotranspiration: Optional[float] = None  # TODO: should probably not default to None
    """maximum possible amount of water that could be lost to evapotranspiration in the field for the current day 
    (mm)"""
    potential_evapotranspiration_adjusted: Optional[float] = None  # TODO, needed?
    """adjusted max evapotranspiration (mm)"""
    grazers_present: bool = False
    """are grazers currently in the field? is grazing occurring?"""
    seasonal_high_water_table: bool = False
    """if the HRU has a seasonal high water table (true/false)"""
