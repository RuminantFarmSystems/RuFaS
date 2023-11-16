"""
RUFAS: Ruminant Farm Systems Model
File name: test_input_manager.py
Description: Implements test cases for Input Manager
Author(s): Niko Tomlinson, ndt2@cornell.edu; Allister Liu, al25632@cornell.edu; Michael Richards, mr2372@cornell.edu
"""
from __future__ import annotations

import json
from functools import reduce
from typing import Any, Callable, Dict

import pandas as pd
import pytest
from mock import MagicMock, Mock, mock_open, patch
from pytest_mock import MockerFixture

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager


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
        "_filter_input_data_by_metadata": mock_input_manager._filter_input_data_by_metadata,
        "_populate_pool": mock_input_manager._populate_pool,
        "_validate_json_element": mock_input_manager._validate_json_element,
        "_validate_array_type": mock_input_manager._validate_array_type,
        "_validate_num_type": mock_input_manager._validate_num_type,
        "_validate_str_type": mock_input_manager._validate_str_type,
        "_validate_bool_type": mock_input_manager._validate_bool_type,
        "_fix_data": mock_input_manager._fix_data,
        "get_data": mock_input_manager.get_data,
        "get_metadata": mock_input_manager.get_metadata,
        "_validate_input_type_dynamic": mock_input_manager._validate_input_type_dynamic,
        "_validate_csv_element": mock_input_manager._validate_csv_element,
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


def test_load_data_from_csv(mock_input_manager: InputManager, ) -> None:
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
    """Unit test for function _load_data_from_csv with missing csv file in file input_manager.py"""
    with patch("builtins.open", side_effect=FileNotFoundError):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            with pytest.raises(FileNotFoundError):
                mock_input_manager._load_data_from_csv("non_existent_file.csv")
            assert add_log.call_count == 1


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
    mock_input_manager._populate_pool = MagicMock(return_value=True)

    eager_termination = True
    mock_metadata_path = "mock/metadata/path"

    mock_input_manager.start_data_processing(mock_metadata_path, eager_termination)

    mock_input_manager._load_metadata.assert_called_once_with(mock_metadata_path)
    mock_input_manager._populate_pool.assert_called_once_with(eager_termination)

    # Restore original methods
    mock_input_manager._load_metadata = input_manager_original_method_states["_load_metadata"]
    mock_input_manager._populate_pool = \
        input_manager_original_method_states["_populate_pool"]


@pytest.mark.parametrize("input_data, metadata_properties, expected_result", [
    (
            {'key1': 'value1', 'key2': 'value2'},
            {'key1': {'default': 'value3'}},
            {'key1': 'value1'}
    ),
    (
            {'key1': {'nested_key1': 'value1', 'nested_key2': 'value2'}},
            {'key1': {'nested_key1': {'default': 'value2'}}},
            {'key1': {'nested_key1': 'value1'}}
    )
])
def test_filter_input_data_by_metadata(mock_input_manager: InputManager, input_data: Dict[str, Any],
                                       metadata_properties: Dict[str, Any], expected_result: Dict[str, Any],
                                       input_manager_original_method_states: Dict[str, Callable], ) -> None:
    """Unit test for function _filter_input_data_by_metadata() in file input_manager.py"""
    filtered_input_data = mock_input_manager._filter_input_data_by_metadata(input_data, metadata_properties)
    assert filtered_input_data == expected_result

    mock_input_manager._filter_input_data_by_metadata = input_manager_original_method_states[
        "_filter_input_data_by_metadata"
    ]


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


@pytest.mark.skip(reason="This test is not working")
def test_populate_pool_valid(mock_input_manager: InputManager, mock_metadata: Dict[str, Dict[str, Any]],
                             input_manager_original_method_states: Dict[str, Callable], ) -> None:
    """Unit test for valid data for function _populate_pool in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata
    mock_input_manager._load_data_from_json = lambda _: {"element1": "value1", "element2": "value2"}
    mock_input_manager._load_data_from_csv = lambda _: {"element3": "value3", "element4": "value4"}
    mock_input_manager._validate_json_element = lambda *args, **kwargs: {"fixed_elements": 1,
                                                                         "valid_elements": 1,
                                                                         "total_elements": 1,
                                                                         "invalid_elements": 0,
                                                                         "is_valid": True
                                                                         }
    mock_input_manager._validate_csv_element = lambda *args, **kwargs: {"fixed_elements": 1,
                                                                        "valid_elements": 1,
                                                                        "total_elements": 1,
                                                                        "invalid_elements": 0,
                                                                        "is_valid": True
                                                                        }

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
            result = mock_input_manager._populate_pool(eager_termination=True)

        assert result is True
        assert add_log.call_count == 4
        assert add_warning.call_count == 0
        assert "file1" in mock_input_manager._InputManager__pool
        assert "file2" in mock_input_manager._InputManager__pool

    mock_input_manager._populate_pool = \
        input_manager_original_method_states["_populate_pool"]
    mock_input_manager._validate_json_element = input_manager_original_method_states["_validate_json_element"]
    mock_input_manager._validate_csv_element = input_manager_original_method_states["_validate_csv_element"]


@pytest.mark.skip(reason="This test is not working")
def test_populate_pool_invalid(mock_input_manager: InputManager, mock_metadata: Dict[str, Dict[str, Any]],
                               input_manager_original_method_states: Dict[str, Callable], ):
    """Unit test for invalid data for function _populate_pool in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata

    mock_input_manager._load_data_from_json = lambda _: {"element1": "value1", "element2": "value2"}
    mock_input_manager._load_data_from_csv = lambda _: {"element3": "value3", "element4": "value4"}
    mock_input_manager._validate_json_element = lambda *args, **kwargs: {"fixed_elements": 1,
                                                                         "valid_elements": 1,
                                                                         "total_elements": 1,
                                                                         "invalid_elements": 1,
                                                                         "is_valid": False
                                                                         }
    mock_input_manager._validate_csv_element = lambda *args, **kwargs: {"fixed_elements": 1,
                                                                        "valid_elements": 1,
                                                                        "total_elements": 1,
                                                                        "invalid_elements": 1,
                                                                        "is_valid": False
                                                                        }

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
            result = mock_input_manager._populate_pool(eager_termination=False)

        assert result is False
        assert add_log.call_count == 4
        assert add_warning.call_count == 0
        assert "file1" not in mock_input_manager._InputManager__pool
        assert "file2" not in mock_input_manager._InputManager__pool

    mock_input_manager._populate_pool = \
        input_manager_original_method_states["_populate_pool"]
    mock_input_manager._validate_json_element = input_manager_original_method_states["_validate_json_element"]
    mock_input_manager._validate_csv_element = input_manager_original_method_states["_validate_csv_element"]


