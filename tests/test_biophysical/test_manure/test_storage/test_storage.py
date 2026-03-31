from unittest.mock import MagicMock

import pytest
from datetime import datetime
from pytest_mock import MockerFixture
from math import inf

from RUFAS.biophysical.manure.storage.storage import Storage
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream, PenManureData, StreamType
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.rufas_time import RufasTime
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
    )
    storage.name = "fixture"
    storage.is_housing_emissions_calculator = False
    storage._om = OutputManager()
    storage._cover = StorageCover.COVER
    storage._storage_time_period = 120
    storage._surface_area = 300.0
    storage._received_manure = ManureStream.make_empty_manure_stream()
    storage.stored_manure = ManureStream.make_empty_manure_stream()
    storage._prefix = "Storage.fixture"
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
def time() -> RufasTime:
    """RufasTime fixture for testing."""
    return RufasTime(
        start_date=datetime(2022, 12, 20), end_date=datetime(2025, 3, 7), current_date=datetime(2025, 2, 20)
    )


def test_storage_init() -> None:
    """Test that a Storage instance is instantiated properly."""
    actual = Storage(
        name="test",
        is_housing_emissions_calculator=False,
        cover=StorageCover.COVER,
        storage_time_period=100,
        surface_area=300.0,
    )

    assert actual.name == "test"
    assert actual.is_housing_emissions_calculator is False
    assert actual._received_manure.mass == 0.0
    assert actual._received_manure.pen_manure_data is None
    assert actual.stored_manure.mass == 0.0
    assert actual.stored_manure.pen_manure_data is None
    assert actual._capacity == inf
    assert actual._cover == StorageCover.COVER
    assert actual._storage_time_period == 100
    assert actual._surface_area == 300.0
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
                    methane_production_potential=0.24,
                    pen_manure_data=None,
                    bedding_non_degradable_volatile_solids=10,
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
                    methane_production_potential=0.24,
                    pen_manure_data=None,
                    bedding_non_degradable_volatile_solids=10,
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
                methane_production_potential=0.24,
                pen_manure_data=None,
                bedding_non_degradable_volatile_solids=20,
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
    "pen_manure_data, is_housing_emissions_calculator, expected_msg",
    [
        # Case 1: Missing pen manure data for housing emissions calculator
        (
            None,
            True,
            (
                "Processor 'fixture' received a ManureStream without pen manure data, "
                "which is required for housing emissions calculations. Cannot place a handler "
                "before Open Lot/Bedded Pack in the manure processor connection chain."
            ),
        ),
        (
            PenManureData(100, 3000.0, AnimalCombination.LAC_COW, None, 100.0, 15.0, StreamType.GENERAL),
            False,
            "Processor 'fixture' received an incompatible ManureStream.",
        ),
    ],
)
def test_receive_manure_error(
    storage: Storage,
    pen_manure_data: PenManureData | None,
    is_housing_emissions_calculator: bool,
    expected_msg: str,
    mocker: MockerFixture,
) -> None:
    """Test that Storage.receive_manure raises appropriate errors for invalid streams."""
    storage.is_housing_emissions_calculator = is_housing_emissions_calculator
    manure_stream = ManureStream.make_empty_manure_stream()
    manure_stream.pen_manure_data = pen_manure_data

    mock_om = mocker.patch.object(storage, "_om")
    mock_om.add_error = MagicMock()

    with pytest.raises(ValueError, match=expected_msg):
        storage.receive_manure(manure_stream)

    mock_om.add_error.assert_called_once()
    assert expected_msg in str(mock_om.add_error.call_args[0][1])


@pytest.mark.parametrize(
    "is_emptying_day, is_overflowing", [(True, False), (False, False), (False, True), (True, True)]
)
def test_process_manure(is_emptying_day: bool, is_overflowing: bool, storage: Storage, mocker: MockerFixture) -> None:
    """Test that the process_manure method in Storage works correctly."""
    mock_report_manure_stream = mocker.patch.object(storage, "_report_manure_stream", return_value=None)
    mock_handle_overflowing_manure = mocker.patch.object(storage, "handle_overflowing_manure", return_value=None)
    mock_time = MagicMock(spec=RufasTime)
    mock_time.simulation_day = storage._storage_time_period - 1 if is_emptying_day else 1
    mocker.patch.object(Storage, "is_overflowing", new_callable=mocker.PropertyMock, return_value=is_overflowing)
    mock_validate_emptying_fraction = mocker.patch.object(storage, "_validate_emptying_fraction", return_value=None)

    storage._received_manure = (
        dummy_received_manure := ManureStream(
            water=1.23,
            ammoniacal_nitrogen=2.34,
            nitrogen=3.45,
            phosphorus=4.56,
            potassium=5.67,
            ash=6.78,
            non_degradable_volatile_solids=7.89,
            degradable_volatile_solids=8.90,
            total_solids=29.01,
            volume=10.12,
            methane_production_potential=0.24,
            pen_manure_data=None,
            bedding_non_degradable_volatile_solids=10,
        )
    )
    storage.stored_manure = (
        dummy_stored_manure := ManureStream(
            water=10.11,
            ammoniacal_nitrogen=20.22,
            nitrogen=30.33,
            phosphorus=40.44,
            potassium=50.55,
            ash=60.66,
            non_degradable_volatile_solids=70.77,
            degradable_volatile_solids=80.88,
            total_solids=290.01,
            volume=100.12,
            methane_production_potential=0.24,
            pen_manure_data=None,
            bedding_non_degradable_volatile_solids=10,
        )
    )
    dummy_total_manure = dummy_received_manure + dummy_stored_manure
    result = storage.process_manure(MagicMock(auto_spec=CurrentDayConditions), mock_time)

    assert storage._received_manure == ManureStream.make_empty_manure_stream()
    if is_emptying_day:
        mock_validate_emptying_fraction.assert_called_once()
        assert result["manure"] == dummy_total_manure
        assert storage.stored_manure == ManureStream.make_empty_manure_stream()
        mock_report_manure_stream.assert_called_once_with(dummy_total_manure, "emptied", mock_time.simulation_day)
    else:
        mock_validate_emptying_fraction.assert_not_called()
        assert result == {}
        assert storage.stored_manure == dummy_total_manure
        mock_report_manure_stream.assert_called_once()
    if is_overflowing:
        mock_handle_overflowing_manure.assert_called_once_with(mock_time)
    else:
        mock_handle_overflowing_manure.assert_not_called()


