import json
from functools import reduce
from pathlib import Path
from typing import Any, Callable, Dict, List, Set, Type, Union, Optional
from typing import Tuple
from unittest.mock import ANY

import pandas as pd
import pytest
from mock import MagicMock, Mock, mock_open, patch
from mock.mock import call
from pytest_mock import MockerFixture

from RUFAS.input_manager import ElementsCounter, ElementState, InputManager, Modifiability


@pytest.fixture
def mock_input_manager() -> InputManager:
    InputManager.__instance = None
    input_manager = InputManager()
    return input_manager


def test_input_manager_singleton() -> None:
    """Unit test to ensure InputManager is a singleton"""
    im1 = InputManager()
    im2 = InputManager()

    assert im1 is im2

    fake_pool = {"a": 1}
    im1.pool = fake_pool
    assert im2.pool is fake_pool

    fake_metadata = {"b": 2}
    im1.meta_data = fake_metadata
    assert im2.meta_data is fake_metadata


@pytest.fixture
def input_manager_original_method_states(
    mock_input_manager: InputManager,
) -> Dict[str, Callable]:
    """Fixture to store original methods of InputManager"""
    return {
        "start_data_processing": mock_input_manager.start_data_processing,
        "_load_metadata": mock_input_manager._load_metadata,
        "_load_properties": mock_input_manager._load_properties,
        "_load_data_from_json": mock_input_manager._load_data_from_json,
        "_load_data_from_csv": mock_input_manager._load_data_from_csv,
        "_populate_pool": mock_input_manager._populate_pool,
        "_filter_input_array_data_by_metadata": mock_input_manager._filter_input_array_data_by_metadata,
        "_filter_input_data_by_metadata": mock_input_manager._filter_input_data_by_metadata,
        "_get_variable_modifiability": mock_input_manager._get_variable_modifiability,
        "_log_missing_data": mock_input_manager._log_missing_data,
        "_validate_input_by_type": mock_input_manager._validate_input_by_type,
        "_array_type_validator": mock_input_manager._array_type_validator,
        "_number_type_validator": mock_input_manager._number_type_validator,
        "_string_type_validator": mock_input_manager._string_type_validator,
        "_bool_type_validator": mock_input_manager._bool_type_validator,
        "_fix_data": mock_input_manager._fix_data,
        "get_data": mock_input_manager.get_data,
        "get_metadata": mock_input_manager.get_metadata,
        "get_data_keys_by_properties": mock_input_manager.get_data_keys_by_properties,
        "flush_pool": mock_input_manager.flush_pool,
        "_metadata_properties_exist": mock_input_manager._metadata_properties_exist,
        "_set_nested_value": mock_input_manager._set_nested_value,
        "_add_variable_to_pool": mock_input_manager._add_variable_to_pool,
        "add_dict_variable_to_pool": mock_input_manager.add_dict_variable_to_pool,
        "add_tabular_variable_to_pool": mock_input_manager.add_tabular_variable_to_pool,
        "_is_input_required_upon_initialization": mock_input_manager._is_input_required_upon_initialization,
        "_is_modifiable_during_runtime": mock_input_manager._is_modifiable_during_runtime,
        "save_metadata_properties": mock_input_manager.save_metadata_properties,
        "_parse_metadata_properties": mock_input_manager._parse_metadata_properties,
        "_check_property_type_primitive": mock_input_manager._check_property_type_primitive,
        "_create_record": mock_input_manager._create_record,
        "_extract_input_data_by_key_list": mock_input_manager._extract_input_data_by_key_list,
    }


def test_metadata_setter_getter(mock_input_manager: InputManager) -> None:
    """Unit test for metadata getter and setter methods"""
    test_data = {"foo": "bar", "integer": 1}
    mock_input_manager.meta_data = test_data
    assert mock_input_manager.meta_data == test_data


def test_pool_setter_getter(mock_input_manager: InputManager) -> None:
    """Unit test for metadata getter and setter methods"""
    test_data = {"foo": "bar", "integer": 1}
    mock_input_manager.pool = test_data
    assert mock_input_manager.pool == test_data


def test_set_metadata_depth_limit(mock_input_manager: InputManager, mocker: MockerFixture) -> None:
    """Test for metadata override function for metadata depth limit"""
    mock_add_log = mocker.patch("RUFAS.output_manager.OutputManager.add_log")
    new_limit = 10
    mock_input_manager.set_metadata_depth_limit(new_limit)
    assert mock_input_manager.metadata_depth_limit == new_limit
    mock_add_log.assert_called_once()


def test_load_properties_success(mock_input_manager: InputManager, mocker: MockerFixture) -> None:
    """Unit test for successfully loading properties in _load_properties method."""
    mocker.patch.object(Path, "exists", return_value=True)
    properties_data = {"key1": "value1", "key2": "value2"}
    mocker.patch("builtins.open", mock_open(read_data=json.dumps(properties_data)))
    mocker.patch(
        "RUFAS.input_manager.InputManager._load_data_from_json",
        return_value=properties_data,
    )

    mock_input_manager._InputManager__metadata = {"files": {"properties": {"path": "path/to/properties.json"}}}

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        mock_input_manager._load_properties()
        assert mock_input_manager._InputManager__metadata["properties"] == properties_data
        assert add_log.call_count == 2


def test_load_properties_file_not_found(mock_input_manager: InputManager, mocker: MockerFixture) -> None:
    """Unit test for handling FileNotFoundError in _load_properties method."""
    mocker.patch("os.path.exists", return_value=False)
    mock_input_manager._InputManager__metadata = {"files": {"properties": {"path": "path/to/missing_properties.json"}}}

    with patch("RUFAS.output_manager.OutputManager.add_error") as add_error:
        with pytest.raises(FileNotFoundError):
            mock_input_manager._load_properties()
        assert add_error.call_count == 1


def test_load_properties_json_decode_error(mock_input_manager: InputManager, mocker: MockerFixture) -> None:
    """Unit test for handling JSONDecodeError in _load_properties method."""
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch.object(Path, "exists", return_value=True)
    mocker.patch("builtins.open", mock_open(read_data="invalid_json"))

    mock_input_manager._InputManager__metadata = {"files": {"properties": {"path": "path/to/invalid_json.json"}}}

    with patch("RUFAS.output_manager.OutputManager.add_error") as add_error:
        with pytest.raises(json.JSONDecodeError):
            mock_input_manager._load_properties()
        assert add_error.call_count == 1


def test_load_properties_unexpected_error(mock_input_manager: InputManager, mocker: MockerFixture) -> None:
    """Unit test for handling unexpected errors in _load_properties method."""
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch.object(Path, "exists", return_value=True)
    mocker.patch("builtins.open", mock_open(read_data="valid_json"))
    mocker.patch(
        "RUFAS.input_manager.InputManager._load_data_from_json",
        side_effect=Exception("Unexpected error"),
    )

    mock_input_manager._InputManager__metadata = {"files": {"properties": {"path": "path/to/properties.json"}}}

    with patch("RUFAS.output_manager.OutputManager.add_error") as add_error:
        with pytest.raises(Exception, match="Unexpected error"):
            mock_input_manager._load_properties()
        assert add_error.call_count == 1


def test_load_metadata(mock_input_manager: InputManager) -> None:
    """Unit test for function _load_metadata in file input_manager.py"""
    with patch(
        "builtins.open",
        mock_open(read_data='{"dummy_key1": "dummy_value1", "dummy_key2": "dummy_value2"}'),
    ):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            mock_input_manager._load_metadata("path/dummy_metadata.json")
            assert mock_input_manager._InputManager__metadata == {
                "dummy_key1": "dummy_value1",
                "dummy_key2": "dummy_value2",
            }
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


def test_load_data_from_json(
    mock_input_manager: InputManager,
) -> None:
    """Unit test for function _load_data_from_json with valid json file in file input_manager.py"""
    dummy_data = {"files": {"dummy_data_file": {"path": "dummy_data.json", "type": "json"}}}
    file_path = "path/to/json/file"
    dummy_file_content = json.dumps(dummy_data)

    with patch("builtins.open", mock_open(read_data=dummy_file_content)):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            result_data = mock_input_manager._load_data_from_json(file_path)

            assert result_data == dummy_data
            assert add_log.call_count == 2


def test_load_data_from_json_missing_file_raises_error(
    mock_input_manager: InputManager,
) -> None:
    """Unit test for function _load_data_from_json with missing json file in file input_manager.py"""
    with patch("builtins.open", side_effect=FileNotFoundError):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            with pytest.raises(FileNotFoundError):
                mock_input_manager._load_data_from_json("non_existent_file.json")
            assert add_log.call_count == 1


def test_load_data_from_json_invalid_data_raises_error(
    mock_input_manager: InputManager,
) -> None:
    """Unit test for function _load_data_from_json with invalid json data in file input_manager.py"""
    with patch("builtins.open", mock_open(read_data="invalid_json_data")):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            with pytest.raises(json.JSONDecodeError):
                mock_input_manager._load_data_from_json("dummy_file.json")
            assert add_log.call_count == 1


def test_load_data_from_csv(
    mock_input_manager: InputManager,
) -> None:
    """Unit test for function _load_data_from_csv with valid csv file in file input_manager.py"""
    dummy_csv_data = "key1,key2\na,1\nb,2\n"
    dummy_expected_data = {"key1": ["a", "b"], "key2": [1, 2]}
    file_path = "path/to/csv/file"
    with patch("builtins.open", mock_open(read_data=dummy_csv_data)):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            result_data = mock_input_manager._load_data_from_csv(file_path)

            assert result_data == dummy_expected_data
            assert add_log.call_count == 2


def test_load_data_from_csv_missing_file_raises_error(
    mock_input_manager: InputManager,
) -> None:
    """Unit test for function _load_data_from_csv with missing csv file in file input_manager.py"""
    with patch("builtins.open", side_effect=FileNotFoundError):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            with pytest.raises(FileNotFoundError):
                mock_input_manager._load_data_from_csv("non_existent_file.csv")
            assert add_log.call_count == 1


def test_load_data_from_csv_invalid_data_raises_error(
    mock_input_manager: InputManager,
) -> None:
    """Unit test for function _load_data_from_json with invalid json data in file input_manager.py"""
    with patch("builtins.open", mock_open(read_data="invalid_csv_data")):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            with patch("pandas.read_csv", side_effect=pd.errors.ParserError("Invalid CSV")):
                with pytest.raises(pd.errors.ParserError):
                    mock_input_manager._load_data_from_csv("dummy_file.csv")
                assert add_log.call_count == 1


def test_start_data_processing(
    mock_input_manager: InputManager,
    mocker: MockerFixture,
) -> None:
    """Unit test for function start_data_processing in file input_manager.py"""
    patch_for_load_metadata = mocker.patch.object(mock_input_manager, "_load_metadata")
    patch_for_populate_pool = mocker.patch.object(mock_input_manager, "_populate_pool", return_value=True)
    patch_for_validate_metadata = mocker.patch.object(mock_input_manager, "_validate_metadata")
    patch_for_load_properties = mocker.patch.object(mock_input_manager, "_load_properties")
    patch_for_validate_properties = mocker.patch.object(mock_input_manager, "_validate_properties")

    eager_termination = True
    mock_metadata_path = "mock/metadata/path"

    mock_input_manager.start_data_processing(mock_metadata_path, eager_termination)

    patch_for_load_metadata.assert_called_once_with(mock_metadata_path)
    patch_for_populate_pool.assert_called_once_with(eager_termination)
    patch_for_load_properties.assert_called_once()
    patch_for_validate_metadata.assert_called_once()
    patch_for_validate_properties.assert_called_once()


