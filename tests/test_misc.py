"""
RUFAS: Ruminant Farm Systems Model
File name: test_misc.py
Description: Implements test cases
Author(s): Pooya Hekmati, sh2235@cornell.edu
"""

import os
from typing import Callable
from typing import Dict
from mock import Mock, mock_open, patch

import pytest
from mock.mock import MagicMock
from pytest import approx, raises
from pytest_mock.plugin import MockerFixture

from RUFAS.general_constants import GeneralConstants
from RUFAS.output_manager import OutputManager
from RUFAS.simulation_engine import SimulationEngine
from RUFAS.util import Utility


def test_annual_reset():
    """Unit test for function annual_reset in file classes.py"""
    pass


def test_annual_mass_balance():
    """Unit test for function annual_mass_balance in file classes.py"""
    pass


def test_calc_sim_length():
    """Unit test for function calc_sim_length in file classes.py"""
    pass


def test_to_str():
    """Unit test for function to_str in file classes.py"""
    pass


def test_advance():
    """Unit test for function advance in file classes.py"""
    pass


def test_end_year():
    """Unit test for function end_year in file classes.py"""
    pass


def test_end_simulation():
    """Unit test for function end_simulation in file classes.py"""
    pass


def test_general_constants() -> None:
    """Tests the general constants in file general_constants.py."""
    constants = GeneralConstants
    assert constants.GRAMS_TO_KG == approx(0.001)
    assert constants.LITERS_TO_CUBIC_METERS == approx(0.001)
    assert constants.KG_TO_CUBIC_METERS == approx(0.001)
    assert constants.DAYS_PER_YEAR == 365
    assert constants.SECONDS_PER_DAY == 86400
    assert constants.WATER_DENSITY_KG_PER_LITER == approx(0.997)
    assert constants.WATER_DENSITY_KG_PER_M3 == approx(0.997 * 0.001)


def test_is_leap_year():
    """Unit test for function is_leap_year in file classes.py"""
    pass


@pytest.fixture
def patch_simulation_engine(mocker: MockerFixture) -> SimulationEngine:
    """Returns a mocked SimulationEngine"""
    mocker.patch("RUFAS.simulation_engine.SimulationEngine._initialize_simulation")

    sim_eng = SimulationEngine("dummy_path")
    sim_eng.config = MagicMock()
    sim_eng.weather = MagicMock()
    sim_eng.time = MagicMock()
    sim_eng.state = MagicMock()
    sim_eng.output = MagicMock()

    return sim_eng


def test_init_simulation_engine(patch_simulation_engine: SimulationEngine) -> None:
    """Unit test for function __init__ in file RUFAS/simulation_engine.py"""
    patch_simulation_engine._initialize_simulation.assert_called_once_with("dummy_path")


def test_simulate(
    patch_simulation_engine: SimulationEngine, mocker: MockerFixture
) -> None:
    """Unit test for function simulate in file RUFAS/simulation_engine.py"""
    mocker.patch("RUFAS.simulation_engine.SimulationEngine._run_simulation_main_loop")
    mocker.patch("RUFAS.simulation_engine.SimulationEngine._show_final_messages")
    sim_eng = patch_simulation_engine
    sim_eng.simulate()
    sim_eng._run_simulation_main_loop.assert_called_once()
    sim_eng.output.finalize.assert_called_once_with(
        sim_eng.state, sim_eng.weather, sim_eng.time
    )
    sim_eng._show_final_messages.assert_called_once()


def test_show_final_messages(
    patch_simulation_engine: SimulationEngine, mocker: MockerFixture
) -> None:
    """Unit test for function _show_final_messages in file RUFAS/simulation_engine.py"""
    mocker.patch("sys.stdout.write")
    patch_simulation_engine._show_final_messages(1, 1)
    assert mocker._patches_and_mocks[1][1].call_count == 3


