from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from RUFAS.routines.manure.constants.manure_constants import ManureConstants
from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import LiquidManurePortionProtocol


@dataclass
class ManureSeparatorDailyOutput(LiquidManurePortionProtocol):
    """Daily output of a manure separator.

    Attributes:
        pen_id: ID of the pen that this output is associated with.
        simulation_day: Number of days into the simulation.
        total_daily_manure_volume: Total amount of manure, bedding, and water combined, m^3.
        final_solids_wet_mass: Total mass of the solids on wet-weight basis, kg.
        final_solids_wet_mass_volume: Total volume of the solids on wet-weight basis, m^3.

        TS_solid: Total amount of solids in the separated solids, kg.
        VS_solid: Total amount of volatile solids in the separated solids, kg.
        N_solid: Amount of nitrogen in the separated solids, kg.
        P_solid: Total amount of phosphorus in the separated solids, kg.
        K_solid: Total amount of potassium in the separated solids, kg.

        TS: Total amount of solids in the manure volume, kg.
        VS_total: Total amount of volatile solids in the manure volume, kg.
        N: Amount of nitrogen in the manure volume, kg.
        TAN: Total ammoniacal nitrogen in the manure volume, kg.
        P: Total amount of phosphorus in the manure volume, kg.
        K: Total amount of potassium in the manure volume, kg.

        final_daily_volume: Total manure volume after separation, m^3.

    """
    pen_id: int = -1
    simulation_day: int = -1
    total_daily_manure_volume: float = 0.0
    final_solids_wet_mass: float = 0.0
    final_solids_wet_mass_volume: float = field(init=False)

    TS_solid: float = 0.0
    VS_solid: float = 0.0
    N_solid: float = 0.0
    P_solid: float = 0.0
    K_solid: float = 0.0

    TS: float = 0.0
    VS_total: float = 0.0
    N: float = 0.0
    TAN: float = 0.0
    P: float = 0.0
    K: float = 0.0

    final_daily_volume: float = field(init=False)
    daily_volume: float = field(init=False)  # To satisfy the LiquidManurePortionProtocol

    def __post_init__(self):
        """Calculates the final daily volume and the final solids wet mass volume."""
        self.final_solids_wet_mass_volume = self.final_solids_wet_mass / ManureConstants.MANURE_SOLIDS_BEDDING_DENSITY
        self.final_daily_volume = self.total_daily_manure_volume - self.final_solids_wet_mass_volume
        self.daily_volume = self.final_daily_volume