@pytest.mark.parametrize(
    "input_data, metadata_properties, expected_result",
    [
        (
            {"key1": "value1", "key2": "value2"},
            {"key1": {"default": "value3"}},
            {"key1": "value1"},
        ),
        (
            {"key1": {"nested_key1": "value1", "nested_key2": "value2"}},
            {"key1": {"nested_key1": {"default": "value2"}}},
            {"key1": {"nested_key1": "value1"}},
        ),
        (
            {"key1": {"nested_key1": ["value1", "value2"], "nested_key2": "value2"}},
            {"key1": {"nested_key1": {"type": "array", "properties": {"default": "value1"}}}},
            {"key1": {"nested_key1": ["value1", "value2"]}},
        ),
        (
            {"key1": {"nested_key1": [{"key3": 1, "key4": 2}, {"key3": 3, "key4": 4}], "nested_key2": "value2"}},
            {"key1": {"nested_key1": {"type": "array", "properties": {"key3": {"default": 2}}}}},
            {"key1": {"nested_key1": [{"key3": 1}, {"key3": 3}]}},
        ),
    ],
)
def test_filter_input_data_by_metadata(
    mock_input_manager: InputManager,
    input_data: Dict[str, Any],
    metadata_properties: Dict[str, Any],
    expected_result: Dict[str, Any],
    input_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Unit test for function _filter_input_data_by_metadata() in file input_manager.py"""
    filtered_input_data = mock_input_manager._filter_input_data_by_metadata(input_data, metadata_properties)
    assert filtered_input_data == expected_result

    mock_input_manager._filter_input_data_by_metadata = input_manager_original_method_states[
        "_filter_input_data_by_metadata"
    ]


@pytest.mark.parametrize(
    "input_data, metadata_properties, expected_result",
    [
        (
            [],
            {"key1": {"default": "value3"}},
            [],
        ),
        (
            [{"a": 1, "b": "A", "c": True}, {"a": 2, "b": "B", "c": False}, {"a": 3, "b": "C", "c": True}],
            {
                "type": "array",
                "properties": {
                    "type": "object",
                    "a": {"type": "number"},
                    "b": {"type": "string"},
                    "c": {"type": "bool"},
                },
            },
            [{"a": 1, "b": "A", "c": True}, {"a": 2, "b": "B", "c": False}, {"a": 3, "b": "C", "c": True}],
        ),
        (
            [{"a": 1, "b": "A", "c": True}, {"a": 2, "b": "B", "c": False}, {"a": 3, "b": "C", "c": True}],
            {"type": "array", "properties": {"type": "object", "a": {"type": "number"}, "b": {"type": "string"}}},
            [{"a": 1, "b": "A"}, {"a": 2, "b": "B"}, {"a": 3, "b": "C"}],
        ),
        (
            [[1, 2, 3, 1.1, 2.2, 3.3]],
            {"type": "array", "properties": {"type": "number"}},
            [[1, 2, 3, 1.1, 2.2, 3.3]],
        ),
        (
            [[1, 2, 3], [1.1, 2.2, 3.3]],
            {"type": "array", "properties": {"type": "array", "properties": {"type": "number"}}},
            [[1, 2, 3], [1.1, 2.2, 3.3]],
        ),
    ],
)
def test_filter_input_array_data_by_metadata(
    mock_input_manager: InputManager,
    input_data: List[Any],
    metadata_properties: Dict[str, Any],
    expected_result: List[Any],
    input_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Unit test for function _filter_input_array_data_by_metadata() in file input_manager.py"""
    filtered_input_data = mock_input_manager._filter_input_array_data_by_metadata(input_data, metadata_properties)
    assert filtered_input_data == expected_result

    mock_input_manager._filter_input_array_data_by_metadata = input_manager_original_method_states[
        "_filter_input_array_data_by_metadata"
    ]


@pytest.fixture
def mock_metadata(mocker: MockerFixture) -> Dict[str, Dict[str, Any]]:
    return {
        "files": {
            "file1": {
                "type": "json",
                "path": "path/to/json/file1.json",
                "properties": "properties1",
            },
            "file2": {
                "type": "csv",
                "path": "path/to/csv/file2.csv",
                "properties": "properties2",
            },
        },
        "properties": {
            "properties1": {"element1": "some_value1", "element2": "some_value2"},
            "properties2": {"element3": "some_value3", "element4": "some_value4"},
        },
    }


def test_populate_pool_valid(
    mock_metadata: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """Unit test for valid data for function _populate_pool in file input_manager.py"""

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata)
    mocker.patch.object(
        input_manager, "_load_data_from_json", side_effect=lambda _: {"element1": "value1", "element2": "value2"}
    )
    mocker.patch.object(
        input_manager, "_load_data_from_csv", side_effect=lambda _: {"element3": "value3", "element4": "value4"}
    )
    mocker.patch.object(input_manager, "_validate_input_by_type", side_effect=lambda *args, **kwargs: True)
    mocker.patch.object(
        input_manager,
        "_add_default_values_to_missing_inputs",
        side_effect=lambda input_data, _: (input_data, None, None),
    )
    mocker.patch.object(input_manager, "_log_missing_keys")
    mocker.patch("RUFAS.input_manager.om.add_warning")
    mocker.patch("RUFAS.input_manager.om.add_log")

    # Act
    result = input_manager._populate_pool(eager_termination=True)

    # Assert
    assert result
    assert "file1" in input_manager.pool
    assert "file2" in input_manager.pool

    input_manager.pool = {}


def test_populate_pool_invalid(
    mock_metadata: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """Unit test for invalid data for function _populate_pool in file input_manager.py"""

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata)
    mocker.patch.object(
        input_manager, "_load_data_from_json", side_effect=lambda _: {"element1": "value1", "element2": "value2"}
    )
    mocker.patch.object(
        input_manager, "_load_data_from_csv", side_effect=lambda _: {"element3": "value3", "element4": "value4"}
    )
    mocker.patch.object(input_manager, "_validate_input_by_type", side_effect=lambda *args, **kwargs: False)
    mocker.patch.object(
        input_manager,
        "_add_default_values_to_missing_inputs",
        side_effect=lambda input_data, _: (input_data, None, None),
    )
    mocker.patch.object(input_manager, "_log_missing_keys")
    mocker.patch("RUFAS.input_manager.om.add_warning")
    mocker.patch("RUFAS.input_manager.om.add_log")
    elements_counter = ElementsCounter()
    elements_counter.increment(ElementState.INVALID)
    mocker.patch.object(input_manager, "elements_counter", elements_counter)

    # Act
    result = input_manager._populate_pool(eager_termination=False)

    # Assert
    assert not result
    assert "file1" not in input_manager.pool
    assert "file2" not in input_manager.pool


def test_populate_pool_partial_invalid(
    mock_metadata: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """Unit test for invalid data for function _populate_pool in file input_manager.py"""

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata)
    mocker.patch.object(
        input_manager, "_load_data_from_json", side_effect=lambda _: {"element1": "value1", "element2": "value2"}
    )
    mocker.patch.object(
        input_manager, "_load_data_from_csv", side_effect=lambda _: {"element3": "value3", "element4": "value4"}
    )
    mocker.patch.object(input_manager, "_validate_input_by_type", side_effect=[True, False, True, False])
    mocker.patch.object(
        input_manager,
        "_add_default_values_to_missing_inputs",
        side_effect=lambda input_data, _: (input_data, None, None),
    )
    mocker.patch.object(input_manager, "_log_missing_keys")
    mocker.patch("RUFAS.input_manager.om.add_warning")
    mocker.patch("RUFAS.input_manager.om.add_log")

    # Act
    result = input_manager._populate_pool(eager_termination=False)

    # Assert
    assert result
    assert "file1" in input_manager.pool
    assert "file2" in input_manager.pool
    assert "element1" in input_manager.pool["file1"]
    assert "element2" not in input_manager.pool["file1"]
    assert "element3" in input_manager.pool["file2"]
    assert "element4" not in input_manager.pool["file2"]

    input_manager.pool = {}


def test_populate_pool_eager_termination(
    mock_metadata: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """Unit test for invalid data with eager termination for function
    _populate_pool in file input_manager.py"""

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata)
    mocker.patch.object(
        input_manager, "_load_data_from_json", side_effect=lambda _: {"element1": "value1", "element2": "value2"}
    )
    mocker.patch.object(
        input_manager, "_load_data_from_csv", side_effect=lambda _: {"element3": "value3", "element4": "value4"}
    )
    mocker.patch.object(input_manager, "_validate_input_by_type", side_effect=lambda *args, **kwargs: False)
    mocker.patch.object(
        input_manager,
        "_add_default_values_to_missing_inputs",
        side_effect=lambda input_data, _: (input_data, None, None),
    )
    mocker.patch.object(input_manager, "_log_missing_keys")
    mocker.patch("RUFAS.input_manager.om.add_warning")
    mocker.patch("RUFAS.input_manager.om.add_log")

    # Act
    result = input_manager._populate_pool(eager_termination=True)

    # Assert
    assert result is False
    assert "file1" not in input_manager.pool
    assert "file2" not in input_manager.pool


def test_populate_pool_raises_keyerror(
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Unit test for invalid data file type for function _populate_pool in file input_manager.py"""
    mock_input_manager.meta_data = {
        "files": {
            "dummy_file_key": {
                "type": "invalid_data_type",
                "path": "/path/to/your/file",
                "properties": "some_properties_key",
            }
        }
    }

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
            with pytest.raises(KeyError):
                mock_input_manager._populate_pool(eager_termination=True)

            assert add_log.call_count == 0
            assert add_warning.call_count == 0

    mock_input_manager._populate_pool = input_manager_original_method_states["_populate_pool"]
    mock_input_manager._validate_input_by_type = input_manager_original_method_states["_validate_input_by_type"]


@pytest.mark.parametrize(
    "input_data_value, dummy_variable_properties, expected_result",
    [
        (True, {}, True),
        (False, {}, True),
        ("hello", {}, False),
        (2, {}, False),
        (3.5, {}, False),
        ({}, {}, False),
        ([], {}, False),
        (None, {}, False),
        (None, {"nullable": True}, True),
    ],
)
def test_bool_type_validator(
    input_data_value: bool,
    dummy_variable_properties: Dict[str, Any],
    expected_result: bool,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for function _bool_type_validator in file input_manager.py
    """

    # Arrange
    input_manager = InputManager()
    var_path: list[str | int] = ["dummy_var_path"]
    variable_properties: Dict[str, Any] = dummy_variable_properties
    dummy_properties_key = "dummy_variable_properties"
    dummy_input_data = {"a": 1, "b": 2}
    dummy_counter = mocker.MagicMock(autospec=ElementsCounter)
    unused_bool_input = False
    patch_extract = mocker.patch.object(input_manager, "_extract_input_data_by_key_list", return_value=input_data_value)
    patch_path_to_str = mocker.patch.object(input_manager, "_convert_variable_path_to_str", return_value="dummy_name")
    patch_for_add_warning = mocker.patch("RUFAS.input_manager.om.add_warning")

    # Act
    result = input_manager._bool_type_validator(
        var_path,
        variable_properties,
        dummy_input_data,
        unused_bool_input,
        dummy_properties_key,
        dummy_counter,
        unused_bool_input,
    )

    # Assert
    patch_extract.assert_called_once_with(dummy_input_data, var_path, variable_properties, unused_bool_input)
    if dummy_variable_properties.get("nullable", False) is False:
        patch_path_to_str.assert_called_once_with(var_path)
    if not expected_result:
        patch_for_add_warning.assert_called_once()
    else:
        patch_for_add_warning.assert_not_called()
    assert result == expected_result


@pytest.mark.parametrize(
    "dummy_value, dummy_variable_properties, expected_result, expected_warning_call_count",
    [
        (1, {"minimum": 3, "maximum": 7}, False, 1),
        (3, {"minimum": 3, "maximum": 7}, True, 0),
        (5, {"minimum": 3}, True, 0),
        (7, {"minimum": 3, "maximum": 7}, True, 0),
        (9, {"maximum": 7}, False, 1),
        (-1, {"minimum": 3, "maximum": 7}, False, 1),
        (None, {"maximum": 1, "minimum": 0}, False, 1),
        ("42", {"minimum": 4, "maximum": 32}, False, 1),
        (None, {"nullable": True}, True, 0),
    ],
)
def test_number_type_validator(
    dummy_value: int,
    dummy_variable_properties: Dict[str, int],
    expected_result: bool,
    expected_warning_call_count: int,
    mocker: MockerFixture,
) -> None:
    """Unit test for function _number_type_validator in file input_manager.py"""

    # Arrange
    input_manager = InputManager()
    dummy_var_path: list[str | int] = ["dummy_num"]
    dummy_input_data = {"a": 1}
    dummy_properties_key = "dummy_variable_properties"
    unused_bool_input = False
    dummy_counter = mocker.MagicMock(autospec=ElementsCounter)
    patch_extract = mocker.patch.object(input_manager, "_extract_input_data_by_key_list", return_value=dummy_value)
    patch_path_to_str = mocker.patch.object(input_manager, "_convert_variable_path_to_str", return_value="dummy_name")

    with patch("RUFAS.input_manager.om.add_warning") as add_warning:
        result = input_manager._number_type_validator(
            dummy_var_path,
            dummy_variable_properties,
            dummy_input_data,
            unused_bool_input,
            dummy_properties_key,
            dummy_counter,
            unused_bool_input,
        )

    patch_extract.assert_called_once_with(
        dummy_input_data, dummy_var_path, dummy_variable_properties, unused_bool_input
    )
    if dummy_variable_properties.get("nullable", False) is False:
        patch_path_to_str.assert_called_once_with(dummy_var_path)
    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.parametrize(
    "dummy_value, dummy_variable_properties, expected_result, expected_warning_call_count",
    [
        ("cow", {"pattern": r"cow", "minimum_length": 1, "maximum_length": 5}, True, 0),
        ("cow", {"pattern": r".{3}", "minimum_length": 1}, True, 0),
        (
            "COW",
            {"pattern": r"cow", "minimum_length": 1, "maximum_length": 5},
            False,
            1,
        ),
        ("cow", {"minimum_length": 1, "maximum_length": 5}, True, 0),
        ("cow", {"minimum_length": 5}, False, 1),
        ("cow", {"maximum_length": 1}, False, 1),
        (None, {"pattern": r"cow", "minimum_length": 1}, False, 1),
        (42.0, {"pattern": r"cow", "maximum_length": 3}, False, 1),
        (None, {"nullable": True}, True, 0),
    ],
)
def test_string_type_validator(
    dummy_value: int,
    dummy_variable_properties: Dict[str, int],
    expected_result: bool,
    expected_warning_call_count: int,
    mock_input_manager: InputManager,
    mocker: MockerFixture,
) -> None:
    """Unit test for _string_type_validator function in file input_manager.py"""
    var_path: list[str | int] = ["dummy_var_path"]
    dummy_properties_key = "dummy_variable_properties"
    dummy_input_data = {"a": 1, "b": 2}
    dummy_counter = mocker.MagicMock(autospec=ElementsCounter)
    unused_bool_input = False
    patch_extract = mocker.patch.object(mock_input_manager, "_extract_input_data_by_key_list", return_value=dummy_value)
    patch_path_to_str = mocker.patch.object(
        mock_input_manager, "_convert_variable_path_to_str", return_value="dummy_name"
    )
    add_warning = mocker.patch("RUFAS.input_manager.om.add_warning")

    result = mock_input_manager._string_type_validator(
        var_path,
        dummy_variable_properties,
        dummy_input_data,
        unused_bool_input,
        dummy_properties_key,
        dummy_counter,
        unused_bool_input,
    )

    patch_extract.assert_called_once_with(dummy_input_data, var_path, dummy_variable_properties, unused_bool_input)
    if dummy_variable_properties.get("nullable", False) is False:
        patch_path_to_str.assert_called_once_with(var_path)
    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.fixture
def mock_metadata_for_fix_data(mocker: MockerFixture) -> dict[str, dict[str, Any]]:
    return {
        "dummyconfig": {},
        "files": {
            "array": {"properties": "array_properties"},
            "string": {"properties": "string_properties"},
            "number": {"properties": "number_properties"},
            "boolean": {"properties": "boolean_properties"},
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
                "element1": {"type": "bool", "default": True},
                "element2": {"type": "bool", "default": False},
                "element3": {
                    "type": "object",
                    "element4": {"type": "bool", "default": True},
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


def mock_input_array_data_for_fix_data() -> Dict[str, Dict[str, Any] | List[Any]]:
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


@pytest.mark.parametrize(
    "dummy_variable_properties, dummy_element_hierarchy, expected_value, expected_result, expected_warning_call_count",
    [
        (
            {
                "type": "array",
                "default": [1, 2, 3, 4, 5],
                "minimum_length": 5,
                "maximum_length": 10,
            },
            ["element1"],
            [1, 2, 3, 4, 5],
            True,
            2,
        ),
        (
            {
                "type": "array",
                "default": [],
                "minimum_length": 0,
                "maximum_length": 5,
            },
            ["element2"],
            [],
            True,
            2,
        ),
        (
            {
                "type": "array",
                "default": [1, 2, 3, 4, 5],
                "minimum_length": 5,
                "maximum_length": 10,
            },
            ["element3"],
            [1, 2, 3, 4, 5],
            True,
            2,
        ),
        (
            {
                "type": "array",
                "default": [1, 2, 3],
                "minimum_length": 2,
                "maximum_length": 5,
            },
            ["element4", "element5"],
            [1, 2, 3],
            True,
            2,
        ),
    ],
)
def test_fix_array_type_fixable_data(
    dummy_variable_properties: Dict[str, Any],
    dummy_element_hierarchy: List[str],
    expected_value: List[Any],
    expected_result: bool,
    expected_warning_call_count: int,
    mock_input_manager: InputManager,
) -> None:
    """Unit test for fixable array-type data for _fix_data function in file input_manager.py"""

    dummy_input_data = mock_input_array_data_for_fix_data()
    dummy_properties_key = "dummy_variable_properties"

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(
            dummy_variable_properties,
            dummy_element_hierarchy,
            dummy_input_data,
            dummy_properties_key,
        )

    variable_to_check = reduce(lambda d, key: d[key], dummy_element_hierarchy, dummy_input_data)
    assert variable_to_check == expected_value
    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.parametrize(
    "dummy_variable_properties, dummy_element_hierarchy, expected_result, expected_warning_call_count",
    [
        (
            {
                "type": "array",
                "minimum_length": 5,
                "maximum_length": 10,
            },
            ["element6"],
            False,
            0,
        ),
        (
            {
                "type": "array",
                "minimum_length": 0,
                "maximum_length": 5,
            },
            ["element7"],
            False,
            0,
        ),
        (
            {
                "type": "array",
                "minimum_length": 2,
                "maximum_length": 5,
            },
            ["element8"],
            False,
            0,
        ),
        (
            {
                "type": "array",
                "minimum_length": 2,
                "maximum_length": 5,
            },
            ["element9", "element10"],
            False,
            0,
        ),
    ],
)
def test_fix_array_type_critical_data(
    dummy_variable_properties: Dict[str, Any],
    dummy_element_hierarchy: List[str],
    expected_result: bool,
    expected_warning_call_count: int,
    mock_input_manager: InputManager,
) -> None:
    """Unit test for critical array-type data for _fix_data function in file input_manager.py"""

    dummy_input_data = mock_input_array_data_for_fix_data()
    dummy_properties_key = "dummy_variable_properties"

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(
            dummy_variable_properties,
            dummy_element_hierarchy,
            dummy_input_data,
            dummy_properties_key,
        )

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


@pytest.mark.parametrize(
    "dummy_variable_properties, dummy_element_hierarchy, expected_value, expected_result, expected_warning_call_count",
    [
        (
            {
                "type": "str",
                "default": "cow",
                "pattern": r"cow",
                "minimum_length": 1,
                "maximum_length": 5,
            },
            ["element1"],
            "cow",
            True,
            2,
        ),
        (
            {
                "type": "str",
                "default": "",
                "minimum_length": 0,
                "maximum_length": 5,
            },
            ["element2"],
            "",
            True,
            2,
        ),
        (
            {
                "type": "str",
                "default": "cow",
                "pattern": r"cow",
                "minimum_length": 2,
                "maximum_length": 5,
            },
            ["element3"],
            "cow",
            True,
            2,
        ),
        (
            {
                "type": "str",
                "default": "cow",
                "pattern": r"cow",
                "minimum_length": 2,
                "maximum_length": 5,
            },
            ["element4", "element5"],
            "cow",
            True,
            2,
        ),
    ],
)
def test_fix_string_type_fixable_data(
    dummy_variable_properties: dict[str, Any],
    dummy_element_hierarchy: list[str],
    expected_value: str,
    expected_result: bool,
    expected_warning_call_count: int,
    mock_input_manager: InputManager,
) -> None:
    """Unit test for fixable string-type data for _fix_data function in file input_manager.py"""

    dummy_input_data = mock_input_string_data_for_fix_data()
    dummy_properties_key = "dummy_variable_properties"

    with (patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning,):
        result = mock_input_manager._fix_data(
            dummy_variable_properties,
            dummy_element_hierarchy,
            dummy_input_data,
            dummy_properties_key,
        )

    variable_to_check = reduce(lambda d, key: d[key], dummy_element_hierarchy, dummy_input_data)
    assert variable_to_check == expected_value
    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


def test_fix_string_type_csv_data(mock_input_manager: InputManager) -> None:
    """Unit test for fixable number-type data from a csv array for _fix_data function in file input_manager.py"""

    dummy_input_data = {"element1": [1, 2, 3, 4, 5]}
    dummy_variable_properties = {"type": "number", "maximum": 4, "default": 3}
    dummy_element_hierarchy = ["element1", 4]
    dummy_properties_key = "dummy_variable_properties"

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(
            dummy_variable_properties,
            dummy_element_hierarchy,
            dummy_input_data,
            dummy_properties_key,
        )

    fixed_variable = reduce(lambda d, key: d[key], dummy_element_hierarchy, dummy_input_data)

    assert fixed_variable == 3
    assert result is True
    assert add_warning.call_count == 2


@pytest.mark.parametrize(
    "dummy_variable_properties, dummy_element_hierarchy, expected_result, expected_warning_call_count",
    [
        (
            {
                "type": "str",
                "pattern": r"cow",
                "minimum_length": 1,
                "maximum_length": 5,
            },
            ["element6"],
            False,
            0,
        ),
        (
            {
                "type": "str",
                "pattern": r"cow",
                "minimum_length": 1,
                "maximum_length": 5,
            },
            ["element7"],
            False,
            0,
        ),
        (
            {
                "type": "str",
                "pattern": r"cow",
                "minimum_length": 1,
                "maximum_length": 5,
            },
            ["element8"],
            False,
            0,
        ),
        (
            {
                "type": "str",
                "pattern": r"cow",
                "minimum_length": 2,
                "maximum_length": 5,
            },
            ["element9", "element10"],
            False,
            0,
        ),
    ],
)
def test_fix_string_type_critical_data(
    dummy_variable_properties: dict[str, Any],
    dummy_element_hierarchy: list[str],
    expected_result: bool,
    expected_warning_call_count: int,
    mock_input_manager: InputManager,
) -> None:
    """Unit test for critical string-type data for _fix_data function in file input_manager.py"""

    dummy_input_data = mock_input_string_data_for_fix_data()
    dummy_properties_key = "dummy_variable_properties"

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(
            dummy_variable_properties,
            dummy_element_hierarchy,
            dummy_input_data,
            dummy_properties_key,
        )

    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


def mock_input_number_data_for_fix_data() -> Dict[str, Dict[str, int] | int]:
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


@pytest.mark.parametrize(
    "dummy_variable_properties, dummy_element_hierarchy, expected_value, expected_result, expected_warning_call_count",
    [
        (
            {
                "type": "number",
                "default": 5,
                "minimum": 0,
                "maximum": 10,
            },
            ["element1"],
            5,
            True,
            2,
        ),
        (
            {
                "type": "number",
                "default": 0,
                "minimum": 0,
                "maximum": 10,
            },
            ["element2"],
            0,
            True,
            2,
        ),
        (
            {
                "type": "number",
                "default": 5,
                "minimum": 1,
                "maximum": 10,
            },
            ["element3"],
            5,
            True,
            2,
        ),
        (
            {
                "type": "number",
                "default": 5,
                "minimum": 0,
                "maximum": 10,
            },
            ["element4", "element5"],
            5,
            True,
            2,
        ),
    ],
)
def test_fix_number_type_fixable_data(
    dummy_variable_properties: dict[str, Any],
    dummy_element_hierarchy: list[str],
    expected_value: str,
    expected_result: bool,
    expected_warning_call_count: int,
    mock_input_manager: InputManager,
) -> None:
    """Unit test for fixable number-type data for _fix_data function in file input_manager.py"""

    dummy_input_data = mock_input_number_data_for_fix_data()
    dummy_properties_key = "dummy_variable_properties"

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(
            dummy_variable_properties,
            dummy_element_hierarchy,
            dummy_input_data,
            dummy_properties_key,
        )

    variable_to_check = reduce(lambda d, key: d[key], dummy_element_hierarchy, dummy_input_data)
    assert variable_to_check == expected_value
    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.parametrize(
    "dummy_variable_properties, dummy_element_hierarchy, expected_result, " "expected_warning_call_count",
    [
        (
            {
                "type": "number",
                "minimum": 0,
                "maximum": 10,
            },
            ["element6"],
            False,
            0,
        ),
        (
            {
                "type": "number",
                "minimum": 0,
                "maximum": 10,
            },
            ["element7"],
            False,
            0,
        ),
        (
            {
                "type": "number",
                "minimum": 1,
                "maximum": 10,
            },
            ["element8"],
            False,
            0,
        ),
        (
            {
                "type": "number",
                "minimum": 0,
                "maximum": 10,
            },
            ["element9", "element10"],
            False,
            0,
        ),
    ],
)
def test_fix_number_type_critical_data(
    dummy_variable_properties: dict[str, Any],
    dummy_element_hierarchy: list[str],
    expected_result: bool,
    expected_warning_call_count: int,
    mock_input_manager: InputManager,
    mock_metadata_for_fix_data: Dict[str, Dict[str, Any]],
) -> None:
    """Unit test for critical number-type data for _fix_data function in file input_manager.py"""

    dummy_input_data = mock_input_number_data_for_fix_data()
    dummy_properties_key = "dummy_variable_properties"

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(
            dummy_variable_properties,
            dummy_element_hierarchy,
            dummy_input_data,
            dummy_properties_key,
        )

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
            "submodule1": {"nested_var": "dummyvalue2"},
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
    "dummy_data_path, expected_result",
    [
        ("module1.integer_var", 5),
        ("module1.float_var", 0.5),
        ("module1.string_var", "dummyvalue1"),
        ("module1.boolean_var", True),
        ("module1.integer_array_var", [1, 2, 3]),
        ("module1.float_array_var", [0.1, 0.2, 3.14159]),
        ("module1.string_array_var", ["1", "2", "3", "4", "5"]),
        ("module1.string_var", "dummyvalue1"),
        ("module1.boolean_array_var", [True, False]),
        ("module1.submodule1.nested_var", "dummyvalue2"),
        ("module2.submodule1.nested_module1.nested_var1", "dummyvalue3"),
        ("module2.submodule1.nested_module1.nested_var2", "dummyvalue4"),
        (
            "module1",
            {
                "integer_var": 5,
                "float_var": 0.5,
                "string_var": "dummyvalue1",
                "boolean_var": True,
                "integer_array_var": [1, 2, 3],
                "float_array_var": [0.1, 0.2, 3.14159],
                "string_array_var": ["1", "2", "3", "4", "5"],
                "boolean_array_var": [True, False],
                "submodule1": {"nested_var": "dummyvalue2"},
            },
        ),
    ],
)
def test_get_data_with_valid_key(
    dummy_data_path: str,
    mock_pool_for_get_data: Dict[str, Dict[str, Any]],
    expected_result: Any,
    mocker: MockerFixture,
) -> None:
    """Unit test for get_data function in file input_manager.py with a valid data_path key"""

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__pool", mock_pool_for_get_data)

    # Act
    result = input_manager.get_data(dummy_data_path)

    assert result == expected_result


@pytest.mark.parametrize(
    "dummy_data_path, error_key",
    [
        ("module1.dummy_key", "dummy_key"),
        ("module1.submodule1.dummy_key", "dummy_key"),
        ("module2.submodule1.nested_module1.dummy_key", "dummy_key"),
        ("module2.submodule1.dummy_key.nested_var1", "dummy_key"),
        ("module2.dummy_key.nested_module1.nested_var1", "dummy_key"),
    ],
)
def test_get_data_returns_none(
    dummy_data_path: str,
    error_key: str,
    mock_pool_for_get_data: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """Unit test for function get_data raising an exception in file input_manager.py"""

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__pool", mock_pool_for_get_data)
    patch_for_add_error = mocker.patch("RUFAS.input_manager.om.add_error")

    # Act
    result = input_manager.get_data(dummy_data_path)

    # Assert
    assert result is None
    patch_for_add_error.assert_called_once_with(
        "Validation: data not found",
        mocker.ANY,
        mocker.ANY,
    )
    assert error_key in patch_for_add_error.call_args[0][1]


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
                        "minimum": 0,
                    },
                    "cow_repro_method": {
                        "type": "string",
                        "description": "Cow Reproductive Program (select one)",
                        "default": "ED",
                        "pattern": "^{TAI|ED|ED-TAI}$",
                    },
                    "simulate_animals": {
                        "type": "boolean",
                        "description": "Whether or not to simulate animals during the simulation",
                        "default": True,
                    },
                    "dummy_cow_array": {
                        "type": "array",
                        "description": "dummy array for testing purposes",
                        "default": [1, 2, 3, 4],
                        "maximum_length": 7,
                    },
                },
            },
            "dummy_crop_properties": {
                "crop_species": {
                    "type": "string",
                    "description": "Name of the crop being grown.",
                    "pattern": "^{generic|corn|spring_wheat|winter_wheat|cereal_rye|spring_barley}$",
                },
                "harvest_years": {
                    "type": "array",
                    "description": "Calendar years in which the harvesting occurs",
                    "minimum_length": 0,
                    "default": [],
                    "properties": {"type": "number", "minimum": 1},
                },
                "pattern_skip": {
                    "type": "number",
                    "description": "Number of years to be skipped between schedule repetitions.",
                    "minimum": 0,
                    "default": 0,
                },
                "simulate_crops": {
                    "type": "boolean",
                    "description": "Dummy boolean variable for testing",
                    "default": False,
                },
            },
        }
    }


