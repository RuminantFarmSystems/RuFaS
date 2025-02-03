import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.processor import Processor
from RUFAS.data_structures.animal_to_manure_connection import (
    AnimalCombination,
    ManureStream,
    ManureStreamType,
    PenManureData,
)


@pytest.fixture
def processor(mocker: MockerFixture) -> Processor:
    """Creates a mock Processor for testing purposes."""
    mocker.patch.object(Processor, "__init__", return_value=None)
    return Processor(is_housing_emissions_calculator=False)


def test_processor_init_error() -> None:
    """Test that base Processor class throws appropriate error when initialized."""
    with pytest.raises(TypeError):
        Processor(is_housing_emissions_calculator=True)


@pytest.mark.parametrize(
    "housing_emissions, pen_manure, expected",
    [
        (True, None, False),
        (False, None, True),
        (
            True,
            PenManureData(
                num_animals=100,
                manure_deposition_surface_area=250.0,
                animal_combination=AnimalCombination.CALF,
                pen_type="test",
                manure_urine_mass=100.0,
                manure_urine_nitrogen=50.0,
                stream_type=ManureStreamType.GENERAL,
            ),
            True,
        ),
        (
            False,
            PenManureData(
                num_animals=100,
                manure_deposition_surface_area=250.0,
                animal_combination=AnimalCombination.CALF,
                pen_type="test",
                manure_urine_mass=100.0,
                manure_urine_nitrogen=50.0,
                stream_type=ManureStreamType.GENERAL,
            ),
            False,
        ),
    ],
)
def test_check_manure_stream_compatibility(
    processor: Processor, housing_emissions: bool, pen_manure: PenManureData | None, expected: bool
) -> None:
    """Tests that ManureStreams are correctly checked for compatibility."""
    pass  # TODO: test with a child of Processor
