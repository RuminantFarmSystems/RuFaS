"""
RUFAS: Ruminant Farm Systems Model
File name: test_input_manager.py
Description: Implements test cases for Input Manager
Author(s): Niko Tomlinson, ndt2@cornell.edu
"""
from functools import reduce
import json
from typing import Any, Callable, Dict
from mock import MagicMock, Mock, mock_open, patch
import pandas as pd
import pytest
from pytest_mock import MockerFixture

from RUFAS.input_manager import InputManager


@pytest.fixture
def mock_input_manager(mocker: MockerFixture) -> InputManager:
    input_manager = InputManager()
    return input_manager


def test_input_manager_singleton(mocker: MockerFixture) -> None:
    """Unit test to ensure InputManager is a singleton"""
    im1 = InputManager()
    im2 = InputManager()

    assert im1 is im2


@pytest.fixture
def input_manager_original_method_states(
        mock_input_manager: InputManager,
) -> Dict[str, Callable]:
    """Fixture to store original methods of OutputManager"""
    return {
        "start_data_processing": mock_input_manager.start_data_processing,
        "_load_metadata": mock_input_manager._load_metadata,
        "_load_data_from_json": mock_input_manager._load_data_from_json,
        "_load_data_from_csv": mock_input_manager._load_data_from_csv,
        "_validate_data": mock_input_manager._validate_data,
        "_validate_element": mock_input_manager._validate_element,
        "_validate_array_type_element": mock_input_manager._validate_array_type_element,
        "_validate_num_type_element": mock_input_manager._validate_num_type_element,
        "_validate_string_type_element": mock_input_manager._validate_string_type_element,
        "_fix_data": mock_input_manager._fix_data,
    }


def test_load_metadata(mock_input_manager: InputManager) -> None:
    """Unit test for function _load_metadata in file input_manager.py"""
    with patch("builtins.open", mock_open(read_data='{"dummy_key1": "dummy_value1", "dummy_key2": "dummy_value2"}')):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            mock_input_manager._load_metadata("path/dummy_metadata.json")
            assert mock_input_manager._InputManager__metadata == {"dummy_key1": "dummy_value1",
                                                                  "dummy_key2": "dummy_value2"}
            assert add_log.call_count == 2


def test_load_metadata_raises_exception(mock_input_manager: InputManager) -> None:
    """Unit test for function _load_metadata raising an exception in file input_manager.py"""
    mock_open_func = Mock()
    mock_open_func.side_effect = Exception("Error opening file")

    with patch("builtins.open", mock_open_func):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            with pytest.raises(Exception):
                mock_input_manager._load_metadata("path/dummy_metadata.json")
            assert add_log.call_count == 1


def test_load_data_from_json(mock_input_manager: InputManager, ) -> None:
    """Unit test for function _load_data_from_json with valid json file in file input_manager.py"""
    dummy_data = {
        "files": {"dummy_data_file": {"path": "dummy_data.json", "type": "json"}}}
    file_path = "path/to/json/file"
    dummy_file_content = json.dumps(dummy_data)

    with patch("builtins.open", mock_open(read_data=dummy_file_content)):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            result_data = mock_input_manager._load_data_from_json(file_path)

            assert result_data == dummy_data
            assert add_log.call_count == 2


def test_load_data_from_json_missing_file_raises_error(mock_input_manager: InputManager, ) -> None:
    """Unit test for function _load_data_from_json with missing json file in file input_manager.py"""
    with patch("builtins.open", side_effect=FileNotFoundError):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            with pytest.raises(FileNotFoundError):
                mock_input_manager._load_data_from_json("non_existent_file.json")
                assert add_log.call_count == 1


def test_load_data_from_json_invalid_data_raises_error(mock_input_manager: InputManager, ) -> None:
    """Unit test for function _load_data_from_json with invalid json data in file input_manager.py"""
    with patch("builtins.open", mock_open(read_data="invalid_json_data")):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            with pytest.raises(json.JSONDecodeError):
                mock_input_manager._load_data_from_json("dummy_file.json")
                assert add_log.call_count == 1