@pytest.mark.parametrize(
    "dummy_metadata_path, expected_result, expected_warning_call_count",
    [
        ("properties.dummy_animal_properties.herd_information.calf_num.default", 8, 0),
        (
            "properties.dummy_animal_properties.herd_information.calf_num",
            {
                "type": "number",
                "description": "Number of Calves (head)",
                "default": 8,
                "minimum": 0,
            },
            0,
        ),
        (
            "properties.dummy_animal_properties.herd_information.cow_repro_method.type",
            "string",
            0,
        ),
        (
            "properties.dummy_animal_properties.herd_information.cow_repro_method.pattern",
            "^{TAI|ED|ED-TAI}$",
            0,
        ),
        (
            "properties.dummy_animal_properties.herd_information.simulate_animals.type",
            "boolean",
            0,
        ),
        (
            "properties.dummy_animal_properties.herd_information.dummy_cow_array",
            {
                "type": "array",
                "description": "dummy array for testing purposes",
                "default": [1, 2, 3, 4],
                "maximum_length": 7,
            },
            0,
        ),
        (
            "properties.dummy_crop_properties.crop_species.description",
            "Name of the crop being grown.",
            0,
        ),
        ("properties.dummy_crop_properties.harvest_years.type", "array", 0),
        (
            "properties.dummy_crop_properties.harvest_years",
            {
                "type": "array",
                "description": "Calendar years in which the harvesting occurs",
                "minimum_length": 0,
                "default": [],
                "properties": {"type": "number", "minimum": 1},
            },
            0,
        ),
        ("properties.dummy_crop_properties.pattern_skip.minimum", 0, 0),
        (
            "properties.dummy_crop_properties.simulate_crops",
            {
                "type": "boolean",
                "description": "Dummy boolean variable for testing",
                "default": False,
            },
            0,
        ),
        (
            "properties",
            {
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
                            "minimum": 0,
                        },
                        "cow_repro_method": {
                            "type": "string",
                            "description": "Cow Reproductive Program (select one)",
                            "default": "ED",
                            "pattern": "^{TAI|ED|ED-TAI}$",
                        },
                        "simulate_animals": {
                            "type": "boolean",
                            "description": "Whether or not to simulate animals during the simulation",
                            "default": True,
                        },
                        "dummy_cow_array": {
                            "type": "array",
                            "description": "dummy array for testing purposes",
                            "default": [1, 2, 3, 4],
                            "maximum_length": 7,
                        },
                    },
                },
                "dummy_crop_properties": {
                    "crop_species": {
                        "type": "string",
                        "description": "Name of the crop being grown.",
                        "pattern": "^{generic|corn|spring_wheat|winter_wheat|cereal_rye|spring_barley}$",
                    },
                    "harvest_years": {
                        "type": "array",
                        "description": "Calendar years in which the harvesting occurs",
                        "minimum_length": 0,
                        "default": [],
                        "properties": {"type": "number", "minimum": 1},
                    },
                    "pattern_skip": {
                        "type": "number",
                        "description": "Number of years to be skipped between schedule repetitions.",
                        "minimum": 0,
                        "default": 0,
                    },
                    "simulate_crops": {
                        "type": "boolean",
                        "description": "Dummy boolean variable for testing",
                        "default": False,
                    },
                },
            },
            0,
        ),
    ],
)
def test_get_metadata_with_valid_key(
    dummy_metadata_path: str,
    mock_pool_for_get_metadata: Dict[str, Dict[str, Any]],
    expected_result: Any,
    expected_warning_call_count: int,
    mock_input_manager: InputManager,
) -> None:
    """Unit test for get_metadata function in file input_manager.py with a valid metadata_path key"""

    mock_input_manager.meta_data = mock_pool_for_get_metadata

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager.get_metadata(dummy_metadata_path)

    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.parametrize(
    "dummy_metadata_path, expected_error_parent_address, expected_error_invalid_key, expected_warning_call_count",
    [
        (
            "dummy_animal_properties.herd_information.calf_num.dummy_key",
            "dummy_animal_properties.herd_information.calf_num",
            "dummy_key",
            1,
        ),
        (
            "dummy_animal_properties.herd_information.dummy_key",
            "dummy_animal_properties.herd_information",
            "dummy_key",
            1,
        ),
        (
            "dummy_crop_properties.crop_species.dummy_key",
            "dummy_crop_properties.crop_species",
            "dummy_key",
            1,
        ),
        ("dummy_crop_properties.dummy_key", "dummy_crop_properties", "dummy_key", 1),
        (
            "dummy_crop_properties.pattern_skip.dummy_key",
            "dummy_crop_properties.pattern_skip",
            "dummy_key",
            1,
        ),
    ],
)
def test_get_metadata_raises_exception(
    dummy_metadata_path: str,
    expected_error_parent_address: str,
    expected_error_invalid_key: str,
    mock_pool_for_get_metadata: Dict[str, Dict[str, Any]],
    expected_warning_call_count: int,
    mock_input_manager: InputManager,
) -> None:
    """Unit test for function get_metadata raising an exception in file input_manager.py"""

    mock_input_manager._InputManager__metadata = mock_pool_for_get_metadata

    with patch("RUFAS.output_manager.OutputManager.add_error") as add_error:
        with pytest.raises(KeyError) as key_error:
            mock_input_manager.get_metadata(dummy_metadata_path)

        error_message = key_error.value.__str__().strip("'")
        assert (
            error_message == f'Data not found: Cannot find "{dummy_metadata_path}", '
            f'"{expected_error_parent_address}" does not have attribute '
            f'"{expected_error_invalid_key}".'
        )
        assert add_error.call_count == expected_warning_call_count


def test_get_data_by_properties_no_data(
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Tests that error is handled properly when get_metadata() raises KeyError."""
    mock_input_manager.get_metadata = MagicMock(side_effect=KeyError)

    with patch("RUFAS.output_manager.OutputManager.add_error") as add_error:
        actual = mock_input_manager.get_data_keys_by_properties("dummy_property")

    assert add_error.call_count == 1
    assert actual == []

    mock_input_manager.get_metadata = input_manager_original_method_states["get_metadata"]


@pytest.mark.parametrize(
    "data,expected_keys",
    [
        (
            {
                "key_1": {"properties": "properties_1"},
                "key_2": {"properties": "properties_2"},
                "key_3": {"properties": "target_properties"},
                "key_4": {"properties": "target_properties"},
                "key_5": {"properties": "target_properties"},
            },
            ["key_3", "key_4", "key_5"],
        ),
        (
            {
                "key_1": {"properties": "target_properties"},
                "key_2": {"properties": "value"},
                "key_3": {"properties": "target_properties"},
                "key_4": {"properties": "properties_4"},
                "key_5": {"properties": "properties_5"},
            },
            ["key_1", "key_3"],
        ),
        ({"key_1": {"properties": "value"}, "key_2": {"properties": "value"}, "key_3": {"properties": "value"}}, []),
        ({}, []),
    ],
)
def test_get_data_keys_by_properties(
    data: dict[str, dict[str, str]],
    expected_keys: list[str],
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test that Input Manager gets data keys by properties correctly."""
    mock_input_manager.get_metadata = MagicMock(return_value=data)

    actual = mock_input_manager.get_data_keys_by_properties("target_properties")

    assert actual == expected_keys

    mock_input_manager.get_metadata = input_manager_original_method_states["get_metadata"]


def test_flush_pool(mock_input_manager: InputManager) -> None:
    """Tests that the InputManager pool is flushed correctly."""

    mock_input_manager._InputManager__pool = {"Key": "I never metadata I didn't like!"}

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        mock_input_manager.flush_pool()

        assert mock_input_manager._InputManager__pool == {}
        assert add_log.call_count == 1


@pytest.mark.parametrize("properties_blob_key", ["properties1", "properties2"])
def test_metadata_properties_exist(
    properties_blob_key: str,
    mock_input_manager: InputManager,
    mock_metadata: Dict[str, Dict[str, Any]],
) -> None:
    mock_input_manager._InputManager__metadata = mock_metadata

    result = mock_input_manager._metadata_properties_exist(
        variable_name="mock_variable", properties_blob_key=properties_blob_key
    )

    assert result is True


def test_metadata_properties_exist_no_metadata(
    mock_input_manager: InputManager,
) -> None:
    mock_input_manager._InputManager__metadata = {}

    with pytest.raises(ValueError):
        mock_input_manager._metadata_properties_exist(
            variable_name="mock_variable",
            properties_blob_key="mock_properties_blob_key",
        )


@pytest.mark.parametrize(
    "variable_name, properties_blob_key",
    [("variable1", "propertiesA"), ("variable2", "propertiesB")],
)
def test_metadata_properties_exists_invalid_properties_blob_key(
    variable_name: str,
    properties_blob_key: str,
    mock_input_manager: InputManager,
    mock_metadata: Dict[str, Dict[str, Any]],
) -> None:
    mock_input_manager._InputManager__metadata = mock_metadata

    with pytest.raises(KeyError):
        mock_input_manager._metadata_properties_exist(
            variable_name=variable_name, properties_blob_key=properties_blob_key
        )


@pytest.fixture
def mock_metadata_for_add_variable_to_pool() -> Dict[str, Dict[str, Any]]:
    return {
        "files": {
            "file1": {
                "type": "json",
                "path": "path/to/json/file1.json",
                "properties": "properties1",
            },
            "file2": {
                "type": "csv",
                "path": "path/to/csv/file2.csv",
                "properties": "properties2",
            },
        },
        "properties": {
            "dict_data": {
                "int": "some_value1",
                "str": "some_value2",
                "float": "some_value1",
                "int_array": "some_value2",
                "float_array": "some_value1",
                "str_arr": "some_value2",
                "type": "object",
                "modifiability": "unrequired unlocked",
            },
            "array_of_int_data": {"array_of_int_data": "some_value3"},
            "array_of_float_data": {"array_of_float_data": "some_value3"},
            "array_of_str_data": {"array_of_str_data": "some_value3"},
            "array_of_dict_data": {"array_of_dict_data": "some_value3"},
            "dict_of_array_data": {
                "array1": "some_value1",
                "array2": "some_value2",
                "array3": "some_value1",
            },
        },
    }


@pytest.mark.parametrize(
    "variable_name, data, properties_blob_key, starting_im_pool",
    [
        (
            "dict_data",
            {
                "int": 0,
                "str": "",
                "float": 0.0,
                "int_array": [0, 1, 2],
                "float_array": [0.0, 1.1, 2.2],
                "str_arr": ["example_str1", "example_str2", "example_str3"],
            },
            "dict_data",
            {},
        ),
        (
            "array_of_int_data",
            {"array_of_int_data": [0, 1, 2]},
            "array_of_int_data",
            {},
        ),
        (
            "array_of_float_data",
            {"array_of_float_data": [0.0, 1.1, 2.2]},
            "array_of_float_data",
            {},
        ),
        (
            "array_of_str_data",
            {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]},
            "array_of_str_data",
            {},
        ),
        (
            "array_of_dict_data",
            {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]},
            "array_of_dict_data",
            {},
        ),
        (
            "dict_of_array_data",
            {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
            "dict_of_array_data",
            {},
        ),
        (
            "dict_data",
            {
                "int": 0,
                "str": "",
                "float": 0.0,
                "int_array": [0, 1, 2],
                "float_array": [0.0, 1.1, 2.2],
                "str_arr": ["example_str1", "example_str2", "example_str3"],
            },
            "dict_data",
            {"dict_data": {"1": 1}},
        ),
        (
            "array_of_int_data",
            {"array_of_int_data": [0, 1, 2]},
            "array_of_int_data",
            {"array_of_int_data": [-1, 0, 1]},
        ),
        (
            "array_of_float_data",
            {"array_of_float_data": [0.0, 1.1, 2.2]},
            "array_of_float_data",
            {"array_of_float_data": [-1.0, 0.0, 1.0]},
        ),
        (
            "array_of_str_data",
            {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]},
            "array_of_str_data",
            {"array_of_str_data": ["a", "b", "c"]},
        ),
        (
            "array_of_dict_data",
            {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]},
            "array_of_dict_data",
            {"array_of_dict_data": [{"A": -1}, {"B": 0}, {"C": 1}]},
        ),
        (
            "dict_of_array_data",
            {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
            "dict_of_array_data",
            {"dict_of_array_data": {"a": [1, 2, 3]}},
        ),
    ],
)
def test_add_variable_to_pool_valid(
    variable_name: str,
    data: Any,
    properties_blob_key: str,
    starting_im_pool: Dict[str, Any],
    mock_metadata_for_add_variable_to_pool: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """Unit test for add_variable_to_pool() method in file input_manager.py with valid data."""

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata_for_add_variable_to_pool)
    mocker.patch.object(input_manager, "_InputManager__pool", starting_im_pool)
    mocker.patch.object(input_manager, "_validate_input_by_type", return_value=True)
    expected_add_warning_count = 1 if starting_im_pool else 0
    patch_for_add_warning = mocker.patch("RUFAS.input_manager.om.add_warning")
    patch_for_add_error = mocker.patch("RUFAS.input_manager.om.add_error")

    # Act
    result = input_manager._add_variable_to_pool(
        variable_name=variable_name,
        input_data=data,
        properties_blob_key=properties_blob_key,
        eager_termination=False,
    )

    # Assert
    assert result
    assert patch_for_add_warning.call_count == expected_add_warning_count
    assert patch_for_add_error.call_count == 0
    assert variable_name in input_manager.pool
    assert input_manager.get_data(variable_name) == data


