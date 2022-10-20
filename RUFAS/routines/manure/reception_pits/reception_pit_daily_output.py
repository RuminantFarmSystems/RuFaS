from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ReceptionPitDailyOutput:
    """Daily output of a reception pit.

    Attributes
        simulation_day: Number of days into the simulation.
        pen_id: ID of the pen that this output is associated with.
        urea: Urea concentration in manure, g/L.
        TAN: Total ammonia nitrogen concentration, g/L.
        N: Amount of nitrogen in manure, kg.
        TS: Total amount of solids from the manure and the bedding, kg.
        VSd: Amount of degradable volatile solids, kg.
        VSnd: Amount of non-degradable volatile solids, kg.
        VS_total: Total amount of volatile solids, kg.
        P: Amount of phosphorus excreted in manure, kg.
        K: Amount of potassium in manure, kg.
        total_daily_manure_volume: Total amount of manure, bedding, and water combined, m^3.

    """
    simulation_day: int = -1
    pen_id: int = -1
    urea: float = 0.0
    TAN: float = 0.0
    N: float = 0.0
    TS: float = 0.0
    VSd: float = 0.0
    VSnd: float = 0.0
    VS_total: float = 0.0
    P: float = 0.0
    K: float = 0.0
    total_daily_manure_volume: float = 0.0
