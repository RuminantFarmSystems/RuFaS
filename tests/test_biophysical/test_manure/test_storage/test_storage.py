import pytest
from datetime import datetime
from pytest_mock import MockerFixture
from math import inf

from RUFAS.biophysical.manure.storage.storage import Storage
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.time import Time
from RUFAS.output_manager import OutputManager


@pytest.fixture
def storage(mocker: MockerFixture) -> Storage:
    """Storage fixture for testing."""
    mocker.patch.object(Storage, "__init__", return_value=None)
    storage = Storage()
    storage.name = "storage fixture"
    storage.is_housing_emissions_calculator = False
    storage._cover = StorageCover.COVER
    storage._storage_time_period = 120
    storage._surface_area = 300.0
    storage._nitrous_oxide_emissions_factor = 0.0
    storage._received_manure = ManureStream.make_empty_manure_stream()
    storage._stored_manure = ManureStream.make_empty_manure_stream()
    storage._prefix = "Storage.test"
    storage._accumulated_output_prefix = "AccumulatedStorage.test"
    return storage


@pytest.fixture
def time() -> Time:
    """Time fixture for testing."""
    return Time(start_date=datetime(2022, 12, 20), end_date=datetime(2025, 3, 7), current_date=datetime(2025, 2, 20))


def test_storage_init() -> None:
    """Test that a Storage instance is instantiated properly."""
    actual = Storage(
        name="test",
        is_housing_emissions_calculator=False,
        cover=StorageCover.COVER,
        storage_time_period=100,
        surface_area=300.0,
        nitrous_oxide_emissions_factor=0.0,
    )

    assert actual.name == "test"
    assert actual.is_housing_emissions_calculator is False
    assert actual._received_manure.mass == 0.0
    assert actual._received_manure.pen_manure_data is None
    assert actual._stored_manure.mass == 0.0
    assert actual._stored_manure.pen_manure_data is None
    assert actual._capacity == inf
    assert actual._cover == StorageCover.COVER
    assert actual._storage_time_period == 100
    assert actual._surface_area == 300.0
    assert actual._nitrous_oxide_emissions_factor == 0.0
    assert actual._prefix == "Storage.test"
    assert actual._accumulated_output_prefix == "AccumulatedStorage.test"


def test_receive_manure() -> None:
    """Test that the receive_manure method in Storage works correctly."""
    pass


def test_process_manure() -> None:
    """Test that the process_manure method in Storage works correctly."""
    pass


def test_handle_overflowing_manure(storage: Storage, mocker: MockerFixture, time: Time) -> None:
    """Test that the handle_overflowing_manure method in Storage works correctly."""
    storage._om = OutputManager()
    add_warning = mocker.patch.object(storage._om, "add_warning", return_value=None)

    storage.handle_overflowing_manure(time)

    assert add_warning.call_count == 1


@pytest.mark.parametrize(
    "volume, capacity, expected", [(100.0, 1_000.0, False), (100.0, 100.0, False), (200.0, 100.0, True)]
)
def test_is_overflowing(storage: Storage, volume: float, capacity: float, expected: bool) -> None:
    """Test that the Storage correctly identifies when it is overflowing."""
    storage._stored_manure.volume = volume
    storage._capacity = capacity

    actual = storage.is_overflowing

    assert actual == expected


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