@pytest.mark.parametrize(
    "variable_name, data, properties_blob_key, starting_im_pool",
    [
        (
            "dict_data",
            {
                "int": 0,
                "str": "",
                "float": 0.0,
                "int_array": [0, 1, 2],
                "float_array": [0.0, 1.1, 2.2],
                "str_arr": ["example_str1", "example_str2", "example_str3"],
            },
            "dict_data",
            {},
        ),
        (
            "array_of_int_data",
            {"array_of_int_data": [0, 1, 2]},
            "array_of_int_data",
            {},
        ),
        (
            "array_of_float_data",
            {"array_of_float_data": [0.0, 1.1, 2.2]},
            "array_of_float_data",
            {},
        ),
        (
            "array_of_str_data",
            {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]},
            "array_of_str_data",
            {},
        ),
        (
            "array_of_dict_data",
            {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]},
            "array_of_dict_data",
            {},
        ),
        (
            "dict_of_array_data",
            {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
            "dict_of_array_data",
            {},
        ),
        (
            "dict_data",
            {
                "int": 0,
                "str": "",
                "float": 0.0,
                "int_array": [0, 1, 2],
                "float_array": [0.0, 1.1, 2.2],
                "str_arr": ["example_str1", "example_str2", "example_str3"],
            },
            "dict_data",
            {"dict_data": {"1": 1}},
        ),
        (
            "array_of_int_data",
            {"array_of_int_data": [0, 1, 2]},
            "array_of_int_data",
            {"array_of_int_data": [-1, 0, 1]},
        ),
        (
            "array_of_float_data",
            {"array_of_float_data": [0.0, 1.1, 2.2]},
            "array_of_float_data",
            {"array_of_float_data": [-1.0, 0.0, 1.0]},
        ),
        (
            "array_of_str_data",
            {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]},
            "array_of_str_data",
            {"array_of_str_data": ["a", "b", "c"]},
        ),
        (
            "array_of_dict_data",
            {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]},
            "array_of_dict_data",
            {"array_of_dict_data": [{"A": -1}, {"B": 0}, {"C": 1}]},
        ),
        (
            "dict_of_array_data",
            {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
            "dict_of_array_data",
            {"dict_of_array_data": {"a": [1, 2, 3]}},
        ),
    ],
)
def test_add_variable_to_pool_invalid(
    variable_name: str,
    data: Any,
    properties_blob_key: str,
    starting_im_pool: Dict[str, Any],
    mock_metadata_for_add_variable_to_pool: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """
    Unit test for add_variable_to_pool() method in file input_manager.py with invalid data.
    """

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata_for_add_variable_to_pool)
    mocker.patch.object(input_manager, "_InputManager__pool", starting_im_pool)
    mocker.patch.object(input_manager, "_validate_input_by_type", return_value=False)
    patch_for_add_warning = mocker.patch("RUFAS.input_manager.om.add_warning")
    patch_for_add_error = mocker.patch("RUFAS.input_manager.om.add_error")
    mock_elements_counter = mocker.MagicMock()
    mock_elements_counter.invalid_elements = 1
    mocker.patch("RUFAS.input_manager.ElementsCounter", return_value=mock_elements_counter)

    # Act
    result = input_manager._add_variable_to_pool(
        variable_name=variable_name,
        input_data=data,
        properties_blob_key=properties_blob_key,
        eager_termination=False,
    )

    # Assert
    assert result is False
    assert patch_for_add_warning.call_count == 0
    assert patch_for_add_error.call_count == 1

    if starting_im_pool:
        assert starting_im_pool[variable_name] == input_manager.get_data(variable_name)
    else:
        assert variable_name not in input_manager.pool


@pytest.mark.parametrize(
    "variable_name, data, properties_blob_key, starting_im_pool",
    [
        (
            "dict_data",
            {
                "int": 0,
                "str": "",
                "float": 0.0,
                "int_array": [0, 1, 2],
                "float_array": [0.0, 1.1, 2.2],
                "str_arr": ["example_str1", "example_str2", "example_str3"],
            },
            "dict_data",
            {},
        ),
        (
            "array_of_int_data",
            {"array_of_int_data": [0, 1, 2]},
            "array_of_int_data",
            {},
        ),
        (
            "array_of_float_data",
            {"array_of_float_data": [0.0, 1.1, 2.2]},
            "array_of_float_data",
            {},
        ),
        (
            "array_of_str_data",
            {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]},
            "array_of_str_data",
            {},
        ),
        (
            "array_of_dict_data",
            {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]},
            "array_of_dict_data",
            {},
        ),
        (
            "dict_of_array_data",
            {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
            "dict_of_array_data",
            {},
        ),
        (
            "dict_data",
            {
                "int": 0,
                "str": "",
                "float": 0.0,
                "int_array": [0, 1, 2],
                "float_array": [0.0, 1.1, 2.2],
                "str_arr": ["example_str1", "example_str2", "example_str3"],
            },
            "dict_data",
            {"dict_data": {"1": 1}},
        ),
        (
            "array_of_int_data",
            {"array_of_int_data": [0, 1, 2]},
            "array_of_int_data",
            {"array_of_int_data": [-1, 0, 1]},
        ),
        (
            "array_of_float_data",
            {"array_of_float_data": [0.0, 1.1, 2.2]},
            "array_of_float_data",
            {"array_of_float_data": [-1.0, 0.0, 1.0]},
        ),
        (
            "array_of_str_data",
            {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]},
            "array_of_str_data",
            {"array_of_str_data": ["a", "b", "c"]},
        ),
        (
            "array_of_dict_data",
            {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]},
            "array_of_dict_data",
            {"array_of_dict_data": [{"A": -1}, {"B": 0}, {"C": 1}]},
        ),
        (
            "dict_of_array_data",
            {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
            "dict_of_array_data",
            {"dict_of_array_data": {"a": [1, 2, 3]}},
        ),
    ],
)
def test_add_variable_to_pool_eager_termination(
    variable_name: str,
    data: Any,
    properties_blob_key: str,
    starting_im_pool: Dict[str, Any],
    mock_metadata_for_add_variable_to_pool: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """
    Unit test for add_variable_to_pool() method in file input_manager.py with eager_termination=True.
    """

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata_for_add_variable_to_pool)
    mocker.patch.object(input_manager, "_InputManager__pool", starting_im_pool)
    mocker.patch.object(input_manager, "_validate_input_by_type", return_value=False)
    mock_elements_counter = mocker.MagicMock()
    mock_elements_counter.invalid_elements = 1
    mocker.patch("RUFAS.input_manager.ElementsCounter", return_value=mock_elements_counter)
    patch_for_add_warning = mocker.patch("RUFAS.input_manager.om.add_warning")
    patch_for_add_error = mocker.patch("RUFAS.input_manager.om.add_error")

    # Act
    with pytest.raises(ValueError):
        input_manager._add_variable_to_pool(
            variable_name=variable_name,
            input_data=data,
            properties_blob_key=properties_blob_key,
            eager_termination=True,
        )

    # Assert
    assert patch_for_add_warning.call_count == 0
    assert patch_for_add_error.call_count == 1
    if starting_im_pool:
        assert starting_im_pool[variable_name] == input_manager.get_data(variable_name)
    else:
        assert variable_name not in input_manager.pool


@pytest.mark.parametrize(
    "variable_name, data, properties_blob_key",
    [
        ("var1", {}, "key1"),
        ("var2", {"a": 1}, "key2"),
        ("var3", {"a": "A", "b": 2, "c": True}, "key3"),
    ],
)
def test_add_dict_variable_to_pool(
    variable_name: str,
    data: Dict[str, Any],
    properties_blob_key: str,
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
) -> None:
    mock_input_manager._metadata_properties_exist = MagicMock(return_value=True)
    mock_input_manager._add_variable_to_pool = MagicMock(return_value=True)

    with patch("RUFAS.output_manager.OutputManager.add_error") as mock_om_add_error:
        result = mock_input_manager.add_dict_variable_to_pool(
            variable_name=variable_name,
            data=data,
            properties_blob_key=properties_blob_key,
            eager_termination=False,
        )

    assert result is True
    assert mock_om_add_error.call_count == 0
    mock_input_manager._metadata_properties_exist.assert_called_once_with(
        variable_name=variable_name, properties_blob_key=properties_blob_key
    )
    mock_input_manager._add_variable_to_pool.assert_called_once_with(
        variable_name=variable_name,
        input_data=data,
        properties_blob_key=properties_blob_key,
        eager_termination=False,
    )

    mock_input_manager.add_dict_variable_to_pool = input_manager_original_method_states["add_dict_variable_to_pool"]
    mock_input_manager._metadata_properties_exist = input_manager_original_method_states["_metadata_properties_exist"]
    mock_input_manager._add_variable_to_pool = input_manager_original_method_states["_add_variable_to_pool"]


@pytest.mark.parametrize(
    "variable_name, data, properties_blob_key",
    [
        ("var1", "a", "key1"),
        ("var2", [1, 2, 3], "key2"),
        ("var3", 5, "key3"),
    ],
)
def test_add_dict_variable_to_pool_type_error(
    variable_name: str,
    data: Dict[str, Any],
    properties_blob_key: str,
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
) -> None:
    mock_input_manager._metadata_properties_exist = MagicMock(return_value=True)
    mock_input_manager._add_variable_to_pool = MagicMock(return_value=True)

    with patch("RUFAS.output_manager.OutputManager.add_error") as mock_om_add_error:
        with pytest.raises(TypeError):
            mock_input_manager.add_dict_variable_to_pool(
                variable_name=variable_name,
                data=data,
                properties_blob_key=properties_blob_key,
                eager_termination=False,
            )

        assert mock_om_add_error.call_count == 1
        mock_input_manager._metadata_properties_exist.assert_not_called()
        mock_input_manager._add_variable_to_pool.assert_not_called()

        mock_input_manager.add_dict_variable_to_pool = input_manager_original_method_states["add_dict_variable_to_pool"]
        mock_input_manager._metadata_properties_exist = input_manager_original_method_states[
            "_metadata_properties_exist"
        ]
        mock_input_manager._add_variable_to_pool = input_manager_original_method_states["_add_variable_to_pool"]


@pytest.mark.parametrize(
    "variable_name, data, properties_blob_key",
    [
        ("var1", {}, "key1"),
        ("var2", {"a": 1}, "key2"),
        ("var3", {"a": "A", "b": 2, "c": True}, "key3"),
    ],
)
def test_add_dict_variable_to_pool_invalid_data(
    variable_name: str,
    data: Dict[str, Any],
    properties_blob_key: str,
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
) -> None:
    mock_input_manager._metadata_properties_exist = MagicMock(return_value=True)
    mock_input_manager._add_variable_to_pool = MagicMock(return_value=False)

    with patch("RUFAS.output_manager.OutputManager.add_error") as mock_om_add_error:
        result = mock_input_manager.add_dict_variable_to_pool(
            variable_name=variable_name,
            data=data,
            properties_blob_key=properties_blob_key,
            eager_termination=False,
        )

        assert result is False
        assert mock_om_add_error.call_count == 0
        mock_input_manager._metadata_properties_exist.assert_called_once_with(
            variable_name=variable_name, properties_blob_key=properties_blob_key
        )
        mock_input_manager._add_variable_to_pool.assert_called_once_with(
            variable_name=variable_name,
            input_data=data,
            properties_blob_key=properties_blob_key,
            eager_termination=False,
        )

        mock_input_manager.add_dict_variable_to_pool = input_manager_original_method_states["add_dict_variable_to_pool"]
        mock_input_manager._metadata_properties_exist = input_manager_original_method_states[
            "_metadata_properties_exist"
        ]
        mock_input_manager._add_variable_to_pool = input_manager_original_method_states["_add_variable_to_pool"]


def test_add_dict_variable_to_pool_metadata_properties_do_not_exist(
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
) -> None:
    mock_input_manager._metadata_properties_exist = MagicMock(return_value=False)
    mock_input_manager._add_variable_to_pool = MagicMock(return_value=False)

    with patch("RUFAS.output_manager.OutputManager.add_error") as mock_om_add_error:
        result = mock_input_manager.add_dict_variable_to_pool(
            variable_name="var1",
            data={"a": 1},
            properties_blob_key="key2",
            eager_termination=False,
        )

        assert result is False
        assert mock_om_add_error.call_count == 0
        mock_input_manager._metadata_properties_exist.assert_called_once_with(
            variable_name="var1", properties_blob_key="key2"
        )
        mock_input_manager._add_variable_to_pool.assert_not_called()

        mock_input_manager.add_dict_variable_to_pool = input_manager_original_method_states["add_dict_variable_to_pool"]
        mock_input_manager._metadata_properties_exist = input_manager_original_method_states[
            "_metadata_properties_exist"
        ]
        mock_input_manager._add_variable_to_pool = input_manager_original_method_states["_add_variable_to_pool"]


