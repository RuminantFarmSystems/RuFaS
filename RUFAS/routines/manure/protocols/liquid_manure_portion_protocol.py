from typing import Protocol


class LiquidManurePortionProtocol(Protocol):
    """List of expected attributes for the liquid manure portion."""
    simulation_day: int
    pen_id: int
    TAN: float
    N: float
    TS: float
    VS_total: float
    P: float
    K: float
    daily_volume: float
