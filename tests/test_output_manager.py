import json
import os
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Sequence, Type, Union, cast

import pandas as pd
import psutil
import pytest
from freezegun import freeze_time
from mock import ANY, PropertyMock, mock_open, patch
from mock.mock import MagicMock, call
from pytest import CaptureFixture, raises
from pytest_mock.plugin import MockerFixture

from RUFAS.general_constants import GeneralConstants
from RUFAS.output_manager import LogVerbosity, OriginLabel, OutputManager
from RUFAS.units import MeasurementUnits
from RUFAS.util import Utility

DISCLAIMER_MESSAGE = "Under construction, use the results with caution."


def test_get_prefix() -> None:
    """Unit test for function _get_prefix in file output_manager.py"""
    om = OutputManager()
    assert om._get_prefix("class", "func") == "class.func"


@pytest.fixture
def mock_output_manager() -> OutputManager:
    output_manager = OutputManager()
    return output_manager


@pytest.mark.parametrize(
    "is_end_to_end_testing_run, expected_prefixes",
    [
        (True, {"json": "e2e_json_", "comparison": "e2e_comparison_"}),
        (False, {"csv": "csv_", "graph": "graph_", "json": "json_", "report": "report_"}),
    ],
)
def test_filter_prefixes(is_end_to_end_testing_run: bool, expected_prefixes: dict[str, str]) -> None:
    """Unit test for the _filter_prefixes property in the file output_manager.py"""
    manager = OutputManager()
    manager.is_end_to_end_testing_run = is_end_to_end_testing_run

    assert manager._filter_prefixes == expected_prefixes


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
        ("var1", {"var1": "m"}, None, " (m)", None),
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
    "data, direction, expected_result, should_write, should_add_error",
    [
        (
            {"var1": {"values": [1.0, True, "test"], "info_maps": []}},
            "portrait",
            f'DISCLAIMER,var1{os.linesep}"{DISCLAIMER_MESSAGE}",1.0{os.linesep},True' f"{os.linesep},test{os.linesep}",
            True,
            False,
        ),
        (
            {"var1": {"values": [1.0, True, "test"]}},
            "portrait",
            f'DISCLAIMER,var1{os.linesep}"{DISCLAIMER_MESSAGE}",1.0{os.linesep},True{os.linesep}' f",test{os.linesep}",
            True,
            False,
        ),
        (
            {
                "var1": {
                    "values": [1, 2, 3],
                    "info_maps": [{"units": "m"}, {"units": "m"}, {"units": "m"}],
                }
            },
            "portrait",
            f'DISCLAIMER,var1 (m){os.linesep}"{DISCLAIMER_MESSAGE}",1{os.linesep},2' f"{os.linesep},3{os.linesep}",
            True,
            False,
        ),
        (
            {"var1": {"values": [1, 2, 3]}},
            "portrait",
            f'DISCLAIMER,var1{os.linesep}"{DISCLAIMER_MESSAGE}",1{os.linesep},2{os.linesep}' f",3{os.linesep}",
            True,
            False,
        ),
        (
            {
                "var1": {
                    "values": [1, 2],
                    "info_maps": [{"units": "unitless"}, {"units": "unitless"}],
                }
            },
            "portrait",
            f'DISCLAIMER,var1 (unitless){os.linesep}"{DISCLAIMER_MESSAGE}",1{os.linesep}' f",2{os.linesep}",
            True,
            False,
        ),
        (
            {
                "var1": {
                    "values": [{"v1": 1, "v2": 1}, {"v1": 2, "v2": 2}],
                    "info_maps": [{"units": {"v1": "m", "v2": "s"}}, {"units": {"v1": "m", "v2": "s"}}],
                }
            },
            "portrait",
            f'DISCLAIMER,var1.v1 (m),var1.v2 (s){os.linesep}"{DISCLAIMER_MESSAGE}",1,1{os.linesep}' f",2,2{os.linesep}",
            True,
            False,
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
            "portrait",
            f"DISCLAIMER,simple_key.key1 (random unit 1),simple_key.key2 (random unit 2)"
            f'{os.linesep}"{DISCLAIMER_MESSAGE}",'
            f'1,"[1, 1]"{os.linesep}'
            f","
            f'2,"[2, 2]"{os.linesep}'
            f","
            f'3,"[3, 3]"{os.linesep}',
            True,
            False,
        ),
        (
            {
                "simple_key1": {"values": [1, 2, 3]},
                "simple_key2": {"values": [4, 5, 6]},
            },
            "portrait",
            f'DISCLAIMER,simple_key1,simple_key2{os.linesep}"{DISCLAIMER_MESSAGE}",'
            f"1,4{os.linesep},2,5{os.linesep},3,6{os.linesep}",
            True,
            False,
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
            "portrait",
            f"DISCLAIMER,simple_key1 (random unit),simple_key2 (random unit)"
            f'{os.linesep}"{DISCLAIMER_MESSAGE}",'
            f"1,4{os.linesep},"
            f"2,5{os.linesep},"
            f"3,6{os.linesep},"
            f",8{os.linesep},"
            f",9{os.linesep}",
            True,
            False,
        ),
        ({}, "portrait", "", False, False),
        (
            {"var1": {"values": [1, 2, 3]}, "var2": {"values": [4, 5, 6]}},
            "landscape",
            f",0,1,2{os.linesep}"
            f'DISCLAIMER,"{DISCLAIMER_MESSAGE}",,{os.linesep}'
            f"var1,1,2,3{os.linesep}"
            f"var2,4,5,6{os.linesep}",
            True,
            False,
        ),
        (
            {"var1": {"values": [1.0, True, "test"], "info_maps": []}},
            "unknown",
            f'DISCLAIMER,var1{os.linesep}"{DISCLAIMER_MESSAGE}",1.0{os.linesep},True' f"{os.linesep},test{os.linesep}",
            True,
            True,
        ),
        (
            {"var1": {"values": [1.0, True, "test"]}},
            "unknown",
            f'DISCLAIMER,var1{os.linesep}"{DISCLAIMER_MESSAGE}",1.0{os.linesep},True{os.linesep}' f",test{os.linesep}",
            True,
            True,
        ),
        (
            {
                "var1": {
                    "values": [1, 2, 3],
                    "info_maps": [{"units": "m"}, {"units": "m"}, {"units": "m"}],
                }
            },
            "unknown",
            f'DISCLAIMER,var1 (m){os.linesep}"{DISCLAIMER_MESSAGE}",1{os.linesep},2' f"{os.linesep},3{os.linesep}",
            True,
            True,
        ),
        (
            {"var1": {"values": [1, 2, 3]}},
            "unknown",
            f'DISCLAIMER,var1{os.linesep}"{DISCLAIMER_MESSAGE}",1{os.linesep},2{os.linesep}' f",3{os.linesep}",
            True,
            True,
        ),
        (
            {
                "var1": {
                    "values": [1, 2],
                    "info_maps": [{"units": "unitless"}, {"units": "unitless"}],
                }
            },
            "unknown",
            f'DISCLAIMER,var1 (unitless){os.linesep}"{DISCLAIMER_MESSAGE}",1{os.linesep}' f",2{os.linesep}",
            True,
            True,
        ),
        (
            {
                "var1": {
                    "values": [{"v1": 1, "v2": 1}, {"v1": 2, "v2": 2}],
                    "info_maps": [{"units": {"v1": "m", "v2": "s"}}, {"units": {"v1": "m", "v2": "s"}}],
                }
            },
            "unknown",
            f'DISCLAIMER,var1.v1 (m),var1.v2 (s){os.linesep}"{DISCLAIMER_MESSAGE}",1,1{os.linesep}' f",2,2{os.linesep}",
            True,
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
            "unknown",
            f"DISCLAIMER,simple_key.key1 (random unit 1),simple_key.key2 (random unit 2)"
            f'{os.linesep}"{DISCLAIMER_MESSAGE}",'
            f'1,"[1, 1]"{os.linesep}'
            f","
            f'2,"[2, 2]"{os.linesep}'
            f","
            f'3,"[3, 3]"{os.linesep}',
            True,
            True,
        ),
        (
            {
                "simple_key1": {"values": [1, 2, 3]},
                "simple_key2": {"values": [4, 5, 6]},
            },
            "unknown",
            f'DISCLAIMER,simple_key1,simple_key2{os.linesep}"{DISCLAIMER_MESSAGE}",'
            f"1,4{os.linesep},2,5{os.linesep},3,6{os.linesep}",
            True,
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
            "unknown",
            f"DISCLAIMER,simple_key1 (random unit),simple_key2 (random unit)"
            f'{os.linesep}"{DISCLAIMER_MESSAGE}",'
            f"1,4{os.linesep},"
            f"2,5{os.linesep},"
            f"3,6{os.linesep},"
            f",8{os.linesep},"
            f",9{os.linesep}",
            True,
            True,
        ),
        ({}, "unknown", "", False, False),
        (
            {"var1": {"values": [1.0, True, "test"], "info_maps": []}},
            None,
            f'DISCLAIMER,var1{os.linesep}"{DISCLAIMER_MESSAGE}",1.0{os.linesep},True' f"{os.linesep},test{os.linesep}",
            True,
            False,
        ),
        (
            {"var1": {"values": [1.0, True, "test"]}},
            None,
            f'DISCLAIMER,var1{os.linesep}"{DISCLAIMER_MESSAGE}",1.0{os.linesep},True{os.linesep}' f",test{os.linesep}",
            True,
            False,
        ),
        (
            {
                "var1": {
                    "values": [1, 2, 3],
                    "info_maps": [{"units": "m"}, {"units": "m"}, {"units": "m"}],
                }
            },
            None,
            f'DISCLAIMER,var1 (m){os.linesep}"{DISCLAIMER_MESSAGE}",1{os.linesep},2' f"{os.linesep},3{os.linesep}",
            True,
            False,
        ),
        (
            {"var1": {"values": [1, 2, 3]}},
            None,
            f'DISCLAIMER,var1{os.linesep}"{DISCLAIMER_MESSAGE}",1{os.linesep},2{os.linesep}' f",3{os.linesep}",
            True,
            False,
        ),
        (
            {
                "var1": {
                    "values": [1, 2],
                    "info_maps": [{"units": "unitless"}, {"units": "unitless"}],
                }
            },
            None,
            f'DISCLAIMER,var1 (unitless){os.linesep}"{DISCLAIMER_MESSAGE}",1{os.linesep}' f",2{os.linesep}",
            True,
            False,
        ),
        (
            {
                "var1": {
                    "values": [{"v1": 1, "v2": 1}, {"v1": 2, "v2": 2}],
                    "info_maps": [{"units": {"v1": "m", "v2": "s"}}, {"units": {"v1": "m", "v2": "s"}}],
                }
            },
            None,
            f'DISCLAIMER,var1.v1 (m),var1.v2 (s){os.linesep}"{DISCLAIMER_MESSAGE}",1,1{os.linesep}' f",2,2{os.linesep}",
            True,
            False,
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
            None,
            f"DISCLAIMER,simple_key.key1 (random unit 1),simple_key.key2 (random unit 2)"
            f'{os.linesep}"{DISCLAIMER_MESSAGE}",'
            f'1,"[1, 1]"{os.linesep}'
            f","
            f'2,"[2, 2]"{os.linesep}'
            f","
            f'3,"[3, 3]"{os.linesep}',
            True,
            False,
        ),
        (
            {
                "simple_key1": {"values": [1, 2, 3]},
                "simple_key2": {"values": [4, 5, 6]},
            },
            None,
            f'DISCLAIMER,simple_key1,simple_key2{os.linesep}"{DISCLAIMER_MESSAGE}",'
            f"1,4{os.linesep},2,5{os.linesep},3,6{os.linesep}",
            True,
            False,
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
            None,
            f"DISCLAIMER,simple_key1 (random unit),simple_key2 (random unit)"
            f'{os.linesep}"{DISCLAIMER_MESSAGE}",'
            f"1,4{os.linesep},"
            f"2,5{os.linesep},"
            f"3,6{os.linesep},"
            f",8{os.linesep},"
            f",9{os.linesep}",
            True,
            False,
        ),
        ({}, None, "", False, False),
    ],
)
def test_dict_to_file_csv(
    mock_output_manager: OutputManager,
    data: Dict[str, Any],
    direction: str,
    expected_result: str,
    should_write: bool,
    should_add_error: bool,
    mocker: MockerFixture,
) -> None:
    """Unit test for the function _dict_to_file_csv in the file output_manager.py"""
    mock_add_error = mocker.patch.object(mock_output_manager, "add_error")
    mocker.patch.object(mock_output_manager, "add_log")
    open_mock = mock_open()

    with patch("builtins.open", open_mock):
        mock_output_manager._dict_to_file_csv(data, Path("test"), direction)

    if should_write:
        open_mock.assert_any_call("test", "w", encoding="utf-8", errors="strict", newline="")

    written_data = "".join(call[1][0] for call in open_mock().write.mock_calls)

    assert written_data == expected_result
    if should_add_error:
        mock_add_error.assert_called_once_with(
            "Unknown Direction for CSV Output",
            f"The provided direction '{direction}' is not recognized. "
            f"Saving the output in portrait direction as default.",
            {
                "class": mock_output_manager.__class__.__name__,
                "function": mock_output_manager._dict_to_file_csv.__name__,
            },
        )


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
        mock_output_manager.dict_to_file_json(data, Path("test"))

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
        mock_output_manager.dict_to_file_json(data, Path("test"), minify_output_file=True)

    written_data = "".join(call[1][0] for call in open_mock().write.mock_calls)
    assert written_data == json.dumps({**{"DISCLAIMER": DISCLAIMER_MESSAGE}, **data}, separators=(",", ":"))


def test_dict_to_file_json_exception(mock_output_manager: OutputManager) -> None:
    """Test file opening failure for dict_to_file_json() in the file output_manager.py"""
    open_mock = mock_open()
    open_mock.side_effect = IOError
    data = {"var1": {"values": [1, 2, 3], "info_maps": [1, 2, 3]}}

    with patch("builtins.open", open_mock):
        with raises(Exception):
            mock_output_manager.dict_to_file_json(data, Path("test"))


def test_dict_to_file_csv_exception(mock_output_manager: OutputManager) -> None:
    """Unit test for the function _dict_to_file_csv in the file output_manager.py"""
    open_mock = mock_open()
    open_mock.side_effect = IOError
    data = {"var1": {"values": [1, 2, 3], "info_maps": [1, 2, 3]}}

    with patch("builtins.open", open_mock):
        with raises(Exception):
            mock_output_manager._dict_to_file_csv(data, Path("test"), "portrait")


def test_generate_key() -> None:
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
    log_verbose: LogVerbosity,
    mocker: MockerFixture,
) -> None:
    """Unit test for function add_error in file output_manager.py"""
    key = "dummy_key"
    name = "dummy_name"
    message = "dummy_value"
    timestamp = "18-Jan-2023_Wed_22-38-14.123456"
    info_map: dict[str, str] = {}
    metadata_prefix = "dummy_prefix"
    mock_generate_key = mocker.patch.object(mock_output_manager, "_generate_key", return_value=key)
    mock_add_to_pool = mocker.patch.object(mock_output_manager, "_add_to_pool")
    mocker.patch("RUFAS.output_manager.Utility.get_timestamp", return_value=timestamp)
    mock_output_manager.set_log_verbose(log_verbose)
    mock_output_manager.set_metadata_prefix(metadata_prefix)
    mock_handle_log_output = mocker.patch.object(mock_output_manager, "_handle_log_output")

    mock_output_manager.add_error(name, message, info_map)

    mock_generate_key.assert_called_once_with(name, info_map)

    assert info_map.get("timestamp") == timestamp
    mock_handle_log_output.assert_called_once_with(name, message, info_map, LogVerbosity.ERRORS)
    mock_add_to_pool.assert_called_once_with(mock_output_manager.errors_pool, key, message, info_map)


@pytest.mark.parametrize(
    "log_verbose",
    [LogVerbosity.NONE, LogVerbosity.ERRORS, LogVerbosity.WARNINGS, LogVerbosity.LOGS],
)
def test_add_warning(
    mock_output_manager: OutputManager,
    log_verbose: LogVerbosity,
    mocker: MockerFixture,
) -> None:
    """Unit test for function add_warning in file output_manager.py"""
    key = "dummy_key"
    name = "dummy_name"
    message = "dummy_value"
    timestamp = "18-Jan-2023_Wed_22-38-14.123456"
    info_map: dict[str, str] = {}
    metadata_prefix = "dummy_prefix"
    mock_generate_key = mocker.patch.object(mock_output_manager, "_generate_key", return_value=key)
    mock_add_to_pool = mocker.patch.object(mock_output_manager, "_add_to_pool")
    mocker.patch("RUFAS.output_manager.Utility.get_timestamp", return_value=timestamp)
    mock_output_manager.set_log_verbose(log_verbose)
    mock_output_manager.set_metadata_prefix(metadata_prefix)
    mock_handle_log_output = mocker.patch.object(mock_output_manager, "_handle_log_output")

    mock_output_manager.add_warning(name, message, info_map)

    mock_generate_key.assert_called_once_with(name, info_map)

    assert info_map.get("timestamp") == timestamp
    mock_handle_log_output.assert_called_once_with(name, message, info_map, LogVerbosity.WARNINGS)

    mock_add_to_pool.assert_called_once_with(mock_output_manager.warnings_pool, key, message, info_map)


