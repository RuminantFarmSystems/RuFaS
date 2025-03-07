from dataclasses import dataclass

from RUFAS.biophysical.animal.data_types.animal_enums import Breed
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import NewBornCalfValuesTypedDict
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType


@dataclass
class ReproductionInputs:
    animal_type: AnimalType
    body_weight: float
    breed: Breed
    days_born: int
    days_in_pregnancy: int
    days_in_milk: int
    net_merit: float
    phosphorus_for_gestation_required_for_calf: float

    @property
    def is_pregnant(self) -> bool:
        return self.days_in_pregnancy > 0

    @property
    def is_milking(self) -> bool:
        return self.days_in_milk > 0


@dataclass
class AnimalReproductionStatistics:
    """
    Animal-level reproduction-related statistical properties.

    Attributes
    ----------
     ED_days: int
        The number of days the animal has been in the ED program.
    estrus_count: int
        The number of estrus during the ED program.
    GnRH_injections: int
        The number of GnRH injections.
    PGF_injections: int
        The number of PGF injections.
    CIDR_injections: int
        The number of CIDR injections.
    semen_number: int
        number of straws of semen used
    AI_times: int
        The number of times that artificial injections are performed.
    breeding_to_pregnancy_time: int
        The number of days it takes for the animal to get pregnant from breeding start.
    pregnancy_diagnoses: int
        The number of pregnancy diagnoses.
    calving_to_pregnancy_time: int
        The time between calving to pregnant for a call in days.

    """

    ED_days: int = 0
    estrus_count: int = 0
    GnRH_injections: int = 0
    PGF_injections: int = 0
    CIDR_injections: int = 0
    semen_number: int = 0
    AI_times: int = 0
    breeding_to_pregnancy_time: int = 0
    pregnancy_diagnoses: int = 0
    calving_to_pregnancy_time: int = 0


@dataclass
class HerdReproductionStatistics:
    """
    Herd-level reproduction-related statistical properties.

    Attributes
    ----------
    num_ai_performed: int
        The number of times AI was performed across all heiferIIs.
    num_successful_conceptions: int
        The number of successful conceptions out of all AI performed.
    num_ai_performed_in_ED: int
        The number of times AI was performed in the ED protocol.
    num_successful_conceptions_in_ED: int
        The number of successful conceptions out of all AI performed in the ED.
    num_ai_performed_in_TAI: int
        The number of times AI was performed in the TAI protocol.
    num_successful_conceptions_in_TAI: int
        The number of successful conceptions out of all AI performed in the TAI.
    num_ai_performed_in_SynchED: int
        The number of times AI was performed in the SynchED protocol.
    num_successful_conceptions_in_SynchED: int
        The number of successful conceptions out of all AI performed in the SynchED.

    """

    num_ai_performed: int = 0
    num_ai_performed_in_ED: int = 0
    num_ai_performed_in_TAI: int = 0
    num_ai_performed_in_SynchED: int = 0
    num_successful_conceptions: int = 0
    num_successful_conceptions_in_ED: int = 0
    num_successful_conceptions_in_TAI: int = 0
    num_successful_conceptions_in_SynchED: int = 0


@dataclass
class ReproductionOutputs:
    body_weight: float
    days_in_milk: int
    days_in_pregnancy: int
    events: AnimalEvents
    phosphorus_for_gestation_required_for_calf: float

    animal_level_statistics: AnimalReproductionStatistics
    herd_level_statistics: HerdReproductionStatistics

    newborn_calf_config: NewBornCalfValuesTypedDict | None = None

    @property
    def is_pregnant(self) -> bool:
        return self.days_in_pregnancy > 0

    @property
    def is_milking(self) -> bool:
        return self.days_in_milk > 0


@dataclass
class ReproductionDataStream:
    animal_type: AnimalType
    body_weight: float
    breed: Breed
    days_born: int
    days_in_pregnancy: int
    days_in_milk: int
    events: AnimalEvents
    net_merit: float
    phosphorus_for_gestation_required_for_calf: float

    animal_level_statistics: AnimalReproductionStatistics
    herd_level_statistics: HerdReproductionStatistics

    newborn_calf_config: NewBornCalfValuesTypedDict | None = None

    @property
    def is_pregnant(self) -> bool:
        return self.days_in_pregnancy > 0

    @property
    def is_milking(self) -> bool:
        return self.days_in_milk > 0
