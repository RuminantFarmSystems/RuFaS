from dataclasses import dataclass
from typing import Optional

from RUFAS.general_constants import GeneralConstants
from RUFAS.biophysical.field.crop.dormancy import Dormancy


@dataclass(kw_only=True)
class FieldData:
    """
    Data object to track the field-specific variables.

    Attributes
    ----------
    name : str, optional
        Name of this field for identification purposes.
    absolute_latitude : float, default=43.5
        The absolute latitude value (degrees above or below equator) where field is located (degrees).
    longitude : float, default=-88.6
        The longitude value of where the field is located (degrees).
    minimum_daylength : float, default=6.33
        Shortest day of the year for this watershed (hours).
    dormancy_threshold_daylength : float, optional
        Threshold daylength to initiate dormancy in a plant (hours).
    current_residue : float, default=0.0
        Total amount of residue on the current day (kg per hectare).
    transpiration : float, default=0.0
        Total amount of water lost to transpiration in the field on the current day (mm).
    max_transpiration : float, default=0.0
        Maximum possible amount of water that could be lost to transpiration in the field for the current day (mm).
    max_evapotranspiration : float, default=0.0
        Maximum possible amount of water that could be lost to evapotranspiration in the field for the current day (mm).
    seasonal_high_water_table : bool, default=False
        Does the Hydrologic Response Unit containing this field have a seasonally high water table.
    field_size : float, default=1.0
        Size of the field (ha).
    watering_amount_in_liters : float, optional
        User-supplied amount of water to be applied to the field over a specified interval of days (liters).
    watering_amount_in_mm : float, default=0.0
        Amount of water to be applied to the field over a specified interval of days (mm).
    watering_interval : int, optional
        Number of days between waterings of the field.
    days_into_watering_interval : int, default=0.0
        Number of days since the start of the current watering interval.
    current_water_deficit : float, default=0.0
        Amount of water that still needs to be applied to the field in the current interval (mm).
    watering_occurs : bool, default=True
        Status indicating if this field is watered at all.
    manure_water : float, default=0.0
        Amount of water to be added to the field from a manure application (mm).
    annual_irrigation_water_use_total : float, default=0.0
        Cumulative total of water used for irrigation in a year (mm).
    simulate_water_stress : bool, default True
        Whether water stress should affect growth of all crops grown in the field.
    simulate_temp_stress : bool, default True
        Whether temperature stress should affect growth of all crops grown in the field.
    simulate_nitrogen_stress : bool, default True
        Whether nitrogen stress should affect growth of all crops grown in the field.
    simulate_phosphorus_stress : bool, default True
        Whether phosphorus stress should affect growth of all crops grown in the field.

    Methods
    -------
    perform_annual_field_reset()
        Resets all cumulative totals that are calculated annually for the field.
    convert_liters_to_millimeters(liter_amount, field_size)
        Converts an amount in liters to an amount in mm based on the area the liters are distributed over.
    """

    name: Optional[str] = None
    absolute_latitude: float = 43.5
    longitude: float = -88.6
    minimum_daylength: float = 6.33
    dormancy_threshold_daylength: Optional[float] = None
    current_residue: float = 0.0

    transpiration: float = 0.0
    max_transpiration: float = 0.0
    max_evapotranspiration: float = 0.0
    seasonal_high_water_table: bool = False
    field_size: float = 1.0

    # --- Irrigation variables ---
    watering_amount_in_liters: Optional[float] = None
    watering_amount_in_mm: float = 0.0
    watering_interval: Optional[int] = None
    days_into_watering_interval: int = 0
    current_water_deficit: float = 0.0
    watering_occurs: bool = True
    manure_water: float = 0.0

    # --- Annual totals ---
    annual_irrigation_water_use_total: float = 0

    simulate_water_stress: bool = True
    simulate_temp_stress: bool = True
    simulate_nitrogen_stress: bool = True
    simulate_phosphorus_stress: bool = True

    def __post_init__(self) -> None:
        """
        Initialize all attributes in FieldData object that need to be set based on other FieldData attributes.

        Raises
        ------
        ValueError
            If the watering amount is < 0.
            If the watering interval is < 0.
        """
        self.dormancy_threshold = Dormancy.find_dormancy_threshold(self.absolute_latitude)
        self.dormancy_threshold_daylength = Dormancy.find_threshold_daylength(
            self.minimum_daylength, self.dormancy_threshold
        )

        should_water = (
            self.watering_amount_in_liters is not None
            and self.watering_interval is not None
            and self.watering_amount_in_liters != 0.0
            and self.watering_interval != 0
        )
        if should_water:
            if self.watering_amount_in_liters < 0.0:
                raise ValueError(f"Expected watering amount to be >= 0, received '{self.watering_amount_in_liters}'.")
            elif self.watering_interval < 0:
                raise ValueError(f"Expected watering interval to be >= 0, received '{self.watering_interval}'.")

            self.watering_amount_in_mm = self.convert_liters_to_millimeters(
                self.watering_amount_in_liters, self.field_size
            )
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
        amount_in_cubic_millimeters = liter_amount * GeneralConstants.LITERS_TO_CUBIC_MILLIMETERS
        field_size_in_square_millimeters = field_size * GeneralConstants.HECTARES_TO_SQUARE_MILLIMETERS
        return amount_in_cubic_millimeters / field_size_in_square_millimeters