def test_load_data_from_csv(mock_input_manager: InputManager) -> None:
    """Unit test for function _load_data_from_csv with valid csv file in file input_manager.py"""
    dummy_csv_data = "key1,key2\na,1\nb,2\n"
    dummy_expected_data = {'key1': ['a', 'b'], 'key2': [1, 2]}
    file_path = "path/to/csv/file"
    with patch("builtins.open", mock_open(read_data=dummy_csv_data)):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            result_data = mock_input_manager._load_data_from_csv(file_path)

            assert result_data == dummy_expected_data
            assert add_log.call_count == 2


def test_load_data_from_csv_missing_file_raises_error(mock_input_manager: InputManager, ) -> None:
    """Unit test for function _load_data_from_json with missing json file in file input_manager.py"""
    with patch("builtins.open", side_effect=FileNotFoundError):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            with pytest.raises(FileNotFoundError):
                mock_input_manager._load_data_from_csv("non_existent_file.csv")
                assert add_log.call_count == 2


def test_load_data_from_csv_invalid_data_raises_error(mock_input_manager: InputManager, ) -> None:
    """Unit test for function _load_data_from_json with invalid json data in file input_manager.py"""
    with patch("builtins.open", mock_open(read_data="invalid_csv_data")):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            with patch("pandas.read_csv", side_effect=pd.errors.ParserError("Invalid CSV")):
                with pytest.raises(pd.errors.ParserError):
                    mock_input_manager._load_data_from_csv("dummy_file.csv")
                    assert add_log.call_count == 1


def test_start_data_processing(mock_input_manager: InputManager,
                               input_manager_original_method_states: Dict[str, Callable], ) -> None:
    """Unit test for function start_data_processing in file input_manager.py"""
    mock_input_manager._load_metadata = MagicMock()
    mock_input_manager._validate_data = MagicMock(return_value=True)

    eager_termination = True
    mock_metadata_path = "mock/metadata/path"

    mock_input_manager.start_data_processing(mock_metadata_path, eager_termination)

    mock_input_manager._load_metadata.assert_called_once_with(mock_metadata_path)
    mock_input_manager._validate_data.assert_called_once_with(eager_termination)

    # Restore original methods
    mock_input_manager._load_metadata = input_manager_original_method_states["_load_metadata"]
    mock_input_manager._validate_data = input_manager_original_method_states["_validate_data"]


@pytest.fixture
def mock_metadata(mocker: MockerFixture) -> Dict[str, Dict[str, Any]]:
    return {
            "files": {
                "file1": {"type": "json", "path": "path/to/json/file1.json", "properties": "properties1"},
                "file2": {"type": "csv", "path": "path/to/csv/file2.csv", "properties": "properties2"},
            },
            "properties": {
                "properties1": {"element1": "some_value1", "element2": "some_value2"},
                "properties2": {"element3": "some_value3", "element4": "some_value4"},
            }
        }


def test_validate_data_valid(mock_input_manager: InputManager, mock_metadata: Dict[str, Dict[str, Any]],
                             input_manager_original_method_states: Dict[str, Callable], ):
    """Unit test for valid data for function _validate_data in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata

    mock_input_manager._load_data_from_json = lambda _: {"element1": "value1", "element2": "value2"}
    mock_input_manager._load_data_from_csv = lambda _: {"element3": "value3", "element4": "value4"}
    mock_input_manager._validate_element = lambda *_: True

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
            result = mock_input_manager._validate_data(eager_termination=True)

            assert result is True
            assert add_log.call_count == 3
            assert add_warning.call_count == 0

    mock_input_manager._validate_data = input_manager_original_method_states["_validate_data"]
    mock_input_manager._validate_element = input_manager_original_method_states["_validate_element"]


def test_validate_data_invalid(mock_input_manager: InputManager, mock_metadata: Dict[str, Dict[str, Any]],
                               input_manager_original_method_states: Dict[str, Callable], ):
    """Unit test for invalid data for function _validate_data in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata

    mock_input_manager._load_data_from_json = lambda _: {"element1": "value1", "element2": "value2"}
    mock_input_manager._load_data_from_csv = lambda _: {"element3": "value3", "element4": "value4"}
    mock_input_manager._validate_element = lambda *_: False

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:

            result = mock_input_manager._validate_data(eager_termination=False)
            assert result is False
            assert add_log.call_count == 3
            assert add_warning.call_count == 0

    mock_input_manager._validate_data = input_manager_original_method_states["_validate_data"]
    mock_input_manager._validate_element = input_manager_original_method_states["_validate_element"]