def test_daily_simulation(
    patch_simulation_engine: SimulationEngine, mocker: MockerFixture
) -> None:
    """Unit test for function _daily_simulation in file RUFAS/simulation_engine.py"""
    mocker.patch("RUFAS.routines.daily_animal_routine")
    mocker.patch("RUFAS.routines.daily_manure_storage_routine")
    mocker.patch("RUFAS.routines.daily_fields_routine")
    mocker.patch("RUFAS.routines.daily_feed_routine")
    mocker.patch("RUFAS.simulation_engine.SimulationEngine._advance_time")
    patch_simulation_engine._daily_simulation()
    assert patch_simulation_engine.output.daily_update.call_count == 1
    for mocked in mocker._patches_and_mocks:
        assert mocked[1].call_count == 1


def test_advance_time(
    patch_simulation_engine: SimulationEngine, mocker: MockerFixture
) -> None:
    """Unit test for function _advance_time in file RUFAS/simulation_engine.py"""
    mocker.patch("RUFAS.classes.Time.to_str")
    mocker.patch("RUFAS.classes.Time.advance")
    patch_simulation_engine.state.animal_management.simulation_day = 1
    patch_simulation_engine._advance_time(False)
    patch_simulation_engine._advance_time(True)
    assert patch_simulation_engine.time.advance.call_count == 2
    assert patch_simulation_engine.time.to_str.call_count == 1
    assert patch_simulation_engine.state.animal_management.simulation_day == 3


def test_input_prompt():
    """Unit test for function input_prompt in file user_prompt.py"""
    pass


def test_query():
    """Unit test for function query in file util.py"""
    pass


def test_get_base_dir():
    """Unit test for function get_base_dir in file util.py"""
    pass


def test_read_json_file():
    """Unit test for function read_json_file in file util.py"""
    pass


def test_LP_solve():
    """Unit test for function LP_solve in file util.py"""
    pass


def test_create_LP_problem():
    """Unit test for function create_LP_problem in file util.py"""
    pass


def test_is_correct_structure():
    """Unit test for function is_correct_structure in file util.py"""
    pass


def test_generate_LP_vars():
    """Unit test for function generate_LP_vars in file util.py"""
    pass


def test_add_LP_constraints():
    """Unit test for function add_LP_constraints in file util.py"""
    pass


def test_solve_with_fastest_solver():
    """Unit test for function solve_with_fastest_solver in file util.py"""
    pass


def test_organize_results():
    """Unit test for function organize_results in file util.py"""
    pass


def test_LP_print():
    """Unit test for function LP_print in file util.py"""
    pass


def test_calc_average() -> None:
    """Unit test for function calc_average in file util.py"""
    # Normal case
    result = Utility.calc_average(num_values=9, cur_avg=5, new_value=6)
    actual_new_num_values, actual_new_avg = result
    assert actual_new_num_values == 10
    assert actual_new_avg == approx(5.1)  # (9 * 5 + 6) / 10

    # Given a count of 0 and an average value of 0.0,
    # the function should return whatever the new value is.
    result = Utility.calc_average(num_values=0, cur_avg=0.0, new_value=6.0)
    actual_new_num_values, actual_new_avg = result
    assert actual_new_num_values == 1
    assert actual_new_avg == approx(6.0)


def test_remove_items_from_list_by_indices() -> None:
    """Unit test for function remove_items_from_list_by_indices in file util.py"""
    # Given an empty list and an empty list of removal indices,
    # the function should do nothing.
    arr = []
    del_idx = []
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert len(arr) == 0

    # Given a non-empty list and an empty list of removal indices,
    # the function should do nothing.
    arr = [0, 1, 2]
    del_idx = []
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert arr == [0, 1, 2]

    # Given a list of size 1 and the removal index of 0,
    # the function should return an empty list.
    arr = [0]
    del_idx = [0]
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert len(arr) == 0

    # Given a list of size 2 and one valid removal index,
    # the function should return a correct list of size 1.
    arr = [10, 20]
    del_idx = [0]
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert arr == [20]

    arr = [10, 20]
    del_idx = [1]
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert arr == [10]

    # Given a list of size 3 and a list of 2 removal indices,
    # the function should return a correct list of size 1.
    arr = [10, 20, 30]
    del_idx = [0, 1]
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert arr == [30]

    arr = [10, 20, 30]
    del_idx = [1, 2]
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert arr == [10]

    arr = [10, 20, 30]
    del_idx = [0, 2]
    Utility.remove_items_from_list_by_indices(arr, del_idx)
    assert arr == [20]

    # Given an empty list and a non-empty list of removal indices,
    # the function should raise IndexError.
    arr = []
    del_idx = [0]
    with raises(IndexError):
        Utility.remove_items_from_list_by_indices(arr, del_idx)


