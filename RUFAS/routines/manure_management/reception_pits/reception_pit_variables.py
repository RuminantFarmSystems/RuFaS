from dataclasses import dataclass


@dataclass
class ReceptionPitVariables:
    TS: float = 0.0
    VS: float = 0.0

    N: float = 0.0
    P: float = 0.0
    K: float = 0.0
    CH4: float = 0.0
    WIP: float = 0.0
    WOP: float = 0.0

    flush_water_volume: float = 0.0
