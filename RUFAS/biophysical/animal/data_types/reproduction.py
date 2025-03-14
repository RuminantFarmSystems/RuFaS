from dataclasses import dataclass

from RUFAS.biophysical.animal.data_types.animal_enums import Breed
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import NewBornCalfValuesTypedDict
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType


@dataclass
class ReproductionInputs:
    """
    This class serves as a data container for encapsulating reproduction-related inputs.

    Attributes
    ----------
    animal_type : AnimalType
        The type of animal.
    body_weight : float
        The body weight of the animal, (kg).
    breed : Breed
        The breed of the animal.
    days_born : int
        The number of days since the animal was born, (simulation days).
    days_in_pregnancy : int
        The number of days the animal has been in pregnancy, (simulation days).
    days_in_milk : int
        The number of days the animal has been lactating, (simulation days).
    net_merit : float
        The genetic merit score of the animal, (lifetime USD).
    phosphorus_for_gestation_required_for_calf : float
        The amount of phosphorus required for fetal development during the
        gestation period in the animal.
    """

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
        """Returns True if the animal is pregnant, False otherwise."""
        return self.days_in_pregnancy > 0

    @property
    def is_milking(self) -> bool:
        """Returns True if the animal is milking, False otherwise."""
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
    pregnancy_diagnoses: int = 0
    calving_to_pregnancy_time: int = 0

    def reset_daily_statistics(self) -> None:
        self.GnRH_injections = 0
        self.PGF_injections = 0
        self.CIDR_injections = 0
        self.semen_number = 0
        self.AI_times = 0
        self.pregnancy_diagnoses = 0


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

    total_num_ai_performed: int = 0
    total_num_successful_conceptions: int = 0

    heifer_num_ai_performed: int = 0
    heifer_num_ai_performed_in_ED: int = 0
    heifer_num_ai_performed_in_TAI: int = 0
    heifer_num_ai_performed_in_SynchED: int = 0
    heifer_num_successful_conceptions: int = 0
    heifer_num_successful_conceptions_in_ED: int = 0
    heifer_num_successful_conceptions_in_TAI: int = 0
    heifer_num_successful_conceptions_in_SynchED: int = 0

    cow_num_ai_performed: int = 0
    cow_num_ai_performed_in_ED: int = 0
    cow_num_ai_performed_in_TAI: int = 0
    cow_num_ai_performed_in_ED_TAI: int = 0
    cow_num_successful_conceptions: int = 0
    cow_num_successful_conceptions_in_ED: int = 0
    cow_num_successful_conceptions_in_TAI: int = 0
    cow_num_successful_conceptions_in_ED_TAI: int = 0

    @property
    def overall_conception_rate(self) -> float:
        """Returns the overall conception rate across all animals in the herd."""
        return (
            self.total_num_successful_conceptions / self.total_num_ai_performed
            if self.total_num_ai_performed > 0
            else 0.0
        )

    @property
    def heifer_conception_rate(self) -> float:
        """Returns the conception rate for heifers in the herd."""
        return (
            self.heifer_num_successful_conceptions / self.heifer_num_ai_performed
            if self.heifer_num_ai_performed > 0
            else 0.0
        )

    @property
    def cow_conception_rate(self) -> float:
        """Returns the conception rate for cows in the herd."""
        return self.cow_num_successful_conceptions / self.cow_num_ai_performed if self.cow_num_ai_performed > 0 else 0.0

    @property
    def heifer_ED_conception_rate(self) -> float:
        """Returns the conception rate for heifers in the herd in the ED protocol."""
        return (
            self.heifer_num_successful_conceptions_in_ED / self.heifer_num_ai_performed_in_ED
            if self.heifer_num_ai_performed_in_ED > 0
            else 0.0
        )

    @property
    def heifer_TAI_conception_rate(self) -> float:
        """Returns the conception rate for heifers in the herd in the TAI protocol."""
        return (
            self.heifer_num_successful_conceptions_in_TAI / self.heifer_num_ai_performed_in_TAI
            if self.heifer_num_ai_performed_in_TAI > 0
            else 0.0
        )

    @property
    def heifer_SynchED_conception_rate(self) -> float:
        """Returns the conception rate for heifers in the herd in the SynchED protocol."""
        return (
            self.heifer_num_successful_conceptions_in_SynchED / self.heifer_num_ai_performed_in_SynchED
            if self.heifer_num_ai_performed_in_SynchED > 0
            else 0.0
        )

    def __add__(self, other: "HerdReproductionStatistics") -> "HerdReproductionStatistics":
        return HerdReproductionStatistics(
            total_num_ai_performed=self.total_num_ai_performed + other.total_num_ai_performed,
            total_num_successful_conceptions=(
                self.total_num_successful_conceptions + other.total_num_successful_conceptions
            ),
            heifer_num_ai_performed=self.heifer_num_ai_performed + other.heifer_num_ai_performed,
            heifer_num_ai_performed_in_ED=self.heifer_num_ai_performed_in_ED + other.heifer_num_ai_performed_in_ED,
            heifer_num_ai_performed_in_TAI=self.heifer_num_ai_performed_in_TAI + other.heifer_num_ai_performed_in_TAI,
            heifer_num_ai_performed_in_SynchED=(
                self.heifer_num_ai_performed_in_SynchED + other.heifer_num_ai_performed_in_SynchED
            ),
            heifer_num_successful_conceptions=(
                self.heifer_num_successful_conceptions + other.heifer_num_successful_conceptions
            ),
            heifer_num_successful_conceptions_in_ED=(
                self.heifer_num_successful_conceptions_in_ED + other.heifer_num_successful_conceptions_in_ED
            ),
            heifer_num_successful_conceptions_in_TAI=(
                self.heifer_num_successful_conceptions_in_TAI + other.heifer_num_successful_conceptions_in_TAI
            ),
            heifer_num_successful_conceptions_in_SynchED=(
                self.heifer_num_successful_conceptions_in_SynchED + other.heifer_num_successful_conceptions_in_SynchED
            ),
            cow_num_ai_performed=self.cow_num_ai_performed + other.cow_num_ai_performed,
            cow_num_successful_conceptions=self.cow_num_successful_conceptions + other.cow_num_successful_conceptions,
        )


