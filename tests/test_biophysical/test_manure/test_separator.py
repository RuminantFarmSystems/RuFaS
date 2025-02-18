import pytest
from typing import Any

from pytest_mock import MockerFixture

from RUFAS.biophysical.manure.processor import Processor
from RUFAS.biophysical.manure.separators.machine_separator import MachineSeparator
from RUFAS.biophysical.manure.separators.separator import Separator, SeparatorConfig
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants


def test_separator_config_initialization() -> None:
    """Test that SeparatorConfig initializes correctly with given values."""
    config = SeparatorConfig(
        water_efficiency=0.85,
        ammoniacal_nitrogen_efficiency=0.75,
        nitrogen_efficiency=0.80,
        phosphorus_efficiency=0.65,
        potassium_efficiency=0.70,
        ash_efficiency=0.55,
        non_degradable_volatile_solids_efficiency=0.60,
        degradable_volatile_solids_efficiency=0.50,
        total_solids_efficiency=0.90
    )

    assert config.water_efficiency == 0.85
    assert config.ammoniacal_nitrogen_efficiency == 0.75
    assert config.nitrogen_efficiency == 0.80
    assert config.phosphorus_efficiency == 0.65
    assert config.potassium_efficiency == 0.70
    assert config.ash_efficiency == 0.55
    assert config.non_degradable_volatile_solids_efficiency == 0.60
    assert config.degradable_volatile_solids_efficiency == 0.50
    assert config.total_solids_efficiency == 0.90


def test_separator_initialization() -> None:
    """Test that Separator initializes correctly with valid inputs."""
    config = SeparatorConfig(
        water_efficiency=0.85,
        ammoniacal_nitrogen_efficiency=0.75,
        nitrogen_efficiency=0.80,
        phosphorus_efficiency=0.65,
        potassium_efficiency=0.70,
        ash_efficiency=0.55,
        non_degradable_volatile_solids_efficiency=0.60,
        degradable_volatile_solids_efficiency=0.50,
        total_solids_efficiency=0.90
    )

    separator = Separator(config)

    assert isinstance(separator, Separator)
    assert isinstance(separator, Processor)
    assert separator.config == config
    assert separator.is_housing_emissions_calculator is False
    assert separator.held_manure is None


@pytest.mark.parametrize(
    "initial_manure, new_manure, expected",
    [
        # Initial state is None, first manure stream is fully stored
        (
            None,
            ManureStream(10, 2, 3, 4, 5, 6, 7, 8, 9, 1.5, None),
            ManureStream(10, 2, 3, 4, 5, 6, 7, 8, 9, 1.5, None)
        ),
        # Accumulation: Two manure streams are added together
        (
            ManureStream(5, 1, 2, 3, 4, 5, 6, 7, 8, 0.8, None),
            ManureStream(10, 2, 3, 4, 5, 6, 7, 8, 9, 1.5, None),
            ManureStream(15, 3, 5, 7, 9, 11, 13, 15, 17, 2.3, None)
        ),
        # Adding to an empty manure stream
        (
            ManureStream(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, None),
            ManureStream(10, 2, 3, 4, 5, 6, 7, 8, 9, 1.5, None),
            ManureStream(10, 2, 3, 4, 5, 6, 7, 8, 9, 1.5, None)
        ),
    ],
)
def test_receive_manure_accumulation(initial_manure: Any, new_manure: ManureStream, expected: ManureStream) -> None:
    """Test that manure is correctly stored and accumulated in Separator."""
    config = SeparatorConfig(
        water_efficiency=0.85,
        ammoniacal_nitrogen_efficiency=0.75,
        nitrogen_efficiency=0.80,
        phosphorus_efficiency=0.65,
        potassium_efficiency=0.70,
        ash_efficiency=0.55,
        non_degradable_volatile_solids_efficiency=0.60,
        degradable_volatile_solids_efficiency=0.50,
        total_solids_efficiency=0.90
    )
    separator = Separator(config)
    separator.held_manure = initial_manure

    separator.receive_manure(new_manure)

    assert separator.held_manure == expected, f"Expected {expected.amount}, got {separator.held_manure.amount}"


@pytest.fixture
def separator(mocker: MockerFixture) -> Separator:
    """Fixture to create a Separator instance with a default config."""
    config = SeparatorConfig(
        water_efficiency=0.85,
        ammoniacal_nitrogen_efficiency=0.75,
        nitrogen_efficiency=0.80,
        phosphorus_efficiency=0.65,
        potassium_efficiency=0.70,
        ash_efficiency=0.55,
        non_degradable_volatile_solids_efficiency=0.60,
        degradable_volatile_solids_efficiency=0.50,
        total_solids_efficiency=0.90
    )
    separator = Separator(config)
    separator._separate_manure = mocker.MagicMock(return_value={"solid": ManureStream(), "liquid": ManureStream()})
    return separator


def test_separate_manure_not_implemented() -> None:
    """Test that calling `_separate_manure()` directly on Separator raises NotImplementedError."""
    config = SeparatorConfig(
        water_efficiency=0.85,
        ammoniacal_nitrogen_efficiency=0.75,
        nitrogen_efficiency=0.80,
        phosphorus_efficiency=0.65,
        potassium_efficiency=0.70,
        ash_efficiency=0.55,
        non_degradable_volatile_solids_efficiency=0.60,
        degradable_volatile_solids_efficiency=0.50,
        total_solids_efficiency=0.90
    )
    separator = Separator(config)
    with pytest.raises(NotImplementedError, match="Subclasses must implement this method."):
        separator._separate_manure()


