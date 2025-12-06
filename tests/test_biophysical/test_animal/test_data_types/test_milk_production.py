from unittest.mock import MagicMock
from RUFAS.biophysical.animal.data_types.milk_production import (
    MilkProductionInputs,
    MilkProductionOutputs,
    MilkProductionStatistics,
)
from RUFAS.units import MeasurementUnits
import pytest


def test_initialization_inputs_values() -> None:
    """Dataclass should store provided values correctly."""
    inputs = MilkProductionInputs(
        days_in_milk=10,
        days_born=500,
        days_in_pregnancy=150,
    )

    assert inputs.days_in_milk == 10
    assert inputs.days_born == 500
    assert inputs.days_in_pregnancy == 150


@pytest.mark.parametrize(
    "days_in_milk, expected",
    [
        (0, False),  # boundary: not milking
        (-1, False),  # unrealistic but should still return False
        (1, True),  # first day milking
        (100, True),  # typical milking period
    ],
)
def test_inputs_is_milking_property(days_in_milk: int, expected: bool) -> None:
    """Verify the is_milking property logic."""
    inputs = MilkProductionInputs(
        days_in_milk=days_in_milk,
        days_born=200,
        days_in_pregnancy=0,
    )
    assert inputs.is_milking is expected


def test_initialization_outputs_values() -> None:
    """Dataclass should store provided values correctly."""
    mock_events = MagicMock()

    outputs = MilkProductionOutputs(
        events=mock_events,
        days_in_milk=25,
    )

    assert outputs.events is mock_events
    assert outputs.days_in_milk == 25


@pytest.mark.parametrize(
    "days_in_milk, expected",
    [
        (0, False),  # boundary: not milking
        (-1, False),  # still False for negative (even if unrealistic)
        (1, True),  # first day milking
        (250, True),  # well into lactation
    ],
)
def test_outputs_is_milking_property(days_in_milk: int, expected: bool) -> None:
    """Verify the is_milking property logic."""
    mock_events = MagicMock()

    outputs = MilkProductionOutputs(
        events=mock_events,
        days_in_milk=days_in_milk,
    )

    assert outputs.is_milking is expected


def test_statistics_initializes_with_given_values() -> None:
    """MilkProductionStatistics should preserve all initialization arguments."""
    stats = MilkProductionStatistics(
        cow_id=101,
        pen_id=3,
        days_in_milk=45,
        estimated_daily_milk_produced=32.5,
        milk_protein=1.1,
        milk_fat=1.3,
        milk_lactose=1.5,
        parity=2,
    )

    assert stats.cow_id == 101
    assert stats.pen_id == 3
    assert stats.days_in_milk == 45
    assert stats.estimated_daily_milk_produced == 32.5
    assert stats.milk_protein == 1.1
    assert stats.milk_fat == 1.3
    assert stats.milk_lactose == 1.5
    assert stats.parity == 2


@pytest.mark.parametrize(
    "days_in_milk, expected_flag",
    [
        (0, False),  # boundary: not milking
        (-5, False),  # negative days should still be treated as not milking
        (1, True),  # just started milking
        (250, True),  # mid/late lactation
    ],
)
def test_statistics_milking_status_flag(days_in_milk: int, expected_flag: bool) -> None:
    """is_milking should reflect whether days_in_milk is greater than zero."""
    stats = MilkProductionStatistics(
        cow_id=101,
        pen_id=3,
        days_in_milk=days_in_milk,
        estimated_daily_milk_produced=25.0,
        milk_protein=1.0,
        milk_fat=1.2,
        milk_lactose=1.4,
        parity=1,
    )

    assert stats.is_milking is expected_flag


def test_statistics_units_mapping_is_consistent() -> None:
    """UNITS dict should contain expected keys and associated measurement units."""
    expected_units = {
        "cow_id": MeasurementUnits.UNITLESS,
        "pen_id": MeasurementUnits.UNITLESS,
        "days_in_milk": MeasurementUnits.DAYS,
        "estimated_daily_milk_produced": MeasurementUnits.KILOGRAMS_PER_DAY,
        "milk_protein": MeasurementUnits.KILOGRAMS_PER_DAY,
        "milk_fat": MeasurementUnits.KILOGRAMS_PER_DAY,
        "milk_lactose": MeasurementUnits.KILOGRAMS_PER_DAY,
        "parity": MeasurementUnits.UNITLESS,
        "is_milking": MeasurementUnits.UNITLESS,
        "simulation_day": MeasurementUnits.SIMULATION_DAY,
    }

    assert MilkProductionStatistics.UNITS == expected_units