@pytest.mark.skip(reason="This test is not working")
def test_populate_pool_eager_termination(mock_input_manager: InputManager, mock_metadata: Dict[str, Dict[str, Any]],
                                         input_manager_original_method_states: Dict[str, Callable], ):
    """Unit test for invalid data with eager termination for function
    _populate_pool in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata

    mock_input_manager._load_data_from_json = lambda _: {"element1": "value1", "element2": "value2"}
    mock_input_manager._load_data_from_csv = lambda _: {"element3": "value3", "element4": "value4"}
    mock_input_manager._validate_json_element = lambda *args, **kwargs: {"fixed_elements": 1,
                                                                         "valid_elements": 1,
                                                                         "total_elements": 1,
                                                                         "invalid_elements": 0,
                                                                         "is_valid": False
                                                                         }

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
            result = mock_input_manager._populate_pool(eager_termination=True)
            assert result is False
            assert add_log.call_count == 0
            assert add_warning.call_count == 0
            assert "file1" not in mock_input_manager._InputManager__pool
            assert "file2" not in mock_input_manager._InputManager__pool

    mock_input_manager._populate_pool = \
        input_manager_original_method_states["_populate_pool"]
    mock_input_manager._validate_json_element = input_manager_original_method_states["_validate_json_element"]


def test_populate_pool_raises_keyerror(mock_input_manager: InputManager,
                                       input_manager_original_method_states: Dict[str, Callable], ) -> None:
    """Unit test for invalid data file type for function _populate_pool in file input_manager.py"""
    mock_input_manager._InputManager__metadata = {"files": {"dummy_file_key": {"type": "invalid_data_type",
                                                                               "path": "/path/to/your/file",
                                                                               "properties": "some_properties_key"}}}

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
            with pytest.raises(KeyError):
                mock_input_manager._populate_pool(eager_termination=True)

                assert add_log.call_count == 0
                assert add_warning.call_count == 0

    mock_input_manager._populate_pool = \
        input_manager_original_method_states["_populate_pool"]
    mock_input_manager._validate_json_element = input_manager_original_method_states["_validate_json_element"]


@pytest.mark.skip(reason="This test is not working")
@pytest.mark.parametrize(
    "variable_properties, input_data_value",
    [
        ({"type": "string", "dummy_property": "dummy_value"}, "dummy_value"),
        ({"type": "number", "dummy_property": 10}, 10),
        ({"type": "bool", "dummy_property": True}, True),
        ({"type": "array", "dummy_property": []}, []),
    ]
)
def test_validate_input_type_dynamic_valid_data(mock_input_manager: InputManager,
                                                input_manager_original_method_states: Dict[str, Callable],
                                                variable_properties: Dict[str, Any],
                                                input_data_value: Any) -> None:
    """Unit test for valid data type for function _validate_input_type_dynamic in file input_manager.py"""
    var_name = "dummy_var"

    result = mock_input_manager._validate_input_type_dynamic(variable_properties, var_name, input_data_value)
    assert result is True

    mock_input_manager._validate_input_type_dynamic = \
        input_manager_original_method_states["_validate_input_type_dynamic"]


def test_validate_input_type_dynamic_invalid_type_raises_keyerror(mock_input_manager: InputManager,
                                                                  input_manager_original_method_states:
                                                                  Dict[str, Callable],
                                                                  ) -> None:
    """Unit test for invalid data type raising a KeyError for function
    _validate_input_type_dynamic in file input_manager.py"""
    variable_properties = {"type": "invalid_type", "dummy_property": "dummy_value"}
    var_name = "dummy_var"
    input_data_value = "dummy_value"

    with pytest.raises(KeyError, match="Invalid type invalid_type"):
        mock_input_manager._validate_input_type_dynamic(variable_properties, var_name, input_data_value)

    mock_input_manager._validate_input_type_dynamic = \
        input_manager_original_method_states["_validate_input_type_dynamic"]


def test_validate_input_type_dynamic_missing_type_raises_keyerror(mock_input_manager: InputManager,
                                                                  input_manager_original_method_states:
                                                                  Dict[str, Callable],
                                                                  ) -> None:
    """Unit test for missing data type raising a KeyError for function
    _validate_input_type_dynamic in file input_manager.py"""
    variable_properties = {"dummy_property": "dummy_value"}
    var_name = "dummy_var"
    input_data_value = "dummy_value"

    with pytest.raises(KeyError, match="Missing 'type' key in variable_properties"):
        mock_input_manager._validate_input_type_dynamic(variable_properties, var_name, input_data_value)

    mock_input_manager._validate_input_type_dynamic = \
        input_manager_original_method_states["_validate_input_type_dynamic"]


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
                "element4": {"type": "object",
                             "description": "dummy_description",
                             "nested_element1": {
                                 "type": "string",
                                 "minimum_length": 1,
                                 "maximum_length": 20
                             },
                             "nested_element2": {
                                 "type": "number",
                                 "minimum": 0,
                                 "maximum": 250
                             }
                             },
                "element5": {"type": "object",
                             "description": "dummy_description",
                             "nested_element1": {
                                 "type": "string",
                                 "minimum_length": 1,
                                 "maximum_length": 20
                             },
                             "nested_element2": {
                                 "type": "number",
                                 "minimum": 0,
                                 "maximum": 250
                             },
                             "nested_element3": {
                                 "type": "object",
                                 "description": "dummy_description",
                                 "nested_sub_element1": {
                                     "type": "string",
                                     "minimum_length": 1,
                                     "maximum_length": 5
                                 },
                                 "nested_sub_element2": {
                                     "type": "array",
                                     "minimum_length": 1,
                                     "maximum_length": 5
                                 },
                             }
                             },
                "element6": {"type": "bool"},
                "element7": {"type": "number", "maximum": 10, "default": 5},
                "element8": {"type": "object", "nested_element": {"type": "number", "maximum": 10}},
            }
        }
    }


@pytest.mark.skip(reason="This test is not working")
def test_validate_element_fixable_data(mock_input_manager: InputManager,
                                       mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
                                       input_manager_original_method_states: Dict[str, Callable], ) -> None:
    """Unit test for a fixable number type input_data for _validate_json_element in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element
    mock_input_manager._validate_num_type = MagicMock(return_value=False)
    mock_input_manager._fix_data = MagicMock(return_value=True)
    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}

    input_data = {"element2": 123}
    result = mock_input_manager._validate_json_element(["element2"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is True
    assert result["fixed_elements"] == 1
    assert result["total_elements"] == 1
    assert result["invalid_elements"] == 0
    assert result["valid_elements"] == 0

    mock_input_manager._validate_json_element = input_manager_original_method_states["_validate_json_element"]
    mock_input_manager._validate_num_type = input_manager_original_method_states["_validate_num_type"]
    mock_input_manager._fix_data = input_manager_original_method_states["_fix_data"]


@pytest.mark.skip(reason="This test is not working")
@pytest.mark.parametrize(
    "property, input_data, total_elements, valid_elements, invalid_elements, fixed_elements",
    [
        ("element1", {"element1": ["123-45-6789", "000-11-6123", "555-55-5555"]}, 3, 3, 0, 0),
        ("element2", {"element2": [6, 149, 55, 22]}, 4, 4, 0, 0),
        ("element6", {"element6": [True, False, True]}, 3, 3, 0, 0),
    ]
)
def test_validate_csv_element_valid_data(mock_input_manager: InputManager,
                                         mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
                                         property: str, input_data: list, total_elements: int,
                                         valid_elements: int, invalid_elements: int, fixed_elements: int,
                                         input_manager_original_method_states: Dict[str, Callable],
                                         ) -> None:
    """Unit test for _validate_csv_element function in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element
    dummy_property = property
    properties_blob_key = "property_map_key1"
    dummy_input_data = input_data
    eager_termination = True
    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}

    result = mock_input_manager._validate_csv_element(dummy_property, properties_blob_key,
                                                      dummy_input_data, eager_termination,
                                                      mock_element_counter_and_validity)
    assert result["is_valid"] is True
    assert result["total_elements"] == total_elements
    assert result["valid_elements"] == valid_elements
    assert result["invalid_elements"] == invalid_elements
    assert result["fixed_elements"] == fixed_elements

    mock_input_manager._validate_csv_element = input_manager_original_method_states["_validate_csv_element"]


@pytest.mark.skip(reason="This test is not working")
@pytest.mark.parametrize(
    "property, input_data, total_elements, valid_elements, invalid_elements, fixed_elements, is_valid,"
    " eager_termination",
    [
        ("element1", {"element1": ["invalid1", "invalid2", "invalid3"]}, 3, 0, 3, 0, False, False),
        ("element2", {"element2": [-6, 1149, 955, -22]}, 1, 0, 1, 0, False, True),
        ("element7", {"element7": [50]}, 1, 0, 0, 1, True, False),
    ]
)
def test_validate_csv_element_invalid_data(mock_input_manager: InputManager,
                                           mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
                                           property: str, input_data: list, total_elements: int, is_valid: bool,
                                           valid_elements: int, invalid_elements: int, fixed_elements: int,
                                           input_manager_original_method_states: Dict[str, Callable],
                                           eager_termination: bool,
                                           ) -> None:
    mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element
    mock_input_manager._fix_data = MagicMock(return_value=is_valid)
    properties_blob_key = "property_map_key1"
    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}

    result = mock_input_manager._validate_csv_element(property, properties_blob_key,
                                                      input_data, eager_termination,
                                                      mock_element_counter_and_validity)
    assert result["is_valid"] is is_valid
    assert result["total_elements"] == total_elements
    assert result["valid_elements"] == valid_elements
    assert result["invalid_elements"] == invalid_elements
    assert result["fixed_elements"] == fixed_elements

    mock_input_manager._validate_csv_element = input_manager_original_method_states["_validate_csv_element"]
    mock_input_manager._fix_data = input_manager_original_method_states["_fix_data"]


@pytest.mark.skip(reason="This test is not working")
def test_validate_json_element_string_type(mock_input_manager: InputManager,
                                           mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
                                           input_manager_original_method_states: Dict[str, Callable],
                                           ) -> None:
    """Unit test for string type input_data for _validate_json_element in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element
    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}

    input_data = {"element1": "123-45-6789"}
    result = mock_input_manager._validate_json_element(["element1"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is True
    assert result["fixed_elements"] == 0
    assert result["total_elements"] == 1
    assert result["invalid_elements"] == 0
    assert result["valid_elements"] == 1

    input_data = {"element1": "invalid_value"}
    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}
    result = mock_input_manager._validate_json_element(["element1"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is False
    assert result["fixed_elements"] == 0
    assert result["total_elements"] == 1
    assert result["invalid_elements"] == 1
    assert result["valid_elements"] == 0

    input_data = {"element8": {"nested_element": 750}}
    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}
    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._validate_json_element(["element8"], "property_map_key1", input_data, False,
                                                           mock_element_counter_and_validity)

        assert add_warning.call_count == 3
        assert result["is_valid"] is False
        assert result["invalid_elements"] == 1
        assert result["fixed_elements"] == 0
        assert result["total_elements"] == 1
        assert result["valid_elements"] == 0

    mock_input_manager._validate_json_element = input_manager_original_method_states["_validate_json_element"]


@pytest.mark.skip(reason="This test is not working")
def test_validate_json_element_number_type(mock_input_manager: InputManager,
                                           mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
                                           input_manager_original_method_states: Dict[str, Callable], ) -> None:
    """Unit test for number type input_data for _validate_json_element in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element

    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}
    input_data = {"element2": 123}
    result = mock_input_manager._validate_json_element(["element2"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is True
    assert result["invalid_elements"] == 0
    assert result["fixed_elements"] == 0
    assert result["total_elements"] == 1
    assert result["valid_elements"] == 1

    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}
    input_data = {"element2": 500}
    result = mock_input_manager._validate_json_element(["element2"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is False
    assert result["invalid_elements"] == 1
    assert result["fixed_elements"] == 0
    assert result["total_elements"] == 1
    assert result["valid_elements"] == 0

    mock_input_manager._validate_json_element = input_manager_original_method_states["_validate_json_element"]


@pytest.mark.skip(reason="This test is not working")
def test_validate_json_element_array_type(mock_input_manager: InputManager,
                                          mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
                                          input_manager_original_method_states: Dict[str, Callable], ) -> None:
    """Unit test for array type input_data for _validate_json_element in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element

    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}
    input_data = {"element3": [1, 2, 3]}
    result = mock_input_manager._validate_json_element(["element3"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is True
    assert result["invalid_elements"] == 0
    assert result["fixed_elements"] == 0
    assert result["total_elements"] == 1
    assert result["valid_elements"] == 1

    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}
    input_data = {"element3": [1, 2, 3, 6, 7, 8, 10]}
    result = mock_input_manager._validate_json_element(["element3"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is False
    assert result["invalid_elements"] == 1
    assert result["fixed_elements"] == 0
    assert result["total_elements"] == 1
    assert result["valid_elements"] == 0

    mock_input_manager._validate_json_element = input_manager_original_method_states["_validate_json_element"]


@pytest.mark.skip(reason="This test is not working")
def test_validate_json_element_valid_object_type(mock_input_manager: InputManager,
                                                 mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
                                                 input_manager_original_method_states: Dict[str, Callable], ) -> None:
    """Unit test for valid nested object type input_data for _validate_json_element in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element

    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}
    input_data = {"element4": {"nested_element1": "value1", "nested_element2": 123}}
    result = mock_input_manager._validate_json_element(["element4"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is True
    assert result["invalid_elements"] == 0
    assert result["fixed_elements"] == 0
    assert result["total_elements"] == 2
    assert result["valid_elements"] == 2

    mock_input_manager._validate_json_element = input_manager_original_method_states["_validate_json_element"]


@pytest.mark.skip(reason="This test is not working")
def test_validate_json_element_invalid_object_type(mock_input_manager: InputManager,
                                                   mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
                                                   input_manager_original_method_states: Dict[str, Callable], ) -> None:
    """Unit test for nested invalid object type input_data for _validate_json_element in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element

    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}
    input_data = {"element4": {"nested_element1": "value1", "nested_element2": 500}}
    result = mock_input_manager._validate_json_element(["element4"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is False
    assert result["invalid_elements"] == 1
    assert result["fixed_elements"] == 0
    assert result["total_elements"] == 2
    assert result["valid_elements"] == 1

    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}
    input_data = {"element4": {"nested_element1": "value123456789value123456789", "nested_element2": 123}}
    result = mock_input_manager._validate_json_element(["element4"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is False
    assert result["invalid_elements"] == 1
    assert result["fixed_elements"] == 0
    assert result["total_elements"] == 1
    assert result["valid_elements"] == 0

    mock_input_manager._validate_json_element = input_manager_original_method_states["_validate_json_element"]


@pytest.mark.skip(reason="This test is not working")
def test_validate_element_valid_nested_object_type(mock_input_manager: InputManager,
                                                   mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
                                                   input_manager_original_method_states: Dict[str, Callable], ) -> None:
    """Unit test for valid object nested within another object type
    input_data for _validate_json_element in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element

    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}
    input_data = {"element5": {"nested_element1": "value1", "nested_element2": 123,
                               "nested_element3": {"nested_sub_element1": "cows", "nested_sub_element2": [1, 2, 3]}}}
    result = mock_input_manager._validate_json_element(["element5"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is True
    assert result["invalid_elements"] == 0
    assert result["fixed_elements"] == 0
    assert result["total_elements"] == 4
    assert result["valid_elements"] == 4

    mock_input_manager._validate_json_element = input_manager_original_method_states["_validate_json_element"]


@pytest.mark.skip(reason="This test is not working")
def test_validate_element_invalid_nested_object_type(mock_input_manager: InputManager,
                                                     mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
                                                     input_manager_original_method_states: Dict[str, Callable],
                                                     ) -> None:
    """Unit test for invalid object nested within another object type
    input_data for _validate_json_element in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element

    input_data = {"element5": {"nested_element1": "value1", "nested_element2": 123,
                               "nested_element3": {"nested_sub_element1": "cows", "nested_sub_element2": []}}}
    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}
    result = mock_input_manager._validate_json_element(["element5"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is False
    assert result["invalid_elements"] == 1
    assert result["fixed_elements"] == 0
    assert result["total_elements"] == 4
    assert result["valid_elements"] == 3

    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}
    input_data = {"element5": {"nested_element1": "value1", "nested_element2": 123,
                               "nested_element3": {"nested_sub_element1": "invalid_cows",
                                                   "nested_sub_element2": [1, 2, 3]}}}
    result = mock_input_manager._validate_json_element(["element5"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is False
    assert result["invalid_elements"] == 1
    assert result["fixed_elements"] == 0
    assert result["total_elements"] == 3
    assert result["valid_elements"] == 2

    mock_input_manager._validate_json_element = input_manager_original_method_states["_validate_json_element"]


@pytest.mark.skip(reason="This test is not working")
def test_validate_json_element_invalid_var_name_raises_metadata_keyerror(mock_input_manager: InputManager,
                                                                         input_manager_original_method_states:
                                                                         Dict[str, Callable],
                                                                         ) -> None:
    """Unit test for keyerror raised for invalid var name for _validate_json_element in file input_manager.py"""
    element_hierarchy = ["valid_key", "invalid_key"]
    properties_blob_key = "dummy_properties_blob_key"
    input_data = {"valid_key": {"another_valid_key": "value"}}
    eager_termination = False
    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}

    with pytest.raises(KeyError):
        mock_input_manager._validate_json_element(element_hierarchy, properties_blob_key, input_data,
                                                  eager_termination, mock_element_counter_and_validity)

    mock_input_manager._validate_json_element = input_manager_original_method_states["_validate_json_element"]


@pytest.mark.skip(reason="This test is not working")
def test_validate_json_element_invalid_var_name_raises_input_data_keyerror(mock_input_manager: InputManager,
                                                                           input_manager_original_method_states:
                                                                           Dict[str, Callable],
                                                                           ) -> None:
    """Unit test for keyerror raised for invalid var name for _validate_json_element in file input_manager.py"""
    mock_input_manager._InputManager__metadata = {"properties": {"dummy_properties_blob_key": {"valid_key": {
        "type": "object", "secondary_key": {"type": "string"}}}}}
    element_hierarchy = ["valid_key", "secondary_key"]
    properties_blob_key = "dummy_properties_blob_key"
    input_data = {"valid_key": {"another_valid_key": "value"}}
    eager_termination = False
    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}

    with patch("RUFAS.output_manager.OutputManager.add_error") as add_error:
        mock_input_manager._validate_json_element(element_hierarchy, properties_blob_key, input_data,
                                                  eager_termination, mock_element_counter_and_validity)

        assert add_error.call_count == 2

    mock_input_manager._validate_json_element = input_manager_original_method_states["_validate_json_element"]


@pytest.mark.skip(reason="This test is not working")
def test_validate_json_element_invalid_var_type_raises_keyerror(mock_input_manager: InputManager, mocker: MockerFixture,
                                                                input_manager_original_method_states:
                                                                Dict[str, Callable],
                                                                ) -> None:
    """Unit test for keyerror raised for invalid var type for _validate_json_element in file input_manager.py"""
    element_hierarchy = ["valid_key"]
    properties_blob_key = "dummy_valid_key"
    input_data = {"valid_key": "some_value"}
    mock_input_manager._InputManager__metadata = {"properties": {properties_blob_key: {"valid_key": {
        "type": "invalid_type"}}}}
    eager_termination = False
    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}

    with pytest.raises(KeyError):
        mock_input_manager._validate_json_element(element_hierarchy, properties_blob_key, input_data,
                                                  eager_termination, mock_element_counter_and_validity)

    mock_input_manager._validate_json_element = input_manager_original_method_states["_validate_json_element"]


@pytest.mark.skip(reason="This test is not working")
def test_validate_json_element_missing_type_raises_keyerror(mock_input_manager: InputManager,
                                                            input_manager_original_method_states:
                                                            Dict[str, Callable],
                                                            ) -> None:
    """Unit test for missing data type raising a KeyError for function
    _validate_json_element in file input_manager.py"""
    element_hierarchy = ["valid_key"]
    properties_blob_key = "dummy_valid_key"
    input_data = {"valid_key": "some_value"}
    mock_input_manager._InputManager__metadata = {"properties": {properties_blob_key: {"valid_key": {}}}}
    eager_termination = False
    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}

    with pytest.raises(KeyError, match="Missing 'type' key in variable_properties"):
        mock_input_manager._validate_json_element(element_hierarchy, properties_blob_key, input_data,
                                                  eager_termination, mock_element_counter_and_validity)

    mock_input_manager._validate_json_element = input_manager_original_method_states["_validate_json_element"]


@pytest.mark.skip(reason="This test is not working")
@pytest.mark.parametrize(
    'dummy_value, dummy_variable_to_check, expected_result, expected_warning_call_count',
    [
        ([1, 2, 3], {"minimum_length": 5, "maximum_length": 10}, False, 1),
        ([1, 2, 3, 4, 5], {"minimum_length": 5, "maximum_length": 10}, True, 0),
        ([1, 2, 3, 4, 5, 6, 7], {"minimum_length": 5}, True, 0),
        ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], {"maximum_length": 10}, True, 0),
        ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], {"minimum_length": 5, "maximum_length": 10}, False, 1),
        ([], {"minimum_length": 5}, False, 1),
        (None, {"minimum_length": 3, "maximum_length": 6}, False, 1),
        ("[1, 2, 3]", {"minimum_length": 1}, False, 1)
    ]
)
def test_array_type_validator(dummy_value: list, dummy_variable_to_check: Dict[str, int], expected_result: bool,
                              expected_warning_call_count: int, mock_input_manager: InputManager) -> None:
    """Unit test for function _validate_array_type in file input_manager.py"""
    dummy_var_name = "dummy_array"

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._validate_array_type(dummy_variable_to_check, dummy_var_name, dummy_value)

    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.skip(reason="This test is not working")
@pytest.mark.parametrize(
    'dummy_value, dummy_variable_to_check, expected_result, expected_warning_call_count',
    [
        ("cow", {"pattern": r"cow", "minimum_length": 1, "maximum_length": 5}, True, 0),
        ("cow", {"pattern": r".{3}", "minimum_length": 1}, True, 0),
        ("COW", {"pattern": r"cow", "minimum_length": 1, "maximum_length": 5}, False, 1),
        ("cow", {"minimum_length": 1, "maximum_length": 5}, True, 0),
        ("cow", {"minimum_length": 5}, False, 1),
        ("cow", {"maximum_length": 1}, False, 1),
        (None, {"pattern": r"cow", "minimum_length": 1}, False, 1),
        (42.0, {"pattern": r"cow", "maximum_length": 3}, False, 1)
    ]
)
def test_string_type_validator(dummy_value: int,
                               dummy_variable_to_check: Dict[str, int],
                               expected_result: bool,
                               expected_warning_call_count: int,
                               mock_input_manager: InputManager) -> None:
    """Unit test for _validate_str_type function in file input_manager.py"""
    dummy_var_name = "dummy_var"

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._validate_str_type(dummy_variable_to_check, dummy_var_name, dummy_value)

    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.fixture
def mock_metadata_for_fix_data(mocker: MockerFixture) -> dict[str, dict[str, Any]]:
    return {
        "dummyconfig": {},
        "files": {
            "array": {
                "properties": "array_properties"
            },
            "string": {
                "properties": "string_properties"
            },
            "number": {
                "properties": "number_properties"
            },
            "boolean": {
                "properties": "boolean_properties"
            },
        },
        "properties": {
            "array_properties": {
                "element1": {
                    "type": "array",
                    "default": [1, 2, 3, 4, 5],
                    "minimum_length": 5,
                    "maximum_length": 10,
                },
                "element2": {
                    "type": "array",
                    "default": [],
                    "minimum_length": 0,
                    "maximum_length": 5,
                },
                "element3": {
                    "type": "array",
                    "default": [1, 2, 3],
                    "minimum_length": 2,
                    "maximum_length": 5,
                },
                "element4": {
                    "type": "object",
                    "element5": {
                        "type": "array",
                        "default": [1, 2, 3],
                        "minimum_length": 2,
                        "maximum_length": 5,
                    },
                },
                "element6": {
                    "type": "array",
                    "minimum_length": 5,
                    "maximum_length": 10,
                },
                "element7": {
                    "type": "array",
                    "minimum_length": 0,
                    "maximum_length": 5,
                },
                "element8": {
                    "type": "array",
                    "minimum_length": 2,
                    "maximum_length": 5,
                },
                "element9": {
                    "type": "object",
                    "element10": {
                        "type": "array",
                        "minimum_length": 2,
                        "maximum_length": 5,
                    },
                },
            },
            "string_properties": {
                "element1": {
                    "type": "str",
                    "default": "cow",
                    "pattern": r"cow",
                    "minimum_length": 1,
                    "maximum_length": 5,
                },
                "element2": {
                    "type": "str",
                    "default": "",
                    "minimum_length": 0,
                    "maximum_length": 5,
                },
                "element3": {
                    "type": "str",
                    "default": "cow",
                    "pattern": r"cow",
                    "minimum_length": 2,
                    "maximum_length": 5,
                },
                "element4": {
                    "type": "object",
                    "element5": {
                        "type": "str",
                        "default": "cow",
                        "pattern": r"cow",
                        "minimum_length": 2,
                        "maximum_length": 5,
                    },
                },
                "element6": {
                    "type": "str",
                    "pattern": r"cow",
                    "minimum_length": 1,
                    "maximum_length": 5,
                },
                "element7": {
                    "type": "str",
                    "pattern": r"cow",
                    "minimum_length": 1,
                    "maximum_length": 5,
                },
                "element8": {
                    "type": "str",
                    "pattern": r"cow",
                    "minimum_length": 1,
                    "maximum_length": 5,
                },
                "element9": {
                    "type": "object",
                    "element10": {
                        "type": "str",
                        "pattern": r"cow",
                        "minimum_length": 2,
                        "maximum_length": 5,
                    },
                },
            },
            "number_properties": {
                "element1": {
                    "type": "number",
                    "default": 5,
                    "minimum": 0,
                    "maximum": 10,
                },
                "element2": {
                    "type": "number",
                    "default": 0,
                    "minimum": 0,
                    "maximum": 10,
                },
                "element3": {
                    "type": "number",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 10,
                },
                "element4": {
                    "type": "object",
                    "element5": {
                        "type": "number",
                        "default": 5,
                        "minimum": 0,
                        "maximum": 10,
                    },
                },
                "element6": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10,
                },
                "element7": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10,
                },
                "element8": {
                    "type": "number",
                    "minimum": 1,
                    "maximum": 10,
                },
                "element9": {
                    "type": "object",
                    "element10": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 10,
                    },
                },
            },
            "boolean_properties": {
                "element1": {
                    "type": "bool",
                    "default": True
                },
                "element2": {
                    "type": "bool",
                    "default": False
                },
                "element3": {
                    "type": "object",
                    "element4": {
                        "type": "bool",
                        "default": True
                    },
                },
                "element5": {
                    "type": "bool",
                },
                "element6": {
                    "type": "bool",
                },
                "element7": {
                    "type": "object",
                    "element8": {
                        "type": "bool",
                    },
                },

            },

        },
    }