@pytest.mark.parametrize(
    "variable_name, data, properties_blob_key",
    [
        ("var1", [1, 2, 3], "key1"),
        ("var2", ["a", "b", "c"], "key2"),
        ("var3", [0.0, 1.1, 2.2], "key3"),
        ("var4", {"a": [1, 2, 3], "b": ["a", "b", "c"], "c": [0.0, 1.1, 2.2]}, "key4"),
    ],
)
def test_add_tabular_variable_to_pool(
    variable_name: str,
    data: Dict[str, List[Any]] | List[Any],
    properties_blob_key: str,
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test for InputManager.add_tabular_variable_to_pool() for valid data"""
    mock_input_manager._metadata_properties_exist = MagicMock(return_value=True)
    mock_input_manager._add_variable_to_pool = MagicMock(return_value=True)

    expected_data_for_add_variable_to_pool = {variable_name: data} if isinstance(data, List) else data

    with patch("RUFAS.output_manager.OutputManager.add_error") as mock_om_add_error:
        result = mock_input_manager.add_tabular_variable_to_pool(
            variable_name=variable_name,
            data=data,
            properties_blob_key=properties_blob_key,
            eager_termination=False,
        )

    assert result is True
    assert mock_om_add_error.call_count == 0
    mock_input_manager._metadata_properties_exist.assert_called_once_with(
        variable_name=variable_name, properties_blob_key=properties_blob_key
    )
    mock_input_manager._add_variable_to_pool.assert_called_once_with(
        variable_name=variable_name,
        input_data=expected_data_for_add_variable_to_pool,
        properties_blob_key=properties_blob_key,
        eager_termination=False,
    )

    mock_input_manager.add_tabular_variable_to_pool = input_manager_original_method_states[
        "add_tabular_variable_to_pool"
    ]
    mock_input_manager._metadata_properties_exist = input_manager_original_method_states["_metadata_properties_exist"]
    mock_input_manager._add_variable_to_pool = input_manager_original_method_states["_add_variable_to_pool"]


@pytest.mark.parametrize(
    "variable_name, data, properties_blob_key",
    [
        ("var1", "a", "key1"),
        ("var2", True, "key2"),
        ("var3", 5, "key3"),
    ],
)
def test_add_tabular_variable_to_pool_type_error(
    variable_name: str,
    data: Dict[str, List[Any]] | List[Any],
    properties_blob_key: str,
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test for InputManager.add_tabular_variable_to_pool() for incorrect data type is received"""
    mock_input_manager._metadata_properties_exist = MagicMock(return_value=True)
    mock_input_manager._add_variable_to_pool = MagicMock(return_value=True)

    with patch("RUFAS.output_manager.OutputManager.add_error") as mock_om_add_error:
        with pytest.raises(TypeError):
            mock_input_manager.add_tabular_variable_to_pool(
                variable_name=variable_name,
                data=data,
                properties_blob_key=properties_blob_key,
                eager_termination=False,
            )

        assert mock_om_add_error.call_count == 1
        mock_input_manager._metadata_properties_exist.assert_not_called()
        mock_input_manager._add_variable_to_pool.assert_not_called()

        mock_input_manager.add_tabular_variable_to_pool = input_manager_original_method_states[
            "add_tabular_variable_to_pool"
        ]
        mock_input_manager._metadata_properties_exist = input_manager_original_method_states[
            "_metadata_properties_exist"
        ]
        mock_input_manager._add_variable_to_pool = input_manager_original_method_states["_add_variable_to_pool"]


@pytest.mark.parametrize(
    "variable_name, data, properties_blob_key",
    [
        ("var1", [1, 2, 3], "key1"),
        ("var2", ["a", "b", "c"], "key2"),
        ("var3", [0.0, 1.1, 2.2], "key3"),
        ("var4", {"a": [1, 2, 3], "b": ["a", "b", "c"], "c": [0.0, 1.1, 2.2]}, "key4"),
    ],
)
def test_add_tabular_variable_to_pool_invalid_data(
    variable_name: str,
    data: Dict[str, List[Any]] | List[Any],
    properties_blob_key: str,
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test for InputManager.add_tabular_variable_to_pool() for invalid data and eager_termination set to False"""
    mock_input_manager._metadata_properties_exist = MagicMock(return_value=True)
    mock_input_manager._add_variable_to_pool = MagicMock(return_value=False)

    expected_data_for_add_variable_to_pool = {variable_name: data} if isinstance(data, List) else data

    with patch("RUFAS.output_manager.OutputManager.add_error") as mock_om_add_error:
        result = mock_input_manager.add_tabular_variable_to_pool(
            variable_name=variable_name,
            data=data,
            properties_blob_key=properties_blob_key,
            eager_termination=False,
        )

        assert result is False
        assert mock_om_add_error.call_count == 0
        mock_input_manager._metadata_properties_exist.assert_called_once_with(
            variable_name=variable_name, properties_blob_key=properties_blob_key
        )
        mock_input_manager._add_variable_to_pool.assert_called_once_with(
            variable_name=variable_name,
            input_data=expected_data_for_add_variable_to_pool,
            properties_blob_key=properties_blob_key,
            eager_termination=False,
        )

        mock_input_manager.add_tabular_variable_to_pool = input_manager_original_method_states[
            "add_tabular_variable_to_pool"
        ]
        mock_input_manager._metadata_properties_exist = input_manager_original_method_states[
            "_metadata_properties_exist"
        ]
        mock_input_manager._add_variable_to_pool = input_manager_original_method_states["_add_variable_to_pool"]


def test_add_tabular_variable_to_pool_metadata_properties_do_not_exist(
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Test for InputManager.add_tabular_variable_to_pool() for invalid data and eager_termination set to False"""
    mock_input_manager._metadata_properties_exist = MagicMock(return_value=False)
    mock_input_manager._add_variable_to_pool = MagicMock(return_value=False)

    with patch("RUFAS.output_manager.OutputManager.add_error") as mock_om_add_error:
        result = mock_input_manager.add_tabular_variable_to_pool(
            variable_name="variable_name",
            data=["data"],
            properties_blob_key="properties_blob_key",
            eager_termination=False,
        )

        assert result is False
        assert mock_om_add_error.call_count == 0
        mock_input_manager._metadata_properties_exist.assert_called_once_with(
            variable_name="variable_name", properties_blob_key="properties_blob_key"
        )
        mock_input_manager._add_variable_to_pool.assert_not_called()

        mock_input_manager.add_tabular_variable_to_pool = input_manager_original_method_states[
            "add_tabular_variable_to_pool"
        ]
        mock_input_manager._metadata_properties_exist = input_manager_original_method_states[
            "_metadata_properties_exist"
        ]
        mock_input_manager._add_variable_to_pool = input_manager_original_method_states["_add_variable_to_pool"]


@pytest.mark.parametrize(
    "variable_name, variable_properties, expected_modifiability",
    [
        ("var1", {"type": "string", "modifiability": "required locked"}, Modifiability.REQUIRED_LOCKED),
        ("var2", {"type": "number", "modifiability": "required unlocked"}, Modifiability.REQUIRED_UNLOCKED),
        ("var3", {"type": "bool", "modifiability": "unrequired unlocked"}, Modifiability.UNREQUIRED_UNLOCKED),
        ("var4", {"type": "object"}, Modifiability.UNREQUIRED_UNLOCKED),
    ],
)
def test_get_variable_modifiability(
    variable_name: str,
    variable_properties: Dict[str, Any],
    expected_modifiability: Modifiability,
    mock_input_manager: InputManager,
) -> None:
    with patch("RUFAS.output_manager.OutputManager.add_warning") as mock_om_add_warning:
        actual_modifiability = mock_input_manager._get_variable_modifiability(
            variable_name=variable_name, variable_properties=variable_properties
        )

        mock_om_add_warning.assert_not_called()
        assert actual_modifiability == expected_modifiability


@pytest.mark.parametrize(
    "variable_name, variable_properties",
    [
        ("var1", {"type": "string", "modifiability": "a"}),
        ("var2", {"type": "number", "modifiability": "b"}),
        ("var3", {"type": "bool", "modifiability": "c"}),
        ("var4", {"type": "object", "modifiability": "d"}),
    ],
)
def test_get_variable_modifiability_unknown_modifiability(
    variable_name: str,
    variable_properties: Dict[str, Any],
    mock_input_manager: InputManager,
) -> None:
    with patch("RUFAS.output_manager.OutputManager.add_warning") as mock_om_add_warning:
        mock_input_manager._get_variable_modifiability(
            variable_name=variable_name, variable_properties=variable_properties
        )

    mock_om_add_warning.assert_called_once()


@pytest.mark.parametrize(
    "variable_name, variable_properties",
    [
        ("var1", {"type": "string", "modifiability": "unrequired unlocked"}),
        ("var2", {"type": "number", "modifiability": "unrequired unlocked"}),
        ("var3", {"type": "bool", "modifiability": "unrequired unlocked"}),
        ("var4", {"type": "object"}),
    ],
)
def test_log_missing_data_initialization_input_not_required(
    variable_name: str,
    variable_properties: Dict[str, Any],
    mock_input_manager: InputManager,
    mocker: MockerFixture,
) -> None:
    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")
    mock_add_warning = mocker.patch("RUFAS.output_manager.OutputManager.add_warning")

    mock_input_manager._log_missing_data(
        var_name=variable_name, variable_properties=variable_properties, called_during_initialization=True
    )

    assert mock_add_error.call_count == 0
    assert mock_add_warning.call_count == 1


@pytest.mark.parametrize(
    "variable_name, variable_properties",
    [
        ("var1", {"type": "string", "modifiability": "required locked"}),
        ("var2", {"type": "number", "modifiability": "required unlocked"}),
        ("var3", {"type": "bool", "modifiability": "required unlocked"}),
        ("var4", {"type": "object", "modifiability": "required locked"}),
    ],
)
def test_log_missing_data_initialization_key_error(
    variable_name: str,
    variable_properties: Dict[str, Any],
    mock_input_manager: InputManager,
    mocker: MockerFixture,
) -> None:
    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")
    mock_add_warning = mocker.patch("RUFAS.output_manager.OutputManager.add_warning")

    with pytest.raises(KeyError):
        mock_input_manager._log_missing_data(
            var_name=variable_name, variable_properties=variable_properties, called_during_initialization=True
        )

    assert mock_add_error.call_count == 1
    assert mock_add_warning.call_count == 0


@pytest.mark.parametrize(
    "variable_name, variable_properties",
    [
        ("var1", {"type": "string", "modifiability": "required locked"}),
        ("var2", {"type": "number", "modifiability": "required locked"}),
        ("var3", {"type": "bool", "modifiability": "unrequired locked"}),
        ("var4", {"type": "object", "modifiability": "unrequired locked"}),
    ],
)
def test_log_missing_data_runtime_key_error(
    variable_name: str,
    variable_properties: Dict[str, Any],
    mock_input_manager: InputManager,
    mocker: MockerFixture,
) -> None:
    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")
    mock_add_warning = mocker.patch("RUFAS.output_manager.OutputManager.add_warning")

    with pytest.raises(KeyError):
        mock_input_manager._log_missing_data(
            var_name=variable_name, variable_properties=variable_properties, called_during_initialization=False
        )

    assert mock_add_error.call_count == 1
    assert mock_add_warning.call_count == 0


@pytest.mark.parametrize(
    "nested_dict, element_hierarchy, value, expected_result",
    [
        ({}, ["a"], 1, {"a": 1}),
        ({"a": 1}, ["a"], 2, {"a": 2}),
        ({"a": {"b": 1}}, ["a", "c"], 2, {"a": {"b": 1, "c": 2}}),
        ({"a": {"b": {"c": 1}}}, ["a", "b", "d"], 2, {"a": {"b": {"c": 1, "d": 2}}}),
        ({"a": {"b": {"c": 1}}}, ["a", "b", "d", "e"], 2, {"a": {"b": {"c": 1, "d": {"e": 2}}}}),
    ],
)
def test_set_nested_value(
    nested_dict: Dict[str, Any],
    element_hierarchy: List[str],
    value: Any,
    expected_result: Dict[str, Any],
    mock_input_manager: InputManager,
) -> None:
    actual_result = mock_input_manager._set_nested_value(
        nested_dict=nested_dict, element_hierarchy=element_hierarchy, value=value
    )

    assert actual_result == expected_result


@pytest.fixture
def mock_metadata_for_add_variable_to_pool_nested() -> Dict[str, Dict[str, Any]]:
    return {
        "properties": {
            "dict_data_runtime_modifiable": {
                "type": "object",
                "modifiability": "unrequired unlocked",
                "int": {
                    "type": "number",
                    "modifiability": "unrequired unlocked",
                },
                "str": {
                    "type": "string",
                    "modifiability": "unrequired unlocked",
                },
                "float": {
                    "type": "number",
                    "modifiability": "unrequired unlocked",
                },
                "int_array": {
                    "type": "array",
                    "modifiability": "unrequired unlocked",
                    "properties": {
                        "type": "number",
                        "modifiability": "unrequired unlocked",
                    },
                },
                "float_array": {
                    "type": "array",
                    "modifiability": "unrequired unlocked",
                    "properties": {
                        "type": "number",
                        "modifiability": "unrequired unlocked",
                    },
                },
                "str_arr": {
                    "type": "array",
                    "modifiability": "unrequired unlocked",
                    "properties": {
                        "type": "string",
                        "modifiability": "unrequired unlocked",
                    },
                },
                "nested_dict": {
                    "type": "object",
                    "modifiability": "unrequired unlocked",
                    "a": {
                        "type": "object",
                        "modifiability": "unrequired unlocked",
                        "b": {
                            "type": "object",
                            "modifiability": "unrequired unlocked",
                            "c": {
                                "type": "object",
                                "modifiability": "unrequired unlocked",
                                "d": {
                                    "type": "number",
                                    "modifiability": "unrequired unlocked",
                                },
                            },
                        },
                    },
                    "A": {
                        "type": "object",
                        "modifiability": "unrequired unlocked",
                        "B": {
                            "type": "object",
                            "modifiability": "unrequired unlocked",
                            "C": {
                                "type": "string",
                                "modifiability": "unrequired unlocked",
                            },
                        },
                    },
                },
            },
            "array_of_int_data_runtime_modifiable": {
                "type": "array",
                "modifiability": "required unlocked",
                "properties": {
                    "type": "number",
                    "modifiability": "required unlocked",
                },
            },
            "array_of_float_data_runtime_modifiable": {
                "type": "array",
                "modifiability": "required unlocked",
                "properties": {
                    "type": "number",
                    "modifiability": "required unlocked",
                },
            },
            "array_of_str_data_runtime_modifiable": {
                "type": "array",
                "modifiability": "required unlocked",
                "properties": {
                    "type": "string",
                    "modifiability": "required unlocked",
                },
            },
            "array_of_dict_data_runtime_modifiable": {
                "type": "array",
                "modifiability": "required unlocked",
                "properties": {
                    "type": "object",
                    "modifiability": "required unlocked",
                    "int": {
                        "type": "number",
                        "modifiability": "required unlocked",
                    },
                    "str": {
                        "type": "string",
                        "modifiability": "required unlocked",
                    },
                    "float": {
                        "type": "number",
                        "modifiability": "required unlocked",
                    },
                },
            },
            "dict_of_array_data_runtime_modifiable": {
                "array1": {
                    "type": "array",
                    "modifiability": "required unlocked",
                    "properties": {
                        "type": "number",
                        "modifiability": "required unlocked",
                    },
                },
                "array2": {
                    "type": "array",
                    "modifiability": "required unlocked",
                    "properties": {
                        "type": "number",
                        "modifiability": "required unlocked",
                    },
                },
                "array3": {
                    "type": "array",
                    "modifiability": "required unlocked",
                    "properties": {
                        "type": "string",
                        "modifiability": "required unlocked",
                    },
                },
            },
            "dict_data_runtime_unmodifiable": {
                "type": "object",
                "modifiability": "required locked",
                "int": {
                    "type": "number",
                    "modifiability": "required locked",
                },
                "str": {
                    "type": "string",
                    "modifiability": "required locked",
                },
                "float": {
                    "type": "number",
                    "modifiability": "required locked",
                },
                "int_array": {
                    "type": "array",
                    "modifiability": "required locked",
                    "properties": {
                        "type": "number",
                        "modifiability": "required locked",
                    },
                },
                "float_array": {
                    "type": "array",
                    "modifiability": "required locked",
                    "properties": {
                        "type": "number",
                        "modifiability": "required locked",
                    },
                },
                "str_arr": {
                    "type": "array",
                    "modifiability": "required locked",
                    "properties": {
                        "type": "string",
                        "modifiability": "required locked",
                    },
                },
                "nested_dict": {
                    "type": "object",
                    "modifiability": "required locked",
                    "a": {
                        "type": "object",
                        "modifiability": "required locked",
                        "b": {
                            "type": "object",
                            "modifiability": "required locked",
                            "c": {
                                "type": "object",
                                "modifiability": "required locked",
                                "d": {
                                    "type": "number",
                                    "modifiability": "required locked",
                                },
                            },
                        },
                    },
                    "A": {
                        "type": "object",
                        "modifiability": "required locked",
                        "B": {
                            "type": "object",
                            "modifiability": "required locked",
                            "C": {
                                "type": "string",
                                "modifiability": "required locked",
                            },
                        },
                    },
                },
            },
            "array_of_int_data_runtime_unmodifiable": {
                "type": "array",
                "modifiability": "required locked",
                "properties": {
                    "type": "number",
                    "modifiability": "required locked",
                },
            },
            "array_of_float_data_runtime_unmodifiable": {
                "type": "array",
                "modifiability": "required locked",
                "properties": {
                    "type": "number",
                    "modifiability": "required locked",
                },
            },
            "array_of_str_data_runtime_unmodifiable": {
                "type": "array",
                "modifiability": "required locked",
                "properties": {
                    "type": "string",
                    "modifiability": "required locked",
                },
            },
            "array_of_dict_data_runtime_unmodifiable": {
                "type": "array",
                "modifiability": "required locked",
                "properties": {
                    "type": "object",
                    "modifiability": "required locked",
                    "int": {
                        "type": "number",
                        "modifiability": "required locked",
                    },
                    "str": {
                        "type": "string",
                        "modifiability": "required locked",
                    },
                    "float": {
                        "type": "number",
                        "modifiability": "required locked",
                    },
                },
            },
            "dict_of_array_data_runtime_unmodifiable": {
                "array1": {
                    "type": "array",
                    "modifiability": "required locked",
                    "properties": {
                        "type": "number",
                        "modifiability": "required locked",
                    },
                },
                "array2": {
                    "type": "array",
                    "modifiability": "required locked",
                    "properties": {
                        "type": "number",
                        "modifiability": "required locked",
                    },
                },
                "array3": {
                    "type": "array",
                    "modifiability": "required locked",
                    "properties": {
                        "type": "string",
                        "modifiability": "required locked",
                    },
                },
            },
        }
    }


@pytest.fixture
def mock_pool_for_add_variable_to_pool_nested() -> Dict[str, Dict[str, Any] | List[Any]]:
    return {
        "dict_data_runtime_modifiable": {
            "int": 1,
            "str": "2",
            "float": 3.3,
            "int_array": [4, 5, 6],
            "float_array": [7.7, 8.8, 9.9],
            "str_arr": ["10"],
            "nested_dict": {"a": {"b": {"c": {"d": 11}}}},
        },
        "array_of_int_data_runtime_modifiable": [1, 2, 3, 4, 5],
        "array_of_float_data_runtime_modifiable": [1.1, 2.2, 3.3, 4.4, 5.5],
        "array_of_str_data_runtime_modifiable": ["1.1", "2.2", "3.3", "4.4", "5.5"],
        "array_of_dict_data_runtime_modifiable": [
            {"int": 1, "str": "2", "float": 3.3},
            {"int": 4, "str": "5", "float": 6.6},
            {"int": 7, "str": "8", "float": 9.9},
        ],
        "dict_of_array_data_runtime_modifiable": {
            "array1": [1, 2, 3],
            "array2": [4.4, 5.5, 6.6],
            "array3": ["7.7", "8.8", "9.9"],
        },
        "dict_data_runtime_unmodifiable": {
            "int": 1,
            "str": "2",
            "float": 3.3,
            "int_array": [4, 5, 6],
            "float_array": [7.7, 8.8, 9.9],
            "str_arr": ["10"],
            "nested_dict": {"a": {"b": {"c": {"d": 11}}}, "A": {"B": {"C": "CCCCC!"}}},
        },
        "array_of_int_data_runtime_unmodifiable": [1, 2, 3, 4, 5],
        "array_of_float_data_runtime_unmodifiable": [1.1, 2.2, 3.3, 4.4, 5.5],
        "array_of_str_data_runtime_unmodifiable": ["1.1", "2.2", "3.3", "4.4", "5.5"],
        "array_of_dict_data_runtime_unmodifiable": [
            {"int": 1, "str": "2", "float": 3.3},
            {"int": 4, "str": "5", "float": 6.6},
            {"int": 7, "str": "8", "float": 9.9},
        ],
        "dict_of_array_data_runtime_unmodifiable": {
            "array1": [1, 2, 3],
            "array2": [4.4, 5.5, 6.6],
            "array3": ["7.7", "8.8", "9.9"],
        },
    }


@pytest.mark.parametrize(
    "variable_name, data, properties_blob_key, is_modifiable_during_runtime, eager_termination,"
    "expected_add_warning_call_count",
    [
        ("dict_data_runtime_modifiable.nested_dict.a.b.c.d", {"d": 11}, "dict_data_runtime_modifiable", True, False, 0),
        ("dict_data_runtime_modifiable.nested_dict.A.B.C", {"C": None}, "dict_data_runtime_modifiable", True, False, 0),
        (
            "dict_data_runtime_unmodifiable.nested_dict.a.b.c.d",
            {"d": 11},
            "dict_data_runtime_unmodifiable",
            False,
            False,
            1,
        ),
        (
            "dict_data_runtime_unmodifiable.nested_dict.A.B.C",
            {"C": "CCCCC!"},
            "dict_data_runtime_unmodifiable",
            False,
            False,
            1,
        ),
        ("dict_data_runtime_unmodifiable.nested_dict.a.b.c.d", 10, "dict_data_runtime_unmodifiable", False, True, 0),
        ("dict_data_runtime_unmodifiable.nested_dict.A.B.C", "10", "dict_data_runtime_unmodifiable", False, True, 0),
    ],
)
def test_add_variable_to_pool_nested(
    variable_name: str,
    data: Dict[str, Any],
    properties_blob_key: str,
    is_modifiable_during_runtime: bool,
    eager_termination: bool,
    expected_add_warning_call_count: int,
    mock_metadata_for_add_variable_to_pool_nested: Dict[str, Any],
    mock_pool_for_add_variable_to_pool_nested: Dict[str, Any],
    mocker: MockerFixture,
) -> None:
    """
    Unit test for the _add_variable_to_pool method of the InputManager class for nested data.
    """

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata_for_add_variable_to_pool_nested)
    mocker.patch.object(input_manager, "_InputManager__pool", mock_pool_for_add_variable_to_pool_nested)
    mocker.patch.object(input_manager, "_validate_input_by_type", return_value=True)
    mocker.patch("RUFAS.input_manager.om.add_log")
    patch_for_add_warning = mocker.patch("RUFAS.input_manager.om.add_warning")
    mocker.patch("RUFAS.input_manager.om.add_error")

    if (not is_modifiable_during_runtime) and eager_termination:
        with pytest.raises(PermissionError):
            input_manager._add_variable_to_pool(
                variable_name=variable_name,
                input_data=data,
                properties_blob_key=properties_blob_key,
                eager_termination=eager_termination,
            )
    else:
        result = input_manager._add_variable_to_pool(
            variable_name=variable_name,
            input_data=data,
            properties_blob_key=properties_blob_key,
            eager_termination=False,
        )

        assert result
        assert patch_for_add_warning.call_count == expected_add_warning_call_count
        assert input_manager.get_data(variable_name) == list(data.values())[0]


@pytest.mark.parametrize(
    "missing_keys, keys_with_defaults, expected_calls",
    [
        # Test case with missing keys and keys with default values
        (
            ["missingKey1", "missingKey2"],
            [("keyWithDefault1", "value1"), ("keyWithDefault2", "value2")],
            {
                "error_calls": [
                    (
                        "Validation: missing required property keys",
                        "Missing required property key: missingKey1.",
                    ),
                    (
                        "Validation: missing required property keys",
                        "Missing required property key: missingKey2.",
                    ),
                ],
                "warning_calls": [
                    (
                        "Validation: missing required property keys",
                        "Default value used for required property key that was missing: " "keyWithDefault1 => value1.",
                    ),
                    (
                        "Validation: missing required property keys",
                        "Default value used for required property key that was missing: " "keyWithDefault2 => value2.",
                    ),
                ],
            },
        ),
        # Test case with missing required keys only
        (
            ["missingKey1", "missingKey2"],
            [],
            {
                "error_calls": [
                    (
                        "Validation: missing required property keys",
                        "Missing required property key: missingKey1.",
                    ),
                    (
                        "Validation: missing required property keys",
                        "Missing required property key: missingKey2.",
                    ),
                ],
                "warning_calls": [],
            },
        ),
        # Test case with only keys with default values
        (
            [],
            [("keyWithDefault", "defaultValue")],
            {
                "error_calls": [],
                "warning_calls": [
                    (
                        "Validation: missing required property keys",
                        "Default value used for required property key that was missing: "
                        "keyWithDefault => defaultValue.",
                    ),
                ],
            },
        ),
    ],
)
def test_log_missing_keys(
    missing_keys: List[str],
    keys_with_defaults: List[Tuple[str, Any]],
    expected_calls: Dict[str, Tuple[str, str]],
    mocker: MockerFixture,
) -> None:
    """
    Unit test for the _log_missing_keys method of the InputManager class.
    """

    # Arrange
    input_manager = InputManager()
    mock_add_error = mocker.patch("RUFAS.input_manager.om.add_error")
    mock_add_warning = mocker.patch("RUFAS.input_manager.om.add_warning")

    # Act
    input_manager._log_missing_keys(missing_keys, keys_with_defaults)

    # Assert
    for call_args in expected_calls["error_calls"]:
        mock_add_error.assert_any_call(*call_args, mocker.ANY)

    for call_args in expected_calls["warning_calls"]:
        mock_add_warning.assert_any_call(*call_args, mocker.ANY)

    assert mock_add_error.call_count == len(expected_calls["error_calls"])
    assert mock_add_warning.call_count == len(expected_calls["warning_calls"])


@pytest.mark.parametrize(
    "input_data, metadata_properties, expected_output",
    [
        ({}, {"prop": {"type": "number", "default": 10}}, ({"prop": 10}, [], [("prop", 10)])),
        (
            {},
            {"prop": {"type": "string", "default": "defaultVal"}},
            ({"prop": "defaultVal"}, [], [("prop", "defaultVal")]),
        ),
        ({}, {"prop": {"type": "bool", "default": True}}, ({"prop": True}, [], [("prop", True)])),
        ({"prop": 5}, {"prop": {"type": "number", "default": 10}}, ({"prop": 5}, [], [])),
        (
            {},
            {
                "nested": {
                    "type": "object",
                    "nestedProp": {"type": "string", "default": "defaultVal"},
                    "default": {"nestedProp": "defaultVal"},
                }
            },
            ({"nested": {"nestedProp": "defaultVal"}}, [], [("nested", {"nestedProp": "defaultVal"})]),
        ),
        (
            {"nested": {}},
            {"nested": {"type": "object", "nestedProp": {"type": "string", "default": "defaultVal"}}},
            ({"nested": {"nestedProp": "defaultVal"}}, [], [("nested.nestedProp", "defaultVal")]),
        ),
        (
            {},
            {
                "arrayProp": {
                    "type": "array",
                    "properties": {
                        "type": "object",
                        "nestedProp": {"type": "number", "default": 42},
                    },
                    "default": [{"nestedProp": 42}],
                },
            },
            ({"arrayProp": [{"nestedProp": 42}]}, [], [("arrayProp", [{"nestedProp": 42}])]),
        ),
        (
            {"arrayProp": []},
            {
                "arrayProp": {
                    "type": "array",
                    "properties": {
                        "type": "object",
                        "nestedProp": {"type": "number", "default": 42},
                        "default": {"nestedProp": 42},
                    },
                },
            },
            ({"arrayProp": [{"nestedProp": 42}]}, [], [("arrayProp[0]", {"nestedProp": 42})]),
        ),
        (
            {"arrayProp": [{}]},
            {
                "arrayProp": {
                    "type": "array",
                    "properties": {"type": "object", "nestedProp": {"type": "number", "default": 42}},
                }
            },
            ({"arrayProp": [{"nestedProp": 42}]}, [], [("arrayProp[0].nestedProp", 42)]),
        ),
        (
            {"arrayProp": [{}]},
            {
                "arrayProp": {
                    "type": "array",
                    "properties": {"type": "object", "nestedProp": {"type": "number"}},
                }
            },
            ({"arrayProp": [{}]}, ["arrayProp[0].nestedProp"], []),
        ),
    ],
)
def test_add_default_values_to_missing_inputs(
    input_data: Dict[str, Any],
    metadata_properties: Dict[str, Any],
    expected_output: Tuple[Dict[str, Any], List[str], List[Tuple[str, Any]]],
) -> None:
    """
    Unit test for the _add_default_values_to_missing_inputs method of the InputManager class.
    """

    # Arrange
    input_manager = InputManager()

    # Act
    output = input_manager._add_default_values_to_missing_inputs(input_data, metadata_properties)

    # Assert
    assert output == expected_output


@pytest.mark.parametrize(
    "input_data, property_key, property_details, expected_output",
    [
        (
            {"arrayProp": []},
            "arrayProp",
            {"properties": {"type": "number", "default": 42}},
            ([42], [], [("arrayProp[0]", 42)]),
        ),
        (
            {"arrayProp": [{}]},
            "arrayProp",
            {"properties": {"type": "object", "nestedProp": {"type": "number", "default": 42}}},
            ([{"nestedProp": 42}], [], [("arrayProp[0].nestedProp", 42)]),
        ),
        (
            {"arrayProp": [{}]},
            "arrayProp",
            {
                "properties": {
                    "type": "object",
                    "nestedProp1": {"type": "number", "default": 42},
                    "nestedProp2": {"type": "string", "default": "defaultVal"},
                }
            },
            (
                [{"nestedProp1": 42, "nestedProp2": "defaultVal"}],
                [],
                [("arrayProp[0].nestedProp1", 42), ("arrayProp[0].nestedProp2", "defaultVal")],
            ),
        ),
        (
            {"arrayProp": [[]]},
            "arrayProp",
            {"properties": {"type": "array", "properties": {"type": "number", "default": 99}}},
            ([[99]], [], [("arrayProp[0][0]", 99)]),
        ),
        ({"arrayProp": [42]}, "arrayProp", {"properties": {"type": "number", "default": 99}}, ([42], [], [])),
        ({"arrayProp": []}, "arrayProp", {"properties": {"type": "number"}}, ([], ["arrayProp[0]"], [])),
    ],
)
def test_add_default_values_to_array_inputs(
    input_data: Dict[str, Any],
    property_key: str,
    property_details: Dict[str, Any],
    expected_output: Tuple[List[Any], List[str], List[Tuple[str, Any]]],
) -> None:
    """
    Unit test for the _add_default_values_to_array_inputs method of the InputManager class.
    """

    # Arrange
    input_manager = InputManager()

    # Act
    output = input_manager._add_default_values_to_array_inputs(input_data, property_key, property_details)

    # Assert
    assert output == expected_output


def test_dump_get_data_logs(
    mock_input_manager: InputManager,
    mocker: MockerFixture,
) -> None:
    mock_input_manager._InputManager__get_data_logs_pool = {
        "14-Feb-2024_Wed_06-15-56.692523": "InputManager.get_data() gets called for ['a'].",
        "14-Feb-2024_Wed_06-15-56.693523": "InputManager.get_data() gets called for ['b'].",
        "14-Feb-2024_Wed_06-15-56.696526": "InputManager.get_data() gets called for ['c'].",
    }
    mock_dir_path = Path("dummy_path")
    mock_generated_file_name = "dummy_file_name.json"
    patch_for_generate_file_name = mocker.patch(
        "RUFAS.input_manager.om.generate_file_name", return_value=mock_generated_file_name
    )
    patch_create_dir = mocker.patch("RUFAS.output_manager.OutputManager.create_directory")

    with patch("RUFAS.output_manager.OutputManager.dict_to_file_json") as mock_dict_to_file_json:
        mock_input_manager.dump_get_data_logs(path=mock_dir_path)

    patch_for_generate_file_name.assert_called_once_with(base_name="InputManager_get_data_log", extension="json")
    patch_create_dir.assert_called_once_with(mock_dir_path)
    mock_dict_to_file_json.assert_called_once_with(
        mock_input_manager._InputManager__get_data_logs_pool, Path("dummy_path", mock_generated_file_name)
    )


@pytest.mark.parametrize(
    "data_address,expected_result,raise_key_error",
    [
        ("animal.herd_information.calf_num", True, False),
        ("animal.herd_information.nonexistent_property", False, True),
    ],
)
def test_check_property_exists_in_pool(
    mocker: MockerFixture, data_address: str, expected_result: bool, raise_key_error: bool
) -> None:
    """
    Unit test for the check_property_exists_in_pool() method of the InputManager class.
    """

    # Arrange
    input_manager = InputManager()
    patch_for_extract_value = mocker.patch.object(input_manager, "_extract_value_by_key_list")
    if raise_key_error:
        patch_for_extract_value.side_effect = KeyError("Key Error")

    # Act
    result = input_manager.check_property_exists_in_pool(data_address)

    # Assert
    assert result == expected_result
    patch_for_extract_value.assert_called_once()


@pytest.mark.parametrize(
    "input_data, variable_path, expected, expected_exception",
    [
        # Success cases
        (
            {
                "animal": {
                    "herd_information": {
                        "calf_num": 8,
                        "heiferI_num": 44,
                        "heiferII_num": 38,
                        "heiferIII_num_springers": 12,
                    }
                }
            },
            ["animal", "herd_information", "calf_num"],
            8,
            None,
        ),
        (
            {
                "manure_management_scenarios": [
                    {"bedding_type": "straw", "manure_handler": "manual scraping"},
                    {"bedding_type": "sawdust", "manure_handler": "flush system"},
                ]
            },
            ["manure_management_scenarios", 0, "bedding_type"],
            "straw",
            None,
        ),
        # Error cases
        (
            {"animal": {"herd_information": {"calf_num": 8}}},
            ["animal", "herd_information", "missing_key"],
            None,
            KeyError,
        ),
        ([{"key": "value"}], [0, "nonexistent_key"], None, KeyError),
    ],
)
def test_extract_value_by_key_list(
    input_data: Union[List[Any], Dict[str, Any]],
    variable_path: List[Union[str, int]],
    expected: Optional[Any],
    expected_exception: Optional[Type[Exception]],
) -> None:
    """
    Unit test for the _extract_value_by_key_list() method of the InputManager class.
    """

    # Arrange
    input_manager = InputManager()

    # Act and assert
    if expected_exception:
        with pytest.raises(expected_exception):
            input_manager._extract_value_by_key_list(input_data, variable_path)
    else:
        result = input_manager._extract_value_by_key_list(input_data, variable_path)
        assert result == expected


@pytest.mark.parametrize(
    "variable_path, expected",
    [
        (["animal", "herd_information", "calf_num"], "animal.herd_information.calf_num"),
        (["manure_management_scenarios", 0, "bedding_type"], "manure_management_scenarios.[0].bedding_type"),
        ([], ""),
        (["level1", 2, "level3", "4", 5], "level1.[2].level3.[4].[5]"),
        (["single_level"], "single_level"),
        (["multi", "path", "with", "strings"], "multi.path.with.strings"),
        ([0, 1, 2, 3], "[0].[1].[2].[3]"),
    ],
)
def test_convert_variable_path_to_str(variable_path: List[Union[str, int]], expected: str) -> None:
    """
    Unit test for the _convert_variable_path_to_str() method of the InputManager class.
    """

    # Arrange
    input_manager = InputManager()

    # Act
    result = input_manager._convert_variable_path_to_str(variable_path)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    "variable_path, variable_properties, input_data, eager_termination, properties_blob_key,"
    "expected_result, patch_extract_return, patch_validate_return",
    [
        # Test case with valid object data
        (
            ["data", "object"],
            {"key": {"type": "string"}},
            {"data": {"object": {"key": "value"}}},
            False,
            "blob_key",
            True,
            {"key": "value"},
            True,
        ),
        # Test case with invalid object data
        (
            ["data", "object"],
            {"key": {"type": "string"}},
            {"data": {"object": "not_a_dict"}},
            False,
            "blob_key",
            False,
            "not_a_dict",
            False,
        ),
        (
            ["data", "object", "nested"],
            {"nested": {"type": "object", "properties": {"key": {"type": "string"}}}},
            {"data": {"object": {"nested": {"key": 123}}}},
            False,
            "blob_key",
            False,
            {"nested": {"key": 123}},
            False,
        ),
        (
            ["data", "early_failure"],
            {"description": "a description", "key1": {"type": "string"}, "key2": {"type": "integer"}},
            {"data": {"early_failure": {"key1": "valid", "key2": "not_an_integer"}}},  # key2 fails validation
            True,
            "blob_key",
            False,
            {"key1": "valid", "key2": "not_an_integer"},
            False,
        ),
    ],
)
def test_object_type_validator(
    mocker: MockerFixture,
    variable_path: List[Union[str, int]],
    variable_properties: Dict[str, Any],
    input_data: Dict[str, Any],
    eager_termination: bool,
    properties_blob_key: str,
    expected_result: bool,
    patch_extract_return: Any,
    patch_validate_return: bool,
) -> None:
    """
    Unit test for the _object_type_validator() method of the InputManager class.
    """

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_extract_input_data_by_key_list", return_value=patch_extract_return)
    mocker.patch.object(input_manager, "_validate_input_by_type", return_value=patch_validate_return)
    mocker.patch("RUFAS.input_manager.om.add_warning", return_value=None)
    mock_elements_counter = mocker.MagicMock()

    # Act
    result = input_manager._object_type_validator(
        variable_path,
        variable_properties,
        input_data,
        eager_termination,
        properties_blob_key,
        mock_elements_counter,
        True,
    )

    # Assert
    assert result == expected_result


