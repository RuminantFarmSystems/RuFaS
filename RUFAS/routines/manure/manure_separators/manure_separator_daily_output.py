from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass
class ManureSeparatorDailyOutput:
    """Daily output of a manure separator.

    Attributes:
        simulation_day: Number of days into the simulation.
        pen_id: ID of the pen that this output is associated with.
        TAN: Total ammonia nitrogen concentration, g/L.
        N: Amount of nitrogen in manure, kg.
        TS: Total amount of solids from the manure and the bedding, kg.
        VS_total: Total amount of volatile solids, kg.
        P: Amount of phosphorus excreted in manure, kg.
        K: Amount of potassium in manure, kg.
        total_daily_manure_volume: Total amount of manure, bedding, and water combined, m^3.
        final_solids_wet_mass: Total mass of the solids on wet-weight basis, kg.
        final_solids_dry_mass: Total mass of the solids on dry-weight basis, kg.

        TS_solid: Total amount of solids in the separated solids, kg.
        VS_solid: Total amount of volatile solids in the separated solids, kg.
        N_solid: Amount of nitrogen in the separated solids, kg.
        P_solid: Total amount of phosphorus in the separated solids, kg.
        K_solid: Total amount of potassium in the separated solids, kg.

        TS_liquid: Total amount of solids in the manure volume, kg.
        VS_liquid: Total amount of volatile solids in the manure volume, kg.
        N_liquid: Amount of nitrogen in the manure volume, kg.
        TAN_liquid: Total ammonia nitrogen concentration in the manure volume, g/L.
        P_liquid: Total amount of phosphorus in the manure volume, kg.
        K_liquid: Total amount of potassium in the manure volume, kg.

        TS_DM_effluent:
        final_daily_volume:

    """
    simulation_day: int = -1
    pen_id: int = -1
    TAN: float = 0.0  # g/L
    N: float = 0.0  # kg
    TS: float = 0.0  # kg
    VS_total: float = 0.0  # kg
    P: float = 0.0  # kg
    K: float = 0.0  # kg
    total_daily_manure_volume: float = 0.0  # m^3
    final_solids_wet_mass: float = 0.0
    final_solids_dry_mass: float = 0.0

    TS_solid: float = 0.0
    VS_solid: float = 0.0
    N_solid: float = 0.0
    P_solid: float = 0.0
    K_solid: float = 0.0

    TS_liquid: float = 0.0
    VS_liquid: float = 0.0
    N_liquid: float = 0.0
    TAN_liquid: float = 0.0
    P_liquid: float = 0.0
    K_liquid: float = 0.0

    TS_DM_effluent: float = 0.0
    final_daily_volume: float = field(init=False)

    def __post_init__(self):
        self.final_daily_volume = self.total_daily_manure_volume - self.final_solids_wet_mass