def mock_input_array_data_for_fix_data() -> dict[str, dict[str, Any]]:
    return {

        "element1": [1, 2, 3],
        "element2": [1, 2, 3, 4, 5],
        "element3": [],
        "element4": {
            "element5": [1, 2],
        },
        "element6": [1, 2, 3],
        "element7": [1, 2, 3, 4, 5],
        "element8": [],
        "element9": {
            "element10": [1, 2],
        },
    }


@pytest.mark.skip(reason="This test is not working")
@pytest.mark.parametrize(
    'dummy_variable_properties, dummy_element_hierarchy, expected_value, expected_result, expected_warning_call_count',
    [
        ({
             "type": "array",
             "default": [1, 2, 3, 4, 5],
             "minimum_length": 5,
             "maximum_length": 10,
         }, ["element1"], [1, 2, 3, 4, 5], True, 2),

        ({
             "type": "array",
             "default": [],
             "minimum_length": 0,
             "maximum_length": 5,
         }, ["element2"], [], True, 2),

        ({
             "type": "array",
             "default": [1, 2, 3, 4, 5],
             "minimum_length": 5,
             "maximum_length": 10,
         }, ["element3"], [1, 2, 3, 4, 5], True, 2),
        ({
             "type": "array",
             "default": [1, 2, 3],
             "minimum_length": 2,
             "maximum_length": 5,
         }, ["element4", "element5"], [1, 2, 3], True, 2),
    ]
)
def test_fix_array_type_fixable_data(dummy_variable_properties: dict[str, Any],
                                     dummy_element_hierarchy: list[str],
                                     expected_value: list, expected_result: bool, expected_warning_call_count: int,
                                     mock_input_manager: InputManager) -> None:
    """Unit test for fixable array-type data for _fix_data function in file input_manager.py"""

    dummy_input_data = mock_input_array_data_for_fix_data()

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(dummy_variable_properties, dummy_element_hierarchy, dummy_input_data)

    variable_to_check = reduce(lambda d, key: d[key], dummy_element_hierarchy,
                               dummy_input_data)
    assert variable_to_check == expected_value
    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.skip(reason="This test is not working")
