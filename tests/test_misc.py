from copy import deepcopy
import os
from pathlib import Path
import re
import json
from typing import Any, Callable, Dict, List
from mock import mock_open, patch

import pytest
from mock.mock import MagicMock, call
from pytest import approx, raises
from pytest_mock.plugin import MockerFixture

from RUFAS.general_constants import GeneralConstants
from RUFAS.output_manager import LogVerbosity, OutputManager
from RUFAS.simulation_engine import SimulationEngine
from RUFAS.util import Utility


def test_annual_reset():
    """Unit test for function annual_reset in classes"""
    pass


def test_annual_mass_balance():
    """Unit test for function annual_mass_balance in classes"""
    pass


def test_calc_sim_length():
    """Unit test for function calc_sim_length in classes"""
    pass


def test_to_str():
    """Unit test for function to_str in classes"""
    pass


def test_advance():
    """Unit test for function advance in classes"""
    pass


def test_end_year():
    """Unit test for function end_year in classes"""
    pass


def test_end_simulation():
    """Unit test for function end_simulation in classes"""
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
    """Unit test for function is_leap_year in classes"""
    pass


@pytest.fixture
def patch_simulation_engine(mocker: MockerFixture) -> SimulationEngine:
    """Returns a mocked SimulationEngine"""
    mocker.patch("RUFAS.simulation_engine.SimulationEngine._initialize_simulation")

    sim_eng = SimulationEngine()
    sim_eng.config = MagicMock()
    sim_eng.weather = MagicMock()
    sim_eng.time = MagicMock()
    sim_eng.state = MagicMock()

    return sim_eng


def test_init_simulation_engine(
    patch_simulation_engine: SimulationEngine, mocker: MockerFixture
) -> None:
    """Unit test for function __init__ in file RUFAS/simulation_engine.py"""
    assert patch_simulation_engine.config is not None
    assert patch_simulation_engine.weather is not None
    assert patch_simulation_engine.time is not None
    assert patch_simulation_engine.state is not None
    patch_simulation_engine._initialize_simulation.assert_called_once()


def test_simulate(
    patch_simulation_engine: SimulationEngine, mocker: MockerFixture
) -> None:
    """Unit test for function simulate in file RUFAS/simulation_engine.py"""
    patch_for_run_simulation_main_loop = mocker.patch(
        "RUFAS.simulation_engine.SimulationEngine._run_simulation_main_loop"
    )
    sim_eng = patch_simulation_engine
    sim_eng.simulate()
    patch_for_run_simulation_main_loop.assert_called_once()


def test_run_simulation_main_loop(patch_simulation_engine: SimulationEngine) -> None:
    """Unit test for function simulate in file RUFAS/simulation_engine.py"""
    sim_eng = patch_simulation_engine
    sim_eng.time.end_simulation = MagicMock(side_effect=[False, True])
    sim_eng._annual_simulation = MagicMock()
    sim_eng._run_simulation_main_loop()
    sim_eng.time.end_simulation.assert_has_calls([call(), call()])
    sim_eng._annual_simulation.assert_called_once()


def test_daily_simulation(
    patch_simulation_engine: SimulationEngine, mocker: MockerFixture
) -> None:
    """Unit test for function _daily_simulation in file RUFAS/simulation_engine.py"""
    mocker.patch("RUFAS.routines.daily_animal_routine")
    mocker.patch("RUFAS.routines.daily_feed_routine")
    mocker.patch("RUFAS.simulation_engine.SimulationEngine._advance_time")
    patch_simulation_engine._daily_simulation()
    for mocked in mocker._patches_and_mocks:
        assert mocked[1].call_count == 1
    patch_simulation_engine.state.field_manager.daily_update_routine.assert_called_once()
    patch_simulation_engine.time.record_time.assert_called_once()
    patch_simulation_engine.weather.record_weather.assert_called_once()


def test_advance_time(
    patch_simulation_engine: SimulationEngine, mocker: MockerFixture
) -> None:
    """Unit test for function _advance_time in file RUFAS/simulation_engine.py"""
    mocker.patch("RUFAS.time.Time.to_str")
    mocker.patch("RUFAS.time.Time.advance")
    patch_simulation_engine.state.animal_manager.simulation_day = 1
    patch_simulation_engine._advance_time(False)
    patch_simulation_engine._advance_time(True)
    assert patch_simulation_engine.time.advance.call_count == 2
    assert patch_simulation_engine.time.to_str.call_count == 1
    assert patch_simulation_engine.state.animal_manager.simulation_day == 3


def test_input_prompt():
    """Unit test for function input_prompt in file user_prompt.py"""
    pass


def test_get_prefix() -> None:
    """Unit test for function _get_prefix in file output_manager.py"""
    om = OutputManager()
    assert om._get_prefix("class", "func") == "class.func"


@pytest.fixture
def mock_output_manager(mocker) -> OutputManager:
    output_manager = OutputManager()
    return output_manager


def test_set_metadata_prefix(mock_output_manager: OutputManager) -> None:
    """Unit test for the function set_metadata_prefix in the file output_manager.py"""
    mock_output_manager.set_metadata_prefix("dummy_prefix")
    assert mock_output_manager._OutputManager__metadata_prefix == "dummy_prefix"


@pytest.mark.parametrize(
    "log_verbose",
    [LogVerbosity.NONE, LogVerbosity.ERRORS, LogVerbosity.WARNINGS, LogVerbosity.LOGS],
)
def test_set_log_verbose(
    mock_output_manager: OutputManager, log_verbose: LogVerbosity
) -> None:
    """Unit test for the function set_log_verbose in the file output_manager.py"""
    mock_output_manager.set_log_verbose(log_verbose)
    assert mock_output_manager._OutputManager__log_verbose == log_verbose


def test_dict_to_csv_column_list(mock_output_manager: OutputManager) -> None:
    """Unit test for the function _dict_to_csv_column_list in the file output_manager.py"""
    data = {
        "values": [1.0, True, "test", {"key": 1}],
    }
    result = mock_output_manager._dict_to_csv_column_list("dummy_variable_name", data)
    v = result[0]
    assert v.to_list() == data["values"]

    data["info_maps"] = [{"map1": "value1", "map2": 1}, {"map1": "value2", "map2": 2}]
    result = mock_output_manager._dict_to_csv_column_list("dummy_variable_name", data)
    assert len(result) == 3
    data_series = result[0]
    map1_series = result[1]
    map2_series = result[2]
    assert data_series.name == "dummy_variable_name"
    assert data_series.to_list() == data["values"]
    assert map1_series.name == "dummy_variable_name.map1"
    assert map1_series.to_list() == ["value1", "value2"]
    assert map2_series.name == "dummy_variable_name.map2"
    assert map2_series.to_list() == [1, 2]


def test_dict_to_csv_column_list_empty_list(mock_output_manager: OutputManager) -> None:
    """Unit test for the function _dict_to_csv_column_list in the file output_manager.py"""
    data = {"values": [], "info_maps": []}
    result = mock_output_manager._dict_to_csv_column_list("dummy_variable_name", data)

    assert len(result) == 2
    series = result[0]
    assert series.name == "dummy_variable_name"
    assert series.to_list() == []
    series = result[1]
    assert series.name == "dummy_variable_name"
    assert series.to_list() == []