@pytest.mark.parametrize(
    "variable_path, variable_properties, input_data, properties_blob_key," "expected_result, expected_warning",
    [
        # Input data is not a list
        (
            ["data", "array"],
            {"maximum_length": 5, "minimum_length": 1},
            "not_a_list",
            "blob_key",
            False,
            "Validation: array container is not a list",
        ),
        # Input list's length is less than the specified minimum length
        (
            ["data", "array"],
            {"maximum_length": 5, "minimum_length": 2},
            [1],
            "blob_key",
            False,
            "Validation: array length less than minimum",
        ),
        # Input list's length exceeds the specified maximum length
        (
            ["data", "array"],
            {"maximum_length": 3, "minimum_length": 1},
            [1, 2, 3, 4],
            "blob_key",
            False,
            "Validation: array length greater than maximum",
        ),
        # Input list's length is within the specified constraints
        (
            ["data", "array"],
            {"maximum_length": 5, "minimum_length": 1},
            [1, 2, 3],
            "blob_key",
            True,
            None,
        ),
    ],
)
def test_validate_array_container_properties(
    mocker: MockerFixture,
    variable_path: List[Union[str, int]],
    variable_properties: Dict[str, Any],
    input_data: Any,
    properties_blob_key: str,
    expected_result: bool,
    expected_warning: str,
) -> None:
    """
    Unit test for the _validate_array_container_properties() method of the InputManager class.
    """

    # Arrange
    input_manager = InputManager()
    patch_for_add_warning = mocker.patch("RUFAS.input_manager.om.add_warning")

    # Act
    result = input_manager._validate_array_container_properties(
        variable_path, variable_properties, input_data, properties_blob_key
    )

    # Assert
    assert result == expected_result
    if expected_warning:
        patch_for_add_warning.assert_called_with(
            expected_warning,
            mocker.ANY,
            mocker.ANY,
        )
    else:
        patch_for_add_warning.assert_not_called()


@pytest.mark.parametrize(
    "variable_path, variable_properties, input_data, eager_termination, properties_blob_key, "
    "patch_extract_return, patch_container_valid, patch_element_valid, expected_result",
    [
        # Array extraction returns a non-list
        (
            ["data", "array"],
            {"properties": {"type": "integer"}},
            {},
            False,
            "blob_key",
            None,
            False,
            True,
            False,
        ),
        # Array container properties are invalid
        (
            ["data", "array"],
            {"properties": {"type": "integer"}},
            {"data": {"array": [1, 2, 3]}},
            False,
            "blob_key",
            [1, 2, 3],
            False,
            True,
            False,
        ),
        # Element validation within the array fails
        (
            ["data", "array"],
            {"properties": {"type": "integer"}},
            {"data": {"array": [1, "two", 3]}},
            False,
            "blob_key",
            [1, "two", 3],
            True,
            False,
            False,
        ),
        # Successful validation of all elements
        (
            ["data", "array"],
            {"properties": {"type": "integer"}},
            {"data": {"array": [1, 2, 3]}},
            False,
            "blob_key",
            [1, 2, 3],
            True,
            True,
            True,
        ),
        # Eager termination on element validation failure
        (
            ["data", "array"],
            {"properties": {"type": "integer"}},
            {"data": {"array": [1, "two", 3]}},
            True,
            "blob_key",
            [1, "two", 3],
            True,
            False,
            False,
        ),
    ],
)
def test_array_type_validator(
    mocker: MockerFixture,
    variable_path: List[Union[str, int]],
    variable_properties: Dict[str, Any],
    input_data: Dict[str, Any],
    eager_termination: bool,
    properties_blob_key: str,
    patch_extract_return: Any,
    patch_container_valid: bool,
    patch_element_valid: bool,
    expected_result: bool,
) -> None:
    """
    Unit test for the _array_type_validator() method of the InputManager class.
    """

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_extract_input_data_by_key_list", return_value=patch_extract_return)
    mocker.patch.object(input_manager, "_validate_array_container_properties", return_value=patch_container_valid)
    mocker.patch.object(input_manager, "_validate_input_by_type", return_value=patch_element_valid)
    mock_elements_counter = mocker.MagicMock()

    # Act
    result = input_manager._array_type_validator(
        variable_path,
        variable_properties,
        input_data,
        eager_termination,
        properties_blob_key,
        mock_elements_counter,
        True,
    )

    # Assert
    assert result == expected_result