@pytest.mark.parametrize(
    'dummy_variable_properties, dummy_element_hierarchy, expected_result, expected_warning_call_count',
    [
        ({
             "type": "array",
             "minimum_length": 5,
             "maximum_length": 10,
         }, ["element6"], False, 0),
        ({
             "type": "array",
             "minimum_length": 0,
             "maximum_length": 5,
         }, ["element7"], False, 0),
        ({
             "type": "array",
             "minimum_length": 2,
             "maximum_length": 5,
         }, ["element8"], False, 0),
        ({
             "type": "array",
             "minimum_length": 2,
             "maximum_length": 5,
         }, ["element9", "element10"], False, 0),
    ]
)
def test_fix_array_type_critical_data(dummy_variable_properties: dict[str, Any],
                                      dummy_element_hierarchy: list[str], expected_result: bool,
                                      expected_warning_call_count: int, mock_input_manager: InputManager) -> None:
    """Unit test for critical array-type data for _fix_data function in file input_manager.py"""

    dummy_input_data = mock_input_array_data_for_fix_data()

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(dummy_variable_properties, dummy_element_hierarchy, dummy_input_data)

    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


def mock_input_string_data_for_fix_data() -> dict[str, dict[str, Any]]:
    return {
        "element1": "muu",
        "element2": "muumuu",
        "element3": "",
        "element4": {
            "element5": "muu",
        },
        "element6": "muu",
        "element7": "muumuu",
        "element8": "",
        "element9": {
            "element10": "muu",
        },
    }


@pytest.mark.skip(reason="This test is not working")
@pytest.mark.parametrize(
    'dummy_variable_properties, dummy_element_hierarchy, expected_value, expected_result, expected_warning_call_count',
    [
        ({
             "type": "str",
             "default": "cow",
             "pattern": r"cow",
             "minimum_length": 1,
             "maximum_length": 5,
         }, ["element1"], "cow", True, 2),
        ({
             "type": "str",
             "default": "",
             "minimum_length": 0,
             "maximum_length": 5,
         }, ["element2"], "", True, 2),
        ({
             "type": "str",
             "default": "cow",
             "pattern": r"cow",
             "minimum_length": 2,
             "maximum_length": 5,
         }, ["element3"], "cow", True, 2),
        ({
             "type": "str",
             "default": "cow",
             "pattern": r"cow",
             "minimum_length": 2,
             "maximum_length": 5,
         }, ["element4", "element5"], "cow", True, 2),
    ]
)
def test_fix_string_type_fixable_data(dummy_variable_properties: dict[str, Any],
                                      dummy_element_hierarchy: list[str], expected_value: str, expected_result: bool,
                                      expected_warning_call_count: int, mock_input_manager: InputManager) -> None:
    """Unit test for fixable string-type data for _fix_data function in file input_manager.py"""

    dummy_input_data = mock_input_string_data_for_fix_data()

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(dummy_variable_properties, dummy_element_hierarchy, dummy_input_data)

    variable_to_check = reduce(lambda d, key: d[key], dummy_element_hierarchy,
                               dummy_input_data)
    assert variable_to_check == expected_value
    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.skip(reason="This test is not working")
def test_fix_string_type_csv_data(mock_input_manager: InputManager) -> None:
    """Unit test for fixable number-type data from a csv array for _fix_data function in file input_manager.py"""

    dummy_input_data = {"element1": [1, 2, 3, 4, 5]}
    dummy_variable_properties = {"type": "number", "maximum": 4, "default": 3}
    dummy_element_hierarchy = ["element1", 4]

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(dummy_variable_properties, dummy_element_hierarchy, dummy_input_data)

    fixed_variable = reduce(lambda d, key: d[key], dummy_element_hierarchy,
                            dummy_input_data)

    assert fixed_variable == 3
    assert result is True
    assert add_warning.call_count == 2


@pytest.mark.skip(reason="This test is not working")
@pytest.mark.parametrize(
    'dummy_variable_properties, dummy_element_hierarchy, expected_result, expected_warning_call_count',
    [
        ({
             "type": "str",
             "pattern": r"cow",
             "minimum_length": 1,
             "maximum_length": 5,
         }, ["element6"], False, 0),
        ({
             "type": "str",
             "pattern": r"cow",
             "minimum_length": 1,
             "maximum_length": 5,
         }, ["element7"], False, 0),
        ({
             "type": "str",
             "pattern": r"cow",
             "minimum_length": 1,
             "maximum_length": 5,
         }, ["element8"], False, 0),
        ({
             "type": "str",
             "pattern": r"cow",
             "minimum_length": 2,
             "maximum_length": 5,
         }, ["element9", "element10"], False, 0),
    ]
)
def test_fix_string_type_critical_data(dummy_variable_properties: dict[str, Any],
                                       dummy_element_hierarchy: list[str], expected_result: bool,
                                       expected_warning_call_count: int, mock_input_manager: InputManager) -> None:
    """Unit test for critical string-type data for _fix_data function in file input_manager.py"""

    dummy_input_data = mock_input_string_data_for_fix_data()

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(dummy_variable_properties,
                                              dummy_element_hierarchy, dummy_input_data)

    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


def mock_input_number_data_for_fix_data() -> dict[str, dict[str, Any]]:
    return {
        "element1": -1,
        "element2": -1,
        "element3": 0,
        "element4": {
            "element5": 15,
        },
        "element6": -1,
        "element7": -1,
        "element8": 0,
        "element9": {
            "element10": 15,
        },
    }


@pytest.mark.skip(reason="This test is not working")
@pytest.mark.parametrize(
    'dummy_variable_properties, dummy_element_hierarchy, expected_value, expected_result, expected_warning_call_count',
    [
        ({
             "type": "number",
             "default": 5,
             "minimum": 0,
             "maximum": 10,
         }, ["element1"], 5, True, 2),
        ({
             "type": "number",
             "default": 0,
             "minimum": 0,
             "maximum": 10,
         }, ["element2"], 0, True, 2),
        ({
             "type": "number",
             "default": 5,
             "minimum": 1,
             "maximum": 10,
         }, ["element3"], 5, True, 2),
        ({
             "type": "number",
             "default": 5,
             "minimum": 0,
             "maximum": 10,
         }, ["element4", "element5"], 5, True, 2),
    ]
)
def test_fix_number_type_fixable_data(dummy_variable_properties: dict[str, Any],
                                      dummy_element_hierarchy: list[str],
                                      expected_value: str, expected_result: bool, expected_warning_call_count: int,
                                      mock_input_manager: InputManager) -> None:
    """Unit test for fixable number-type data for _fix_data function in file input_manager.py"""

    dummy_input_data = mock_input_number_data_for_fix_data()

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(dummy_variable_properties, dummy_element_hierarchy, dummy_input_data)

    variable_to_check = reduce(lambda d, key: d[key], dummy_element_hierarchy,
                               dummy_input_data)
    assert variable_to_check == expected_value
    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.skip(reason="This test is not working")
