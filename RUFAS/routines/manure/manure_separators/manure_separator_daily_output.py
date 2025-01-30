from __future__ import annotations

from dataclasses import dataclass, field

from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants
from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import LiquidManurePortionProtocol
from RUFAS.units import MeasurementUnits


@dataclass
class ManureSeparatorDailyOutput(LiquidManurePortionProtocol):
    """Daily output of a manure separator.

    Attribute
    ---------
    pen_id: int
        ID of the pen that this output is associated with.
    pen_id_unit: MeasurementUnits
        Unit for

    simulation_day: int
        Number of days into the simulation.
    simulation_day_unit: MeasurementUnits
        Unit for simulation_day
    total_daily_manure_volume: float
        Total amount of manure, bedding, and water combined, m^3.
    total_daily_manure_volume_unit: MeasurementUnits
        Unit for total_daily_manure_volume
    final_solids_wet_mass: float
        Total mass of the solids on wet-weight basis, kg.
    final_solids_wet_mass_unit: MeasurementUnits
        Unit for final_solids_wet_mass
    final_solids_wet_mass_volume: float
        Total volume of the solids on wet-weight basis, m^3.
    final_solids_wet_mass_volume_unit: MeasurementUnits
        Unit for final_solids_wet_mass_volume

    solid_manure_total_solids: float
        Total amount of solids in the separated solids, kg.
    solid_manure_total_solids_unit: MeasurementUnits
        Unit for solid_manure_total_solids
    solid_manure_total_volatile_solids: float
        Total amount of volatile solids in the separated solids, kg.
    solid_manure_total_volatile_solids_unit: MeasurementUnits
        Unit for solid_manure_total_volatile_solids
    solid_manure_nitrogen: float
        Amount of nitrogen in the separated solids, kg.
    solid_manure_nitrogen_unit: MeasurementUnits
        Unit for solid_manure_nitrogen
    solid_manure_phosphorus: float
        Total amount of phosphorus in the separated solids, kg.
    solid_manure_phosphorus_unit: MeasurementUnits
        Unit for solid_manure_phosphorus
    solid_manure_potassium: float
        Total amount of potassium in the separated solids, kg.
    solid_manure_potassium_unit: MeasurementUnits
        Unit for solid_manure_potassium

    liquid_manure_total_solids: float
        Total amount of solids in the manure volume, kg.
    liquid_manure_total_solids_unit: MeasurementUnits
        Unit for liquid_manure_total_solids
    liquid_manure_total_degradable_volatile_solids: float
        Total amount of degradable volatile solids in the manure volume, kg.
    liquid_manure_total_degradable_volatile_solids_unit: MeasurementUnits
        Unit for liquid_manure_total_degradable_volatile_solids
    liquid_manure_total_non_degradable_volatile_solids: float
        Total amount of non-degradable volatile solids in the manure volume, kg.
    liquid_manure_total_non_degradable_volatile_solids_unit: MeasurementUnits
        Unit for liquid_manure_total_non_degradable_volatile_solids
    liquid_manure_total_volatile_solids: float
        Total amount of volatile solids in the manure volume, kg.
    liquid_manure_total_volatile_solids_unit: MeasurementUnits
        Unit for liquid_manure_total_volatile_solids
    liquid_manure_nitrogen: float
        Amount of nitrogen in the manure volume, kg.
    liquid_manure_nitrogen_unit: MeasurementUnits
        Unit for liquid_manure_nitrogen
    liquid_manure_total_ammoniacal_nitrogen: float
        Total ammoniacal nitrogen in the manure volume, kg.
    liquid_manure_total_ammoniacal_nitrogen_unit: MeasurementUnits
        Unit for liquid_manure_total_ammoniacal_nitrogen
    liquid_manure_phosphorus: float
        Total amount of phosphorus in the manure volume, kg.
    liquid_manure_phosphorus_unit: MeasurementUnits
        Unit for liquid_manure_phosphorus
    liquid_manure_potassium: float
        Total amount of potassium in the manure volume, kg.
    liquid_manure_potassium_unit: MeasurementUnits
        Unit for liquid_manure_potassium

    final_daily_volume: float
        Total manure volume after separation, m^3.
    final_daily_volume_unit: MeasurementUnits
        Unit for final_daily_volume
    liquid_manure_daily_volume: float
        Same as final_daily_volume. Used for satisfying the LiquidManurePortionProtocol.
    liquid_manure_daily_volume_unit: MeasurementUnits
        Unit for liquid_manure_daily_volume

    """

    pen_id: int = -1
    pen_id_unit: MeasurementUnits = MeasurementUnits.UNITLESS

    simulation_day: int = -1
    simulation_day_unit: MeasurementUnits = MeasurementUnits.SIMULATION_DAY

    total_daily_manure_volume: float = 0.0
    total_daily_manure_volume_unit: MeasurementUnits = MeasurementUnits.CUBIC_METERS

    final_solids_wet_mass: float = 0.0
    final_solids_wet_mass_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    final_solids_wet_mass_volume: float = field(init=False)
    final_solids_wet_mass_volume_unit: MeasurementUnits = MeasurementUnits.CUBIC_METERS

    solid_manure_total_solids: float = 0.0
    solid_manure_total_solids_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    solid_manure_total_volatile_solids: float = 0.0
    solid_manure_total_volatile_solids_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    solid_manure_nitrogen: float = 0.0
    solid_manure_nitrogen_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    solid_manure_phosphorus: float = 0.0
    solid_manure_phosphorus_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    solid_manure_potassium: float = 0.0
    solid_manure_potassium_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    liquid_manure_total_solids: float = 0.0
    liquid_manure_total_solids_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    liquid_manure_total_degradable_volatile_solids: float = 0.0
    liquid_manure_total_degradable_volatile_solids_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    liquid_manure_total_non_degradable_volatile_solids: float = 0.0
    liquid_manure_total_non_degradable_volatile_solids_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    liquid_manure_total_volatile_solids: float = 0.0
    liquid_manure_total_volatile_solids_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    liquid_manure_nitrogen: float = 0.0
    liquid_manure_nitrogen_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    liquid_manure_total_ammoniacal_nitrogen: float = 0.0
    liquid_manure_total_ammoniacal_nitrogen_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    liquid_manure_phosphorus: float = 0.0
    liquid_manure_phosphorus_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    liquid_manure_potassium: float = 0.0
    liquid_manure_potassium_unit: MeasurementUnits = MeasurementUnits.KILOGRAMS

    final_daily_volume: float = field(init=False)
    final_daily_volume_unit: MeasurementUnits = MeasurementUnits.CUBIC_METERS

    # To satisfy the LiquidManurePortionProtocol
    liquid_manure_daily_volume: float = field(init=False)
    liquid_manure_daily_volume_unit: MeasurementUnits = MeasurementUnits.CUBIC_METERS

    def __post_init__(self) -> None:
        """Calculates the final daily volume and the final solids wet mass volume."""
        self.final_solids_wet_mass_volume = self.final_solids_wet_mass / ManureConstants.MANURE_SOLIDS_BEDDING_DENSITY
        self.final_daily_volume = self.total_daily_manure_volume - self.final_solids_wet_mass_volume
        self.liquid_manure_daily_volume = self.final_daily_volume