def test_percent_calculator() -> None:
    """Unit test for function percent_calculator in file util.py"""
    # Normal case
    # Given any random non-zero denominator,
    # the function should return correct percentages.
    pc = Utility.percent_calculator(denominator=20)
    assert pc(0) == approx(0.0)
    assert pc(20) == approx(100.0)
    assert pc(8) == approx(40.0)  # e.g., 8/20 = 40%
    assert pc(-8) == approx(-40.0)
    assert pc(24) == approx(120.0)

    # Given a denominator of 100,
    # the function should return the numerator as percentage.
    pc = Utility.percent_calculator(denominator=100)
    assert pc(0.0) == approx(0.0)
    assert pc(12.3) == approx(12.3)
    assert pc(100.0) == approx(100.0)

    # Given a 0 denominator, the function should raise a ZeroDivisionError.
    pc = Utility.percent_calculator(denominator=0)
    with raises(ZeroDivisionError):
        pc(1.0)


def test_get_prefix() -> None:
    """Unit test for function _get_prefix in file output_manager.py"""
    om = OutputManager()
    assert om._get_prefix("class", "func") == "class.func"


@pytest.fixture
def mock_output_manager(mocker) -> OutputManager:
    output_manager = OutputManager()
    return output_manager


def test_generate_key(mocker: MockerFixture) -> None:
    """Unit test for function _generate_key in file output_manager.py"""
    om = OutputManager()
    with raises(KeyError):
        om._generate_key("name", {})

    info_map = {"class": "dummy_class", "function": "dummy_func"}
    key = om._generate_key("key_name", info_map)
    assert key == "dummy_class.dummy_func.key_name"

    info_map["suppress_prefix"] = True
    key = om._generate_key("key_name", info_map)
    assert key == "key_name"

    info_map["suppress_prefix"] = False
    key = om._generate_key("key_name", info_map)
    assert key == "dummy_class.dummy_func.key_name"

    key = om._generate_key("key_name", info_map)
    assert key == "dummy_class.dummy_func.key_name"

    info_map["suppress_prefix"] = True
    key = om._generate_key("key_name", info_map)
    assert key == "key_name"

    info_map["prefix"] = "dummy_prefix"
    key = om._generate_key("key_name", info_map)
    assert key == "dummy_prefix.key_name"

    info_map["suffix"] = "dummy_suffix"
    key = om._generate_key("key_name", info_map)
    assert key == "dummy_prefix.key_name.dummy_suffix"


