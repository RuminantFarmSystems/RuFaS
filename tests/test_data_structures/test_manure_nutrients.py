from __future__ import annotations

import pytest
from pytest import approx, mark

from RUFAS.data_structures.manure_nutrients import ManureNutrients
from RUFAS.data_structures.manure_types import ManureType


@mark.parametrize(
    "manure_type, nitrogen, phosphorus, potassium, dry_matter, total_manure_mass, "
    "expected_dry_matter_fraction, expected_nitrogen_composition, expected_phosphorus_composition",
    [
        (
            ManureType.LIQUID,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
        ),  # All attributes are zero
        (
            ManureType.SOLID,
            1.0,
            2.0,
            3.0,
            4.0,
            5.0,
            4.0 / 5.0,
            1.0 / 5.0,
            2.0 / 5.0,
        ),  # All attributes have some values
    ],
)
def test_manure_nutrients_init(
    manure_type: ManureType,
    nitrogen: float,
    phosphorus: float,
    potassium: float,
    dry_matter: float,
    total_manure_mass: float,
    expected_dry_matter_fraction: float,
    expected_nitrogen_composition: float,
    expected_phosphorus_composition: float,
) -> None:
    """
    Unit test for the ManureNutrients class in manure_nutrients.py.

    Test the initialization of the ManureNutrients dataclass and properties that compute manure composition
    for each manure type.

    """
    # Act
    nutrients = ManureNutrients(
        nitrogen=nitrogen,
        phosphorus=phosphorus,
        potassium=potassium,
        dry_matter=dry_matter,
        total_manure_mass=total_manure_mass,
        manure_type=manure_type,
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
    "manure_type, nutrient_values",
    [
        (
            ManureType.LIQUID,
            {
                "nitrogen": -1.0,
                "phosphorus": 2.0,
                "potassium": 3.0,
                "dry_matter": 4.0,
                "total_manure_mass": 5.0,
            },
        ),
        (
            ManureType.LIQUID,
            {
                "nitrogen": 1.0,
                "phosphorus": -2.0,
                "potassium": 3.0,
                "dry_matter": 4.0,
                "total_manure_mass": 5.0,
            },
        ),
        (
            ManureType.LIQUID,
            {
                "nitrogen": 1.0,
                "phosphorus": 2.0,
                "potassium": -3.0,
                "dry_matter": 4.0,
                "total_manure_mass": 5.0,
            },
        ),
        (
            ManureType.SOLID,
            {
                "nitrogen": 1.0,
                "phosphorus": 2.0,
                "potassium": 3.0,
                "dry_matter": -4.0,
                "total_manure_mass": 5.0,
            },
        ),
        (
            ManureType.SOLID,
            {
                "nitrogen": 1.0,
                "phosphorus": 2.0,
                "potassium": 3.0,
                "dry_matter": 4.0,
                "total_manure_mass": -5.0,
            },
        ),
        (
            "",
            {
                "nitrogen": 1.0,
                "phosphorus": 2.0,
                "potassium": 3.0,
                "dry_matter": 4.0,
                "total_manure_mass": 5.0,
            },
        ),
    ],
)
def test_manure_nutrients_invalid_init(manure_type: ManureType | str, nutrient_values: dict[str, float]) -> None:
    """
    Unit test for the __post_init__ method in the ManureNutrients class in manure_nutrients.py.

    Test the validation in the initialization of the ManureNutrients class,
    expecting it to raise an error when any of the attributes are negative.

    """
    for key in nutrient_values:
        if nutrient_values[key] < 0:
            with pytest.raises(ValueError, match=f"Field {key} must be non-negative."):
                ManureNutrients(**nutrient_values, manure_type=manure_type)
            break
    if not manure_type:
        with pytest.raises(ValueError, match="Field manure_type must be an instance of ManureType."):
            ManureNutrients(**nutrient_values, manure_type=manure_type)