def test_handle_overflowing_manure(storage: Storage, mocker: MockerFixture, time: RufasTime) -> None:
    """Test that the handle_overflowing_manure method in Storage works correctly."""
    add_warning = mocker.patch.object(storage._om, "add_warning", return_value=None)

    storage.handle_overflowing_manure(time)

    assert add_warning.call_count == 1


@pytest.mark.parametrize(
    "volume, capacity, expected", [(100.0, 1_000.0, False), (100.0, 100.0, False), (200.0, 100.0, True)]
)
def test_is_overflowing(storage: Storage, volume: float, capacity: float, expected: bool) -> None:
    """Test that the Storage correctly identifies when it is overflowing."""
    storage.stored_manure.volume = volume
    storage._capacity = capacity

    actual = storage.is_overflowing

    assert actual == expected


@pytest.mark.parametrize(
    "emptying_fraction, is_valid", [(0.0, True), (0.5, True), (1.0, True), (-0.1, False), (1.1, False)]
)
def test_validate_emptying_fraction(
    storage: Storage, mocker: MockerFixture, emptying_fraction: float, is_valid: bool
) -> None:
    """Test that the _validate_emptying_fraction method in Storage works correctly."""
    mock_add_error = mocker.patch.object(storage._om, "add_error", return_value=None)

    mocker.patch.object(Storage, "_emptying_fraction", new_callable=mocker.PropertyMock, return_value=emptying_fraction)
    if is_valid:
        storage._validate_emptying_fraction()
        mock_add_error.assert_not_called()
    else:
        with pytest.raises(ValueError):
            storage._validate_emptying_fraction()
        mock_add_error.assert_called_once()


@pytest.mark.parametrize(
    "vol_sols,temp,degradable,expected",
    [(100.0, 20.0, False, 0.001903822474058042), (100.0, -10.0, True, 0.00430691788)],
)
def test_calculate_methane_emissions(vol_sols: float, temp: float, degradable: bool, expected: float) -> None:
    """Test that methane emissions from a storage are calculated correctly."""
    actual = Storage._calculate_methane_emissions(vol_sols, temp, degradable)

    assert pytest.approx(actual) == expected


@pytest.mark.parametrize("temp, expected", [(-20.0, 0.00041572185), (0.0, 0.006959885), (10, 0.024528464)])
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


def test_calculate_surface_area(mocker: MockerFixture) -> None:
    """Test that the surface area of a storage is calculated correctly."""
    mocker.patch("RUFAS.biophysical.manure.storage.storage.MANURE_CONVERSION_CONSTANT", 0.1175)
    mocker.patch("RUFAS.biophysical.manure.storage.storage.FREEBOARD_CONSTANT", 1.20)
    mocker.patch("RUFAS.biophysical.manure.storage.storage.DEPTH_CONSTANT", 4.572)
    mocker.patch("RUFAS.biophysical.manure.storage.storage.PRECIPITATION_CONSTANT", 0.25)
    mocker.patch(
        "RUFAS.biophysical.manure.storage.storage.InputManager", autospec=True
    ).return_value.get_data.return_value = 100

    storage = Storage(
        name="test_storage",
        is_housing_emissions_calculator=False,
        cover=StorageCover.COVER,
        storage_time_period=30,
        surface_area=None,
    )
    storage.__post_init__()
    assert storage._surface_area == pytest.approx(97.8713558537714)


@pytest.mark.parametrize("day, expected", [(1, 21.03555677117994), (15, 22.08877447039771), (20, 22.36809139242717)])
def test_determine_outdoor_storage_temperature(storage: Storage, day: int, expected: float) -> None:
    """Test that the temperature of manure in outdoor storages is calculated correctly."""
    storage.intercept_mean_temp = 15
    storage.phase_shift = 12
    storage.amplitude = 12.2

    actual = storage._determine_outdoor_storage_temperature(day, -20.0)

    assert actual == expected


def test_determine_outdoor_storage_temperature_missing_factors_error(storage: Storage) -> None:
    """
    Tests that a ValueError is raised when all required attributes (amplitude,
    intercept, and phase_shift) are missing from the instance.
    """
    storage.amplitude = None
    storage.intercept_mean_temp = None
    storage.phase_shift = None

    with pytest.raises(ValueError) as e:
        storage._determine_outdoor_storage_temperature(1, -20.0)

    assert str(e.value) == "No data for outdoor storage temperature calculations."
