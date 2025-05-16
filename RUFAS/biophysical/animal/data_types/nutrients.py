from dataclasses import dataclass

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType


@dataclass
class NutrientsInputs:
    """
    Represents input data related to an animal's daily nutrient updates

    Attributes
    ----------
    animal_type : AnimalType
        The type of animal.
    body_weight : float
        Current body weight of the animal, (kg).
    mature_body_weight : float
        Mature or expected adult body weight of the animal, (kg).
    daily_growth : float
        Average daily growth rate of the animal, (kg/day).
    days_in_pregnancy : int
        The number of days the animal has been pregnant, (simulation days).
    days_in_milk : int
        The number of days the animal has been in milk production, (simulation days).
    daily_milk_produced : float
        Amount of milk produced by the animal daily, (kg).

    """

    animal_type: AnimalType
    body_weight: float
    mature_body_weight: float
    daily_growth: float
    days_in_pregnancy: int
    days_in_milk: int
    daily_milk_produced: float

    @property
    def is_pregnant(self) -> bool:
        """Returns True if the animal is pregnant, False otherwise."""
        return self.days_in_pregnancy > 0

    @property
    def is_milking(self) -> bool:
        """Returns True if the animal is milking, False otherwise."""
        return self.days_in_milk > 0
