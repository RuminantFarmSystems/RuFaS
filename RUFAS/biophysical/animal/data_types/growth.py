from dataclasses import dataclass

from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType


@dataclass
class GrowthInputs:
    """
    Encapsulates growth-related input parameters needed for an animal to perform daily growth update routines.

    Attributes
    ----------
    days_in_pregnancy : int
        Number of days the animal has been pregnant, (simulation days).
    animal_type : AnimalType
        The type of animal.
    body_weight : float
        Current body weight of the animal, (kg).
    mature_body_weight : float
        Mature body weight of the animal, (kg).
    birth_weight : float
        Birth weight of the animal, (kg).
    days_born : int
        Number of days since the animal's birth, (simulation days).
    days_in_milk : int
        Total number of days the animal has been lactating, (simulation days).
    conceptus_weight : float
        Weight of the conceptus in the pregnant animal, (kg).
    gestation_length : int
        Total gestation period of the animal, (simulation days).
    calf_birth_weight : float
        Birth weight of the calf, (kg).
    calves : int
        Number of calves the animal has delivered, (unitless).
    calving_interval : float
        The interval between consecutive calving events, (simulation days).

    """

    days_in_pregnancy: int
    animal_type: AnimalType
    body_weight: float
    mature_body_weight: float
    birth_weight: float
    days_born: int
    days_in_milk: int

    conceptus_weight: float
    gestation_length: int
    calf_birth_weight: float
    calves: int
    calving_interval: float

    @property
    def is_pregnant(self) -> bool:
        """Returns True if the animal is pregnant, False otherwise."""
        return self.days_in_pregnancy > 0

    @property
    def is_milking(self) -> bool:
        """Returns True if the animal is milking, False otherwise."""
        return self.days_in_milk > 0


@dataclass
class GrowthOutputs:
    """
    Represents the growth outputs for an animal.

    Attributes
    ----------
    body_weight : float
        The body weight of the animal, (kg).
    conceptus_weight : float
        The weight of the conceptus, (kg).
    events : AnimalEvents
        An instance of `AnimalEvents` containing various lifecycle
        events associated with the animal.
    """

    body_weight: float
    conceptus_weight: float
    events: AnimalEvents