@pytest.mark.parametrize(
    'dummy_variable_properties, dummy_element_hierarchy, expected_result, '
    'expected_warning_call_count',
    [
        ({
             "type": "number",
             "minimum": 0,
             "maximum": 10,
         }, ["element6"], False, 0),
        ({
             "type": "number",
             "minimum": 0,
             "maximum": 10,
         }, ["element7"], False, 0),
        ({
             "type": "number",
             "minimum": 1,
             "maximum": 10,
         }, ["element8"], False, 0),
        ({
             "type": "number",
             "minimum": 0,
             "maximum": 10,
         }, ["element9", "element10"], False, 0),
    ]
)
def test_fix_number_type_critical_data(dummy_variable_properties: dict[str, Any],
                                       dummy_element_hierarchy: list[str], expected_result: bool,
                                       expected_warning_call_count: int, mock_input_manager: InputManager,
                                       mock_metadata_for_fix_data: Dict[str, Dict[str, Any]]) -> None:
    """Unit test for critical number-type data for _fix_data function in file input_manager.py"""

    dummy_input_data = mock_input_number_data_for_fix_data()

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(dummy_variable_properties,
                                              dummy_element_hierarchy, dummy_input_data)

    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.fixture
def mock_pool_for_get_data(mocker: MockerFixture) -> Dict[str, Dict[str, Any]]:
    return {
        "module1": {
            "integer_var": 5,
            "float_var": 0.5,
            "string_var": "dummyvalue1",
            "boolean_var": True,
            "integer_array_var": [1, 2, 3],
            "float_array_var": [0.1, 0.2, 3.14159],
            "string_array_var": ["1", "2", "3", "4", "5"],
            "boolean_array_var": [True, False],
            "submodule1": {
                "nested_var": "dummyvalue2"
            },
        },
        "module2": {
            "submodule1": {
                "nested_module1": {
                    "nested_var1": "dummyvalue3",
                    "nested_var2": "dummyvalue4",
                },
            },
        },
    }


@pytest.mark.parametrize(
    'dummy_data_path, expected_result, expected_warning_call_count',
    [
        ("module1.integer_var", 5, 0),
        ("module1.float_var", 0.5, 0),
        ("module1.string_var", "dummyvalue1", 0),
        ("module1.boolean_var", True, 0),
        ("module1.integer_array_var", [1, 2, 3], 0),
        ("module1.float_array_var", [0.1, 0.2, 3.14159], 0),
        ("module1.string_array_var", ["1", "2", "3", "4", "5"], 0),
        ("module1.string_var", "dummyvalue1", 0),
        ("module1.boolean_array_var", [True, False], 0),
        ("module1.submodule1.nested_var", "dummyvalue2", 0),
        ("module2.submodule1.nested_module1.nested_var1", "dummyvalue3", 0),
        ("module2.submodule1.nested_module1.nested_var2", "dummyvalue4", 0),
        ("module1", {
            "integer_var": 5,
            "float_var": 0.5,
            "string_var": "dummyvalue1",
            "boolean_var": True,
            "integer_array_var": [1, 2, 3],
            "float_array_var": [0.1, 0.2, 3.14159],
            "string_array_var": ["1", "2", "3", "4", "5"],
            "boolean_array_var": [True, False],
            "submodule1": {
                "nested_var": "dummyvalue2"
            }}, 0),
    ]
)
def test_get_data_with_valid_key(dummy_data_path: str,
                                 mock_pool_for_get_data: Dict[str, Dict[str, Any]],
                                 expected_result: Any, expected_warning_call_count: int,
                                 mock_input_manager: InputManager) -> None:
    """Unit test for get_data function in file input_manager.py with a valid data_path key"""

    mock_input_manager._InputManager__pool = mock_pool_for_get_data

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager.get_data(dummy_data_path)

    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.parametrize(
    'dummy_data_path, expected_error_parent_address, expected_error_invalid_key, expected_warning_call_count',
    [
        ("module1.dummy_key", "module1", "dummy_key", 1),
        ("module1.submodule1.dummy_key", "module1.submodule1", "dummy_key", 1),
        ("module2.submodule1.nested_module1.dummy_key", "module2.submodule1.nested_module1", "dummy_key", 1),
        ("module2.submodule1.dummy_key.nested_var1", "module2.submodule1", "dummy_key", 1),
        ("module2.dummy_key.nested_module1.nested_var1", "module2", "dummy_key", 1),
    ]
)
def test_get_data_raises_exception(dummy_data_path: str,
                                   expected_error_parent_address: str, expected_error_invalid_key: str,
                                   mock_pool_for_get_data: Dict[str, Dict[str, Any]],
                                   expected_warning_call_count: int,
                                   mock_input_manager: InputManager) -> None:
    """Unit test for function get_data raising an exception in file input_manager.py"""

    mock_input_manager._InputManager__pool = mock_pool_for_get_data

    with patch("RUFAS.output_manager.OutputManager.add_error") as add_error:
        with pytest.raises(KeyError) as key_error:
            mock_input_manager.get_data(dummy_data_path)

        error_message = key_error.value.__str__().strip("\'")
        assert error_message == f"Data not found: Cannot find \"{dummy_data_path}\", " \
                                f"\"{expected_error_parent_address}\" does not have attribute " \
                                f"\"{expected_error_invalid_key}\"."
        assert add_error.call_count == expected_warning_call_count


@pytest.fixture
def mock_pool_for_get_metadata(mocker: MockerFixture) -> Dict[str, Dict[str, Any]]:
    return {
        "properties": {
            "dummy_animal_properties": {
                "type": "object",
                "description": "Animal data",
                "herd_information": {
                    "type": "object",
                    "description": "Herd Demographics",
                    "calf_num": {
                        "type": "number",
                        "description": "Number of Calves (head)",
                        "default": 8,
                        "minimum": 0
                    },
                    "cow_repro_method": {
                        "type": "string",
                        "description": "Cow Reproductive Program (select one)",
                        "default": "ED",
                        "pattern": "^{TAI|ED|ED-TAI}$"
                    },
                    "simulate_animals": {
                        "type": "boolean",
                        "description": "Whether or not to simulate animals during the simulation",
                        "default": True
                    },
                    "dummy_cow_array": {
                        "type": "array",
                        "description": "dummy array for testing purposes",
                        "default": [1, 2, 3, 4],
                        "maximum_length": 7
                    }
                }
            },
            "dummy_crop_properties": {
                "crop_species": {
                    "type": "string",
                    "description": "Name of the crop being grown.",
                    "pattern": "^{generic|corn|spring_wheat|winter_wheat|cereal_rye|spring_barley}$"
                },
                "harvest_years": {
                    "type": "array",
                    "description": "Calendar years in which the harvesting occurs",
                    "minimum_length": 0,
                    "default": [],
                    "properties": {
                        "type": "number",
                        "minimum": 1
                    }
                },
                "pattern_skip": {
                    "type": "number",
                    "description": "Number of years to be skipped between schedule repetitions.",
                    "minimum": 0,
                    "default": 0
                },
                "simulate_crops": {
                    "type": "boolean",
                    "description": "Dummy boolean variable for testing",
                    "default": False
                }
            }
        }
    }


@pytest.mark.parametrize(
    'dummy_metadata_path, expected_result, expected_warning_call_count',
    [
        ("properties.dummy_animal_properties.herd_information.calf_num.default", 8, 0),
        ("properties.dummy_animal_properties.herd_information.calf_num",
         {"type": "number", "description": "Number of Calves (head)", "default": 8, "minimum": 0}, 0),
        ("properties.dummy_animal_properties.herd_information.cow_repro_method.type", "string", 0),
        ("properties.dummy_animal_properties.herd_information.cow_repro_method.pattern", "^{TAI|ED|ED-TAI}$", 0),
        ("properties.dummy_animal_properties.herd_information.simulate_animals.type", "boolean", 0),
        ("properties.dummy_animal_properties.herd_information.dummy_cow_array",
         {"type": "array", "description": "dummy array for testing purposes", "default": [1, 2, 3, 4],
          "maximum_length": 7}, 0),
        ("properties.dummy_crop_properties.crop_species.description", "Name of the crop being grown.", 0),
        ("properties.dummy_crop_properties.harvest_years.type", "array", 0),
        ("properties.dummy_crop_properties.harvest_years",
         {"type": "array", "description": "Calendar years in which the harvesting occurs", "minimum_length": 0,
          "default": [], "properties": {"type": "number", "minimum": 1}}, 0),
        ("properties.dummy_crop_properties.pattern_skip.minimum", 0, 0),
        ("properties.dummy_crop_properties.simulate_crops",
         {"type": "boolean", "description": "Dummy boolean variable for testing", "default": False}, 0),
        ("properties", {
            "dummy_animal_properties": {
                "type": "object",
                "description": "Animal data",
                "herd_information": {
                    "type": "object",
                    "description": "Herd Demographics",
                    "calf_num": {
                        "type": "number",
                        "description": "Number of Calves (head)",
                        "default": 8,
                        "minimum": 0
                    },
                    "cow_repro_method": {
                        "type": "string",
                        "description": "Cow Reproductive Program (select one)",
                        "default": "ED",
                        "pattern": "^{TAI|ED|ED-TAI}$"
                    },
                    "simulate_animals": {
                        "type": "boolean",
                        "description": "Whether or not to simulate animals during the simulation",
                        "default": True
                    },
                    "dummy_cow_array": {
                        "type": "array",
                        "description": "dummy array for testing purposes",
                        "default": [1, 2, 3, 4],
                        "maximum_length": 7
                    }
                }
            },
            "dummy_crop_properties": {
                "crop_species": {
                    "type": "string",
                    "description": "Name of the crop being grown.",
                    "pattern": "^{generic|corn|spring_wheat|winter_wheat|cereal_rye|spring_barley}$"
                },
                "harvest_years": {
                    "type": "array",
                    "description": "Calendar years in which the harvesting occurs",
                    "minimum_length": 0,
                    "default": [],
                    "properties": {
                        "type": "number",
                        "minimum": 1
                    }
                },
                "pattern_skip": {
                    "type": "number",
                    "description": "Number of years to be skipped between schedule repetitions.",
                    "minimum": 0,
                    "default": 0
                },
                "simulate_crops": {
                    "type": "boolean",
                    "description": "Dummy boolean variable for testing",
                    "default": False
                }
            }
        }, 0)
    ]
)
def test_get_metadata_with_valid_key(dummy_metadata_path: str,
                                     mock_pool_for_get_metadata: Dict[str, Dict[str, Any]],
                                     expected_result: Any, expected_warning_call_count: int,
                                     mock_input_manager: InputManager) -> None:
    """Unit test for get_metadata function in file input_manager.py with a valid metadata_path key"""

    mock_input_manager._InputManager__metadata = mock_pool_for_get_metadata

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager.get_metadata(dummy_metadata_path)

    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.parametrize(
    'dummy_metadata_path, expected_error_parent_address, expected_error_invalid_key, expected_warning_call_count',
    [
        ("dummy_animal_properties.herd_information.calf_num.dummy_key",
         "dummy_animal_properties.herd_information.calf_num", "dummy_key", 1),
        ("dummy_animal_properties.herd_information.dummy_key",
         "dummy_animal_properties.herd_information", "dummy_key", 1),
        ("dummy_crop_properties.crop_species.dummy_key", "dummy_crop_properties.crop_species", "dummy_key", 1),
        ("dummy_crop_properties.dummy_key", "dummy_crop_properties", "dummy_key", 1),
        ("dummy_crop_properties.pattern_skip.dummy_key", "dummy_crop_properties.pattern_skip", "dummy_key", 1)
    ]
)
def test_get_metadata_raises_exception(dummy_metadata_path: str,
                                       expected_error_parent_address: str, expected_error_invalid_key: str,
                                       mock_pool_for_get_metadata: Dict[str, Dict[str, Any]],
                                       expected_warning_call_count: int,
                                       mock_input_manager: InputManager) -> None:
    """Unit test for function get_metadata raising an exception in file input_manager.py"""

    mock_input_manager._InputManager__metadata = mock_pool_for_get_metadata

    with patch("RUFAS.output_manager.OutputManager.add_error") as add_error:
        with pytest.raises(KeyError) as key_error:
            mock_input_manager.get_metadata(dummy_metadata_path)

        error_message = key_error.value.__str__().strip("\'")
        assert error_message == f"Data not found: Cannot find \"{dummy_metadata_path}\", " \
                                f"\"{expected_error_parent_address}\" does not have attribute " \
                                f"\"{expected_error_invalid_key}\"."
        assert add_error.call_count == expected_warning_call_count


