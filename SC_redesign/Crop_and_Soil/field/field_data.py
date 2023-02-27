from typing import Optional
from dataclasses import dataclass
from SC_redesign.Crop_and_Soil.field.harvest_operations import HarvestOperation
from SC_redesign.Crop_and_Soil.crop.dormancy import Dormancy



@dataclass(kw_only=True)
class FieldData:
    """data object to track the field-specific variables"""

    # --- Soil Management Variables ---
    is_amendment_day: bool = False
    """should nutrients be added to the soil today?"""
    is_tillage_day: bool = False
    """should the soil be tilled today?"""

    # --- Crop management Variables ---
    use_scheduled_harvest: bool = True
    """Should harvesting be done according to user-defined schedule? False will trigger the alternative: heat unit 
    scheduling, whereby harvest operations are conducted to maximize yield (based on heat unit accumulation)."""
    is_planting_day: bool = False
    """is today the day to plant new crops?"""
    is_harvest_day: bool = False
    """is today the day to cut crops in the field?"""
    cut_fraction: float = 0.5
    """proportion of crop biomass present in the field that should be cut at the next/current cut (or harvest) event
    (unitless)"""
    harvest_proportion: float = 1.0
    """proportion of the cut biomass to be removed from the field after the next/current cut event (unitless)"""
    harvest_type: Optional[HarvestOperation] = HarvestOperation("default")
    """the HarvestOperation, specifying which harvest operation to use"""
    absolute_latitude: float = 43.5     # TODO: set default to somewhere other than Wisconsin, or no default?
    """The absolute latitude value (degrees above or below equator) where field is located (degrees)"""
    minimum_daylength: float = 6.33     # TODO: set default to somewhere other than Wisconsin, or no default?
    """Shortest day of the year for this watershed (hours)"""
    dormancy_threshold_daylength: Optional[float] = None
    """Threshold daylength to initiate dormancy in a plant (hours)"""


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

    def __post_init__(self):
        """Initialize all attributes in FieldData object that need to be set based on other FieldData attributes"""
        dormancy_threshold = Dormancy._find_dormancy_threshold(self.absolute_latitude)
        self.dormancy_threshold_daylength = Dormancy._find_threshold_daylength(self.minimum_daylength,
                                                                               dormancy_threshold)
