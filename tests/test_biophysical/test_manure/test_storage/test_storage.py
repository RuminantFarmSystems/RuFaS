import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.storage.storage import Storage
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover


def storage(mocker: MockerFixture) -> Storage:
    """Storage fixture for testing."""
    mocker.patch.object(Storage, "__init__", return_value=None)
    return Storage(
        "storage fixture",
        is_housing_emissions_calculator=False,
        cover=StorageCover.COVER,
        surface_area=300.0,
        nitrous_oxide_emissions_factor=0.0,
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
    "vol_sols,temp,degradable,expected", [(100.0, 20.0, False, 0.003138872), (100.0, -10.0, True, 0.007100907)]
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


@pytest.mark.parametrize("temp", [-45.0, 61.0])
def test_calculate_arrhenius_exponent_error(temp: float) -> None:
    """Test that Arrhenius exponent equation raises an error when passed an invalid temperature."""
    with pytest.raises(ValueError):
        Storage._calculate_arrhenius_exponent(temp)


@pytest.mark.parametrize("loss, expected_burned, expected_loss", [(100.0, 81.0, 19.0), (0.0, 0.0, 0.0)])
def test_calculate_cover_and_flare_methane(loss: float, expected_burned: float, expected_loss: float) -> None:
    """Test that the amount of methane destroyed by a cap and flare is calculated correctly."""
    actual_burned, actual_loss = Storage._calculate_cover_and_flare_methane(loss)

    assert actual_burned == expected_burned
    assert actual_loss == expected_loss


@pytest.mark.parametrize("temp, expected", [(-10.0, 0.0), (0.0, 0.0), (15.0, 15.0), (35.0, 35.0), (45.0, 35.0)])
def test_determine_outdoor_storage_temperature(temp: float, expected: float) -> None:
    """Test that the temperature of manure in outdoor storages is calculated correctly."""
    actual = Storage._determine_outdoor_storage_temperature(temp)

    assert actual == expected
