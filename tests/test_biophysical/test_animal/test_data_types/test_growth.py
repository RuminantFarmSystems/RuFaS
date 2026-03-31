import pytest
from typing import Generator

from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.growth import GrowthInputs, GrowthOutputs


@pytest.fixture
def sample_growth_inputs() -> Generator[GrowthInputs, None, None]:
    """Fixture to provide a sample GrowthInputs instance."""
    yield GrowthInputs(
        days_in_pregnancy=150,
        animal_type=AnimalType.LAC_COW,
        body_weight=650.0,
        mature_body_weight=700.0,
        birth_weight=40.0,
        days_born=1000,
        days_in_milk=200,
        conceptus_weight=50.0,
        gestation_length=280,
        calf_birth_weight=45.0,
        calves=1,
        calving_interval=365.0,
    )


@pytest.fixture
def sample_growth_outputs() -> Generator[GrowthOutputs, None, None]:
    """Fixture to provide a sample GrowthOutputs instance."""
    yield GrowthOutputs(body_weight=660.0, conceptus_weight=55.0, events=AnimalEvents())


def test_growth_inputs_initialization(sample_growth_inputs: GrowthInputs) -> None:
    """Test that GrowthInputs correctly stores attribute values."""
    assert sample_growth_inputs.days_in_pregnancy == 150
    assert sample_growth_inputs.animal_type == AnimalType.LAC_COW
    assert sample_growth_inputs.body_weight == 650.0
    assert sample_growth_inputs.mature_body_weight == 700.0
    assert sample_growth_inputs.birth_weight == 40.0
    assert sample_growth_inputs.days_born == 1000
    assert sample_growth_inputs.days_in_milk == 200
    assert sample_growth_inputs.conceptus_weight == 50.0
    assert sample_growth_inputs.gestation_length == 280
    assert sample_growth_inputs.calf_birth_weight == 45.0
    assert sample_growth_inputs.calves == 1
    assert sample_growth_inputs.calving_interval == 365.0


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
    days_in_pregnancy: int, expected_is_pregnant: bool, sample_growth_inputs: GrowthInputs
) -> None:
    """Test the is_pregnant property for various days_in_pregnancy values."""
    growth_input = sample_growth_inputs
    growth_input.days_in_pregnancy = days_in_pregnancy
    assert growth_input.is_pregnant == expected_is_pregnant


@pytest.mark.parametrize(
    "days_in_milk, expected_is_milking",
    [
        (200, True),  # Lactating
        (1, True),  # Just started milking
        (0, False),  # Dry cow (not milking)
        (-1, False),  # Edge case: negative milking days
    ],
)
def test_is_milking_property(days_in_milk: int, expected_is_milking: bool, sample_growth_inputs: GrowthInputs) -> None:
    """Test the is_milking property for various days_in_milk values."""
    growth_input = sample_growth_inputs
    growth_input.days_in_milk = days_in_milk
    assert growth_input.is_milking == expected_is_milking


def test_growth_outputs_initialization(sample_growth_outputs: GrowthOutputs) -> None:
    """Test that GrowthOutputs correctly stores attribute values."""
    assert sample_growth_outputs.body_weight == 660.0
    assert sample_growth_outputs.conceptus_weight == 55.0
    assert isinstance(sample_growth_outputs.events, AnimalEvents)
