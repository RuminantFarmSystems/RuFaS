from typing import TypedDict

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType


class GeneticHistory(TypedDict):
    """
    A class to represent the genetic history of an individual animal on a farm.

    This class is used to track the genetic attributes of an animal over the course of a simulation.
    It contains information about the simulation day, the age of the animal in days, and its genetic attributes.

    Attributes
    ----------
    simulation_day : int
        The day of the simulation corresponding to the genetic record of the animal.
    id : int
        The unique identifier of the animal.
    days_born : int
        The number of days since the birth of the animal.
    animal_type : AnimalType
        The type of animal.
    days_in_milk : int
        The number of days the animal has been in milk production, (simulation days).
    days_in_pregnancy : int
        The number of days the animal has been pregnant, (simulation days).
    parity : int
        The number of times the animal has given birth.
    TBV_fat : float
        The True Breed Value for fat of the animal, (kg).
    TBV_protein : float
        The True Breed Value for protein of the animal, (kg).
    E_permanent_fat : float
        The Permanent Environment Effect for fat of the animal, (kg).
    E_permanent_protein : float
        The Permanent Environment Effect for protein of the animal, (kg).
    E_temporary_fat : float
        The Temporary Environment Effect for fat of the animal, (kg).
    E_temporary_protein : float
        The Temporary Environment Effect for protein of the animal, (kg).
    phenotype_fat : float
        The fat phenotype of the animal, (kg).
    phenotype_protein : float
        The protein phenotype of the animal, (kg).
    EBV_fat : float
        The Estimated Breeding Value for fat of the animal, (kg).
    EBV_protein : float
        The Estimated Breeding Value for protein of the animal, (kg).
    ranking_index : float
        The ranking index of the animal, (unitless).
    """

    simulation_day: int

    id: int
    days_born: int
    animal_type: AnimalType
    days_in_milk: int
    days_in_pregnancy: int
    parity: int

    TBV_fat: float
    TBV_protein: float
    E_permanent_fat: float
    E_permanent_protein: float

    E_temporary_fat: float
    E_temporary_protein: float
    phenotype_fat: float
    phenotype_protein: float
    EBV_fat: float
    EBV_protein: float
    ranking_index: float
