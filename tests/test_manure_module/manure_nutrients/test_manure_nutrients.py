from __future__ import annotations

import pytest
from pytest import approx, mark

from RUFAS.routines.manure.manure_nutrients.manure_nutrients import ManureNutrients


@mark.parametrize(
    "nitrogen, phosphorus, potassium, dry_matter, total_manure_mass, "
    "expected_dry_matter_fraction, expected_nitrogen_composition, expected_phosphorus_composition",
    [
        (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),  # All attributes are zero
        (1.0, 2.0, 3.0, 4.0, 5.0, 4.0 / 5.0, 1.0 / 5.0, 2.0 / 5.0),  # All attributes have some values
    ]
)
def test_manure_nutrients_init(nitrogen, phosphorus, potassium, dry_matter, total_manure_mass,
                               expected_dry_matter_fraction, expected_nitrogen_composition,
                               expected_phosphorus_composition):
    """
    Unit test for the ManureNutrients class in manure_nutrients.py.

    Test the initialization of the ManureNutrients dataclass and properties that compute manure composition.

    """
    # Act
    nutrients = ManureNutrients(
        nitrogen=nitrogen,
        phosphorus=phosphorus,
        potassium=potassium,
        dry_matter=dry_matter,
        total_manure_mass=total_manure_mass,
    )

    # Assert
    assert nutrients.nitrogen == approx(nitrogen)
    assert nutrients.phosphorus == approx(phosphorus)
    assert nutrients.potassium == approx(potassium)
    assert nutrients.dry_matter == approx(dry_matter)
    assert nutrients.total_manure_mass == approx(total_manure_mass)
    assert nutrients.dry_matter_fraction == approx(expected_dry_matter_fraction)
    assert nutrients.nitrogen_composition == approx(expected_nitrogen_composition)
    assert nutrients.phosphorus_composition == approx(expected_phosphorus_composition)


@pytest.mark.parametrize(
    "nutrient_values",
    [
        {"nitrogen": -1.0, "phosphorus": 2.0, "potassium": 3.0, "dry_matter": 4.0, "total_manure_mass": 5.0},
        {"nitrogen": 1.0, "phosphorus": -2.0, "potassium": 3.0, "dry_matter": 4.0, "total_manure_mass": 5.0},
        {"nitrogen": 1.0, "phosphorus": 2.0, "potassium": -3.0, "dry_matter": 4.0, "total_manure_mass": 5.0},
        {"nitrogen": 1.0, "phosphorus": 2.0, "potassium": 3.0, "dry_matter": -4.0, "total_manure_mass": 5.0},
        {"nitrogen": 1.0, "phosphorus": 2.0, "potassium": 3.0, "dry_matter": 4.0, "total_manure_mass": -5.0},
    ],
)
def test_manure_nutrients_invalid_init(nutrient_values: dict[str, float]):
    """
    Unit test for the __post_init__ method in the ManureNutrients class in manure_nutrients.py.

    Test the validation in the initialization of the ManureNutrients class,
    expecting it to raise an error when any of the attributes are negative.

    """
    with pytest.raises(ValueError):
        ManureNutrients(**nutrient_values)


def test_manure_nutrients_add_subtract():
    """
    Unit test for the addition and subtraction operations (__add__, __sub__)
    in the ManureNutrients class in manure_nutrients.py.

    Test the results of these operations on two ManureNutrients instances.

    """
    # Arrange
    nutrients = ManureNutrients(
        nitrogen=1.0,
        phosphorus=2.0,
        potassium=3.0,
        dry_matter=4.0,
        total_manure_mass=5.0,
    )

    nutrients2 = ManureNutrients(
        nitrogen=2.0,
        phosphorus=3.0,
        potassium=4.0,
        dry_matter=5.0,
        total_manure_mass=6.0,
    )

    # Act
    nutrients_added = nutrients + nutrients2
    nutrients_subtracted = nutrients2 - nutrients

    # Assert
    assert nutrients_added.nitrogen == pytest.approx(3.0)
    assert nutrients_added.phosphorus == pytest.approx(5.0)
    assert nutrients_added.potassium == pytest.approx(7.0)
    assert nutrients_added.dry_matter == pytest.approx(9.0)
    assert nutrients_added.total_manure_mass == pytest.approx(11.0)

    assert nutrients_subtracted.nitrogen == pytest.approx(1.0)
    assert nutrients_subtracted.phosphorus == pytest.approx(1.0)
    assert nutrients_subtracted.potassium == pytest.approx(1.0)
    assert nutrients_subtracted.dry_matter == pytest.approx(1.0)
    assert nutrients_subtracted.total_manure_mass == pytest.approx(1.0)


@pytest.mark.parametrize("multiplier", [0, 2, 3.5, 1e10, -1])
def test_manure_nutrients_multiplication(multiplier: int | float):
    """
    Unit test for the arithmetic operations (__mul__, __rmul__)
    in the ManureNutrients class in manure_nutrients.py.

    Test the result of these operations with various multipliers,
    including edge values such as 0, large numbers, and negative numbers.

    """
    # Arrange
    nutrients = ManureNutrients(
        nitrogen=1.0,
        phosphorus=2.0,
        potassium=3.0,
        dry_matter=4.0,
        total_manure_mass=5.0,
    )

    # Act and Assert
    if multiplier >= 0:
        nutrients_multiplied = nutrients * multiplier
        nutrients_multiplied_2 = multiplier * nutrients

        assert nutrients_multiplied.nitrogen == pytest.approx(1.0 * multiplier)
        assert nutrients_multiplied.phosphorus == pytest.approx(2.0 * multiplier)
        assert nutrients_multiplied.potassium == pytest.approx(3.0 * multiplier)
        assert nutrients_multiplied.dry_matter == pytest.approx(4.0 * multiplier)
        assert nutrients_multiplied.total_manure_mass == pytest.approx(5.0 * multiplier)

        assert nutrients_multiplied_2.nitrogen == pytest.approx(1.0 * multiplier)
        assert nutrients_multiplied_2.phosphorus == pytest.approx(2.0 * multiplier)
        assert nutrients_multiplied_2.potassium == pytest.approx(3.0 * multiplier)
        assert nutrients_multiplied_2.dry_matter == pytest.approx(4.0 * multiplier)
        assert nutrients_multiplied_2.total_manure_mass == pytest.approx(5.0 * multiplier)
    else:
        with pytest.raises(ValueError):
            nutrients * multiplier

        with pytest.raises(ValueError):
            multiplier * nutrients