@pytest.mark.parametrize(
    "data, expected_result, should_write",
    [
        (
            {"var1": {"values": [1.0, True, "test"], "info_maps": []}},
            f"var1,var1{os.linesep}1.0,{os.linesep}True,{os.linesep}test,{os.linesep}",
            True,
        ),
        (
            {"var1": {"values": [1.0, True, "test"]}},
            f"var1{os.linesep}1.0{os.linesep}True{os.linesep}test{os.linesep}",
            True,
        ),
        (
            {
                "var1": {
                    "values": [1, 2, 3],
                    "info_maps": [{"v": 1}, {"v": 2}, {"v": 3}],
                }
            },
            f"var1,var1.v{os.linesep}1,1{os.linesep}2,2{os.linesep}3,3{os.linesep}",
            True,
        ),
        (
            {"var1": {"values": [1, 2, 3]}},
            f"var1{os.linesep}1{os.linesep}2{os.linesep}3{os.linesep}",
            True,
        ),
        (
            {
                "var1": {
                    "values": [1],
                    "info_maps": [{"map1": "value1"}, {"map1": "value2"}],
                }
            },
            f"var1,var1.map1{os.linesep}1,value1{os.linesep},value2{os.linesep}",
            True,
        ),
        (
            {
                "var1": {
                    "values": [{"v1": 1, "v2": 1}, {"v1": 2, "v2": 2}],
                    "info_maps": [{"map1": "value1"}, {"map1": "value2"}],
                }
            },
            f"var1.v1,var1.v2,var1.map1{os.linesep}1,1,value1{os.linesep}2,2,value2{os.linesep}",
            True,
        ),
        (
            {
                "simple_key": {
                    "values": [
                        {"key1": 1, "key2": [1, 1]},
                        {"key1": 2, "key2": [2, 2]},
                        {"key1": 3, "key2": [3, 3]},
                    ],
                    "info_maps": [
                        {
                            "subkey1": 1,
                            "subkey2": "Hello",
                            "subkey3": [1, 2, 3],
                            "subkey4": {"nestedkey1": "World", "nestedkey2": [4, 5, 6]},
                        },
                        {
                            "subkey1": 2,
                            "subkey2": "Hi",
                            "subkey3": [4, 5, 6],
                            "subkey4": {"nestedkey1": "There", "nestedkey2": [7, 8, 9]},
                        },
                    ],
                }
            },
            f"simple_key.key1,simple_key.key2,simple_key.subkey1,simple_key.subkey2,"
            f"simple_key.subkey3,simple_key.subkey4{os.linesep}"
            f"1,\"[1, 1]\",1,Hello,\"[1, 2, 3]\",\"{{'nestedkey1': 'World', 'nestedkey2': [4, 5, 6]}}\"{os.linesep}"
            f"2,\"[2, 2]\",2,Hi,\"[4, 5, 6]\",\"{{'nestedkey1': 'There', 'nestedkey2': [7, 8, 9]}}\"{os.linesep}"
            f'3,"[3, 3]",,,,{os.linesep}',
            True,
        ),
        (
            {
                "simple_key1": {"values": [1, 2, 3]},
                "simple_key2": {"values": [4, 5, 6]},
            },
            f"simple_key1,simple_key2{os.linesep}"
            f"1,4{os.linesep}2,5{os.linesep}3,6{os.linesep}",
            True,
        ),
        (
            {
                "simple_key1": {
                    "values": [1, 2, 3],
                    "info_maps": [{"subkey1": "Farm", "subkey2": "Field"}],
                },
                "simple_key2": {
                    "values": [4, 5, 6, 8, 9],
                    "info_maps": [
                        {
                            "subkey1": "Tractor",
                        }
                    ],
                },
            },
            f"simple_key1,simple_key1.subkey1,simple_key1.subkey2,simple_key2,"
            f"simple_key2.subkey1{os.linesep}"
            f"1,Farm,Field,4,Tractor{os.linesep}"
            f"2,,,5,{os.linesep}"
            f"3,,,6,{os.linesep}"
            f",,,8,{os.linesep}"
            f",,,9,{os.linesep}",
            True,
        ),
        ({}, "", False),
    ],
)
def test_dict_to_file_csv(
    mock_output_manager: OutputManager,
    data: Dict[str, Any],
    expected_result: str,
    should_write: bool,
) -> None:
    """Unit test for the function _dict_to_file_csv in the file output_manager.py"""
    open_mock = mock_open()

    with patch("builtins.open", open_mock):
        mock_output_manager._dict_to_file_csv(data, "test")

    if should_write:
        open_mock.assert_called_with(
            "test", "w", encoding="utf-8", errors="strict", newline=""
        )
    written_data = "".join(call[1][0] for call in open_mock().write.mock_calls)
    assert written_data == expected_result


def test_dict_to_file_json(mock_output_manager: OutputManager) -> None:
    """Unit test for the function _dict_to_file_json in the file output_manager.py"""

    data = {
        "var1": {"values": [1], "info_maps": [{"map1": "value1"}, {"map1": "value2"}]},
        "var2": {
            "values": [{"v1": 1, "v2": 1}, {"v1": 2, "v2": 2}],
            "info_maps": [{"map1": "value1"}, {"map1": "value2"}],
        },
    }

    open_mock = mock_open()
    with patch("builtins.open", open_mock):
        mock_output_manager._dict_to_file_json(data, "test")

    written_data = "".join(call[1][0] for call in open_mock().write.mock_calls)
    assert written_data == json.dumps(data, indent=0)


def test_dict_to_file_json_exception(mock_output_manager: OutputManager) -> None:
    """Test file opening failure for _dict_to_file_json() in the file output_manager.py"""
    open_mock = mock_open()
    open_mock.side_effect = IOError
    data = {"var1": {"values": [1, 2, 3], "info_maps": [1, 2, 3]}}

    with patch("builtins.open", open_mock):
        with raises(Exception):
            mock_output_manager._dict_to_file_json(data, "test")


def test_dict_to_file_csv_exception(mock_output_manager: OutputManager) -> None:
    """Unit test for the function _dict_to_file_csv in the file output_manager.py"""
    open_mock = mock_open()
    open_mock.side_effect = IOError
    data = {"var1": {"values": [1, 2, 3], "info_maps": [1, 2, 3]}}

    with patch("builtins.open", open_mock):
        with raises(Exception):
            mock_output_manager._dict_to_file_csv(data, "test")


@pytest.mark.parametrize(
    "exception, error_message",
    [
        (
            OSError,
            "test OS Error",
        ),
        (
            FileNotFoundError,
            "test File not Found Error",
        ),
    ],
)
def test_save_variables_to_csv_files_exceptions(
    mock_output_manager: OutputManager, exception: Exception, error_message: str
) -> None:
    """Unit test for the function _save_variables_to_csv_files() in the file output_manager.py"""

    with patch("pathlib.Path.mkdir") as mock_mkdir:
        mock_mkdir.side_effect = exception(error_message)
        with pytest.raises(exception, match=error_message):
            mock_output_manager._save_variables_to_csv_files({}, "filter", "path")


def test_generate_key(mocker: MockerFixture) -> None:
    """Unit test for function _generate_key in file output_manager.py"""
    om = OutputManager()
    with raises(KeyError):
        om._generate_key("name", {})

    with raises(KeyError):
        om._generate_key("name", {"class": "test"})

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


def test_get_timestamp(mocker: MockerFixture) -> None:
    """Unit test for the function _get_timestamp in file output_manager.py"""
    om = OutputManager()
    # match 28-Jun-2023_Wed_15-48-21.406585
    timestamp_with_millis_pattern = (
        r"\d{2}-[A-Za-z]{3}-\d{4}_[A-Za-z]{3}_\d{2}-\d{2}-\d{2}\.\d{6}"
    )
    # match 28-Jun-2023_Wed_15-48-21
    timestamp_without_millis_pattern = (
        r"\d{2}-[A-Za-z]{3}-\d{4}_[A-Za-z]{3}_\d{2}-\d{2}-\d{2}"
    )

    assert re.match(
        timestamp_with_millis_pattern, om._get_timestamp(include_millis=True)
    )
    assert re.match(
        timestamp_without_millis_pattern, om._get_timestamp(include_millis=False)
    )


