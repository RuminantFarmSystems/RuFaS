from dataclasses import dataclass

from RUFAS.biophysical.animal.data_types.animal_enums import AnimalStatus
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import NewBornCalfValuesTypedDict


@dataclass
class DailyRoutinesOutput:
    """
    Representation of the output of daily routines in an animal management system.

    Attributes
    ----------
    animal_status : AnimalStatus
        The status of the animal after performing the daily routines. It determines
        whether the animal remains in the same state or any alteration occurs.
    newborn_calf_config : NewBornCalfValuesTypedDict or None
        Configuration data used to create a newborn calf if a calf was birthed during
        the daily routine. If no calf is born, the value is None.

    """

    animal_status: AnimalStatus = AnimalStatus.REMAIN
    newborn_calf_config: NewBornCalfValuesTypedDict | None = None