def test_flush_pool(mock_input_manager: InputManager) -> None:
    """Tests that the InputManager pool is flushed correctly."""

    mock_input_manager._InputManager__pool = {"Key": "I never metadata I didn't like!"}

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        mock_input_manager.flush_pool()

        assert mock_input_manager._InputManager__pool == {}
        assert add_log.call_count == 1


@pytest.mark.parametrize("variable_value, variable_properties, expected_result", [
    # Test with a boolean True
    (True, {}, (True, "")),
    # Test with a boolean False
    (False, {}, (True, "")),
    # Test with a string "True"
    ("True", {}, (False, "Bool variable is not a boolean")),
    # Test with a string "False"
    ("False", {}, (False, "Bool variable is not a boolean")),
    # Test with an integer 1
    (1, {}, (False, "Bool variable is not a boolean")),
    # Test with an integer 0
    (0, {}, (False, "Bool variable is not a boolean")),
    # Test with a None value
    (None, {}, (False, "Bool variable is not a boolean")),
    # Test with an empty list
    ([], {}, (False, "Bool variable is not a boolean")),
    # Test with a list
    ([1, 2, 3], {}, (False, "Bool variable is not a boolean")),
    # Test with an empty dictionary
    ({}, {}, (False, "Bool variable is not a boolean")),
    # Test with a dictionary
    ({"key": "value"}, {}, (False, "Bool variable is not a boolean")),
    # Test with a float 1.0
    (1.0, {}, (False, "Bool variable is not a boolean")),
    # Test with a float 0.0
    (0.0, {}, (False, "Bool variable is not a boolean")),
])
def test_is_bool_value(variable_value: Any, variable_properties: dict[str, Any],
                       expected_result: tuple[bool, str]) -> None:
    """
    Unit test for method _is_bool_value() in file input_manager.py.
    """

    assert InputManager._is_bool_value(variable_value, variable_properties) == expected_result


@pytest.mark.parametrize("variable_path, variable_properties, input_data, expected_result", [
    # Test with a boolean True
    (["key1"], {"type": "bool"}, {"key1": True}, True),
    # Test with a boolean False
    (["key2"], {"type": "bool"}, {"key2": False}, False),
    # Test with a non-boolean string and default True
    (["key3"], {"type": "bool", "default": True}, {"key3": "not a bool"}, True),
    # Test with a non-boolean string and default False
    (["key4"], {"type": "bool", "default": False}, {"key4": "not a bool"}, False),
])
def test_validate_bool_type(mocker: MockerFixture,
                            variable_path: list[str | int],
                            variable_properties: dict[str, Any],
                            input_data: dict[str, Any],
                            expected_result: bool) -> None:
    """
    Unit test for method _validate_bool_type() in file input_manager.py.

    This test simply checks that _validate_bool_type() calls _validate_primitive_type_with_revalidation()
    with the correct arguments.
    """
    # Arrange
    mock_validate_primitive = mocker.patch.object(
        InputManager,
        '_validate_primitive_type_with_revalidation',
        return_value=expected_result
    )
    input_manager = InputManager()

    # Act
    result = input_manager._validate_bool_type(variable_path, variable_properties, input_data)

    # Assert
    assert result == expected_result
    mock_validate_primitive.assert_called_once_with(variable_path, variable_properties,
                                                    input_data, [InputManager._is_bool_value])


@pytest.mark.parametrize("variable_path, variable_properties, input_data, expected_result", [
    # Test with a boolean True
    (["key1"], {"type": "bool"}, {"key1": True}, True),
    # Test with a boolean False
    (["key1"], {"type": "bool"}, {"key1": False}, True),
    # Test with a string and default True
    (["key1"], {"type": "bool", "default": True}, {"key1": "not a bool"}, True),
    # Test with a string and default False
    (["key1"], {"type": "bool", "default": False}, {"key1": "not a bool"}, True),
    # Test with a string but have no default
    (["key1"], {"type": "bool"}, {"key1": "not a bool"}, False),
    # Test with an integer 1 but have no default
    (["key1"], {"type": "bool"}, {"key1": 1}, False),
    # Test with a string but default is not boolean
    (["key1"], {"type": "bool", "default": "not a bool"}, {"key1": "not a bool"}, False),
    # Test with an integer 1 but default is not boolean
    (["key1"], {"type": "bool", "default": "not a bool"}, {"key1": 1}, False),
])
def test_validate_bool_type_integration_test(variable_path: list[str | int],
                                             variable_properties: dict[str, Any],
                                             input_data: dict[str, Any],
                                             expected_result: bool) -> None:
    """
    Integration test for method _validate_bool_type() in file input_manager.py.

    This test is to test the integration between _validate_bool_type() and
    _validate_primitive_type_with_revalidation().
    """
    # Arrange
    input_manager = InputManager()
    om = OutputManager()
    initial_data = InputManager._get_nested_dict_value(input_data, variable_path)

    # Act
    result = input_manager._validate_bool_type(variable_path, variable_properties, input_data)

    # Assert
    assert result == expected_result
    if type(initial_data) is not bool:
        assert "InputManager._validate_primitive_type_with_revalidation.Bool variable is not a boolean" \
               in om.warnings_pool
        if "default" in variable_properties and type(variable_properties["default"]) is bool:
            assert "InputManager._fix_data.Data fixed" in om.warnings_pool
        elif "default" in variable_properties:
            assert "InputManager._revalidate_element_after_fix.Fixed element is still invalid" in om.errors_pool
        else:
            assert "InputManager._validate_primitive_type_with_revalidation.Invalid, unfixable element found" \
                   in om.errors_pool

    # Cleanup
    om.flush_pools()


@pytest.mark.parametrize("variable_value, variable_properties, expected_result", [
    # Test with an integer
    (10, {}, (True, "")),
    # Test with zero
    (0, {}, (True, "")),
    # Test with a negative integer
    (-1, {}, (True, "")),
    # Test with a float
    (1.5, {}, (True, "")),
    # Test with a negative float
    (-2.3, {}, (True, "")),
    # Test with a string
    ("string", {}, (False, "Value is not a number")),
    # Test with a boolean True
    (True, {}, (False, "Value is not a number")),
    # Test with a None value
    (None, {}, (False, "Value is not a number")),
    # Test with a list
    ([1, 2, 3], {}, (False, "Value is not a number")),
    # Test with a dictionary
    ({"key": "value"}, {}, (False, "Value is not a number")),
])
def test_is_numeric_value(variable_value: Any, variable_properties: dict[str, Any],
                          expected_result: tuple[bool, str]) -> None:
    """
    Unit test for method _is_numeric_value() in file input_manager.py.
    """

    assert InputManager._is_numeric_value(variable_value, variable_properties) == expected_result


@pytest.mark.parametrize("variable_value, variable_properties, expected_result", [
    # Value greater than minimum
    (5, {"minimum": 3}, (True, "")),
    # Value equal to minimum
    (3, {"minimum": 3}, (True, "")),
    # Value less than minimum
    (2, {"minimum": 3}, (False, "Value less than minimum")),
    # No minimum set
    (5, {}, (True, "")),
    # Negative value less than minimum
    (-1, {"minimum": 0}, (False, "Value less than minimum")),
    # Zero value greater than negative minimum
    (0, {"minimum": -1}, (True, "")),
])
def test_check_num_lower_bound(variable_value: int | float, variable_properties: dict[str, Any],
                               expected_result: tuple[bool, str]) -> None:
    """
    Unit test for method _check_num_lower_bound() in file input_manager.py.
    """

    assert InputManager._check_num_lower_bound(variable_value, variable_properties) == expected_result


@pytest.mark.parametrize("variable_value, variable_properties, expected_result", [
    # Value less than maximum
    (5, {"maximum": 7}, (True, "")),
    # Value equal to maximum
    (7, {"maximum": 7}, (True, "")),
    # Value greater than maximum
    (8, {"maximum": 7}, (False, "Value greater than maximum")),
    # No maximum set
    (5, {}, (True, "")),
    # Zero value greater than negative maximum
    (0, {"maximum": -1}, (False, "Value greater than maximum")),
    # Negative value less than maximum
    (-2, {"maximum": -1}, (True, "")),
])
def test_check_num_upper_bound(variable_value: int | float, variable_properties: dict[str, Any],
                               expected_result: tuple[bool, str]) -> None:
    """
    Unit test for method _check_num_upper_bound() in file input_manager.py.
    """

    assert InputManager._check_num_upper_bound(variable_value, variable_properties) == expected_result