@pytest.mark.parametrize(
    "log_verbose",
    [LogVerbosity.NONE, LogVerbosity.ERRORS, LogVerbosity.WARNINGS, LogVerbosity.LOGS],
)
def test_add_log(
    mock_output_manager: OutputManager,
    log_verbose: LogVerbosity,
    mocker: MockerFixture,
) -> None:
    """Unit test for function add_log in file output_manager.py"""
    key = "dummy_key"
    name = "dummy_name"
    message = "dummy_value"
    timestamp = "18-Jan-2023_Wed_22-38-14.123456"
    info_map: dict[str, str | dict[str, Any]] = {}
    mock_generate_key = mocker.patch.object(mock_output_manager, "_generate_key", return_value=key)
    mock_add_to_pool = mocker.patch.object(mock_output_manager, "_add_to_pool")
    mock_get_timestamp = mocker.patch("RUFAS.output_manager.Utility.get_timestamp", return_value=timestamp)
    mock_set_log_verbose = mocker.patch.object(mock_output_manager, "set_log_verbose")
    mock_set_log_verbose(log_verbose)
    mocker.patch.object(mock_output_manager, "set_metadata_prefix")
    mock_handle_log_output = mocker.patch.object(mock_output_manager, "_handle_log_output")

    mock_output_manager.add_log(name, message, info_map)

    mock_generate_key.assert_called_once_with(name, info_map)

    assert info_map.get("timestamp") == timestamp

    mock_output_manager._add_to_pool(mock_output_manager.logs_pool, key, message, info_map)

    mock_handle_log_output.assert_called_once_with(name, message, info_map, LogVerbosity.LOGS)
    mock_get_timestamp.assert_called_once()
    mock_add_to_pool.assert_called_with(mock_output_manager.logs_pool, key, message, info_map)


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
        # Case 4: 'units' is a dict, but lengths do not match with value, should raise KeyError
        (
            "var4",
            [1, 2, 3],
            {"class": "TestClass", "function": "test_function", "units": {"key1": "kg", "key2": "g"}},
            True,
            KeyError,
        ),
        # Case 5: 'units' is a dict, lengths match with value, no exception
        (
            "var5",
            [1, 2],
            {"class": "TestClass", "function": "test_function", "units": {"key1": "kg", "key2": "g"}},
            True,
            None,
        ),
        # Case 6: 'units' is a dict, lengths do not match with value (empty value), no exception
        (
            "var6",
            {},
            {"class": "TestClass", "function": "test_function", "units": {"key1": "kg", "key2": "g"}},
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
    "name, value, info_map, first_map",
    [
        # Case 1: Everything correct, no exception should be raised
        ("var1", 100, {"class": "TestClass", "function": "test_function", "units": "kg"}, True),
        # Case 1.5: Everything correct, no exception should be raised, only first info map should be recorded.
        ("var1", 100, {"class": "TestClass", "function": "test_function", "units": "kg"}, False),
        # Case 3: Value is a dict, should process sub-keys
        ("var3", {"sub1": 10, "sub2": 20}, {"class": "TestClass", "function": "test_function", "units": "kg"}, True),
    ],
)
def test_add_variable_chunkification_save_chunk_threshold_specified(
    name: str,
    value: Any,
    info_map: Dict[str, Any],
    first_map: bool,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for the add_variable() method in output_manager.py.
    """

    # Arrange
    output_manager = OutputManager()
    output_manager.chunkification = True
    output_manager.current_pool_size = 1024
    output_manager.average_add_variable_call_addition = 1024
    output_manager.add_variable_call = 9
    output_manager.save_chunk_threshold_call_count = 10
    mocker.patch.object(output_manager, "_stringify_units", return_value="validated_units")
    mocker.patch.object(output_manager, "_generate_key", return_value="key_with_prefix")
    patched_add_to_pool = mocker.patch.object(output_manager, "_add_to_pool")
    mocker.patch.dict(output_manager._variables_usage_counter, {}, clear=True)
    patched_save_current_variable_pool = mocker.patch.object(output_manager, "_save_current_variable_pool")

    expected_pool_size = 1024 + 1024

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

    assert output_manager.current_pool_size == expected_pool_size
    assert output_manager.add_variable_call == 10
    patched_save_current_variable_pool.assert_called_once()


@pytest.mark.parametrize(
    "name, value, info_map, first_map",
    [
        # Case 1: Everything correct, no exception should be raised
        ("var1", 100, {"class": "TestClass", "function": "test_function", "units": "kg"}, True),
        # Case 1.5: Everything correct, no exception should be raised, only first info map should be recorded.
        ("var1", 100, {"class": "TestClass", "function": "test_function", "units": "kg"}, False),
        # Case 3: Value is a dict, should process sub-keys
        ("var3", {"sub1": 10, "sub2": 20}, {"class": "TestClass", "function": "test_function", "units": "kg"}, True),
    ],
)
def test_add_variable_chunkification_save_chunk_threshold_no_call(
    name: str,
    value: Any,
    info_map: Dict[str, Any],
    first_map: bool,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for the add_variable() method in output_manager.py.
    """

    # Arrange
    output_manager = OutputManager()
    output_manager.chunkification = True
    output_manager.current_pool_size = 1024
    output_manager.average_add_variable_call_addition = 1024
    output_manager.add_variable_call = 8
    output_manager.save_chunk_threshold_call_count = 10
    mocker.patch.object(output_manager, "_stringify_units", return_value="validated_units")
    mocker.patch.object(output_manager, "_generate_key", return_value="key_with_prefix")
    patched_add_to_pool = mocker.patch.object(output_manager, "_add_to_pool")
    mocker.patch.dict(output_manager._variables_usage_counter, {}, clear=True)
    patched_save_current_variable_pool = mocker.patch.object(output_manager, "_save_current_variable_pool")

    expected_pool_size = 1024 + 1024

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

    assert output_manager.current_pool_size == expected_pool_size
    assert output_manager.add_variable_call == 9
    patched_save_current_variable_pool.assert_not_called()


@pytest.mark.parametrize(
    "name, value, info_map, first_map",
    [
        # Case 1: Everything correct, no exception should be raised
        ("var1", 100, {"class": "TestClass", "function": "test_function", "units": "kg"}, True),
        # Case 1.5: Everything correct, no exception should be raised, only first info map should be recorded.
        ("var1", 100, {"class": "TestClass", "function": "test_function", "units": "kg"}, False),
        # Case 3: Value is a dict, should process sub-keys
        ("var3", {"sub1": 10, "sub2": 20}, {"class": "TestClass", "function": "test_function", "units": "kg"}, True),
    ],
)
def test_add_variable_chunkification_save_chunk_threshold_unspecified(
    name: str,
    value: Any,
    info_map: Dict[str, Any],
    first_map: bool,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for the add_variable() method in output_manager.py.
    """

    # Arrange
    output_manager = OutputManager()
    output_manager.chunkification = True
    output_manager.current_pool_size = 1024
    output_manager.average_add_variable_call_addition = 1024
    output_manager.maximum_pool_size = 2000
    output_manager.add_variable_call = 9
    output_manager.save_chunk_threshold_call_count = 0
    mocker.patch.object(output_manager, "_stringify_units", return_value="validated_units")
    mocker.patch.object(output_manager, "_generate_key", return_value="key_with_prefix")
    patched_add_to_pool = mocker.patch.object(output_manager, "_add_to_pool")
    mocker.patch.dict(output_manager._variables_usage_counter, {}, clear=True)
    patched_save_current_variable_pool = mocker.patch.object(output_manager, "_save_current_variable_pool")

    expected_pool_size = 1024 + 1024

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

    assert output_manager.current_pool_size == expected_pool_size
    assert output_manager.add_variable_call == 10
    patched_save_current_variable_pool.assert_called_once()


@pytest.mark.parametrize(
    "name, value, info_map, first_map",
    [
        # Case 1: Everything correct, no exception should be raised
        ("var1", 100, {"class": "TestClass", "function": "test_function", "units": "kg"}, True),
        # Case 1.5: Everything correct, no exception should be raised, only first info map should be recorded.
        ("var1", 100, {"class": "TestClass", "function": "test_function", "units": "kg"}, False),
        # Case 3: Value is a dict, should process sub-keys
        ("var3", {"sub1": 10, "sub2": 20}, {"class": "TestClass", "function": "test_function", "units": "kg"}, True),
    ],
)
def test_add_variable_chunkification_save_chunk_threshold_unspecified_no_call(
    name: str,
    value: Any,
    info_map: Dict[str, Any],
    first_map: bool,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for the add_variable() method in output_manager.py.
    """

    # Arrange
    output_manager = OutputManager()
    output_manager.chunkification = True
    output_manager.current_pool_size = 1024
    output_manager.average_add_variable_call_addition = 1024
    output_manager.maximum_pool_size = 4096
    output_manager.add_variable_call = 9
    output_manager.save_chunk_threshold_call_count = 0
    mocker.patch.object(output_manager, "_stringify_units", return_value="validated_units")
    mocker.patch.object(output_manager, "_generate_key", return_value="key_with_prefix")
    patched_add_to_pool = mocker.patch.object(output_manager, "_add_to_pool")
    mocker.patch.dict(output_manager._variables_usage_counter, {}, clear=True)
    patched_save_current_variable_pool = mocker.patch.object(output_manager, "_save_current_variable_pool")

    expected_pool_size = 1024 + 1024

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

    assert output_manager.current_pool_size == expected_pool_size
    assert output_manager.add_variable_call == 10
    patched_save_current_variable_pool.assert_not_called()


@pytest.mark.parametrize(
    "variables, info_maps, first_info_map_only",
    [
        (
            {"var1": 100, "var2": 200},
            [
                {"class": "TestClass", "function": "test_function", "units": "kg"},
                {"class": "TestClass", "function": "test_function", "units": "kg"},
            ],
            True,
        ),
        ({}, [], False),
        (
            {"var1": 100, "var2": 200},
            [
                {"class": "TestClass", "function": "test_function", "units": "kg"},
                {"class": "TestClass", "function": "test_function", "units": "m"},
            ],
            True,
        ),
        (
            {f"var{i}": i for i in range(1000)},
            [{"class": "TestClass", "function": "test_function", "units": "kg"}] * 1000,
            False,
        ),
        ({"var1": 100}, [{"class": "TestClass", "function": "test_function", "units": "kg"}], False),
    ],
)
def test_add_variable_bulk(
    variables: dict[str, Any], info_maps: list[dict[str, Any]], first_info_map_only: bool, mocker: MockerFixture
) -> None:
    """Unit test for the add_variable_bulk() method in output_manager.py."""
    om = OutputManager()
    mock_add_variable = mocker.patch.object(om, "add_variable")
    inputs = [({name: value}, info_maps[index]) for index, (name, value) in enumerate(variables.items())]
    om.add_variable_bulk(inputs, first_info_map_only)

    assert mock_add_variable.call_args_list == [
        call(name, value, info_maps[index], first_info_map_only)
        for index, (name, value) in enumerate(variables.items())
    ]


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
    units: dict[str, Any] | MeasurementUnits,
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
def test_handle_log_output(capsys: CaptureFixture[str], log_level: LogVerbosity, color_code: str) -> None:
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
    om.chunkification = False
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


def test_dump_all_nondata_pools(mocker: MockerFixture) -> None:
    """Test case for function dump_all_nondata_pools in output_manager.py"""

    # Arrange
    output_manager = OutputManager()
    path = Path("dummy_path")
    patch_create_dir = mocker.patch.object(output_manager, "create_directory")
    patch_for_dump_errors = mocker.patch.object(output_manager, "dump_errors")
    patch_for_dump_warnings = mocker.patch.object(output_manager, "dump_warnings")
    patch_for_dump_logs = mocker.patch.object(output_manager, "dump_logs")
    patch_for_dump_variable_names_and_contexts = mocker.patch.object(output_manager, "dump_variable_names_and_contexts")
    patch_for_report_variables_usage_counts = mocker.patch.object(output_manager, "report_variables_usage_counts")

    # Act
    output_manager.dump_all_nondata_pools(path, False, "verbose")

    # Assert
    patch_create_dir.assert_called_once_with(path)
    patch_for_dump_variable_names_and_contexts.assert_called_once_with(path, False, "verbose")
    patch_for_dump_errors.assert_called_once_with(path)
    patch_for_dump_warnings.assert_called_once_with(path)
    patch_for_dump_logs.assert_called_once_with(path)
    patch_for_report_variables_usage_counts.assert_called_once_with(path)

    # Act
    output_manager.dump_all_nondata_pools(Path(path), True, "verbose")

    # Assert
    assert patch_create_dir.call_count == 2
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
    om.set_metadata_prefix(metadata_prefix)

    mocker.patch("RUFAS.output_manager.Utility.get_timestamp", return_value=timestamp)
    assert om.generate_file_name(base_name, extension) == f"{metadata_prefix}_{base_name}_{timestamp}.{extension}"


def test_dump_logs(
    mock_output_manager: OutputManager,
    mocker: MockerFixture,
) -> None:
    """Test case for function dump_logs in output_manager.py"""
    mock_generate_file_name = mocker.patch.object(mock_output_manager, "generate_file_name", return_value="dummy_name")
    mock_dict_to_file_json = mocker.patch.object(mock_output_manager, "dict_to_file_json")

    mock_output_manager.dump_logs(Path("dummy_path"))

    mock_generate_file_name.assert_called_once_with("logs", "json")
    mock_dict_to_file_json.assert_called_once_with(mock_output_manager.logs_pool, Path("dummy_path", "dummy_name"))


def test_dump_warnings(mock_output_manager: OutputManager, mocker: MockerFixture) -> None:
    """Test case for function dump_warnings in output_manager.py"""
    mock_generate_file_name = mocker.patch.object(mock_output_manager, "generate_file_name", return_value="dummy_name")
    mock_dict_to_file_json = mocker.patch.object(mock_output_manager, "dict_to_file_json")

    mock_output_manager.dump_warnings(Path("dummy_path"))

    mock_generate_file_name.assert_called_once_with("warnings", "json")
    mock_dict_to_file_json.assert_called_once_with(mock_output_manager.warnings_pool, Path("dummy_path", "dummy_name"))


def test_dump_errors(mock_output_manager: OutputManager, mocker: MockerFixture) -> None:
    """Test case for function dump_errors in output_manager.py"""
    mock_generate_file_name = mocker.patch.object(mock_output_manager, "generate_file_name", return_value="dummy_name")
    mock_dict_to_file_json = mocker.patch.object(mock_output_manager, "dict_to_file_json")

    mock_output_manager.dump_errors(Path("dummy_path"))

    mock_generate_file_name.assert_called_once_with("errors", "json")
    mock_dict_to_file_json.assert_called_once_with(mock_output_manager.errors_pool, Path("dummy_path", "dummy_name"))


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
                "var1 (units1)" + os.linesep,
                "var1.info_maps: timestamp (units1)" + os.linesep,
                "var1.info_maps: units" + os.linesep,
                "var2.info_maps: map1 (units1)" + os.linesep,
                "var2.info_maps: units" + os.linesep,
                "var2.values: v1 (units1)" + os.linesep,
                "var2.values: v2 (units1)" + os.linesep,
                "var3 ({'key1': 'unit1', 'key2': 'unit2'})" + os.linesep,
                "var3.info_maps: key1 (unit1)" + os.linesep,
                "var3.info_maps: key2 (unit2)" + os.linesep,
                "var3.info_maps: units" + os.linesep,
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
                "var3" + os.linesep,
            ],
            True,
            "verbose",
        ),
        (
            [
                "_exclude_info_maps=False, expect info_maps accordingly." + os.linesep,
                "var1 (units1)" + os.linesep,
                "var1" + os.linesep,
                "    .info_maps: timestamp (units1)" + os.linesep,
                "    .info_maps: units" + os.linesep,
                "var2" + os.linesep,
                "    .info_maps: map1 (units1)" + os.linesep,
                "    .info_maps: units" + os.linesep,
                "    .values: v1 (units1)" + os.linesep,
                "    .values: v2 (units1)" + os.linesep,
                "var3 ({'key1': 'unit1', 'key2': 'unit2'})" + os.linesep,
                "var3" + os.linesep,
                "    .info_maps: key1 (unit1)" + os.linesep,
                "    .info_maps: key2 (unit2)" + os.linesep,
                "    .info_maps: units" + os.linesep,
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
                "var3" + os.linesep,
            ],
            True,
            "block",
        ),
        (
            [
                "_exclude_info_maps=False, expect info_maps accordingly." + os.linesep,
                "var1 (units1)" + os.linesep,
                "var1.info_maps: ['timestamp', 'units']" + os.linesep,
                "var2.info_maps: ['map1', 'units']" + os.linesep,
                "var2.values: ['v1', 'v2'] (units1)" + os.linesep,
                "var3 ({'key1': 'unit1', 'key2': 'unit2'})" + os.linesep,
                "var3.info_maps: ['key1', 'key2', 'units']" + os.linesep,
            ],
            False,
            "inline",
        ),
        (
            [
                "_exclude_info_maps=True, expect info_maps accordingly." + os.linesep,
                "var1" + os.linesep,
                "var2.values: ['v1', 'v2']" + os.linesep,
                "var3" + os.linesep,
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
                "var3" + os.linesep,
            ],
            True,
            "basic",
        ),
        (
            [
                "_exclude_info_maps=False, expect info_maps accordingly." + os.linesep,
                "var1 (units1)" + os.linesep,
                "var1.timestamp (units1)" + os.linesep,
                "var1.units" + os.linesep,
                "var2.map1 (units1)" + os.linesep,
                "var2.units" + os.linesep,
                "var2.v1 (units1)" + os.linesep,
                "var2.v2 (units1)" + os.linesep,
                "var3 ({'key1': 'unit1', 'key2': 'unit2'})" + os.linesep,
                "var3.key1 (unit1)" + os.linesep,
                "var3.key2 (unit2)" + os.linesep,
                "var3.units" + os.linesep,
            ],
            False,
            "basic",
        ),
        (
            [
                "_exclude_info_maps=False, expect info_maps accordingly." + os.linesep,
                "var1 (units1)" + os.linesep,
                "var1.info_maps: timestamp (units1)" + os.linesep,
                "var1.info_maps: units" + os.linesep,
                "var2.info_maps: map1 (units1)" + os.linesep,
                "var2.info_maps: units" + os.linesep,
                "var2.values: v1 (units1)" + os.linesep,
                "var2.values: v2 (units1)" + os.linesep,
                "var3 ({'key1': 'unit1', 'key2': 'unit2'})" + os.linesep,
                "var3.info_maps: key1 (unit1)" + os.linesep,
                "var3.info_maps: key2 (unit2)" + os.linesep,
                "var3.info_maps: units" + os.linesep,
            ],
            False,
            "verbose",
        ),
    ],
)
def test_dump_variable_names_and_contexts(
    mock_output_manager: OutputManager,
    expected_result: List[str],
    exclude_info_maps: bool,
    format_option: str,
    mocker: MockerFixture,
) -> None:
    """Test case for function dump_variable_names_and_contexts in output_manager.py"""
    mock_variable_pool: Dict[str, Dict[str, List[Any]]] = {
        "var1": {
            "values": [1],
            "info_maps": [{"timestamp": "value1", "units": "units1"}, {"simulation_day": "value2", "units": "units2"}],
        },
        "var2": {
            "values": [{"v1": 1, "v2": 1}, {"v1": 2, "v2": 2}],
            "info_maps": [{"map1": "value1", "units": "units1"}, {"map1": "value2", "units": "units2"}],
        },
        "var3": {
            "values": [1],
            "info_maps": [{"key1": "value1", "key2": "value2", "units": {"key1": "unit1", "key2": "unit2"}}],
        },
    }
    mock_output_manager.variables_pool = mock_variable_pool
    mock_generate_file_name = mocker.patch.object(mock_output_manager, "generate_file_name", return_value="dummy_name")
    mock_list_to_file_txt = mocker.patch.object(mock_output_manager, "_list_to_file_txt")

    mock_output_manager.dump_variable_names_and_contexts(Path("dummy_path"), exclude_info_maps, format_option)

    mock_generate_file_name.assert_called_once_with("variable_names", "txt")
    mock_list_to_file_txt.assert_called_once_with(expected_result, Path("dummy_path", "dummy_name"))


