from dataclasses import dataclass

from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.units import MeasurementUnits


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


@dataclass
class MilkProductionStatistics:
    """
    Represents the daily milk report containing the daily statistics of milk production.

    Attributes
    ----------
    cow_id : int
        The animal id of the cow.
    pen_id : int
        The pen id of the pen that the animal belongs in.
    days_in_milk : int
        The number of days the animal has been in milk production, (days).
    estimated_daily_milk_produced : float
        The estimated daily milk produced by the animal, (kg/day).
    milk_protein : float
        The daily protein content in the milk produced by the animal, (kg/day).
    milk_fat : float
        The daily fat content in the milk produced by the animal, (kg/day).
    milk_lactose : float
        The daily lactose content in the milk produced by the animal, (kg/day).
    parity : int
        The number of claves the cow has given birth, (unitless).
    days_born : int
        The number of days since the birth of the animal, (days).
    days_in_pregnancy : int
        The number of days since the animal has been pregnant, (days).
    animal_type : AnimalType
        The type of animal, (unitless).
    TBV_fat : float or None
        The True Breed Value for fat of the animal, (kg). Defaults to None.
    TBV_protein : float or None
        The True Breed Value for protein of the animal, (kg). Defaults to None.
    E_permanent_fat : float or None
        The Permanent Environment Effect for fat of the animal, (kg). Defaults to None.
    E_permanent_protein : float or None
        The Permanent Environment Effect for protein of the animal, (kg). Defaults to None.
    E_temporary_fat : float or None
        The Temporary Environment Effect for fat of the animal, (kg). Defaults to None.
    E_temporary_protein : float or None
        The Temporary Environment Effect for protein of the animal, (kg). Defaults to None.
    phenotype_fat : float or None
        The fat phenotype of the animal, (kg). Defaults to None.
    phenotype_protein : float or None
        The protein phenotype of the animal, (kg). Defaults to None.
    EBV_fat : float or None
        The Estimated Breeding Value for fat of the animal, (kg). Defaults to None.
    EBV_protein : float or None
        The Estimated Breeding Value for protein of the animal, (kg). Defaults to None.
    ranking_index : float or None
        The ranking index of the animal, (unitless). Defaults to None.
    """

    cow_id: int
    pen_id: int
    days_in_milk: int
    estimated_daily_milk_produced: float
    milk_protein: float
    milk_fat: float
    milk_lactose: float
    parity: int
    days_born: int
    days_in_pregnancy: int
    animal_type: AnimalType

    TBV_fat: float | None = None
    TBV_protein: float | None = None
    E_permanent_fat: float | None = None
    E_permanent_protein: float | None = None

    E_temporary_fat: float | None = None
    E_temporary_protein: float | None = None
    phenotype_fat: float | None = None
    phenotype_protein: float | None = None
    EBV_fat: float | None = None
    EBV_protein: float | None = None
    ranking_index: float | None = None

    UNITS = {
        "cow_id": MeasurementUnits.UNITLESS,
        "pen_id": MeasurementUnits.UNITLESS,
        "days_in_milk": MeasurementUnits.DAYS,
        "estimated_daily_milk_produced": MeasurementUnits.KILOGRAMS_PER_DAY,
        "milk_protein": MeasurementUnits.KILOGRAMS_PER_DAY,
        "milk_fat": MeasurementUnits.KILOGRAMS_PER_DAY,
        "milk_lactose": MeasurementUnits.KILOGRAMS_PER_DAY,
        "parity": MeasurementUnits.UNITLESS,
        "is_milking": MeasurementUnits.UNITLESS,
        "simulation_day": MeasurementUnits.SIMULATION_DAY,
        "days_born": MeasurementUnits.DAYS,
        "days_in_pregnancy": MeasurementUnits.DAYS,
        "animal_type": MeasurementUnits.UNITLESS,
        "TBV_fat": MeasurementUnits.KILOGRAMS,
        "TBV_protein": MeasurementUnits.KILOGRAMS,
        "E_permanent_fat": MeasurementUnits.KILOGRAMS,
        "E_permanent_protein": MeasurementUnits.KILOGRAMS,
        "E_temporary_fat": MeasurementUnits.KILOGRAMS,
        "E_temporary_protein": MeasurementUnits.KILOGRAMS,
        "phenotype_fat": MeasurementUnits.KILOGRAMS,
        "phenotype_protein": MeasurementUnits.KILOGRAMS,
        "EBV_fat": MeasurementUnits.KILOGRAMS,
        "EBV_protein": MeasurementUnits.KILOGRAMS,
        "ranking_index": MeasurementUnits.UNITLESS,
    }

    @property
    def is_milking(self) -> bool:
        """Returns True if the animal is currently milking, False otherwise."""
        return self.days_in_milk > 0
