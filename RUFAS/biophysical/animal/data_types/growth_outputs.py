from dataclasses import dataclass

from RUFAS.routines.animal.life_cycle.animal_events import AnimalEvents


@dataclass
class GrowthOutputs:
    body_weight: float
    conceptus_weight: float
    events: AnimalEvents