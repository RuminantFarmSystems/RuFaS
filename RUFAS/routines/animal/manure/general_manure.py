from typing import Tuple
from RUFAS.general_constants import GeneralConstants
from ....data_structures.animal_manure_excretions import AnimalManureExcretions


def get_default_animal_manure_excretions() -> AnimalManureExcretions:
    """
    Get a default AnimalManureExcretions object.

    Returns
    -------
    AnimalManureExcretions
        Default AnimalManureExcretions object.

    """

    return AnimalManureExcretions(
        urea=0.0,
        urine=0.0,
        manure_total_ammoniacal_nitrogen=0.0,
        urine_nitrogen=0.0,
        manure_nitrogen=0.0,
        manure_mass=0.0,
        total_solids=0.0,
        degradable_volatile_solids=0.0,
        non_degradable_volatile_solids=0.0,
        inorganic_phosphorus_fraction=0.0,
        organic_phosphorus_fraction=0.0,
        non_water_inorganic_phosphorus_fraction=0.0,
        non_water_organic_phosphorus_fraction=0.0,
        phosphorus=0.0,
        phosphorus_fraction=0.0,
        potassium=0.0,
        enteric_methane_g=0.0,
    )


def add_animal_manure_excretions(
    first: AnimalManureExcretions, second: AnimalManureExcretions
) -> AnimalManureExcretions:
    """
    Add two AnimalManureExcretions objects together.

    Parameters
    ----------
    first : AnimalManureExcretions
        First AnimalManureExcretions object.
    second : AnimalManureExcretions
        Second AnimalManureExcretions object.

    Returns
    -------
    AnimalManureExcretions
        Sum of the two AnimalManureExcretions objects.

    """

    data = {}
    for key in first:
        data[key] = first[key] + second[key]
    return AnimalManureExcretions(**data)


def scalar_mult_animal_manure_excretions(manure: AnimalManureExcretions, scalar: float) -> AnimalManureExcretions:
    data = {}
    for key in manure:
        data[key] = manure[key] * scalar
    return AnimalManureExcretions(**data)


def calculate_phosphorus_excretion_values(
    daily_milk_production: float,
    total_manure_excreted: float,
    fecal_phosphorus: float,
    urine_phosphorus_required: float,
) -> Tuple[float, float, float, float, float]:
    """Calculates a set of phosphorus excretion values produced by a given animal.

    Parameters
    ----------
    daily_milk_production : float
        Amount of daily milk produced by the animal, kg.
        This parameter should be set to 0 if this function is called for a non-cow animal.
    total_manure_excreted : float
        Amount of manure excreted by the animal, kg.
    fecal_phosphorus : float
        Amount of fecal phosphorus excreted by the animal, g.
    urine_phosphorus_required : float
        Amount of phosphorus required for urine production, g.

    Returns
    -------
    float
        Total amount of phosphorus excreted by the animal, g.
    float
        Fraction of extractable inorganic phosphorus, unitless.
    float
        Fraction of water extractable organic phosphorus, unitless.
    float
        Amount of manure phosphorus excreted, g.
    float
        Fraction of phosphorus in the manure, unitless.

    """
    # P fraction of manure (A.3.A.1)
    if total_manure_excreted > 0:
        manure_phosphorus_fraction = (fecal_phosphorus + urine_phosphorus_required) / (
            total_manure_excreted * GeneralConstants.KG_TO_GRAMS
        )
    else:
        manure_phosphorus_fraction = 0.0

    # Water extractable Inorganic P (WIP) fraction - fraction of manure
    # compromised of inorganic water extractable P [A.3.A.2]
    inorganic_phosphorus_fraction = 0.50 * manure_phosphorus_fraction

    # Water extractable Organic P (WOP) fraction - fraction of maure
    # comprised of organic water extractable P [A.3.A.3]
    organic_phosphorus_fraction = 0.05 * manure_phosphorus_fraction

    # amount of P in milk per animal (g) [A.3E.B.1]
    phosphorus_in_milk = 0.0009 * daily_milk_production * GeneralConstants.KG_TO_GRAMS

    # manure P excretion for manure module input (g) [A.3.B.2]
    manure_phosphorus_excreted = fecal_phosphorus + urine_phosphorus_required

    # amount of P excreted by an animal (g) [A.3.B.3]
    total_phosphorus_excreted = phosphorus_in_milk + fecal_phosphorus + urine_phosphorus_required

    return (
        total_phosphorus_excreted,
        inorganic_phosphorus_fraction,
        organic_phosphorus_fraction,
        manure_phosphorus_excreted,
        manure_phosphorus_fraction,
    )
