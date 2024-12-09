from dataclasses import dataclass
from typing import Any

from RUFAS.biophysical.animal.data_types.animal_enums import AnimalStatus


@dataclass
class DailyRoutinesOutput:
    animal_status: AnimalStatus
    animal_values: dict[str, Any]