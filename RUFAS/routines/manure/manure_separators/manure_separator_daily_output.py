from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass
class ManureSeparatorDailyOutput:
    """Daily output of a manure separator.
    """
    simulation_day: int = -1
    pen_id: int = -1
    TAN_s: float = 0.0  # g/L
    N_manure: float = 0.0  # kg
    TSd: float = 0.0  # kg
    VSd: float = 0.0  # kg
    VSnd: float = 0.0  # kg
    VS_total: float = 0.0  # kg
    p_excrt_manure: float = 0.0  # kg
    K_manure: float = 0.0  # kg
    total_daily_mass: float = 0.0  # L or kg
    wet_weight_of_final_solids: float = 0.0

    final_solids_dry_content: float = 0.0
    TS_solid: float = 0.0
    VS_solid: float = 0.0
    N_solid: float = 0.0
    TAN_solid: float = 0.0
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
        self.final_daily_volume = self.total_daily_mass - self.wet_weight_of_final_solids
