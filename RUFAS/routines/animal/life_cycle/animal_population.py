from dataclasses import dataclass
from typing import List

from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII


@dataclass(kw_only=True)
class AnimalPopulation:
    calves: List[Calf]
    heiferIs: List[HeiferI]
    heiferIs: List[HeiferII]
    heiferIs: List[HeiferIII]
    cows: List[Cow]
    replacement: List[Cow]
