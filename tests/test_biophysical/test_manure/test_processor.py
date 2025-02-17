import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.processor import Processor


def test_processor_init_error() -> None:
    """Test that base Processor class throws appropriate error when initialized."""
    with pytest.raises(TypeError):
        Processor(is_housing_emissions_calculator=True)


# TODO: test with a child or grandchild of Processor, either in #2098 or #2099
def test_check_manure_stream_compatibility() -> None:
    """Tests that ManureStreams are correctly checked for compatibility."""
    pass


@pytest.mark.parametrize(
    "total_ammoniacal, volume, density, resistance, temp, area, pH, expected",
    [(0.0, 1_000.0, 10.0, 4.1, 20.0, 1_500.0, 8.0, 0.0), (25.0, 800.0, 15.0, 1.8, 5.0, 300.0, 6.5, 25.0)],
)
def test_calculate_ammonia_emissions(
    mocker: MockerFixture,
    total_ammoniacal: float,
    volume: float,
    density: float,
    resistance: float,
    temp: float,
    area: float,
    pH: float,
    expected: float,
) -> None:
    """Test that ammonia emissions from a storage are calculated correctly."""
    mocker.patch.object(Processor, "_calculate_ammonia_equilibrium_coefficient", return_value=0.1)

    actual = Processor._calculate_ammonia_emissions(total_ammoniacal, volume, density, resistance, temp, area, pH)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "total_ammoniacal, volume, density, area",
    [
        (-1_000.0, 3_000.0, 44.0, 500.0),
        (1_000.0, -3_000.0, 44.0, 500.0),
        (1_000.0, 3_000.0, -44.0, 500.0),
        (1_000.0, 3_000.0, 44.0, -500.0),
    ],
)
def test_calculate_ammonia_emissions_error(total_ammoniacal: float, volume: float, density: float, area: float) -> None:
    """Test that ammonia emissions calculations raise an error when passed an invalid value."""
    with pytest.raises(ValueError):
        Processor._calculate_ammonia_emissions(total_ammoniacal, volume, density, 4.1, 20.0, area, 6.0)