def test_dump_variable_names_and_contexts_no_values(
    mock_output_manager: OutputManager,
    mocker: MockerFixture,
) -> None:
    """Test case for function dump_variable_names_and_contexts in output_manager.py when no values are present."""
    mock_flat_pool: dict[str, dict[str, list[Any]]] = {
        "var1": {
            "no_values": [1],
            "info_maps": [{"test": "value1"}, {"test": "value2"}],
        },
    }

    expected_output = [
        "_exclude_info_maps=False, expect info_maps accordingly." + os.linesep,
        "var1: **NO VARIABLES**" + os.linesep,
    ]

    mocker.patch.object(mock_output_manager, "_get_flat_variables_pool", return_value=mock_flat_pool)

    mock_generate_file_name = mocker.patch.object(mock_output_manager, "generate_file_name", return_value="dummy_name")
    mock_list_to_file_txt = mocker.patch.object(mock_output_manager, "_list_to_file_txt")

    mock_output_manager.dump_variable_names_and_contexts(Path("dummy_path"), False, format_option="verbose")

    mock_generate_file_name.assert_called_once_with("variable_names", "txt")
    mock_list_to_file_txt.assert_called_once_with(expected_output, Path("dummy_path", "dummy_name"))


def test_set_variables_pool_with_override(
    mock_output_manager: OutputManager,
) -> None:
    """Sets variables_pool and uses the explicit override for current_pool_size."""
    new_pool: dict[str, dict[str, Any]] = {"a": {"values": [1], "info_maps": []}}

    mock_output_manager._set_variables_pool(new_pool, pool_size_override=999)

    assert mock_output_manager.variables_pool is new_pool
    assert mock_output_manager.current_pool_size == 999


def test_set_variables_pool_without_override(mock_output_manager: OutputManager, mocker: MockerFixture) -> None:
    """Sets variables_pool and calculates current_pool_size via sys.getsizeof on repr(new_pool)."""
    new_pool: dict[str, dict[str, Any]] = {"x": {"values": [1, 2, 3], "info_maps": [{"u": "kg"}]}}

    mocked_getsizeof = mocker.patch("sys.getsizeof", return_value=1234)

    mock_output_manager._set_variables_pool(new_pool)

    assert mock_output_manager.variables_pool is new_pool
    mocked_getsizeof.assert_called_once_with(new_pool.__repr__())
    assert mock_output_manager.current_pool_size == 1234


def test_get_flat_variables_pool_empty_returns_empty(
    mock_output_manager: OutputManager,
) -> None:
    """Returns {} when variables_pool is empty/falsy."""
    mock_output_manager.variables_pool = {}

    result = mock_output_manager._get_flat_variables_pool()

    assert result == {}


def test_get_flat_variables_pool_already_flat_returns_self(
    mock_output_manager: OutputManager,
) -> None:
    """If all values are dicts containing 'values', return the mapping as-is."""
    flat_pool: dict[str, dict[str, Any]] = {
        "var1": {"values": [1], "info_maps": [{"units": "kg"}]},
        "var2": {"values": [2, 3], "info_maps": [{"units": "kg"}]},
    }
    mock_output_manager.variables_pool = flat_pool

    result = mock_output_manager._get_flat_variables_pool()

    assert result is flat_pool
    assert "var1" in result and "var2" in result
    assert result["var1"]["values"] == [1]


def test_get_flat_variables_pool_nested_is_flattened_and_non_dict_skipped(
    mock_output_manager: OutputManager,
) -> None:
    """Flattens nested pools and skips non-dict entries at the pool level."""
    mock_output_manager.variables_pool = cast(
        Any,
        {
            "poolA": {
                "var1": {"values": [1], "info_maps": [{"units": "kg"}]},
                "var2": {"values": [2], "info_maps": [{"units": "kg"}]},
            },
            "poolB": {
                "v3": {"values": [3], "info_maps": [{"units": "m"}]},
            },
            "not_a_pool": 42,
        },
    )

    result = mock_output_manager._get_flat_variables_pool()

    assert set(result.keys()) == {"poolA.var1", "poolA.var2", "poolB.v3"}
    assert result["poolA.var1"]["values"] == [1]
    assert result["poolB.v3"]["info_maps"][0]["units"] == "m"


def test_load_multiple_variables_pools_from_files_mixed_descriptors(
    mock_output_manager: OutputManager,
    mocker: MockerFixture,
) -> None:
    """Loads pools from a tuple(Path) and a dict(str path), passes correct info_map, and namespaces results."""
    pools_input: Sequence[tuple[str, Path] | dict[str, Any]] = [
        ("poolA", Path("a.json")),
        {"name": "poolB", "path": "b.json"},
    ]

    loaded_pool_a: dict[str, dict[str, Any]] = {"varA": {"values": [1], "info_maps": [{"units": "kg"}]}}
    loaded_pool_b: dict[str, dict[str, Any]] = {"varB": {"values": [2], "info_maps": [{"units": "m"}]}}

    read_mock = mocker.patch.object(
        mock_output_manager,
        "_read_variables_pool_file",
        side_effect=[loaded_pool_a, loaded_pool_b],
    )
    set_pool_mock = mocker.patch.object(mock_output_manager, "_set_variables_pool")

    mock_output_manager.load_multiple_variables_pools_from_files(pools_input)

    expected_class = mock_output_manager.__class__.__name__
    expected_func = "load_multiple_variables_pools_from_files"

    args0, kwargs0 = read_mock.call_args_list[0]
    assert args0[0] == Path("a.json")
    assert args0[1] == {"class": expected_class, "function": expected_func, "pool_name": "poolA"}

    args1, kwargs1 = read_mock.call_args_list[1]
    assert args1[0] == Path("b.json")
    assert args1[1] == {"class": expected_class, "function": expected_func, "pool_name": "poolB"}

    set_pool_mock.assert_called_once_with({"poolA": loaded_pool_a, "poolB": loaded_pool_b})


def test_load_multiple_variables_pools_from_files_only_tuples(
    mock_output_manager: OutputManager,
    mocker: MockerFixture,
) -> None:
    """Loads pools when all descriptors are (name, Path) tuples and preserves namespacing."""
    pools_input = [
        ("X", Path("x.json")),
        ("Y", Path("y.json")),
    ]

    loaded_x: dict[str, dict[str, Any]] = {"vx": {"values": [10], "info_maps": [{"units": "kg"}]}}
    loaded_y: dict[str, dict[str, Any]] = {"vy": {"values": [20], "info_maps": [{"units": "kg"}]}}

    read_mock = mocker.patch.object(
        mock_output_manager,
        "_read_variables_pool_file",
        side_effect=[loaded_x, loaded_y],
    )
    set_pool_mock = mocker.patch.object(mock_output_manager, "_set_variables_pool")

    mock_output_manager.load_multiple_variables_pools_from_files(pools_input)

    assert read_mock.call_count == 2
    assert read_mock.call_args_list[0][0][0] == Path("x.json")
    assert read_mock.call_args_list[1][0][0] == Path("y.json")

    set_pool_mock.assert_called_once_with({"X": loaded_x, "Y": loaded_y})


def test_load_multiple_variables_pools_from_files_empty_input(
    mock_output_manager: OutputManager,
    mocker: MockerFixture,
) -> None:
    """If no pools are provided, _set_variables_pool is called with an empty dict."""
    read_mock = mocker.patch.object(mock_output_manager, "_read_variables_pool_file")
    set_pool_mock = mocker.patch.object(mock_output_manager, "_set_variables_pool")

    mock_output_manager.load_multiple_variables_pools_from_files([])

    read_mock.assert_not_called()
    set_pool_mock.assert_called_once_with({})


def test_list_to_file_txt(
    mock_output_manager: OutputManager,
    tmp_path: Path,
) -> None:
    """Test case for function _list_to_file_text in output_manager.py"""
    dummy_file_path = tmp_path / "dummy_file.txt"
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


def test_exclude_info_maps(
    mock_output_manager: OutputManager,
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
    mock_file_text: str,
    filter_by_exclusion: bool,
) -> None:
    """Test case for function _load_filter_file_content in output_manager.py"""
    mock_file.return_value.read.return_value = mock_file_text
    result, direction = mock_output_manager._load_filter_file_content(Path("path/to/file.txt"))
    assert result == [{"filters": ["apples", "bananas", "cherries"], "filter_by_exclusion": filter_by_exclusion}]
    assert direction is None


@patch("builtins.open", new_callable=mock_open)
def test_load_filter_file_content_json(
    mock_file: MagicMock,
    mock_output_manager: OutputManager,
) -> None:
    """Test case for function _load_filter_file_content in output_manager.py"""

    data: Dict[str, Any] = {
        "filters": ["filter1", "filter2"],
        "other_key": "value",
    }
    mock_file.return_value.read.return_value = json.dumps(data)
    result, direction = mock_output_manager._load_filter_file_content(Path("some_file.json"))
    assert result == [data]
    assert direction is None


@patch("builtins.open", new_callable=mock_open)
@pytest.mark.parametrize("expected_direction", ["portrait", "landscape", "unknown"])
def test_load_filter_file_content_json_with_direction(
    mock_file: MagicMock,
    expected_direction: str,
    mock_output_manager: OutputManager,
) -> None:
    """Test case for function _load_filter_file_content in output_manager.py"""

    data: Dict[str, Any] = {"filters": ["filter1", "filter2"], "other_key": "value", "direction": expected_direction}
    mock_file.return_value.read.return_value = json.dumps(data)
    result, direction = mock_output_manager._load_filter_file_content(Path("some_file.json"))
    assert result == [data]
    assert direction == expected_direction


