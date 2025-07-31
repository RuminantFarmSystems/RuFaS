import pytest
from pytest import approx

from RUFAS.biophysical.animal.data_types.animal_manure_excretions import AnimalManureExcretions
from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.animal.manure.general_manure import calculate_phosphorus_excretion_values


@pytest.mark.skip(reason="Skipping this test as AnimalManureExcretions is modified")
def test_animal_manure_excretion_typed_dict() -> None:
    """Unit test for the AnimalManureExcretions TypedDict class in general_manure.py."""
    # Arrange
    urea = 1.0
    urine = 2.0
    manure_total_ammoniacal_nitrogen = 4.0
    urine_nitrogen = 4.0
    manure_nitrogen = 5.0
    manure_mass = 6.0
    total_solids = 7.0
    degradable_volatile_solids = 8.0
    non_degradable_volatile_solids = 9.0
    inorganic_phosphorus_fraction = 10.0
    organic_phosphorus_fraction = 11.0
    phosphorus = 12.0
    phosphorus_fraction = 13.0
    potassium = 14.0
    methane = 15.0

    # Act
    animal_manure_excretions = AnimalManureExcretions(
        urea=urea,
        urine=urine,
        manure_total_ammoniacal_nitrogen=manure_total_ammoniacal_nitrogen,
        urine_nitrogen=urine_nitrogen,
        manure_nitrogen=manure_nitrogen,
        manure_mass=manure_mass,
        total_solids=total_solids,
        degradable_volatile_solids=degradable_volatile_solids,
        non_degradable_volatile_solids=non_degradable_volatile_solids,
        inorganic_phosphorus_fraction=inorganic_phosphorus_fraction,
        organic_phosphorus_fraction=organic_phosphorus_fraction,
        phosphorus=phosphorus,
        phosphorus_fraction=phosphorus_fraction,
        potassium=potassium,
        methane=methane,
    )

    # Assert
    assert animal_manure_excretions["urea"] == approx(urea)
    assert animal_manure_excretions["urine"] == approx(urine)
    assert animal_manure_excretions["manure_total_ammoniacal_nitrogen"] == approx(manure_total_ammoniacal_nitrogen)
    assert animal_manure_excretions["urine_nitrogen"] == approx(urine_nitrogen)
    assert animal_manure_excretions["manure_nitrogen"] == approx(manure_nitrogen)
    assert animal_manure_excretions["manure_mass"] == approx(manure_mass)
    assert animal_manure_excretions["total_solids"] == approx(total_solids)
    assert animal_manure_excretions["degradable_volatile_solids"] == approx(degradable_volatile_solids)
    assert animal_manure_excretions["non_degradable_volatile_solids"] == approx(non_degradable_volatile_solids)
    assert animal_manure_excretions["inorganic_phosphorus_fraction"] == approx(inorganic_phosphorus_fraction)
    assert animal_manure_excretions["organic_phosphorus_fraction"] == approx(organic_phosphorus_fraction)
    assert animal_manure_excretions["phosphorus"] == approx(phosphorus)
    assert animal_manure_excretions["phosphorus_fraction"] == approx(phosphorus_fraction)
    assert animal_manure_excretions["potassium"] == approx(potassium)
    assert animal_manure_excretions["methane"] == approx(methane)


def test_calculate_phosphorus_excretion_values() -> None:
    """Unit test for the calculate_phosphorus_excretion_values function in general_manure.py."""
    # Arrange
    daily_milk_production = 1.0
    total_manure_excreted = 2.0
    fecal_phosphorus = 3.0
    urine_phosphorus_required = 4.0

    expected_manure_phosphorus_fraction = (fecal_phosphorus + urine_phosphorus_required) / (
        total_manure_excreted * GeneralConstants.KG_TO_GRAMS
    )
    expected_inorganic_phosphorus_fraction = 0.5 * expected_manure_phosphorus_fraction
    expected_organic_phosphorus_fraction = 0.05 * expected_manure_phosphorus_fraction
    expected_manure_phosphorus_excreted = fecal_phosphorus + urine_phosphorus_required
    expected_total_phosphorus_excreted = (
        fecal_phosphorus + urine_phosphorus_required + 0.0009 * daily_milk_production * GeneralConstants.KG_TO_GRAMS
    )

    # Act
    phosphorus_excretion_values = calculate_phosphorus_excretion_values(
        daily_milk_production=daily_milk_production,
        total_manure_excreted=total_manure_excreted,
        fecal_phosphorus=fecal_phosphorus,
        urine_phosphorus_required=urine_phosphorus_required,
    )
    (
        total_phosphorus_excreted,
        inorganic_phosphorus_fraction,
        organic_phosphorus_fraction,
        manure_phosphorus_excreted,
        manure_phosphorus_fraction,
    ) = phosphorus_excretion_values

    # Assert
    assert total_phosphorus_excreted == approx(expected_total_phosphorus_excreted)
    assert inorganic_phosphorus_fraction == approx(expected_inorganic_phosphorus_fraction)
    assert organic_phosphorus_fraction == approx(expected_organic_phosphorus_fraction)
    assert manure_phosphorus_excreted == approx(expected_manure_phosphorus_excreted)
    assert manure_phosphorus_fraction == approx(expected_manure_phosphorus_fraction)