def test_add_error(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Unit test for function add_error in file output_manager.py"""
    key = "dummy_key"
    name = "dummy_name"
    value = "dummy_value"
    info_map = {}
    mock_output_manager._generate_key = MagicMock(return_value=key)
    mock_output_manager._add_to_pool = MagicMock()

    mock_output_manager.add_error(name, value, info_map)

    mock_output_manager._generate_key.assert_called_once_with(name, info_map)
    mock_output_manager._add_to_pool(
        mock_output_manager.errors_pool, key, value, info_map
    )

    mock_output_manager._generate_key = output_manager_original_method_states[
        "_generate_key"
    ]
    mock_output_manager._add_to_pool = output_manager_original_method_states[
        "_add_to_pool"
    ]


def test_add_warning(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Unit test for function add_warning in file output_manager.py"""
    key = "dummy_key"
    name = "dummy_name"
    value = "dummy_value"
    info_map = {}
    mock_output_manager._generate_key = MagicMock(return_value=key)
    mock_output_manager._add_to_pool = MagicMock()

    mock_output_manager.add_warning(name, value, info_map)

    mock_output_manager._generate_key.assert_called_once_with(name, info_map)
    mock_output_manager._add_to_pool(
        mock_output_manager.warnings_pool, key, value, info_map
    )

    mock_output_manager._generate_key = output_manager_original_method_states[
        "_generate_key"
    ]
    mock_output_manager._add_to_pool = output_manager_original_method_states[
        "_add_to_pool"
    ]


def test_add_log(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Unit test for function add_log in file output_manager.py"""
    key = "dummy_key"
    name = "dummy_name"
    value = "dummy_value"
    info_map = {}
    mock_output_manager._generate_key = MagicMock(return_value=key)
    mock_output_manager._add_to_pool = MagicMock()

    mock_output_manager.add_log(name, value, info_map)

    mock_output_manager._generate_key.assert_called_once_with(name, info_map)
    mock_output_manager._add_to_pool(
        mock_output_manager.logs_pool, key, value, info_map
    )

    mock_output_manager._generate_key = output_manager_original_method_states[
        "_generate_key"
    ]
    mock_output_manager._add_to_pool = output_manager_original_method_states[
        "_add_to_pool"
    ]


def test_add_variable(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Unit test for function add_variable in file output_manager.py"""
    key = "dummy_key"
    name = "dummy_name"
    value = "dummy_value"
    info_map = {}
    mock_output_manager._generate_key = MagicMock(return_value=key)
    mock_output_manager._add_to_pool = MagicMock()

    mock_output_manager.add_variable(name, value, info_map)

    mock_output_manager._generate_key.assert_called_once_with(name, info_map)
    mock_output_manager._add_to_pool(
        mock_output_manager.variables_pool, key, value, info_map
    )

    mock_output_manager._generate_key = output_manager_original_method_states[
        "_generate_key"
    ]
    mock_output_manager._add_to_pool = output_manager_original_method_states[
        "_add_to_pool"
    ]


def test_add_to_pool(mock_output_manager: OutputManager) -> None:
    """Unit test for function _add_to_pool in file output_manager.py"""
    info_map = {
        "class": "dummy_class",
        "function": "dummy_func",
        "context": "dummy_context",
    }
    key = "dummy_key"
    pool = {}
    mock_output_manager._add_to_pool(pool, key, "dummy_value1", info_map)
    assert pool[key] == {
        "info_maps": [{"context": "dummy_context"}],
        "values": ["dummy_value1"],
    }
    info_map["more_context"] = 1234567890
    mock_output_manager._add_to_pool(pool, key, "dummy_value2", info_map)
    assert pool[key] == {
        "info_maps": [
            {"context": "dummy_context"},
            {"context": "dummy_context", "more_context": 1234567890},
        ],
        "values": ["dummy_value1", "dummy_value2"],
    }


def test_output_manager_singleton(mocker: MockerFixture) -> None:
    """Test case to ensure output_manager is singleton"""
    key = "key1"
    om1 = OutputManager()
    om2 = OutputManager()
    mocker.patch.object(om1, "_generate_key", return_value=key)
    info_map = {
        "class": "dummy_class",
        "function": "dummy_func",
        "context": "dummy_context",
    }
    om1.add_variable("dummy_name", "dummy_value", info_map)
    assert om2.variables_pool[key] == {
        "info_maps": [{"context": "dummy_context"}],
        "values": ["dummy_value"],
    }


def test_flush_pools() -> None:
    """Test case for function flush_pools in output_manager.py"""
    om = OutputManager()
    info_map = {"class": "dummy_class", "function": "dummy_func"}
    om.add_variable("dummy_name", "dummy_value", info_map)
    om.add_log("dummy_name", "dummy_msg", info_map)
    om.add_warning("dummy_name", "dummy_msg", info_map)
    om.add_error("dummy_name", "dummy_msg", info_map)
    om.flush_pools()
    assert om.variables_pool == {}
    assert om.logs_pool == {}
    assert om.warnings_pool == {}
    assert om.errors_pool == {}


@pytest.fixture
def output_manager_original_method_states(
    mock_output_manager: OutputManager,
) -> Dict[str, Callable]:
    """Fixture to store original methods of OutputManager"""
    return {
        "_generate_file_name": mock_output_manager._generate_file_name,
        "_generate_key": mock_output_manager._generate_key,
        "_dict_to_file_json": mock_output_manager._dict_to_file_json,
        "_list_to_file_txt": mock_output_manager._list_to_file_txt,
        "_add_to_pool": mock_output_manager._add_to_pool,
        "_exclude_info_maps": mock_output_manager._exclude_info_maps,
        "_load_txt_file_to_list": mock_output_manager._load_txt_file_to_list,
        "_load_input_txt_file_names_to_list": mock_output_manager._load_input_txt_file_names_to_list,
        "_filter_variables_pool": mock_output_manager._filter_variables_pool,
        "save_variables": mock_output_manager.save_variables,
        "add_variable": mock_output_manager.add_variable,
        "add_error": mock_output_manager.add_error,
        "add_log": mock_output_manager.add_log,
        "add_warning": mock_output_manager.add_warning,
        "dump_variables": mock_output_manager.dump_variables,
        "dump_logs": mock_output_manager.dump_logs,
        "dump_warnings": mock_output_manager.dump_warnings,
        "dump_errors": mock_output_manager.dump_errors,
        "dump_variable_names_and_contexts": mock_output_manager.dump_variable_names_and_contexts,
    }


def test_dump_all_pools(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for function dump_all_pools in output_manager.py"""
    path = "dummy_path"
    mock_output_manager.dump_errors = MagicMock()
    mock_output_manager.dump_warnings = MagicMock()
    mock_output_manager.dump_logs = MagicMock()
    mock_output_manager.dump_variables = MagicMock()
    mock_output_manager.dump_variable_names_and_contexts = MagicMock()

    mock_output_manager.dump_all_pools(path, exclude_info_maps=False)

    mock_output_manager.dump_errors.assert_called_once_with(path)
    mock_output_manager.dump_warnings.assert_called_once_with(path)
    mock_output_manager.dump_logs.assert_called_once_with(path)
    mock_output_manager.dump_variables.assert_called_once_with(
        path, False
    )
    mock_output_manager.dump_variable_names_and_contexts.assert_called_once_with(path, False)

    mock_output_manager.dump_all_pools(path, exclude_info_maps=True)
    mock_output_manager.dump_variables.assert_called_with(path, True)
    mock_output_manager.dump_variable_names_and_contexts.assert_called_with(path, True)
    assert mock_output_manager.dump_logs.call_count == 2
    assert mock_output_manager.dump_warnings.call_count == 2
    assert mock_output_manager.dump_errors.call_count == 2

    # Restore original methods
    mock_output_manager.dump_variables = output_manager_original_method_states[
        "dump_variables"
    ]
    mock_output_manager.dump_logs = output_manager_original_method_states["dump_logs"]
    mock_output_manager.dump_warnings = output_manager_original_method_states[
        "dump_warnings"
    ]
    mock_output_manager.dump_errors = output_manager_original_method_states[
        "dump_errors"
    ]
    mock_output_manager.dump_variable_names_and_contexts = output_manager_original_method_states[
        "dump_variable_names_and_contexts"
    ]


def test_generate_file_name(mocker: MockerFixture) -> None:
    """Unit test for function _generate_file_name in file output_manager.py"""
    timestamp = "18-Jan-2023_Wed_22-38-14"
    mocker.patch("time.strftime", return_value=timestamp)
    base_name = "dummy_name"
    extension = "ext"
    om = OutputManager()
    assert (
        om._generate_file_name(base_name, extension)
        == f"{base_name}_{timestamp}.{extension}"
    )


def test_dump_variables(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for function dump_variables in output_manager.py"""
    mock_output_manager._generate_file_name = MagicMock(return_value="dummy_name")
    mock_output_manager._dict_to_file_json = MagicMock()

    mock_output_manager.dump_variables("dummy_path")

    mock_output_manager._generate_file_name.assert_called_once_with("all_variables", "json")
    mock_output_manager._dict_to_file_json.assert_called_once_with(
        mock_output_manager.variables_pool, os.path.join("dummy_path", "dummy_name")
    )

    # Restore original methods
    mock_output_manager._generate_file_name = output_manager_original_method_states[
        "_generate_file_name"
    ]
    mock_output_manager._dict_to_file_json = output_manager_original_method_states[
        "_dict_to_file_json"
    ]


def test_dump_logs(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for function dump_logs in output_manager.py"""
    mock_output_manager._generate_file_name = MagicMock(return_value="dummy_name")
    mock_output_manager._dict_to_file_json = MagicMock()

    mock_output_manager.dump_logs("dummy_path")

    mock_output_manager._generate_file_name.assert_called_once_with("logs", "json")
    mock_output_manager._dict_to_file_json.assert_called_once_with(
        mock_output_manager.logs_pool, os.path.join("dummy_path", "dummy_name")
    )

    # Restore original methods
    mock_output_manager._generate_file_name = output_manager_original_method_states[
        "_generate_file_name"
    ]
    mock_output_manager._dict_to_file_json = output_manager_original_method_states[
        "_dict_to_file_json"
    ]


def test_dump_warnings(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for function dump_warnings in output_manager.py"""
    mock_output_manager._generate_file_name = MagicMock(return_value="dummy_name")
    mock_output_manager._dict_to_file_json = MagicMock()

    mock_output_manager.dump_warnings("dummy_path")

    mock_output_manager._generate_file_name.assert_called_once_with("warnings", "json")
    mock_output_manager._dict_to_file_json.assert_called_once_with(
        mock_output_manager.warnings_pool, os.path.join("dummy_path", "dummy_name")
    )

    # Restore original methods
    mock_output_manager._generate_file_name = output_manager_original_method_states[
        "_generate_file_name"
    ]
    mock_output_manager._dict_to_file_json = output_manager_original_method_states[
        "_dict_to_file_json"
    ]


def test_dump_errors(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for function dump_errors in output_manager.py"""
    mock_output_manager._generate_file_name = MagicMock(return_value="dummy_name")
    mock_output_manager._dict_to_file_json = MagicMock()

    mock_output_manager.dump_errors("dummy_path")

    mock_output_manager._generate_file_name.assert_called_once_with("errors", "json")
    mock_output_manager._dict_to_file_json.assert_called_once_with(
        mock_output_manager.errors_pool, os.path.join("dummy_path", "dummy_name")
    )

    # Restore original methods
    mock_output_manager._generate_file_name = output_manager_original_method_states[
        "_generate_file_name"
    ]
    mock_output_manager._dict_to_file_json = output_manager_original_method_states[
        "_dict_to_file_json"
    ]


def test_dump_variable_names_and_contexts(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for function dump_variable_names_and_contexts in output_manager.py"""
    dummy_list = ['_exclude_info_maps=False, expect info_maps accordingly.\n']
    mock_output_manager._generate_file_name = MagicMock(return_value="dummy_name")
    mock_output_manager._list_to_file_txt = MagicMock()

    mock_output_manager.dump_variable_names_and_contexts("dummy_path", False)

    mock_output_manager._generate_file_name.assert_called_once_with("variable_names", "txt")
    mock_output_manager._list_to_file_txt.assert_called_once_with(
        dummy_list, os.path.join("dummy_path", "dummy_name")
    )

    # Restore original methods
    mock_output_manager._generate_file_name = output_manager_original_method_states[
        "_generate_file_name"
    ]
    mock_output_manager._list_to_file_txt = output_manager_original_method_states[
        "_list_to_file_txt"
    ]


def test_list_to_file_txt(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    tmpdir,
) -> None:
    """Test case for function _list_to_file_text in output_manager.py"""
    dummy_file_path = tmpdir.join('dummy_file.txt')
    dummy_list = ['apple', 'banana', 'cherry']

    mock_output_manager._list_to_file_txt(dummy_list, dummy_file_path)
    with open(dummy_file_path) as read_dummy_file:
        dummy_file_content = read_dummy_file.read()
    assert "applebananacherry" in dummy_file_content

    with pytest.raises(TypeError) as e:
        mock_output_manager._list_to_file_txt(1234, dummy_file_path)
        assert "object is not iterable" in str(e.value)

    dummy_broken_file_path = ''

    with pytest.raises(FileNotFoundError) as e:
        mock_output_manager._list_to_file_txt(dummy_list, dummy_broken_file_path)
        assert "No such file or directory" in str(e.value)

    # Restore original method
    mock_output_manager._list_to_file_txt = output_manager_original_method_states[
        "_list_to_file_txt"
    ]


def test_exclude_info_maps(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable]
) -> None:
    """Test case for function _exclude_info_maps in output_manager.py"""
    # Test case 1: Empty pool
    pool = {}
    expected_result = {}
    assert mock_output_manager._exclude_info_maps(pool) == expected_result

    # Test case 2: Pools with info_maps
    pool = {
        "key1": {
            "info_maps": "value1",
            "other_key": "other_value"
        },
        "key2": {
            "info_maps": "value1",
            "other_key": "other_value"
        }
    }
    expected_result = {
        "key1": {
            "other_key": "other_value"
        },
        "key2": {
            "other_key": "other_value"
        }
    }
    assert mock_output_manager._exclude_info_maps(pool) == expected_result

    # Restore original method
    mock_output_manager._exclude_info_maps = output_manager_original_method_states[
        "_exclude_info_maps"
    ]


def test_load_txt_file_to_list(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    tmpdir
) -> None:
    """Test case for function _load_txt_file_to_list in output_manager.py"""
    with patch('builtins.open', mock_open(read_data='apples\nbananas\ncherries')):
        result = mock_output_manager._load_txt_file_to_list('path/to/file.txt')

    assert result == ['apples', 'bananas', 'cherries']

    mock_open_func = Mock()
    mock_open_func.side_effect = Exception('Error opening file')

    with patch('builtins.open', mock_open_func):
        with pytest.raises(Exception):
            mock_output_manager._load_txt_file_to_list('path/to/file.txt')

    # Restore original method
    mock_output_manager._load_txt_file_to_list = output_manager_original_method_states[
        "_load_txt_file_to_list"
    ]


def test_load_input_txt_file_names_to_list(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    tmpdir
) -> None:
    """Test case for function _load_input_txt_file_names_to_list in output_manager.py"""
    tmpdir.join("file1.txt").write("File 1 content")
    tmpdir.join("file2.txt").write("File 2 content")
    tmpdir.join("file3.csv").write("File 3 content")

    txt_files = mock_output_manager._load_input_txt_file_names_to_list(tmpdir)

    assert len(txt_files) == 2
    assert "file1.txt" in txt_files
    assert "file2.txt" in txt_files
    assert "file3.csv" not in txt_files

    with pytest.raises(IsADirectoryError):
        mock_output_manager._load_input_txt_file_names_to_list("nonexistent_directory")

    # Restore original method
    mock_output_manager._load_input_txt_file_names_to_list = output_manager_original_method_states[
        "_load_input_txt_file_names_to_list"
    ]


def test_filter_variables_pool(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable]
) -> None:
    """Test case for function _filter_variables_pool in output_manager.py"""

    # Test case 1: Empty inclusion_keys
    inclusion_keys = []
    expected_result = {}
    assert mock_output_manager._filter_variables_pool(inclusion_keys) == expected_result

    # Test case 2: inclusion_keys with existing keys
    inclusion_keys = ["key1", "key2"]
    mock_output_manager.variables_pool = {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3"
    }
    expected_result = {
        "key1": "value1",
        "key2": "value2"
    }
    assert mock_output_manager._filter_variables_pool(inclusion_keys) == expected_result

    # Test case 3: inclusion_keys with non-existing keys
    inclusion_keys = ["key1", "key4"]
    expected_result = {
        "key1": "value1"
    }
    assert mock_output_manager._filter_variables_pool(inclusion_keys) == expected_result

    # Test case 4: inclusion_keys with duplicate keys
    inclusion_keys = ["key1", "key1"]
    expected_result = {
        "key1": "value1"
    }
    assert mock_output_manager._filter_variables_pool(inclusion_keys) == expected_result

    # Restore original method and variables_pool
    mock_output_manager._filter_variables_pool = output_manager_original_method_states[
        "_filter_variables_pool"
    ]
    mock_output_manager.variables_pool = {}


def test_save_variables(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable]
) -> None:
    """Test case for function save_variables in output_manager.py"""
    mock_output_manager._generate_file_name = MagicMock(return_value="dummy_name")
    mock_output_manager._dict_to_file_json = MagicMock()
    mock_output_manager._load_txt_file_to_list = MagicMock()
    mock_output_manager._exclude_info_maps = MagicMock()
    
    mock_output_manager._load_input_txt_file_names_to_list = MagicMock(return_value=["dummy_input_filepath"])

 # test case for when exclude_info_maps flag set to False
    mock_output_manager.save_variables("dummy_path", "dummy_dir_path", False)
    mock_output_manager._load_input_txt_file_names_to_list.assert_called_once_with("dummy_dir_path")
    mock_output_manager._generate_file_name.assert_called_once_with("saved_variables_dummy_input_filepath", "json")
    mock_output_manager._exclude_info_maps.assert_not_called()
    mock_output_manager._dict_to_file_json.assert_called_once_with(
        mock_output_manager.variables_pool, os.path.join("dummy_path", "dummy_name")
    )

    # test case for when exclude_info_maps flag set to True
    mock_output_manager._exclude_info_maps = MagicMock(return_value={})
    mock_output_manager.save_variables("dummy_path", "dummy_dir_path", True)
    mock_output_manager._exclude_info_maps.assert_called_once_with({})
    mock_output_manager._generate_file_name.assert_called_once_with("saved_variables_dummy_input_filepath", "json")
    mock_output_manager._load_txt_file_to_list.assert_called_with("dummy_dir_path")
    mock_output_manager._dict_to_file_json.assert_called_with(
        mock_output_manager.variables_pool, os.path.join("dummy_path", "dummy_name")
    )

    # Restore original method
    mock_output_manager.save_variables = output_manager_original_method_states[
        "save_variables"
    ]


class DummyClass:
    def __init__(self, value: int) -> None:
        self.value = value


class DummyNestedClass:
    def __init__(self, value: int) -> None:
        self.value = DummyClass(value)


@pytest.mark.parametrize(
    "input_obj, depth, max_depth, expected_output",
    [
        (42, 0, 1, 42),
        (3.14, 0, 1, 3.14),
        ("test", 0, 1, "test"),
        (True, 0, 1, True),
        (False, 0, 1, False),
        (None, 0, 1, None),
        ([], 0, 1, []),
        ((), 0, 1, ()),
        ({}, 0, 1, {}),
        (set(), 0, 1, []),
        ([1, "test", True], 0, 1, [1, "test", True]),
        ((1, "test", True), 0, 1, (1, "test", True)),
        ({1, 2, 3}, 0, 1, [1, 2, 3]),
        ({"a": 1, "b": 2}, 0, 1, {"a": 1, "b": 2}),
        ({"a": [1, 2, 3], "b": {"c": 4}}, 0, 3, {"a": [1, 2, 3], "b": {"c": 4}}),
        (["a", (1, 2), {"b": 3}], 0, 2, ["a", (1, 2), {"b": 3}]),
        ([1, [2, [3, 4], 5], 6], 0, 2, [1, [2, "[3, 4]", 5], 6]),
        ({"a": {"b": {"c": 42}}}, 0, 2, {"a": {"b": {"c": 42}}}),
        (DummyClass(42), 0, 1, {"value": 42}),
        (DummyNestedClass(42), 0, 2, {"value": {"value": 42}}),
        ({"a": {"b": DummyClass(42)}}, 0, 3, {"a": {"b": {"value": 42}}}),
        (
            [42, "test", 3.14, True, None, [1, 2, 3], {"a": 1}],
            0,
            2,
            [42, "test", 3.14, True, None, [1, 2, 3], {"a": 1}],
        ),
    ],
)
def test_make_serializable_recursive(
    input_obj: object,
    depth: int,
    max_depth: int,
    expected_output: object,
    mocker: MockerFixture,
) -> None:
    """Unit test for function _make_serializable() in file util.py"""
    # Arrange
    patch_for_get_str = mocker.patch.object(
        Utility, "_get_str", side_effect=lambda x: str(x)
    )

    # Act
    result = Utility._make_serializable(input_obj, depth, max_depth)

    # Assert
    assert result == expected_output
