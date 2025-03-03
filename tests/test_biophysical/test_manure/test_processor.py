import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.processor import Processor


def test_processor_init_error() -> None:
    """Test that base Processor class throws appropriate error when initialized."""
    with pytest.raises(TypeError):
        Processor(name="test processor", is_housing_emissions_calculator=True)


# TODO: test with a grandchild of Processor in #2102, #2103, #2104, or #2105
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


@pytest.mark.parametrize(
    "temp, pH, expected", [(300.0, 7.8, 44041.363886), (275.0, 6.1, 39965670.832018), (255.0, 8.8, 1276771.214701)]
)
def test_calculate_ammonia_equilibirum_coefficient(temp: float, pH: float, expected: float) -> None:
    """Tests that the ammonia equilibrium coefficient is calculated correctly."""
    actual = Processor._calculate_ammonia_equilibrium_coefficient(temp, pH)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize("temp, expected", [(300.0, 1724.51377067), (275.0, 4836.6588355), (255.0, 12766.69347978)])
def test_calculate_henry_law_coefficient_of_ammonia(temp: float, expected: float) -> None:
    """Tests that the Coefficient of Ammonia calculated by Henry's Law is correct."""
    actual = Processor._calculate_henry_law_coefficient_of_ammonia(temp)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize(
    "temp, pH, expected", [(300.0, 7.8, 25.53842401), (275.0, 6.1, 8263.0741988), (255.0, 8.8, 100.0079791)]
)
def test_calculate_dissociation_coefficient_of_ammonium(temp: float, pH: float, expected: float) -> None:
    """Tests that the dissociation coefficient of ammonium is calculated correctly."""
    actual = Processor._calculate_dissociation_coefficient_of_ammonium(temp, pH)

    assert pytest.approx(actual) == expected
