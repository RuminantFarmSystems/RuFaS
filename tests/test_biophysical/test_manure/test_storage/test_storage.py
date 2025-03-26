import pytest
from datetime import datetime
from pytest_mock import MockerFixture
from math import inf

from RUFAS.biophysical.manure.storage.storage import Storage
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream, PenManureData, StreamType
from RUFAS.enums import AnimalCombination
from RUFAS.time import Time
from RUFAS.output_manager import OutputManager


@pytest.fixture
def storage(mocker: MockerFixture) -> Storage:
    """Storage fixture for testing."""
    mocker.patch.object(Storage, "__init__", return_value=None)
    storage = Storage(
        name="fixture",
        is_housing_emissions_calculator=False,
        cover=StorageCover.COVER,
        storage_time_period=120,
        surface_area=300.0,
        nitrous_oxide_emissions_factor=0.0,
    )
    storage.name = "fixture"
    storage.is_housing_emissions_calculator = False
    storage._om = OutputManager()
    storage._cover = StorageCover.COVER
    storage._storage_time_period = 120
    storage._surface_area = 300.0
    storage._nitrous_oxide_emissions_factor = 0.0
    storage._received_manure = ManureStream.make_empty_manure_stream()
    storage._stored_manure = ManureStream.make_empty_manure_stream()
    storage._prefix = "Storage.fixture"
    storage._accumulated_output_prefix = "AccumulatedStorage.fixture"
    return storage


@pytest.fixture
def current_conditions() -> CurrentDayConditions:
    """CurrentDayConditions fixture for testing."""
    return CurrentDayConditions(
        incoming_light=10.0,
        min_air_temperature=18.0,
        mean_air_temperature=21.0,
        max_air_temperature=24.0,
        daylength=16.0,
        annual_mean_air_temperature=14.0,
        snowfall=0.0,
        rainfall=4.0,
        precipitation=4.0,
    )


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
    assert actual._prefix == "Manure.Processor.Storage.test"


@pytest.mark.parametrize(
    "manure_received, expected",
    [
        ([], ManureStream.make_empty_manure_stream()),
        ([ManureStream.make_empty_manure_stream()], ManureStream.make_empty_manure_stream()),
        (
            [
                ManureStream(
                    water=100.0,
                    ammoniacal_nitrogen=20.0,
                    nitrogen=10.0,
                    phosphorus=5.0,
                    potassium=2.0,
                    ash=40.0,
                    non_degradable_volatile_solids=20.0,
                    degradable_volatile_solids=30.0,
                    total_solids=1000.0,
                    volume=1500.0,
                    pen_manure_data=None,
                ),
                ManureStream(
                    water=100.0,
                    ammoniacal_nitrogen=20.0,
                    nitrogen=10.0,
                    phosphorus=5.0,
                    potassium=2.0,
                    ash=40.0,
                    non_degradable_volatile_solids=20.0,
                    degradable_volatile_solids=30.0,
                    total_solids=1000.0,
                    volume=1500.0,
                    pen_manure_data=None,
                ),
            ],
            ManureStream(
                water=200.0,
                ammoniacal_nitrogen=40.0,
                nitrogen=20.0,
                phosphorus=10.0,
                potassium=4.0,
                ash=80.0,
                non_degradable_volatile_solids=40.0,
                degradable_volatile_solids=60.0,
                total_solids=2000.0,
                volume=3000.0,
                pen_manure_data=None,
            ),
        ),
    ],
)
def test_receive_manure(storage: Storage, manure_received: list[ManureStream], expected: ManureStream) -> None:
    """Test that the receive_manure method in Storage works correctly."""
    for stream in manure_received:
        storage.receive_manure(stream)

    assert storage._received_manure == expected


@pytest.mark.parametrize(
    "pen_manure_data, is_housing_emissions_calculator",
    [
        (None, True),
        (PenManureData(100, 3000.0, AnimalCombination.LAC_COW, None, 100.0, 15.0, StreamType.GENERAL), False),
    ],
)
def test_receive_manure_error(
    storage: Storage, pen_manure_data: PenManureData | None, is_housing_emissions_calculator: bool
) -> None:
    """Test that the receive_manure method in Storage raises an error correctly."""
    storage.is_housing_emissions_calculator = is_housing_emissions_calculator
    manure_stream = ManureStream.make_empty_manure_stream()
    manure_stream.pen_manure_data = pen_manure_data
    with pytest.raises(ValueError, match="Processor 'fixture' received an incompatible ManureStream."):
        storage.receive_manure(manure_stream)


@pytest.mark.parametrize(
    "received_volume, stored_volume, capacity, storage_period, day, expected_stored_volume, expected_emptied_volume,"
    "expected_overflow",
    [
        (1000.0, 2000.0, 4000.0, 30, 20, 3000.0, None, False),
        (1000.0, 2000.0, 2500.0, 30, 20, 3000.0, None, True),
        (1000.0, 2000.0, 2500.0, None, 20, 3000.0, None, True),
        (1000.0, 2000.0, 2500.0, 30, 30, 0.0, 3000.0, False),
    ],
)
def test_process_manure(
    storage: Storage,
    current_conditions: CurrentDayConditions,
    time: Time,
    mocker: MockerFixture,
    received_volume: float,
    stored_volume: float,
    capacity: float,
    storage_period: int | None,
    day: int,
    expected_stored_volume: float,
    expected_emptied_volume: float | None,
    expected_overflow: bool,
) -> None:
    """Test that Storage processes manure correctly."""
    storage._received_manure.volume = received_volume
    storage._stored_manure.volume = stored_volume
    storage._capacity = capacity
    storage._storage_time_period = storage_period
    mocker.patch.object(Time, "simulation_day", new_callable=mocker.PropertyMock, return_value=day)
    handle_overflow = mocker.patch.object(storage, "handle_overflowing_manure", return_value=None)
    mock_report_manure_stream = mocker.patch.object(storage, "_report_manure_stream", return_value=None)
    if expected_emptied_volume is not None:
        manure_stream = ManureStream.make_empty_manure_stream()
        manure_stream.volume = expected_emptied_volume
        expected_returned_manure = {"manure": manure_stream}
    else:
        expected_returned_manure = {}

    actual = storage.process_manure(current_conditions, time)

    assert actual == expected_returned_manure
    assert storage._stored_manure.volume == expected_stored_volume
    if expected_emptied_volume is not None:
        mock_report_manure_stream.assert_called_once_with(expected_returned_manure["manure"], "emptied", time)
    else:
        mock_report_manure_stream.assert_not_called()
    if expected_overflow:
        handle_overflow.assert_called_once_with(time)


def test_handle_overflowing_manure(storage: Storage, mocker: MockerFixture, time: Time) -> None:
    """Test that the handle_overflowing_manure method in Storage works correctly."""
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


@pytest.mark.parametrize("factor, nitrogen, expected", [(0.1, 100.0, 10.0), (0.0, 20.0, 0.0), (1.0, 40.0, 40.0)])
def test_calculate_nitrous_oxide_emissions(factor: float, nitrogen: float, expected: float) -> None:
    """Tests that the amount of nitrous oxided emitted from a storage is calculated correctly."""
    actual = Storage._calculate_nitrous_oxide_emissions(factor, nitrogen)

    assert actual == expected
