from typing import Dict, List, Tuple
from mock import call
import pytest
from pytest_mock import MockerFixture
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.economy_emission_energy import EconomyEneregyEmission

IM = InputManager()
OM = OutputManager()


def fuel_consumption_scenarios() -> List[Tuple[Dict[str, float], float]]:
    return [
        # Test case 1: Normal scenario with average inputs
        (
            {
                "acre_size": 10.0,
                "drawbar_speed": 8.0,
                "field_capacity": 30.0,
                "functional_draft": 1000.0,
                "harvest_yield": 5.0,
                "IFSM_operation_data_E": 100.0,
                "IFMS_operation_data_F": 0.1,
                "IFSM_operation_data_G": 0.5,
                "IFSM_operation_data_width": 1.2,
                "implement_mass": 300.0,
                "total_time": 8.0,
                "tractor_mass": 1500.0,
                "tractor_PTO": 90.0,
                "tractor_speed": 25.0,
            },
            52138.6233277905,  # Expected consumption for the given inputs
        ),
        # Test case 2: Zero values for all inputs
        # acre_size, field_capacity, harvest_yield, total_time, and tractor_PTO can't be zero
        (
            {
                "acre_size": 1.0,
                "drawbar_speed": 0.0,
                "field_capacity": 1.0,
                "functional_draft": 0.0,
                "harvest_yield": 1.0,
                "IFSM_operation_data_E": 0.0,
                "IFMS_operation_data_F": 0.0,
                "IFSM_operation_data_G": 0.0,
                "IFSM_operation_data_width": 0.0,
                "implement_mass": 0.0,
                "total_time": 1.0,
                "tractor_mass": 0.0,
                "tractor_PTO": 1.0,
                "tractor_speed": 0.0,
            },
            0.0,  # Expected consumption for zero inputs
        ),
        # Test case 3: High values for all inputs
        (
            {
                "acre_size": 10000.0,
                "drawbar_speed": 1000.0,
                "field_capacity": 500.0,
                "functional_draft": 20000.0,
                "harvest_yield": 2000.0,
                "IFSM_operation_data_E": 1000000.0,
                "IFMS_operation_data_F": 1000000.0,
                "IFSM_operation_data_G": 1000000.0,
                "IFSM_operation_data_width": 1000.0,
                "implement_mass": 100000.0,
                "total_time": 100.0,
                "tractor_mass": 1000000.0,
                "tractor_PTO": 10000.0,
                "tractor_speed": 500.0,
            },
            14927935750975.893,  # Expected consumption for high inputs
        ),
    ]


@pytest.fixture
def economy_instance() -> EconomyEneregyEmission:
    return EconomyEneregyEmission()


@pytest.mark.parametrize("inputs, expected_consumption", fuel_consumption_scenarios())
def test_calculate_diesel_consumption(
    economy_instance: EconomyEneregyEmission,
    inputs: Dict[str, float],
    expected_consumption: float,
) -> None:
    actual_consumption = economy_instance._calculate_diesel_consumption(**inputs)
    assert pytest.approx(actual_consumption, rel=1e-3) == expected_consumption


def test_run_crop_management_fuel_consumption_scenarios(
    economy_instance: EconomyEneregyEmission, mocker: MockerFixture
) -> None:
    # Arrange
    info_map = {
        "class": "EconomyEneregyEmission",
        "function": "run_crop_management_fuel_consumption_scenarios",
    }
    scenarios = fuel_consumption_scenarios()
    mock_data = {}
    expected_calls = []
    in_idx = 0
    out_idx = 1
    for count, value_set in enumerate(scenarios):
        scenario_name = f"scenario_{count}"
        mock_data[scenario_name] = value_set[in_idx]
        expected_calls.append(call(scenario_name, value_set[out_idx], info_map))
    mock_get_data = mocker.patch(
        "RUFAS.economy_emission_energy.IM.get_data", return_value=mock_data
    )
    mock_add_variable = mocker.patch("RUFAS.economy_emission_energy.OM.add_variable")
    # Act
    economy_instance.run_crop_management_fuel_consumption_scenarios()
    # Assert
    mock_get_data.assert_called_once_with(
        "EEE.crop_management_fuel_consumption_scenarios"
    )
    assert mock_add_variable.call_args_list == expected_calls