@patch("builtins.open", new_callable=mock_open)
def test_load_filter_file_content_json_multiple(
    mock_file: MagicMock,
    mock_output_manager: OutputManager,
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
    result, direction = mock_output_manager._load_filter_file_content(Path("some_file.json"))
    assert result == data["multiple"]
    assert direction is None


@patch("builtins.open", new_callable=mock_open)
@pytest.mark.parametrize("direction", ["portrait", "landscape", "unknown"])
def test_load_filter_file_content_json_multiple_with_direction(
    mock_file: MagicMock,
    direction: str,
    mock_output_manager: OutputManager,
) -> None:
    """Test case for function _load_filter_file_content in output_manager.py"""
    data: Dict[str, Any] = {
        "direction": direction,
        "multiple": [
            {
                "filters": ["filter1", "filter2"],
                "other_key": "value1",
            },
            {
                "filters": ["filter3", "filter4"],
                "other_key": "value2",
            },
        ],
    }
    mock_file.return_value.read.return_value = json.dumps(data)
    result, direction = mock_output_manager._load_filter_file_content(Path("some_file.json"))
    assert result == data["multiple"]
    assert direction == direction


@patch("builtins.open", new_callable=mock_open)
def test_load_filter_file_content_exception(
    mock_file: MagicMock,
    mock_output_manager: OutputManager,
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


def test_list_filter_files_in_dir(
    mock_output_manager: OutputManager,
    tmpdir,
    mocker: MockerFixture,
) -> None:
    mock_add_warning = mocker.patch.object(mock_output_manager, "add_warning")
    tmpdir.join("json_file1.txt").write("File 1 content")
    tmpdir.join("csv_file2.json").write("File 2 content")
    tmpdir.join("file3.txt").write("File 3 content")

    filter_files = mock_output_manager._list_filter_files_in_dir(Path(tmpdir))

    assert len(filter_files) == 2
    assert "json_file1.txt" in filter_files
    assert "csv_file2.json" in filter_files
    assert "file3.csv" not in filter_files
    mock_add_warning.assert_called_once()

    with pytest.raises(NotADirectoryError):
        mock_output_manager._list_filter_files_in_dir(Path("nonexistent_directory"))


@pytest.fixture
def mock_simple_variables_pool() -> Dict[str, OutputManager.pool_element_type]:
    """Simple variables pool to be used for testing the Output Manager."""
    return {
        "key1": {"values": ["value1", "value2", "value3"], "info_maps": [{"key": "val"}]},
        "key2": {"values": ["value4", "value5", "value6"], "info_maps": [{"key": "val"}]},
        "key3": {"values": ["value7", "value8", "value9"], "info_maps": [{"key": "val"}]},
    }


@pytest.mark.parametrize(
    "filter_content,expected,data_padded",
    [
        ({"filters": []}, {}, False),
        (
            {"filters": [], "filter_by_exclusion": True, "expand_data": True},
            {
                "key1": {"values": ["value1", "value2", "value3"], "info_maps": [{"key": "val"}]},
                "key2": {"values": ["value4", "value5", "value6"], "info_maps": [{"key": "val"}]},
                "key3": {"values": ["value7", "value8", "value9"], "info_maps": [{"key": "val"}]},
            },
            True,
        ),
        (
            {"filters": ["key1", "key2"], "expand_data": True},
            {
                "key1": {"values": ["value1", "value2", "value3"], "info_maps": [{"key": "val"}]},
                "key2": {"values": ["value4", "value5", "value6"], "info_maps": [{"key": "val"}]},
            },
            True,
        ),
        (
            {"filters": ["key1", "key2"], "filter_by_exclusion": True},
            {"key3": {"values": ["value7", "value8", "value9"], "info_maps": [{"key": "val"}]}},
            False,
        ),
        (
            {"filters": ["key1", "key4"], "filter_by_exclusion": False},
            {"key1": {"values": ["value1", "value2", "value3"], "info_maps": [{"key": "val"}]}},
            False,
        ),
        (
            {"filters": ["key1", "key4"], "slice_start": 1, "filter_by_exclusion": True},
            {
                "key2": {"values": ["value5", "value6"], "info_maps": []},
                "key3": {"values": ["value8", "value9"], "info_maps": []},
            },
            False,
        ),
        (
            {"filters": ["key1", "key1"], "slice_end": 1, "filter_by_exclusion": False},
            {"key1": {"values": ["value1"], "info_maps": [{"key": "val"}]}},
            False,
        ),
        (
            {"filters": ["key1", "key1"], "filter_by_exclusion": True},
            {
                "key2": {"values": ["value4", "value5", "value6"], "info_maps": [{"key": "val"}]},
                "key3": {"values": ["value7", "value8", "value9"], "info_maps": [{"key": "val"}]},
            },
            False,
        ),
    ],
)
def test_filter_variables_pool(
    mock_output_manager: OutputManager,
    mock_simple_variables_pool: Dict[str, OutputManager.pool_element_type],
    mocker: MockerFixture,
    filter_content: Dict[str, Any],
    expected: Dict[str, Dict[str, str]],
    data_padded: bool,
) -> None:
    """Tests filter_variables_pool in the OutputManager."""
    mock_output_manager.variables_pool = mock_simple_variables_pool
    expand_data_temporally = mocker.patch.object(Utility, "expand_data_temporally", side_effect=lambda _: _)

    assert mock_output_manager.filter_variables_pool(filter_content) == expected

    if data_padded:
        expand_data_temporally.assert_called_once()
    else:
        expand_data_temporally.assert_not_called()


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
    mock_output_manager.variables_pool = {}


def test_filter_variables_pool_exclude_regex_patterns(
    mock_output_manager: OutputManager,
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
    mock_output_manager.variables_pool = {}


@pytest.fixture
def mock_variables_pool_complex() -> dict[str, OutputManager.pool_element_type]:
    dummy_variables_pool: dict[str, OutputManager.pool_element_type] = {
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
    mock_variables_pool_complex: dict[str, OutputManager.pool_element_type],
    mocker: MockerFixture,
) -> None:
    """Test case for pattern pool with regex patterns and exclude keyword with function filter_variables_pool in
    output_manager.py"""
    mock_output_manager.variables_pool = mock_variables_pool_complex
    # use filter_name
    filter_content: Dict[str, Any] = {
        "name": "test_case_1",
        "filters": ["^DummyClass1.*"],
        "filter_by_exclusion": False,
        "use_name": True,
        "variables": ["var2", "a"],
    }
    expected_result: dict[str, OutputManager.pool_element_type] = {
        "test_case_1_0": {"values": ["value1", "value2", "value3"]},
        "test_case_1_1.a": {"values": ["A", "AA"]},
        "test_case_1_2.a": {"values": ["AAA"]},
    }
    assert mock_output_manager.filter_variables_pool(filter_content) == expected_result

    # unpacking pool error
    filter_content = {"filters": ["^DummyClass1.*"], "filter_by_exclusion": False, "variables": "a"}
    expected_result = {
        "DummyClass1.dummy_fun1.dummy_var1": {"values": ["value1", "value2", "value3"]},
        "DummyClass1.dummy_fun1.dummy_var2.a": {"values": ["A", "AA"]},
        "DummyClass1.dummy_fun2.dummy_var3.a": {"values": ["AAA"]},
    }
    mock_add_error = mocker.patch.object(mock_output_manager, "add_error")
    actual: dict[str, OutputManager.pool_element_type] = mock_output_manager.filter_variables_pool(filter_content)
    mock_add_error.assert_has_calls(
        [
            call(
                "Unpacking Pool Error",
                "Unable to unpack key='DummyClass1.dummy_fun1.dummy_var2' in the data pool, "
                "need a valid `variables` entry for this entry.is_data_in_dict=True, selected_variables='a', "
                "see Wiki for proper setup details.",
                {
                    "class": "OutputManager",
                    "function": "_parse_filtered_variables",
                    "filter_name": "NO NAME FOUND",
                    "filter_by_exclusion": False,
                    "use_filter_name": False,
                },
            ),
            call(
                "Unpacking Pool Error",
                "Unable to unpack key='DummyClass1.dummy_fun2.dummy_var3' in the data pool, "
                "need a valid `variables` entry for this entry.is_data_in_dict=True, selected_variables='a', "
                "see Wiki for proper setup details.",
                {
                    "class": "OutputManager",
                    "function": "_parse_filtered_variables",
                    "filter_name": "NO NAME FOUND",
                    "filter_by_exclusion": False,
                    "use_filter_name": False,
                },
            ),
        ],
        any_order=False,
    )

    assert actual == expected_result

    # use_name in dict data
    filter_content = {
        "name": "test_case_3",
        "filters": ["^DummyClass1.*"],
        "filter_by_exclusion": False,
        "use_name": False,
        "variables": ["a", "b", "c"],
    }
    expected_result = {
        "DummyClass1.dummy_fun1.dummy_var1": {"values": ["value1", "value2", "value3"]},
        "DummyClass1.dummy_fun1.dummy_var2.a": {"values": ["A", "AA"]},
        "DummyClass1.dummy_fun1.dummy_var2.b": {"values": [1.0, 2.0]},
        "DummyClass1.dummy_fun1.dummy_var2.c": {"values": [True, True]},
        "DummyClass1.dummy_fun2.dummy_var3.a": {"values": ["AAA"]},
        "DummyClass1.dummy_fun2.dummy_var3.b": {"values": [3.0]},
        "DummyClass1.dummy_fun2.dummy_var3.c": {"values": [False]},
    }

    assert mock_output_manager.filter_variables_pool(filter_content) == expected_result


@pytest.mark.parametrize(
    "pool,vars,exclusion,expected,expected_counter",
    [
        (
            {
                "DummyClass1.dummy_fun1.dummy_var1": {"values": ["value1", "value2", "value3"]},
                "DummyClass1.dummy_fun1.dummy_var2": {
                    "values": [{"a": "A", "b": 1.0, "c": True}, {"a": "AA", "b": 2.0, "c": True}]
                },
                "DummyClass1.dummy_fun2.dummy_var3": {"values": [{"a": "AAA", "b": 3.0, "c": False}]},
            },
            ["a"],
            False,
            {
                "DummyClass1.dummy_fun1.dummy_var1": {"values": ["value1", "value2", "value3"]},
                "a": {"values": ["A", "AA", "AAA"]},
            },
            Counter(
                {
                    "DummyClass1.dummy_fun1.dummy_var1": 1,
                    "DummyClass1.dummy_fun1.dummy_var2.a": 1,
                    "DummyClass1.dummy_fun2.dummy_var3.a": 1,
                }
            ),
        ),
        (
            {
                "DummyClass1.dummy_fun1.dummy_var1": {"values": ["value1", "value2", "value3"]},
                "DummyClass1.dummy_fun1.dummy_var2": {
                    "values": [{"a": "A", "b": 1.0, "c": True}, {"a": "AA", "b": 2.0, "c": True}]
                },
                "DummyClass1.dummy_fun2.dummy_var3": {"values": [{"a": "AAA", "b": 3.0, "c": False}]},
            },
            ["a"],
            True,
            {
                "DummyClass1.dummy_fun1.dummy_var1": {"values": ["value1", "value2", "value3"]},
                "b": {"values": [1.0, 2.0, 3.0]},
                "c": {"values": [True, True, False]},
            },
            Counter(
                {
                    "DummyClass1.dummy_fun1.dummy_var1": 1,
                    "DummyClass1.dummy_fun1.dummy_var2.b": 1,
                    "DummyClass1.dummy_fun1.dummy_var2.c": 1,
                    "DummyClass1.dummy_fun2.dummy_var3.b": 1,
                    "DummyClass1.dummy_fun2.dummy_var3.c": 1,
                }
            ),
        ),
    ],
)
def test_parse_filtered_variables(
    mock_output_manager: OutputManager,
    pool: dict[str, OutputManager.pool_element_type],
    vars: list[str],
    exclusion: bool,
    expected: dict[str, OutputManager.pool_element_type],
    expected_counter: Counter[str],
) -> None:
    """Tests _parse_filtered_variables in the Output Manager."""
    mock_output_manager._variables_usage_counter = Counter()

    actual = mock_output_manager._parse_filtered_variables(pool, vars, "test", False, exclusion, True)

    assert actual == expected
    assert mock_output_manager._variables_usage_counter == expected_counter


@pytest.mark.parametrize(
    "exclude_info_maps, produce_graphics, filter_content, is_faulty, chunkification, direction",
    [
        (True, True, [{"filters": ".*", "title": "dummy_title"}], False, False, "portrait"),
        (True, False, [{"filters": ".*", "title": "dummy_title"}], False, False, "portrait"),
        (False, True, [{"filters": ".*", "title": "dummy_title"}], False, False, "portrait"),
        (False, False, [{"filters": ".*", "title": "dummy_title"}], False, False, "portrait"),
        (True, True, [{"no_filters": ".*", "title": "dummy_title"}], True, False, "portrait"),
        (True, True, [{"filters": ".*", "title": "dummy_title"}], False, True, "portrait"),
        (True, False, [{"filters": ".*", "title": "dummy_title"}], False, True, "portrait"),
        (False, True, [{"filters": ".*", "title": "dummy_title"}], False, True, "portrait"),
        (False, False, [{"filters": ".*", "title": "dummy_title"}], False, True, "portrait"),
        (True, True, [{"no_filters": ".*", "title": "dummy_title"}], True, True, "portrait"),
        (True, True, [{"filters": ".*", "title": "dummy_title"}], False, False, "landscape"),
        (True, False, [{"filters": ".*", "title": "dummy_title"}], False, False, "landscape"),
        (False, True, [{"filters": ".*", "title": "dummy_title"}], False, False, "landscape"),
        (False, False, [{"filters": ".*", "title": "dummy_title"}], False, False, "landscape"),
        (True, True, [{"no_filters": ".*", "title": "dummy_title"}], True, False, "landscape"),
        (True, True, [{"filters": ".*", "title": "dummy_title"}], False, True, "landscape"),
        (True, False, [{"filters": ".*", "title": "dummy_title"}], False, True, "landscape"),
        (False, True, [{"filters": ".*", "title": "dummy_title"}], False, True, "landscape"),
        (False, False, [{"filters": ".*", "title": "dummy_title"}], False, True, "landscape"),
        (True, True, [{"no_filters": ".*", "title": "dummy_title"}], True, True, "landscape"),
        (True, True, [{"filters": ".*", "title": "dummy_title"}], False, False, "unknown"),
        (True, False, [{"filters": ".*", "title": "dummy_title"}], False, False, "unknown"),
        (False, True, [{"filters": ".*", "title": "dummy_title"}], False, False, "unknown"),
        (False, False, [{"filters": ".*", "title": "dummy_title"}], False, False, "unknown"),
        (True, True, [{"no_filters": ".*", "title": "dummy_title"}], True, False, "unknown"),
        (True, True, [{"filters": ".*", "title": "dummy_title"}], False, True, "unknown"),
        (True, False, [{"filters": ".*", "title": "dummy_title"}], False, True, "unknown"),
        (False, True, [{"filters": ".*", "title": "dummy_title"}], False, True, "unknown"),
        (False, False, [{"filters": ".*", "title": "dummy_title"}], False, True, "unknown"),
        (True, True, [{"no_filters": ".*", "title": "dummy_title"}], True, True, "unknown"),
    ],
)
def test_save_results(
    mocker: MockerFixture,
    mock_output_manager: OutputManager,
    exclude_info_maps: bool,
    produce_graphics: bool,
    filter_content: List[Dict[str, str]],
    is_faulty: bool,
    chunkification: bool,
    direction: str,
) -> None:
    # Arrange
    filters_path = Path("filters_path")
    csvs_dir = Path("output/CSVs/")
    jsons_dir = Path("output/JSONs/")
    reports_dir = Path("output/reports/")
    graphics_dir = Path("outputs/graphics_dir")
    mock_output_manager.variables_pool = {}
    mocker.patch.object(mock_output_manager, "generate_file_name", return_value="dummy_name")
    mocker.patch.object(mock_output_manager, "_load_filter_file_content", return_value=(filter_content, direction))
    filter_files = ["csv_input_filepath1.txt", "graph_input_filepath2.txt", "json_input_filepath3.txt"]
    mocker.patch.object(mock_output_manager, "_list_filter_files_in_dir", return_value=filter_files)
    mock_exclude_info_maps = mocker.patch.object(mock_output_manager, "_exclude_info_maps", return_value={})
    route_save_functions = mocker.patch.object(mock_output_manager, "_route_save_functions")
    add_error = mocker.patch.object(mock_output_manager, "add_error")
    mocker.patch.object(mock_output_manager, "time")
    mock_output_manager.chunkification = chunkification
    mock_save_current_variable_pool = mocker.patch.object(mock_output_manager, "_save_current_variable_pool")
    mock_load_saved_pools = mocker.patch.object(mock_output_manager, "load_saved_pools", return_value={})

    # Act
    mock_output_manager.save_results(
        filters_path, exclude_info_maps, produce_graphics, reports_dir, graphics_dir, csvs_dir, jsons_dir
    )

    # Assert
    if is_faulty:
        mock_exclude_info_maps.assert_not_called()
        route_save_functions.assert_not_called()
        assert add_error.call_count == len(filter_files)
    else:
        add_error.assert_not_called()
        if exclude_info_maps:
            mock_exclude_info_maps.assert_has_calls([call({}), call({}), call({})])
        else:
            mock_exclude_info_maps.assert_not_called()
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
                    direction,
                )
                for file_name in filter_files
            ]
        )
        if chunkification:
            mock_save_current_variable_pool.assert_called_once()
            mock_load_saved_pools.assert_called()


@pytest.mark.parametrize(
    "exclude_info_maps, produce_graphics, filter_contents, is_faulty, warn_on_conflict, direction",
    [
        (True, True, [{"filters": ".*", "title": "dummy_title"}], False, False, "portrait"),
        (True, False, [{"filters": ".*", "title": "dummy_title"}], False, False, "portrait"),
        (False, True, [{"filters": ".*", "title": "dummy_title"}], False, False, "portrait"),
        (False, False, [{"filters": ".*", "title": "dummy_title"}], False, False, "portrait"),
        (True, True, [{"no_filters": ".*", "title": "dummy_title"}], True, False, "portrait"),
        (
            True,
            True,
            [{"filters": ".*", "title": "dummy_title", "graph_details": {"type": "plot"}}],
            False,
            False,
            "portrait",
        ),
        (
            True,
            True,
            [{"filters": ".*", "title": "dummy_title", "cross_references": "dummy_ref"}],
            False,
            False,
            "portrait",
        ),
        (
            True,
            True,
            [{"filters": ".*", "title": "dummy_title", "data_significant_digits": 8}],
            False,
            False,
            "portrait",
        ),
        (
            True,
            True,
            [{"filters": ".*", "title": "dummy_title", "cross_references": "dummy_ref", "data_significant_digits": 8}],
            False,
            True,
            "portrait",
        ),
        (True, True, [{"filters": ".*", "title": "dummy_title"}], False, False, "landscape"),
        (True, False, [{"filters": ".*", "title": "dummy_title"}], False, False, "landscape"),
        (False, True, [{"filters": ".*", "title": "dummy_title"}], False, False, "landscape"),
        (False, False, [{"filters": ".*", "title": "dummy_title"}], False, False, "landscape"),
        (True, True, [{"no_filters": ".*", "title": "dummy_title"}], True, False, "landscape"),
        (
            True,
            True,
            [{"filters": ".*", "title": "dummy_title", "graph_details": {"type": "plot"}}],
            False,
            False,
            "landscape",
        ),
        (
            True,
            True,
            [{"filters": ".*", "title": "dummy_title", "cross_references": "dummy_ref"}],
            False,
            False,
            "landscape",
        ),
        (
            True,
            True,
            [{"filters": ".*", "title": "dummy_title", "data_significant_digits": 8}],
            False,
            False,
            "landscape",
        ),
        (
            True,
            True,
            [{"filters": ".*", "title": "dummy_title", "cross_references": "dummy_ref", "data_significant_digits": 8}],
            False,
            True,
            "landscape",
        ),
        (True, True, [{"filters": ".*", "title": "dummy_title"}], False, False, "unknown"),
        (True, False, [{"filters": ".*", "title": "dummy_title"}], False, False, "unknown"),
        (False, True, [{"filters": ".*", "title": "dummy_title"}], False, False, "unknown"),
        (False, False, [{"filters": ".*", "title": "dummy_title"}], False, False, "unknown"),
        (True, True, [{"no_filters": ".*", "title": "dummy_title"}], True, False, "unknown"),
        (
            True,
            True,
            [{"filters": ".*", "title": "dummy_title", "graph_details": {"type": "plot"}}],
            False,
            False,
            "unknown",
        ),
        (
            True,
            True,
            [{"filters": ".*", "title": "dummy_title", "cross_references": "dummy_ref"}],
            False,
            False,
            "unknown",
        ),
        (
            True,
            True,
            [{"filters": ".*", "title": "dummy_title", "data_significant_digits": 8}],
            False,
            False,
            "unknown",
        ),
        (
            True,
            True,
            [{"filters": ".*", "title": "dummy_title", "cross_references": "dummy_ref", "data_significant_digits": 8}],
            False,
            True,
            "unknown",
        ),
    ],
)
def test_save_results_report_generation(
    mock_output_manager: OutputManager,
    exclude_info_maps: bool,
    produce_graphics: bool,
    filter_contents: List[Dict[str, str]],
    is_faulty: bool,
    warn_on_conflict: bool,
    direction: str,
    mocker: MockerFixture,
) -> None:
    # Arrange
    filters_path = Path("filters_path")
    csvs_dir = Path("output/CSVs/")
    jsons_dir = Path("output/JSONs/")
    reports_dir = Path("output/reports/")
    graphics_dir = Path("outputs/graphics_dir")
    mock_output_manager.variables_pool = {}
    mock_output_manager.chunkification = False
    mocker.patch.object(mock_output_manager, "generate_file_name", return_value="dummy_name")
    mocker.patch.object(mock_output_manager, "_load_filter_file_content", return_value=(filter_contents, direction))
    mocker.patch.object(
        mock_output_manager,
        "_list_filter_files_in_dir",
        return_value=[
            "report_input_filepath1.txt",
            "report_input_filepath2.txt",
        ],
    )
    mocker.patch.object(mock_output_manager, "_exclude_info_maps", return_value={})
    mock_dict_to_file_csv = mocker.patch.object(mock_output_manager, "_dict_to_file_csv")
    mocker.patch.object(mock_output_manager, "add_error")
    mocker.patch.object(mock_output_manager, "route_logs", return_value=None)
    mock_output_manager.set_metadata_prefix("test_prefix")
    mocker.patch.object(mock_output_manager, "create_directory")
    mock_add_warning = mocker.patch.object(mock_output_manager, "add_warning")

    with patch("RUFAS.output_manager.ReportGenerator") as mock_report_generator_class:
        mock_report_generator = mock_report_generator_class.return_value
        mock_report_generator.generate_report = MagicMock()
        mock_report_generator.reports = {"dummy_report": "data"}

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
            assert mock_dict_to_file_csv.call_count == len(mock_output_manager._list_filter_files_in_dir.return_value)

        if not is_faulty and any("graph_details" in content for content in filter_contents):
            for content in filter_contents:
                if "graph_details" in content:
                    assert "graphics_dir" in content["graph_details"]
                    assert content["graph_details"]["graphics_dir"] == graphics_dir
                    assert content["graph_details"]["metadata_prefix"] == "test_prefix"

        expected_warning_count = 0
        if warn_on_conflict:
            expected_warning_count = 2

        assert mock_add_warning.call_count == expected_warning_count


