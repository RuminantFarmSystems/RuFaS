import json
import os
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, List, Union, Type

import pandas as pd
import pytest
from freezegun import freeze_time
from mock import mock_open, patch
from mock.mock import MagicMock, call
from pytest import raises
from pytest_mock.plugin import MockerFixture

from RUFAS.output_manager import LogVerbosity, OutputManager
from RUFAS.units import MeasurementUnits

DISCLAIMER_MESSAGE = "Under construction, use the results with caution."


def test_get_prefix() -> None:
    """Unit test for function _get_prefix in file output_manager.py"""
    om = OutputManager()
    assert om._get_prefix("class", "func") == "class.func"


@pytest.fixture
def mock_output_manager() -> OutputManager:
    output_manager = OutputManager()
    return output_manager


def test_set_metadata_prefix(mock_output_manager: OutputManager) -> None:
    """Unit test for the function set_metadata_prefix in the file output_manager.py"""

    # Assert before setting metadata_prefix
    assert getattr(mock_output_manager, "_OutputManager__metadata_prefix") == ""

    # Act
    mock_output_manager.set_metadata_prefix("dummy_prefix")

    # Assert after setting metadata_prefix
    assert getattr(mock_output_manager, "_OutputManager__metadata_prefix") == "dummy_prefix"

    # Cleanup
    mock_output_manager.set_metadata_prefix("")


@pytest.mark.parametrize(
    "log_verbose",
    [LogVerbosity.NONE, LogVerbosity.ERRORS, LogVerbosity.WARNINGS, LogVerbosity.LOGS],
)
def test_set_log_verbose(mock_output_manager: OutputManager, log_verbose: LogVerbosity) -> None:
    """Unit test for the function set_log_verbose in the file output_manager.py"""

    # Assert before setting log_verbose
    assert getattr(mock_output_manager, "_OutputManager__log_verbose") == LogVerbosity.CREDITS

    # Act
    mock_output_manager.set_log_verbose(log_verbose)

    # Assert after setting log_verbose
    assert getattr(mock_output_manager, "_OutputManager__log_verbose") == log_verbose

    # Cleanup
    mock_output_manager.set_log_verbose(LogVerbosity.CREDITS)


@pytest.mark.parametrize(
    "variable_name, data, expected_result",
    [
        (
            "temperature",
            {"values": [25.0, 30.0, 35.0], "info_maps": [{"units": "Celsius"}]},
            [pd.Series([25.0, 30.0, 35.0], name="temperature_Celsius", dtype=object)],
        ),
        (
            "position",
            {
                "values": [
                    {"x": 1.0, "y": 2.0},
                    {"x": 3.0, "y": 4.0},
                    {"x": 5.0, "y": 6.0},
                ],
                "info_maps": [{"units": {"x": "m", "y": "m"}}],
            },
            [
                pd.Series([1.0, 3.0, 5.0], name="position.x_m", dtype=object),
                pd.Series([2.0, 4.0, 6.0], name="position.y_m", dtype=object),
            ],
        ),
        (
            "measurements",
            {
                "values": [
                    {"value": 10.5, "error": 0.1},
                    {"value": 20.3, "error": 0.2},
                    {"value": 15.7, "error": 0.15},
                ],
                "info_maps": [{"units": {"value": "kg", "error": "kg"}}],
            },
            [
                pd.Series([10.5, 20.3, 15.7], name="measurements.value_kg", dtype=object),
                pd.Series([0.1, 0.2, 0.15], name="measurements.error_kg", dtype=object),
            ],
        ),
        (
            "pressure",
            {"values": [100.0, 200.0, 300.0]},
            [pd.Series([100.0, 200.0, 300.0], name="pressure", dtype=object)],
        ),
        (
            "empty_data",
            {"values": [], "info_maps": []},
            [pd.Series([], name="empty_data", dtype=object)],
        ),
    ],
)
def test_dict_to_csv_column_list(
    variable_name: str,
    data: Dict[str, List[Any]],
    expected_result: List[pd.Series],
) -> None:
    """Unit test for the function _dict_to_csv_column_list in the file output_manager.py"""

    # Arrange
    output_manager = OutputManager()
    expected_length = len(expected_result)

    # Act
    result = output_manager._dict_to_csv_column_list(variable_name, data)

    # Assert
    assert len(result) == expected_length

    for i, series in enumerate(result):
        assert series.equals(expected_result[i])

        if i == 0 and data.get("info_maps", []):
            units = data["info_maps"][0].get("units")
            if isinstance(units, dict):
                for subkey in units:
                    assert f" ({units[subkey]})" in series.name
            elif units:
                assert f" ({units})" in series.name

    # Cleanup
    output_manager.flush_pools()


@pytest.mark.parametrize(
    "variable_name, units, subkey, expected_result, expected_error",
    [
        ("temperature", "Celsius", None, " (Celsius)", None),
        ("position", {"x": "m", "y": "m"}, "x", " (m)", None),
        ("position", {"x": "m", "y": "m"}, "z", "", "units_key_error"),
        ("pressure", None, None, "", None),
        ("empty_units", "", None, "", None),
        ("nested_units", {"value": "kg", "error": "kg"}, "value", " (kg)", None),
        ("nested_units", {"value": "kg", "error": "kg"}, "uncertainty", "", "units_key_error"),
        ("coordinates", {"x": "m", "y": "m"}, None, "", "units_subkey_missing"),
    ],
)
def test_get_units_substr(
    variable_name: str,
    units: str | Dict[str, str] | None,
    subkey: str | None,
    expected_result: str,
    expected_error: str | None,
    mocker: MockerFixture,
) -> None:
    """Unit test for the _get_units_substr() method in the file output_manager.py"""

    # Arrange
    output_manager = OutputManager()
    patch_for_add_error = mocker.patch.object(output_manager, "add_error")
    info_map = {
        "class": output_manager.__class__.__name__,
        "function": "_get_units_substr",
    }

    # Act
    result = output_manager._get_units_substr(variable_name, units, subkey)

    # Assert
    assert result == expected_result

    if expected_error == "units_key_error":
        patch_for_add_error.assert_called_once_with(
            "units_key_error",
            f"Key '{subkey}' not found in the units dictionary for variable '{variable_name}'.",
            info_map=info_map,
        )
    elif expected_error == "units_subkey_missing":
        patch_for_add_error.assert_called_once_with(
            "units_subkey_missing",
            f"Variable {variable_name} has a dictionary for its 'units' property, "
            f"but the 'values' associated with this variable are not dictionaries themselves.",
            info_map=info_map,
        )
    else:
        patch_for_add_error.assert_not_called()


