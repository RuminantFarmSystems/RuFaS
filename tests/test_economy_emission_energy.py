from typing import Dict, List, Tuple
import pytest
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.economy_emission_energy import EconomyEneregyEmission

IM = InputManager()
OM = OutputManager()


@pytest.fixture
def economy_instance():
    return EconomyEneregyEmission()


def fuel_consumption_scenarios() -> Tuple[str, List[Tuple[Dict[str, float], float]]]:
    return (
        "inputs, expected_consumption",
        [
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
                10.0,  # Expected consumption for the given inputs
            ),
            # Test case 2: Zero values for all inputs
            (
                {
                    "acre_size": 0.0,
                    "drawbar_speed": 0.0,
                    "field_capacity": 0.0,
                    "functional_draft": 0.0,
                    "harvest_yield": 0.0,
                    "IFSM_operation_data_E": 0.0,
                    "IFMS_operation_data_F": 0.0,
                    "IFSM_operation_data_G": 0.0,
                    "IFSM_operation_data_width": 0.0,
                    "implement_mass": 0.0,
                    "total_time": 0.0,
                    "tractor_mass": 0.0,
                    "tractor_PTO": 0.0,
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
                10000.0,  # Expected consumption for high inputs
            ),
        ],
    )


@pytest.mark.parametrize(fuel_consumption_scenarios())
def test_calculate_diesel_consumption(economy_instance, inputs, expected_consumption):
    actual_consumption = economy_instance._calculate_diesel_consumption(**inputs)
    assert pytest.approx(actual_consumption, rel=1e-3) == expected_consumption


class MockInputManager:
    def get_data(self, key):
        scn = fuel_consumption_scenarios()
        value_sets = scn[1]  # see fuel_consumption_scenarios() for details
        mock_data = {}
        for count, value_set in enumerate(value_sets):
            mock_data[f"scenario_{count}"] = value_set[0]
        return mock_data[key]


class MockOutputManager:
    def add_variable(self, name, value, info_map):
        # Do nothing for testing
        pass


def test_run_crop_management_fuel_consumption_scenarios(monkeypatch, economy_instance):
    monkeypatch.setattr(economy_instance, "IM", MockInputManager())
    monkeypatch.setattr(economy_instance, "OM", MockOutputManager())
    economy_instance.run_crop_management_fuel_consumption_scenarios()
    # assert correct calls to OM.add_variable() are made
