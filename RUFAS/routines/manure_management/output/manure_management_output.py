from dataclasses import dataclass


@dataclass
class ManureManagementOutput:
    tot_manure: float = 0.0
    tot_N: float = 0.0
    tot_P: float = 0.0
    tot_K: float = 0.0
    tot_DM: float = 0.0
    WIP: float = 0.0
    WOP: float = 0.0
