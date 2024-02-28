from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from RUFAS.routines.manure.constants_and_units.datatype_with_unit import IntWithUnit, FloatWithUnit
from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import (
    LiquidManurePortionProtocol,
)


@dataclass
class ReceptionPitDailyOutput(LiquidManurePortionProtocol):
    """Daily output of a reception pit.

    Attributes:
        pen_id: ID of the pen that this output is associated with.
        simulation_day: Number of days into the simulation.
        manure_urea: Urea concentration in manure, g/L.
        liquid_manure_total_ammoniacal_nitrogen: Total ammoniacal nitrogen, kg.
        liquid_manure_nitrogen: Amount of nitrogen in manure, kg.
        liquid_manure_total_solids: Total amount of solids from the manure and the bedding, kg.
        manure_degradable_volatile_solids: Amount of degradable volatile solids, kg.
        manure_non_degradable_volatile_solids: Amount of non-degradable volatile solids, kg.
        liquid_manure_total_volatile_solids: Total amount of volatile solids, kg.
        liquid_manure_phosphorus: Amount of phosphorus excreted in manure, kg.
        liquid_manure_potassium: Amount of potassium in manure, kg.
        total_daily_manure_volume: Total amount of manure, bedding, and water combined, m^3.
        liquid_manure_daily_volume: Same as total_daily_manure_volume.
        Used for satisfying the LiquidManurePortionProtocol.

    """

    pen_id: IntWithUnit = -1
    pen_id.unit = "unitless"

    simulation_day: IntWithUnit = -1
    simulation_day.unit = "simulation days"

    manure_urea: FloatWithUnit = 0.0
    manure_urea.unit = "g/L"

    liquid_manure_total_ammoniacal_nitrogen: FloatWithUnit = 0.0
    liquid_manure_total_ammoniacal_nitrogen.unit = "kg"

    liquid_manure_nitrogen: FloatWithUnit = 0.0
    liquid_manure_nitrogen.unit = "kg"

    liquid_manure_total_solids: FloatWithUnit = 0.0
    liquid_manure_total_solids.unit = "kg"

    manure_degradable_volatile_solids: FloatWithUnit = 0.0
    manure_degradable_volatile_solids.unit = "kg"

    manure_non_degradable_volatile_solids: FloatWithUnit = 0.0
    manure_non_degradable_volatile_solids.unit = "kg"

    liquid_manure_total_volatile_solids: FloatWithUnit = 0.0
    liquid_manure_total_volatile_solids.unit = "kg"

    liquid_manure_phosphorus: FloatWithUnit = 0.0
    liquid_manure_phosphorus.unit = "kg"

    liquid_manure_potassium: FloatWithUnit = 0.0
    liquid_manure_potassium.unit = "kg"

    total_daily_manure_volume: FloatWithUnit = 0.0
    total_daily_manure_volume.unit = "m^3"

    # To satisfy the LiquidManurePortionProtocol
    liquid_manure_daily_volume: FloatWithUnit = field(init=False)
    liquid_manure_daily_volume.unit = "m^3"

    def __post_init__(self):
        """Ensures that the daily volume is set to the total daily manure volume."""
        self.liquid_manure_daily_volume = self.total_daily_manure_volume
