from typing import Optional, List, Dict
from dataclasses import dataclass
from RUFAS.routines.field.crop.dormancy import Dormancy
from RUFAS.routines.field.crop_and_soil_constants import LITERS_TO_CUBIC_MILLIMETERS, HECTARES_TO_SQUARE_MILLIMETERS


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
    absolute_latitude: float = 43.5  # TODO: set default to somewhere other than Wisconsin, or no default?
    """The absolute latitude value (degrees above or below equator) where field is located (degrees)"""
    minimum_daylength: float = 6.33  # TODO: set default to somewhere other than Wisconsin, or no default?
    """Shortest day of the year for this watershed (hours)"""
    longitude: float = -88.6  # TODO: set default to somewhere other than Wisconsin, or no default?
    """The longitude value of where the field is located (degrees)."""
    dormancy_threshold_daylength: Optional[float] = None
    """Threshold daylength to initiate dormancy in a plant (hours)"""
    current_residue: float = 0
    """total amount of residue on the current day (kg per hectare)"""
    current_crop_config: Optional[List[Dict]] = None
    """list of dictionaries to configure crops to be planted in the field. The dicts should contain
    attribute-value pairs, with attributes matching those of CropData."""

    # --- Field-level Variables ---
    name: Optional[str] = None
    """Name of this field for identification purposes."""
    transpiration: float = 0.0
    """total amount of water lost to transpiration in the field on the current day (mm)"""
    max_transpiration: float = 0.0
    """maximum possible amount of water that could be lost to transpiration in the field for the current day (mm)"""
    max_evapotranspiration: float = 0.0
    """maximum possible amount of water that could be lost to evapotranspiration in the field for the current day
    (mm)"""
    grazers_present: bool = False
    """are grazers currently in the field? is grazing occurring?"""
    seasonal_high_water_table: bool = False
    """if the HRU has a seasonal high water table (true/false)"""
    field_size: float = 1
    """size of the field (ha)"""

    # --- Irrigation variables ---
    watering_amount_in_liters: Optional[float] = None
    """User-supplied amount of water to be applied to the field over a specified interval of days (liters)"""
    watering_amount_in_mm: float = 0
    """Amount of water to be applied to the field over a specified interval of days (mm)"""
    watering_interval: Optional[int] = None
    """Number of days over which the specified amount of water needs to be applied."""
    days_into_watering_interval: int = 0
    """Number of days since the start of the current watering interval."""
    current_water_deficit: float = 0
    """Amount of water that still needs to be applied to the field in the current interval (mm)"""
    watering_occurs: bool = True
    """Status indicating if this field is watered at all."""

    # --- Annual totals ---
    annual_irrigation_water_use_total: float = 0
    """Cumulative total of water used for irrigation in a year (mm)"""

    def __post_init__(self):
        """Initialize all attributes in FieldData object that need to be set based on other FieldData attributes.

        Raises
        ------
        ValueError
            If the watering amount is < 0.
        ValueError
            If the watering interval is < 0.

        """
        self.dormancy_threshold = Dormancy.find_dormancy_threshold(self.absolute_latitude)
        self.dormancy_threshold_daylength = Dormancy.find_threshold_daylength(self.minimum_daylength,
                                                                              self.dormancy_threshold)

        should_water = self.watering_amount_in_liters is not None and self.watering_interval is not None and \
            self.watering_amount_in_liters != 0.0 and self.watering_interval != 0
        if should_water:
            if self.watering_amount_in_liters < 0.0:
                raise ValueError(f"Expected watering amount to be >= 0, received '{self.watering_amount_in_liters}'.")
            elif self.watering_interval < 0:
                raise ValueError(f"Expected watering interval to be >= 0, received '{self.watering_interval}'.")

            self.watering_amount_in_mm = self.convert_liters_to_millimeters(self.watering_amount_in_liters,
                                                                            self.field_size)
            self.current_water_deficit = self.watering_amount_in_mm
        else:
            self.watering_occurs = False

    def perform_annual_field_reset(self) -> None:
        """Resets all cumulative totals that are calculated annually for the field."""
        self.annual_irrigation_water_use_total = 0

    @staticmethod
    def convert_liters_to_millimeters(liter_amount: float, field_size: float) -> float:
        """Converts an amount in liters to an amount in mm based on the area the liters are distributed over.

        Parameters
        ----------
        liter_amount : float
            Volume to be converted (liters)
        field_size : float
            Size of the field (ha)

        Returns
        -------
        float
            Millimeter amount that is distributed evenly across the specified field area (mm)

        """
        amount_in_cubic_millimeters = liter_amount * LITERS_TO_CUBIC_MILLIMETERS
        field_size_in_square_millimeters = field_size * HECTARES_TO_SQUARE_MILLIMETERS
        return amount_in_cubic_millimeters / field_size_in_square_millimeters