@pytest.mark.parametrize("direction", ["portrait", "landscape", "unknown"])
def test_route_save_functions_csv_with_rounding(
    direction: str,
    mocker: MockerFixture,
    mock_output_manager: OutputManager,
) -> None:
    # Arrange
    dict_to_file_csv = mocker.patch.object(mock_output_manager, "_dict_to_file_csv")
    mock_add_log = mocker.patch.object(mock_output_manager, "add_log")
    mock_create_dir = mocker.patch.object(mock_output_manager, "create_directory")
    round_numeric_values_in_dict = mocker.patch(
        "RUFAS.util.Utility.round_numeric_values_in_dict", side_effect=lambda x, y: x
    )

    filtered_pool = {"key": {"var": 123.456789}}
    filter_content = {
        "filters": "regex",
        "data_significant_digits": 3,
    }

    # Act
    mock_output_manager._route_save_functions(
        "csv_file",
        filtered_pool,
        True,
        filter_content,
        Path("json_dir"),
        Path("graphics_dir"),
        Path("output/CSVs/"),
        direction,
    )

    # Assert
    round_numeric_values_in_dict.assert_called_once_with({"var": 123.456789}, 3)
    variable_csv_file_path = mock_output_manager.generate_file_name("saved_variables_csv_file", "csv")
    dict_to_file_csv.assert_called_once_with(
        {"key": {"var": 123.456789}}, Path("output", "CSVs", variable_csv_file_path), direction
    )
    mock_add_log.assert_called_once_with(
        "Rounding Values",
        "Rounded values to 3 significant digits",
        {
            "class": mock_output_manager.__class__.__name__,
            "function": "_route_save_functions",
        },
    )
    mock_create_dir.assert_called_once_with(Path("output", "CSVs"))


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
        filter_file, filtered_pool, produce_graphics, filter_content, jsons_dir, graphics_dir, csvs_dir, "portrait"
    )

    # Assert
    patch_create_directory.assert_called_once_with(jsons_dir)
    patch_for_save_to_json.assert_called_once_with(filter_file, jsons_dir, filtered_pool, filter_content)


def test_route_save_functions_comparison(mocker: MockerFixture) -> None:
    """Unit test for the _route_save_functions() method in the OutputManager
    class with an e2e comparison filter file."""
    # Arrange
    output_manager = OutputManager()
    output_manager.is_first_post_processing = False
    mocker.patch.object(
        type(output_manager), "_filter_prefixes", new_callable=PropertyMock, return_value={"comparison": "comparison_"}
    )
    patch_create_directory = mocker.patch.object(output_manager, "create_directory")
    patch_for_save_to_json = mocker.patch.object(output_manager, "_save_to_json")
    filter_file = "comparison_file"
    json_dir = Path("json_dir")
    filtered_pool = {"key": {"var": "value"}}
    produce_graphics = True
    filter_content = {"filters": "regex"}
    graphics_dir = Path("graphics_dir")
    csv_dir = Path("csvs_dir")

    # Act
    output_manager._route_save_functions(
        filter_file, filtered_pool, produce_graphics, filter_content, json_dir, graphics_dir, csv_dir, "portrait"
    )

    # Assert
    patch_create_directory.assert_called_once_with(json_dir)
    patch_for_save_to_json.assert_called_once_with(filter_file, json_dir, filtered_pool, filter_content)


@pytest.mark.parametrize(
    "filter_content, filter_file_extension, filter_file_prefix, expected_filename",
    [
        # Name provided without .json
        ({"name": "test_name"}, ".json", "", "saved_variables_test_name.json"),
        # No name provided, but filter_file ends with .json
        ({}, ".json", "", "saved_variables_filter_file_with_millis.json"),
        # No name, filter_file does not end with .json
        ({}, ".txt", "", "saved_variables_filter_file.json"),
        # Filter file contains 'e2e_comparison', with name in filter_content
        ({"name": "comparison_test"}, ".json", "e2e_comparison", "comparison_comparison_test.json"),
    ],
)
def test_save_to_json(
    mocker: MockerFixture,
    tmp_path: Path,
    filter_content: Dict[str, Union[str, int]],
    filter_file_extension: str,
    filter_file_prefix: str,
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
    filter_file = f"{filter_file_prefix}_filter_file{filter_file_extension}"
    save_path = tmp_path  # Using pytest's tmp_path fixture
    filtered_pool = {"key": "value"}

    # Act
    output_manager._save_to_json(filter_file, save_path, filtered_pool, filter_content)

    # Assert
    if "e2e_comparison" in filter_file:
        base_name = f"comparison_{filter_content['name']}"
    else:
        base_name = (
            f"saved_variables_{filter_content['name']}"
            if "name" in filter_content
            else f"saved_variables_{filter_file}"
        )

    patch_for_generate_file_name.assert_called_once_with(base_name, "json")
    patch_for_dict_to_file_json.assert_called_once_with(
        filtered_pool, save_path / expected_filename, origin_label=OriginLabel.NONE
    )


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
    mocker.patch.object(mock_output_manager, "route_logs", return_value=True)
    graph_data = {"filters": ".*", "other keys": "other values"}

    mock_output_manager._route_save_functions(
        "graph_file",
        {"key": [1, 2, 3, 4]},
        False,
        graph_data,
        Path("jsons_dir"),
        Path("graphics_dir"),
        Path("csvs_dir"),
        "portrait",
    )

    mock_generate_graph.assert_not_called()
    mock_create_directory.assert_called_with(Path("graphics_dir"))
    add_warning.assert_called_once_with(
        "No Graphics",
        "Graphic generation is disabled, skipping filter_file='graph_file'",
        {"class": "OutputManager", "function": "_route_save_functions"},
    )

    mock_output_manager._route_save_functions(
        "graph_file",
        {"key": [1, 2, 3, 4]},
        True,
        graph_data,
        Path("jsons_dir"),
        Path("graphics_dir"),
        Path("csvs_dir"),
        "portrait",
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
        "graph_file",
        {"key": [1, 2, 3, 4]},
        True,
        graph_data,
        Path("jsons_dir"),
        Path("graphics_dir"),
        Path("csvs_dir"),
        "portrait",
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
    log_pool: list[dict[str, str | dict[str, str]]], expected_calls: dict[str, int], mocker: MockerFixture
) -> None:
    output_manager = OutputManager()

    mocked_add_error = mocker.patch.object(output_manager, "add_error")
    mocked_add_log = mocker.patch.object(output_manager, "add_log")
    mocked_add_warning = mocker.patch.object(output_manager, "add_warning")

    output_manager.route_logs(log_pool)

    assert mocked_add_error.call_count == expected_calls["add_error"]
    assert mocked_add_log.call_count == expected_calls["add_log"]
    assert mocked_add_warning.call_count == expected_calls["add_warning"]


@pytest.mark.parametrize(
    "log_pool, expected_calls",
    [
        (
            [
                {
                    "wrong key": "info_log",
                    "message": "Info message",
                    "info_map": {"class": "GraphGenerator", "function": "prepare_plot_data"},
                },
                {
                    "warning": "warning_type",
                    "message": "Warning message",
                    "info_map": {"class": "GraphGenerator", "function": "prepare_plot_data"},
                },
            ],
            {"add_error": 0, "add_log": 0, "add_warning": 2},
        ),
        (
            [
                {
                    "error": "info_log",
                    "massage": "Info message",
                    "info_map": {"class": "GraphGenerator", "function": "prepare_plot_data"},
                },
                {
                    "warning": "warning_type",
                    "message": "Warning message",
                    "info_map": {"class": "GraphGenerator", "function": "prepare_plot_data"},
                },
            ],
            {"add_error": 1, "add_log": 0, "add_warning": 1},
        ),
        (
            [
                {
                    "wrong key": "info_log",
                    "message": "Info message",
                    "info_map": {"class": "GraphGenerator", "function": "prepare_plot_data"},
                },
                {
                    "warning": "warning_type",
                    "message": 2,
                    "info_map": {"class": "GraphGenerator", "function": "prepare_plot_data"},
                },
            ],
            {"add_error": 0, "add_log": 0, "add_warning": 2},
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
                    "message": 3,
                    "info_map": {"class": "GraphGenerator", "function": "prepare_plot_data"},
                },
            ],
            {"add_error": 1, "add_log": 0, "add_warning": 1},
        ),
        (
            [
                {
                    "error": "error_type",
                    "message": 3,
                    "info_map": {"class": "GraphGenerator", "function": "prepare_plot_data"},
                },
                {
                    "log": "info_log",
                    "message": 3,
                    "info_map": {"class": "GraphGenerator", "function": "prepare_plot_data"},
                },
            ],
            {"add_error": 0, "add_log": 0, "add_warning": 2},
        ),
    ],
)
def test_route_logs_mismatch(
    log_pool: dict[str, str | dict[str, str]], expected_calls: dict[str, int], mocker: MockerFixture
) -> None:
    output_manager = OutputManager()

    mocked_add_error = mocker.patch.object(output_manager, "add_error")
    mocked_add_log = mocker.patch.object(output_manager, "add_log")
    mocked_add_warning = mocker.patch.object(output_manager, "add_warning")

    output_manager.route_logs(log_pool)

    assert mocked_add_error.call_count == expected_calls["add_error"]
    assert mocked_add_log.call_count == expected_calls["add_log"]
    assert mocked_add_warning.call_count == expected_calls["add_warning"]


def test_load_variables_pool_from_file_valid_path(
    mock_output_manager: OutputManager,
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


@patch("builtins.open", new_callable=mock_open)
def test_load_variables_pool_from_file_raises_exception(
    mock_file: MagicMock,
    mock_output_manager: OutputManager,
) -> None:
    """Checks that load_variables_pool_from_file raises exceptions with a bad filepath provided"""
    mock_output_manager.variables_pool = {}
    mock_file.side_effect = FileNotFoundError
    with pytest.raises(FileNotFoundError):
        mock_output_manager.load_variables_pool_from_file(Path("bad/file/path"))
    assert mock_output_manager.variables_pool == {}

    mock_file.return_value.read.return_value = "this is not valid JSON"
    with patch("builtins.open", mock_open(read_data="bad/file/path")):
        with pytest.raises(json.JSONDecodeError):
            mock_output_manager.load_variables_pool_from_file(Path("bad/file/path.json"))
    assert mock_output_manager.variables_pool == {}


@pytest.mark.parametrize(
    "is_file_found_in_dir",
    [True, False],
)
def test_clear_output_dir(
    mocker: MockerFixture,
    mock_output_manager: OutputManager,
    is_file_found_in_dir: bool,
) -> None:
    """Checks clear_output_dir function in output_manager.py"""
    # Arrange
    mock_empty_dir = mocker.patch("RUFAS.util.Utility.empty_dir")
    mock_add_log = mocker.patch.object(mock_output_manager, "add_log")
    mock_add_error = mocker.patch.object(mock_output_manager, "add_error")
    mock_is_file_in_dir = mocker.patch.object(mock_output_manager, "is_file_in_dir", return_value=is_file_found_in_dir)
    mock_mkdir = mocker.patch("pathlib.Path.mkdir", return_value=Path("dummy_path"))

    # Act
    vars_file_path = mock_mkdir.return_value / "dummy_vars_file.txt"
    mock_output_manager.clear_output_dir(vars_file_path, Path("output_dir"))

    # Assert
    if is_file_found_in_dir:
        mock_empty_dir.assert_not_called()
        mock_add_log.assert_not_called()
        mock_add_error.assert_called_once()
    else:
        mock_empty_dir.assert_called_once_with(Path("output_dir"), keep=[".keep", "output_filters"])
        mock_add_log.assert_called_once()
        mock_add_error.assert_not_called()

    mock_is_file_in_dir.assert_called_once_with(Path("output_dir"), vars_file_path)


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
    mock_output_manager: OutputManager, dir_path: Path, file_path: Path, expected_result: bool
) -> None:
    """Checks is_file_in_dir function in output_manager.py"""
    assert mock_output_manager.is_file_in_dir(dir_path, file_path) is expected_result


def test_create_directory_successful(mocker: MockerFixture, mock_output_manager: OutputManager) -> None:
    """Checks create_directory function successfully creates a directory in output_manager.py"""
    # Arrange
    mock_add_log = mocker.patch.object(mock_output_manager, "add_log")
    mock_add_error = mocker.patch.object(mock_output_manager, "add_error")
    mock_mkdir = mocker.patch.object(Path, "mkdir")

    test_path = Path("/test/directory")

    # Act
    mock_output_manager.create_directory(test_path)

    # Assert
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    assert mock_add_log.call_count == 2
    mock_add_error.assert_not_called()


@pytest.mark.parametrize(
    "exception_to_raise",
    [PermissionError, Exception],
)
def test_create_directory_exceptions(
    mocker: MockerFixture,
    mock_output_manager: OutputManager,
    exception_to_raise: Exception,
) -> None:
    """Checks create_directory function handles exceptions properly"""
    # Arrange
    mock_add_log = mocker.patch.object(mock_output_manager, "add_log")
    mock_add_error = mocker.patch.object(mock_output_manager, "add_error")
    mock_mkdir = mocker.patch("pathlib.Path.mkdir", side_effect=exception_to_raise)

    # Act
    mock_output_manager.create_directory(Path("unauthorized/path/"))

    # Assert
    mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
    assert mock_add_log.call_count == 1
    assert mock_add_error.call_count == 1


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
    errors_pool: dict[str, dict[str, list[Any]]],
    warnings_pool: dict[str, dict[str, list[Any]]],
    logs_pool: dict[str, dict[str, list[Any]]],
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
            f"RuFaS: Ruminant Farm Systems Model. Version: v\n{DISCLAIMER_MESSAGE}\n",
        ),
        (
            LogVerbosity.ERRORS,
            f"RuFaS: Ruminant Farm Systems Model. Version: v\n{DISCLAIMER_MESSAGE}\n",
        ),
        (
            LogVerbosity.WARNINGS,
            f"RuFaS: Ruminant Farm Systems Model. Version: v\n{DISCLAIMER_MESSAGE}\n",
        ),
        (
            LogVerbosity.LOGS,
            f"RuFaS: Ruminant Farm Systems Model. Version: v\n{DISCLAIMER_MESSAGE}\n",
        ),
    ],
)
def test_print_credits(
    mock_output_manager: OutputManager, log_verbose: LogVerbosity, expected_output: str, capfd: CaptureFixture[str]
) -> None:
    """
    Unit test for the print_credits() method in OutputManager class.
    """
    mock_output_manager._OutputManager__log_verbose = log_verbose
    version = "v"
    mock_output_manager.print_credits(version)

    captured = capfd.readouterr()
    assert captured.out == expected_output


