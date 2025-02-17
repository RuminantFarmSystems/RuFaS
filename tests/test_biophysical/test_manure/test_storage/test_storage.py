import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.storage.storage import Storage
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover


def test_storage_init_error() -> None:
    """Test that Storage cannot be initialized because it does not fully implement the abstract base class."""

    with pytest.raises(TypeError):
        Storage(
            name="test storage",
            is_housing_emissions_calculator=False,
            cover=StorageCover.NO_COVER,
            storage_time_period=100,
        )


# TODO: Test when a Storage child is implemented, either #2103, 2104, or 2105
def test_storage_init() -> None:
    """Test that a Storage instance is instantiated properly."""
    pass


# TODO: Test when a Storage child is implemented, either #2103, 2104, or 2105
def test_receive_manure() -> None:
    """Test that the receive_manure method in Storage works correctly."""
    pass


@pytest.mark.parametrize(
    "vol_sols,temp,degradable,expected",
    [(100.0, 20.0, False, 0.003138872), (100.0, -10.0, True, 0.007100907)]
)
def test_calculate_methane_emissions(vol_sols: float, temp: float, degradable: bool, expected: float) -> None:
    """Test that methane emissions from a storage are calculated correctly."""
    actual = Storage._calculate_methane_emissions(vol_sols, temp, degradable)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize("temp, expected", [(-20.0, 0.000685409), (0.0, 0.0114749106), (10, 0.0404406008)])
def test_calculate_arrhenius_exponent(temp: float, expected: float) -> None:
    """Test that the Arrhenius Exponent is calculated correctly."""
    actual = Storage._calculate_arrhenius_exponent(temp)

    assert pytest.approx(actual) == expected


def test_calculate_arrhenius_exponent_error() -> None:
    """Test that Arrhenius exponent equation raises an error when passed an invalid temperature."""
    


@pytest.mark.parametrize(
    "total_ammoniacal, volume, density, temp, area, pH, expected",
    [
        (0.0, 1_000.0, 10.0, 20.0, 1_500.0, 8.0, 0.0),
        (25.0, 800.0, 15.0, 5.0, 300.0, 6.5, 25.0)
    ]
)
def test_calculate_ammonia_emissions(mocker: MockerFixture, total_ammoniacal: float, volume: float, density: float, temp: float, area: float, pH: float, expected: float) -> None:
    """Test that ammonia emissions from a storage are calculated correctly."""
    mocker.patch.object(Storage, "_calculate_ammonia_equilibrium_coefficient", return_value=0.1)

    actual = Storage._calculate_ammonia_emissions(total_ammoniacal, volume, density, temp, area, pH)

    assert pytest.approx(actual) == expected
