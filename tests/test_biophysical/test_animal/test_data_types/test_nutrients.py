import pytest

from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.nutrients import NutrientsInputs


@pytest.fixture
def sample_nutrients_inputs() -> NutrientsInputs:
    """Fixture providing a sample NutrientsInputs instance."""
    return NutrientsInputs(
        animal_type=AnimalType.LAC_COW,
        body_weight=650.0,
        mature_body_weight=700.0,
        daily_growth=1.2,
        days_in_pregnancy=150,
        days_in_milk=200,
        daily_milk_produced=35.0,
    )


def test_nutrients_inputs_initialization(sample_nutrients_inputs: NutrientsInputs) -> None:
    """Test that NutrientsInputs correctly stores attribute values."""
    assert sample_nutrients_inputs.animal_type == AnimalType.LAC_COW
    assert sample_nutrients_inputs.body_weight == 650.0
    assert sample_nutrients_inputs.mature_body_weight == 700.0
    assert sample_nutrients_inputs.daily_growth == 1.2
    assert sample_nutrients_inputs.days_in_pregnancy == 150
    assert sample_nutrients_inputs.days_in_milk == 200
    assert sample_nutrients_inputs.daily_milk_produced == 35.0


@pytest.mark.parametrize(
    "days_in_pregnancy, expected_is_pregnant",
    [
        (150, True),  # Pregnant
        (1, True),  # Just became pregnant
        (0, False),  # Not pregnant
        (-1, False),  # Edge case: negative pregnancy days
    ],
)
def test_is_pregnant_property(
    days_in_pregnancy: int, expected_is_pregnant: bool, sample_nutrients_inputs: NutrientsInputs
) -> None:
    """Test the is_pregnant property for various days_in_pregnancy values."""
    sample_nutrients_inputs.days_in_pregnancy = days_in_pregnancy
    assert sample_nutrients_inputs.is_pregnant == expected_is_pregnant


@pytest.mark.parametrize(
    "days_in_milk, expected_is_milking",
    [
        (200, True),  # Lactating
        (1, True),  # Just started milking
        (0, False),  # Dry cow (not milking)
        (-1, False),  # Edge case: negative milking days
    ],
)
def test_is_milking_property(
    days_in_milk: int, expected_is_milking: bool, sample_nutrients_inputs: NutrientsInputs
) -> None:
    """Test the is_milking property for various days_in_milk values."""
    sample_nutrients_inputs.days_in_milk = days_in_milk
    assert sample_nutrients_inputs.is_milking == expected_is_milking