def test_manure_nutrients_add_subtract() -> None:
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
        manure_type=ManureType.LIQUID,
    )

    nutrients2 = ManureNutrients(
        nitrogen=2.0,
        phosphorus=3.0,
        potassium=4.0,
        dry_matter=5.0,
        total_manure_mass=6.0,
        manure_type=ManureType.LIQUID,
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


@pytest.mark.parametrize(
    "manure_type_nutrients, manure_type_nutrients2, nitrogen, nitrogen2, phosphorus, phosphorus2,"
    "nutrient_to_subtract",
    [
        (ManureType.LIQUID, ManureType.SOLID, 1.0, 2.0, 2.0, 3.0, "nitrogen"),
        (ManureType.LIQUID, ManureType.LIQUID, 2.0, 1.0, 2.0, 3.0, "nitrogen"),
        (ManureType.LIQUID, ManureType.LIQUID, 1.0, 2.0, 3.0, 2.0, "phosphorus"),
    ],
)
def test_manure_nutrients_add_subtract_raises_errors(
    manure_type_nutrients: ManureType,
    manure_type_nutrients2: ManureType,
    nitrogen: float,
    nitrogen2: float,
    phosphorus: float,
    phosphorus2: float,
    nutrient_to_subtract: str,
) -> None:
    """
    Unit test for the addition and subtraction operations (__add__, __sub__)
    in the ManureNutrients class in manure_nutrients.py raising errors.

    """
    # Arrange
    nutrients = ManureNutrients(
        nitrogen=nitrogen,
        phosphorus=phosphorus,
        potassium=3.0,
        dry_matter=4.0,
        total_manure_mass=5.0,
        manure_type=manure_type_nutrients,
    )

    nutrients2 = ManureNutrients(
        nitrogen=nitrogen2,
        phosphorus=phosphorus2,
        potassium=4.0,
        dry_matter=5.0,
        total_manure_mass=6.0,
        manure_type=manure_type_nutrients2,
    )

    # Act
    if nutrients.manure_type != nutrients2.manure_type:
        with pytest.raises(
            TypeError,
            match=f"Cannot add {nutrients.manure_type} " f"nutrients to {nutrients2.manure_type} nutrients.",
        ):
            nutrients + nutrients2
        with pytest.raises(
            TypeError,
            match=f"Cannot subtract {nutrients.manure_type} " f"nutrients from {nutrients2.manure_type} nutrients.",
        ):
            nutrients2 - nutrients

        nutrients2 = "dummy_invalid_nutrients"
        with pytest.raises(TypeError, match=f"Cannot add {type(nutrients)} to {type(nutrients2)}."):
            nutrients + nutrients2
        with pytest.raises(
            TypeError,
            match=f"Cannot subtract {type(nutrients2)} from {type(nutrients)}.",
        ):
            nutrients - nutrients2
    else:
        with pytest.raises(
            ValueError,
            match=f"The amount of {nutrient_to_subtract} in other " f"object is greater than what is available.",
        ):
            nutrients2 - nutrients


@pytest.mark.parametrize("multiplier", [0, 2, 3.5, 1e10, -1, None])
def test_manure_nutrients_multiplication(multiplier: int | float | None) -> None:
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
        manure_type=ManureType.LIQUID,
    )

    # Act and Assert
    if multiplier is None:
        with pytest.raises(TypeError, match=f"Cannot multiply {type(nutrients)} by {type(multiplier)}."):
            nutrients * multiplier  # __mul__
        with pytest.raises(TypeError, match=f"Cannot multiply {type(nutrients)} by {type(multiplier)}."):
            multiplier * nutrients  # __rmul__
    elif multiplier < 0:
        with pytest.raises(ValueError, match=f"Cannot multiply {type(nutrients)} by a negative scalar."):
            nutrients * multiplier  # __mul__
        with pytest.raises(ValueError, match=f"Cannot multiply {type(nutrients)} by a negative scalar."):
            multiplier * nutrients  # __rmul__
    else:
        nutrients_multiplied = nutrients * multiplier  # __mul__
        nutrients_multiplied_2 = multiplier * nutrients  # __rmul__

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


def test_reset_values() -> None:
    """Test the rest_values() function."""
    nutrients = ManureNutrients(
        manure_type=ManureType.LIQUID,
        nitrogen=134,
        phosphorus=159.6,
        potassium=924,
        dry_matter=77.7,
        total_manure_mass=131,
    )
    reset = nutrients.reset_values()
    assert reset == ManureNutrients(
        manure_type=ManureType.LIQUID, nitrogen=0, phosphorus=0, potassium=0, dry_matter=0, total_manure_mass=0
    )
