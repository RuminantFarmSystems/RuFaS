from dataclasses import dataclass

from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents


@dataclass
class MilkProductionInputs:
    days_in_milk: int
    days_born: int
    days_in_pregnancy: int

    @property
    def is_milking(self) -> bool:
        return self.days_in_milk > 0


@dataclass
class MilkProductionOutputs:
    events: AnimalEvents
    days_in_milk: int

    @property
    def is_milking(self) -> bool:
        return self.days_in_milk > 0