@pytest.mark.parametrize(
    "data_type, input_value, expected_result, validator_return, fixable, fix_attempted, simple_type",
    [
        # Primitive data type: valid string
        ("string", "valid string", True, True, False, False, True),
        # Primitive data type: invalid string, fixable
        ("string", "invalid string", True, False, True, True, True),
        # Primitive data type: invalid string, not fixable
        ("string", "invalid string", False, False, False, True, True),
        # Primitive data type: valid number
        ("number", 123, True, True, False, False, True),
        # Primitive data type: invalid number, fixable
        ("number", "invalid number", True, False, True, True, True),
        # Primitive data type: invalid number, not fixable
        ("number", "invalid number", False, False, False, True, True),
        # Primitive data type: valid bool
        ("bool", True, True, True, False, False, True),
        # Primitive data type: invalid bool, fixable
        ("bool", "invalid bool", True, False, True, True, True),
        # Primitive data type: invalid bool, not fixable
        ("bool", "invalid bool", False, False, False, True, True),
        # Complex data type: object, valid
        ("object", {"key": "value"}, True, True, False, False, False),
        # Complex data type: object, invalid
        ("object", "not a dict", False, False, False, False, False),
        # Complex data type: array, valid
        ("array", [1, 2, 3], True, True, False, False, False),
        # Complex data type: array, invalid
        ("array", "not a list", False, False, False, False, False),
    ],
)
def test_validate_input_by_type(
    mocker: MockerFixture,
    data_type: str,
    input_value: Any,
    expected_result: bool,
    validator_return: bool,
    fixable: bool,
    fix_attempted: bool,
    simple_type: bool,
) -> None:
    """
    Unit test for the _validate_input_by_type method of the InputManager class.
    """

    # Arrange
    input_manager = InputManager()
    variable_properties = {"type": data_type}
    variable_path: List[Union[str, int]] = ["path", "to", "variable"]
    input_data = {"path": {"to": {"variable": input_value}}}
    eager_termination = False
    properties_blob_key = "blobKey"
    elements_counter = mocker.MagicMock()

    mocker.patch.object(input_manager, "_extract_value_by_key_list", return_value=input_value)
    mocker.patch.object(input_manager, "_convert_variable_path_to_str", return_value="path.to.variable")
    patch_for_fix_data = mocker.patch.object(input_manager, "_fix_data", return_value=fixable)

    validator_mock = mocker.patch.object(input_manager, f"_{data_type}_type_validator", return_value=validator_return)

    # Act
    result = input_manager._validate_input_by_type(
        variable_properties, variable_path, input_data, eager_termination, properties_blob_key, elements_counter, True
    )

    # Assert
    assert result == expected_result
    validator_mock.assert_called_once()

    if fix_attempted:
        patch_for_fix_data.assert_called_once()
    else:
        patch_for_fix_data.assert_not_called()

    if not simple_type:
        elements_counter.increment.assert_not_called()
    elif expected_result and not fix_attempted:
        elements_counter.increment.assert_called_once_with(ElementState.VALID)
    elif fixable:
        elements_counter.increment.assert_called_once_with(ElementState.FIXED)
    else:
        elements_counter.increment.assert_called_once_with(ElementState.INVALID)


def test_validate_input_by_type_key_error() -> None:
    input_manager = InputManager()
    variable_properties = {"a": "b"}
    variable_path = ["valid_key"]
    properties_blob_key = "dummy_properties_blob_key"
    input_data = {"valid_key": {"another_valid_key": "value"}}
    eager_termination = False
    elements_counter = ElementsCounter()

    # Act and Assert
    with pytest.raises(KeyError):
        input_manager._validate_input_by_type(
            variable_properties,
            variable_path,
            input_data,
            eager_termination,
            properties_blob_key,
            elements_counter,
            True,
        )


def test_validate_input_by_type_value_error() -> None:
    input_manager = InputManager()
    variable_properties = {"type": "b"}
    variable_path = ["valid_key"]
    properties_blob_key = "dummy_properties_blob_key"
    input_data = {"valid_key": {"another_valid_key": "value"}}
    eager_termination = False
    elements_counter = ElementsCounter()

    # Act and Assert
    with pytest.raises(ValueError):
        input_manager._validate_input_by_type(
            variable_properties,
            variable_path,
            input_data,
            eager_termination,
            properties_blob_key,
            elements_counter,
            True,
        )


def test_save_metadata_properties(mock_input_manager: InputManager) -> None:
    """Tests save_metadata_properties() function in InputManager."""
    mock_records = [{"name": "example", "value": 42}]
    output_dir = Path("/fake/directory")
    metadata = {"properties": "test_properties"}
    mock_input_manager.meta_data = metadata

    with (
        patch.object(mock_input_manager, "_parse_metadata_properties", return_value=mock_records) as mock_parse,
        patch("pandas.DataFrame.to_csv") as mock_to_csv,
        patch(
            "RUFAS.output_manager.OutputManager.generate_file_name", return_value="output.csv"
        ) as mock_generate_file_name,
        patch("RUFAS.output_manager.OutputManager.create_directory", new_callable=MagicMock) as mock_create_dir,
    ):

        mock_input_manager.save_metadata_properties(output_dir)

        mock_parse.assert_called_once_with("test_properties")
        mock_create_dir.assert_called_once_with(output_dir)
        mock_to_csv.assert_called_once_with(output_dir / "output.csv", index=False)
        mock_generate_file_name.assert_called_once_with("InputManager_metadata_properties", extension="csv")


@pytest.mark.parametrize(
    "exception, error_message",
    [(FileNotFoundError, "No such file or directory"), (PermissionError, "Permission denied"), (OSError, "OS error")],
)
def test_save_metadata_properties_errors(
    mock_input_manager: InputManager,
    mocker: MockerFixture,
    exception: Type[FileNotFoundError | PermissionError | OSError],
    error_message: str,
) -> None:
    output_dir = Path("/example/dir")
    generated_filename = "file.csv"
    expected_path = output_dir / generated_filename
    metadata = {"properties": "test_properties"}
    mock_input_manager.meta_data = metadata
    mock_records = [{"key": "value"}]

    mock_parse = mocker.patch.object(mock_input_manager, "_parse_metadata_properties", return_value=mock_records)
    mocker.patch("RUFAS.output_manager.OutputManager.create_directory")
    mocker.patch("pandas.DataFrame.to_csv", side_effect=exception(error_message))
    mocker.patch("RUFAS.input_manager.om.generate_file_name", return_value=generated_filename)
    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")

    with pytest.raises(exception) as exc_info:
        mock_input_manager.save_metadata_properties(output_dir)

    assert str(exc_info.value) == error_message

    mock_parse.assert_called_once_with("test_properties")
    mock_add_error.assert_called_once_with(
        "Save CSV failure.", f"Unable to save to {expected_path} because of {error_message}.", ANY
    )


@pytest.mark.parametrize(
    "nested_data, expected_primitive_call_counts, expected_create_record_call_count, expected_results",
    [
        (
            {
                "level1": {
                    "level2": {
                        "property1": {"type": "string", "value": "Hello"},
                        "property2": {"type": "number", "value": 42},
                    },
                    "description": "Level 1 description",
                }
            },
            {"True": 2, "False": 2},
            2,
            [{"mocked": "record"}, {"mocked": "record"}],
        ),
        (
            {
                "level1": {
                    "level2": {
                        "nestedProperty": {
                            "type": "object",
                            "innerProperty": {"type": "string", "value": "Nested", "description": "Deep description"},
                        }
                    },
                    "description": "Level 1 description",
                }
            },
            {"True": 2, "False": 3},
            2,
            [{"mocked": "record"}],
        ),
    ],
)
def test_parse_metadata_properties(
    mock_input_manager: InputManager,
    nested_data: Dict[str, Any],
    expected_primitive_call_counts: Dict[str, int],
    expected_create_record_call_count: int,
    expected_results: List[Dict[str, str]],
) -> None:
    """Tests _parse_metadata_properties() function in InputManager."""

    def side_effect_check_property_type_primitive(value) -> bool:
        """Function to mock check_property_type_primitive dynamically."""
        return value.get("type") in ["string", "number"]

    with (
        patch.object(
            mock_input_manager, "_check_property_type_primitive", side_effect=side_effect_check_property_type_primitive
        ) as mock_primitive,
        patch.object(mock_input_manager, "_create_record", return_value={"mocked": "record"}) as mock_create_record,
    ):

        prefix = ""
        sep = "_"

        result = mock_input_manager._parse_metadata_properties(nested_data, prefix, sep)

        true_count = sum(1 for call in mock_primitive.call_args_list if call[0][0].get("type") in ["string", "number"])
        false_count = len(mock_primitive.call_args_list) - true_count

        assert true_count == expected_primitive_call_counts["True"]
        assert false_count == expected_primitive_call_counts["False"]
        assert mock_create_record.call_count == expected_create_record_call_count
        assert result == expected_results


@pytest.mark.parametrize(
    "property_dict, expected_result",
    [
        # Direct primitive types
        ({"type": "bool"}, True),
        ({"type": "string"}, True),
        ({"type": "number"}, True),
        # Array containing primitive types
        ({"type": "array", "properties": {"type": "bool"}}, True),
        ({"type": "array", "properties": {"type": "string"}}, True),
        ({"type": "array", "properties": {"type": "number"}}, True),
        # Non-primitive type
        ({"type": "object"}, False),
        ({"type": "array", "properties": {"type": "object"}}, False),
        # Invalid or unexpected type cases
        ({"type": "array", "properties": {}}, False),  # Array but properties are empty
        ({"type": "complex"}, False),  # Unsupported type
    ],
)
def test_check_property_type_primitive(
    mock_input_manager: InputManager, property_dict: Dict[str, str], expected_result: bool
) -> None:
    """Tests _check_property_type_primitive() function in InputManager."""
    result = mock_input_manager._check_property_type_primitive(property_dict)
    assert result == expected_result


@pytest.mark.parametrize(
    "data_entry, name, expected_record",
    [
        (
            {
                "type": "string",
                "description": "A simple string",
                "pattern": "[A-Za-z]+",
                "default": "example",
                "maximum": "",
                "minimum": "",
            },
            "user_details_properties_name",
            {
                "properties_group": "user_details_properties",
                "name": "name",
                "type": "string",
                "description": "A simple string",
                "pattern": "[A-Za-z]+",
                "default": "example",
                "maximum": "",
                "minimum": "",
            },
        ),
        (
            {"type": "number", "description": "A simple number"},
            "config_properties_version",
            {
                "properties_group": "config_properties",
                "name": "version",
                "type": "number",
                "description": "A simple number",
                "pattern": "",
                "default": "",
                "maximum": "",
                "minimum": "",
            },
        ),
    ],
)
def test_create_record(
    mock_input_manager: InputManager, data_entry: dict[str, str], name: str, expected_record: dict[str, str]
) -> None:
    """Tests _create_record() function in InputManager."""
    result = mock_input_manager._create_record(data_entry, name)
    assert result == expected_record


@pytest.mark.parametrize(
    "does_file_exist, metadata, expected_exception",
    [
        (
            True,
            {"files": {"file1": {"path": "valid/path/to/file1.csv", "type": "csv", "properties": "some properties"}}},
            False,
        ),
        (
            False,
            {"files": {"file1": {"path": "valid/path/to/file1.json", "type": "json", "properties": "some properties"}}},
            True,
        ),
        (
            True,
            {
                "files": {
                    "file1": {
                        "path": "valid/path/to/file1.txt",
                        "type": "invalid_type",
                        "properties": "some properties",
                    }
                }
            },
            True,
        ),
        (True, {"files": {"file1": {"path": "valid/path/to/file1.json", "properties": "some properties"}}}, True),
        (
            True,
            {
                "files": {
                    "file1": {
                        "path": "valid/path/to/file1.json",
                        "type": "json",
                        "properties": "some properties",
                        "extra_key": "extra_value",
                    }
                }
            },
            True,
        ),
        (
            True,
            {
                "files": {
                    "file1": {
                        "path": "valid/path/to/file1.json",
                        "type": "json",
                        "properties": "",
                    }
                }
            },
            True,
        ),
    ],
)
def test_validate_metadata(
    mocker: MockerFixture,
    does_file_exist: bool,
    metadata: Dict[str, Any],
    expected_exception: bool,
) -> None:
    mocker.patch("os.path.isfile", return_value=does_file_exist)
    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")
    mock_add_log = mocker.patch("RUFAS.output_manager.OutputManager.add_log")
    input_manager = InputManager()
    input_manager.meta_data = metadata

    if expected_exception:
        with pytest.raises(ValueError):
            input_manager._validate_metadata()
        mock_add_log.assert_not_called()
        mock_add_error.assert_called()
    else:
        input_manager._validate_metadata()
        mock_add_log.assert_called()
        mock_add_error.assert_not_called()


@pytest.mark.parametrize(
    "file_exists, error, file_content, modified_properties, expected_diff",
    [
        (
            True,
            None,
            '{"key1": "value1", "key3": "value3"}',
            {"key1": "value1_changed", "key3": "value3"},
            {"values_changed": {"root['key1']": {"old_value": "value1", "new_value": "value1_changed"}}},
        ),
        (
            False,
            OSError,
            '{"key1": "value1", "key3": "value3"}',
            {"key1": "value1_changed", "key3": "value3"},
            {"values_changed": {"root['key1']": {"old_value": "value1", "new_value": "value1_changed"}}},
        ),
        (
            False,
            PermissionError,
            '{"key1": "value1", "key3": "value3"}',
            {"key1": "value1_changed", "key3": "value3"},
            {"values_changed": {"root['key1']": {"old_value": "value1", "new_value": "value1_changed"}}},
        ),
        (True, None, '{"key1": "value1", "key2": "value2"}', {"key1": "value1", "key2": "value2"}, {}),
    ],
)
def test_compare_metadata_properties(
    mocker: MockerFixture,
    file_exists: bool,
    error: Type[PermissionError | OSError],
    file_content: str,
    modified_properties: dict[str, str],
    expected_diff: dict[str, dict[str, str]],
) -> None:
    dummy_properties = {"key1": "value1", "key2": "value2"}
    dummy_properties_modified = modified_properties
    input_manager = InputManager()

    properties_file_path = Path("/fake/dir/original_properties.json")
    comparison_properties_file_path = Path("/fake/dir/comparison_properties.json")
    output_path = Path("path/to/output")

    if file_exists:
        mock_file = mock_open(read_data=file_content)
        mocker.patch("builtins.open", mock_file)
    else:
        mocker.patch("builtins.open", side_effect=error)

    mocker.patch.object(
        input_manager,
        "_load_metadata",
        side_effect=lambda file: setattr(
            input_manager,
            "meta_data",
            dummy_properties_modified if file == comparison_properties_file_path else dummy_properties,
        ),
    )

    mocker.patch("deepdiff.DeepDiff", return_value=expected_diff)

    mock_add_log = mocker.patch("RUFAS.output_manager.OutputManager.add_log")
    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")

    if file_exists:
        input_manager.compare_metadata_properties(properties_file_path, comparison_properties_file_path, output_path)
        mock_file.assert_called()
        mock_add_log.assert_called()
        mock_add_error.assert_not_called()
    else:
        with pytest.raises(error):
            input_manager.compare_metadata_properties(
                properties_file_path, comparison_properties_file_path, output_path
            )
        mock_add_log.assert_called()
        mock_add_error.assert_called()


@pytest.mark.parametrize(
    "metadata, limit, expected_depth, expected_path, should_raise, expected_errors, expected_err_msg",
    [
        ({"properties": {"a": {"type": "number"}}}, 2, 1, ["a"], False, [], ""),
        ({"properties": {"a": {"b": {"type": "array", "properties": {}}}}}, 3, 3, ["a", "b", "properties"], False, [],
         ""),
        (
            {"properties": {"a": {"b": {"c": {"type": "bool"}}}}},
            2,
            3,
            ["a", "b", "c"],
            True,
            ["Max metadata depth exceeded."],
            "Metadata depth exceeds maximum allowed depth of 2 at path ['a', 'b', 'c']",
        ),
        ({"properties": {"a": {"b": {"c": {"type": "string"}}}}}, 3, 3, ["a", "b", "c"], False, [], ""),
        (
            {"properties": {"a": {"b": {"type": "invalid_type"}}}},
            3,
            2,
            ["a", "b"],
            True,
            ["Properties value type error"],
            "Properties 'type' value not in ['number', 'array', 'bool', 'string', 'object']",
        ),
        ({"properties": {"a": {"b": {"c": {"type": "object"}}}}}, 3, 3, ["a", "b", "c"], False, [], ""),
    ],
)
def test_validate_properties(
    mocker: MockerFixture,
    metadata: Dict[str, Any],
    limit: int,
    expected_depth: int,
    expected_path: List[str],
    should_raise: bool,
    expected_errors: List[str],
    expected_err_msg: str,
) -> None:
    """Tests _validate_properties() function in InputManager."""
    input_manager = InputManager()
    input_manager.meta_data = metadata
    input_manager.metadata_depth_limit = limit

    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")
    mock_add_log = mocker.patch("RUFAS.output_manager.OutputManager.add_log")

    if should_raise:
        with pytest.raises(ValueError) as exc_info:
            input_manager._validate_properties()
        assert str(exc_info.value) == expected_err_msg
        assert mock_add_error.call_count == len(expected_errors)
        for error_msg in expected_errors:
            mock_add_error.assert_any_call(error_msg, mocker.ANY, mocker.ANY)
        mock_add_log.assert_not_called()
    else:
        input_manager._validate_properties()
        mock_add_log.assert_called()
        mock_add_error.assert_not_called()
        assert mock_add_log.call_args_list == [
            call(
                "Metadata properties depth",
                f"Max depth of metadata properties is {expected_depth}",
                {"class": "InputManager", "function": "_validate_properties"},
            ),
            call(
                "Metadata properties path",
                f"Deepest path of metadata properties is {expected_path}",
                {"class": "InputManager", "function": "_validate_properties"},
            ),
        ]


