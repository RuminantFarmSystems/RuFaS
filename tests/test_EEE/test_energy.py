from typing import Any
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.EEE.energy import EnergyEstimator
from RUFAS.EEE.tractor import Tractor
from RUFAS.EEE.tractor_implement import TractorImplement
from RUFAS.data_structures.tillage_implements import TractorSize, FieldOperationEvent, TillageImplement
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from tests.test_EEE.fixtures import (
    parsed_diesel_consumption_inputs,
    EEE_constants,
    tractor_dataset,
    filtered_variable_pool
)

assert parsed_diesel_consumption_inputs is not None
assert EEE_constants is not None
assert tractor_dataset is not None
assert filtered_variable_pool is not None


def test_estimate_all(
        parsed_diesel_consumption_inputs: list[dict[str, Any]],
        EEE_constants: list[dict[str, Any]],
        tractor_dataset: dict[str, list[Any]],
        mocker: MockerFixture
) -> None:
    """Tests the estimation routines are called correctly."""
    im, om = InputManager(), OutputManager()
    mock_parse_inputs_for_diesel_consumption_calculation = mocker.patch.object(
        EnergyEstimator,
        "parse_inputs_for_diesel_consumption_calculation",
        return_value=parsed_diesel_consumption_inputs
    )
    mock_calculate_diesel_consumption = mocker.patch.object(
        EnergyEstimator,
        "calculate_diesel_consumption",
        return_value=10
    )
    mock_report_diesel_consumption = mocker.patch.object(
        EnergyEstimator,
        "report_diesel_consumption"
    )

    def mock_get_data(data_address: str) -> Any:
        if data_address == "EEE_constants.constants":
            return EEE_constants
        elif data_address == "tractor_dataset":
            return tractor_dataset
        else:
            return 10

    mocker.patch.object(
        im,
        "get_data",
        side_effect=mock_get_data
    )
    mock_om_add_variable = mocker.patch.object(om, "add_variable")

    EnergyEstimator.estimate_all()

    mock_parse_inputs_for_diesel_consumption_calculation.assert_called_once_with()
    assert mock_calculate_diesel_consumption.call_count == len(parsed_diesel_consumption_inputs)
    assert mock_report_diesel_consumption.call_count == len(parsed_diesel_consumption_inputs)
    mock_om_add_variable.assert_called_once()


@pytest.mark.parametrize(
    "diesel_consumption_data, expected_add_variable_calls",
    [
        (
            {
                "operation_event": FieldOperationEvent.HARVEST,
                "operation_year": 2018,
                "operation_day": 18,
                "field_name": "dummy_field",
                "crop_type": "alfalfa_hay",
                "field_production_size": 188,
                "crop_yield": 1.8,
                "application_depth": None,
                "mass": None,
                "tillage_implement": None,
            },
            5 + 2
        ),
        (
            {
                "operation_event": FieldOperationEvent.PLANTING,
                "operation_year": 2018,
                "operation_day": 18,
                "field_name": "dummy_field",
                "crop_type": "alfalfa_hay",
                "field_production_size": 188,
                "crop_yield": None,
                "application_depth": None,
                "mass": None,
                "tillage_implement": None,
            },
            5 + 1
        ),
        (
            {
                "operation_event": FieldOperationEvent.MANURE_APPLICATION,
                "operation_year": 2018,
                "operation_day": 18,
                "field_name": "dummy_field",
                "crop_type": None,
                "field_production_size": 188,
                "crop_yield": None,
                "application_depth": 10,
                "mass": 8.8,
                "tillage_implement": None,
            },
            5 + 2
        ),
        (
            {
                "operation_event": FieldOperationEvent.FERTILIZER_APPLICATION,
                "operation_year": 2018,
                "operation_day": 18,
                "field_name": "dummy_field",
                "crop_type": None,
                "field_production_size": 188,
                "crop_yield": None,
                "application_depth": 10,
                "mass": 8.8,
                "tillage_implement": None,
            },
            5 + 2
        ),
        (
            {
                "operation_event": FieldOperationEvent.TILLING,
                "operation_year": 2018,
                "operation_day": 18,
                "field_name": "dummy_field",
                "crop_type": None,
                "field_production_size": 188,
                "crop_yield": None,
                "application_depth": 10,
                "mass": None,
                "tillage_implement": TillageImplement.DISK_HARROW,
            },
            5 + 2
        ),
    ]
)
def test_report_diesel_consumption(
        diesel_consumption_data: dict[str, Any],
        expected_add_variable_calls: int,
        mocker: MockerFixture
) -> None:
    """Tests the diesel consumption report function."""
    om = OutputManager()
    mock_om_add_variable = mocker.patch.object(om, "add_variable")

    ee = EnergyEstimator()
    ee.report_diesel_consumption(
        diesel_consumption_data=diesel_consumption_data,
        herd_size=18,
        tractor_size=TractorSize.SMALL,
        diesel_consumption_tractor_implement_liter_per_ton=10
    )

    assert mock_om_add_variable.call_count == expected_add_variable_calls


