from dataclasses import dataclass

from RUFAS.biophysical.animal.data_types.animal_enums import AnimalStatus
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import NewBornCalfValuesTypedDict
from RUFAS.biophysical.animal.data_types.reproduction import HerdReproductionStatistics


@dataclass
class DailyRoutinesOutput:
    """
    Representation of the output of daily routines in an animal management system.

    Attributes
    ----------
    herd_reproduction_statistics : HerdReproductionStatistics
        A collection of statistical properties related to the animal's reproduction lifecycle.
    animal_status : AnimalStatus
        The status of the animal after performing the daily routines. It determines
        whether the animal remains in the same state or any alteration occurs.
    newborn_calf_config : NewBornCalfValuesTypedDict or None
        Configuration data used to create a newborn calf if a calf was birthed during
        the daily routine. If no calf is born, the value is None.
    daily_digestion_output: dict[AnimalType, dict[str, float]] | None = None
        The output from the daily digestion result with keys indicating the animal type and values
        contains the method-emission amount pair results.

    """

    herd_reproduction_statistics: HerdReproductionStatistics
    animal_status: AnimalStatus = AnimalStatus.REMAIN
    newborn_calf_config: NewBornCalfValuesTypedDict | None = None