def test_validate_data_eager_termination(mock_input_manager: InputManager, mock_metadata: Dict[str, Dict[str, Any]],
                                         input_manager_original_method_states: Dict[str, Callable], ):
    """Unit test for invalid data with eager termination for function _validate_data in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata

    mock_input_manager._load_data_from_json = lambda _: {"element1": "value1", "element2": "value2"}
    mock_input_manager._load_data_from_csv = lambda _: {"element3": "value3", "element4": "value4"}
    mock_input_manager._validate_element = lambda *_: False

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:

            result = mock_input_manager._validate_data(eager_termination=True)
            assert result is False
            assert add_log.call_count == 0
            assert add_warning.call_count == 0

    mock_input_manager._validate_data = input_manager_original_method_states["_validate_data"]
    mock_input_manager._validate_element = input_manager_original_method_states["_validate_element"]


@pytest.fixture
def mock_metadata_for_validate_element(mocker: MockerFixture) -> Dict[str, Dict[str, Any]]:
    return {
            "files": {
                "file1": {
                    "type": "json",
                    "path": "/path/to/file1.json",
                    "properties": "property_map_key1"
                }
            },
            "properties": {
                "property_map_key1": {
                    "element1": {"type": "string", "pattern": r"^\d{3}-\d{2}-\d{4}$"},
                    "element2": {"type": "number", "minimum": 0, "maximum": 150},
                    "element3": {"type": "array",
                                 "minimum_length": 1, "maximum_length": 5},
                }
            }
        }


def test_validate_element_string_type(mock_input_manager: InputManager,
                                      mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
                                      input_manager_original_method_states: Dict[str, Callable], ):
    """Unit test for string type input_data for _validate_element in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element

    input_data = {"element1": "123-45-6789"}
    result = mock_input_manager._validate_element("module_key", "element1", "property_map_key1", input_data)

    assert result is True

    mock_input_manager._validate_element = input_manager_original_method_states["_validate_element"]


def test_validate_element_number_type(mock_input_manager: InputManager,
                                      mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
                                      input_manager_original_method_states: Dict[str, Callable], ):
    """Unit test for number type input_data for _validate_element in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element

    input_data = {"element2": 123}
    result = mock_input_manager._validate_element("module_key", "element2", "property_map_key1", input_data)

    assert result is True

    mock_input_manager._validate_element = input_manager_original_method_states["_validate_element"]


def test_validate_element_array_type(mock_input_manager: InputManager,
                                     mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
                                     input_manager_original_method_states: Dict[str, Callable], ):
    """Unit test for array type input_data for _validate_element in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element

    input_data = {"element3": [1, 2, 3]}
    result = mock_input_manager._validate_element("module_key", "element3", "property_map_key1", input_data)

    assert result is True

    mock_input_manager._validate_element = input_manager_original_method_states["_validate_element"]