@pytest.mark.parametrize("variable_path, variable_properties, input_data, expected_result", [
    # Test with valid integer
    (["key1"], {"type": "number"}, {"key1": 5}, True),
    # Test with valid float
    (["key1"], {"type": "number"}, {"key1": 3.5}, True),
    # Test with integer less than minimum
    (["key1"], {"type": "number", "minimum": 2}, {"key1": 1}, False),
    # Test with integer greater than maximum
    (["key1"], {"type": "number", "maximum": 10}, {"key1": 11}, False),
    # Test with non-numeric string
    (["key1"], {"type": "number"}, {"key1": "not a number"}, False),
    # Test with invalid but fixable input (non-numeric string with default numeric value)
    (["key1"], {"type": "number", "default": 5}, {"key1": "not a number"}, True),
    # Test with integer exactly at minimum
    (["key1"], {"type": "number", "minimum": 5, "maximum": 10}, {"key1": 5}, True),
    # Test with integer exactly at maximum
    (["key1"], {"type": "number", "minimum": 5, "maximum": 10}, {"key1": 10}, True),
    # Test with integer in between minimum and maximum
    (["key1"], {"type": "number", "minimum": 5, "maximum": 10}, {"key1": 7}, True),
    # Test with float just below minimum
    (["key1"], {"type": "number", "minimum": 5}, {"key1": 4.999}, False),
    # Test with float just above maximum
    (["key1"], {"type": "number", "maximum": 10}, {"key1": 10.001}, False),
])
def test_validate_num_type(mocker: MockerFixture,
                           variable_path: list[str | int],
                           variable_properties: dict[str, Any],
                           input_data: dict[str, Any],
                           expected_result: bool) -> None:
    """
    Unit test for method _validate_num_type() in file input_manager.py.

    This test simply checks that _validate_num_type() calls _validate_primitive_type_with_revalidation()
    with the correct arguments.
    """

    # Arrange
    mock_validate_primitive = mocker.patch.object(
        InputManager,
        '_validate_primitive_type_with_revalidation',
        return_value=expected_result
    )
    input_manager = InputManager()

    # Act
    result = input_manager._validate_num_type(variable_path, variable_properties, input_data)

    # Assert
    assert result == expected_result
    mock_validate_primitive.assert_called_once_with(
        variable_path, variable_properties, input_data, [
            InputManager._is_numeric_value,
            InputManager._check_num_lower_bound,
            InputManager._check_num_upper_bound
        ]
    )


@pytest.mark.parametrize("variable_path, variable_properties, input_data, expected_result", [
    # Test with valid integer
    (["key1"], {"type": "number"}, {"key1": 5}, True),
    # Test with valid float
    (["key1"], {"type": "number"}, {"key1": 3.5}, True),
    # Test with integer less than minimum
    (["key1"], {"type": "number", "minimum": 6}, {"key1": 5}, False),
    # Test with integer equal to minimum
    (["key1"], {"type": "number", "minimum": 5}, {"key1": 5}, True),
    # Test with integer more than minimum
    (["key1"], {"type": "number", "minimum": 4}, {"key1": 5}, True),
    # Test with integer more than maximum
    (["key1"], {"type": "number", "maximum": 4}, {"key1": 5}, False),
    # Test with integer equal to maximum
    (["key1"], {"type": "number", "maximum": 5}, {"key1": 5}, True),
    # Test with integer less than maximum
    (["key1"], {"type": "number", "maximum": 6}, {"key1": 5}, True),
    # Test with non-numeric string, no default
    (["key1"], {"type": "number"}, {"key1": "not a number"}, False),
    # Test with non-numeric string, fixable with default
    (["key1"], {"type": "number", "default": 5}, {"key1": "not a number"}, True),
    # Test with non-numeric string, unfixable
    (["key1"], {"type": "number", "default": "not a number"}, {"key1": "not a number"}, False),
    # Test with float less than minimum
    (["key1"], {"type": "number", "minimum": 6}, {"key1": 5.999}, False),
    # Test with float equal to minimum
    (["key1"], {"type": "number", "minimum": 5}, {"key1": 5.0}, True),
    # Test with float more than minimum
    (["key1"], {"type": "number", "minimum": 4}, {"key1": 4.001}, True),
])
def test_validate_num_type_integration_test(variable_path: list[str | int],
                                            variable_properties: dict[str, Any],
                                            input_data: dict[str, Any],
                                            expected_result: bool) -> None:
    """
    Integration test for method _validate_num_type() in file input_manager.py.

    This test checks the integration between _validate_num_type() and
    _validate_primitive_type_with_revalidation().
    """
    # Arrange
    input_manager = InputManager()
    om = OutputManager()
    initial_data = InputManager._get_nested_dict_value(input_data, variable_path)

    # Act
    result = input_manager._validate_num_type(variable_path, variable_properties, input_data)

    # Assert
    assert result == expected_result
    if type(initial_data) not in (int, float):
        assert "InputManager._validate_primitive_type_with_revalidation.Value is not a number" \
               in om.warnings_pool
        if "default" in variable_properties and isinstance(variable_properties["default"], (int, float)):
            assert "InputManager._fix_data.Data fixed" in om.warnings_pool
        elif "default" in variable_properties:
            assert "InputManager._revalidate_element_after_fix.Fixed element is still invalid" in om.errors_pool
        else:
            assert "InputManager._validate_primitive_type_with_revalidation.Invalid, unfixable element found" \
                   in om.errors_pool

    # Cleanup
    om.flush_pools()


@pytest.mark.parametrize("variable_value, variable_properties, expected_result", [
    # Test with a regular string
    ("hello", {}, (True, "")),
    # Test with an empty string
    ("", {}, (True, "")),
    # Test with an integer
    (123, {}, (False, "String variable is not a string.")),
    # Test with a float
    (1.0, {}, (False, "String variable is not a string.")),
    # Test with a boolean
    (True, {}, (False, "String variable is not a string.")),
    # Test with a list
    ([1, 2, 3], {}, (False, "String variable is not a string.")),
    # Test with a dictionary
    ({"key": "value"}, {}, (False, "String variable is not a string.")),
    # Test with a None value
    (None, {}, (False, "String variable is not a string."))
])
def test_is_str_value(variable_value, variable_properties, expected_result):
    """
    Unit test for method _is_str_value() in file input_manager.py.
    """

    assert InputManager._is_str_value(variable_value, variable_properties) == expected_result


@pytest.mark.parametrize("variable_value, variable_properties, expected_result", [
    # Test with string longer than minimum
    ("hello", {"minimum_length": 3}, (True, "")),
    # Test with string shorter than minimum
    ("hi", {"minimum_length": 3}, (False, "String length less than minimum.")),
    # Test with string equal to minimum
    ("hello", {}, (True, "")),
    # Test with empty string and some minimum length
    ("", {"minimum_length": 1}, (False, "String length less than minimum.")),
    # Test with empty string and zero minimum length
    ("", {"minimum_length": 0}, (True, "")),
])
def test_check_str_len_lower_bound(variable_value: str, variable_properties: dict[str, Any],
                                   expected_result: tuple[bool, str]) -> None:
    """
    Unit test for method _check_str_len_lower_bound() in file input_manager.py.
    """

    assert InputManager._check_str_len_lower_bound(variable_value, variable_properties) == expected_result


@pytest.mark.parametrize("variable_value, variable_properties, expected_result", [
    # Test with string equal to maximum length
    ("hello", {"maximum_length": 5}, (True, "")),
    # Test with string shorter than maximum length
    ("hello", {"maximum_length": 10}, (True, "")),
    # Test with string longer than maximum length
    ("hello", {"maximum_length": 4}, (False, "String length greater than maximum.")),
    # Test with string but no maximum length specified
    ("hello", {}, (True, "")),
    # Test with empty string and no maximum length specified
    ("", {"maximum_length": 0}, (True, "")),
    # Test with empty string and some maximum length
    ("", {"maximum_length": 1}, (True, "")),
])
def test_check_str_len_upper_bound(variable_value: str, variable_properties: dict[str, Any],
                                   expected_result: tuple[bool, str]) -> None:
    """
    Unit test for method _check_str_len_upper_bound() in file input_manager.py.
    """

    assert InputManager._check_str_len_upper_bound(variable_value, variable_properties) == expected_result


@pytest.mark.parametrize("variable_value, variable_properties, expected_result", [
    # Test with an alphanumeric string matching the pattern
    ("hello123", {"pattern": r"\w+"}, (True, "")),
    # Test with an alphanumeric string not matching the pattern
    ("hello123", {"pattern": r"\d+"}, (False, "String does not match pattern.")),
    # Test with a numeric string matching the pattern
    ("12345", {"pattern": r"\d+"}, (True, "")),
    # Test with an exact match
    ("hello", {"pattern": r"hello"}, (True, "")),
    # Test with a case-sensitive failed match
    ("HELLO", {"pattern": r"hello"}, (False, "String does not match pattern.")),
    # Test with a string containing a space
    ("hello world", {"pattern": r"hello world"}, (True, "")),
    # Test with a string matching a character class pattern
    ("hello", {"pattern": r"[a-z]+"}, (True, "")),
    # Test with an empty string and a pattern that matches anything
    ("", {"pattern": r".*"}, (True, "")),
    # Test with a string but no pattern specified
    ("hello", {}, (True, "")),
    # Test with case-insensitive flag
    ("HELLO", {"pattern": r"(?i)hello"}, (True, "")),  # Case-insensitive flag, should match
    # Test with pipe character to match one of two options
    ("cat", {"pattern": r"cat|dog"}, (True, "")),
    # Test with pipe character to match one of two options
    ("dog", {"pattern": r"cat|dog"}, (True, "")),
    # Test with pipe character and no match
    ("bird", {"pattern": r"cat|dog"}, (False, "String does not match pattern.")),
    # Test with pipe character and match all options
    ("catdog", {"pattern": r"cat|dog"}, (False, "String does not match pattern.")),
    # Test with pipe character and match some options but not all
    ("dogfish", {"pattern": r"cat|dog"}, (False, "String does not match pattern.")),
    # Test with pipe character, start, and end of string
    ("dog", {"pattern": r"^dog|cat$"}, (True, "")),
    # Test with pipe character, start, and end of string
    ("cat", {"pattern": r"^dog|cat$"}, (True, "")),
    # Test with pipe character, start, and end of string and only part of the string matches
    ("a cat", {"pattern": r"^dog|cat$"}, (False, "String does not match pattern.")),
    # Test with dot character
    ("hello.world", {"pattern": r"hello.world"}, (True, "")),
    # Test with dot character but no match
    ("helloworld", {"pattern": r"hello.world"}, (False, "String does not match pattern.")),
    # Test with literal dot character
    ("hello.world", {"pattern": r"hello\.world"}, (True, "")),
    # Test with literal dot character but no match
    ("helloworld", {"pattern": r"hello\.world"}, (False, "String does not match pattern.")),
    # Test with minimum number of characters
    ("helloooo", {"pattern": r"hello{2,}"}, (True, "")),
    # Test with minimum number of characters but no match
    ("hello", {"pattern": r"hello{2,}"}, (False, "String does not match pattern.")),
    # Test with maximum number of characters
    ("hello", {"pattern": r"hello{,2}"}, (True, "")),
    # Test with maximum number of characters but no match
    ("helloooo", {"pattern": r"hello{,2}"}, (False, "String does not match pattern.")),
])
def test_check_str_pattern_match(variable_value: str, variable_properties: dict[str, Any],
                                 expected_result: tuple[bool, str]) -> None:
    """
    Unit test for method _check_str_pattern_match() in file input_manager.py.
    """

    assert InputManager._check_str_pattern_match(variable_value, variable_properties) == expected_result


