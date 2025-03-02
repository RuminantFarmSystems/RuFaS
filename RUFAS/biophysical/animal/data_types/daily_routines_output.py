from dataclasses import dataclass

from RUFAS.biophysical.animal.data_types.animal_enums import AnimalStatus
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import NewBornCalfValuesTypedDict


@dataclass
class DailyRoutinesOutput:
    animal_status: AnimalStatus = AnimalStatus.REMAIN
    newborn_calf_config: NewBornCalfValuesTypedDict | None = None
