import pytest
from typing import Any

from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.biophysical.manure.separator.separator import Separator
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.units import MeasurementUnits


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
        processor_type="ScrewPress",
    )
    return separator


def test_separator_init_with_params(mock_separator: Separator) -> None:
    """Test the initialization of the Separator class with parameters."""
    assert mock_separator.name == "TestSeparator"
    assert mock_separator._prefix == "Manure.Separator.ScrewPress.TestSeparator"
    assert mock_separator.held_manure is None
    assert mock_separator.separated_solids_dry_matter == 0.8
    assert mock_separator.ammoniacal_nitrogen_efficiency == 0.7
    assert mock_separator.nitrogen_efficiency == 0.6
    assert mock_separator.phosphorus_efficiency == 0.5
    assert mock_separator.potassium_efficiency == 0.4
    assert mock_separator.ash_efficiency == 0.3
    assert mock_separator.volatile_solids_efficiency == 0.2
    assert mock_separator.total_solids_efficiency == 0.1


@pytest.mark.parametrize(
    "initial_manure, new_manure, expected",
    [
        # Initial state is None, first manure stream is fully stored
        (
            None,
            ManureStream(10, 2, 3, 4, 5, 6, 8, 7, 10, 9, 1.5, 0.24, None),
            ManureStream(10, 2, 3, 4, 5, 6, 8, 7, 10, 9, 1.5, 0.24, None),
        ),
        # Accumulation: Two manure streams are added together
        (
            ManureStream(5, 1, 2, 3, 4, 5, 7, 6, 10, 8, 0.8, 0.24, None),
            ManureStream(10, 2, 3, 4, 5, 6, 8, 7, 10, 9, 1.5, 0.24, None),
            ManureStream(15, 3, 5, 7, 9, 11, 15, 13, 20, 17, 2.3, 0.24, None),
        ),
        # Adding to an empty manure stream
        (
            ManureStream(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.24, None),
            ManureStream(10, 2, 3, 4, 5, 6, 8, 7, 10, 9, 1.5, 0.24, None),
            ManureStream(10, 2, 3, 4, 5, 6, 8, 7, 10, 9, 1.5, 0.24, None),
        ),
    ],
)
def test_receive_manure_accumulation(
    initial_manure: Any, new_manure: ManureStream, expected: ManureStream, mock_separator: Separator
) -> None:
    """Test that manure is correctly stored and accumulated in Separator."""
    mock_separator.held_manure = initial_manure

    mock_separator.receive_manure(new_manure)

    assert mock_separator.held_manure == expected, f"Expected {expected}, got {mock_separator.held_manure}"


@pytest.fixture
def mock_manure_stream() -> ManureStream:
    """ManureStream object for testing."""
    return ManureStream(
        water=100.0,
        ammoniacal_nitrogen=50.0,
        nitrogen=80.0,
        phosphorus=40.0,
        potassium=30.0,
        ash=20.0,
        non_degradable_volatile_solids=10.0,
        degradable_volatile_solids=15.0,
        total_solids=70.0,
        volume=200.0,
        methane_production_potential=0.24,
        pen_manure_data=None,
        bedding_non_degradable_volatile_solids=10
    )


def test_process_manure(mock_separator: Separator, mocker: MockerFixture, mock_manure_stream: ManureStream) -> None:
    """Test the process_manure method to ensure correct separation."""
    # Arrange
    mock_separator.held_manure = mock_manure_stream
    mock_conditions = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_report_manure_stream = mocker.patch.object(mock_separator, "_report_manure_stream", autospec=True)

    # Act
    result: dict[str, ManureStream] = mock_separator.process_manure(mock_conditions, mock_time)

    # Assert
    assert isinstance(result, dict)
    assert "solid" in result
    assert "liquid" in result
    assert isinstance(result["solid"], ManureStream)
    assert isinstance(result["liquid"], ManureStream)

    solid = result["solid"]
    assert solid.total_solids == mock_manure_stream.total_solids * mock_separator.total_solids_efficiency
    assert solid.water == solid.total_solids / 0.8 - solid.total_solids
    assert solid.ammoniacal_nitrogen == (
        mock_manure_stream.ammoniacal_nitrogen * mock_separator.ammoniacal_nitrogen_efficiency
    )
    assert solid.nitrogen == mock_manure_stream.nitrogen * mock_separator.nitrogen_efficiency
    assert solid.phosphorus == mock_manure_stream.phosphorus * mock_separator.phosphorus_efficiency
    assert solid.potassium == mock_manure_stream.potassium * mock_separator.potassium_efficiency
    assert solid.ash == mock_manure_stream.ash * mock_separator.ash_efficiency
    assert solid.volume == (solid.water + solid.total_solids) / ManureConstants.SOLID_MANURE_DENSITY

    liquid = result["liquid"]
    assert liquid.water == mock_manure_stream.water - solid.water
    assert liquid.total_solids == mock_manure_stream.total_solids * (1 - mock_separator.total_solids_efficiency)
    assert liquid.ammoniacal_nitrogen == (
        mock_manure_stream.ammoniacal_nitrogen * (1 - mock_separator.ammoniacal_nitrogen_efficiency)
    )
    assert liquid.nitrogen == mock_manure_stream.nitrogen * (1 - mock_separator.nitrogen_efficiency)
    assert liquid.phosphorus == mock_manure_stream.phosphorus * (1 - mock_separator.phosphorus_efficiency)
    assert liquid.potassium == mock_manure_stream.potassium * (1 - mock_separator.potassium_efficiency)
    assert liquid.ash == mock_manure_stream.ash * (1 - mock_separator.ash_efficiency)
    assert liquid.volume == (liquid.water + liquid.total_solids) / ManureConstants.LIQUID_MANURE_DENSITY

    assert mock_separator.held_manure is None
    assert mock_report_manure_stream.call_count == 2


def test_process_manure_empty_held_manure(mocker: MockerFixture, mock_separator: Separator) -> None:
    """Test that process_manure correctly handles an empty manure separator."""
    # Arrange
    mock_separator.held_manure = None
    mock_conditions = mocker.MagicMock()
    mock_time = mocker.MagicMock()
    mock_om = mocker.patch.object(mock_separator, "_om", autospec=True)

    # Act
    result = mock_separator.process_manure(mock_conditions, mock_time)

    # Assert
    assert result == {}
    mock_om.add_variable.assert_called_once_with(
        "empty_separator_output",
        {},
        {
            "class": "Separator",
            "function": "process_manure",
            "prefix": "Manure.Separator.ScrewPress.TestSeparator",
            "simulation_day": mock_time.simulation_day,
            "units": MeasurementUnits.UNITLESS,
        },
    )


def test_clear_held_manure(mock_separator: Separator) -> None:
    """Test that held_manure is cleared after calling clear_held_manure."""
    mock_separator.held_manure = ManureStream(10, 2, 3, 4, 5, 6, 7, 8, 9, 1.5, 0.24, None, 10)

    mock_separator.clear_held_manure()

    assert mock_separator.held_manure is None