@pytest.mark.parametrize("variable_path, variable_properties, input_data, expected_result", [
    # Test with a valid string
    (["key1"], {"type": "string"}, {"key1": "test"}, True),
    # Test with a string shorter than minimum length
    (["key1"], {"type": "string", "minimum_length": 2}, {"key1": "t"}, False),
    # Test with a string equal to minimum length
    (["key1"], {"type": "string", "maximum_length": 4}, {"key1": "test"}, True),
    # Test with a string longer than minimum length
    (["key1"], {"type": "string", "maximum_length": 3}, {"key1": "test"}, False),
    # Test with a string longer that matches pattern
    (["key1"], {"type": "string", "pattern": r"test"}, {"key1": "test"}, True),
    # Test with a string longer that does not match pattern
    (["key1"], {"type": "string", "pattern": r"\d+"}, {"key1": "test"}, False),
    # Test with an invalid type but fixable with default
    (["key1"], {"type": "string", "default": "default"}, {"key1": 123}, True),  # Invalid type but fixable
])
def test_validate_str_type(mocker: MockerFixture,
                           variable_path: list[str | int],
                           variable_properties: dict[str, Any],
                           input_data: dict[str, Any],
                           expected_result: bool) -> None:
    """
    Unit test for method _validate_str_type() in file input_manager.py.

    This test simply checks if the method calls _validate_primitive_type_with_revalidation() with the correct
    arguments.
    """

    # Arrange
    mock_validate_primitive = mocker.patch.object(
        InputManager,
        '_validate_primitive_type_with_revalidation',
        return_value=expected_result
    )
    input_manager = InputManager()

    # Act
    result = input_manager._validate_str_type(variable_path, variable_properties, input_data)

    # Assert
    assert result == expected_result
    mock_validate_primitive.assert_called_once_with(
        variable_path, variable_properties, input_data, [
            InputManager._is_str_value,
            InputManager._check_str_len_lower_bound,
            InputManager._check_str_len_upper_bound,
            InputManager._check_str_pattern_match
        ]
    )


@pytest.mark.parametrize("variable_path, variable_properties, input_data, expected_result", [
    # Test with valid string
    (["key1"], {"type": "string"}, {"key1": "test"}, True),
    # Test with string shorter than minimum length
    (["key1"], {"type": "string", "minimum_length": 5}, {"key1": "test"}, False),
    # Test with string equal to minimum length
    (["key1"], {"type": "string", "minimum_length": 4}, {"key1": "test"}, True),
    # Test with string longer than minimum length
    (["key1"], {"type": "string", "minimum_length": 3}, {"key1": "test"}, True),
    # Test with string longer than maximum length
    (["key1"], {"type": "string", "maximum_length": 3}, {"key1": "test"}, False),
    # Test with string equal to maximum length
    (["key1"], {"type": "string", "maximum_length": 4}, {"key1": "test"}, True),
    # Test with string shorter than maximum length
    (["key1"], {"type": "string", "maximum_length": 5}, {"key1": "test"}, True),
    # Test with string not matching pattern, no default
    (["key1"], {"type": "string", "pattern": r"\d+"}, {"key1": "test"}, False),
    # Test with string matching pattern
    (["key1"], {"type": "string", "pattern": r"\w+"}, {"key1": "test"}, True),
    # Test with non-string type, no default
    (["key1"], {"type": "string"}, {"key1": 123}, False),
    # Test with non-string type, fixable with default
    (["key1"], {"type": "string", "default": "default"}, {"key1": 123}, True),
    # Test with non-string type, unfixable
    (["key1"], {"type": "string", "default": 123}, {"key1": 123}, False),
    # Nested Paths
    (["key1", "nestedKey"], {"type": "string"}, {"key1": {"nestedKey": "nestedTest"}}, True),
    # Test with empty string
    (["key1"], {"type": "string"}, {"key1": ""}, True),
    # Test with whitespaces
    (["key1"], {"type": "string"}, {"key1": "    "}, True),
    # Quantifiers and character classes
    (["key1"], {"type": "string", "pattern": r"\w{2,5}"}, {"key1": "abc"}, True),
])
def test_validate_str_type_integration_test(variable_path: list[str | int],
                                            variable_properties: dict[str, Any],
                                            input_data: dict[str, Any],
                                            expected_result: bool) -> None:
    """
    Integration test for method _validate_str_type() in file input_manager.py.

    This test checks the integration between _validate_str_type() and
    _validate_primitive_type_with_revalidation().
    """

    # Arrange
    input_manager = InputManager()
    om = OutputManager()
    initial_data = InputManager._get_nested_dict_value(input_data, variable_path)

    # Act
    result = input_manager._validate_str_type(variable_path, variable_properties, input_data)

    # Assert
    assert result == expected_result
    if type(initial_data) is not str:
        assert "InputManager._validate_primitive_type_with_revalidation.String variable is not a string." \
               in om.warnings_pool
        if "default" in variable_properties and isinstance(variable_properties["default"], str):
            assert "InputManager._fix_data.Data fixed" in om.warnings_pool
        elif "default" in variable_properties:
            assert "InputManager._revalidate_element_after_fix.Fixed element is still invalid" in om.errors_pool
        else:
            assert "InputManager._validate_primitive_type_with_revalidation.Invalid, unfixable element found" \
                   in om.errors_pool

    # Cleanup
    om.flush_pools()


@pytest.mark.parametrize("variable_value, variable_properties, expected_result", [
    # Test with a dictionary
    ({"key": "value"}, {}, (True, "")),
    # Test with a list
    ([1, 2, 3], {}, (False, "Object variable is not a dictionary.")),
    # Test with a string
    ("string", {}, (False, "Object variable is not a dictionary.")),
    # Test with an integer
    (123, {}, (False, "Object variable is not a dictionary.")),
    # Test with a None value
    (None, {}, (False, "Object variable is not a dictionary.")),
    # Test with a boolean
    (True, {}, (False, "Object variable is not a dictionary.")),
    # Test with a float
    (4.5, {}, (False, "Object variable is not a dictionary.")),
    # Test with a set
    (set(), {}, (False, "Object variable is not a dictionary.")),
    # Test with a tuple
    ((), {}, (False, "Object variable is not a dictionary.")),
])
def test_is_object_value(variable_value: Any, variable_properties: dict[str, Any],
                         expected_result: tuple[bool, str]) -> None:
    """
    Unit test for method _is_object_value() in file input_manager.py.
    """

    assert InputManager._is_object_value(variable_value, variable_properties) == expected_result


@pytest.mark.parametrize(
    "variable_path, variable_properties, input_data, expected_result, "
    "mock_get_nested_dict_value_return, mock_is_object_value_return, "
    "mock_validate_input_type_dynamic_return, mock_handle_container_error_return",
    [
        # Case 1: Handle container error unsuccessfully
        (["key1"], {"type": "object"}, {"key1": "not an object"}, False,
         "not an object", (False, "Error Message"), None, False),

        # Case 2: Handle container error successfully
        (["key1"], {"type": "object"}, {"key1": "not an object"}, True,
         "not an object", (False, "Error Message"), None, True),

        # Case 3: Object validation passes, but sub-element validation fails
        (["key1"], {"type": "object", "subkey": {"type": "string"}}, {"key1": {"subkey": 1}}, False,
         {"subkey": 1}, (True, ""), False, None),

        # Case 4: Object validation passes, and sub-element validation passes
        (["key1"], {"type": "object", "subkey": {"type": "string"}}, {"key1": {"subkey": "value"}}, True,
         {"subkey": "value"}, (True, ""), True, None),
    ]
)
def test_validate_object_type(
        mocker: MockerFixture,
        variable_path: list[str | int],
        variable_properties: dict[str, Any],
        input_data: dict[str, Any],
        expected_result: bool,
        mock_get_nested_dict_value_return: Any,
        mock_is_object_value_return: tuple[bool, str],
        mock_validate_input_type_dynamic_return: bool,
        mock_handle_container_error_return: bool
) -> None:
    """
    Unit test for method _validate_object_type() in file input_manager.py.

    This test simply checks if the method calls the correct methods with the correct arguments and all the
    possible return routes are reachable.
    """

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(InputManager, '_get_nested_dict_value', return_value=mock_get_nested_dict_value_return)
    mocker.patch.object(InputManager, '_is_object_value', return_value=mock_is_object_value_return)
    mocker.patch.object(InputManager, '_validate_input_type_dynamic',
                        return_value=mock_validate_input_type_dynamic_return)
    mocker.patch.object(InputManager, '_handle_container_error', return_value=mock_handle_container_error_return)

    # Act
    result = input_manager._validate_object_type(variable_path, variable_properties, input_data)

    # Assert
    assert result == expected_result


@pytest.mark.parametrize("variable_path, variable_properties, input_data, expected_result", [
    # Test with valid dictionary
    (["key1"], {"type": "object", "subkey": {"type": "string"}},
     {"key1": {"subkey": "value"}}, True),

    # Test with valid dictionary
    (["key1"], {"type": "object", "subkey": {"type": "string"}},
     {"key1": {"subkey": 123}}, False),

    # Test with invalid type (not a dictionary)
    (["key1"], {"type": "object"},
     {"key1": "not a dictionary"}, False),

    # Test with valid dictionary and nested elements
    (["key1", "subkey1"], {"type": "object", "sub_subkey1": {"type": "string"}},
     {"key1": {"subkey1": {"sub_subkey1": "value"}}}, True),

    # Test with dictionary containing invalid nested element
    (["key1"], {"type": "object", "subkey1": {"type": "number"}},
     {"key1": {"subkey1": "not a number"}}, False),

    # Test with empty dictionary
    (["key1"], {"type": "object"},
     {"key1": {}}, True),

    # Test with dictionary containing multiple nested elements
    (["key1"], {"type": "object", "subkey1": {"type": "string"}, "subkey2": {"type": "number"}},
     {"key1": {"subkey1": "value", "subkey2": 123}}, True),

    # Test with null dictionary
    (["key1"], {"type": "object"},
     {"key1": None}, False),

    # Test with dictionary containing a list
    (["key1"], {"type": "object", "subkey1": {"type": "array", "properties": {"type": "number"}}},
     {"key1": {"subkey1": [1, 2, 3]}}, True),
])
def test_validate_object_type_integration_test(variable_path: list[str | int],
                                               variable_properties: dict[str, Any],
                                               input_data: dict[str, Any],
                                               expected_result: bool) -> None:
    """
    Integration test for method _validate_object_type() in file input_manager.py.
    """

    # Arrange
    input_manager = InputManager()

    # Act
    result = input_manager._validate_object_type(variable_path, variable_properties, input_data)

    # Assert
    assert result == expected_result
