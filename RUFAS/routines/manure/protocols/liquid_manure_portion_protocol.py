from typing import Protocol


class LiquidManurePortionProtocol(Protocol):
    """List of expected attributes for the liquid manure portion."""
    simulation_day: int
    pen_id: int
    liquid_manure_total_ammoniacal_nitrogen: float
    liquid_manure_nitrogen: float
    liquid_manure_total_solids: float
    liquid_manure_total_volatile_solids: float
    liquid_manure_phosphorus: float
    liquid_manure_potassium: float
    liquid_manure_daily_volume: float
