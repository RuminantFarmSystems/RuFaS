from typing import Optional

from RUFAS.data_structures.pen_manure_data import PenManureData


class ManureStream:
    def __init__(
        self,
        water: float,
        ammoniacal_nitrogen: float,
        nitrogen: float,
        phosphorus: float,
        potassium: float,
        ash: float,
        non_degradable_volatile_solids: float,
        degradable_volatile_solids: float,
        total_solid: float,
        pen_manure_data: Optional[PenManureData],
    ) -> None:
        self.water = water
        self.ammoniacal_nitrogen = ammoniacal_nitrogen
        self.nitrogen = nitrogen
        self.phosphorus = phosphorus
        self.potassium = potassium
        self.ash = ash
        self.non_degradable_volatile_solids = non_degradable_volatile_solids
        self.degradable_volatile_solids = degradable_volatile_solids
        self.total_solid = total_solid
        self.pen_manure_data = pen_manure_data

    @property
    def total_volatile_solids(self) -> float:
        return self.non_degradable_volatile_solids + self.degradable_volatile_solids

    @property
    def mass(self) -> float:
        return self.water + self.total_solid

    @property
    def volume(self) -> float:
        return 0  # TBD

    def reset_pen_manure_data(self) -> None:
        self.pen_manure_data = None