def test_validate_element_object_type(mock_input_manager: InputManager, mocker: MockerFixture,
                                      mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
                                      input_manager_original_method_states: Dict[str, Callable], ):
    """Unit test for nested object type input_data for _validate_element in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element
    mocker.patch.object(mock_input_manager, "_validate_element", return_value=True)
    mocker.patch.object(mock_input_manager, "_fix_data", return_value=False)
    input_data = {"element4": {"nested_element1": "value1", "nested_element2": 123}}
    result = mock_input_manager._validate_element("module_key", "element4", "property_map_key1", input_data)

    assert result is True

    mock_input_manager._validate_element = input_manager_original_method_states["_validate_element"]


@pytest.mark.parametrize(
    'dummy_value, dummy_variable_to_check, expected_result, expected_warning_call_count',
    [
        ([1, 2, 3], {"minimum_length": 5, "maximum_length": 10}, False, 1),
        ([1, 2, 3, 4, 5], {"minimum_length": 5, "maximum_length": 10}, True, 0),
        ([1, 2, 3, 4, 5, 6, 7], {"minimum_length": 5}, True, 0),
        ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], {"maximum_length": 10}, True, 0),
        ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], {"minimum_length": 5, "maximum_length": 10}, False, 1),
        ([], {"minimum_length": 5}, False, 1),
    ]
)
def test_validate_array_type_element(dummy_value: list, dummy_variable_to_check: Dict[str, int], expected_result: bool,
                                     expected_warning_call_count: int, mock_input_manager: InputManager) -> None:
    """Unit test for function _validate_array_type_element function in file input_manager.py"""
    dummy_var_name = "dummy_array"

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._validate_array_type_element(dummy_variable_to_check, dummy_var_name, dummy_value)

    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.parametrize(
    'dummy_value, dummy_variable_to_check, expected_result, expected_warning_call_count',
    [
        (1, {"minimum": 3, "maximum": 7}, False, 1),
        (3, {"minimum": 3, "maximum": 7}, True, 0),
        (5, {"minimum": 3}, True, 0),
        (7, {"minimum": 3, "maximum": 7}, True, 0),
        (9, {"maximum": 7}, False, 1),
        (-1, {"minimum": 3, "maximum": 7}, False, 1),
    ]
)
def test_validate_num_type_element(dummy_value: int,
                                   dummy_variable_to_check: Dict[str, int],
                                   expected_result: bool,
                                   expected_warning_call_count: int,
                                   mock_input_manager: InputManager) -> None:
    """Unit test for function _validate_num_type_element function in file input_manager.py"""
    dummy_var_name = "dummy_num"

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._validate_num_type_element(dummy_variable_to_check, dummy_var_name, dummy_value)

    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.parametrize(
    'dummy_value, dummy_variable_to_check, expected_result, expected_warning_call_count',
    [
        ("cow", {"pattern": r"cow", "minimum_length": 1, "maximum_length": 5}, True, 0),
        ("cow", {"pattern": r".{3}", "minimum_length": 1}, True, 0),
        ("COW", {"pattern": r"cow", "minimum_length": 1, "maximum_length": 5}, False, 1),
        ("cow", {"minimum_length": 1, "maximum_length": 5}, True, 0),
        ("cow", {"minimum_length": 5}, False, 1),
        ("cow", {"maximum_length": 1}, False, 1),
    ]
)
def test_validate_string_type_element(dummy_value: int,
                                      dummy_variable_to_check: Dict[str, int],
                                      expected_result: bool,
                                      expected_warning_call_count: int,
                                      mock_input_manager: InputManager) -> None:
    """Unit test for function _validate_string_type_element function in file input_manager.py"""
    dummy_var_name = "dummy_var"

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._validate_string_type_element(dummy_variable_to_check, dummy_var_name, dummy_value)

    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.parametrize(
    'dummy_module_key, dummy_property_map_key, dummy_element_hierarchy, expected_value, expected_result, '
    'expected_warning_call_count',
    [
        ("economy", "economy_properties", ["array_var1"], [1, 2, 3, 4, 5], True, 1),
        ("economy", "economy_properties", ["array_var2"], [], True, 1),
        ("economy", "economy_properties", ["array_var3"], [1, 2, 3], True, 1),
        ("economy", "economy_properties", ["array_var4", "array_var5"], [1, 2, 3], True, 1),
    ]
)
def test_fix_array_type_fixable_data(dummy_module_key: str, dummy_property_map_key: str,
                                     dummy_element_hierarchy: list[str], expected_value: list, expected_result: bool,
                                     expected_warning_call_count: int, mock_input_manager: InputManager,
                                     mock_metadata: Dict[str, Dict[str, Any]],
                                     mock_pool: Dict[str, Dict[str, Any]], ) -> None:
    """Unit test for fixable array-type data for _fix_data function in file input_manager.py"""

    mock_input_manager._InputManager__metadata = mock_metadata
    mock_input_manager._InputManager__pool = mock_pool

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(dummy_module_key, dummy_property_map_key, dummy_element_hierarchy)

    variable_to_check = reduce(lambda d, key: d[key], dummy_element_hierarchy,
                               mock_pool[dummy_module_key])
    assert variable_to_check == expected_value
    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.parametrize(
    'dummy_module_key, dummy_property_map_key, dummy_element_hierarchy, expected_result, '
    'expected_warning_call_count',
    [
        ("economy", "economy_properties", ["array_var6"], False, 0),
        ("economy", "economy_properties", ["array_var7"], False, 0),
        ("economy", "economy_properties", ["array_var8"], False, 0),
        ("economy", "economy_properties", ["array_var9", "array_var10"], False, 0),
    ]
)
def test_fix_array_type_critical_data(dummy_module_key: str, dummy_property_map_key: str,
                                      dummy_element_hierarchy: list[str], expected_result: bool,
                                      expected_warning_call_count: int, mock_input_manager: InputManager,
                                      mock_metadata: Dict[str, Dict[str, Any]],
                                      mock_pool: Dict[str, Dict[str, Any]], ) -> None:
    """Unit test for critical array-type data for _fix_data function in file input_manager.py"""

    mock_input_manager._InputManager__metadata = mock_metadata
    mock_input_manager._InputManager__pool = mock_pool

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(dummy_module_key, dummy_property_map_key, dummy_element_hierarchy)

    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.parametrize(
    'dummy_module_key, dummy_property_map_key, dummy_element_hierarchy, expected_value, expected_result, '
    'expected_warning_call_count',
    [
        ("economy", "economy_properties", ["str_var1"], "cow", True, 1),
        ("economy", "economy_properties", ["str_var2"], "", True, 1),
        ("economy", "economy_properties", ["str_var3"], "cow", True, 1),
        ("economy", "economy_properties", ["str_var4", "str_var5"], "cow", True, 1),
    ]
)
def test_fix_str_type_fixable_data(dummy_module_key: str, dummy_property_map_key: str,
                                   dummy_element_hierarchy: list[str], expected_value: str, expected_result: bool,
                                   expected_warning_call_count: int, mock_input_manager: InputManager,
                                   mock_metadata: Dict[str, Dict[str, Any]],
                                   mock_pool: Dict[str, Dict[str, Any]], ) -> None:
    """Unit test for fixable string-type data for _fix_data function in file input_manager.py"""

    mock_input_manager._InputManager__metadata = mock_metadata
    mock_input_manager._InputManager__pool = mock_pool

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(dummy_module_key, dummy_property_map_key, dummy_element_hierarchy)

    variable_to_check = reduce(lambda d, key: d[key], dummy_element_hierarchy,
                               mock_pool[dummy_module_key])
    assert variable_to_check == expected_value
    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.parametrize(
    'dummy_module_key, dummy_property_map_key, dummy_element_hierarchy, expected_result, '
    'expected_warning_call_count',
    [
        ("economy", "economy_properties", ["str_var6"], False, 0),
        ("economy", "economy_properties", ["str_var7"], False, 0),
        ("economy", "economy_properties", ["str_var8"], False, 0),
        ("economy", "economy_properties", ["str_var9", "str_var10"], False, 0),
    ]
)
def test_fix_str_type_critical_data(dummy_module_key: str, dummy_property_map_key: str,
                                    dummy_element_hierarchy: list[str], expected_result: bool,
                                    expected_warning_call_count: int, mock_input_manager: InputManager,
                                    mock_metadata: Dict[str, Dict[str, Any]],
                                    mock_pool: Dict[str, Dict[str, Any]], ) -> None:
    """Unit test for critical string-type data for _fix_data function in file input_manager.py"""

    mock_input_manager._InputManager__metadata = mock_metadata
    mock_input_manager._InputManager__pool = mock_pool

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(dummy_module_key, dummy_property_map_key, dummy_element_hierarchy)

    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.parametrize(
    'dummy_module_key, dummy_property_map_key, dummy_element_hierarchy, expected_value, expected_result, '
    'expected_warning_call_count',
    [
        ("economy", "economy_properties", ["num_var1"], 5, True, 1),
        ("economy", "economy_properties", ["num_var2"], 0, True, 1),
        ("economy", "economy_properties", ["num_var3"], 5, True, 1),
        ("economy", "economy_properties", ["num_var4", "num_var5"], 5, True, 1),
    ]
)
def test_fix_num_type_fixable_data(dummy_module_key: str, dummy_property_map_key: str,
                                   dummy_element_hierarchy: list[str], expected_value: str, expected_result: bool,
                                   expected_warning_call_count: int, mock_input_manager: InputManager,
                                   mock_metadata: Dict[str, Dict[str, Any]],
                                   mock_pool: Dict[str, Dict[str, Any]], ) -> None:
    """Unit test for fixable number-type data for _fix_data function in file input_manager.py"""

    mock_input_manager._InputManager__metadata = mock_metadata
    mock_input_manager._InputManager__pool = mock_pool

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(dummy_module_key, dummy_property_map_key, dummy_element_hierarchy)

    variable_to_check = reduce(lambda d, key: d[key], dummy_element_hierarchy,
                               mock_pool[dummy_module_key])
    assert variable_to_check == expected_value
    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.parametrize(
    'dummy_module_key, dummy_property_map_key, dummy_element_hierarchy, expected_result, '
    'expected_warning_call_count',
    [
        ("economy", "economy_properties", ["num_var6"], False, 0),
        ("economy", "economy_properties", ["num_var7"], False, 0),
        ("economy", "economy_properties", ["num_var8"], False, 0),
        ("economy", "economy_properties", ["num_var9", "num_var10"], False, 0),
    ]
)
def test_fix_num_type_critical_data(dummy_module_key: str, dummy_property_map_key: str,
                                    dummy_element_hierarchy: list[str], expected_result: bool,
                                    expected_warning_call_count: int, mock_input_manager: InputManager,
                                    mock_metadata: Dict[str, Dict[str, Any]],
                                    mock_pool: Dict[str, Dict[str, Any]], ) -> None:
    """Unit test for critical number-type data for _fix_data function in file input_manager.py"""

    mock_input_manager._InputManager__metadata = mock_metadata
    mock_input_manager._InputManager__pool = mock_pool

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(dummy_module_key, dummy_property_map_key, dummy_element_hierarchy)

    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.parametrize(
    'dummy_module_key, dummy_property_map_key, dummy_element_hierarchy, expected_value, expected_result, '
    'expected_warning_call_count',
    [
        ("economy", "economy_properties", ["bool_var1"], True, True, 1),
        ("economy", "economy_properties", ["bool_var2"], False, True, 1),
        ("economy", "economy_properties", ["bool_var3", "bool_var4"], True, True, 1),
    ]
)
def test_fix_bool_type_fixable_data(dummy_module_key: str, dummy_property_map_key: str,
                                    dummy_element_hierarchy: list[str], expected_value: str, expected_result: bool,
                                    expected_warning_call_count: int, mock_input_manager: InputManager,
                                    mock_metadata: Dict[str, Dict[str, Any]],
                                    mock_pool: Dict[str, Dict[str, Any]], ) -> None:
    """Unit test for fixable Boolean-type data for _fix_data function in file input_manager.py"""

    mock_input_manager._InputManager__metadata = mock_metadata
    mock_input_manager._InputManager__pool = mock_pool

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(dummy_module_key, dummy_property_map_key, dummy_element_hierarchy)

    variable_to_check = reduce(lambda d, key: d[key], dummy_element_hierarchy,
                               mock_pool[dummy_module_key])
    assert variable_to_check == expected_value
    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.parametrize(
    'dummy_module_key, dummy_property_map_key, dummy_element_hierarchy, expected_result, '
    'expected_warning_call_count',
    [
        ("economy", "economy_properties", ["bool_var5"], False, 0),
        ("economy", "economy_properties", ["bool_var6"], False, 0),
        ("economy", "economy_properties", ["bool_var7", "bool_var8"], False, 0),
    ]
)
def test_fix_bool_type_critical_data(dummy_module_key: str, dummy_property_map_key: str,
                                     dummy_element_hierarchy: list[str], expected_result: bool,
                                     expected_warning_call_count: int, mock_input_manager: InputManager,
                                     mock_metadata: Dict[str, Dict[str, Any]],
                                     mock_pool: Dict[str, Dict[str, Any]], ) -> None:
    """Unit test for critical number-type data for _fix_data function in file input_manager.py"""

    mock_input_manager._InputManager__metadata = mock_metadata
    mock_input_manager._InputManager__pool = mock_pool

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(dummy_module_key, dummy_property_map_key, dummy_element_hierarchy)

    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count
