from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict

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

    pen_id: int = -1
    pen_id_unit: str = "unitless"

    simulation_day: int = -1
    simulation_day_unit: str = "simulation days"

    total_daily_manure_volume: float = 0.0
    total_daily_manure_volume_unit: str = "m^3"

    final_solids_wet_mass: float = 0.0
    final_solids_wet_mass_unit: str = "kg"

    final_solids_wet_mass_volume: Optional[float] = None
    final_solids_wet_mass_volume_unit: str = "m^3"

    solid_manure_total_solids: float = 0.0
    solid_manure_total_solids_unit: str = "kg"

    solid_manure_total_volatile_solids: float = 0.0
    solid_manure_total_volatile_solids_unit: str = "kg"

    solid_manure_nitrogen: float = 0.0
    solid_manure_nitrogen_unit: str = "kg"

    solid_manure_phosphorus: float = 0.0
    solid_manure_phosphorus_unit: str = "kg"

    solid_manure_potassium: float = 0.0
    solid_manure_potassium_unit: str = "kg"

    liquid_manure_total_solids: float = 0.0
    liquid_manure_total_solids_unit: str = "kg"

    liquid_manure_total_volatile_solids: float = 0.0
    liquid_manure_total_volatile_solids_unit: str = "kg"

    liquid_manure_nitrogen: float = 0.0
    liquid_manure_nitrogen_unit: str = "kg"

    liquid_manure_total_ammoniacal_nitrogen: float = 0.0
    liquid_manure_total_ammoniacal_nitrogen_unit: str = "kg"

    liquid_manure_phosphorus: float = 0.0
    liquid_manure_phosphorus_unit: str = "kg"

    liquid_manure_potassium: float = 0.0
    liquid_manure_potassium_unit: str = "kg"

    final_daily_volume: Optional[float] = None
    final_daily_volume_unit: str = "m^3"

    # To satisfy the LiquidManurePortionProtocol
    liquid_manure_daily_volume: Optional[float] = None
    liquid_manure_daily_volume_unit: str = "m^3"

    def __post_init__(self):
        """Calculates the final daily volume and the final solids wet mass volume."""
        self.final_solids_wet_mass_volume = self.final_solids_wet_mass / ManureConstants.MANURE_SOLIDS_BEDDING_DENSITY
        self.final_daily_volume = self.total_daily_manure_volume - self.final_solids_wet_mass_volume
        self.liquid_manure_daily_volume = self.final_daily_volume

    @property
    def units_dict(self) -> Dict[str, str]:
        return {
            k: v for unit in
            ({k: v} for (k, v) in self.__dict__.items() if k.endswith("_unit"))
            for (k, v) in unit.items()
        }