@pytest.mark.parametrize(
    "held_manure, expected",
    [
        # No manure (should return empty manure streams)
        (None, {"solid": ManureStream(), "liquid": ManureStream()}),
        # Zero manure (should return empty manure streams)
        (ManureStream(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, None), {"solid": ManureStream(), "liquid": ManureStream()}),
    ],
)
def test_process_manure_no_manure(separator: Separator, held_manure: Any, expected: dict[str, ManureStream],
                                  mocker: MockerFixture) -> None:
    """Test that processing with no manure returns empty streams."""
    separator.held_manure = held_manure  # Set initial state
    mock_time = mocker.MagicMock()
    mock_conditions = mocker.MagicMock()
    result = separator.process_manure(mock_conditions, mock_time)

    assert result == expected, f"Expected {expected}, got {result}"
    separator._separate_manure.assert_not_called()


def test_process_manure_with_manure(separator: Separator, mocker: MockerFixture) -> None:
    """Test that manure processing calls `_separate_manure()` and returns its result."""
    separator.held_manure = ManureStream(10, 2, 3, 4, 5, 6, 7, 8, 9, 1.5, None)
    mock_time = mocker.MagicMock()
    mock_conditions = mocker.MagicMock()
    expected_result = {"solid": ManureStream(), "liquid": ManureStream()}
    separator._separate_manure.return_value = expected_result

    result = separator.process_manure(mock_conditions, mock_time)

    separator._separate_manure.assert_called_once()
    assert result == expected_result, f"Expected {expected_result}, got {result}"


@pytest.fixture
def machine_separator() -> MachineSeparator:
    """Fixture to create a MachineSeparator instance."""
    config = SeparatorConfig(
        water_efficiency=0.85,
        ammoniacal_nitrogen_efficiency=0.75,
        nitrogen_efficiency=0.80,
        phosphorus_efficiency=0.65,
        potassium_efficiency=0.70,
        ash_efficiency=0.55,
        non_degradable_volatile_solids_efficiency=0.60,
        degradable_volatile_solids_efficiency=0.50,
        total_solids_efficiency=0.90
    )
    separator = MachineSeparator(config)
    separator.held_manure = ManureStream(
        water=100,
        ammoniacal_nitrogen=10,
        nitrogen=20,
        phosphorus=30,
        potassium=40,
        ash=50,
        non_degradable_volatile_solids=60,
        degradable_volatile_solids=70,
        total_solids=80,
        volume=5,
        pen_manure_data=None
    )
    return separator


def test_separate_manure_output_structure(machine_separator: MachineSeparator) -> None:
    """Test that `_separate_manure()` returns the expected dictionary structure."""
    result = machine_separator._separate_manure()

    assert isinstance(result, dict), "Output should be a dictionary"
    assert "solid" in result and "liquid" in result, "Returned dictionary should have 'solid' and 'liquid' keys"
    assert isinstance(result["solid"], ManureStream), "Solid stream should be a ManureStream instance"
    assert isinstance(result["liquid"], ManureStream), "Liquid stream should be a ManureStream instance"


def test_separate_manure_correct_calculations(machine_separator: MachineSeparator) -> None:
    """Test that `_separate_manure()` correctly applies efficiency calculations."""
    result = machine_separator._separate_manure()

    solid_expected = ManureStream(
        water=100 * machine_separator.config.water_efficiency,
        ammoniacal_nitrogen=10 * machine_separator.config.ammoniacal_nitrogen_efficiency,
        nitrogen=20 * machine_separator.config.nitrogen_efficiency,
        phosphorus=30 * machine_separator.config.phosphorus_efficiency,
        potassium=40 * machine_separator.config.potassium_efficiency,
        ash=50 * machine_separator.config.ash_efficiency,
        non_degradable_volatile_solids=60 * machine_separator.config.non_degradable_volatile_solids_efficiency,
        degradable_volatile_solids=70 * machine_separator.config.degradable_volatile_solids_efficiency,
        total_solids=80 * machine_separator.config.total_solids_efficiency,
        volume=5 * ManureConstants.SOLID_MANURE_DENSITY,
        pen_manure_data=None
    )

    liquid_expected = ManureStream(
        water=100 * (1 - machine_separator.config.water_efficiency),
        ammoniacal_nitrogen=10 * (1 - machine_separator.config.ammoniacal_nitrogen_efficiency),
        nitrogen=20 * (1 - machine_separator.config.nitrogen_efficiency),
        phosphorus=30 * (1 - machine_separator.config.phosphorus_efficiency),
        potassium=40 * (1 - machine_separator.config.potassium_efficiency),
        ash=50 * (1 - machine_separator.config.ash_efficiency),
        non_degradable_volatile_solids=60 * (1 - machine_separator.config.non_degradable_volatile_solids_efficiency),
        degradable_volatile_solids=70 * (1 - machine_separator.config.degradable_volatile_solids_efficiency),
        total_solids=80 * (1 - machine_separator.config.total_solids_efficiency),
        volume=5 * ManureConstants.LIQUID_MANURE_DENSITY,
        pen_manure_data=None
    )

    assert result["solid"] == solid_expected, f"Expected {solid_expected}, got {result['solid']}"
    assert result["liquid"] == liquid_expected, f"Expected {liquid_expected}, got {result['liquid']}"


def test_separate_manure_raises_error_on_none(machine_separator: MachineSeparator) -> None:
    """Test that `_separate_manure()` raises ValueError if `held_manure` is None."""
    machine_separator.held_manure = None

    with pytest.raises(ValueError, match="Cannot separate manure when 'held_manure' is None."):
        machine_separator._separate_manure()
