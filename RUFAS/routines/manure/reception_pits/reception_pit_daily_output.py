from __future__ import annotations

from dataclasses import dataclass, field

from RUFAS.units import MeasurementUnits
from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import (
    LiquidManurePortionProtocol,
)


@dataclass
class ReceptionPitDailyOutput(LiquidManurePortionProtocol):
    """Daily output of a reception pit.

    Attribute
    ---------
    pen_id: int
        ID of the pen that this output is associated with.
    pen_id_unit: MeasurementUnits
        Unit for pen_id.
    simulation_day: int
        Number of days into the simulation.
    simulation_day_unit: MeasurementUnits
        Unit for simulation_day.
    manure_urea: float
        Urea concentration in manure, g/L.
    manure_urea_unit: MeasurementUnits
        Unit for manure_urea.
    liquid_manure_total_ammoniacal_nitrogen: float
        Total ammoniacal nitrogen, kg.
    liquid_manure_total_ammoniacal_nitrogen_unit: MeasurementUnits
        Unit for liquid_manure_total_ammoniacal_nitrogen.
    liquid_manure_nitrogen: float
        Amount of nitrogen in manure, kg.
    liquid_manure_nitrogen_unit: MeasurementUnits
        Unit for liquid_manure_nitrogen.
    liquid_manure_total_solids: float
        Total amount of solids from the manure and the bedding, kg.
    liquid_manure_total_solids_unit: MeasurementUnits
        Unit for liquid_manure_total_solids.
    liquid_manure_total_degradable_volatile_solids: float
        Total amount of degradable solids from the manure and the bedding, kg.
    liquid_manure_total_degradable_volatile_solids_unit: MeasurementUnits
        Unit for liquid_manure_total_degradable_volatile_solids
    liquid_manure_total_non_degradable_volatile_solids: float
        Total amount of non-degradable solids from the manure and the bedding, kg.
    liquid_manure_total_non_degradable_volatile_solids_unit: MeasurementUnits
        Unit for liquid_manure_total_non_degradable_volatile_solids
    manure_degradable_volatile_solids: float
        Amount of degradable volatile solids, kg.
    manure_degradable_volatile_solids_unit: MeasurementUnits
        Unit for manure_degradable_volatile_solids.
    manure_non_degradable_volatile_solids: float
        Amount of non-degradable volatile solids, kg.
    manure_non_degradable_volatile_solids_unit: MeasurementUnits
        Unit for manure_non_degradable_volatile_solids.
    liquid_manure_total_volatile_solids: float
        Total amount of volatile solids, kg.
    liquid_manure_total_volatile_solids_unit: MeasurementUnits
        Unit for liquid_manure_total_volatile_solids.
    liquid_manure_phosphorus: float
        Amount of phosphorus excreted in manure, kg.
    liquid_manure_phosphorus_unit: MeasurementUnits
        Unit for liquid_manure_phosphorus.
    liquid_manure_potassium: float
        Amount of potassium in manure, kg.
    liquid_manure_potassium_unit: MeasurementUnits
        Unit for liquid_manure_potassium.
    total_daily_manure_volume: float
        Total amount of manure, bedding, and water combined, m^3.
    total_daily_manure_volume_unit: MeasurementUnits
        Unit for total_daily_manure_volume.
    liquid_manure_daily_volume: float
        Same as total_daily_manure_volume. Used for satisfying the LiquidManurePortionProtocol.
    liquid_manure_daily_volume_unit: MeasurementUnits
        Unit for liquid_manure_daily_volume.

    """

    pen_id: int = -1
    pen_id_unit: MeasurementUnits = MeasurementUnits.UNITLESS

    simulation_day: int = -1
    simulation_day_unit: MeasurementUnits = MeasurementUnits.SIMULATION_DAY

    manure_urea: float = 0.0
    manure_urea_unit: MeasurementUnits = MeasurementUnits.GRAMS_PER_LITER

    liquid_manure_total_ammoniacal_nitrogen: float = 0.0
    liquid_manure_total_ammoniacal_nitrogen_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    liquid_manure_nitrogen: float = 0.0
    liquid_manure_nitrogen_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    liquid_manure_total_solids: float = 0.0
    liquid_manure_total_solids_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    liquid_manure_total_degradable_volatile_solids: float = 0.0
    liquid_manure_total_degradable_volatile_solids_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    liquid_manure_total_non_degradable_volatile_solids: float = 0.0
    liquid_manure_total_non_degradable_volatile_solids_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    liquid_manure_total_volatile_solids: float = 0.0
    liquid_manure_total_volatile_solids_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    liquid_manure_phosphorus: float = 0.0
    liquid_manure_phosphorus_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    liquid_manure_potassium: float = 0.0
    liquid_manure_potassium_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    total_daily_manure_volume: float = 0.0
    total_daily_manure_volume_unit: MeasurementUnits = MeasurementUnits.CUBIC_METERS

    # To satisfy the LiquidManurePortionProtocol
    liquid_manure_daily_volume: float = field(init=False)
    liquid_manure_daily_volume_unit: MeasurementUnits = MeasurementUnits.CUBIC_METERS

    def __post_init__(self) -> None:
        """Ensures that the daily volume is set to the total daily manure volume."""
        self.liquid_manure_daily_volume = self.total_daily_manure_volume