@pytest.mark.parametrize(
    "key_path,value,error_title,error_msg,should_raise",
    [
        (
            ["some_key"],
            {"default": "not_a_number", "minimum": 3, "maximum": 7},
            "Invalid metadata default number value.",
            "Invalid 'default' for '['some_key']': Expected a number but got <class 'str'>",
            True,
        ),
        (
            ["some_key"],
            {"default": 5, "minimum": "not_a_number", "maximum": 7},
            "Invalid metadata default minimum.",
            "Invalid 'minimum' for '['some_key']': Expected a number but got <class 'str'>",
            True,
        ),
        (
            ["some_key"],
            {"default": 5, "minimum": 3, "maximum": "not_a_number"},
            "Invalid metadata default maximum.",
            "Invalid 'maximum' for '['some_key']': Expected a number but got <class 'str'>",
            True,
        ),
        (
            ["some_key"],
            {"default": 2, "minimum": 3, "maximum": 7},
            "Invalid metadata default.",
            "Invalid 'default' for '['some_key']': 'default' 2 is less than 'minimum' 3",
            True,
        ),
        (
            ["some_key"],
            {"default": 8, "minimum": 3, "maximum": 7},
            "Invalid metadata default.",
            "Invalid 'default' for '['some_key']': 'default' 8 is greater than 'maximum' 7",
            True,
        ),
        (
            ["some_key"],
            {"minimum": 5, "maximum": 3},
            "Invalid metadata array length range.",
            "Invalid 'range' for key '['some_key']': 'minimum' value 5 is greater than 'maximum' value 3",
            True,
        ),
        (["some_key"], {"default": 5, "minimum": 3, "maximum": 8}, "", "", False),
    ],
)
def test_metadata_number_validator(
    mocker: MockerFixture,
    key_path: List[str],
    value: Dict[str, Any],
    error_title: str,
    error_msg: str,
    should_raise: bool,
):
    """Tests metadata_number_validator() method in InputManager"""
    input_manager = InputManager()
    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")
    mock_validate_properties_keys = mocker.patch("RUFAS.input_manager.InputManager._validate_metadata_properties_keys")
    info_map = {"class": "InputManager", "function": "_metadata_number_validator"}
    if should_raise:
        with pytest.raises(ValueError):
            input_manager._metadata_number_validator(key_path, value)
        assert mock_add_error.called
        assert mock_add_error.call_args[0] == (error_title, error_msg, info_map)
        mock_validate_properties_keys.assert_called_once()
    else:
        input_manager._metadata_number_validator(key_path, value)
        assert mock_add_error.assert_not_called
        mock_validate_properties_keys.assert_called_once()


@pytest.mark.parametrize(
    "key_path,value,error_title,error_msg,should_raise",
    [
        (
            ["some_key"],
            {"default": 123, "pattern": None},
            "Invalid metadata default string value.",
            "Invalid 'default' for '['some_key']': Expected a string but got <class 'int'>",
            True,
        ),
        (
            ["some_key"],
            {"default": "abcdef", "pattern": r"^[0-9]+$"},
            "Invalid metadata default string value.",
            "Invalid 'default' for '['some_key']': 'default' value 'abcdef' does not match pattern ^[0-9]+$",
            True,
        ),
        (["some_key"], {"default": "12345", "pattern": r"^[0-9]+$"}, "", "", False),
        (["some_key"], {"default": "", "pattern": r"^[0-9]+$"}, "", "", False),
    ],
)
def test_metadata_string_validator(
    mocker: MockerFixture,
    key_path: List[str],
    value: Dict[str, Any],
    error_title: str,
    error_msg: str,
    should_raise: bool,
):
    """Tests _metadata_string_validator() method in InputManager"""
    input_manager = InputManager()
    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")
    mock_validate_properties_keys = mocker.patch("RUFAS.input_manager.InputManager._validate_metadata_properties_keys")
    info_map = {"class": "InputManager", "function": "_metadata_string_validator"}

    if should_raise:
        with pytest.raises(ValueError):
            input_manager._metadata_string_validator(key_path, value)
        assert mock_add_error.called
        assert mock_add_error.call_args[0] == (error_title, error_msg, info_map)
        mock_validate_properties_keys.assert_called_once()
    else:
        input_manager._metadata_string_validator(key_path, value)
        mock_add_error.assert_not_called
        mock_validate_properties_keys.assert_called_once()


@pytest.mark.parametrize(
    "key_path,value,error_title,error_msg,should_raise",
    [
        (
            ["some_key"],
            {"default": "not_a_bool"},
            "Invalid metadata default bool value.",
            "Invalid 'default' for '['some_key']': Expected a bool but got <class 'str'>",
            True,
        ),
        (
            ["some_key"],
            {"default": 1},
            "Invalid metadata default bool value.",
            "Invalid 'default' for '['some_key']': Expected a bool but got <class 'int'>",
            True,
        ),
        (["some_key"], {"default": True}, "", "", False),
        (["some_key"], {"default": None}, "", "", False),
    ],
)
def test_metadata_bool_validator(
    mocker: MockerFixture,
    key_path: List[str],
    value: Dict[str, Any],
    error_title: str,
    error_msg: str,
    should_raise: bool,
):
    """Tests _metadata_bool_validator() method in InputManager"""
    input_manager = InputManager()
    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")
    mock_validate_properties_keys = mocker.patch("RUFAS.input_manager.InputManager._validate_metadata_properties_keys")
    info_map = {"class": "InputManager", "function": "_metadata_bool_validator"}

    if should_raise:
        with pytest.raises(ValueError):
            input_manager._metadata_bool_validator(key_path, value)
        assert mock_add_error.called
        assert mock_add_error.call_args[0] == (error_title, error_msg, info_map)
        mock_validate_properties_keys.assert_called_once()
    else:
        input_manager._metadata_bool_validator(key_path, value)
        mock_add_error.assert_not_called
        mock_validate_properties_keys.assert_called_once()


@pytest.mark.parametrize(
    "key_path,value,error_title,error_msg,should_raise",
    [
        (
            ["some_key"],
            {"default": "not_a_list"},
            "Invalid metadata default array value.",
            "Invalid 'default' for '['some_key']': Expected a list but got <class 'str'>",
            True,
        ),
        (
            ["some_key"],
            {"default": [1, 2, 3], "minimum_length": "not_a_number"},
            "Invalid metadata default array minimum length.",
            "Invalid 'minimum_length' for '['some_key']': Expected a number but got <class 'str'>",
            True,
        ),
        (
            ["some_key"],
            {"default": [1, 2, 3], "maximum_length": "not_a_number"},
            "Invalid metadata default array maximum length.",
            "Invalid 'maximum_length' for '['some_key']': Expected a number but got <class 'str'>",
            True,
        ),
        (
            ["some_key"],
            {"default": [1, 2], "minimum_length": 3},
            "Invalid metadata default array length.",
            "Invalid 'default' for '['some_key']': 'default' length of [1, 2] is less than 'minimum_length' length 3",
            True,
        ),
        (
            ["some_key"],
            {"default": [1, 2, 3, 4], "maximum_length": 3},
            "Invalid metadata default array length.",
            "Invalid 'default' for '['some_key']': 'default' length of [1, 2, 3, 4] is greater than 'maximum' length 3",
            True,
        ),
        (
            ["some_key"],
            {"minimum_length": 5, "maximum_length": 3},
            "Invalid metadata array length range.",
            "Invalid length 'range' for key '['some_key']': 'minimum_length'"
            " value 5 is greater than 'maximum_length' value 3",
            True,
        ),
        (["some_key"], {"default": [1, 2, 3], "minimum_length": 1, "maximum_length": 5}, "", "", False),
        (["some_key"], {"default": None, "minimum_length": 1, "maximum_length": 5}, "", "", False),
    ],
)
def test_metadata_array_validator(
    mocker: MockerFixture,
    key_path: List[str],
    value: Dict[str, Any],
    error_title: str,
    error_msg: str,
    should_raise: bool,
):
    """Tests _metadata_array_validator() method in InputManager"""
    input_manager = InputManager()
    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")
    mock_validate_properties_keys = mocker.patch("RUFAS.input_manager.InputManager._validate_metadata_properties_keys")
    info_map = {"class": "InputManager", "function": "_metadata_array_validator"}

    if should_raise:
        with pytest.raises(ValueError):
            input_manager._metadata_array_validator(key_path, value)
        assert mock_add_error.called
        assert mock_add_error.call_args[0] == (error_title, error_msg, info_map)
        mock_validate_properties_keys.assert_called_once()
    else:
        input_manager._metadata_array_validator(key_path, value)
        mock_add_error.assert_not_called
        mock_validate_properties_keys.assert_called_once()


def test_metadata_object_validator(
    mocker: MockerFixture,
):
    """Tests _metadata_object_validator() method in InputManager"""
    input_manager = InputManager()
    mock_validate_properties_keys = mocker.patch("RUFAS.input_manager.InputManager._validate_metadata_properties_keys")
    key_path = ["path", "cow"]
    value = {"type": "object", "description": "cow", "cow": {"data_about_cow": 17}}
    input_manager._metadata_object_validator(key_path, value)
    mock_validate_properties_keys.assert_called_once()


@pytest.mark.parametrize(
    "required_keys, valid_keys, properties, path, should_raise, expected_message",
    [
        ({"id", "type"}, {"id", "name", "type"}, {"type": "num", "id": 123, "name": "example"}, ["root"], False, ""),
        (
            {"type"},
            {"type"},
            {"type": "num", "id": 123},
            ["root"],
            True,
            "Invalid keys ['id'] in num for ['root']. Valid keys are ['type'].",
        ),
        (
            {"id"},
            set(),
            {"type": "num", "name": "example"},
            ["root"],
            True,
            "Missing required keys ['id'] for ['root']. Required keys are ['id'].",
        ),
        (
            {"id", "type"},
            {"id", "type"},
            {"type": "num", "id": 123, "extra": "data"},
            ["root", "child"],
            True,
            "Invalid keys ['extra'] in num for ['root', 'child']. Valid keys are ['id', 'type'].",
        ),
        (
            {"id", "type"},
            {"id", "type"},
            {"name": "example"},
            ["root"],
            True,
            "Missing required keys ['id', 'type'] for ['root']. Required keys are ['id', 'type'].",
        ),
    ],
)
def test_validate_metadata_properties_keys(
    mocker: MockerFixture,
    required_keys: Set[str],
    valid_keys: Set[str],
    properties: Dict[str, Any],
    path: List[str],
    should_raise: bool,
    expected_message: str,
):
    input_manager = InputManager()
    mock_add_error = mocker.patch("RUFAS.output_manager.OutputManager.add_error")

    if should_raise:
        with pytest.raises(ValueError):
            input_manager._validate_metadata_properties_keys(required_keys, valid_keys, properties, path)
        mock_add_error.assert_called_once_with(
            "Metadata Validation",
            expected_message,
            {
                "class": "InputManager",
                "function": "_validate_metadata_properties_keys",
            },
        )
    else:
        input_manager._validate_metadata_properties_keys(required_keys, valid_keys, properties, path)
        mock_add_error.assert_not_called()


def test_increment_in_elements_counter() -> None:
    """
    Unit test for the increment() method of the ElementsCounter class.
    """

    # Arrange
    counter = ElementsCounter()

    # Act
    counter.increment(ElementState.VALID)
    counter.increment(ElementState.INVALID)
    counter.increment(ElementState.FIXED)

    # Assert
    assert counter.valid_elements == 1
    assert counter.invalid_elements == 1
    assert counter.fixed_elements == 1
    assert counter.total_elements() == 3


def test_update_increments_correctly() -> None:
    """
    Unit test for the update() method of the ElementsCounter class.
    """

    # Arrange
    counter = ElementsCounter()

    # Act
    counter.update(ElementState.INVALID, 2)
    counter.update(ElementState.VALID, 1)
    counter.update(ElementState.FIXED, 3)

    # Assert
    assert counter.valid_elements == 1
    assert counter.invalid_elements == 2
    assert counter.fixed_elements == 3


def test_update_value_error() -> None:
    """
    Unit test for the update() method of the ElementsCounter class.
    """

    # Arrange
    counter = ElementsCounter()

    # Act
    with pytest.raises(ValueError):
        counter.update("not valid", 2)


def test_reset_method_in_elements_counter() -> None:
    """
    Unit test for the reset() method of the ElementsCounter class.
    """

    # Arrange
    counter = ElementsCounter()
    counter.increment(ElementState.VALID)
    counter.increment(ElementState.INVALID)
    counter.increment(ElementState.FIXED)

    # Assert Before
    assert counter.valid_elements == 1
    assert counter.invalid_elements == 1
    assert counter.fixed_elements == 1

    # Act
    counter.reset()

    # Assert After
    assert counter.valid_elements == 0
    assert counter.invalid_elements == 0
    assert counter.fixed_elements == 0


def test_total_elements_in_elements_counter() -> None:
    """
    Unit test for the total_elements() method of the ElementsCounter class.
    """

    # Arrange
    counter = ElementsCounter()
    counter.increment(ElementState.VALID)
    counter.increment(ElementState.INVALID)
    counter.increment(ElementState.FIXED)
    counter.increment(ElementState.VALID)
    expected_total = 2 + 1 + 1  # 2 valid, 1 invalid, 1 fixed

    # Act
    actual_total = counter.total_elements()

    # Assert
    assert actual_total == expected_total


def test_str_in_elements_counter() -> None:
    """
    Unit test for the __str__ method of the ElementsCounter class.
    """

    # Arrange
    counter = ElementsCounter()
    counter.valid_elements = 2
    counter.invalid_elements = 1
    counter.fixed_elements = 1
    expected_str = "{'valid_elements': 2, 'invalid_elements': 1, 'fixed_elements': 1, 'total_elements': 4}"

    # Act and Assert
    assert str(counter) == expected_str


def test_add_in_elements_counter() -> None:
    """
    Unit test for the __add__ method of the ElementsCounter class.
    """

    # Arrange
    counter1 = ElementsCounter()
    counter1.valid_elements = 2
    counter1.invalid_elements = 1
    counter1.fixed_elements = 0

    counter2 = ElementsCounter()
    counter2.valid_elements = 1
    counter2.invalid_elements = 1
    counter2.fixed_elements = 2

    # Act
    result_counter = counter1 + counter2

    # Assert result counter values
    assert result_counter.valid_elements == 3
    assert result_counter.invalid_elements == 2
    assert result_counter.fixed_elements == 2
    assert result_counter.total_elements() == 7

    # Assert original counter values
    assert counter1.valid_elements == 2
    assert counter1.invalid_elements == 1
    assert counter1.fixed_elements == 0

    assert counter2.valid_elements == 1
    assert counter2.invalid_elements == 1
    assert counter2.fixed_elements == 2


def test_extract_input_data_by_key_list_no_error(mock_input_manager: InputManager, mocker: MockerFixture) -> None:
    dummy_input_data: Dict[str, Any] = {"a": 1, "b": 2}
    dummy_var_path: list[str | int] = ["dummy_var_path"]
    dummy_var_properties: Dict[str, Any] = {"pattern": r"cow", "minimum_length": 1, "maximum_length": 5}
    dummy_value = 1
    patch_extract = mocker.patch.object(mock_input_manager, "_extract_value_by_key_list", return_value=dummy_value)
    patch_log_missing_data = mocker.patch.object(mock_input_manager, "_log_missing_data")

    result = mock_input_manager._extract_input_data_by_key_list(
        input_data=dummy_input_data,
        variable_path=dummy_var_path,
        variable_properties=dummy_var_properties,
        called_during_initialization=True,
    )

    assert result == dummy_value
    patch_log_missing_data.assert_not_called()

    result = mock_input_manager._extract_input_data_by_key_list(
        input_data=dummy_input_data,
        variable_path=dummy_var_path,
        variable_properties=dummy_var_properties,
        called_during_initialization=False,
    )

    assert result == dummy_value
    patch_extract.assert_has_calls([call(dummy_input_data, dummy_var_path), call(dummy_input_data, dummy_var_path)])
    patch_log_missing_data.assert_not_called()


@pytest.mark.parametrize(
    "var_path, var_name, called_during_initialization",
    [
        (["a", "b", "c"], "c", True),
        (["a", "b", 1], "b", True),
        (["a", 2, 0], "a", True),
        (["a", 0, "c"], "c", True),
        (["a", 0, "c", 2], "c", True),
        (["a", "b", "c"], "c", False),
        (["a", "b", 1], "b", False),
        (["a", 2, 0], "a", False),
        (["a", 0, "c"], "c", False),
        (["a", 0, "c", 2], "c", False),
    ],
)
def test_extract_input_data_by_key_list_key_error(
    var_path: List[str | int],
    var_name: str,
    called_during_initialization: bool,
    mock_input_manager: InputManager,
    mocker: MockerFixture,
) -> None:
    dummy_input_data: Dict[str, Any] = {"a": 1, "b": 2}
    dummy_var_properties: Dict[str, Any] = {"pattern": r"cow", "minimum_length": 1, "maximum_length": 5}
    patch_extract = mocker.patch.object(mock_input_manager, "_extract_value_by_key_list", side_effect=KeyError)
    patch_log_missing_data = mocker.patch.object(mock_input_manager, "_log_missing_data")

    result = mock_input_manager._extract_input_data_by_key_list(
        input_data=dummy_input_data,
        variable_path=var_path,
        variable_properties=dummy_var_properties,
        called_during_initialization=called_during_initialization,
    )

    assert result is None
    patch_extract.assert_called_once_with(dummy_input_data, var_path)
    patch_log_missing_data.assert_called_once_with(
        variable_properties=dummy_var_properties,
        var_name=var_name,
        called_during_initialization=called_during_initialization,
    )