@pytest.mark.parametrize(
    "log_verobse",
    [LogVerbosity.NONE, LogVerbosity.ERRORS, LogVerbosity.WARNINGS, LogVerbosity.LOGS],
)
def test_add_error(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    log_verobse: LogVerbosity,
) -> None:
    """Unit test for function add_error in file output_manager.py"""
    key = "dummy_key"
    name = "dummy_name"
    message = "dummy_value"
    timestamp = "18-Jan-2023_Wed_22-38-14.123456"
    info_map = {}
    metadata_prefix = "dummy_prefix"
    mock_output_manager._generate_key = MagicMock(return_value=key)
    mock_output_manager._add_to_pool = MagicMock()
    mock_output_manager._get_timestamp = MagicMock(return_value=timestamp)
    mock_output_manager.set_log_verbose(log_verobse)
    mock_output_manager.set_metadata_prefix(metadata_prefix)
    mock_output_manager._handle_log_output = MagicMock()

    mock_output_manager.add_error(name, message, info_map)

    mock_output_manager._generate_key.assert_called_once_with(name, info_map)

    assert info_map.get("timestamp") == timestamp
    mock_output_manager._handle_log_output.assert_called_once_with(
        name, message, info_map, LogVerbosity.ERRORS
    )
    mock_output_manager._add_to_pool(
        mock_output_manager.errors_pool, key, message, info_map
    )

    mock_output_manager._generate_key = output_manager_original_method_states[
        "_generate_key"
    ]
    mock_output_manager._add_to_pool = output_manager_original_method_states[
        "_add_to_pool"
    ]
    mock_output_manager._get_timestamp = output_manager_original_method_states[
        "_get_timestamp"
    ]
    mock_output_manager._handle_log_output = output_manager_original_method_states[
        "_handle_log_output"
    ]


@pytest.mark.parametrize(
    "log_verobse",
    [LogVerbosity.NONE, LogVerbosity.ERRORS, LogVerbosity.WARNINGS, LogVerbosity.LOGS],
)
def test_add_warning(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    log_verobse: LogVerbosity,
) -> None:
    """Unit test for function add_warning in file output_manager.py"""
    key = "dummy_key"
    name = "dummy_name"
    message = "dummy_value"
    timestamp = "18-Jan-2023_Wed_22-38-14.123456"
    info_map = {}
    metadata_prefix = "dummy_prefix"
    mock_output_manager._generate_key = MagicMock(return_value=key)
    mock_output_manager._add_to_pool = MagicMock()
    mock_output_manager._get_timestamp = MagicMock(return_value=timestamp)
    mock_output_manager.set_log_verbose(log_verobse)
    mock_output_manager.set_metadata_prefix(metadata_prefix)
    mock_output_manager._handle_log_output = MagicMock()

    mock_output_manager.add_warning(name, message, info_map)

    mock_output_manager._generate_key.assert_called_once_with(name, info_map)

    assert info_map.get("timestamp") == timestamp
    mock_output_manager._handle_log_output.assert_called_once_with(
        name, message, info_map, LogVerbosity.WARNINGS
    )

    mock_output_manager._add_to_pool(
        mock_output_manager.warnings_pool, key, message, info_map
    )

    mock_output_manager._generate_key = output_manager_original_method_states[
        "_generate_key"
    ]
    mock_output_manager._add_to_pool = output_manager_original_method_states[
        "_add_to_pool"
    ]
    mock_output_manager._get_timestamp = output_manager_original_method_states[
        "_get_timestamp"
    ]
    mock_output_manager._handle_log_output = output_manager_original_method_states[
        "_handle_log_output"
    ]


@pytest.mark.parametrize(
    "log_verobse",
    [LogVerbosity.NONE, LogVerbosity.ERRORS, LogVerbosity.WARNINGS, LogVerbosity.LOGS],
)
def test_add_log(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    log_verobse: LogVerbosity,
) -> None:
    """Unit test for function add_log in file output_manager.py"""
    key = "dummy_key"
    name = "dummy_name"
    message = "dummy_value"
    timestamp = "18-Jan-2023_Wed_22-38-14.123456"
    info_map = {}
    metadata_prefix = "dummy_prefix"
    mock_output_manager._generate_key = MagicMock(return_value=key)
    mock_output_manager._add_to_pool = MagicMock()
    mock_output_manager._get_timestamp = MagicMock(return_value=timestamp)
    mock_output_manager.set_log_verbose(log_verobse)
    mock_output_manager.set_metadata_prefix(metadata_prefix)
    mock_output_manager._handle_log_output = MagicMock()

    mock_output_manager.add_log(name, message, info_map)

    mock_output_manager._generate_key.assert_called_once_with(name, info_map)

    assert info_map.get("timestamp") == timestamp

    mock_output_manager._handle_log_output.assert_called_once_with(
        name, message, info_map, LogVerbosity.LOGS
    )

    mock_output_manager._add_to_pool(
        mock_output_manager.logs_pool, key, message, info_map
    )

    mock_output_manager._generate_key = output_manager_original_method_states[
        "_generate_key"
    ]
    mock_output_manager._add_to_pool = output_manager_original_method_states[
        "_add_to_pool"
    ]
    mock_output_manager._get_timestamp = output_manager_original_method_states[
        "_get_timestamp"
    ]
    mock_output_manager._handle_log_output = output_manager_original_method_states[
        "_handle_log_output"
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


@pytest.mark.parametrize(
    "dummy_value",
    ["dummy_value", 2, 3.45, True],
)
def test_add_to_pool(mock_output_manager: OutputManager, dummy_value: Any) -> None:
    """Unit test for function _add_to_pool in file output_manager.py"""
    info_map = {
        "class": "dummy_class",
        "function": "dummy_func",
        "context": "dummy_context",
    }
    key = "dummy_key"
    pool = {}
    mock_output_manager._add_to_pool(pool, key, dummy_value, info_map)
    assert pool[key] == {
        "info_maps": [{"context": "dummy_context"}],
        "values": [dummy_value],
    }
    assert pool[key]["values"][0] == dummy_value
    assert pool[key]["values"][0] is dummy_value

    info_map["more_context"] = 1234567890
    mock_output_manager._add_to_pool(pool, key, {dummy_value}, info_map)
    assert pool[key] == {
        "info_maps": [
            {"context": "dummy_context"},
            {"context": "dummy_context", "more_context": 1234567890},
        ],
        "values": [dummy_value, {dummy_value}],
    }
    assert pool[key]["values"][1] == deepcopy({dummy_value})
    assert pool[key]["values"][1] is not {dummy_value}


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


@pytest.mark.parametrize(
    "log_level, color_code",
    [
        (LogVerbosity.NONE, "\033[0m"),
        (LogVerbosity.ERRORS, "\33[91m"),
        (LogVerbosity.WARNINGS, "\33[93m"),
        (LogVerbosity.LOGS, "\33[92m"),
    ],
)
def test_handle_log_output(capsys, log_level: LogVerbosity, color_code: str) -> None:
    name = "dummy name"
    msg = "dummy message"
    info_map = {"timestamp": "dummy_timestamp"}
    om = OutputManager()
    om.set_metadata_prefix("dummy_prefix")
    om._handle_log_output(name, msg, info_map, log_level)
    log_format = "{color}[{timestamp}][{log_level}][{metadata_prefix}] {name}: {message}{color_reset}\n"
    expected_message = log_format.format(
        timestamp=info_map["timestamp"],
        color=color_code,
        color_reset="\033[0m",
        metadata_prefix="dummy_prefix",
        name=name,
        message=msg,
        log_level=log_level,
    )
    captured = capsys.readouterr()
    assert expected_message in captured.out


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
        "_add_to_pool": mock_output_manager._add_to_pool,
        "_dict_to_file_csv": mock_output_manager._dict_to_file_csv,
        "_dict_to_file_json": mock_output_manager._dict_to_file_json,
        "_exclude_info_maps": mock_output_manager._exclude_info_maps,
        "_filter_variables_pool": mock_output_manager._filter_variables_pool,
        "_generate_file_name": mock_output_manager._generate_file_name,
        "_generate_key": mock_output_manager._generate_key,
        "_get_timestamp": mock_output_manager._get_timestamp,
        "_handle_log_output": mock_output_manager._handle_log_output,
        "set_metadata_prefix": mock_output_manager.set_metadata_prefix,
        "set_log_verbose": mock_output_manager.set_log_verbose,
        "_list_to_file_txt": mock_output_manager._list_to_file_txt,
        "_list_filter_files_in_dir": mock_output_manager._list_filter_files_in_dir,
        "_load_filter_file_content": mock_output_manager._load_filter_file_content,
        "load_variables_pool_from_file": mock_output_manager.load_variables_pool_from_file,
        "_save_variables_to_csv_files ": mock_output_manager._save_variables_to_csv_files,
        "save_results": mock_output_manager.save_results,
        "_save_variables_to_csv_files": mock_output_manager._save_variables_to_csv_files,
        "add_variable": mock_output_manager.add_variable,
        "add_error": mock_output_manager.add_error,
        "add_log": mock_output_manager.add_log,
        "add_warning": mock_output_manager.add_warning,
        "dump_variables": mock_output_manager.dump_variables,
        "dump_logs": mock_output_manager.dump_logs,
        "dump_warnings": mock_output_manager.dump_warnings,
        "dump_errors": mock_output_manager.dump_errors,
        "dump_variable_names_and_contexts": mock_output_manager.dump_variable_names_and_contexts,
        "_route_save_functions": mock_output_manager._route_save_functions,
    }


