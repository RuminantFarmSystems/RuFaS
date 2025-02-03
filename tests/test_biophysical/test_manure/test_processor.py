import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.processor import Processor


def processor(mocker: MockerFixture) -> Processor:
    """Creates a mock Processor for testing purposes."""
    mocker.patch.object(Processor, "__init__", return_value=None)
    return Processor(is_housing_emissions_calculator=False)


def test_processor_init_error() -> None:
    """Test that base Processor class throws appropriate error when initialized."""
    with pytest.raises(TypeError):
        Processor(is_housing_emissions_calculator=True)


@pytest.mark.parametrize(
    "housing_emissions, pen_manure, expected"
    [
        (True, None, False),
        (False, None, True),
        (True, PenManureData(), True),
        (False, PenManureData(), False)
    ]
)
def test_check_manure_stream_compatibility(
    processor: Processor, housing_emissions: bool, pen_manure: PenManureData | None, expected: bool
) -> None:
    """Tests that ManureStreams are correctly checked for compatibility."""
    processor.is_housing_emissions_calculator = housing_emissions
    manure_stream = ManureStream(pen_manure_data=pen_manure)

    actual = processor.check_manure_stream_compatibility(manure_stream)

    assert actual == expected