def test_parse_inputs_for_diesel_consumption_calculation(
        filtered_variable_pool: dict[str, Any],
        parsed_diesel_consumption_inputs: list[dict[str, Any]],
        mocker: MockerFixture,
) -> None:
    """Tests the diesel consumption calculation inputs are parsed correctly."""
    om = OutputManager()
    mocker.patch.object(
        om,
        "filter_variables_pool",
        side_effect=filtered_variable_pool
    )

    ee = EnergyEstimator()
    result = ee.parse_inputs_for_diesel_consumption_calculation()
    assert result == parsed_diesel_consumption_inputs


@pytest.mark.parametrize(
    "crop_yield, field_production_size, clay_percent, applications_mass, application_dm_content, expected_result",
    [
        (100, 50, 20, 500, 0.5, 0.14476319 * 2),
        (150, 75, 30, 750, 0.6, 0.09650879 * 2),
        (200, 100, 40, None, None, 0.07238159 * 2),
    ]
)
def test_calculate_diesel_consumption(
        crop_yield: float,
        field_production_size: float,
        clay_percent: float,
        applications_mass: float | None,
        application_dm_content: float | None,
        expected_result: float,
        mocker: MockerFixture
) -> None:
    """Tests the diesel consumption calculation is performed correctly."""
    tractor = MagicMock(auto_spec=Tractor)
    implement_1, implement_2 = MagicMock(auto_spec=TractorImplement), MagicMock(auto_spec=TractorImplement)
    mocker.patch.object(implement_1, "calculate_operation_time_hr", return_value=1.8)
    mocker.patch.object(implement_2, "calculate_operation_time_hr", return_value=1.8)
    tractor.implements = [implement_1, implement_2]

    ee = EnergyEstimator()
    mock_calculate_total_power_needed = mocker.patch.object(ee, "_calculate_total_power_needed", return_value=18)

    result = ee.calculate_diesel_consumption(
        crop_yield, field_production_size, tractor, clay_percent, applications_mass, application_dm_content
    )

    assert mock_calculate_total_power_needed.call_count == 2
    assert result == pytest.approx(expected_result)


def test_calculate_total_power_needed(mocker: MockerFixture) -> None:
    """Tests the total power needed is calculated correctly."""
    tractor, implement = MagicMock(auto_spec=Tractor), MagicMock(auto_spec=TractorImplement)
    mock_calculate_axel_power = mocker.patch.object(tractor, "calculate_axel_power", return_value=18)
    mock_calculate_drawbar_power = mocker.patch.object(implement, "calculate_drawbar_power", return_value=25)
    mock_calculate_needed_PTO = mocker.patch.object(implement, "calculate_needed_PTO", return_value=10)

    ee = EnergyEstimator()
    result = ee._calculate_total_power_needed(tractor, implement, 1.1, 2.2, 3.3, 4.4)

    mock_calculate_axel_power.assert_called_once_with(implement)
    mock_calculate_drawbar_power.assert_called_once_with(3.3)
    mock_calculate_needed_PTO.assert_called_once_with(1.1, 2.2, 4.4)
    assert result == pytest.approx(18 + 25 + 10)
