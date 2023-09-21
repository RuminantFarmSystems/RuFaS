from __future__ import annotations

import pytest
from pytest import approx, mark

from RUFAS.routines.manure.manure_nutrients.nutrient_request import NutrientRequest


@mark.parametrize(
    "nitrogen, phosphorus",
    [
        (0.0, 0.0),  # No nutrients requested
        (-1.0, 0.0),  # Negative nitrogen requested
        (1.0, -2.0),  # Negative phosphorus requested
    ]
)
def test_nutrient_request_invalid_init(nitrogen: float, phosphorus: float):
    """
    Unit test for the __post_init__ method in the NutrientRequest class in nutrient_request.py.

    Test the validation in the initialization of the NutrientRequest class,
    expecting it to raise an error when no nutrients are requested or
    when a negative amount of any nutrient is requested.

    """
    with pytest.raises(ValueError):
        NutrientRequest(nitrogen=nitrogen, phosphorus=phosphorus)


@mark.parametrize(
    "nitrogen, phosphorus",
    [
        (0.0, 1.0),  # Only phosphorus requested
        (1.0, 0.0),  # Only nitrogen requested
        (1.0, 2.0),  # Both nutrients requested
    ]
)
def test_nutrient_request_valid_init(nitrogen: float, phosphorus: float):
    """
    Unit test for the NutrientRequest class in nutrient_request.py.

    Test the initialization of the NutrientRequest dataclass with valid values.

    """
    # Act
    nutrient_request = NutrientRequest(nitrogen=nitrogen, phosphorus=phosphorus)

    # Assert
    assert nutrient_request.nitrogen == approx(nitrogen)
    assert nutrient_request.phosphorus == approx(phosphorus)