def test_dump_all_nondata_pools(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for function dump_all_nondata_pools in output_manager.py"""
    path = "dummy_path"
    mock_output_manager.dump_errors = MagicMock()
    mock_output_manager.dump_warnings = MagicMock()
    mock_output_manager.dump_logs = MagicMock()
    mock_output_manager.dump_variable_names_and_contexts = MagicMock()

    mock_output_manager.dump_all_nondata_pools(path, False, "verbose")

    mock_output_manager.dump_errors.assert_called_once_with(path)
    mock_output_manager.dump_warnings.assert_called_once_with(path)
    mock_output_manager.dump_logs.assert_called_once_with(path)
    mock_output_manager.dump_variable_names_and_contexts.assert_called_once_with(
        path, False, "verbose"
    )

    mock_output_manager.dump_all_nondata_pools(path, True)
    mock_output_manager.dump_variable_names_and_contexts.assert_called_with(
        path, True, "verbose"
    )
    assert mock_output_manager.dump_logs.call_count == 2
    assert mock_output_manager.dump_warnings.call_count == 2
    assert mock_output_manager.dump_errors.call_count == 2

    # Restore original methods
    mock_output_manager.dump_logs = output_manager_original_method_states["dump_logs"]
    mock_output_manager.dump_warnings = output_manager_original_method_states[
        "dump_warnings"
    ]
    mock_output_manager.dump_errors = output_manager_original_method_states[
        "dump_errors"
    ]
    mock_output_manager.dump_variable_names_and_contexts = (
        output_manager_original_method_states["dump_variable_names_and_contexts"]
    )


def test_generate_file_name(mocker: MockerFixture) -> None:
    """Unit test for function _generate_file_name in file output_manager.py"""
    timestamp = "18-Jan-2023_Wed_22-38-14"
    base_name = "dummy_name"
    extension = "ext"
    metadata_prefix = "dummy_prefix"
    om = OutputManager()
    om._OutputManager__metadata_prefix = metadata_prefix

    with patch.object(om, "_get_timestamp") as mock_method:
        mock_method.return_value = timestamp
        assert (
            om._generate_file_name(base_name, extension)
            == f"{metadata_prefix}_{base_name}_{timestamp}.{extension}"
        )


def test_dump_variables(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for function dump_variables in output_manager.py"""
    filtered_info_maps_dict = {}
    mock_output_manager._generate_file_name = MagicMock(return_value="dummy_name")
    mock_output_manager._dict_to_file_json = MagicMock()
    mock_output_manager._exclude_info_maps = MagicMock(
        return_value=filtered_info_maps_dict
    )

    mock_output_manager.dump_variables("dummy_path", False)

    mock_output_manager._exclude_info_maps.assert_not_called()
    mock_output_manager._generate_file_name.assert_called_once_with(
        "all_variables", "json"
    )
    mock_output_manager._dict_to_file_json.assert_called_once_with(
        mock_output_manager.variables_pool, os.path.join("dummy_path", "dummy_name")
    )

    mock_output_manager._generate_file_name = MagicMock(return_value="dummy_name")
    mock_output_manager._dict_to_file_json = MagicMock()
    mock_output_manager._exclude_info_maps = MagicMock(
        return_value=filtered_info_maps_dict
    )

    mock_output_manager.dump_variables("dummy_path", True)

    mock_output_manager._exclude_info_maps.assert_called_once()
    mock_output_manager._generate_file_name.assert_called_once_with(
        "all_variables", "json"
    )
    mock_output_manager._dict_to_file_json.assert_called_once_with(
        filtered_info_maps_dict, os.path.join("dummy_path", "dummy_name")
    )

    # Restore original methods
    mock_output_manager._generate_file_name = output_manager_original_method_states[
        "_generate_file_name"
    ]
    mock_output_manager._dict_to_file_json = output_manager_original_method_states[
        "_dict_to_file_json"
    ]
    mock_output_manager._exclude_info_maps = output_manager_original_method_states[
        "_exclude_info_maps"
    ]


def test_save_variables_to_csv_files(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for function _save_variables_to_csv_files in output_manager.py"""
    mock_output_manager._generate_file_name = MagicMock(return_value="dummy_name")
    mock_output_manager._dict_to_file_csv = MagicMock()

    mock_variable_pool = {"var1": {"values": [1], "info_maps": []}}

    with patch("pathlib.Path.mkdir") as mock_mkdir:
        mock_mkdir.return_value = None
        mock_output_manager._save_variables_to_csv_files(
            mock_variable_pool, "csv_dummy_filter_filepath.txt", "dummy_path"
        )

    mock_mkdir.assert_called_with(parents=True, exist_ok=True)
    dummy_file_name = "saved_variables_csv_dummy_filter_filepath.txt"
    mock_output_manager._generate_file_name.assert_called_once_with(
        dummy_file_name, "csv"
    )
    mock_output_manager._dict_to_file_csv.assert_called_once_with(
        mock_variable_pool, os.path.join("dummy_path", "dummy_name")
    )

    # Restore original methods
    mock_output_manager._generate_file_name = output_manager_original_method_states[
        "_generate_file_name"
    ]
    mock_output_manager._dict_to_file_csv = output_manager_original_method_states[
        "_dict_to_file_csv"
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


@pytest.mark.parametrize(
    "expected_result, exclude_info_maps, format_option",
    [
        (
            [
                "_exclude_info_maps=False, expect info_maps accordingly." + os.linesep,
                "var1" + os.linesep,
                "var1.info_maps: test" + os.linesep,
                "var2.info_maps: map1" + os.linesep,
                "var2.values: v1" + os.linesep,
                "var2.values: v2" + os.linesep,
            ],
            False,
            "verbose",
        ),
        (
            [
                "_exclude_info_maps=True, expect info_maps accordingly." + os.linesep,
                "var1" + os.linesep,
                "var2.values: v1" + os.linesep,
                "var2.values: v2" + os.linesep,
            ],
            True,
            "verbose",
        ),
        (
            [
                "_exclude_info_maps=False, expect info_maps accordingly." + os.linesep,
                "var1" + os.linesep,
                "    .info_maps: test" + os.linesep,
                "var2" + os.linesep,
                "    .info_maps: map1" + os.linesep,
                "    .values: v1" + os.linesep,
                "    .values: v2" + os.linesep,
            ],
            False,
            "block",
        ),
        (
            [
                "_exclude_info_maps=True, expect info_maps accordingly." + os.linesep,
                "var1" + os.linesep,
                "var2" + os.linesep,
                "    .values: v1" + os.linesep,
                "    .values: v2" + os.linesep,
            ],
            True,
            "block",
        ),
        (
            [
                "_exclude_info_maps=False, expect info_maps accordingly." + os.linesep,
                "var1" + os.linesep,
                "var1.info_maps: ['test']" + os.linesep,
                "var2.info_maps: ['map1']" + os.linesep,
                "var2.values: ['v1', 'v2']" + os.linesep,
            ],
            False,
            "inline",
        ),
        (
            [
                "_exclude_info_maps=True, expect info_maps accordingly." + os.linesep,
                "var1" + os.linesep,
                "var2.values: ['v1', 'v2']" + os.linesep,
            ],
            True,
            "inline",
        ),
        (
            [
                "_exclude_info_maps=True, expect info_maps accordingly." + os.linesep,
                "var1" + os.linesep,
                "var2.v1" + os.linesep,
                "var2.v2" + os.linesep,
            ],
            True,
            "basic",
        ),
        (
            [
                "_exclude_info_maps=False, expect info_maps accordingly." + os.linesep,
                "var1" + os.linesep,
                "var1.test" + os.linesep,
                "var2.map1" + os.linesep,
                "var2.v1" + os.linesep,
                "var2.v2" + os.linesep,
            ],
            False,
            "basic",
        ),
    ],
)
def test_dump_variable_names_and_contexts(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    expected_result: List[str],
    exclude_info_maps: bool,
    format_option: str,
) -> None:
    """Test case for function dump_variable_names_and_contexts in output_manager.py"""
    mock_variable_pool: Dict[str, Dict[str, List[Any]]] = {
        "var1": {"values": [1], "info_maps": [{"test": "value1"}, {"test": "value2"}]},
        "var2": {
            "values": [{"v1": 1, "v2": 1}, {"v1": 2, "v2": 2}],
            "info_maps": [{"map1": "value1"}, {"map1": "value2"}],
        },
    }
    original_variables_pool = mock_output_manager.variables_pool
    mock_output_manager.variables_pool = mock_variable_pool
    mock_output_manager._generate_file_name = MagicMock(return_value="dummy_name")
    mock_output_manager._list_to_file_txt = MagicMock()

    mock_output_manager.dump_variable_names_and_contexts(
        "dummy_path", exclude_info_maps, format_option
    )

    mock_output_manager._generate_file_name.assert_called_once_with(
        "variable_names", "txt"
    )
    mock_output_manager._list_to_file_txt.assert_called_once_with(
        expected_result, os.path.join("dummy_path", "dummy_name")
    )

    # Restore original methods
    mock_output_manager._generate_file_name = output_manager_original_method_states[
        "_generate_file_name"
    ]
    mock_output_manager._list_to_file_txt = output_manager_original_method_states[
        "_list_to_file_txt"
    ]
    mock_output_manager.variables_pool = original_variables_pool


def test_dump_variable_names_and_contexts_no_values(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for function dump_variable_names_and_contexts in output_manager.py"""
    mock_variable_pool: Dict[str, Dict[str, List[Any]]] = {
        "var1": {
            "no_values": [1],
            "info_maps": [{"test": "value1"}, {"test": "value2"}],
        },
    }
    expected_output = [
        "_exclude_info_maps=False, expect info_maps accordingly." + os.linesep,
        "var1: **NO VARIABLES**" + os.linesep,
    ]
    original_variables_pool = mock_output_manager.variables_pool
    mock_output_manager.variables_pool = mock_variable_pool
    mock_output_manager._generate_file_name = MagicMock(return_value="dummy_name")
    mock_output_manager._list_to_file_txt = MagicMock()

    mock_output_manager.dump_variable_names_and_contexts(
        "dummy_path", False, format_option="verbose"
    )

    mock_output_manager._generate_file_name.assert_called_once_with(
        "variable_names", "txt"
    )
    mock_output_manager._list_to_file_txt.assert_called_once_with(
        expected_output, os.path.join("dummy_path", "dummy_name")
    )

    # Restore original methods
    mock_output_manager._generate_file_name = output_manager_original_method_states[
        "_generate_file_name"
    ]
    mock_output_manager._list_to_file_txt = output_manager_original_method_states[
        "_list_to_file_txt"
    ]
    mock_output_manager.variables_pool = original_variables_pool


def test_list_to_file_txt(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    tmpdir,
) -> None:
    """Test case for function _list_to_file_text in output_manager.py"""
    dummy_file_path = tmpdir.join("dummy_file.txt")
    dummy_list = ["apple", "banana", "cherry"]

    mock_output_manager._list_to_file_txt(dummy_list, dummy_file_path)
    with open(dummy_file_path) as read_dummy_file:
        dummy_file_content = read_dummy_file.read()
    assert "applebananacherry" in dummy_file_content

    with pytest.raises(TypeError) as e:
        mock_output_manager._list_to_file_txt(1234, dummy_file_path)
    assert "object is not iterable" in str(e.value)

    dummy_broken_file_path = ""

    with pytest.raises(FileNotFoundError) as e:
        mock_output_manager._list_to_file_txt(dummy_list, dummy_broken_file_path)
    assert "No such file or directory" in str(e.value)

    # Restore original method
    mock_output_manager._list_to_file_txt = output_manager_original_method_states[
        "_list_to_file_txt"
    ]


def test_exclude_info_maps(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for function _exclude_info_maps in output_manager.py"""
    # Test case 1: Empty pool
    pool = {}
    expected_result = {}
    assert mock_output_manager._exclude_info_maps(pool) == expected_result

    # Test case 2: Pools with info_maps
    pool = {
        "key1": {"info_maps": "value1", "other_key": "other_value"},
        "key2": {"info_maps": "value1", "other_key": "other_value"},
    }
    expected_result = {
        "key1": {"other_key": "other_value"},
        "key2": {"other_key": "other_value"},
    }
    assert mock_output_manager._exclude_info_maps(pool) == expected_result

    # Restore original method
    mock_output_manager._exclude_info_maps = output_manager_original_method_states[
        "_exclude_info_maps"
    ]


@pytest.mark.parametrize(
    "mock_file_text",
    ["apples\nbananas\ncherries",
     "apples\nbananas\ncherries\n\n\n",
     "apples\nbananas\n\n\n\ncherries",
     "apples\nbananas\n\n\ncherries\n\n\n"])
@patch("builtins.open", new_callable=mock_open)
def test_load_filter_file_content_txt(
    mock_file: MagicMock,
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    mock_file_text: str,
) -> None:
    """Test case for function _load_filter_file_content in output_manager.py"""
    mock_file.return_value.read.return_value = mock_file_text
    result = mock_output_manager._load_filter_file_content("path/to/file.txt")
    assert result == [{"filters": ["apples", "bananas", "cherries"]}]

    # Restore original method
    mock_output_manager._load_filter_file_content = (
        output_manager_original_method_states["_load_filter_file_content"]
    )


@patch("builtins.open", new_callable=mock_open)
def test_load_filter_file_content_json(
    mock_file: MagicMock,
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for function _load_filter_file_content in output_manager.py"""

    data: List[Dict[str, Any]] = {
        "filters": ["filter1", "filter2"],
        "other_key": "value",
    }
    mock_file.return_value.read.return_value = json.dumps(data)
    result = mock_output_manager._load_filter_file_content("some_file.json")
    assert result == [data]

    # Restore original method
    mock_output_manager._load_filter_file_content = (
        output_manager_original_method_states["_load_filter_file_content"]
    )


@patch("builtins.open", new_callable=mock_open)
def test_load_filter_file_content_json_multiple(
    mock_file: MagicMock,
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for function _load_filter_file_content in output_manager.py"""

    data: List[Dict[str, Any]] = {
        "multiple": [
            {
                "filters": ["filter1", "filter2"],
                "other_key": "value1",
            },
            {
                "filters": ["filter3", "filter4"],
                "other_key": "value2",
            },
        ]
    }
    mock_file.return_value.read.return_value = json.dumps(data)
    result = mock_output_manager._load_filter_file_content("some_file.json")
    assert result == data["multiple"]

    # Restore original method
    mock_output_manager._load_filter_file_content = (
        output_manager_original_method_states["_load_filter_file_content"]
    )


@patch("builtins.open", new_callable=mock_open)
def test_load_filter_file_content_exception(
    mock_file: MagicMock,
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for function _load_filter_file_content in output_manager.py"""
    with pytest.raises(Exception):
        mock_output_manager._load_filter_file_content("invalid_extention.abc")

    mock_file.return_value.read.return_value = "this is not valid JSON"
    with pytest.raises(json.JSONDecodeError):
        mock_output_manager._load_filter_file_content("some_file.json")

    mock_file.side_effect = FileNotFoundError
    with pytest.raises(FileNotFoundError):
        mock_output_manager._load_filter_file_content("non_existent_file.txt")

    mock_file.side_effect = UnicodeDecodeError(
        "encoding", b"", 1, 2, "Fake decode error"
    )
    with pytest.raises(UnicodeDecodeError):
        mock_output_manager._load_filter_file_content("corrupted_file.txt")

    mock_file.side_effect = Exception("Unexpected error")
    with pytest.raises(Exception):
        mock_output_manager._load_filter_file_content("some_file.txt")

    # Restore original method
    mock_output_manager._load_filter_file_content = (
        output_manager_original_method_states["_load_filter_file_content"]
    )


def test_list_filter_files_in_dir(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    tmpdir,
) -> None:
    mock_output_manager.add_warning = MagicMock()
    tmpdir.join("json_file1.txt").write("File 1 content")
    tmpdir.join("csv_file2.json").write("File 2 content")
    tmpdir.join("file3.txt").write("File 3 content")

    filter_files = mock_output_manager._list_filter_files_in_dir(tmpdir)

    assert len(filter_files) == 2
    assert "json_file1.txt" in filter_files
    assert "csv_file2.json" in filter_files
    assert "file3.csv" not in filter_files
    mock_output_manager.add_warning.assert_called_once()

    with pytest.raises(NotADirectoryError):
        mock_output_manager._list_filter_files_in_dir("nonexistent_directory")

    # Restore original method
    mock_output_manager._list_filter_files_in_dir = (
        output_manager_original_method_states["_list_filter_files_in_dir"]
    )
    mock_output_manager.add_warning = output_manager_original_method_states[
        "add_warning"
    ]


def test_filter_variables_pool_include_empty_filter_pattern_pool(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for empty filter pattern pool with function _filter_variables_pool in output_manager.py"""
    mock_output_manager.variables_pool = {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3",
    }
    dummy_input_file = ""
    filter_patterns = []
    expected_result = {}

    assert (
        mock_output_manager._filter_variables_pool(filter_patterns, dummy_input_file)
        == expected_result
    )

    # Restore original method
    mock_output_manager._filter_variables_pool = output_manager_original_method_states[
        "_filter_variables_pool"
    ]
    mock_output_manager.variables_pool = {}


def test_filter_variables_pool_exclude_empty_filter_pattern_pool(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for exclude keyword in empty filter pattern pool with
    function _filter_variables_pool in output_manager.py"""
    mock_output_manager.variables_pool = {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3",
    }
    dummy_input_file = ""
    filter_patterns = ["exclude"]
    expected_result = {"key1": "value1", "key2": "value2", "key3": "value3"}

    assert (
        mock_output_manager._filter_variables_pool(filter_patterns, dummy_input_file)
        == expected_result
    )

    # Restore original method
    mock_output_manager._filter_variables_pool = output_manager_original_method_states[
        "_filter_variables_pool"
    ]
    mock_output_manager.variables_pool = {}


def test_filter_variables_pool_with_matching_filters_in_pattern_pool(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for matching pattern pool with function _filter_variables_pool in output_manager.py"""
    mock_output_manager.variables_pool = {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3",
    }
    dummy_input_file = ""
    filter_patterns = ["key1", "key2"]
    expected_result = {"key1": "value1", "key2": "value2"}

    assert (
        mock_output_manager._filter_variables_pool(filter_patterns, dummy_input_file)
        == expected_result
    )

    # Restore original method
    mock_output_manager._filter_variables_pool = output_manager_original_method_states[
        "_filter_variables_pool"
    ]
    mock_output_manager.variables_pool = {}


def test_filter_variables_pool_exclude_matching_filters_in_pattern_pool(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for exclude keyword in matching pattern pool with
    function _filter_variables_pool in output_manager.py"""
    mock_output_manager.variables_pool = {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3",
    }
    dummy_input_file = ""
    filter_patterns = ["exclude", "key1", "key2"]
    expected_result = {"key3": "value3"}

    assert (
        mock_output_manager._filter_variables_pool(filter_patterns, dummy_input_file)
        == expected_result
    )

    # Restore original method
    mock_output_manager._filter_variables_pool = output_manager_original_method_states[
        "_filter_variables_pool"
    ]
    mock_output_manager.variables_pool = {}


def test_filter_variables_pool_non_matching_pattern(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for pattern pool with non-matching pattern with
    function _filter_variables_pool in output_manager.py"""
    mock_output_manager.variables_pool = {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3",
    }
    dummy_input_file = ""
    filter_patterns = ["key1", "key4"]
    expected_result = {"key1": "value1"}

    assert (
        mock_output_manager._filter_variables_pool(filter_patterns, dummy_input_file)
        == expected_result
    )

    # Restore original method
    mock_output_manager._filter_variables_pool = output_manager_original_method_states[
        "_filter_variables_pool"
    ]
    mock_output_manager.variables_pool = {}


def test_filter_variables_pool_exclude_non_matching_pattern(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for pattern pool with exclude keyword and non-matching pattern with
    function _filter_variables_pool in output_manager.py"""
    mock_output_manager.variables_pool = {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3",
    }
    dummy_input_file = ""
    filter_patterns = ["exclude", "key1", "key4"]
    expected_result = {"key2": "value2", "key3": "value3"}

    assert (
        mock_output_manager._filter_variables_pool(filter_patterns, dummy_input_file)
        == expected_result
    )


def test_filter_variables_pool_duplicate_patterns(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for pattern pool with duplicate patterns with
    function _filter_variables_pool in output_manager.py"""
    mock_output_manager.variables_pool = {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3",
    }
    dummy_input_file = ""
    filter_patterns = ["key1", "key1"]
    expected_result = {"key1": "value1"}

    assert (
        mock_output_manager._filter_variables_pool(filter_patterns, dummy_input_file)
        == expected_result
    )

    # Restore original method
    mock_output_manager._filter_variables_pool = output_manager_original_method_states[
        "_filter_variables_pool"
    ]
    mock_output_manager.variables_pool = {}


def test_filter_variables_pool_exclude_duplicate_patterns(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for pattern pool with duplicate patterns and exclude keyword with
    function _filter_variables_pool in output_manager.py"""
    mock_output_manager.variables_pool = {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3",
    }
    dummy_input_file = ""
    filter_patterns = ["exclude", "key1", "key1"]
    expected_result = {"key2": "value2", "key3": "value3"}

    assert (
        mock_output_manager._filter_variables_pool(filter_patterns, dummy_input_file)
        == expected_result
    )

    # Restore original method
    mock_output_manager._filter_variables_pool = output_manager_original_method_states[
        "_filter_variables_pool"
    ]
    mock_output_manager.variables_pool = {}


@pytest.fixture
def mock_variables_pool() -> Dict[str, str]:
    dummy_variables_pool = {
        "DummyClass1.dummy_fun1.dummy_var1": "value1",
        "DummyClass1.dummy_fun1.dummy_var2": "value2",  # same class as prev, same fun, different var
        "DummyClass2.dummy_fun2.dummy_var3": "value3",  # new class, new fun, new var
        "DummyClass2.dummy_fun3.dummy_var4": "value4",  # same class as prev, new fun, new var
        "DummyClass2.dummy_fun4.dummy_var4": "value5",  # same class as prev, new fun, same var
        "DummyClass3.dummy_fun4.dummy_var2": "value6",  # new class, new fun, same var name as 2nd entry
        "DummyClass4.dummy_fun2.dummy_var5": "value7",  # new class, same fun name as 3rd entry, new var
    }
    return dummy_variables_pool


def test_filter_variables_pool_regex_patterns(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    mock_variables_pool: Dict[str, str],
) -> None:
    """Test case for pattern pool using regex patterns with
    function _filter_variables_pool in output_manager.py"""
    mock_output_manager.variables_pool = mock_variables_pool
    dummy_input_file = ""

    # get all Class1 vars
    filter_patterns = ["^DummyClass1.*"]
    expected_result = {
        "DummyClass1.dummy_fun1.dummy_var1": "value1",
        "DummyClass1.dummy_fun1.dummy_var2": "value2",
    }

    assert (
        mock_output_manager._filter_variables_pool(filter_patterns, dummy_input_file)
        == expected_result
    )

    # get only vars from fun2s
    filter_patterns = [".*fun2.*"]
    expected_result = {
        "DummyClass2.dummy_fun2.dummy_var3": "value3",
        "DummyClass4.dummy_fun2.dummy_var5": "value7",
    }

    assert (
        mock_output_manager._filter_variables_pool(filter_patterns, dummy_input_file)
        == expected_result
    )

    # get Class2 with var4 but not Class2 with var3
    filter_patterns = ["^DummyClass2.*var4$"]
    expected_result = {
        "DummyClass2.dummy_fun3.dummy_var4": "value4",
        "DummyClass2.dummy_fun4.dummy_var4": "value5",
    }

    assert (
        mock_output_manager._filter_variables_pool(filter_patterns, dummy_input_file)
        == expected_result
    )

    # get all var2s and var4s
    filter_patterns = [".*var2$", ".*var4$"]
    expected_result = {
        "DummyClass1.dummy_fun1.dummy_var2": "value2",
        "DummyClass2.dummy_fun3.dummy_var4": "value4",
        "DummyClass2.dummy_fun4.dummy_var4": "value5",
        "DummyClass3.dummy_fun4.dummy_var2": "value6",
    }

    assert (
        mock_output_manager._filter_variables_pool(filter_patterns, dummy_input_file)
        == expected_result
    )

    # Restore original method
    mock_output_manager._filter_variables_pool = output_manager_original_method_states[
        "_filter_variables_pool"
    ]
    mock_output_manager.variables_pool = {}


def test_filter_variables_pool_exclude_regex_patterns(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    mock_variables_pool: Dict[str, str],
) -> None:
    """Test case for pattern pool with regex patterns and exclude keyword with
    function _filter_variables_pool in output_manager.py"""
    mock_output_manager.variables_pool = mock_variables_pool
    dummy_input_file = ""

    # get everything except Class1 vars
    filter_patterns = ["exclude", "^DummyClass1.*"]
    expected_result = {
        "DummyClass2.dummy_fun2.dummy_var3": "value3",
        "DummyClass2.dummy_fun3.dummy_var4": "value4",
        "DummyClass2.dummy_fun4.dummy_var4": "value5",
        "DummyClass3.dummy_fun4.dummy_var2": "value6",
        "DummyClass4.dummy_fun2.dummy_var5": "value7",
    }

    assert (
        mock_output_manager._filter_variables_pool(filter_patterns, dummy_input_file)
        == expected_result
    )

    # get everything except vars from fun2s
    filter_patterns = ["exclude", ".*fun2.*"]
    expected_result = {
        "DummyClass1.dummy_fun1.dummy_var1": "value1",
        "DummyClass1.dummy_fun1.dummy_var2": "value2",
        "DummyClass2.dummy_fun3.dummy_var4": "value4",
        "DummyClass2.dummy_fun4.dummy_var4": "value5",
        "DummyClass3.dummy_fun4.dummy_var2": "value6",
    }

    assert (
        mock_output_manager._filter_variables_pool(filter_patterns, dummy_input_file)
        == expected_result
    )

    # get everything without Class2 with var4
    filter_patterns = ["exclude", "^DummyClass2.*var4$"]
    expected_result = {
        "DummyClass1.dummy_fun1.dummy_var1": "value1",
        "DummyClass1.dummy_fun1.dummy_var2": "value2",
        "DummyClass2.dummy_fun2.dummy_var3": "value3",
        "DummyClass3.dummy_fun4.dummy_var2": "value6",
        "DummyClass4.dummy_fun2.dummy_var5": "value7",
    }

    assert (
        mock_output_manager._filter_variables_pool(filter_patterns, dummy_input_file)
        == expected_result
    )

    # get everything that doesn't have var2s and var4s
    filter_patterns = ["exclude", ".*var2$", ".*var4$"]
    expected_result = {
        "DummyClass1.dummy_fun1.dummy_var1": "value1",
        "DummyClass2.dummy_fun2.dummy_var3": "value3",
        "DummyClass4.dummy_fun2.dummy_var5": "value7",
    }

    assert (
        mock_output_manager._filter_variables_pool(filter_patterns, dummy_input_file)
        == expected_result
    )

    # Restore original method
    mock_output_manager._filter_variables_pool = output_manager_original_method_states[
        "_filter_variables_pool"
    ]
    mock_output_manager.variables_pool = {}


@pytest.mark.parametrize(
    "exclude_info_maps, produce_graphics, filter_content, is_faulty",
    [
        (True, True, [{"filters": ".*", "title": "dummy_title"}], False),
        (True, False, [{"filters": ".*", "title": "dummy_title"}], False),
        (False, True, [{"filters": ".*", "title": "dummy_title"}], False),
        (False, False, [{"filters": ".*", "title": "dummy_title"}], False),
        (True, True, [{"no_filters": ".*", "title": "dummy_title"}], True),
        (True, True, ["no_dict"], True),
    ],
)
def test_save_results(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    exclude_info_maps: bool,
    produce_graphics: bool,
    filter_content: List[Dict[str, str]],
    is_faulty: bool,
) -> None:
    # Arrange
    mock_output_manager.variables_pool = {}
    mock_output_manager._generate_file_name = MagicMock(return_value="dummy_name")
    mock_output_manager._load_filter_file_content = MagicMock(
        return_value=filter_content
    )
    mock_output_manager._list_filter_files_in_dir = MagicMock(
        return_value=[
            "csv_input_filepath1.txt",
            "graph_input_filepath2.txt",
        ]
    )
    mock_output_manager._exclude_info_maps = MagicMock(return_value={})
    mock_output_manager._route_save_functions = MagicMock()
    mock_output_manager.add_error = MagicMock()

    # Act
    mock_output_manager.save_results(
        "save_path", "filters_path", exclude_info_maps, produce_graphics, "graphics_dir"
    )

    # Assert
    if is_faulty:
        mock_output_manager._exclude_info_maps.assert_not_called()
        mock_output_manager._route_save_functions.assert_not_called()
        assert mock_output_manager.add_error.call_count == 2
    else:
        mock_output_manager.add_error.assert_not_called()
        if exclude_info_maps:
            mock_output_manager._exclude_info_maps.assert_has_calls(
                [call({}), call({})]
            )
        else:
            mock_output_manager._exclude_info_maps.assert_not_called()
        mock_output_manager._route_save_functions.assert_has_calls(
            [
                call(
                    "csv_input_filepath1.txt",
                    "save_path",
                    {},
                    produce_graphics,
                    {"filters": ".*", "title": "dummy_title"},
                    "graphics_dir",
                ),
                call(
                    "graph_input_filepath2.txt",
                    "save_path",
                    {},
                    produce_graphics,
                    {"filters": ".*", "title": "dummy_title"},
                    "graphics_dir",
                ),
            ]
        )

    # Restore original method
    mock_output_manager.save_results = output_manager_original_method_states[
        "save_results"
    ]
    mock_output_manager._list_filter_files_in_dir = (
        output_manager_original_method_states["_list_filter_files_in_dir"]
    )
    mock_output_manager._generate_file_name = output_manager_original_method_states[
        "_generate_file_name"
    ]
    mock_output_manager._load_filter_file_content = (
        output_manager_original_method_states["_load_filter_file_content"]
    )
    mock_output_manager._exclude_info_maps = output_manager_original_method_states[
        "_exclude_info_maps"
    ]
    mock_output_manager._route_save_functions = output_manager_original_method_states[
        "_route_save_functions"
    ]
    mock_output_manager.add_error = output_manager_original_method_states["add_error"]


def test_route_save_functions_csv(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    mock_output_manager._save_variables_to_csv_files = MagicMock()
    mock_output_manager._route_save_functions(
        "csv_file",
        "save_path",
        {"key": {"var": "value"}},
        True,
        {"filters": "regex"},
        "graphics_dir",
    )
    mock_output_manager._save_variables_to_csv_files.assert_called_once_with(
        {"key": {"var": "value"}}, "csv_file", os.path.join("save_path", "CSVs", "om")
    )
    # Restore original method
    mock_output_manager._save_variables_to_csv_files = (
        output_manager_original_method_states["_save_variables_to_csv_files"]
    )
    mock_output_manager._route_save_functions = output_manager_original_method_states[
        "_route_save_functions"
    ]


def test_route_save_functions_json(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    mock_output_manager._dict_to_file_json = MagicMock()
    mock_output_manager._generate_file_name = MagicMock(return_value="filename.json")
    mock_output_manager._route_save_functions(
        "json_file",
        "save_path",
        {"key": {"var": "value"}},
        True,
        {"filters": "regex"},
        "graphics_dir",
    )
    mock_output_manager._dict_to_file_json.assert_called_once_with(
        {"key": {"var": "value"}}, os.path.join("save_path", "filename.json")
    )
    # Restore original method
    mock_output_manager._dict_to_file_json = output_manager_original_method_states[
        "_dict_to_file_json"
    ]
    mock_output_manager._route_save_functions = output_manager_original_method_states[
        "_route_save_functions"
    ]


def test_route_save_functions_graph(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    with patch(
        "RUFAS.graph_generator.GraphGenerator.generate_graph"
    ) as mock_generate_graph:
        mock_output_manager.add_warning = MagicMock()
        mock_output_manager.add_error = MagicMock()
        graph_data = {"filters": ".*", "other keys": "other values"}
        mock_output_manager._route_save_functions(
            "graph_file",
            "save_path",
            {"key": {"var": "value"}},
            False,
            graph_data,
            "graphics_dir",
        )
        mock_generate_graph.assert_not_called()
        mock_output_manager.add_warning.assert_called_once_with(
            "No Graphics",
            "Graphic generation is disabled, skipping filter_file='graph_file'",
            {"class": "OutputManager", "function": "_route_save_functions"},
        )

        mock_output_manager._route_save_functions(
            "graph_file",
            "save_path",
            {"key": {"var": "value"}},
            True,
            graph_data,
            "graphics_dir",
        )
        mock_output_manager.add_warning.assert_called_once_with(
            "No Graphics",
            "Graphic generation is disabled, skipping filter_file='graph_file'",
            {"class": "OutputManager", "function": "_route_save_functions"},
        )
        mock_generate_graph.assert_called_once_with(
            {"key": {"var": "value"}},
            graph_data,
            "save_path",
            "graph_file",
            "graphics_dir",
        )

        mock_generate_graph.side_effect = Exception("test exception")
        mock_output_manager._route_save_functions(
            "graph_file",
            "save_path",
            {"key": {"var": "value"}},
            True,
            graph_data,
            "graphics_dir",
        )
        mock_output_manager.add_error.assert_called_once_with(
            "graph generation exception",
            "test exception",
            {"class": "OutputManager", "function": "_route_save_functions"},
        )

    mock_output_manager._route_save_functions = output_manager_original_method_states[
        "_route_save_functions"
    ]
    mock_output_manager.add_warning = output_manager_original_method_states[
        "add_warning"
    ]
    mock_output_manager.add_error = output_manager_original_method_states["add_error"]


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
    _ = mocker.patch.object(Utility, "_get_str", side_effect=lambda x: str(x))

    # Act
    result = Utility._make_serializable(input_obj, depth, max_depth)

    # Assert
    assert result == expected_output


def test_load_variables_pool_from_file_valid_path(mock_output_manager: OutputManager,
                                                  output_manager_original_method_states: Dict[str, Callable],
                                                  ) -> None:
    """Checks that load_variables_pool_from_file loads the valid filepath provided to the OM variables pool"""
    dummy_data = {"vars": {"var1": {"values": [1, 2, 3], "info_map": {"imvar1": 1, "imvar2": 2}},
                           "var2": {"values": {"a": 1, "b": 2}, "info_map": {}}}}
    with patch('builtins.open', mock_open(read_data=json.dumps(dummy_data))):
        mock_output_manager.load_variables_pool_from_file(Path("path/to/file"))
        assert mock_output_manager.variables_pool == dummy_data

    mock_output_manager.load_variables_pool_from_file = output_manager_original_method_states[
        "load_variables_pool_from_file"
    ]


@patch("builtins.open", new_callable=mock_open)
def test_load_variables_pool_from_file_raises_exception(mock_file: MagicMock,
                                                        mock_output_manager: OutputManager,
                                                        output_manager_original_method_states: Dict[str, Callable],
                                                        ) -> None:
    """Checks that load_variables_pool_from_file raises exceptions with a bad filepath provided"""
    mock_file.side_effect = FileNotFoundError
    with pytest.raises(FileNotFoundError):
        mock_output_manager.load_variables_pool_from_file(Path("bad/file/path"))
        assert mock_output_manager.variables_pool == {}

    mock_file.return_value.read.return_value = "this is not valid JSON"
    with patch('builtins.open', mock_open(read_data="bad/file/path")):
        with pytest.raises(json.JSONDecodeError):
            mock_output_manager.load_variables_pool_from_file(Path("bad/file/path.json"))
            assert mock_output_manager.variables_pool == {}

    mock_output_manager.load_variables_pool_from_file = output_manager_original_method_states[
        "load_variables_pool_from_file"
    ]


@pytest.mark.parametrize(
    "self, other, expected_result",
    [
        (LogVerbosity.NONE, LogVerbosity.NONE, True),
        (LogVerbosity.NONE, LogVerbosity.ERRORS, True),
        (LogVerbosity.NONE, LogVerbosity.WARNINGS, True),
        (LogVerbosity.NONE, LogVerbosity.LOGS, True),
        (LogVerbosity.ERRORS, LogVerbosity.ERRORS, True),
        (LogVerbosity.ERRORS, LogVerbosity.NONE, False),
        (LogVerbosity.ERRORS, LogVerbosity.WARNINGS, True),
        (LogVerbosity.ERRORS, LogVerbosity.LOGS, True),
        (LogVerbosity.WARNINGS, LogVerbosity.NONE, False),
        (LogVerbosity.WARNINGS, LogVerbosity.WARNINGS, True),
        (LogVerbosity.WARNINGS, LogVerbosity.ERRORS, False),
        (LogVerbosity.WARNINGS, LogVerbosity.LOGS, True),
        (LogVerbosity.LOGS, LogVerbosity.LOGS, True),
        (LogVerbosity.LOGS, LogVerbosity.NONE, False),
        (LogVerbosity.LOGS, LogVerbosity.ERRORS, False),
        (LogVerbosity.LOGS, LogVerbosity.WARNINGS, False),
    ],
)
def test_log_verbosity_less_than_method(
    self: LogVerbosity, other: LogVerbosity, expected_result: bool
) -> None:
    """Unit test for __le__ method in LogVerbosity class"""
    actual_result = self <= other
    assert actual_result == expected_result


def test_log_verbosity_str_method() -> None:
    """Unit test for __str__ method in LogVerbosity class"""
    assert str(LogVerbosity.NONE) == "NONE"
    assert str(LogVerbosity.ERRORS) == "ERROR"
    assert str(LogVerbosity.WARNINGS) == "WARNING"
    assert str(LogVerbosity.LOGS) == "LOG"


def test_log_verbosity_enum_values() -> None:
    """Unit test for LogVerbosity class enum values"""
    assert LogVerbosity.NONE.value == "none"
    assert LogVerbosity.ERRORS.value == "errors"
    assert LogVerbosity.WARNINGS.value == "warnings"
    assert LogVerbosity.LOGS.value == "logs"