@pytest.mark.parametrize(
    "log_verbose, task_id, expected_output",
    [
        (LogVerbosity.NONE, "id", ""),
        (LogVerbosity.CREDITS, "id", "Starting task: id\n"),
        (LogVerbosity.ERRORS, "id", "Starting task: id\n"),
        (LogVerbosity.WARNINGS, "id", "Starting task: id\n"),
        (LogVerbosity.LOGS, "id", "Starting task: id\n"),
    ],
)
def test_print_task_id(
    mock_output_manager: OutputManager,
    log_verbose: LogVerbosity,
    task_id: str,
    expected_output: str,
    capfd: CaptureFixture[str],
) -> None:
    """
    Unit test for the print_task_id() method in OutputManager class.
    """
    mock_output_manager._OutputManager__log_verbose = log_verbose
    mock_output_manager.print_task_id(task_id)
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
    mock_output_manager: OutputManager, log_verbose: LogVerbosity, expected_output: str, capfd: CaptureFixture[str]
) -> None:
    mock_output_manager._OutputManager__log_verbose = log_verbose
    task_id = "id"
    with patch.object(OutputManager, "_get_errors_warnings_logs_counts", return_value=(2, 1, 5)):
        mock_output_manager.print_errors_warnings_logs_counts(task_id)
        captured = capfd.readouterr()
        assert captured.out == expected_output


def test_summarize_e2e_test_results_good_path(
    tmp_path: Path, mock_output_manager: OutputManager, mocker: MockerFixture
) -> None:
    """Unit test for the summarize_e2e_test_results() method in OutputManager class."""
    mock_print = mocker.patch.object(mock_output_manager, "_print_e2e_results_summary")

    data = {
        "Animal.something": {"values": [True]},
        "crop_and_soil.other": {"values": [False]},
        "DISCLAIMER": "ignored",
    }
    (tmp_path / "E2E_Animal_comparison.json").write_text(json.dumps(data))
    (tmp_path / "E2E_Animal_notes.json").write_text("{}")
    (tmp_path / "E2E_Animal_comparison.txt").write_text("text")
    mock_add_log = mocker.patch.object(mock_output_manager, "add_log")
    mock_add_error = mocker.patch.object(mock_output_manager, "add_error")

    mock_output_manager.summarize_e2e_test_results(tmp_path, ["E2E_Animal"])

    info_map = {"class": OutputManager.__name__, "function": OutputManager.summarize_e2e_test_results.__name__}
    expected_add_log_calls = [
        call(
            "Attempting to open e2e test results directory",
            "Opening e2e test results directory to read results files",
            info_map,
        ),
        call(
            "Successfully opened e2e test results directory", "Directory opened and files successfully read", info_map
        ),
    ]
    mock_add_log.assert_has_calls(expected_add_log_calls)

    mock_add_error.assert_not_called()

    mock_print.assert_called_once()
    (summary_arg,) = mock_print.call_args.args
    assert summary_arg == {"E2E_Animal": {"Animal": True, "CropAndSoil": False, "Manure": "n/a"}}


def test_summarize_e2e_test_results_invalid_prefix_logs_error(
    tmp_path: Path, mock_output_manager: OutputManager, mocker: MockerFixture
) -> None:
    """Unit test for the summarize_e2e_test_results() method in OutputManager class with no matching prefix."""
    mock_print = mocker.patch.object(mock_output_manager, "_print_e2e_results_summary")

    (tmp_path / "NoMatch_comparison.json").write_text(json.dumps({"Animal.something": {"values": [True]}}))
    mock_add_error = mocker.patch.object(mock_output_manager, "add_error")

    mock_output_manager.summarize_e2e_test_results(tmp_path, ["E2E_Animal"])

    mock_add_error.assert_any_call(
        "Invalid e2e output prefix",
        pytest.helpers.contains("NoMatch_comparison.json") if hasattr(pytest, "helpers") else ANY,
        ANY,
    )

    mock_print.assert_called_once()
    (summary_arg,) = mock_print.call_args.args
    assert summary_arg == {"E2E_Animal": {"Animal": "n/a", "CropAndSoil": "n/a", "Manure": "n/a"}}


def test_summarize_e2e_test_results_file_read_error(
    tmp_path: Path, mock_output_manager: OutputManager, mocker: MockerFixture
) -> None:
    """Unit test for the summarize_e2e_test_results() method in OutputManager class with a file read error."""
    mock_print = mocker.patch.object(mock_output_manager, "_print_e2e_results_summary")

    bad_path = tmp_path / "E2E_Animal_comparison.json"
    bad_path.mkdir()
    mock_add_error = mocker.patch.object(mock_output_manager, "add_error")

    mock_output_manager.summarize_e2e_test_results(tmp_path, ["E2E_Animal"])

    mock_add_error.assert_any_call(
        "File path invalid.",
        ANY,
        ANY,
    )

    mock_print.assert_called_once()
    (summary_arg,) = mock_print.call_args.args
    assert summary_arg == {"E2E_Animal": {"Animal": "n/a", "CropAndSoil": "n/a", "Manure": "n/a"}}


def test__print_e2e_results_summary_formats_output(
    capsys: CaptureFixture[str], mock_output_manager: OutputManager, mocker: MockerFixture
) -> None:
    """Unit test for the _print_e2e_results_summary() method in OutputManager class."""
    summary = {
        "E2E_Animal": {
            "Animal": True,
            "CropAndSoil": False,
            "Manure": "n/a",
        }
    }

    OutputManager._print_e2e_results_summary(mock_output_manager, summary)

    out = capsys.readouterr().out
    expected = (
        "Summary of e2e results:\n\n"
        "E2E_Animal results:\n"
        "  Animal: Passing\n"
        "  CropAndSoil: Failing\n"
        "  Manure: n/a\n"
        "\n"
    )
    assert out == expected


@pytest.mark.parametrize(
    "key, expected",
    [
        ("Animal.foo", "Animal"),
        ("crop_and_soil.bar", "CropAndSoil"),
        ("manure.moo", "Manure"),
        ("Other.stuff", "Other"),
        ("weirdkey", "weirdkey"),
    ],
)
def test__normalize_module_header(key: str, expected: str) -> None:
    assert OutputManager._normalize_module_header(key) == expected


@pytest.mark.parametrize(
    "input_data, origin_label, expected",
    [
        # Basic test case with a single data_origin per value and origin_label=TRUE_AND_REPORT_ORIGINS
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
            OriginLabel.TRUE_AND_REPORT_ORIGINS,
            {
                "ModuleA.variable_x": {
                    "info_maps": [
                        {"data_origin": [["SourceClassA", "method_a"]], "units": MeasurementUnits.UNITLESS.value},
                        {"data_origin": [["SourceClassA", "method_a"]], "units": MeasurementUnits.UNITLESS.value},
                    ],
                    "values": [10, 20],
                    "detailed_values": [
                        "[SourceClassA.method_a]->[ModuleA.variable_x]: 10 (unitless)",
                        "[SourceClassA.method_a]->[ModuleA.variable_x]: 20 (unitless)",
                    ],
                }
            },
        ),
        # Test case with a single data_origin per value and origin_label=TRUE_ORIGIN
        (
            {
                "ModuleB.variable_y": {
                    "info_maps": [
                        {"data_origin": [["SourceClassB", "method_b"]], "units": MeasurementUnits.MILLIMETERS.value},
                        {"data_origin": [["SourceClassB", "method_b"]], "units": MeasurementUnits.MILLIMETERS.value},
                    ],
                    "values": [30, 40],
                }
            },
            OriginLabel.TRUE_ORIGIN,
            {
                "ModuleB.variable_y": {
                    "info_maps": [
                        {"data_origin": [["SourceClassB", "method_b"]], "units": MeasurementUnits.MILLIMETERS.value},
                        {"data_origin": [["SourceClassB", "method_b"]], "units": MeasurementUnits.MILLIMETERS.value},
                    ],
                    "values": [30, 40],
                    "detailed_values": [
                        "[SourceClassB.method_b]: 30 (mm)",
                        "[SourceClassB.method_b]: 40 (mm)",
                    ],
                }
            },
        ),
        # Test case with a single data_origin per value and origin_label=REPORT_ORIGIN
        (
            {
                "ModuleC.variable_z": {
                    "info_maps": [
                        {
                            "data_origin": [["SourceClassC", "method_c"]],
                            "units": MeasurementUnits.DEGREES_CELSIUS.value,
                        },
                        {
                            "data_origin": [["SourceClassC", "method_c"]],
                            "units": MeasurementUnits.DEGREES_CELSIUS.value,
                        },
                    ],
                    "values": [25.5, 26.1],
                }
            },
            OriginLabel.REPORT_ORIGIN,
            {
                "ModuleC.variable_z": {
                    "info_maps": [
                        {
                            "data_origin": [["SourceClassC", "method_c"]],
                            "units": MeasurementUnits.DEGREES_CELSIUS.value,
                        },
                        {
                            "data_origin": [["SourceClassC", "method_c"]],
                            "units": MeasurementUnits.DEGREES_CELSIUS.value,
                        },
                    ],
                    "values": [25.5, 26.1],
                    "detailed_values": [
                        "[ModuleC.variable_z]: 25.5 (°C)",
                        "[ModuleC.variable_z]: 26.1 (°C)",
                    ],
                }
            },
        ),
        # Test case with a single data_origin per value and origin_label=NONE
        (
            {
                "ModuleD.variable_w": {
                    "info_maps": [
                        {"data_origin": [["SourceClassD", "method_d"]], "units": MeasurementUnits.METERS.value},
                        {"data_origin": [["SourceClassD", "method_d"]], "units": MeasurementUnits.METERS.value},
                    ],
                    "values": [1.5, 2.0],
                }
            },
            OriginLabel.NONE,
            {
                "ModuleD.variable_w": {
                    "info_maps": [
                        {"data_origin": [["SourceClassD", "method_d"]], "units": "m"},
                        {"data_origin": [["SourceClassD", "method_d"]], "units": "m"},
                    ],
                    "values": [1.5, 2.0],
                }
            },
        ),
        # Test case with dictionary values and origin_label=TRUE_AND_REPORT_ORIGINS
        (
            {
                "ModuleE.variable_dict": {
                    "info_maps": [
                        {"data_origin": [["SourceClassE", "method_e"]], "units": {"key1": "unit1", "key2": "unit2"}},
                        {"data_origin": [["SourceClassE", "method_e"]], "units": {"key1": "unit1", "key2": "unit2"}},
                    ],
                    "values": [{"key1": 10, "key2": 20}, {"key1": 30, "key2": 40}],
                }
            },
            OriginLabel.TRUE_AND_REPORT_ORIGINS,
            {
                "ModuleE.variable_dict": {
                    "info_maps": [
                        {"data_origin": [["SourceClassE", "method_e"]], "units": {"key1": "unit1", "key2": "unit2"}},
                        {"data_origin": [["SourceClassE", "method_e"]], "units": {"key1": "unit1", "key2": "unit2"}},
                    ],
                    "values": [{"key1": 10, "key2": 20}, {"key1": 30, "key2": 40}],
                    "detailed_values": [
                        "[SourceClassE.method_e]->[ModuleE.variable_dict]: key1 = 10 (unit1), key2 = 20 (unit2)",
                        "[SourceClassE.method_e]->[ModuleE.variable_dict]: key1 = 30 (unit1), key2 = 40 (unit2)",
                    ],
                }
            },
        ),
        # Test case with missing data_origin and units
        (
            {
                "ModuleF.missing_data_origin_units": {
                    "info_maps": [
                        {"other_key": "other_value"},
                        {"other_key": "other_value"},
                    ],
                    "values": [50, 60],
                }
            },
            OriginLabel.TRUE_AND_REPORT_ORIGINS,
            {
                "ModuleF.missing_data_origin_units": {
                    "info_maps": [
                        {"other_key": "other_value"},
                        {"other_key": "other_value"},
                    ],
                    "values": [50, 60],
                }
            },
        ),
        # Test case with mismatched lengths of data_origins, units, and values
        (
            {
                "ModuleG.mismatched_lengths": {
                    "info_maps": [
                        {"data_origin": [["SourceClassG", "method_g"]], "units": MeasurementUnits.DAYS.value},
                    ],
                    "values": [70, 80],
                }
            },
            OriginLabel.TRUE_AND_REPORT_ORIGINS,
            {
                "ModuleG.mismatched_lengths": {
                    "info_maps": [
                        {"data_origin": [["SourceClassG", "method_g"]], "units": MeasurementUnits.DAYS.value},
                    ],
                    "values": [70, 80],
                }
            },
        ),
        # Test case where one of the info_maps is missing the "units" key
        (
            {
                "ModuleH.missing_units": {
                    "info_maps": [
                        {"data_origin": [["SourceClassH", "method_h"]]},
                        {"data_origin": [["SourceClassH", "method_h"]], "units": MeasurementUnits.KILOGRAMS.value},
                    ],
                    "values": [100, 200],
                }
            },
            OriginLabel.TRUE_AND_REPORT_ORIGINS,
            {
                "ModuleH.missing_units": {
                    "info_maps": [
                        {"data_origin": [["SourceClassH", "method_h"]]},
                        {"data_origin": [["SourceClassH", "method_h"]], "units": MeasurementUnits.KILOGRAMS.value},
                    ],
                    "values": [100, 200],
                }
            },
        ),
    ],
)
def test_add_detailed_values(
    input_data: dict[str, Any],
    origin_label: OriginLabel,
    expected: dict[str, Any],
) -> None:
    """
    Unit test for the _add_detailed_values() method in OutputManager class.
    """

    # Arrange
    output_manager = OutputManager()

    # Act
    result = output_manager._add_detailed_values(input_data, origin_label)

    # Assert
    assert result == expected


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
        # Case 6: 'info_maps' is empty
        ({"info_maps": [], "values": [1]}, False),
        # Case 7: 'values' is empty
        ({"info_maps": [{"data_origin": "source"}], "values": []}, False),
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

    info_map = {"class": "OutputManager", "function": "_save_current_variable_pool"}

    dummy_saved_pool_chunks_num = 0
    dummy_variable_pool = {"a": 1, "b": "B", "c": True}

    output_manager.saved_pool_chunks_path = Path("dummy_path")
    output_manager.saved_pool_chunks_num = dummy_saved_pool_chunks_num
    output_manager.variables_pool = dummy_variable_pool
    output_manager.current_pool_size = 1024

    mock_generate_file_name = mocker.patch.object(output_manager, "generate_file_name", return_value="dummy_file.json")
    mock_dict_to_file_json = mocker.patch.object(output_manager, "dict_to_file_json")
    mock_add_log = mocker.patch.object(output_manager, "add_log")

    output_manager._save_current_variable_pool()

    mock_generate_file_name.assert_called_once_with(f"saved_pool_{dummy_saved_pool_chunks_num}", "json")

    dummy_file_path = Path.joinpath(output_manager.saved_pool_chunks_path, "dummy_file.json")
    mock_dict_to_file_json.assert_called_once_with(
        data_dict=dummy_variable_pool, path=dummy_file_path, minify_output_file=True
    )

    log_message = f"Saved the current variable pool to {dummy_file_path}"
    mock_add_log.assert_called_once_with("save_current_variable_pool", log_message, info_map)

    assert output_manager.variables_pool == {}
    assert output_manager.current_pool_size == sys.getsizeof(output_manager.variables_pool.__repr__())
    assert output_manager.saved_pool_chunks_num == 1


def test_sort_saved_chunk_files(mock_output_manager: OutputManager, tmpdir) -> None:
    tmpdir.join("saved_pool_1_dummy_timestamp.json").write("File 1 content")
    tmpdir.join("saved_pool_0_dummy_timestamp.json").write("File 0 content")
    tmpdir.join("saved_pool_3_dummy_timestamp.json").write("File 3 content")
    tmpdir.join("saved_pool_2_dummy_timestamp.txt").write("File 2 content")

    mock_output_manager.saved_pool_chunks_path = Path(tmpdir)

    result = mock_output_manager._sort_saved_chunk_files()

    assert result == [
        tmpdir.join("saved_pool_0_dummy_timestamp.json"),
        tmpdir.join("saved_pool_1_dummy_timestamp.json"),
        tmpdir.join("saved_pool_3_dummy_timestamp.json"),
    ]


