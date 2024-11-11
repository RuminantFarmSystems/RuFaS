from dataclasses import dataclass


@dataclass
class MilkProductionInputs:
    days_in_milk: int
    days_born: int
    days_in_pregnancy: int

    @property
    def is_milking(self) -> bool:
        return self.days_in_milk > 0