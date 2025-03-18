from typing import Any, cast
import pytest
from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.processor import Processor
from RUFAS.biophysical.manure.separator.separator import Separator
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.time import Time
from RUFAS.units import MeasurementUnits


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


@pytest.fixture
def mock_separator() -> Separator:
    """Mock the Separator class."""
    separator = Separator(
        name="TestSeparator",
        separated_solids_dry_matter=0.8,
        ammoniacal_nitrogen_efficiency=0.7,
        nitrogen_efficiency=0.6,
        phosphorus_efficiency=0.5,
        potassium_efficiency=0.4,
        ash_efficiency=0.3,
        volatile_solids_efficiency=0.2,
        total_solids_efficiency=0.1,
    )
    return separator


@pytest.fixture
def manure_stream() -> ManureStream:
    """Creates a test manure stream."""
    return ManureStream(
        water=1000.0,
        ammoniacal_nitrogen=10.0,
        nitrogen=20.0,
        phosphorus=5.0,
        potassium=8.0,
        ash=2.0,
        non_degradable_volatile_solids=15.0,
        degradable_volatile_solids=25.0,
        total_solids=50.0,
        volume=1.5,
        pen_manure_data=None,
    )


@pytest.fixture
def time(mocker: MockerFixture) -> Any:
    """Creates a mocked Time object with a simulation day."""
    time = mocker.MagicMock()
    time.simulation_day = 42
    return time


def test_log_manure_stream_via_process_manure(
    mock_separator: Separator, manure_stream: ManureStream, time: Time, mocker: MockerFixture
) -> None:
    """Test that _log_manure_stream is called correctly from process_manure."""
    mock_om = mocker.patch.object(mock_separator, "_om", autospec=True)
    mock_current_day_conditions = mocker.MagicMock()
    mock_separator.receive_manure(manure_stream)
    mock_separator.process_manure(mock_current_day_conditions, time)

    assert mock_om.add_variable.call_count > 0

    mock_om.add_variable.assert_any_call(
        "SeparatedSolids.manure_total_solids",
        pytest.approx(manure_stream.total_solids * mock_separator.total_solids_efficiency),
        {
            "class": "Separator",
            "function": "_log_manure_stream",
            "prefix": "Separator.TestSeparator",
            "simulation_day": 42,
            "units": MeasurementUnits.KILOGRAMS,
        },
    )


def test_log_manure_stream_valid_dict(mock_separator: Separator, time: Time, mocker: MockerFixture) -> None:
    """Test logging when manure_stream is a valid dictionary."""
    manure_dict: dict[str, float | None] = {
        "water": 1000.0,
        "ammoniacal_nitrogen": 10.0,
        "nitrogen": 20.0,
        "phosphorus": 5.0,
        "potassium": 8.0,
        "ash": 2.0,
        "non_degradable_volatile_solids": 15.0,
        "degradable_volatile_solids": 25.0,
        "total_solids": 50.0,
        "volume": 1.5,
        "mass": 1050.0,
        "total_volatile_solids": 40.0,
        "pen_manure_data": None,
    }
    mock_om = mocker.patch.object(mock_separator, "_om", autospec=True)
    mock_separator._log_manure_stream(manure_dict, "test_stream", time)

    mock_om.add_variable.assert_any_call(
        "test_stream.manure_water",
        1000.0,
        {
            "class": "Separator",
            "function": "_log_manure_stream",
            "prefix": mock_separator._prefix,
            "simulation_day": 42,
            "units": MeasurementUnits.KILOGRAMS,
        },
    )


def test_log_manure_stream_invalid_type(mock_separator: Separator, time: Time, mocker: MockerFixture) -> None:
    """Test error logging and ValueError when manure_stream is an invalid type."""
    invalid_input = cast("ManureStream | dict[str, float | None]", "invalid_string")
    mock_om = mocker.patch.object(mock_separator, "_om", autospec=True)
    with pytest.raises(ValueError, match="Manure stream must be a dictionary or a ManureStream instance"):
        mock_separator._log_manure_stream(invalid_input, "error_stream", time)

    mock_om.add_error.assert_called_once_with(
        "Manure Stream Type Error",
        "This function requires either a ManureStream instance or a dictionary.",
        {
            "class": "Separator",
            "function": "_log_manure_stream",
            "prefix": mock_separator._prefix,
            "simulation_day": 42,
        },
    )


def test_log_manure_stream_mismatched_keys(mock_separator: Separator, time: Time, mocker: MockerFixture) -> None:
    """Test error logging and ValueError when manure_stream_dict keys do not match MANURE_STREAM_UNITS."""
    invalid_manure_dict: dict[str, float | None] = {"wrong_key": 42.0}
    mock_om = mocker.patch.object(mock_separator, "_om", autospec=True)
    with pytest.raises(ValueError, match="Manure Stream must contain the same keys as manure_stream_units"):
        mock_separator._log_manure_stream(invalid_manure_dict, "mismatch_stream", time)

    mock_om.add_error.assert_called_once_with(
        "Manure Stream Keys Error",
        f"Expected keys: {set(mock_separator.MANURE_STREAM_UNITS.keys())}, received: {{'wrong_key'}}.",
        {
            "class": "Separator",
            "function": "_log_manure_stream",
            "prefix": mock_separator._prefix,
            "simulation_day": 42,
        },
    )