def test_load_saved_pools_pool_size_exceedance(
    mock_output_manager: OutputManager,
    mocker: MockerFixture,
) -> None:
    expected = {
        "a": {"values": [0, 1, 2, 3, 4, 5, 6, 7, 8], "info_maps": [{}, {}, {}, {}, {}, {}]},
        "b": {"values": ["a", "b", "c", "d", "e", "f"], "info_maps": [{}, {}, {}, {}, {}, {}]},
        "c": {"values": [True, True, True], "info_maps": [{}, {}, {}]},
        "d": {"values": [1.1, 2.2, 3.3], "info_maps": [{}, {}, {}]},
    }
    sorted_files = ["file1.json", "file2.json"]

    mocker.patch.object(mock_output_manager, "_sort_saved_chunk_files", return_value=sorted_files)
    mocker.patch.object(mock_output_manager, "load_variables_pool_from_file")

    mock_pools = {
        "file1.json": {
            "a": {"info_maps": [{}, {}], "values": [0, 1]},
            "b": {"info_maps": [{}, {}], "values": ["a", "b"]},
            "c": {"info_maps": [{}], "values": [True]},
        },
        "file2.json": {
            "a": {"info_maps": [{}, {}, {}, {}], "values": [2, 3, 4, 5, 6, 7, 8]},
            "b": {"info_maps": [{}, {}, {}, {}], "values": ["c", "d", "e", "f"]},
            "c": {"info_maps": [{}, {}], "values": [True, True]},
            "d": {"info_maps": [{}, {}, {}], "values": [1.1, 2.2, 3.3]},
        },
    }

    load_mock = mocker.patch.object(mock_output_manager, "load_variables_pool_from_file")
    load_mock.side_effect = lambda file: setattr(mock_output_manager, "variables_pool", mock_pools[file])

    mock_output_manager.load_saved_pools()

    assert mock_output_manager.variables_pool == expected


def test_run_startup_sequence_clear_output_directory(
    mock_output_manager: OutputManager,
    mocker: MockerFixture,
) -> None:
    mock_print_task_id = mocker.patch.object(mock_output_manager, "print_task_id")
    mock_flush_pools = mocker.patch.object(mock_output_manager, "flush_pools")
    mock_set_exclude_info_maps_flag = mocker.patch.object(mock_output_manager, "set_exclude_info_maps_flag")
    mock_set_log_verbose = mocker.patch.object(mock_output_manager, "set_log_verbose")
    mock_set_metadata_prefix = mocker.patch.object(mock_output_manager, "set_metadata_prefix")
    mock_create_directory = mocker.patch.object(mock_output_manager, "create_directory")
    mock_clear_output_dir = mocker.patch.object(mock_output_manager, "clear_output_dir")
    mock_setup_pool_overflow_control = mocker.patch.object(mock_output_manager, "setup_pool_overflow_control")

    dummy_verbosity: LogVerbosity = LogVerbosity.LOGS
    dummy_exclude_info_maps: bool = False
    dummy_output_directory: Path = Path("dummy/path")
    dummy_chunkification: bool = False
    dummy_max_memory_usage_percent: int = 80
    dummy_max_memory_usage: int = 0
    dummy_save_chunk_threshold_call_count: int = 0
    dummy_variables_file_path: Path = Path("dummy/path")
    dummy_output_prefix: str = "dummy_prefix"
    dummy_task_id: str = "dummy_task"
    is_e2e_run: bool = True

    mock_output_manager.run_startup_sequence(
        dummy_verbosity,
        dummy_exclude_info_maps,
        dummy_output_directory,
        True,
        dummy_chunkification,
        dummy_max_memory_usage_percent,
        dummy_max_memory_usage,
        dummy_save_chunk_threshold_call_count,
        dummy_variables_file_path,
        dummy_output_prefix,
        dummy_task_id,
        is_e2e_run,
    )

    mock_print_task_id.assert_called_once_with(dummy_task_id)
    mock_flush_pools.assert_called_once()
    mock_set_exclude_info_maps_flag.assert_called_once_with(dummy_exclude_info_maps)
    mock_set_log_verbose.assert_called_once_with(dummy_verbosity)
    mock_set_metadata_prefix.assert_called_once_with(dummy_output_prefix)
    mock_create_directory.assert_called_once_with(dummy_output_directory)
    mock_clear_output_dir.assert_called_once_with(dummy_variables_file_path, dummy_output_directory)
    mock_setup_pool_overflow_control.assert_not_called()
    assert mock_output_manager.is_end_to_end_testing_run == is_e2e_run


def test_run_startup_sequence_not_clear_output_directory(
    mock_output_manager: OutputManager,
    mocker: MockerFixture,
) -> None:
    mock_print_task_id = mocker.patch.object(mock_output_manager, "print_task_id")
    mock_flush_pools = mocker.patch.object(mock_output_manager, "flush_pools")
    mock_set_exclude_info_maps_flag = mocker.patch.object(mock_output_manager, "set_exclude_info_maps_flag")
    mock_set_log_verbose = mocker.patch.object(mock_output_manager, "set_log_verbose")
    mock_set_metadata_prefix = mocker.patch.object(mock_output_manager, "set_metadata_prefix")
    mock_create_directory = mocker.patch.object(mock_output_manager, "create_directory")
    mock_clear_output_dir = mocker.patch.object(mock_output_manager, "clear_output_dir")
    mock_setup_pool_overflow_control = mocker.patch.object(mock_output_manager, "setup_pool_overflow_control")

    dummy_verbosity: LogVerbosity = LogVerbosity.LOGS
    dummy_exclude_info_maps: bool = False
    dummy_output_directory: Path = Path("dummy/path")
    dummy_chunkification: bool = False
    dummy_max_memory_usage_percent: int = 80
    dummy_max_memory_usage: int = 0
    dummy_save_chunk_threshold_call_count: int = 0
    dummy_variables_file_path: Path = Path("dummy/path")
    dummy_output_prefix: str = "dummy_prefix"
    dummy_task_id: str = "dummy_task"
    is_e2e_run: bool = False

    mock_output_manager.run_startup_sequence(
        dummy_verbosity,
        dummy_exclude_info_maps,
        dummy_output_directory,
        False,
        dummy_chunkification,
        dummy_max_memory_usage_percent,
        dummy_max_memory_usage,
        dummy_save_chunk_threshold_call_count,
        dummy_variables_file_path,
        dummy_output_prefix,
        dummy_task_id,
        False,
    )

    mock_print_task_id.assert_called_once_with(dummy_task_id)
    mock_flush_pools.assert_called_once()
    mock_set_exclude_info_maps_flag.assert_called_once_with(dummy_exclude_info_maps)
    mock_set_log_verbose.assert_called_once_with(dummy_verbosity)
    mock_set_metadata_prefix.assert_called_once_with(dummy_output_prefix)
    mock_create_directory.assert_called_once_with(dummy_output_directory)
    mock_clear_output_dir.assert_not_called()
    assert mock_output_manager.is_end_to_end_testing_run == is_e2e_run
    mock_setup_pool_overflow_control.assert_not_called()


def test_run_startup_sequence_chunkification(
    mock_output_manager: OutputManager,
    mocker: MockerFixture,
) -> None:
    mock_print_task_id = mocker.patch.object(mock_output_manager, "print_task_id")
    mock_flush_pools = mocker.patch.object(mock_output_manager, "flush_pools")
    mock_set_exclude_info_maps_flag = mocker.patch.object(mock_output_manager, "set_exclude_info_maps_flag")
    mock_set_log_verbose = mocker.patch.object(mock_output_manager, "set_log_verbose")
    mock_set_metadata_prefix = mocker.patch.object(mock_output_manager, "set_metadata_prefix")
    mock_create_directory = mocker.patch.object(mock_output_manager, "create_directory")
    mock_clear_output_dir = mocker.patch.object(mock_output_manager, "clear_output_dir")
    mock_setup_pool_overflow_control = mocker.patch.object(mock_output_manager, "setup_pool_overflow_control")

    dummy_verbosity: LogVerbosity = LogVerbosity.LOGS
    dummy_exclude_info_maps: bool = False
    dummy_output_directory: Path = Path("dummy/path")
    dummy_chunkification: bool = True
    dummy_max_memory_usage_percent: int = 80
    dummy_max_memory_usage: int = 0
    dummy_save_chunk_threshold_call_count: int = 0
    dummy_variables_file_path: Path = Path("dummy/path")
    dummy_output_prefix: str = "dummy_prefix"
    dummy_task_id: str = "dummy_task"

    mock_output_manager.run_startup_sequence(
        dummy_verbosity,
        dummy_exclude_info_maps,
        dummy_output_directory,
        False,
        dummy_chunkification,
        dummy_max_memory_usage_percent,
        dummy_max_memory_usage,
        dummy_save_chunk_threshold_call_count,
        dummy_variables_file_path,
        dummy_output_prefix,
        dummy_task_id,
        False,
    )
    mock_print_task_id.assert_called_once_with(dummy_task_id)
    mock_flush_pools.assert_called_once()
    mock_set_exclude_info_maps_flag.assert_called_once_with(dummy_exclude_info_maps)
    mock_set_log_verbose.assert_called_once_with(dummy_verbosity)
    mock_set_metadata_prefix.assert_called_once_with(dummy_output_prefix)
    mock_create_directory.assert_called_once_with(dummy_output_directory)
    mock_clear_output_dir.assert_not_called()
    mock_setup_pool_overflow_control.assert_called_once_with(
        dummy_output_directory,
        dummy_max_memory_usage_percent,
        dummy_max_memory_usage,
        dummy_save_chunk_threshold_call_count,
    )


def test_setup_pool_overflow_control_user_define_save_chunk_threshold_call_count(
    mocker: MockerFixture, mock_output_manager: OutputManager
) -> None:
    """Tests setup_pool_overflow_control with a user-defined save_chunk_threshold_call_count."""
    # Arrange
    info_map = {"class": "OutputManager", "function": "setup_pool_overflow_control"}
    mock_output_manager.chunkification = False
    mock_output_manager.available_memory = 0
    mock_output_manager.saved_pool_chunks_path = Path("")
    mock_output_manager.save_chunk_threshold_call_count = None
    mock_output_manager.maximum_pool_size = 0
    mock_output_manager.set_metadata_prefix("test_prefix")

    mock_create_directory = mocker.patch.object(mock_output_manager, "create_directory")
    mock_add_log = mocker.patch.object(mock_output_manager, "add_log")

    # Mock psutil.virtual_memory to simulate available memory
    psutil_virtual_memory_return = mocker.MagicMock()
    psutil_virtual_memory_return.available = 1024
    mocker.patch("psutil.virtual_memory", return_value=psutil_virtual_memory_return)

    # Input parameters
    dummy_output_directory: Path = Path("dummy/path")
    dummy_max_memory_usage_percent: int = 80
    dummy_max_memory_usage: int = 0
    dummy_save_chunk_threshold_call_count: int = 15000

    # Act
    with freeze_time("2024-05-20 13:14:00"):
        mock_output_manager.setup_pool_overflow_control(
            dummy_output_directory,
            dummy_max_memory_usage_percent,
            dummy_max_memory_usage,
            dummy_save_chunk_threshold_call_count,
        )

    # Expected values
    expected_saved_pool_chunks_path = Path.joinpath(
        dummy_output_directory, "saved_pool/test_prefix_20-May-2024_Mon_13-14-00.000000"
    )
    expected_available_memory = 1024
    expected_available_memory_gb = expected_available_memory / (1024**3)
    expected_log_message = (
        f"Created {expected_saved_pool_chunks_path} for saved pools during simulation.\n"
        f"Current system available memory: {expected_available_memory_gb:.2f} GB = "
        f"{expected_available_memory} Bytes.\n"
        "The threshold add_variable_call count for saving pool chunk is set to "
        f"{dummy_save_chunk_threshold_call_count}"
    )

    # Assert
    assert mock_output_manager.chunkification is True
    assert mock_output_manager.available_memory == expected_available_memory
    assert mock_output_manager.saved_pool_chunks_path == expected_saved_pool_chunks_path
    assert mock_output_manager.save_chunk_threshold_call_count == dummy_save_chunk_threshold_call_count
    assert mock_output_manager.maximum_pool_size == dummy_max_memory_usage
    mock_add_log.assert_called_once_with("Pool Overflow Control Setup", expected_log_message, info_map)
    mock_create_directory.assert_called_once_with(expected_saved_pool_chunks_path)


def test_setup_pool_overflow_control_user_define_max_memory_usage(
    mocker: MockerFixture, mock_output_manager: OutputManager
) -> None:
    info_map = {"class": "OutputManager", "function": "setup_pool_overflow_control"}
    mock_output_manager.chunkification = False
    mock_output_manager.available_memory = 0
    mock_output_manager.saved_pool_chunks_path = Path("")
    mock_output_manager.save_chunk_threshold_call_count = 0
    mock_output_manager.maximum_pool_size = 0

    mock_create_directory = mocker.patch.object(mock_output_manager, "create_directory")
    mock_add_log = mocker.patch.object(mock_output_manager, "add_log")

    psutil_virtual_memory_return = MagicMock()
    psutil_virtual_memory_return.available = 1024
    psutil.virtual_memory = MagicMock(return_value=psutil_virtual_memory_return)

    dummy_output_directory: Path = Path("dummy/path")
    dummy_max_memory_usage_percent: int = 80
    dummy_max_memory_usage: int = 1024
    dummy_save_chunk_threshold_call_count: int = 0

    with freeze_time("2024-05-20 13:14:00"):
        mock_output_manager.setup_pool_overflow_control(
            dummy_output_directory,
            dummy_max_memory_usage_percent,
            dummy_max_memory_usage,
            dummy_save_chunk_threshold_call_count,
        )

    expected_saved_pool_chunks_path = Path.joinpath(
        dummy_output_directory, "saved_pool/test_prefix_20-May-2024_Mon_13-14-00.000000"
    )
    expected_available_memory = 1024
    expected_available_memory_gb = expected_available_memory / (1024**3)
    expected_log_message = (
        f"Created {expected_saved_pool_chunks_path} for saved pools during simulation.\n"
        f"Current system available memory: {expected_available_memory_gb:.2f} GB = "
        f"{expected_available_memory} Bytes.\n"
        "The maximum output variable pool size is set to "
        f"{dummy_max_memory_usage} Bytes"
    )

    assert mock_output_manager.chunkification is True
    assert mock_output_manager.available_memory == expected_available_memory
    assert mock_output_manager.saved_pool_chunks_path == expected_saved_pool_chunks_path
    assert mock_output_manager.save_chunk_threshold_call_count == 0
    assert mock_output_manager.maximum_pool_size == dummy_max_memory_usage
    mock_add_log.assert_called_once_with("Pool Overflow Control Setup", expected_log_message, info_map)
    mock_create_directory.assert_called_once_with(expected_saved_pool_chunks_path)
    mock_output_manager.chunkification = False


def test_setup_pool_overflow_control_user_define_max_memory_usage_percentage(mocker: MockerFixture) -> None:
    info_map = {"class": "OutputManager", "function": "setup_pool_overflow_control"}
    output_manager = OutputManager()
    output_manager.chunkification = False
    output_manager.available_memory = 0
    output_manager.saved_pool_chunks_path = Path("")
    output_manager.save_chunk_threshold_call_count = 0
    output_manager.maximum_pool_size = 0
    output_manager.__metadata_prefix = "test_prefix"

    mock_create_directory = mocker.patch.object(output_manager, "create_directory")
    mock_add_log = mocker.patch.object(output_manager, "add_log")

    psutil_virtual_memory_return = MagicMock()
    psutil_virtual_memory_return.available = 1024
    psutil.virtual_memory = MagicMock(return_value=psutil_virtual_memory_return)

    dummy_output_directory: Path = Path("dummy/path")
    dummy_max_memory_usage_percent: int = 80
    dummy_max_memory_usage: int = 0
    dummy_save_chunk_threshold_call_count: int = 0

    with freeze_time("2024-05-20 13:14:00"):
        output_manager.setup_pool_overflow_control(
            dummy_output_directory,
            dummy_max_memory_usage_percent,
            dummy_max_memory_usage,
            dummy_save_chunk_threshold_call_count,
        )

    expected_saved_pool_chunks_path = Path.joinpath(
        dummy_output_directory, "saved_pool/test_prefix_20-May-2024_Mon_13-14-00.000000"
    )
    expected_available_memory = 1024
    expected_available_memory_gb = expected_available_memory / (1024**3)
    expected_max_pool_size = (dummy_max_memory_usage_percent / 100) * expected_available_memory
    expected_log_message = (
        f"Created {expected_saved_pool_chunks_path} for saved pools during simulation.\n"
        f"Current system available memory: {expected_available_memory_gb:.2f} GB = "
        f"{expected_available_memory} Bytes.\n"
        "The maximum output variable pool size is set to "
        f"{expected_max_pool_size} Bytes"
    )

    assert output_manager.chunkification is True
    assert output_manager.available_memory == expected_available_memory
    assert output_manager.saved_pool_chunks_path == expected_saved_pool_chunks_path
    assert output_manager.save_chunk_threshold_call_count == 0
    assert output_manager.maximum_pool_size == expected_max_pool_size

    mock_create_directory.assert_called_once_with(expected_saved_pool_chunks_path)
    mock_add_log.assert_called_once_with("Pool Overflow Control Setup", expected_log_message, info_map)
    output_manager.chunkification = False


@pytest.mark.parametrize(
    "filter_content, expected_label, expected_error",
    [
        # Case 1: Missing 'origin_label' key
        ({}, OriginLabel.NONE, False),
        # Case 2: Non-string 'origin_label' value
        ({"origin_label": 123}, OriginLabel.NONE, True),
        # Case 3: Invalid 'origin_label' value
        ({"origin_label": "invalid_label"}, OriginLabel.NONE, True),
        # Case 4: Valid 'origin_label' value
        ({"origin_label": "true and report origins"}, OriginLabel("true and report origins"), False),
    ],
)
def test_get_origin_label(
    filter_content: dict[str, Any], expected_label: OriginLabel, expected_error: bool, mocker: MockerFixture
) -> None:
    """
    Unit test for the _get_origin_label() method in OutputManager class.
    """
    # Arrange
    output_manager = OutputManager()
    mocked_add_error = mocker.patch.object(output_manager, "add_error")

    # Act
    result = output_manager._get_origin_label(filter_content)

    # Assert
    assert result == expected_label

    if expected_error:
        mocked_add_error.assert_called_once()
    else:
        mocked_add_error.assert_not_called()


