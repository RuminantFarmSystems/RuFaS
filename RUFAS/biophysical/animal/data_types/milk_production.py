from dataclasses import dataclass

from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents


@dataclass
class MilkProductionInputs:
    """
    Represents the input data related to milk production for an animal.

    Attributes
    ----------
    days_in_milk : int
        The number of days the animal has been in milk production, (simulation days).
    days_born : int
        The number of days since the animal was born, (simulation days).
    days_in_pregnancy : int
        The number of days the animal has been pregnant, (simulation days).

    """
    days_in_milk: int
    days_born: int
    days_in_pregnancy: int

    @property
    def is_milking(self) -> bool:
        """Returns True if the animal is currently milking, False otherwise."""
        return self.days_in_milk > 0


@dataclass
class MilkProductionOutputs:
    """
    Represents the outputs of milk production in an animal.

    Attributes
    ----------
    events : AnimalEvents
        Animal-related events associated with milk production.
    days_in_milk : int
        Number of days the animal has been in milk production, (simulation days).

    """
    events: AnimalEvents
    days_in_milk: int

    @property
    def is_milking(self) -> bool:
        """Returns True if the animal is currently milking, False otherwise."""
        return self.days_in_milk > 0