@pytest.mark.parametrize(
    "data, expected_result, should_write",
    [
        (
            {"var1": {"values": [1.0, True, "test"], "info_maps": []}},
            f'DISCLAIMER,var1{os.linesep}"{DISCLAIMER_MESSAGE}",1.0{os.linesep},True' f"{os.linesep},test{os.linesep}",
            True,
        ),
        (
            {"var1": {"values": [1.0, True, "test"]}},
            f'DISCLAIMER,var1{os.linesep}"{DISCLAIMER_MESSAGE}",1.0{os.linesep},True{os.linesep}' f",test{os.linesep}",
            True,
        ),
        (
            {
                "var1": {
                    "values": [1, 2, 3],
                    "info_maps": [{"units": "m"}, {"units": "m"}, {"units": "m"}],
                }
            },
            f'DISCLAIMER,var1 (m){os.linesep}"{DISCLAIMER_MESSAGE}",1{os.linesep},2' f"{os.linesep},3{os.linesep}",
            True,
        ),
        (
            {"var1": {"values": [1, 2, 3]}},
            f'DISCLAIMER,var1{os.linesep}"{DISCLAIMER_MESSAGE}",1{os.linesep},2{os.linesep}' f",3{os.linesep}",
            True,
        ),
        (
            {
                "var1": {
                    "values": [1, 2],
                    "info_maps": [{"units": "unitless"}, {"units": "unitless"}],
                }
            },
            f'DISCLAIMER,var1 (unitless){os.linesep}"{DISCLAIMER_MESSAGE}",1{os.linesep}' f",2{os.linesep}",
            True,
        ),
        (
            {
                "var1": {
                    "values": [{"v1": 1, "v2": 1}, {"v1": 2, "v2": 2}],
                    "info_maps": [{"units": {"v1": "m", "v2": "s"}}, {"units": {"v1": "m", "v2": "s"}}],
                }
            },
            f'DISCLAIMER,var1.v1 (m),var1.v2 (s){os.linesep}"{DISCLAIMER_MESSAGE}",1,1{os.linesep}' f",2,2{os.linesep}",
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
                            "units": {
                                "key1": "random unit 1",
                                "key2": "random unit 2",
                            }
                        },
                        {
                            "units": {
                                "key1": "random unit 1",
                                "key2": "random unit 2",
                            }
                        },
                    ],
                }
            },
            f"DISCLAIMER,simple_key.key1 (random unit 1),simple_key.key2 (random unit 2)"
            f'{os.linesep}"{DISCLAIMER_MESSAGE}",'
            f'1,"[1, 1]"{os.linesep}'
            f","
            f'2,"[2, 2]"{os.linesep}'
            f","
            f'3,"[3, 3]"{os.linesep}',
            True,
        ),
        (
            {
                "simple_key1": {"values": [1, 2, 3]},
                "simple_key2": {"values": [4, 5, 6]},
            },
            f'DISCLAIMER,simple_key1,simple_key2{os.linesep}"{DISCLAIMER_MESSAGE}",'
            f"1,4{os.linesep},2,5{os.linesep},3,6{os.linesep}",
            True,
        ),
        (
            {
                "simple_key1": {
                    "values": [1, 2, 3],
                    "info_maps": [
                        {"subkey1": "Farm", "subkey2": "Field", "units": "random unit"},
                        {"subkey1": "Farm", "subkey2": "Field", "units": "random unit"},
                        {"subkey1": "Farm", "subkey2": "Field", "units": "random unit"},
                    ],
                },
                "simple_key2": {
                    "values": [4, 5, 6, 8, 9],
                    "info_maps": [
                        {"subkey1": "Tractor", "units": "random unit"},
                        {"subkey1": "Tractor", "units": "random unit"},
                        {"subkey1": "Tractor", "units": "random unit"},
                    ],
                },
            },
            f"DISCLAIMER,simple_key1 (random unit),simple_key2 (random unit)"
            f'{os.linesep}"{DISCLAIMER_MESSAGE}",'
            f"1,4{os.linesep},"
            f"2,5{os.linesep},"
            f"3,6{os.linesep},"
            f",8{os.linesep},"
            f",9{os.linesep}",
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
        open_mock.assert_any_call("test", "w", encoding="utf-8", errors="strict", newline="")

    written_data = "".join(call[1][0] for call in open_mock().write.mock_calls)

    assert written_data == expected_result


def test_dict_to_file_json(mock_output_manager: OutputManager) -> None:
    """Unit test for the function dict_to_file_json in the file output_manager.py"""

    data = {
        "var1": {"values": [1], "info_maps": [{"map1": "value1"}, {"map1": "value2"}]},
        "var2": {
            "values": [{"v1": 1, "v2": 1}, {"v1": 2, "v2": 2}],
            "info_maps": [{"map1": "value1"}, {"map1": "value2"}],
        },
    }

    open_mock = mock_open()
    with patch("builtins.open", open_mock):
        mock_output_manager.dict_to_file_json(data, "test")

    written_data = "".join(call[1][0] for call in open_mock().write.mock_calls)
    assert written_data == json.dumps({**{"DISCLAIMER": DISCLAIMER_MESSAGE}, **data}, indent=2)


def test_dict_to_file_json_minify_output(mock_output_manager: OutputManager) -> None:
    """Unit test for the function dict_to_file_json in the file output_manager.py"""

    data = {
        "var1": {"values": [1], "info_maps": [{"map1": "value1"}, {"map1": "value2"}]},
        "var2": {
            "values": [{"v1": 1, "v2": 1}, {"v1": 2, "v2": 2}],
            "info_maps": [{"map1": "value1"}, {"map1": "value2"}],
        },
    }

    open_mock = mock_open()
    with patch("builtins.open", open_mock):
        mock_output_manager.dict_to_file_json(data, "test", minify_output_file=True)

    written_data = "".join(call[1][0] for call in open_mock().write.mock_calls)
    assert written_data == json.dumps({**{"DISCLAIMER": DISCLAIMER_MESSAGE}, **data}, separators=(",", ":"))


def test_dict_to_file_json_exception(mock_output_manager: OutputManager) -> None:
    """Test file opening failure for dict_to_file_json() in the file output_manager.py"""
    open_mock = mock_open()
    open_mock.side_effect = IOError
    data = {"var1": {"values": [1, 2, 3], "info_maps": [1, 2, 3]}}

    with patch("builtins.open", open_mock):
        with raises(Exception):
            mock_output_manager.dict_to_file_json(data, "test")


def test_dict_to_file_csv_exception(mock_output_manager: OutputManager) -> None:
    """Unit test for the function _dict_to_file_csv in the file output_manager.py"""
    open_mock = mock_open()
    open_mock.side_effect = IOError
    data = {"var1": {"values": [1, 2, 3], "info_maps": [1, 2, 3]}}

    with patch("builtins.open", open_mock):
        with raises(Exception):
            mock_output_manager._dict_to_file_csv(data, "test")


def test_generate_key(mocker: MockerFixture) -> None:
    """Unit test for function _generate_key in file output_manager.py"""
    om = OutputManager()
    with raises(KeyError):
        om._generate_key("name", {})

    with raises(KeyError):
        om._generate_key("name", {"class": "test"})

    info_map: dict[str, str | bool] = {"class": "dummy_class", "function": "dummy_func"}
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


@pytest.mark.parametrize(
    "log_verbose",
    [LogVerbosity.NONE, LogVerbosity.ERRORS, LogVerbosity.WARNINGS, LogVerbosity.LOGS],
)
def test_add_error(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    log_verbose: LogVerbosity,
    mocker: MockerFixture,
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
    # mock_output_manager._get_timestamp = MagicMock(return_value=timestamp)
    mocker.patch("RUFAS.output_manager.Utility.get_timestamp", return_value=timestamp)
    mock_output_manager.set_log_verbose(log_verbose)
    mock_output_manager.set_metadata_prefix(metadata_prefix)
    mock_output_manager._handle_log_output = MagicMock()

    mock_output_manager.add_error(name, message, info_map)

    mock_output_manager._generate_key.assert_called_once_with(name, info_map)

    assert info_map.get("timestamp") == timestamp
    mock_output_manager._handle_log_output.assert_called_once_with(name, message, info_map, LogVerbosity.ERRORS)
    mock_output_manager._add_to_pool(mock_output_manager.errors_pool, key, message, info_map)

    mock_output_manager._generate_key = output_manager_original_method_states["_generate_key"]
    mock_output_manager._add_to_pool = output_manager_original_method_states["_add_to_pool"]
    mock_output_manager._handle_log_output = output_manager_original_method_states["_handle_log_output"]
    mock_output_manager.add_error = output_manager_original_method_states["add_error"]


@pytest.mark.parametrize(
    "log_verbose",
    [LogVerbosity.NONE, LogVerbosity.ERRORS, LogVerbosity.WARNINGS, LogVerbosity.LOGS],
)
def test_add_warning(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    log_verbose: LogVerbosity,
    mocker: MockerFixture,
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
    mocker.patch("RUFAS.output_manager.Utility.get_timestamp", return_value=timestamp)
    mock_output_manager.set_log_verbose(log_verbose)
    mock_output_manager.set_metadata_prefix(metadata_prefix)
    mock_output_manager._handle_log_output = MagicMock()

    mock_output_manager.add_warning(name, message, info_map)

    mock_output_manager._generate_key.assert_called_once_with(name, info_map)

    assert info_map.get("timestamp") == timestamp
    mock_output_manager._handle_log_output.assert_called_once_with(name, message, info_map, LogVerbosity.WARNINGS)

    mock_output_manager._add_to_pool(mock_output_manager.warnings_pool, key, message, info_map)

    mock_output_manager._generate_key = output_manager_original_method_states["_generate_key"]
    mock_output_manager._add_to_pool = output_manager_original_method_states["_add_to_pool"]
    mock_output_manager._handle_log_output = output_manager_original_method_states["_handle_log_output"]
    mock_output_manager.add_warning = output_manager_original_method_states["add_warning"]


@pytest.mark.parametrize(
    "log_verbose",
    [LogVerbosity.NONE, LogVerbosity.ERRORS, LogVerbosity.WARNINGS, LogVerbosity.LOGS],
)
def test_add_log(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    log_verbose: LogVerbosity,
    mocker: MockerFixture,
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
    mocker.patch("RUFAS.output_manager.Utility.get_timestamp", return_value=timestamp)
    mock_output_manager.set_log_verbose(log_verbose)
    mock_output_manager.set_metadata_prefix(metadata_prefix)
    mock_output_manager._handle_log_output = MagicMock()

    mock_output_manager.add_log(name, message, info_map)

    mock_output_manager._generate_key.assert_called_once_with(name, info_map)

    assert info_map.get("timestamp") == timestamp

    mock_output_manager._handle_log_output.assert_called_once_with(name, message, info_map, LogVerbosity.LOGS)

    mock_output_manager._add_to_pool(mock_output_manager.logs_pool, key, message, info_map)

    mock_output_manager._generate_key = output_manager_original_method_states["_generate_key"]
    mock_output_manager._add_to_pool = output_manager_original_method_states["_add_to_pool"]
    mock_output_manager._handle_log_output = output_manager_original_method_states["_handle_log_output"]
    mock_output_manager.add_log = output_manager_original_method_states["add_log"]


@pytest.mark.parametrize(
    "name, value, info_map, first_map, expected_exception",
    [
        # Case 1: Everything correct, no exception should be raised
        ("var1", 100, {"class": "TestClass", "function": "test_function", "units": "kg"}, True, None),
        # Case 1.5: Everything correct, no exception should be raised, only first info map should be recorded.
        ("var1", 100, {"class": "TestClass", "function": "test_function", "units": "kg"}, False, None),
        # Case 2: 'units' key missing, should raise KeyError
        ("var2", 200, {"class": "TestClass", "function": "test_function"}, True, KeyError),
        # Case 3: Value is a dict, should process sub-keys
        (
            "var3",
            {"sub1": 10, "sub2": 20},
            {"class": "TestClass", "function": "test_function", "units": "kg"},
            True,
            None,
        ),
    ],
)
def test_add_variable(
    name: str,
    value: Any,
    info_map: Dict[str, Any],
    first_map: bool,
    expected_exception: Type[BaseException] | None,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for the add_variable() method in output_manager.py.
    """

    # Arrange
    output_manager = OutputManager()
    mocker.patch.object(output_manager, "_stringify_units", return_value="validated_units")
    mocker.patch.object(output_manager, "_generate_key", return_value="key_with_prefix")
    patched_add_to_pool = mocker.patch.object(output_manager, "_add_to_pool")
    mocker.patch.dict(output_manager._variables_usage_counter, {}, clear=True)

    if expected_exception:
        with pytest.raises(expected_exception):
            output_manager.add_variable(name, value, info_map, first_map)
    else:
        # Act
        output_manager.add_variable(name, value, info_map, first_map)
        # Assert
        patched_add_to_pool.assert_called_once_with(
            output_manager.variables_pool,
            "key_with_prefix",
            value,
            {**info_map, "units": "validated_units"},
            first_map,
        )
        if isinstance(value, dict):
            for k in value.keys():
                assert output_manager._variables_usage_counter[f"key_with_prefix.{k}"] == 0


@pytest.mark.parametrize(
    "units, expected_result",
    [
        (MeasurementUnits.ANIMALS, MeasurementUnits.ANIMALS.value),
        (
            {
                "first": MeasurementUnits.ANIMALS,
                "second": MeasurementUnits.ANIMALS,
                "nested": {"third": MeasurementUnits.DAYS},
            },
            {
                "first": MeasurementUnits.ANIMALS.value,
                "second": MeasurementUnits.ANIMALS.value,
                "nested": {"third": MeasurementUnits.DAYS.value},
            },
        ),
        (
            "invalid_unit",
            TypeError("The following unit does not have the type MeasurementUnits: invalid_unit (type <class 'str'>)."),
        ),
        (
            {
                "first": MeasurementUnits.ANIMALS,
                "invalid": "not_a_unit",
            },
            TypeError("The following unit does not have the type MeasurementUnits: not_a_unit (type <class 'str'>)."),
        ),
        (
            {
                "first": {"nested_invalid": "definitely_not_a_unit"},
                "second": MeasurementUnits.ANIMALS,
            },
            TypeError(
                "The following unit does not have the type MeasurementUnits: "
                "definitely_not_a_unit (type <class 'str'>)."
            ),
        ),
        (
            {
                "first": MeasurementUnits.ANIMALS,
                "invalid_type": 123,
            },
            TypeError("The following unit does not have the type MeasurementUnits: 123 (type <class 'int'>)."),
        ),
        (
            {
                "first": {"nested_invalid_type": True},
                "second": MeasurementUnits.ANIMALS,
            },
            TypeError("The following unit does not have the type MeasurementUnits: True (type <class 'bool'>)."),
        ),
    ],
)
def test_stringify_units(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    units: Dict[str, MeasurementUnits | Dict[str, MeasurementUnits]] | MeasurementUnits | str,
    expected_result: Dict[str, str] | str | Exception,
    mocker: MockerFixture,
) -> None:
    """Test for function _stringify_units in file output_manager.py"""
    if isinstance(expected_result, Exception):
        patch_for_add_error = mocker.patch.object(mock_output_manager, "add_error")
        with pytest.raises(type(expected_result)) as e:
            mock_output_manager._stringify_units(units)
        assert str(expected_result) == str(e.value)
        patch_for_add_error.assert_called_once()
    else:
        assert mock_output_manager._stringify_units(units) == expected_result


@pytest.mark.parametrize(
    "dummy_value, exclude_info_maps_flag, first_map_only",
    [
        ("dummy_value", False, False),
        (2, False, False),
        (3.45, False, True),
        (True, False, True),
        ({"key": "value"}, False, True),
        ([1, 2, 3], False, False),
        ("dummy_value", True, False),
        (2, True, False),
        (3.45, True, True),
        (True, True, True),
        ({"key": "value"}, True, True),
        ([1, 2, 3], True, True),
    ],
)
def test_add_to_pool(
    mock_output_manager: OutputManager,
    dummy_value: Any,
    exclude_info_maps_flag: bool,
    first_map_only: bool,
) -> None:
    """Unit test for function _add_to_pool in file output_manager.py"""

    # Arrange
    info_map = {
        "class": "dummy_class",
        "function": "dummy_func",
        "context": "dummy_context",
        "units": MeasurementUnits.ANIMALS.value,
    }
    key = "dummy_key"
    pool: Dict[str, Dict[str, Any]] = {}
    assert not mock_output_manager._exclude_info_maps_flag
    mock_output_manager._exclude_info_maps_flag = exclude_info_maps_flag

    # Act
    mock_output_manager._add_to_pool(pool, key, dummy_value, info_map, first_map_only)

    # Assert
    assert pool[key]["values"][0] == dummy_value
    if isinstance(dummy_value, (int, bool, float, str)):
        assert pool[key]["values"][0] is dummy_value
    else:
        assert pool[key]["values"][0] == deepcopy(dummy_value)

    if exclude_info_maps_flag:
        assert pool[key]["info_maps"] == []
    else:
        assert pool[key]["info_maps"] == [
            {"context": "dummy_context", "units": MeasurementUnits.ANIMALS.value},
        ]

    # Arrange
    info_map["more_context"] = "1234567890"

    # Act
    mock_output_manager._add_to_pool(pool, key, dummy_value, info_map, first_map_only)

    # Assert
    assert pool[key]["values"][1] == dummy_value
    if isinstance(dummy_value, (int, bool, float, str)):
        assert pool[key]["values"][1] is dummy_value
    else:
        assert pool[key]["values"][1] == deepcopy(dummy_value)

    if exclude_info_maps_flag:
        assert pool[key]["info_maps"] == []
    elif not first_map_only:
        assert pool[key]["info_maps"] == [
            {"context": "dummy_context", "units": MeasurementUnits.ANIMALS.value},
            {"context": "dummy_context", "more_context": "1234567890", "units": MeasurementUnits.ANIMALS.value},
        ]
    else:
        assert pool[key]["info_maps"] == [
            {"context": "dummy_context", "units": MeasurementUnits.ANIMALS.value},
        ]

    # Cleanup
    mock_output_manager._exclude_info_maps_flag = False


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
        "units": MeasurementUnits.ANIMALS,
    }
    om1.add_variable("dummy_name", "dummy_value", info_map)
    assert om2.variables_pool[key] == {
        "info_maps": [{"context": "dummy_context", "units": MeasurementUnits.ANIMALS.value}],
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
    om.set_log_verbose(log_level)
    om._handle_log_output(name, msg, info_map, log_level)
    log_format = "{color}[{timestamp}][{log_level}][{metadata_prefix}] {name}. {message}{color_reset}\n"
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
    info_map = {"class": "dummy_class", "function": "dummy_func", "units": MeasurementUnits.ANIMALS}
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
        "_write_disclaimer": mock_output_manager._write_disclaimer,
        "_dict_to_file_csv": mock_output_manager._dict_to_file_csv,
        "dict_to_file_json": mock_output_manager.dict_to_file_json,
        "_exclude_info_maps": mock_output_manager._exclude_info_maps,
        "filter_variables_pool": mock_output_manager.filter_variables_pool,
        "generate_file_name": mock_output_manager.generate_file_name,
        "_generate_key": mock_output_manager._generate_key,
        "_handle_log_output": mock_output_manager._handle_log_output,
        "set_metadata_prefix": mock_output_manager.set_metadata_prefix,
        "set_log_verbose": mock_output_manager.set_log_verbose,
        "_list_to_file_txt": mock_output_manager._list_to_file_txt,
        "_list_filter_files_in_dir": mock_output_manager._list_filter_files_in_dir,
        "_load_filter_file_content": mock_output_manager._load_filter_file_content,
        "load_variables_pool_from_file": mock_output_manager.load_variables_pool_from_file,
        "save_results": mock_output_manager.save_results,
        "add_variable": mock_output_manager.add_variable,
        "add_error": mock_output_manager.add_error,
        "add_log": mock_output_manager.add_log,
        "add_warning": mock_output_manager.add_warning,
        "dump_logs": mock_output_manager.dump_logs,
        "dump_warnings": mock_output_manager.dump_warnings,
        "dump_errors": mock_output_manager.dump_errors,
        "dump_variable_names_and_contexts": mock_output_manager.dump_variable_names_and_contexts,
        "_route_save_functions": mock_output_manager._route_save_functions,
        "clear_output_dir": mock_output_manager.clear_output_dir,
        "is_file_in_dir": mock_output_manager.is_file_in_dir,
        "create_directory": mock_output_manager.create_directory,
        "_route_logs": mock_output_manager._route_logs,
        "print_credits": mock_output_manager.print_credits,
        "_stringify_units": mock_output_manager._stringify_units,
    }


def test_dump_all_nondata_pools(mocker: MockerFixture) -> None:
    """Test case for function dump_all_nondata_pools in output_manager.py"""

    # Arrange
    output_manager = OutputManager()
    path = "dummy_path"
    patch_for_dump_errors = mocker.patch.object(output_manager, "dump_errors")
    patch_for_dump_warnings = mocker.patch.object(output_manager, "dump_warnings")
    patch_for_dump_logs = mocker.patch.object(output_manager, "dump_logs")
    patch_for_dump_variable_names_and_contexts = mocker.patch.object(output_manager, "dump_variable_names_and_contexts")
    patch_for_report_variables_usage_counts = mocker.patch.object(output_manager, "report_variables_usage_counts")

    # Act
    output_manager.dump_all_nondata_pools(path, False, "verbose")

    # Assert
    patch_for_dump_variable_names_and_contexts.assert_called_once_with(path, False, "verbose")
    patch_for_dump_errors.assert_called_once_with(path)
    patch_for_dump_warnings.assert_called_once_with(path)
    patch_for_dump_logs.assert_called_once_with(path)
    patch_for_report_variables_usage_counts.assert_called_once_with(path)

    # Act
    output_manager.dump_all_nondata_pools(path, True, "verbose")

    # Assert
    assert patch_for_dump_variable_names_and_contexts.call_count == 2
    assert patch_for_dump_errors.call_count == 2
    assert patch_for_dump_warnings.call_count == 2
    assert patch_for_dump_logs.call_count == 2
    assert patch_for_report_variables_usage_counts.call_count == 2

    output_manager.flush_pools()


def test_generate_file_name(mocker: MockerFixture) -> None:
    """Unit test for function generate_file_name in file output_manager.py"""
    timestamp = "18-Jan-2023_Wed_22-38-14"
    base_name = "dummy_name"
    extension = "ext"
    metadata_prefix = "dummy_prefix"
    om = OutputManager()
    om._OutputManager__metadata_prefix = metadata_prefix

    with patch("RUFAS.output_manager.Utility.get_timestamp") as mock_method:
        mock_method.return_value = timestamp
        assert om.generate_file_name(base_name, extension) == f"{metadata_prefix}_{base_name}_{timestamp}.{extension}"


def test_dump_logs(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for function dump_logs in output_manager.py"""
    mock_output_manager.generate_file_name = MagicMock(return_value="dummy_name")
    mock_output_manager.dict_to_file_json = MagicMock()

    mock_output_manager.dump_logs(Path("dummy_path"))

    mock_output_manager.generate_file_name.assert_called_once_with("logs", "json")
    mock_output_manager.dict_to_file_json.assert_called_once_with(
        mock_output_manager.logs_pool, Path("dummy_path", "dummy_name")
    )

    # Restore original methods
    mock_output_manager.generate_file_name = output_manager_original_method_states["generate_file_name"]
    mock_output_manager.dict_to_file_json = output_manager_original_method_states["dict_to_file_json"]


def test_dump_warnings(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for function dump_warnings in output_manager.py"""
    mock_output_manager.generate_file_name = MagicMock(return_value="dummy_name")
    mock_output_manager.dict_to_file_json = MagicMock()

    mock_output_manager.dump_warnings(Path("dummy_path"))

    mock_output_manager.generate_file_name.assert_called_once_with("warnings", "json")
    mock_output_manager.dict_to_file_json.assert_called_once_with(
        mock_output_manager.warnings_pool, Path("dummy_path", "dummy_name")
    )

    # Restore original methods
    mock_output_manager.generate_file_name = output_manager_original_method_states["generate_file_name"]
    mock_output_manager.dict_to_file_json = output_manager_original_method_states["dict_to_file_json"]


def test_dump_errors(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for function dump_errors in output_manager.py"""
    mock_output_manager.generate_file_name = MagicMock(return_value="dummy_name")
    mock_output_manager.dict_to_file_json = MagicMock()

    mock_output_manager.dump_errors(Path("dummy_path"))

    mock_output_manager.generate_file_name.assert_called_once_with("errors", "json")
    mock_output_manager.dict_to_file_json.assert_called_once_with(
        mock_output_manager.errors_pool, Path("dummy_path", "dummy_name")
    )

    # Restore original methods
    mock_output_manager.generate_file_name = output_manager_original_method_states["generate_file_name"]
    mock_output_manager.dict_to_file_json = output_manager_original_method_states["dict_to_file_json"]


def test_report_variables_usage_counts(mocker: MockerFixture) -> None:
    """
    Unit test for report_variables_usage_counts() method in OutputManager class.
    """

    # Arrange
    path = Path("/fake/directory")
    expected_file_name = "variables_usage_counts.csv"
    expected_full_path = Path(path, expected_file_name)
    output_manager = OutputManager()

    patch_for_generate_file_name = mocker.patch.object(
        output_manager, "generate_file_name", return_value=expected_file_name
    )
    patch_for_dict_to_file_json = mocker.patch.object(output_manager, "_dict_to_file_csv")
    data_dict: Dict[str, Dict[str, List[Any]]] = {
        "variable_name": {"values": []},
        "usage_count": {"values": []},
    }

    # Act
    output_manager.report_variables_usage_counts(path)

    # Assert
    patch_for_generate_file_name.assert_called_once_with("variables_usage_counts", "csv")
    patch_for_dict_to_file_json.assert_called_once_with(data_dict, expected_full_path)


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
    mock_output_manager.generate_file_name = MagicMock(return_value="dummy_name")
    mock_output_manager._list_to_file_txt = MagicMock()

    mock_output_manager.dump_variable_names_and_contexts(Path("dummy_path"), exclude_info_maps, format_option)

    mock_output_manager.generate_file_name.assert_called_once_with("variable_names", "txt")
    mock_output_manager._list_to_file_txt.assert_called_once_with(expected_result, Path("dummy_path", "dummy_name"))

    # Restore original methods
    mock_output_manager.generate_file_name = output_manager_original_method_states["generate_file_name"]
    mock_output_manager._list_to_file_txt = output_manager_original_method_states["_list_to_file_txt"]
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
    mock_output_manager.generate_file_name = MagicMock(return_value="dummy_name")
    mock_output_manager._list_to_file_txt = MagicMock()

    mock_output_manager.dump_variable_names_and_contexts(Path("dummy_path"), False, format_option="verbose")

    mock_output_manager.generate_file_name.assert_called_once_with("variable_names", "txt")
    mock_output_manager._list_to_file_txt.assert_called_once_with(expected_output, Path("dummy_path", "dummy_name"))

    # Restore original methods
    mock_output_manager.generate_file_name = output_manager_original_method_states["generate_file_name"]
    mock_output_manager._list_to_file_txt = output_manager_original_method_states["_list_to_file_txt"]
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
    mock_output_manager._list_to_file_txt = output_manager_original_method_states["_list_to_file_txt"]


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
    mock_output_manager._exclude_info_maps = output_manager_original_method_states["_exclude_info_maps"]


@pytest.mark.parametrize(
    "mock_file_text,filter_by_exclusion",
    [
        ("apples\nbananas\ncherries", False),
        ("apples\nbananas\ncherries\n\n\n", False),
        ("apples\nbananas\n\n\n\ncherries", False),
        ("apples\nbananas\n\n\ncherries\n\n\n", False),
        ("exclude\napples\nbananas\ncherries", True),
    ],
)
@patch("builtins.open", new_callable=mock_open)
def test_load_filter_file_content_txt(
    mock_file: MagicMock,
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    mock_file_text: str,
    filter_by_exclusion: bool,
) -> None:
    """Test case for function _load_filter_file_content in output_manager.py"""
    mock_file.return_value.read.return_value = mock_file_text
    result = mock_output_manager._load_filter_file_content(Path("path/to/file.txt"))
    assert result == [{"filters": ["apples", "bananas", "cherries"], "filter_by_exclusion": filter_by_exclusion}]

    # Restore original method
    mock_output_manager._load_filter_file_content = output_manager_original_method_states["_load_filter_file_content"]


@patch("builtins.open", new_callable=mock_open)
def test_load_filter_file_content_json(
    mock_file: MagicMock,
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for function _load_filter_file_content in output_manager.py"""

    data: Dict[str, Any] = {
        "filters": ["filter1", "filter2"],
        "other_key": "value",
    }
    mock_file.return_value.read.return_value = json.dumps(data)
    result = mock_output_manager._load_filter_file_content(Path("some_file.json"))
    assert result == [data]

    # Restore original method
    mock_output_manager._load_filter_file_content = output_manager_original_method_states["_load_filter_file_content"]


@patch("builtins.open", new_callable=mock_open)
def test_load_filter_file_content_json_multiple(
    mock_file: MagicMock,
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for function _load_filter_file_content in output_manager.py"""

    data: Dict[str, Any] = {
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
    result = mock_output_manager._load_filter_file_content(Path("some_file.json"))
    assert result == data["multiple"]

    # Restore original method
    mock_output_manager._load_filter_file_content = output_manager_original_method_states["_load_filter_file_content"]


@patch("builtins.open", new_callable=mock_open)
def test_load_filter_file_content_exception(
    mock_file: MagicMock,
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for function _load_filter_file_content in output_manager.py"""
    with pytest.raises(Exception):
        mock_output_manager._load_filter_file_content(Path("invalid_extention.abc"))

    mock_file.return_value.read.return_value = "this is not valid JSON"
    with pytest.raises(json.JSONDecodeError):
        mock_output_manager._load_filter_file_content(Path("some_file.json"))

    mock_file.side_effect = FileNotFoundError
    with pytest.raises(FileNotFoundError):
        mock_output_manager._load_filter_file_content(Path("non_existent_file.txt"))

    mock_file.side_effect = UnicodeDecodeError("encoding", b"", 1, 2, "Fake decode error")
    with pytest.raises(UnicodeDecodeError):
        mock_output_manager._load_filter_file_content(Path("corrupted_file.txt"))

    mock_file.side_effect = Exception("Unexpected error")
    with pytest.raises(Exception):
        mock_output_manager._load_filter_file_content(Path("some_file.txt"))

    # Restore original method
    mock_output_manager._load_filter_file_content = output_manager_original_method_states["_load_filter_file_content"]


def test_list_filter_files_in_dir(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    tmpdir,
) -> None:
    mock_output_manager.add_warning = MagicMock()
    tmpdir.join("json_file1.txt").write("File 1 content")
    tmpdir.join("csv_file2.json").write("File 2 content")
    tmpdir.join("file3.txt").write("File 3 content")

    filter_files = mock_output_manager._list_filter_files_in_dir(Path(tmpdir))

    assert len(filter_files) == 2
    assert "json_file1.txt" in filter_files
    assert "csv_file2.json" in filter_files
    assert "file3.csv" not in filter_files
    mock_output_manager.add_warning.assert_called_once()

    with pytest.raises(NotADirectoryError):
        mock_output_manager._list_filter_files_in_dir(Path("nonexistent_directory"))

    # Restore original method
    mock_output_manager._list_filter_files_in_dir = output_manager_original_method_states["_list_filter_files_in_dir"]
    mock_output_manager.add_warning = output_manager_original_method_states["add_warning"]


def test_filter_variables_pool_include_empty_filter_pattern_pool(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for empty filter pattern pool with function filter_variables_pool in output_manager.py"""
    mock_output_manager.variables_pool = {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3",
    }
    filter_content = {"filters": []}
    expected_result = {}

    assert mock_output_manager.filter_variables_pool(filter_content) == expected_result

    # Restore original method
    mock_output_manager.filter_variables_pool = output_manager_original_method_states["filter_variables_pool"]
    mock_output_manager.variables_pool = {}


def test_filter_variables_pool_exclude_empty_filter_pattern_pool(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for exclude keyword in empty filter pattern pool with
    function filter_variables_pool in output_manager.py"""
    mock_output_manager.variables_pool = {
        "key1": {"values": "value1"},
        "key2": {"values": "value2"},
        "key3": {"values": "value3"},
    }
    filter_content = {"filters": [], "filter_by_exclusion": True}
    expected_result = {
        "key1": {"values": "value1"},
        "key2": {"values": "value2"},
        "key3": {"values": "value3"},
    }

    assert mock_output_manager.filter_variables_pool(filter_content) == expected_result

    # Restore original method
    mock_output_manager.filter_variables_pool = output_manager_original_method_states["filter_variables_pool"]
    mock_output_manager.variables_pool = {}


def test_filter_variables_pool_with_matching_filters_in_pattern_pool(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for matching pattern pool with function filter_variables_pool in output_manager.py"""
    mock_output_manager.variables_pool = {
        "key1": {"values": "value1"},
        "key2": {"values": "value2"},
        "key3": {"values": "value3"},
    }
    filter_content = {"filters": ["key1", "key2"]}
    expected_result = {"key1": {"values": "value1"}, "key2": {"values": "value2"}}

    assert mock_output_manager.filter_variables_pool(filter_content) == expected_result

    # Restore original method
    mock_output_manager.filter_variables_pool = output_manager_original_method_states["filter_variables_pool"]
    mock_output_manager.variables_pool = {}


def test_filter_variables_pool_exclude_matching_filters_in_pattern_pool(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for exclude keyword in matching pattern pool with
    function filter_variables_pool in output_manager.py"""
    mock_output_manager.variables_pool = {
        "key1": {"values": "value1"},
        "key2": {"values": "value2"},
        "key3": {"values": "value3"},
    }
    filter_content = {"filters": ["key1", "key2"], "filter_by_exclusion": True}
    expected_result = {"key3": {"values": "value3"}}

    assert mock_output_manager.filter_variables_pool(filter_content) == expected_result

    # Restore original method
    mock_output_manager.filter_variables_pool = output_manager_original_method_states["filter_variables_pool"]
    mock_output_manager.variables_pool = {}


def test_filter_variables_pool_non_matching_pattern(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for pattern pool with non-matching pattern with
    function filter_variables_pool in output_manager.py"""
    mock_output_manager.variables_pool = {
        "key1": {"values": "value1"},
        "key2": {"values": "value2"},
        "key3": {"values": "value3"},
    }
    filter_content = {"filters": ["key1", "key4"], "filter_by_exclusion": False}
    expected_result = {"key1": {"values": "value1"}}

    assert mock_output_manager.filter_variables_pool(filter_content) == expected_result

    # Restore original method
    mock_output_manager.filter_variables_pool = output_manager_original_method_states["filter_variables_pool"]
    mock_output_manager.variables_pool = {}


def test_filter_variables_pool_exclude_non_matching_pattern(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for pattern pool with exclude keyword and non-matching pattern with
    function filter_variables_pool in output_manager.py"""
    mock_output_manager.variables_pool = {
        "key1": {"values": "value1"},
        "key2": {"values": "value2"},
        "key3": {"values": "value3"},
    }
    filter_content = {"filters": ["key1", "key4"], "filter_by_exclusion": True}
    expected_result = {"key2": {"values": "value2"}, "key3": {"values": "value3"}}

    assert mock_output_manager.filter_variables_pool(filter_content) == expected_result


def test_filter_variables_pool_duplicate_patterns(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for pattern pool with duplicate patterns with
    function filter_variables_pool in output_manager.py"""
    mock_output_manager.variables_pool = {
        "key1": {"values": "value1"},
        "key2": {"values": "value2"},
        "key3": {"values": "value3"},
    }
    filter_content = {"filters": ["key1", "key1"], "filter_by_exclusion": False}
    expected_result = {"key1": {"values": "value1"}}

    assert mock_output_manager.filter_variables_pool(filter_content) == expected_result

    # Restore original method
    mock_output_manager.filter_variables_pool = output_manager_original_method_states["filter_variables_pool"]
    mock_output_manager.variables_pool = {}


def test_filter_variables_pool_exclude_duplicate_patterns(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test case for pattern pool with duplicate patterns and exclude keyword with
    function filter_variables_pool in output_manager.py"""
    mock_output_manager.variables_pool = {
        "key1": {"values": "value1"},
        "key2": {"values": "value2"},
        "key3": {"values": "value3"},
    }
    filter_content = {"filters": ["key1", "key1"], "filter_by_exclusion": True}
    expected_result = {"key2": {"values": "value2"}, "key3": {"values": "value3"}}

    assert mock_output_manager.filter_variables_pool(filter_content) == expected_result

    # Restore original method
    mock_output_manager.filter_variables_pool = output_manager_original_method_states["filter_variables_pool"]
    mock_output_manager.variables_pool = {}


@pytest.fixture
def mock_variables_pool() -> Dict[str, Dict[str, str]]:
    dummy_variables_pool = {
        "DummyClass1.dummy_fun1.dummy_var1": {"values": "value1"},
        "DummyClass1.dummy_fun1.dummy_var2": {"values": "value2"},  # same class as prev, same fun, different var
        "DummyClass2.dummy_fun2.dummy_var3": {"values": "value3"},  # new class, new fun, new var
        "DummyClass2.dummy_fun3.dummy_var4": {"values": "value4"},  # same class as prev, new fun, new var
        "DummyClass2.dummy_fun4.dummy_var4": {"values": "value5"},  # same class as prev, new fun, same var
        "DummyClass3.dummy_fun4.dummy_var2": {"values": "value6"},  # new class, new fun, same var name as 2nd entry
        "DummyClass4.dummy_fun2.dummy_var5": {"values": "value7"},  # new class, same fun name as 3rd entry, new var
    }
    return dummy_variables_pool


def test_filter_variables_pool_regex_patterns(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    mock_variables_pool: Dict[str, Dict[str, str]],
) -> None:
    """Test case for pattern pool using regex patterns with
    function filter_variables_pool in output_manager.py"""
    mock_output_manager.variables_pool = mock_variables_pool

    # get all Class1 vars
    filter_content = {"filters": ["^DummyClass1.*"], "filter_by_exclusion": False}
    expected_result = {
        "DummyClass1.dummy_fun1.dummy_var1": {"values": "value1"},
        "DummyClass1.dummy_fun1.dummy_var2": {"values": "value2"},
    }

    assert mock_output_manager.filter_variables_pool(filter_content) == expected_result

    # get only vars from fun2s
    filter_content = {"filters": [".*fun2.*"], "filter_by_exclusion": False}
    expected_result = {
        "DummyClass2.dummy_fun2.dummy_var3": {"values": "value3"},
        "DummyClass4.dummy_fun2.dummy_var5": {"values": "value7"},
    }

    assert mock_output_manager.filter_variables_pool(filter_content) == expected_result

    # get Class2 with var4 but not Class2 with var3
    filter_content = {"filters": ["^DummyClass2.*var4$"], "filter_by_exclusion": False}
    expected_result = {
        "DummyClass2.dummy_fun3.dummy_var4": {"values": "value4"},
        "DummyClass2.dummy_fun4.dummy_var4": {"values": "value5"},
    }

    assert mock_output_manager.filter_variables_pool(filter_content) == expected_result

    # get all var2s and var4s
    filter_content = {"filters": [".*var2$", ".*var4$"], "filter_by_exclusion": False}
    expected_result = {
        "DummyClass1.dummy_fun1.dummy_var2": {"values": "value2"},
        "DummyClass2.dummy_fun3.dummy_var4": {"values": "value4"},
        "DummyClass2.dummy_fun4.dummy_var4": {"values": "value5"},
        "DummyClass3.dummy_fun4.dummy_var2": {"values": "value6"},
    }

    assert mock_output_manager.filter_variables_pool(filter_content) == expected_result

    # Restore original method
    mock_output_manager.filter_variables_pool = output_manager_original_method_states["filter_variables_pool"]
    mock_output_manager.variables_pool = {}


def test_filter_variables_pool_exclude_regex_patterns(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    mock_variables_pool: Dict[str, str],
) -> None:
    """Test case for pattern pool with regex patterns and exclude keyword with
    function filter_variables_pool in output_manager.py"""
    mock_output_manager.variables_pool = mock_variables_pool

    # get everything except Class1 vars
    filter_content = {"filters": ["^DummyClass1.*"], "filter_by_exclusion": True}
    expected_result = {
        "DummyClass2.dummy_fun2.dummy_var3": {"values": "value3"},
        "DummyClass2.dummy_fun3.dummy_var4": {"values": "value4"},
        "DummyClass2.dummy_fun4.dummy_var4": {"values": "value5"},
        "DummyClass3.dummy_fun4.dummy_var2": {"values": "value6"},
        "DummyClass4.dummy_fun2.dummy_var5": {"values": "value7"},
    }

    assert mock_output_manager.filter_variables_pool(filter_content) == expected_result

    # get everything except vars from fun2s
    filter_content = {"filters": ["exclude", ".*fun2.*"], "filter_by_exclusion": True}
    expected_result = {
        "DummyClass1.dummy_fun1.dummy_var1": {"values": "value1"},
        "DummyClass1.dummy_fun1.dummy_var2": {"values": "value2"},
        "DummyClass2.dummy_fun3.dummy_var4": {"values": "value4"},
        "DummyClass2.dummy_fun4.dummy_var4": {"values": "value5"},
        "DummyClass3.dummy_fun4.dummy_var2": {"values": "value6"},
    }

    assert mock_output_manager.filter_variables_pool(filter_content) == expected_result

    # get everything without Class2 with var4
    filter_content = {"filters": ["^DummyClass2.*var4$"], "filter_by_exclusion": True}
    expected_result = {
        "DummyClass1.dummy_fun1.dummy_var1": {"values": "value1"},
        "DummyClass1.dummy_fun1.dummy_var2": {"values": "value2"},
        "DummyClass2.dummy_fun2.dummy_var3": {"values": "value3"},
        "DummyClass3.dummy_fun4.dummy_var2": {"values": "value6"},
        "DummyClass4.dummy_fun2.dummy_var5": {"values": "value7"},
    }

    assert mock_output_manager.filter_variables_pool(filter_content) == expected_result

    # get everything that doesn't have var2s and var4s
    filter_content = {"filters": [".*var2$", ".*var4$"], "filter_by_exclusion": True}
    expected_result = {
        "DummyClass1.dummy_fun1.dummy_var1": {"values": "value1"},
        "DummyClass2.dummy_fun2.dummy_var3": {"values": "value3"},
        "DummyClass4.dummy_fun2.dummy_var5": {"values": "value7"},
    }

    assert mock_output_manager.filter_variables_pool(filter_content) == expected_result

    # Restore original method
    mock_output_manager.filter_variables_pool = output_manager_original_method_states["filter_variables_pool"]
    mock_output_manager.variables_pool = {}


@pytest.fixture
def mock_variables_pool_complex() -> Dict[str, OutputManager.pool_element_type]:
    dummy_variables_pool: Dict[str, OutputManager.pool_element_type] = {
        "DummyClass1.dummy_fun1.dummy_var1": {"values": ["value1", "value2", "value3"]},
        "DummyClass1.dummy_fun1.dummy_var2": {
            "values": [{"a": "A", "b": 1.0, "c": True}, {"a": "AA", "b": 2.0, "c": True}]
        },
        "DummyClass1.dummy_fun2.dummy_var3": {"values": [{"a": "AAA", "b": 3.0, "c": False}]},
        "DummyClass2.dummy_fun3.dummy_var4": {"values": "value4"},
    }
    return dummy_variables_pool


def test_filter_variables_pool_complex(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    mock_variables_pool_complex: Dict[str, str],
) -> None:
    """Test case for pattern pool with regex patterns and exclude keyword with
    function filter_variables_pool in output_manager.py"""
    mock_output_manager.variables_pool = mock_variables_pool_complex

    # use filter_name
    filter_content: Dict[str, Any] = {
        "name": "test_case_1",
        "filters": ["^DummyClass1.*"],
        "filter_by_exclusion": False,
        "use_name": True,
        "variables": ["var2", "a"],
    }
    expected_result: Dict[str, OutputManager.pool_element_type] = {
        "test_case_1_0": {"values": ["value1", "value2", "value3"]},
        "test_case_1_1.a": {"values": ["A", "AA"]},
        "test_case_1_2.a": {"values": ["AAA"]},
    }

    assert mock_output_manager.filter_variables_pool(filter_content) == expected_result

    # unpacking pool error
    filter_content: Dict[str, Any] = {"filters": ["^DummyClass1.*"], "filter_by_exclusion": False, "variables": "a"}
    expected_result: Dict[str, OutputManager.pool_element_type] = {
        "DummyClass1.dummy_fun1.dummy_var1": {"values": ["value1", "value2", "value3"]},
        "a": {"values": ["A", "AA", "AAA"]},
    }
    mock_output_manager.add_error = MagicMock()
    with freeze_time("2023-12-12 13:34:42"):
        actual: Dict[str, OutputManager.pool_element_type] = mock_output_manager.filter_variables_pool(filter_content)
    mock_output_manager.add_error.assert_has_calls(
        [
            call(
                "Unpacking Pool Error",
                "Unable to unpack key='DummyClass1.dummy_fun1.dummy_var2' in the data pool, "
                "need a valid `variables` entry for this entry.is_data_in_dict=True, selected_variables='a'",
                {
                    "class": "OutputManager",
                    "function": "filter_variables_pool",
                    "filter_name": "NO NAME FOUND",
                    "filter_by_exclusion": False,
                    "use_filter_name": False,
                    "timestamp": "12-Dec-2023_Tue_13-34-42.000000",
                },
            ),
            call(
                "Unpacking Pool Error",
                "Unable to unpack key='DummyClass1.dummy_fun2.dummy_var3' in the data pool, "
                "need a valid `variables` entry for this entry.is_data_in_dict=True, selected_variables='a'",
                {
                    "class": "OutputManager",
                    "function": "filter_variables_pool",
                    "filter_name": "NO NAME FOUND",
                    "filter_by_exclusion": False,
                    "use_filter_name": False,
                    "timestamp": "12-Dec-2023_Tue_13-34-42.000000",
                },
            ),
        ]
    )
    assert actual == expected_result

    # use_filter_name in dict data
    filter_content: Dict[str, Any] = {
        "name": "test_case_3",
        "filters": ["^DummyClass1.*"],
        "filter_by_exclusion": False,
        "use_name": False,
        "variables": ["a", "b", "c"],
    }
    expected_result: Dict[str, OutputManager.pool_element_type] = {
        "DummyClass1.dummy_fun1.dummy_var1": {"values": ["value1", "value2", "value3"]},
        "a": {"values": ["A", "AA", "AAA"]},
        "b": {"values": [1.0, 2.0, 3.0]},
        "c": {"values": [True, True, False]},
    }

    assert mock_output_manager.filter_variables_pool(filter_content) == expected_result

    # Restore original method
    mock_output_manager.filter_variables_pool = output_manager_original_method_states["filter_variables_pool"]
    mock_output_manager.add_error = output_manager_original_method_states["add_error"]
    mock_output_manager.variables_pool = {}


@pytest.mark.parametrize(
    "exclude_info_maps, produce_graphics, filter_content, is_faulty, chunkification",
    [
        (True, True, [{"filters": ".*", "title": "dummy_title"}], False, False),
        (True, False, [{"filters": ".*", "title": "dummy_title"}], False, False),
        (False, True, [{"filters": ".*", "title": "dummy_title"}], False, False),
        (False, False, [{"filters": ".*", "title": "dummy_title"}], False, False),
        (True, True, [{"no_filters": ".*", "title": "dummy_title"}], True, False),
        (True, True, [{"filters": ".*", "title": "dummy_title"}], False, True),
        (True, False, [{"filters": ".*", "title": "dummy_title"}], False, True),
        (False, True, [{"filters": ".*", "title": "dummy_title"}], False, True),
        (False, False, [{"filters": ".*", "title": "dummy_title"}], False, True),
        (True, True, [{"no_filters": ".*", "title": "dummy_title"}], True, True),
    ],
)
def test_save_results(
    mocker: MockerFixture,
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    exclude_info_maps: bool,
    produce_graphics: bool,
    filter_content: List[Dict[str, str]],
    is_faulty: bool,
    chunkification: bool,
) -> None:
    # Arrange
    filters_path = Path("filters_path")
    csvs_dir = Path("output/CSVs/")
    jsons_dir = Path("output/JSONs/")
    reports_dir = Path("output/reports/")
    graphics_dir = Path("outputs/graphics_dir")
    mock_output_manager.variables_pool = {}
    mocker.patch.object(mock_output_manager, "generate_file_name", return_value="dummy_name")
    mocker.patch.object(mock_output_manager, "_load_filter_file_content", return_value=filter_content)
    filter_files = ["csv_input_filepath1.txt", "graph_input_filepath2.txt", "json_input_filepath3.txt"]
    mocker.patch.object(mock_output_manager, "_list_filter_files_in_dir", return_value=filter_files)
    mock_output_manager._exclude_info_maps = MagicMock(return_value={})
    route_save_functions = mocker.patch.object(mock_output_manager, "_route_save_functions")
    add_error = mocker.patch.object(mock_output_manager, "add_error")
    mock_output_manager.time = MagicMock()
    mock_output_manager.chunkification = chunkification
    mock_output_manager._save_current_variable_pool = MagicMock()
    mock_output_manager._sort_saved_chunk_files = MagicMock()
    mock_output_manager.filter_saved_pools = MagicMock(return_value={})

    # Act
    mock_output_manager.save_results(
        filters_path, exclude_info_maps, produce_graphics, reports_dir, graphics_dir, csvs_dir, jsons_dir
    )

    # Assert
    if is_faulty:
        mock_output_manager._exclude_info_maps.assert_not_called()
        route_save_functions.assert_not_called()
        assert add_error.call_count == len(filter_files)
    else:
        add_error.assert_not_called()
        if exclude_info_maps:
            mock_output_manager._exclude_info_maps.assert_has_calls([call({}), call({}), call({})])
        else:
            mock_output_manager._exclude_info_maps.assert_not_called()
        route_save_functions.assert_has_calls(
            [
                call(
                    file_name,
                    {},
                    produce_graphics,
                    {"filters": ".*", "title": "dummy_title"},
                    jsons_dir,
                    graphics_dir,
                    csvs_dir,
                )
                for file_name in filter_files
            ]
        )
        if chunkification:
            mock_output_manager._save_current_variable_pool.assert_called_once()
            mock_output_manager._sort_saved_chunk_files.assert_called()
            mock_output_manager.filter_saved_pools.assert_called()

    mock_output_manager._exclude_info_maps = output_manager_original_method_states["_exclude_info_maps"]


@pytest.mark.parametrize(
    "exclude_info_maps, produce_graphics, filter_content, is_faulty",
    [
        (True, True, [{"filters": ".*", "title": "dummy_title"}], False),
        (True, False, [{"filters": ".*", "title": "dummy_title"}], False),
        (False, True, [{"filters": ".*", "title": "dummy_title"}], False),
        (False, False, [{"filters": ".*", "title": "dummy_title"}], False),
        (True, True, [{"no_filters": ".*", "title": "dummy_title"}], True),
        (True, True, [{"filters": ".*", "title": "dummy_title", "graph_details": {"type": "plot"}}], False),
    ],
)
def test_save_results_report_generation(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    exclude_info_maps: bool,
    produce_graphics: bool,
    filter_content: List[Dict[str, str]],
    is_faulty: bool,
    mocker: MockerFixture,
) -> None:
    # Arrange
    filters_path = Path("filters_path")
    csvs_dir = Path("output/CSVs/")
    jsons_dir = Path("output/JSONs/")
    reports_dir = Path("output/reports/")
    graphics_dir = Path("outputs/graphics_dir")
    mock_output_manager.variables_pool = {}
    mocker.patch.object(mock_output_manager, "generate_file_name", return_value="dummy_name")
    mocker.patch.object(mock_output_manager, "_load_filter_file_content", return_value=filter_content)
    mock_output_manager._list_filter_files_in_dir = MagicMock(
        return_value=[
            "report_input_filepath1.txt",
            "report_input_filepath2.txt",
        ]
    )
    mock_output_manager._exclude_info_maps = MagicMock(return_value={})
    mock_output_manager._dict_to_file_csv = MagicMock()
    mock_output_manager.add_error = MagicMock()
    mocker.patch.object(mock_output_manager, "_route_logs", return_value=None)
    mock_output_manager._OutputManager__metadata_prefix = "test_prefix"
    mock_output_manager.create_directory = MagicMock()

    with patch("RUFAS.output_manager.ReportGenerator") as mock_report_generator_class:
        mock_report_generator = mock_report_generator_class.return_value
        mock_report_generator.generate_report = MagicMock()

        # Act
        mock_output_manager.save_results(
            filters_path, exclude_info_maps, produce_graphics, reports_dir, graphics_dir, csvs_dir, jsons_dir
        )

        # Assert
        assert mock_output_manager.add_error.call_count == is_faulty * len(
            mock_output_manager._list_filter_files_in_dir.return_value
        )
        if not is_faulty:
            mock_output_manager.add_error.assert_not_called()
            assert mock_output_manager._dict_to_file_csv.call_count == len(
                mock_output_manager._list_filter_files_in_dir.return_value
            )

        if not is_faulty and any("graph_details" in content for content in filter_content):
            for content in filter_content:
                if "graph_details" in content:
                    assert "graphics_dir" in content["graph_details"]
                    assert content["graph_details"]["graphics_dir"] == graphics_dir
                    assert content["graph_details"]["metadata_prefix"] == "test_prefix"

    # Restore original method states
    mock_output_manager.save_results = output_manager_original_method_states["save_results"]
    mock_output_manager._list_filter_files_in_dir = output_manager_original_method_states["_list_filter_files_in_dir"]
    mock_output_manager._exclude_info_maps = output_manager_original_method_states["_exclude_info_maps"]
    mock_output_manager._dict_to_file_csv = output_manager_original_method_states["_dict_to_file_csv"]
    mock_output_manager.add_error = output_manager_original_method_states["add_error"]
    mock_output_manager.create_directory = output_manager_original_method_states["create_directory"]


def test_route_save_functions_csv(
    mocker: MockerFixture,
    mock_output_manager: OutputManager,
) -> None:
    dict_to_file_csv = mocker.patch.object(mock_output_manager, "_dict_to_file_csv")

    mock_output_manager._route_save_functions(
        "csv_file",
        {"key": {"var": "value"}},
        True,
        {"filters": "regex"},
        Path("json_dir"),
        Path("graphics_dir"),
        Path("output/CSVs/"),
    )

    variable_csv_file_path = mock_output_manager.generate_file_name("saved_variables_csv_file", "csv")
    dict_to_file_csv.assert_called_once_with({"key": {"var": "value"}}, Path("output", "CSVs", variable_csv_file_path))


def test_route_save_functions_json(mocker: MockerFixture) -> None:
    # Arrange
    output_manager = OutputManager()
    patch_create_directory = mocker.patch.object(output_manager, "create_directory")
    patch_for_save_to_json = mocker.patch.object(output_manager, "_save_to_json")
    filter_file = "json_file"
    jsons_dir = Path("json_dir")
    filtered_pool = {"key": {"var": "value"}}
    produce_graphics = True
    filter_content = {"filters": "regex"}
    graphics_dir = Path("graphics_dir")
    csvs_dir = Path("csvs_dir")

    # Act
    output_manager._route_save_functions(
        filter_file, filtered_pool, produce_graphics, filter_content, jsons_dir, graphics_dir, csvs_dir
    )

    # Assert
    patch_create_directory.assert_called_once_with(jsons_dir)
    patch_for_save_to_json.assert_called_once_with(filter_file, jsons_dir, filtered_pool, filter_content)


@pytest.mark.parametrize(
    "filter_content, filter_file_extension, expected_filename",
    [
        # Name provided without .json
        ({"name": "test_name"}, ".json", "saved_variables_test_name.json"),
        # No name provided, but filter_file ends with .json
        (
            {},
            ".json",
            "saved_variables_filter_file_with_millis.json",
        ),
        # No name, filter_file does not end with .json
        ({}, ".txt", "saved_variables_filter_file.json"),
    ],
)
def test_save_to_json(
    mocker: MockerFixture,
    tmp_path: Path,
    filter_content: Dict[str, Union[str, int]],
    filter_file_extension: str,
    expected_filename: str,
) -> None:
    """
    Unit test for the _save_to_json() method in the OutputManager class.
    """

    # Arrange
    output_manager = OutputManager()
    patch_for_generate_file_name = mocker.patch.object(
        output_manager, "generate_file_name", return_value=expected_filename
    )
    patch_for_dict_to_file_json = mocker.patch.object(output_manager, "dict_to_file_json")
    filter_file = f"filter_file{filter_file_extension}"
    save_path = tmp_path  # Using pytest's tmp_path fixture
    filtered_pool = {"key": "value"}

    # Act
    output_manager._save_to_json(filter_file, save_path, filtered_pool, filter_content)

    # Assert
    base_name = (
        f"saved_variables_{filter_content['name']}" if "name" in filter_content else f"saved_variables_{filter_file}"
    )
    patch_for_generate_file_name.assert_called_once_with(base_name, "json")
    patch_for_dict_to_file_json.assert_called_once_with(filtered_pool, save_path / expected_filename)


def test_route_save_functions_graph(
    mocker: MockerFixture,
    mock_output_manager: OutputManager,
) -> None:
    mock_generate_graph = mocker.patch("RUFAS.graph_generator.GraphGenerator.generate_graph")
    dummy_log = ["dummy_log"]
    mock_generate_graph.return_value = dummy_log
    mock_create_directory = mocker.patch.object(mock_output_manager, "create_directory")
    add_warning = mocker.patch.object(mock_output_manager, "add_warning")
    add_error = mocker.patch.object(mock_output_manager, "add_error")
    mocker.patch.object(mock_output_manager, "_route_logs", return_value=True)
    graph_data = {"filters": ".*", "other keys": "other values"}

    mock_output_manager._route_save_functions(
        "graph_file",
        {"key": [1, 2, 3, 4]},
        False,
        graph_data,
        Path("jsons_dir"),
        Path("graphics_dir"),
        Path("csvs_dir"),
    )

    mock_generate_graph.assert_not_called()
    mock_create_directory.assert_called_with(Path("graphics_dir"))
    add_warning.assert_called_once_with(
        "No Graphics",
        "Graphic generation is disabled, skipping filter_file='graph_file'",
        {"class": "OutputManager", "function": "_route_save_functions"},
    )

    mock_output_manager._route_save_functions(
        "graph_file", {"key": [1, 2, 3, 4]}, True, graph_data, Path("jsons_dir"), Path("graphics_dir"), Path("csvs_dir")
    )
    add_warning.assert_called_once_with(
        "No Graphics",
        "Graphic generation is disabled, skipping filter_file='graph_file'",
        {"class": "OutputManager", "function": "_route_save_functions"},
    )

    mock_generate_graph.assert_called_once_with(
        {"key": [1, 2, 3, 4]}, graph_data, "graph_file", Path("graphics_dir"), True
    )

    mock_generate_graph.side_effect = Exception("test exception")
    mock_output_manager._route_save_functions(
        "graph_file", {"key": [1, 2, 3, 4]}, True, graph_data, Path("jsons_dir"), Path("graphics_dir"), Path("csvs_dir")
    )
    add_error.assert_called_with(
        "graph generation exception",
        "test exception",
        {"class": "OutputManager", "function": "_route_save_functions"},
    )


@pytest.mark.parametrize(
    "log_pool, expected_calls",
    [
        (
            [
                {
                    "log": "info_log",
                    "message": "Info message",
                    "info_map": {"class": "GraphGenerator", "function": "prepare_plot_data"},
                },
                {
                    "warning": "warning_type",
                    "message": "Warning message",
                    "info_map": {"class": "GraphGenerator", "function": "prepare_plot_data"},
                },
            ],
            {"add_error": 0, "add_log": 1, "add_warning": 1},
        ),
        (
            [
                {
                    "error": "error_type",
                    "message": "Error message",
                    "info_map": {"class": "GraphGenerator", "function": "prepare_plot_data"},
                },
                {
                    "log": "info_log",
                    "message": "Info message",
                    "info_map": {"class": "GraphGenerator", "function": "prepare_plot_data"},
                },
            ],
            {"add_error": 1, "add_log": 1, "add_warning": 0},
        ),
    ],
)
def test_route_logs(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
    log_pool,
    expected_calls,
):
    mock_output_manager.add_error = MagicMock()
    mock_output_manager.add_log = MagicMock()
    mock_output_manager.add_warning = MagicMock()

    mock_output_manager._route_logs(log_pool)

    assert mock_output_manager.add_error.call_count == expected_calls["add_error"]
    assert mock_output_manager.add_log.call_count == expected_calls["add_log"]
    assert mock_output_manager.add_warning.call_count == expected_calls["add_warning"]

    mock_output_manager.add_log = output_manager_original_method_states["add_log"]
    mock_output_manager.add_warning = output_manager_original_method_states["add_warning"]
    mock_output_manager.add_error = output_manager_original_method_states["add_error"]
    mock_output_manager._route_logs = output_manager_original_method_states["_route_logs"]


def test_load_variables_pool_from_file_valid_path(
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Checks that load_variables_pool_from_file loads the valid filepath provided to the OM variables pool"""
    dummy_data = {
        "vars": {
            "var1": {"values": [1, 2, 3], "info_map": {"imvar1": 1, "imvar2": 2}},
            "var2": {"values": {"a": 1, "b": 2}, "info_map": {}},
        }
    }
    with patch("builtins.open", mock_open(read_data=json.dumps(dummy_data))):
        mock_output_manager.load_variables_pool_from_file(Path("path/to/file"))
        assert mock_output_manager.variables_pool == dummy_data

    mock_output_manager.load_variables_pool_from_file = output_manager_original_method_states[
        "load_variables_pool_from_file"
    ]


@patch("builtins.open", new_callable=mock_open)
def test_load_variables_pool_from_file_raises_exception(
    mock_file: MagicMock,
    mock_output_manager: OutputManager,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Checks that load_variables_pool_from_file raises exceptions with a bad filepath provided"""
    mock_file.side_effect = FileNotFoundError
    with pytest.raises(FileNotFoundError):
        mock_output_manager.load_variables_pool_from_file(Path("bad/file/path"))
        assert mock_output_manager.variables_pool == {}

    mock_file.return_value.read.return_value = "this is not valid JSON"
    with patch("builtins.open", mock_open(read_data="bad/file/path")):
        with pytest.raises(json.JSONDecodeError):
            mock_output_manager.load_variables_pool_from_file(Path("bad/file/path.json"))
            assert mock_output_manager.variables_pool == {}

    mock_output_manager.load_variables_pool_from_file = output_manager_original_method_states[
        "load_variables_pool_from_file"
    ]


@pytest.mark.parametrize(
    "is_file_found_in_dir",
    [True, False],
)
def test_clear_output_dir(
    mocker: MockerFixture,
    mock_output_manager: OutputManager,
    is_file_found_in_dir: bool,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Checks clear_output_dir function in output_manager.py"""
    patch_empty_dir = mocker.patch("RUFAS.util.Utility.empty_dir")
    mock_output_manager.add_log = MagicMock()
    mock_output_manager.add_error = MagicMock()
    mock_output_manager.is_file_in_dir = MagicMock(return_value=is_file_found_in_dir)
    with patch("pathlib.Path.mkdir") as mock_mkdir:
        vars_file_path = mock_mkdir.return_value / "dummy_vars_file.txt"
        mock_output_manager.clear_output_dir(vars_file_path, Path("output_dir"))
        if is_file_found_in_dir:
            patch_empty_dir.assert_not_called()
            assert mock_output_manager.add_log.call_count == 0
            assert mock_output_manager.add_error.call_count == 1
        else:
            patch_empty_dir.assert_called_once()
            assert mock_output_manager.add_log.call_count == 1
            assert mock_output_manager.add_error.call_count == 0

    mock_output_manager.is_file_in_dir = output_manager_original_method_states["is_file_in_dir"]
    mock_output_manager.clear_output_dir = output_manager_original_method_states["clear_output_dir"]
    mock_output_manager.add_log = output_manager_original_method_states["add_log"]
    mock_output_manager.add_error = output_manager_original_method_states["add_error"]


@pytest.mark.parametrize(
    "dir_path, file_path, expected_result",
    [
        (None, None, False),
        (Path("path/to/directory"), Path("path/to/directory/file.json"), True),
        (Path("path/to/directory"), Path("path/to/different_directory/file.json"), False),
        (Path("path/to/directory"), Path("path/to/directory/subdirectory/file.json"), True),
        (Path("path/to/directory"), None, False),
    ],
)
def test_is_file_in_dir(
    mock_output_manager: OutputManager,
    dir_path: Path,
    file_path: Path,
    expected_result: bool,
    output_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Checks is_file_in_dir function in output_manager.py"""
    assert mock_output_manager.is_file_in_dir(dir_path, file_path) is expected_result

    mock_output_manager.is_file_in_dir = output_manager_original_method_states["is_file_in_dir"]


def test_create_directory_successful(
    mock_output_manager: OutputManager, output_manager_original_method_states: Dict[str, Callable]
) -> None:
    """Checks create_directory function successfully creates a dir in output_manager.py"""
    mock_output_manager.add_log = MagicMock()
    mock_output_manager.add_error = MagicMock()
    with patch.object(Path, "mkdir") as mock_mkdir:
        test_path = Path("/test/directory")
        mock_output_manager.create_directory(test_path)
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    assert mock_output_manager.add_log.call_count == 2
    assert mock_output_manager.add_error.call_count == 0

    mock_output_manager.create_directory = output_manager_original_method_states["create_directory"]
    mock_output_manager.add_log = output_manager_original_method_states["add_log"]
    mock_output_manager.add_error = output_manager_original_method_states["add_error"]


def test_create_directory_exceptions(
    mock_output_manager: OutputManager, output_manager_original_method_states: Dict[str, Callable]
) -> None:
    """Checks create_directory function has proper exceptions"""
    mock_output_manager.add_log = MagicMock()
    mock_output_manager.add_error = MagicMock()
    with patch("pathlib.Path.mkdir", side_effect=PermissionError):
        mock_output_manager.create_directory(Path("unauthorized/path/"))

    assert mock_output_manager.add_log.call_count == 1
    assert mock_output_manager.add_error.call_count == 1

    mock_output_manager.add_log = MagicMock()
    mock_output_manager.add_error = MagicMock()
    with patch("pathlib.Path.mkdir", side_effect=Exception):
        mock_output_manager.create_directory(Path("unauthorized/path/"))

    assert mock_output_manager.add_log.call_count == 1
    assert mock_output_manager.add_error.call_count == 1

    mock_output_manager.create_directory = output_manager_original_method_states["create_directory"]
    mock_output_manager.add_log = output_manager_original_method_states["add_log"]
    mock_output_manager.add_error = output_manager_original_method_states["add_error"]


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
def test_log_verbosity_less_than_method(self: LogVerbosity, other: LogVerbosity, expected_result: bool) -> None:
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


@pytest.mark.parametrize(
    "errors_pool, warnings_pool, logs_pool, expected",
    [
        ({}, {}, {}, (0, 0, 0)),
        ({"key1": {"values": [1, 2, 3]}}, {}, {}, (3, 0, 0)),
        ({}, {"key1": {"values": [1, 2]}}, {}, (0, 2, 0)),
        ({}, {}, {"key1": {"values": [1, 2, 3, 4]}}, (0, 0, 4)),
        ({"key1": {"values": [1]}, "key2": {"values": [2, 3]}}, {"key1": {"values": [1, 2, 3, 4]}}, {}, (3, 4, 0)),
        (
            {"key1": {"values": [1]}, "key2": {"values": [2, 3]}},
            {"key1": {"values": [1, 2, 3, 4]}},
            {"key1": {"values": [1, 2, 3]}},
            (3, 4, 3),
        ),
    ],
)
def test_get_error_and_warning_counts(
    mocker: MockerFixture,
    errors_pool: dict[str, dict[str, list]],
    warnings_pool: dict[str, dict[str, list]],
    logs_pool: dict[str, dict[str, list]],
    expected: tuple[int, int],
) -> None:
    """
    Unit test for the _get_errors_warnings_logs_counts() method in OutputManager class.
    """

    # Arrange
    om = OutputManager()
    mocker.patch.object(om, "errors_pool", errors_pool)
    mocker.patch.object(om, "warnings_pool", warnings_pool)
    mocker.patch.object(om, "logs_pool", logs_pool)

    # Act and Assert
    assert om._get_errors_warnings_logs_counts() == expected


@pytest.mark.parametrize(
    "log_verbose, expected_output",
    [
        (LogVerbosity.NONE, ""),
        (
            LogVerbosity.CREDITS,
            f"RuFaS: Ruminant Farm Systems Model. Version: v\n{DISCLAIMER_MESSAGE}\nStarting task: id\n",
        ),
        (
            LogVerbosity.ERRORS,
            f"RuFaS: Ruminant Farm Systems Model. Version: v\n{DISCLAIMER_MESSAGE}\nStarting task: id\n",
        ),
        (
            LogVerbosity.WARNINGS,
            f"RuFaS: Ruminant Farm Systems Model. Version: v\n{DISCLAIMER_MESSAGE}\nStarting task: id\n",
        ),
        (
            LogVerbosity.LOGS,
            f"RuFaS: Ruminant Farm Systems Model. Version: v\n{DISCLAIMER_MESSAGE}\nStarting task: id\n",
        ),
    ],
)
def test_print_credits(
    mock_output_manager: OutputManager, log_verbose: LogVerbosity, expected_output: str, capfd
) -> None:
    """
    Unit test for the print_credits() method in OutputManager class.
    """
    mock_output_manager._OutputManager__log_verbose = log_verbose
    task_id = "id"
    version = "v"
    mock_output_manager.print_credits(version, task_id)

    captured = capfd.readouterr()
    assert captured.out == expected_output


@pytest.mark.parametrize(
    "log_verbose, expected_output",
    [
        (LogVerbosity.NONE, ""),
        (LogVerbosity.CREDITS, "Finished task: id with 2 error(s), 1 warning(s), and 5 log(s).\n"),
        (LogVerbosity.ERRORS, "Finished task: id with 2 error(s), 1 warning(s), and 5 log(s).\n"),
        (LogVerbosity.WARNINGS, "Finished task: id with 2 error(s), 1 warning(s), and 5 log(s).\n"),
        (LogVerbosity.LOGS, "Finished task: id with 2 error(s), 1 warning(s), and 5 log(s).\n"),
    ],
)
def test_print_errors_warnings_logs(
    mock_output_manager: OutputManager, log_verbose: LogVerbosity, expected_output: str, capfd
):
    mock_output_manager._OutputManager__log_verbose = log_verbose
    task_id = "id"
    with patch.object(OutputManager, "_get_errors_warnings_logs_counts", return_value=(2, 1, 5)):
        mock_output_manager.print_errors_warnings_logs_counts(task_id)
        captured = capfd.readouterr()
        assert captured.out == expected_output


@pytest.mark.parametrize(
    "input_data, detailed_values_flag, expected",
    [
        # Basic test case with a single data_origin per value
        (
            {
                "ModuleA.variable_x": {
                    "info_maps": [
                        {"data_origin": [["SourceClassA", "method_a"]], "units": MeasurementUnits.UNITLESS.value},
                        {"data_origin": [["SourceClassA", "method_a"]], "units": MeasurementUnits.UNITLESS.value},
                    ],
                    "values": [10, 20],
                }
            },
            True,  # detailed_values_flag
            {
                "ModuleA.variable_x": {
                    "info_maps": [
                        {"data_origin": [["SourceClassA", "method_a"]], "units": MeasurementUnits.UNITLESS.value},
                        {"data_origin": [["SourceClassA", "method_a"]], "units": MeasurementUnits.UNITLESS.value},
                    ],
                    "values": [10, 20],
                    "detailed_values": [
                        [("[SourceClassA.method_a]->[ModuleA.variable_x]", 10)],
                        [("[SourceClassA.method_a]->[ModuleA.variable_x]", 20)],
                    ],
                }
            },
        ),
        # Test case with multiple data_origin entries for a single value
        (
            {
                "ModuleB.variable_y": {
                    "info_maps": [
                        {
                            "data_origin": [["SourceClassB", "method_b"], ["SourceClassC", "method_c"]],
                            "units": MeasurementUnits.MILLIMETERS.value,
                        },
                        {"data_origin": [["SourceClassB", "method_b"]], "units": MeasurementUnits.MILLIMETERS.value},
                    ],
                    "values": [30, 40],
                }
            },
            True,  # detailed_values_flag
            {
                "ModuleB.variable_y": {
                    "info_maps": [
                        {
                            "data_origin": [["SourceClassB", "method_b"], ["SourceClassC", "method_c"]],
                            "units": MeasurementUnits.MILLIMETERS.value,
                        },
                        {"data_origin": [["SourceClassB", "method_b"]], "units": MeasurementUnits.MILLIMETERS.value},
                    ],
                    "values": [30, 40],
                    "detailed_values": [
                        [
                            ("[SourceClassB.method_b]->[ModuleB.variable_y]", 30),
                            ("[SourceClassC.method_c]->[ModuleB.variable_y]", 30),
                        ],
                        [("[SourceClassB.method_b]->[ModuleB.variable_y]", 40)],
                    ],
                }
            },
        ),
        # Missing both keys
        (
            {
                "ModuleD.missing_both": {
                    "other_key": "some_value",
                }
            },
            True,  # detailed_values_flag
            {
                "ModuleD.missing_both": {
                    "other_key": "some_value",
                }
            },
        ),
        # Missing `info_maps` key
        (
            {
                "ModuleE.missing_info_maps": {
                    "values": [50, 60],
                }
            },
            True,  # detailed_values_flag
            {
                "ModuleE.missing_info_maps": {
                    "values": [50, 60],
                }
            },
        ),
        # Missing `values` key
        (
            {
                "ModuleF.missing_values": {
                    "info_maps": [{"data_origin": [["ClassX", "method_x"]]}],
                }
            },
            True,  # detailed_values_flag
            {
                "ModuleF.missing_values": {
                    "info_maps": [{"data_origin": [["ClassX", "method_x"]]}],
                }
            },
        ),
        # _detailed_values_flag set to False
        (
            {
                "ModuleG.variable_z": {
                    "info_maps": [{"data_origin": [["SourceClassG", "method_g"]], "units": "units_g"}],
                    "values": [70],
                }
            },
            False,  # detailed_values_flag
            {
                "ModuleG.variable_z": {
                    "info_maps": [{"data_origin": [["SourceClassG", "method_g"]], "units": "units_g"}],
                    "values": [70],
                }
            },
        ),
        (
            {
                "ModuleK.no_data_origin": {
                    "info_maps": [
                        {"units": "units_k"},  # Missing data_origin
                        {"data_origin": [["ClassW", "method_w"]], "units": "units_w"},
                    ],
                    "values": [110, 120],
                }
            },
            True,  # detailed_values_flag
            {
                "ModuleK.no_data_origin": {
                    "info_maps": [
                        {"units": "units_k"},
                        {"data_origin": [["ClassW", "method_w"]], "units": "units_w"},
                    ],
                    "values": [110, 120],
                }
            },
        ),
    ],
)
def test_add_detailed_values(
    input_data: Dict[str, Any], detailed_values_flag: bool, expected: Dict[str, Any], mocker: MockerFixture
) -> None:
    """
    Unit test for the _add_detailed_values() method in OutputManager class.
    """

    # Arrange
    output_manager = OutputManager()
    mocker.patch.object(output_manager, "_include_detailed_values", detailed_values_flag)

    # Act
    result = output_manager._add_detailed_values(input_data)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    "new_flag_value",
    [
        True,
        False,
    ],
)
def test_set_detailed_values(new_flag_value: bool) -> None:
    """
    Unit test for the set_include_detailed_values() method in OutputManager class.
    """

    # Arrange
    manager1 = OutputManager()

    # Assert initial value
    assert not manager1._include_detailed_values

    # Act
    manager1.set_include_detailed_values(new_flag_value)

    # Assert
    assert manager1._include_detailed_values == new_flag_value

    # Clean up
    manager1.set_include_detailed_values(False)


@pytest.mark.parametrize(
    "sub_data_dict, expected_result",
    [
        # Case 1: All conditions met
        ({"info_maps": [{"data_origin": "source"}], "values": [1]}, True),
        # Case 2: Not a dictionary
        ("not_a_dict", False),
        # Case 3: Missing 'info_maps' key
        ({"values": [1]}, False),
        # Case 4: Missing 'values' key
        ({"info_maps": [{"data_origin": "source"}]}, False),
        # Case 5: 'info_maps' and 'values' have different lengths
        ({"info_maps": [{"data_origin": "source"}, {"data_origin": "source2"}], "values": [1]}, False),
    ],
)
def test_can_add_detailed_values(sub_data_dict: Dict[str, Any], expected_result: bool) -> None:
    """
    Unit test for the _can_add_detailed_values() method in OutputManager class.
    """

    # Arrange
    output_manager = OutputManager()

    # Act
    result = output_manager._can_add_detailed_values(sub_data_dict)

    # Assert
    assert result == expected_result


@pytest.mark.parametrize("flag_value", [False, True])
def test_set_exclude_info_maps_flag(flag_value: bool) -> None:
    """
    Unit test for the set_exclude_info_maps_flag() method in OutputManager class
    """

    # Arrange
    output_manager = OutputManager()

    # Assert before
    assert not output_manager._exclude_info_maps_flag

    # Act
    output_manager.set_exclude_info_maps_flag(flag_value)

    # Assert after
    assert output_manager._exclude_info_maps_flag == flag_value

    # Cleanup
    output_manager._exclude_info_maps_flag = False


def test_save_current_variable_pool(mocker: MockerFixture) -> None:
    output_manager = OutputManager()

    info_map = {
        "class": output_manager.__class__.__name__,
        "function": output_manager._save_current_variable_pool.__name__,
    }

    dummy_saved_pool_chunks_num = 0
    dummy_variable_pool = {"a": 1, "b": "B", "c": True}

    output_manager.saved_pool_chunks_path = Path("dummy_path")
    output_manager.saved_pool_chunks_num = dummy_saved_pool_chunks_num
    output_manager.variables_pool = dummy_variable_pool
    output_manager.current_pool_size = 1024

    mock_create_directory = mocker.patch.object(output_manager, "create_directory")
    mock_generate_file_name = mocker.patch.object(output_manager, "generate_file_name", return_value="dummy_file.json")
    mock_dict_to_file_json = mocker.patch.object(output_manager, "dict_to_file_json")
    mock_add_log = mocker.patch.object(output_manager, "add_log")

    output_manager._save_current_variable_pool()

    mock_create_directory.assert_called_once_with(output_manager.saved_pool_chunks_path)
    mock_generate_file_name.assert_called_once_with(f"saved_pool_{dummy_saved_pool_chunks_num}", "json")

    dummy_file_path = Path.joinpath(output_manager.saved_pool_chunks_path, "dummy_file.json")
    mock_dict_to_file_json.assert_called_once_with(
        data_dict=dummy_variable_pool, path=dummy_file_path, minify_output_file=False
    )

    log_message = f"Saved the current variable pool to {dummy_file_path}"
    mock_add_log.assert_called_once_with("save_current_variable_pool", log_message, info_map)

    assert output_manager.variables_pool == {}
    assert output_manager.current_pool_size == sys.getsizeof(output_manager.variables_pool.__repr__())
    assert output_manager.saved_pool_chunks_num == 1


def test_filter_saved_pools():
    pass