def test_validate_string_list_valid(mocker: MockerFixture) -> None:
    """Test for validate_string_list()."""
    om = OutputManager()
    mock_add_error = mocker.patch.object(om, "add_error")
    om.validate_list_of_strings(["a", "b"], "key", "test_filter")
    mock_add_error.assert_not_called()


def test_validate_string_list_invalid_type(mocker: MockerFixture) -> None:
    """Test for validate_string_list() raising on non-list."""
    om = OutputManager()
    mock_add_error = mocker.patch.object(om, "add_error")
    om.validate_list_of_strings("not_a_list", "key", "test_filter")
    mock_add_error.assert_called_once()


def test_validate_string_list_invalid_element(mocker: MockerFixture) -> None:
    """Test for validate_string_list() raising on non-string elements."""
    om = OutputManager()
    mock_add_error = mocker.patch.object(om, "add_error")
    om.validate_list_of_strings(["a", 1], "key", "test_filter")
    mock_add_error.assert_called_once()


def test_validate_dict_of_numbers_valid(mocker: MockerFixture) -> None:
    """Test for validate_dict_of_numbers()."""
    om = OutputManager()
    mock_add_error = mocker.patch.object(om, "add_error")

    om.validate_dict_of_numbers({"a": 1, "b": 2.0}, "constants", "test_filter")

    mock_add_error.assert_not_called()


def test_validate_dict_of_numbers_invalid_value(mocker: MockerFixture) -> None:
    """Test for validate_dict_of_numbers() raising on non-numeric values."""
    om = OutputManager()
    mock_add_error = mocker.patch.object(om, "add_error")

    om.validate_dict_of_numbers({"a": "one"}, "constants", "test_filter")

    mock_add_error.assert_called_once()


def test_validate_aggregator_valid(mocker: MockerFixture) -> None:
    """Test for validate_aggregator() with supported functions."""
    om = OutputManager()
    mock_add_error = mocker.patch.object(om, "add_error")
    for func in ["average", "division", "product", "SD", "sum", "subtraction"]:
        om.validate_aggregator(func, "agg", "test_filter")
    mock_add_error.assert_not_called()


def test_validate_aggregator_invalid(mocker: MockerFixture) -> None:
    """Test for validate_aggregator() raising on unsupported function."""
    om = OutputManager()

    with pytest.raises(ValueError):
        om.validate_aggregator("median", "agg", "test_filter")


def test_validate_type_match(mocker: MockerFixture) -> None:
    """Test for validate_type() not calling add_error on matching type."""
    om = OutputManager()
    mock_add = mocker.patch.object(om, "add_error")

    om.validate_type("abc", "field", "test_filter", str, "a string")

    mock_add.assert_not_called()


def test_validate_type_mismatch(mocker: MockerFixture) -> None:
    """Test for validate_type() calling add_error on type mismatch."""
    om = OutputManager()
    mock_add = mocker.patch.object(om, "add_error")

    om.validate_type(123, "field", "test_filter", str, "a string")

    mock_add.assert_called_once_with(
        "Invalid report filter data type",
        "[ERROR] 'field' in test_filter must be a string but received <class 'int'>.",
        {"class": om.__class__.__name__, "function": om.validate_type.__name__},
    )


def test_validate_graph_type_valid(mocker: MockerFixture) -> None:
    """Test for validate_graph_type() with supported types."""
    om = OutputManager()
    mock_add_error = mocker.patch.object(om, "add_error")

    for t in ["plot", "barbs", "violin"]:
        om.validate_graph_type(t, "type", "test_filter")

    mock_add_error.assert_not_called()


def test_validate_graph_type_invalid(mocker: MockerFixture) -> None:
    """Test for validate_graph_type() raising on unsupported type."""
    om = OutputManager()
    mock_add_error = mocker.patch.object(om, "add_error")

    om.validate_graph_type("unsupported", "type", "test_filter")

    mock_add_error.assert_called_once()


def test_validate_customization_details_valid(mocker: MockerFixture) -> None:
    """Test for validate_customization_details() with allowed options."""
    om = OutputManager()
    mock_add_error = mocker.patch.object(om, "add_error")
    om.validate_customization_details({"title": "My Chart", "grid": True}, "customization_details", "test_filter")
    mock_add_error.assert_not_called()


def test_validate_customization_details_invalid_type(mocker: MockerFixture) -> None:
    """Test for validate_customization_details() raising on non-dict."""
    om = OutputManager()
    mock_add = mocker.patch.object(om, "add_error")
    om.validate_customization_details("not a dict", "customization_details", "test_filter")
    mock_add.assert_called_once()


def test_validate_customization_details_unknown_option(mocker: MockerFixture) -> None:
    """Test for validate_customization_details() raising on unknown option."""
    om = OutputManager()
    mock_add_error = mocker.patch.object(om, "add_error")
    om.validate_customization_details({"unknown_opt": 123}, "customization_details", "test_filter")
    mock_add_error.assert_called_once()


def test_validate_graph_details_and_options_valid() -> None:
    """Test for validate_graph_details() with complete details."""
    details = {
        "type": "plot",
        "filters": ["a"],
        "customization_details": {"title": "Chart"},
        "legend": ["L1"],
        "display_units": True,
        "use_calendar_dates": False,
        "data_significant_digits": 3,
    }
    om = OutputManager()
    om.validate_graph_details(details, "graph_details", "test_filter")


def test_validate_graph_details_missing_type(mocker: MockerFixture) -> None:
    """Test for validate_graph_details() raising when type missing."""
    om = OutputManager()
    mock_error = mocker.patch.object(om, "add_error")
    om.validate_graph_details({"filters": ["a"]}, "graph_details", "test_filter")
    mock_error.assert_called_once()


def test_validate_filter_content_valid_report(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test for validate_filter_content() with minimal valid filter."""
    content: Any = [
        {
            "name": "Report1",
            "filters": ["x"],
            "vertical_aggregation": "sum",
            "fill_value": 0,
            "graph_details": {"type": "stem"},
        }
    ]
    file: Path = tmp_path / "f1.json"
    file.write_text(str(content))
    om = OutputManager()
    mocker.patch.object(om, "_list_filter_files_in_dir", return_value=[file.name])
    mocker.patch.object(om, "_load_filter_file_content", return_value=(content, None))
    mock_validate_type = mocker.patch.object(OutputManager, "validate_type")
    mock_graph_details_validation = mocker.patch.object(OutputManager, "validate_graph_details")
    om.validate_filter_content(tmp_path)
    assert mock_validate_type.call_count == 2
    mock_graph_details_validation.assert_called_once()


def test_validate_filter_content_valid_csv(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test for validate_filter_content() with minimal valid filter."""
    content: Any = [
        {
            "name": "Report1",
            "filters": ["x"],
        }
    ]
    file: Path = tmp_path / "csv_f1.json"
    file.write_text(str(content))
    om = OutputManager()
    mocker.patch.object(om, "_list_filter_files_in_dir", return_value=[file.name])
    mocker.patch.object(om, "_load_filter_file_content", return_value=(content, None))
    mock_csv_validation = mocker.patch.object(OutputManager, "validate_csv_filters")
    om.validate_filter_content(tmp_path)
    mock_csv_validation.assert_called_once()


def test_validate_filter_content_valid_json(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test for validate_filter_content() with minimal valid filter."""
    content: Any = [
        {
            "name": "Report1",
            "filters": ["x"],
        }
    ]
    file: Path = tmp_path / "json_f1.json"
    file.write_text(str(content))
    om = OutputManager()
    mocker.patch.object(om, "_list_filter_files_in_dir", return_value=[file.name])
    mocker.patch.object(om, "_load_filter_file_content", return_value=(content, None))
    mock_json_validation = mocker.patch.object(OutputManager, "validate_json_filters")
    om.validate_filter_content(tmp_path)
    mock_json_validation.assert_called_once()


def test_validate_filter_content_valid_txt(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test for validate_filter_content() with minimal valid filter."""
    content: Any = "txt tests"
    file: Path = tmp_path / "f1.txt"
    file.write_text(str(content))
    om = OutputManager()
    mocker.patch.object(om, "_list_filter_files_in_dir", return_value=[file.name])
    mocker.patch.object(om, "_load_filter_file_content", return_value=(content, None))
    mock_log = mocker.patch.object(OutputManager, "add_log")
    om.validate_filter_content(tmp_path)
    mock_log.assert_called_once()


def test_validate_filter_content_missing_key(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test for validate_filter_content() raising when filters key missing."""
    bad: Any = [{"name": "Report1"}]
    file: Path = tmp_path / "f1.json"
    file.write_text(str(bad))
    om = OutputManager()
    mock_error = mocker.patch.object(om, "add_error")
    mocker.patch.object(om, "_list_filter_files_in_dir", return_value=[file.name])
    mocker.patch.object(om, "_load_filter_file_content", return_value=(bad, None))
    om.validate_filter_content(tmp_path)
    mock_error.assert_called_once()


def test_validate_report_filters_valid_filters(mocker: MockerFixture) -> None:
    """Test for validate_report_filters() with filters key present."""
    om = OutputManager()
    filter_content: Any = {"filters": ["x"]}
    error_spy = mocker.patch.object(om, "add_error")
    om.validate_report_filters(filter_content, "test_filter")
    error_spy.assert_not_called()


def test_validate_report_filters_valid_cross_references(mocker: MockerFixture) -> None:
    """Test for validate_report_filters() with cross_references key present."""
    om = OutputManager()
    filter_content: Any = {"cross_references": ["R1"]}
    error_spy = mocker.patch.object(om, "add_error")
    om.validate_report_filters(filter_content, "test_filter")
    error_spy.assert_not_called()


def test_validate_report_filters_missing_both(mocker: MockerFixture) -> None:
    """Test for validate_report_filters() raising when neither filters nor cross_references present."""
    om = OutputManager()
    filter_content: Any = {"name": "TestReport"}
    error_spy = mocker.patch.object(om, "add_error")
    om.validate_report_filters(filter_content, "test_filter")
    assert error_spy.call_count == 1
    title_arg, message_arg, info_map = error_spy.call_args.args
    assert "Parsing error" in title_arg


def test_validate_report_filters_unknown_key(mocker: MockerFixture) -> None:
    """Test for validate_report_filters() raising on unknown key."""
    om = OutputManager()
    filter_content: Any = {"filters": ["x"], "unknown": 123}
    error_spy = mocker.patch.object(om, "add_error")
    om.validate_report_filters(filter_content, "test_filter")
    assert any("Unknown key in report filter" in call.args[0] for call in error_spy.mock_calls)


def test_validate_report_filters_fill_value_ignored(mocker: MockerFixture) -> None:
    """Test for validate_report_filters() ignoring fill_value key."""
    om = OutputManager()
    filter_content: Any = {"filters": ["x"], "fill_value": "anything"}
    error_spy = mocker.patch.object(om, "add_error")
    om.validate_report_filters(filter_content, "test_filter")
    error_spy.assert_not_called()


def test_validate_report_filters_constants_no_change(mocker: Any) -> None:
    om = OutputManager()
    setattr(GeneralConstants, "UNCHANGED_CONST", 5)

    filter_content: Any = {"filters": ["x"], "constants": {"UNCHANGED_CONST": 5}}
    warning_spy = mocker.patch.object(om, "add_warning")

    om.validate_report_filters(filter_content, "test_filter")

    assert getattr(GeneralConstants, "UNCHANGED_CONST") == 5

    warning_spy.assert_not_called()


def test_validate_filter_content_unsupported_key(tmp_path: Path, mocker: MockerFixture) -> None:
    """Test for validate_filter_content() raising when filters key missing."""
    bad: Any = [{"name": "Report1", "filters": ["x"], "random": 0}]
    file: Path = tmp_path / "f1.json"
    file.write_text(str(bad))
    om = OutputManager()
    mock_error = mocker.patch.object(om, "add_error")
    mocker.patch.object(om, "_list_filter_files_in_dir", return_value=[file.name])
    mocker.patch.object(om, "_load_filter_file_content", return_value=(bad, None))
    om.validate_filter_content(tmp_path)
    mock_error.assert_called_once()


def test_validate_json_filters_valid(mocker: MockerFixture) -> None:
    """validate_json_filters should call the right validators on a minimal valid JSON filter."""
    om = OutputManager()
    content: dict[str, Any] = {
        "name": "JSON1",
        "filters": ["a"],
        "variables": ["b"],
    }
    mock_validate_type = mocker.patch.object(OutputManager, "validate_type")
    mock_validate_list = mocker.patch.object(OutputManager, "validate_list_of_strings")
    mock_add_error = mocker.patch.object(om, "add_error")
    om.validate_json_filters(content, "test.json")
    mock_validate_type.assert_called_once_with("JSON1", "name", "test.json", expected=str, type_label="a string")
    assert mock_validate_list.call_count == 2
    mock_validate_list.assert_has_calls(
        [
            mocker.call(["a"], "filters", "test.json"),
            mocker.call(["b"], "variables", "test.json"),
        ],
        any_order=True,
    )
    mock_add_error.assert_not_called()


def test_validate_json_filters_non_dict(mocker: MockerFixture) -> None:
    """validate_json_filters should error out if passed a non-dict."""
    om = OutputManager()
    bad_content: Any = ["not", "a", "dict"]
    mock_add_error = mocker.patch.object(om, "add_error")
    om.validate_json_filters(bad_content, "bad.json")
    mock_add_error.assert_called_once()
    args, _ = mock_add_error.call_args
    assert "Parsing error" in args[0]


def test_validate_json_filters_unknown_key(mocker: MockerFixture) -> None:
    """validate_json_filters should report unknown keys and still run known validators."""
    om = OutputManager()
    content: dict[str, Any] = {
        "name": "JSON2",
        "filters": ["x"],
        "variables": ["y"],
        "extra": 123,
    }
    mock_validate_type = mocker.patch.object(OutputManager, "validate_type")
    mock_validate_list = mocker.patch.object(OutputManager, "validate_list_of_strings")
    mock_add_error = mocker.patch.object(om, "add_error")
    om.validate_json_filters(content, "f.json")
    mock_validate_type.assert_called_once()
    assert mock_validate_list.call_count == 2
    add_error_calls = [c for c in mock_add_error.call_args_list if "Unknown key in json filter" in c[0][0]]
    assert len(add_error_calls) == 1


def test_validate_csv_filters_valid(mocker: MockerFixture) -> None:
    """validate_csv_filters should call the right validators on a minimal valid CSV filter."""
    om = OutputManager()
    content: dict[str, Any] = {
        "name": "CSV1",
        "filters": ["a"],
        "direction": "up",
    }
    mock_validate_type = mocker.patch.object(OutputManager, "validate_type")
    mock_validate_list = mocker.patch.object(OutputManager, "validate_list_of_strings")
    mock_validate_direction = mocker.patch.object(OutputManager, "validate_direction")
    mock_add_error = mocker.patch.object(om, "add_error")
    om.validate_csv_filters(content, "test.csv")
    mock_validate_type.assert_called_once_with("CSV1", "name", "test.csv", expected=str, type_label="a string")
    mock_validate_list.assert_called_once_with(["a"], "filters", "test.csv")
    mock_validate_direction.assert_called_once_with("up", "direction", "test.csv")
    mock_add_error.assert_not_called()


def test_validate_csv_filters_non_dict(mocker: MockerFixture) -> None:
    """validate_csv_filters should error out if passed a non-dict."""
    om = OutputManager()
    bad_content: Any = "not a dict"
    mock_add_error = mocker.patch.object(om, "add_error")
    om.validate_csv_filters(bad_content, "bad.csv")
    mock_add_error.assert_called_once()
    assert "Parsing error" in mock_add_error.call_args[0][0]


def test_validate_csv_filters_unknown_key(mocker: MockerFixture) -> None:
    """validate_csv_filters should report unknown keys and still run known validators."""
    om = OutputManager()
    content: dict[str, Any] = {
        "name": "CSV2",
        "filters": ["f"],
        "direction": "down",
        "surprise": True,
    }
    mock_validate_type = mocker.patch.object(OutputManager, "validate_type")
    mock_validate_list = mocker.patch.object(OutputManager, "validate_list_of_strings")
    mock_validate_direction = mocker.patch.object(OutputManager, "validate_direction")
    mock_add_error = mocker.patch.object(om, "add_error")
    om.validate_csv_filters(content, "f.csv")
    mock_validate_type.assert_called_once()
    mock_validate_list.assert_called_once()
    mock_validate_direction.assert_called_once()
    calls = [c for c in mock_add_error.call_args_list if "Unknown key in csv filter" in c[0][0]]
    assert len(calls) == 1
