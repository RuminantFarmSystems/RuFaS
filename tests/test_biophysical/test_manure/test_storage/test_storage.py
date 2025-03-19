from dataclasses import replace
import pytest
from datetime import datetime, timedelta
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
def storage() -> Storage:
    """Storage fixture for testing."""
    storage = Storage(
        name="fixture",
        is_housing_emissions_calculator=False,
        cover=StorageCover.COVER,
        storage_time_period=120,
        surface_area=300.0,
        nitrous_oxide_emissions_factor=0.0,
    )
    storage._om = OutputManager()
    storage._storage_time_period = 120
    storage._nitrous_oxide_emissions_factor = 0.0
    storage._received_manure = ManureStream.make_empty_manure_stream()
    storage._stored_manure = ManureStream.make_empty_manure_stream()
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
    assert actual._prefix == "Storage.test"
    assert actual._accumulated_output_prefix == "AccumulatedStorage.test"


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


@pytest.fixture
def empty_manure_stream() -> ManureStream:
    """Fixture to create an empty ManureStream instance."""
    return ManureStream.make_empty_manure_stream()


@pytest.fixture
def sample_manure_stream() -> ManureStream:
    """Fixture to create a non-empty ManureStream instance."""
    return ManureStream(
        water=100.0,
        ammoniacal_nitrogen=5.0,
        nitrogen=10.0,
        phosphorus=3.0,
        potassium=4.0,
        ash=2.0,
        non_degradable_volatile_solids=6.0,
        degradable_volatile_solids=8.0,
        total_solids=10.0,
        volume=1.0,
        pen_manure_data=None,
    )


def test_storage_accumulates_received(storage: Storage, time: Time, sample_manure_stream: ManureStream,
                                      current_conditions: CurrentDayConditions) -> None:
    """Test that received manure is added to stored manure."""
    storage._received_manure = sample_manure_stream

    storage.process_manure(current_conditions, time)

    assert storage._stored_manure == sample_manure_stream
    assert storage._received_manure.is_empty is True


def test_process_manure_empties_on_scheduled_day(storage: Storage, time: Time, sample_manure_stream: ManureStream,
                                                 current_conditions: CurrentDayConditions, mocker: MockerFixture
                                                 ) -> None:
    """Test that manure is emptied on scheduled emptying day."""
    time.current_date = time.start_date + timedelta(days=storage._storage_time_period)
    storage._stored_manure = sample_manure_stream
    mock_report_manure_stream = mocker.patch.object(storage, "_report_manure_stream")

    returned_manure = storage.process_manure(current_conditions, time)

    mock_report_manure_stream.assert_any_call(sample_manure_stream, "emptied", time)
    assert returned_manure == {"manure": replace(sample_manure_stream)}
    assert storage._stored_manure.is_empty is True


def test_process_manure_does_not_empty_on_non_scheduled_day(storage: Storage, time: Time,
                                                            sample_manure_stream: ManureStream,
                                                            current_conditions: CurrentDayConditions,
                                                            mocker: MockerFixture) -> None:
    """Test that manure is not emptied on a non-scheduled emptying day."""
    time.current_day = time.start_date + timedelta(days=storage._storage_time_period + 1)
    storage._stored_manure = sample_manure_stream
    mock_report_manure_stream = mocker.patch.object(storage, "_report_manure_stream")

    returned_manure = storage.process_manure(current_conditions, time)

    mock_report_manure_stream.assert_called_once()
    assert returned_manure == {}


def test_process_manure_handles_overflowing(storage: Storage, time: Time, sample_manure_stream: ManureStream,
                                            current_conditions: CurrentDayConditions, mocker: MockerFixture) -> None:
    """Test that overflow handling is triggered if manure is overflowing."""
    storage._capacity = 50.0

    mock_handle_overflow = mocker.patch.object(storage, "handle_overflowing_manure")

    storage._stored_manure = sample_manure_stream
    storage._stored_manure.volume = 60

    storage.process_manure(current_conditions, time)

    mock_handle_overflow.assert_called_once_with(time)


def test_process_manure_reports_stored_manure(storage: Storage, time: Time, sample_manure_stream: ManureStream,
                                              current_conditions: CurrentDayConditions,
                                              mocker: MockerFixture) -> None:
    """Test that manure storage is reported after processing."""
    storage._stored_manure = sample_manure_stream
    mock_report_manure_stream = mocker.patch.object(storage, "_report_manure_stream")

    storage.process_manure(current_conditions, time)

    mock_report_manure_stream.assert_any_call(
        sample_manure_stream, storage._accumulated_output_prefix, time
    )


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


@pytest.mark.parametrize("temp, expected", [(-10.0, 0.0), (0.0, 0.0), (15.0, 15.0), (35.0, 35.0), (45.0, 35.0)])
def test_determine_outdoor_storage_temperature(temp: float, expected: float) -> None:
    """Test that the temperature of manure in outdoor storages is calculated correctly."""
    actual = Storage._determine_outdoor_storage_temperature(temp)

    assert actual == expected


@pytest.mark.parametrize("factor, nitrogen, expected", [(0.1, 100.0, 10.0), (0.0, 20.0, 0.0), (1.0, 40.0, 40.0)])
def test_calculate_nitrous_oxide_emissions(factor: float, nitrogen: float, expected: float) -> None:
    """Tests that the amount of nitrous oxided emitted from a storage is calculated correctly."""
    actual = Storage._calculate_nitrous_oxide_emissions(factor, nitrogen)

    assert actual == expected
