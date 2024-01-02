from __future__ import annotations

import pytest
from pytest import approx, mark
from RUFAS.routines.manure.manure_treatments.manure_types import ManureType
from RUFAS.routines.manure.manure_nutrients.nutrient_request import NutrientRequest


@mark.parametrize(
    "nitrogen, phosphorus, manure_type",
    [
        (0.0, 0.0, ManureType.LIQUID),  # No nutrients requested
        (-1.0, 0.0, ManureType.SOLID),  # Negative nitrogen requested
        (1.0, -2.0, ManureType.LIQUID),  # Negative phosphorus requested
        (1.0, 1.0, ""),  # Invalid ManureType
    ]
)
def test_nutrient_request_invalid_init(nitrogen: float, phosphorus: float, manure_type: ManureType):
    """
    Unit test for the __post_init__ method in the NutrientRequest class in nutrient_request.py.

    Test the validation in the initialization of the NutrientRequest class,
    expecting it to raise an error when no nutrients are requested or
    when a negative amount of any nutrient is requested.

    """
    with pytest.raises(ValueError):
        NutrientRequest(nitrogen=nitrogen, phosphorus=phosphorus, manure_type=manure_type)


@mark.parametrize(
    "nitrogen, phosphorus, manure_type",
    [
        (0.0, 1.0, ManureType.LIQUID),  # Only phosphorus requested
        (1.0, 0.0, ManureType.LIQUID),  # Only nitrogen requested
        (1.0, 2.0, ManureType.SOLID),  # Both nutrients requested
    ]
)
def test_nutrient_request_valid_init(nitrogen: float, phosphorus: float, manure_type: ManureType):
    """
    Unit test for the NutrientRequest class in nutrient_request.py.

    Test the initialization of the NutrientRequest dataclass with valid values.

    """
    # Act
    nutrient_request = NutrientRequest(nitrogen=nitrogen, phosphorus=phosphorus, manure_type=manure_type)

    # Assert
    assert nutrient_request.nitrogen == approx(nitrogen)
    assert nutrient_request.phosphorus == approx(phosphorus)