@dataclass
class ReproductionOutputs:
    """
    Representation of reproduction-related outputs for an animal.

    Attributes
    ----------
    body_weight : float
        Weight of the animal, (kg).
    days_in_milk : int
        Number of days the animal has been producing milk, (simulation days).
    days_in_pregnancy : int
        Number of days into the pregnancy of the animal, (simulation days).
    events : AnimalEvents
        Instance of events related to the animal's reproduction lifecycle.
    phosphorus_for_gestation_required_for_calf : float
        Amount of phosphorus required for gestation to support calf development, (kg).
    herd_reproduction_statistics : HerdReproductionStatistics
        A collection of statistical properties related to the animal's reproduction lifecycle.
    newborn_calf_config : NewBornCalfValuesTypedDict or None
        Configuration related to the newborn calf, if applicable.

    """

    body_weight: float
    days_in_milk: int
    days_in_pregnancy: int
    events: AnimalEvents
    phosphorus_for_gestation_required_for_calf: float

    herd_reproduction_statistics: HerdReproductionStatistics
    newborn_calf_config: NewBornCalfValuesTypedDict | None = None

    @property
    def is_pregnant(self) -> bool:
        """Returns True if the animal is pregnant, False otherwise."""
        return self.days_in_pregnancy > 0

    @property
    def is_milking(self) -> bool:
        """Returns True if the animal is milking, False otherwise."""
        return self.days_in_milk > 0


@dataclass
class ReproductionDataStream:
    """
    Represents a data stream for reproduction-related attributes and statistics of an animal.
    This object is passed around and updated throughout the reproduction daily updates.

    Attributes
    ----------
    animal_type : AnimalType
        Indicator of the type of the animal.
    body_weight : float
        The body weight of the animal, (kg).
    breed : Breed
        The breed classification of the animal.
    days_born : int
        Total number of days since the animal was born, (simulation days).
    days_in_pregnancy : int
        The current number of days the animal has been pregnant, (simulation days).
    days_in_milk : int
        The current number of days the animal has been milking, (simulation days).
    events : AnimalEvents
        Associated events relevant to the animal’s lifecycle and reproduction.
    net_merit : float
        Net merit value, representing the economic value of the animal, (lifetime USD).
    phosphorus_for_gestation_required_for_calf : float
        The phosphorus needed for gestation, specifically for the growth of the calf, (kg).
        individual animal.
    herd_reproduction_statistics : HerdReproductionStatistics
        A collection of statistical properties related to the animal's reproduction lifecycle.
    newborn_calf_config : NewBornCalfValuesTypedDict or None
        Configuration data for a newborn calf, if applicable. Defaults to None.

    """

    animal_type: AnimalType
    body_weight: float
    breed: Breed
    days_born: int
    days_in_pregnancy: int
    days_in_milk: int
    events: AnimalEvents
    net_merit: float
    phosphorus_for_gestation_required_for_calf: float

    herd_reproduction_statistics: HerdReproductionStatistics
    newborn_calf_config: NewBornCalfValuesTypedDict | None = None

    @property
    def is_pregnant(self) -> bool:
        return self.days_in_pregnancy > 0

    @property
    def is_milking(self) -> bool:
        return self.days_in_milk > 0
