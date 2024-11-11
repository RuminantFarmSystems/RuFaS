from dataclasses import dataclass

from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents


@dataclass
class MilkProductionOutputs:
    events: AnimalEvents
    days_in_milk: int

    @property
    def is_milking(self) -> bool:
        return self.days_in_milk > 0
