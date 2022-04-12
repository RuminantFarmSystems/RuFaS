from __future__ import annotations

from dataclasses import astuple, dataclass


@dataclass
class DailyVariables:
    CH4_emissions: float = 0.0
    TS: float = 0.0
    VS: float = 0.0
    N: float = 0.0
    P: float = 0.0
    K: float = 0.0
    TS_liquid: float = 0.0
    VS_liquid: float = 0.0
    N_liquid: float = 0.0
    P_liquid: float = 0.0
    K_liquid: float = 0.0
    TS_loss: float = 0.0
    VS_loss: float = 0.0
    TS_DM_effluent: float = 0.0
    other_solids: float = 0.0
    other_liquids: float = 0.0
    WIP: float = 0.0
    WOP: float = 0.0

    raw_manure: float = 0.0
    initial_manure: float = 0.0
    manure_calc: float = 0.0
    manure_delta: float = 0.0
    manure_management_balance_difference: float = 0.0
    manure_applied: float = 0.0
    N_applied: float = 0.0
    P_applied: float = 0.0

    def __add__(self, other: DailyVariables) -> DailyVariables:
        if not isinstance(other, DailyVariables):
            raise TypeError('Cannot add a non-DailyVariables object to a DailyVariables object.')
        return DailyVariables(*[
            attr1 + attr2 for attr1, attr2 in zip(astuple(self), astuple(other))
        ])
