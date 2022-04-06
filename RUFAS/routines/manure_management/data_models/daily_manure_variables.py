from __future__ import annotations

from dataclasses import dataclass, astuple


@dataclass
class DailyManureVariables:
    raw_manure: float = 0.0
    initial_manure: float = 0.0
    manure_calc: float = 0.0
    manure_delta: float = 0.0
    manure_management_balance_difference: float = 0.0
    manure_applied: float = 0.0
    N_applied: float = 0.0
    P_applied: float = 0.0

    def __add__(self, other: DailyManureVariables) -> DailyManureVariables:
        if not isinstance(other, DailyManureVariables):
            raise TypeError('Cannot add a non-DailyManureVariables object to a DailyManureVariables object.')
        return DailyManureVariables(*[
            attr1 + attr2 for attr1, attr2 in zip(astuple(self), astuple(other))
        ])
