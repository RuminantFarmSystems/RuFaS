from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Optional

from RUFAS.routines.manure.constants_and_units.datatype_with_unit import FloatWithUnit, IntWithUnit
from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants
from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import (
    LiquidManurePortionProtocol,
)


@dataclass
class ManureSeparatorDailyOutput(LiquidManurePortionProtocol):
    """Daily output of a manure separator.

    Attributes:
        pen_id: ID of the pen that this output is associated with.
        simulation_day: Number of days into the simulation.
        total_daily_manure_volume: Total amount of manure, bedding, and water combined, m^3.
        final_solids_wet_mass: Total mass of the solids on wet-weight basis, kg.
        final_solids_wet_mass_volume: Total volume of the solids on wet-weight basis, m^3.

        solid_manure_total_solids: Total amount of solids in the separated solids, kg.
        solid_manure_total_volatile_solids: Total amount of volatile solids in the separated solids, kg.
        solid_manure_nitrogen: Amount of nitrogen in the separated solids, kg.
        solid_manure_phosphorus: Total amount of phosphorus in the separated solids, kg.
        solid_manure_potassium: Total amount of potassium in the separated solids, kg.

        liquid_manure_total_solids: Total amount of solids in the manure volume, kg.
        liquid_manure_total_volatile_solids: Total amount of volatile solids in the manure volume, kg.
        liquid_manure_nitrogen: Amount of nitrogen in the manure volume, kg.
        liquid_manure_total_ammoniacal_nitrogen: Total ammoniacal nitrogen in the manure volume, kg.
        liquid_manure_phosphorus: Total amount of phosphorus in the manure volume, kg.
        liquid_manure_potassium: Total amount of potassium in the manure volume, kg.

        final_daily_volume: Total manure volume after separation, m^3.
        liquid_manure_daily_volume: Same as final_daily_volume.
        Used for satisfying the LiquidManurePortionProtocol.

    """

    pen_id: IntWithUnit = IntWithUnit(-1, unit="unitless")
    simulation_day: IntWithUnit = IntWithUnit(-1, unit="simulation days")
    total_daily_manure_volume: FloatWithUnit = FloatWithUnit(0.0, unit="m^3")
    final_solids_wet_mass: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    final_solids_wet_mass_volume: Optional[FloatWithUnit] = FloatWithUnit(None, unit="m^3")

    solid_manure_total_solids: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    solid_manure_total_volatile_solids: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    solid_manure_nitrogen: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    solid_manure_phosphorus: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    solid_manure_potassium: FloatWithUnit = FloatWithUnit(0.0, unit="kg")

    liquid_manure_total_solids: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    liquid_manure_total_volatile_solids: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    liquid_manure_nitrogen: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    liquid_manure_total_ammoniacal_nitrogen: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    liquid_manure_phosphorus: FloatWithUnit = FloatWithUnit(0.0, unit="kg")
    liquid_manure_potassium: FloatWithUnit = FloatWithUnit(0.0, unit="kg")

    final_daily_volume: Optional[FloatWithUnit] = FloatWithUnit(None, unit="m^3")
    # To satisfy the LiquidManurePortionProtocol
    liquid_manure_daily_volume: Optional[FloatWithUnit] = FloatWithUnit(None, unit="m^3")

    def __post_init__(self):
        """Calculates the final daily volume and the final solids wet mass volume."""
        self.final_solids_wet_mass_volume = self.final_solids_wet_mass / ManureConstants.MANURE_SOLIDS_BEDDING_DENSITY
        self.final_daily_volume = self.total_daily_manure_volume - self.final_solids_wet_mass_volume
        self.liquid_manure_daily_volume = self.final_daily_volume
