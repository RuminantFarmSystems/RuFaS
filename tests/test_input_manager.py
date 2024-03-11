import json
from functools import reduce
from pathlib import Path
from typing import Any, Callable, Dict, List, Type, Union, Optional
from typing import Tuple

import pandas as pd
import pytest
from mock import MagicMock, Mock, mock_open, patch
from pytest_mock import MockerFixture

from RUFAS.input_manager import InputManager, ElementsCounter, ElementState


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
        "_dict_type_validator": mock_input_manager._dict_type_validator,
        "_array_type_validator": mock_input_manager._array_type_validator,
        "_num_type_validator": mock_input_manager._num_type_validator,
        "_string_type_validator": mock_input_manager._string_type_validator,
        "_bool_type_validator": mock_input_manager._bool_type_validator,
        "_fix_data": mock_input_manager._fix_data,
        "get_data": mock_input_manager.get_data,
        "get_metadata": mock_input_manager.get_metadata,
        "get_data_keys_by_properties": mock_input_manager.get_data_keys_by_properties,
        "flush_pool": mock_input_manager.flush_pool,
        "_metadata_properties_exist": mock_input_manager._metadata_properties_exist,
        "_add_variable_to_pool": mock_input_manager._add_variable_to_pool,
        "add_dict_variable_to_pool": mock_input_manager.add_dict_variable_to_pool,
        "add_tabular_variable_to_pool": mock_input_manager.add_tabular_variable_to_pool,
        "_load_properties": mock_input_manager._load_properties,
    }


def test_load_properties_success(mock_input_manager: InputManager, mocker: MockerFixture) -> None:
    """Unit test for successfully loading properties in _load_properties method."""
    mocker.patch("os.path.exists", return_value=True)
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
    mocker.patch("builtins.open", mock_open(read_data="invalid_json"))

    mock_input_manager._InputManager__metadata = {"files": {"properties": {"path": "path/to/invalid_json.json"}}}

    with patch("RUFAS.output_manager.OutputManager.add_error") as add_error:
        with pytest.raises(json.JSONDecodeError):
            mock_input_manager._load_properties()
        assert add_error.call_count == 1


def test_load_properties_unexpected_error(mock_input_manager: InputManager, mocker: MockerFixture) -> None:
    """Unit test for handling unexpected errors in _load_properties method."""
    mocker.patch("os.path.exists", return_value=True)
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
    input_manager_original_method_states: Dict[str, Callable],
    mocker: MockerFixture,
) -> None:
    """Unit test for function start_data_processing in file input_manager.py"""
    patch_for_load_metadata = mocker.patch.object(mock_input_manager, "_load_metadata")
    patch_for_populate_pool = mocker.patch.object(mock_input_manager, "_populate_pool", return_value=True)
    patch_for_load_properties = mocker.patch.object(mock_input_manager, "_load_properties")

    eager_termination = True
    mock_metadata_path = "mock/metadata/path"

    mock_input_manager.start_data_processing(mock_metadata_path, eager_termination)

    patch_for_load_metadata.assert_called_once_with(mock_metadata_path)
    patch_for_populate_pool.assert_called_once_with(eager_termination)
    patch_for_load_properties.assert_called_once()


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
    mock_input_manager: InputManager,
    mock_metadata: Dict[str, Dict[str, Any]],
    input_manager_original_method_states: Dict[str, Callable],
    mocker: MockerFixture,
) -> None:
    """Unit test for valid data for function _populate_pool in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata
    mock_input_manager._load_data_from_json = lambda _: {"element1": "value1", "element2": "value2"}
    mock_input_manager._load_data_from_csv = lambda _: {"element3": "value3", "element4": "value4"}
    mock_input_manager._dict_type_validator = lambda *args, **kwargs: {
        "fixed_elements": 1,
        "valid_elements": 1,
        "total_elements": 1,
        "invalid_elements": 0,
        "is_valid": True,
    }
    mock_input_manager._validate_tabular_element = lambda *args, **kwargs: {
        "fixed_elements": 1,
        "valid_elements": 1,
        "total_elements": 1,
        "invalid_elements": 0,
        "is_valid": True,
    }
    mocker.patch.object(
        mock_input_manager,
        "_add_default_values_to_missing_inputs",
        side_effect=lambda input_data, _: (input_data, None, None),
    )
    mocker.patch.object(mock_input_manager, "_log_missing_keys")

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
            result = mock_input_manager._populate_pool(eager_termination=True)

        assert result is True
        assert add_log.call_count == 4
        assert add_warning.call_count == 0
        assert "file1" in mock_input_manager._InputManager__pool
        assert "file2" in mock_input_manager._InputManager__pool

    mock_input_manager._populate_pool = input_manager_original_method_states["_populate_pool"]
    mock_input_manager._dict_type_validator = input_manager_original_method_states["_dict_type_validator"]
    mock_input_manager._validate_tabular_element = input_manager_original_method_states["_validate_tabular_element"]


def test_populate_pool_invalid(
    mock_input_manager: InputManager,
    mock_metadata: Dict[str, Dict[str, Any]],
    input_manager_original_method_states: Dict[str, Callable],
    mocker: MockerFixture,
) -> None:
    """Unit test for invalid data for function _populate_pool in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata

    mock_input_manager._load_data_from_json = lambda _: {"element1": "value1", "element2": "value2"}
    mock_input_manager._load_data_from_csv = lambda _: {"element3": "value3", "element4": "value4"}
    mock_input_manager._dict_type_validator = lambda *args, **kwargs: {
        "fixed_elements": 1,
        "valid_elements": 1,
        "total_elements": 1,
        "invalid_elements": 1,
        "is_valid": False,
    }
    mock_input_manager._validate_tabular_element = lambda *args, **kwargs: {
        "fixed_elements": 1,
        "valid_elements": 1,
        "total_elements": 1,
        "invalid_elements": 1,
        "is_valid": False,
    }
    mocker.patch.object(
        mock_input_manager,
        "_add_default_values_to_missing_inputs",
        side_effect=lambda input_data, _: (input_data, None, None),
    )
    mocker.patch.object(mock_input_manager, "_log_missing_keys")

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
            result = mock_input_manager._populate_pool(eager_termination=False)

        assert result is False
        assert add_log.call_count == 4
        assert add_warning.call_count == 0
        assert "file1" not in mock_input_manager._InputManager__pool
        assert "file2" not in mock_input_manager._InputManager__pool

    mock_input_manager._populate_pool = input_manager_original_method_states["_populate_pool"]
    mock_input_manager._dict_type_validator = input_manager_original_method_states["_dict_type_validator"]
    mock_input_manager._validate_tabular_element = input_manager_original_method_states["_validate_tabular_element"]


#
#
def test_populate_pool_partial_invalid(
    mock_input_manager: InputManager,
    mock_metadata: Dict[str, Dict[str, Any]],
    input_manager_original_method_states: Dict[str, Callable],
    mocker: MockerFixture,
):
    """Unit test for invalid data for function _populate_pool in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata

    mock_input_manager._load_data_from_json = lambda _: {"element1": "value1", "element2": "value2"}
    mock_input_manager._load_data_from_csv = lambda _: {"element3": "value3", "element4": "value4"}
    mock_input_manager._dict_type_validator = MagicMock(
        side_effect=[
            {"fixed_elements": 1, "valid_elements": 1, "total_elements": 1, "invalid_elements": 0, "is_valid": True},
            {"fixed_elements": 0, "valid_elements": 0, "total_elements": 1, "invalid_elements": 1, "is_valid": False},
        ]
    )
    mock_input_manager._validate_tabular_element = MagicMock(
        side_effect=[
            {"fixed_elements": 1, "valid_elements": 1, "total_elements": 1, "invalid_elements": 0, "is_valid": True},
            {"fixed_elements": 0, "valid_elements": 0, "total_elements": 1, "invalid_elements": 1, "is_valid": False},
        ]
    )
    mocker.patch.object(
        mock_input_manager,
        "_add_default_values_to_missing_inputs",
        side_effect=lambda input_data, _: (input_data, None, None),
    )
    mocker.patch.object(mock_input_manager, "_log_missing_keys")

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
            result = mock_input_manager._populate_pool(eager_termination=False)

        assert result is False
        assert add_log.call_count == 4
        assert add_warning.call_count == 0
        assert "file1" in mock_input_manager._InputManager__pool
        assert "file2" in mock_input_manager._InputManager__pool
        assert "element1" in mock_input_manager._InputManager__pool["file1"]
        assert "element2" not in mock_input_manager._InputManager__pool["file1"]
        assert "element3" in mock_input_manager._InputManager__pool["file2"]
        assert "element4" not in mock_input_manager._InputManager__pool["file2"]

    mock_input_manager._populate_pool = input_manager_original_method_states["_populate_pool"]
    mock_input_manager._dict_type_validator = input_manager_original_method_states["_dict_type_validator"]
    mock_input_manager._validate_tabular_element = input_manager_original_method_states["_validate_tabular_element"]


def test_populate_pool_eager_termination(
    mock_input_manager: InputManager,
    mock_metadata: Dict[str, Dict[str, Any]],
    input_manager_original_method_states: Dict[str, Callable],
    mocker: MockerFixture,
) -> None:
    """Unit test for invalid data with eager termination for function
    _populate_pool in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata

    mock_input_manager._load_data_from_json = lambda _: {"element1": "value1", "element2": "value2"}
    mock_input_manager._load_data_from_csv = lambda _: {"element3": "value3", "element4": "value4"}
    mock_input_manager._dict_type_validator = lambda *args, **kwargs: {
        "fixed_elements": 1,
        "valid_elements": 1,
        "total_elements": 1,
        "invalid_elements": 0,
        "is_valid": False,
    }
    mocker.patch.object(
        mock_input_manager,
        "_add_default_values_to_missing_inputs",
        side_effect=lambda input_data, _: (input_data, None, None),
    )
    mocker.patch.object(mock_input_manager, "_log_missing_keys")

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
            result = mock_input_manager._populate_pool(eager_termination=True)
            assert result is False
            assert add_log.call_count == 0
            assert add_warning.call_count == 0
            assert "file1" not in mock_input_manager._InputManager__pool
            assert "file2" not in mock_input_manager._InputManager__pool

    mock_input_manager._populate_pool = input_manager_original_method_states["_populate_pool"]
    mock_input_manager._dict_type_validator = input_manager_original_method_states["_dict_type_validator"]


def test_populate_pool_raises_keyerror(
    mock_input_manager: InputManager,
    input_manager_original_method_states: Dict[str, Callable],
) -> None:
    """Unit test for invalid data file type for function _populate_pool in file input_manager.py"""
    mock_input_manager._InputManager__metadata = {
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
    mock_input_manager._dict_type_validator = input_manager_original_method_states["_dict_type_validator"]


@pytest.fixture
def mock_metadata_for_validate_element(
    mocker: MockerFixture,
) -> Dict[str, Dict[str, Any]]:
    return {
        "files": {
            "file1": {
                "type": "json",
                "path": "/path/to/file1.json",
                "properties": "property_map_key1",
            }
        },
        "properties": {
            "property_map_key1": {
                "element1": {"type": "string", "pattern": r"^\d{3}-\d{2}-\d{4}$"},
                "element2": {"type": "number", "minimum": 0, "maximum": 150},
                "element3": {
                    "type": "array",
                    "minimum_length": 1,
                    "maximum_length": 5,
                    "properties": {"type": "number"},
                },
                "element4": {
                    "type": "object",
                    "description": "dummy_description",
                    "nested_element1": {
                        "type": "string",
                        "minimum_length": 1,
                        "maximum_length": 20,
                    },
                    "nested_element2": {"type": "number", "minimum": 0, "maximum": 250},
                },
                "element5": {
                    "type": "object",
                    "description": "dummy_description",
                    "nested_element1": {
                        "type": "string",
                        "minimum_length": 1,
                        "maximum_length": 20,
                    },
                    "nested_element2": {"type": "number", "minimum": 0, "maximum": 250},
                    "nested_element3": {
                        "type": "object",
                        "description": "dummy_description",
                        "nested_sub_element1": {
                            "type": "string",
                            "minimum_length": 1,
                            "maximum_length": 5,
                        },
                        "nested_sub_element2": {
                            "type": "array",
                            "minimum_length": 1,
                            "maximum_length": 5,
                            "properties": {"type": "number"},
                        },
                    },
                },
                "element6": {"type": "bool"},
                "element7": {"type": "number", "maximum": 10, "default": 5},
                "element8": {
                    "type": "object",
                    "nested_element": {"type": "number", "maximum": 10},
                },
            }
        },
    }


# def test_validate_element_fixable_data(
#     mock_input_manager: InputManager,
#     mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
#     input_manager_original_method_states: Dict[str, Callable],
# ) -> None:
#     """Unit test for a fixable number type input_data for _dict_type_validator in file input_manager.py"""
#     mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element
#     mock_input_manager._num_type_validator = MagicMock(return_value=False)
#     mock_input_manager._fix_data = MagicMock(return_value=True)
#     mock_element_counter_and_validity = {
#         "fixed_elements": 0,
#         "total_elements": 0,
#         "valid_elements": 0,
#         "invalid_elements": 0,
#         "is_valid": True,
#     }
#
#     input_data = {"element2": 123}
#     result = mock_input_manager._dict_type_validator(
#         ["element2"],
#         "property_map_key1",
#         input_data,
#         True,
#         mock_element_counter_and_validity,
#     )
#
#     assert result["is_valid"] is True
#     assert result["fixed_elements"] == 1
#     assert result["total_elements"] == 1
#     assert result["invalid_elements"] == 0
#     assert result["valid_elements"] == 0
#
#     mock_input_manager._dict_type_validator = input_manager_original_method_states["_dict_type_validator"]
#     mock_input_manager._num_type_validator = input_manager_original_method_states["_num_type_validator"]
#     mock_input_manager._fix_data = input_manager_original_method_states["_fix_data"]
#
#
@pytest.mark.parametrize(
    "prop, input_data, total_elements, valid_elements, invalid_elements, fixed_elements",
    [
        (
            "element1",
            {"element1": ["123-45-6789", "000-11-6123", "555-55-5555"]},
            3,
            3,
            0,
            0,
        ),
        ("element2", {"element2": [6, 149, 55, 22]}, 4, 4, 0, 0),
        ("element6", {"element6": [True, False, True]}, 3, 3, 0, 0),
    ],
)
def test_validate_tabular_element_valid_data(
    mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
    prop: str,
    input_data: Dict[str, Any],
    total_elements: int,
    valid_elements: int,
    invalid_elements: int,
    fixed_elements: int,
    mocker: MockerFixture,
) -> None:
    """Unit test for _validate_tabular_element function in file input_manager.py"""

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata_for_validate_element)
    dummy_property = prop
    properties_blob_key = "property_map_key1"
    dummy_input_data = input_data
    eager_termination = True
    elements_counter = ElementsCounter()

    # Act
    result = input_manager._validate_tabular_element(
        dummy_property, properties_blob_key, dummy_input_data, eager_termination, elements_counter
    )

    # Assert
    assert result
    assert elements_counter.total_elements() == total_elements
    assert elements_counter.valid_elements == valid_elements
    assert elements_counter.invalid_elements == invalid_elements
    assert elements_counter.fixed_elements == fixed_elements


@pytest.mark.parametrize(
    "prop, input_data, total_elements, valid_elements, invalid_elements, fixed_elements, is_valid,"
    " eager_termination",
    [
        (
            "element1",
            {"element1": ["invalid1", "invalid2", "invalid3"]},
            3,
            0,
            3,
            0,
            False,
            False,
        ),
        ("element2", {"element2": [-6, 1149, 955, -22]}, 1, 0, 1, 0, False, True),
        ("element7", {"element7": [50]}, 1, 0, 0, 1, True, False),
    ],
)
def test_validate_csv_element_invalid_data(
    mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
    prop: str,
    input_data: Dict[str, Any],
    total_elements: int,
    is_valid: bool,
    valid_elements: int,
    invalid_elements: int,
    fixed_elements: int,
    eager_termination: bool,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for _validate_tabular_element function in file input_manager.py with invalid data
    """

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata_for_validate_element)
    mocker.patch.object(input_manager, "_fix_data", return_value=is_valid)
    properties_blob_key = "property_map_key1"
    elements_counter = ElementsCounter()

    # Act
    result = input_manager._validate_tabular_element(
        prop,
        properties_blob_key,
        input_data,
        eager_termination,
        elements_counter,
    )

    # Assert
    assert result == is_valid
    assert elements_counter.total_elements() == total_elements
    assert elements_counter.valid_elements == valid_elements
    assert elements_counter.invalid_elements == invalid_elements
    assert elements_counter.fixed_elements == fixed_elements


def test_dict_type_validator_string_type(
    mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """
    Unit test for string type input_data for _dict_type_validator in file input_manager.py
    """

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata_for_validate_element)
    elements_counter = ElementsCounter()
    input_data: Dict[str, Any] = {"element1": "123-45-6789"}

    # Act
    result = input_manager._dict_type_validator(
        "element1",
        "property_map_key1",
        input_data,
        True,
        elements_counter,
    )

    # Assert
    assert result
    assert elements_counter.fixed_elements == 0
    assert elements_counter.total_elements() == 1
    assert elements_counter.valid_elements == 1
    assert elements_counter.invalid_elements == 0

    # Arrange
    input_data = {"element1": "invalid_value"}
    elements_counter.reset()

    # Act
    result = input_manager._dict_type_validator(
        "element1",
        "property_map_key1",
        input_data,
        True,
        elements_counter,
    )

    # Assert
    assert not result
    assert elements_counter.fixed_elements == 0
    assert elements_counter.total_elements() == 1
    assert elements_counter.valid_elements == 0
    assert elements_counter.invalid_elements == 1

    # Arrange
    input_data = {"element8": {"nested_element": 750}}
    elements_counter.reset()
    patch_for_add_warning = mocker.patch("RUFAS.input_manager.om.add_warning")

    # Act
    result = input_manager._dict_type_validator(
        "element8",
        "property_map_key1",
        input_data,
        False,
        elements_counter,
    )

    # Assert
    assert patch_for_add_warning.call_count == 1
    assert not result
    assert elements_counter.fixed_elements == 0
    assert elements_counter.total_elements() == 1
    assert elements_counter.valid_elements == 0
    assert elements_counter.invalid_elements == 1


def test_dict_type_validator_number_type(
    mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """
    Unit test for number type input_data for _dict_type_validator in file input_manager.py
    """

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata_for_validate_element)
    elements_counter = ElementsCounter()
    input_data: Dict[str, Any] = {"element2": 123}

    # Act
    result = input_manager._dict_type_validator(
        "element2",
        "property_map_key1",
        input_data,
        True,
        elements_counter,
    )

    # Assert
    assert result
    assert elements_counter.fixed_elements == 0
    assert elements_counter.total_elements() == 1
    assert elements_counter.valid_elements == 1
    assert elements_counter.invalid_elements == 0

    # Arrange
    input_data = {"element2": 500}
    elements_counter.reset()

    # Act
    result = input_manager._dict_type_validator(
        "element2",
        "property_map_key1",
        input_data,
        True,
        elements_counter,
    )

    # Assert
    assert not result
    assert elements_counter.fixed_elements == 0
    assert elements_counter.total_elements() == 1
    assert elements_counter.valid_elements == 0
    assert elements_counter.invalid_elements == 1


def test_dict_type_validator_array_type(
    mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """
    Unit test for array type input_data for _dict_type_validator in file input_manager.py
    """

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata_for_validate_element)
    elements_counter = ElementsCounter()
    input_data: Dict[str, Any] = {"element3": [1, 2, 3]}

    # Act
    result = input_manager._dict_type_validator(
        "element3",
        "property_map_key1",
        input_data,
        True,
        elements_counter,
    )

    # Assert
    assert result
    assert elements_counter.fixed_elements == 0
    assert elements_counter.total_elements() == 3
    assert elements_counter.valid_elements == 3
    assert elements_counter.invalid_elements == 0

    # Arrange
    input_data = {"element3": [1, 2, 3, 6, 7, 8, 10]}
    elements_counter.reset()

    # Act
    result = input_manager._dict_type_validator(
        "element3",
        "property_map_key1",
        input_data,
        True,
        elements_counter,
    )

    # Assert
    assert not result
    assert elements_counter.fixed_elements == 0
    assert elements_counter.total_elements() == 0
    assert elements_counter.valid_elements == 0
    assert elements_counter.invalid_elements == 0


def test_dict_type_validator_valid_object_type(
    mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """
    Unit test for valid nested object type input_data for _dict_type_validator in file input_manager.py
    """

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata_for_validate_element)
    elements_counter = ElementsCounter()
    input_data: Dict[str, Any] = {"element4": {"nested_element1": "value1", "nested_element2": 123}}

    # Act
    result = input_manager._dict_type_validator(
        "element4",
        "property_map_key1",
        input_data,
        True,
        elements_counter,
    )

    # Assert
    assert result
    assert elements_counter.fixed_elements == 0
    assert elements_counter.total_elements() == 2
    assert elements_counter.valid_elements == 2
    assert elements_counter.invalid_elements == 0


def test_dict_type_validator_invalid_object_type(
    mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """
    Unit test for nested invalid object type input_data for _dict_type_validator in file input_manager.py
    """

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata_for_validate_element)
    elements_counter = ElementsCounter()
    input_data = {"element4": {"nested_element1": "value1", "nested_element2": 500}}

    # Act
    result = input_manager._dict_type_validator(
        "element4",
        "property_map_key1",
        input_data,
        True,
        elements_counter,
    )

    # Assert
    assert not result
    assert elements_counter.fixed_elements == 0
    assert elements_counter.total_elements() == 2
    assert elements_counter.valid_elements == 1
    assert elements_counter.invalid_elements == 1

    # Arrange
    input_data = {
        "element4": {
            "nested_element1": "value123456789value123456789",
            "nested_element2": 123,
        }
    }
    elements_counter.reset()

    # Act
    result = input_manager._dict_type_validator(
        "element4",
        "property_map_key1",
        input_data,
        True,
        elements_counter,
    )

    # Assert
    assert not result
    assert elements_counter.fixed_elements == 0
    assert elements_counter.total_elements() == 1
    assert elements_counter.valid_elements == 0
    assert elements_counter.invalid_elements == 1


def test_validate_element_valid_nested_object_type(
    mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """
    Unit test for valid object nested within another object type
    input_data for _dict_type_validator in file input_manager.py
    """

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata_for_validate_element)
    elements_counter = ElementsCounter()
    input_data = {
        "element5": {
            "nested_element1": "value1",
            "nested_element2": 123,
            "nested_element3": {
                "nested_sub_element1": "cows",
                "nested_sub_element2": [1, 2, 3],
            },
        }
    }

    # Act
    result = input_manager._dict_type_validator(
        "element5",
        "property_map_key1",
        input_data,
        True,
        elements_counter,
    )

    # Assert
    assert result
    assert elements_counter.fixed_elements == 0
    assert elements_counter.total_elements() == 6
    assert elements_counter.valid_elements == 6
    assert elements_counter.invalid_elements == 0


def test_validate_element_invalid_nested_object_type(
    mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """Unit test for invalid object nested within another object type
    input_data for _dict_type_validator in file input_manager.py"""

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata_for_validate_element)
    input_data = {
        "element5": {
            "nested_element1": "value1",
            "nested_element2": 123,
            "nested_element3": {
                "nested_sub_element1": "cows",
                "nested_sub_element2": [],
            },
        }
    }
    elements_counter = ElementsCounter()

    # Act
    result = input_manager._dict_type_validator(
        "element5",
        "property_map_key1",
        input_data,
        True,
        elements_counter,
    )

    # Assert
    assert not result
    assert elements_counter.fixed_elements == 0
    assert elements_counter.total_elements() == 3
    assert elements_counter.valid_elements == 3
    assert elements_counter.invalid_elements == 0

    # Arrange
    input_data = {
        "element5": {
            "nested_element1": "value1",
            "nested_element2": 123,
            "nested_element3": {
                "nested_sub_element1": "invalid_cows",
                "nested_sub_element2": [1, 2, 3],
            },
        }
    }
    elements_counter.reset()

    # Act
    result = input_manager._dict_type_validator(
        "element5",
        "property_map_key1",
        input_data,
        True,
        elements_counter,
    )

    # Assert
    assert not result
    assert elements_counter.fixed_elements == 0
    assert elements_counter.total_elements() == 3
    assert elements_counter.valid_elements == 2
    assert elements_counter.invalid_elements == 1


@pytest.mark.parametrize(
    "input_data_value, expected_result",
    [
        (True, True),
        (False, True),
        ("hello", False),
        (2, False),
        (3.5, False),
        ({}, False),
        ([], False),
        (None, False),
    ],
)
def test_bool_type_validator(
    input_data_value: bool,
    expected_result: bool,
    mocker: MockerFixture,
) -> None:
    """
    Unit test for function _bool_type_validator in file input_manager.py
    """

    # Arrange
    input_manager = InputManager()
    variable_properties: Dict[str, Any] = {}
    var_name = "dummy_var_name"
    dummy_properties_key = "dummy_variable_properties"
    patch_for_add_warning = mocker.patch("RUFAS.input_manager.om.add_warning")

    # Act
    result = input_manager._bool_type_validator(variable_properties, var_name, input_data_value, dummy_properties_key)

    # Assert
    if not expected_result:
        patch_for_add_warning.assert_called_once()
    else:
        patch_for_add_warning.assert_not_called()
    assert result == expected_result


def test_dict_type_validator_invalid_var_name_raises_metadata_keyerror() -> None:
    """
    Unit test for keyerror raised for invalid var name for _dict_type_validator in file input_manager.py
    """

    # Arrange
    input_manager = InputManager()
    first_level_key = "valid_key"
    properties_blob_key = "dummy_properties_blob_key"
    input_data = {"valid_key": {"another_valid_key": "value"}}
    eager_termination = False
    elements_counter = ElementsCounter()

    # Act and Assert
    with pytest.raises(KeyError):
        input_manager._dict_type_validator(
            first_level_key,
            properties_blob_key,
            input_data,
            eager_termination,
            elements_counter,
        )


def test_validate_json_element_invalid_var_type_raises_keyerror(
    mocker: MockerFixture,
) -> None:
    """
    Unit test for keyerror raised for invalid var type for _dict_type_validator in file input_manager.py
    """

    # Arrange
    input_manager = InputManager()
    first_level_key = "valid_key"
    properties_blob_key = "dummy_valid_key"
    input_data = {"valid_key": "some_value"}
    mocker.patch.object(
        input_manager,
        "_InputManager__metadata",
        {"properties": {properties_blob_key: {"valid_key": {"type": "invalid_type"}}}},
    )
    eager_termination = False
    elements_counter = ElementsCounter()

    # Act and Assert
    with pytest.raises(ValueError):
        input_manager._dict_type_validator(
            first_level_key,
            properties_blob_key,
            input_data,
            eager_termination,
            elements_counter,
        )


def test_validate_json_element_missing_type_raises_keyerror(
    mocker: MockerFixture,
) -> None:
    """
    Unit test for missing data type raising a KeyError for function
    _dict_type_validator in file input_manager.py"""

    # Arrange
    input_manager = InputManager()
    first_level_key = "valid_key"
    properties_blob_key = "dummy_valid_key"
    input_data = {"valid_key": "some_value"}
    mocker.patch.object(
        input_manager, "_InputManager__metadata", {"properties": {properties_blob_key: {"valid_key": {}}}}
    )
    eager_termination = False
    elements_counter = ElementsCounter()

    # Act and Assert
    with pytest.raises(KeyError, match="Missing 'type' key"):
        input_manager._dict_type_validator(
            first_level_key,
            properties_blob_key,
            input_data,
            eager_termination,
            elements_counter,
        )


@pytest.mark.parametrize(
    "dummy_value, dummy_variable_to_check, expected_result, expected_warning_call_count",
    [
        (1, {"minimum": 3, "maximum": 7}, False, 1),
        (3, {"minimum": 3, "maximum": 7}, True, 0),
        (5, {"minimum": 3}, True, 0),
        (7, {"minimum": 3, "maximum": 7}, True, 0),
        (9, {"maximum": 7}, False, 1),
        (-1, {"minimum": 3, "maximum": 7}, False, 1),
        (None, {"maximum": 1, "minimum": 0}, False, 1),
        ("42", {"minimum": 4, "maximum": 32}, False, 1),
    ],
)
def test_num_type_validator(
    dummy_value: int,
    dummy_variable_to_check: Dict[str, int],
    expected_result: bool,
    expected_warning_call_count: int,
) -> None:
    """Unit test for function _num_type_validator in file input_manager.py"""

    # Arrange
    input_manager = InputManager()
    dummy_var_name = "dummy_num"
    dummy_properties_key = "dummy_variable_properties"

    with patch("RUFAS.input_manager.om.add_warning") as add_warning:
        result = input_manager._num_type_validator(
            dummy_variable_to_check, dummy_var_name, dummy_value, dummy_properties_key
        )

    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


@pytest.mark.parametrize(
    "dummy_value, dummy_variable_to_check, expected_result, expected_warning_call_count",
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
    ],
)
def test_string_type_validator(
    dummy_value: int,
    dummy_variable_to_check: Dict[str, int],
    expected_result: bool,
    expected_warning_call_count: int,
    mock_input_manager: InputManager,
) -> None:
    """Unit test for _string_type_validator function in file input_manager.py"""
    dummy_var_name = "dummy_var"
    dummy_properties_key = "dummy_variable_properties"

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._string_type_validator(
            dummy_variable_to_check, dummy_var_name, dummy_value, dummy_properties_key
        )

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
    dummy_variable_properties: dict[str, Any],
    dummy_element_hierarchy: list[str],
    expected_value: list,
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
    dummy_variable_properties: dict[str, Any],
    dummy_element_hierarchy: list[str],
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

    mock_input_manager._InputManager__metadata = mock_pool_for_get_metadata

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
        (
            {
                "key_1": {"properties": "value"},
                "key_2": {"properties": "value"},
                "key_3": {"properties": "value"},
            },
            [],
        ),
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
    "variable_name, data, properties_blob_key, starting_im_pool, is_dict_variable",
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
            True,
        ),
        (
            "array_of_int_data",
            {"array_of_int_data": [0, 1, 2]},
            "array_of_int_data",
            {},
            False,
        ),
        (
            "array_of_float_data",
            {"array_of_float_data": [0.0, 1.1, 2.2]},
            "array_of_float_data",
            {},
            False,
        ),
        (
            "array_of_str_data",
            {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]},
            "array_of_str_data",
            {},
            False,
        ),
        (
            "array_of_dict_data",
            {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]},
            "array_of_dict_data",
            {},
            False,
        ),
        (
            "dict_of_array_data",
            {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
            "dict_of_array_data",
            {},
            False,
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
            True,
        ),
        (
            "array_of_int_data",
            {"array_of_int_data": [0, 1, 2]},
            "array_of_int_data",
            {"array_of_int_data": [-1, 0, 1]},
            False,
        ),
        (
            "array_of_float_data",
            {"array_of_float_data": [0.0, 1.1, 2.2]},
            "array_of_float_data",
            {"array_of_float_data": [-1.0, 0.0, 1.0]},
            False,
        ),
        (
            "array_of_str_data",
            {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]},
            "array_of_str_data",
            {"array_of_str_data": ["a", "b", "c"]},
            False,
        ),
        (
            "array_of_dict_data",
            {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]},
            "array_of_dict_data",
            {"array_of_dict_data": [{"A": -1}, {"B": 0}, {"C": 1}]},
            False,
        ),
        (
            "dict_of_array_data",
            {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
            "dict_of_array_data",
            {"dict_of_array_data": {"a": [1, 2, 3]}},
            False,
        ),
    ],
)
def test_add_variable_to_pool_valid(
    variable_name: str,
    data: Any,
    properties_blob_key: str,
    starting_im_pool: Dict[str, Any],
    is_dict_variable: bool,
    mock_metadata_for_add_variable_to_pool: Dict[str, Dict[str, Any]],
    mocker: MockerFixture,
) -> None:
    """Unit test for add_variable_to_pool() method in file input_manager.py with valid data."""

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", mock_metadata_for_add_variable_to_pool)
    mocker.patch.object(input_manager, "_InputManager__pool", starting_im_pool)
    mocker.patch.object(input_manager, "_dict_type_validator", return_value=True)
    mocker.patch.object(input_manager, "_validate_tabular_element", return_value=True)
    expected_add_warning_count = 1 if starting_im_pool else 0
    patch_for_add_warning = mocker.patch("RUFAS.input_manager.om.add_warning")
    patch_for_add_error = mocker.patch("RUFAS.input_manager.om.add_error")

    # Act
    result = input_manager._add_variable_to_pool(
        variable_name=variable_name,
        data=data,
        properties_blob_key=properties_blob_key,
        eager_termination=False,
        is_variable_dict=is_dict_variable,
    )

    # Assert
    assert result
    assert patch_for_add_warning.call_count == expected_add_warning_count
    assert patch_for_add_error.call_count == 0
    assert variable_name in getattr(input_manager, "_InputManager__pool")
    assert input_manager.get_data(variable_name) == data


@pytest.mark.parametrize(
    "variable_name, data, properties_blob_key, starting_im_pool, is_dict_variable",
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
            True,
        ),
        (
            "array_of_int_data",
            {"array_of_int_data": [0, 1, 2]},
            "array_of_int_data",
            {},
            False,
        ),
        (
            "array_of_float_data",
            {"array_of_float_data": [0.0, 1.1, 2.2]},
            "array_of_float_data",
            {},
            False,
        ),
        (
            "array_of_str_data",
            {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]},
            "array_of_str_data",
            {},
            False,
        ),
        (
            "array_of_dict_data",
            {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]},
            "array_of_dict_data",
            {},
            False,
        ),
        (
            "dict_of_array_data",
            {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
            "dict_of_array_data",
            {},
            False,
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
            True,
        ),
        (
            "array_of_int_data",
            {"array_of_int_data": [0, 1, 2]},
            "array_of_int_data",
            {"array_of_int_data": [-1, 0, 1]},
            False,
        ),
        (
            "array_of_float_data",
            {"array_of_float_data": [0.0, 1.1, 2.2]},
            "array_of_float_data",
            {"array_of_float_data": [-1.0, 0.0, 1.0]},
            False,
        ),
        (
            "array_of_str_data",
            {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]},
            "array_of_str_data",
            {"array_of_str_data": ["a", "b", "c"]},
            False,
        ),
        (
            "array_of_dict_data",
            {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]},
            "array_of_dict_data",
            {"array_of_dict_data": [{"A": -1}, {"B": 0}, {"C": 1}]},
            False,
        ),
        (
            "dict_of_array_data",
            {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
            "dict_of_array_data",
            {"dict_of_array_data": {"a": [1, 2, 3]}},
            False,
        ),
    ],
)
def test_add_variable_to_pool_invalid(
    variable_name: str,
    data: Any,
    properties_blob_key: str,
    starting_im_pool: Dict[str, Any],
    is_dict_variable: bool,
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
    mocker.patch.object(input_manager, "_dict_type_validator", return_value=False)
    mocker.patch.object(input_manager, "_validate_tabular_element", return_value=False)
    patch_for_add_warning = mocker.patch("RUFAS.input_manager.om.add_warning")
    patch_for_add_error = mocker.patch("RUFAS.input_manager.om.add_error")
    mock_elements_counter = mocker.MagicMock()
    mock_elements_counter.invalid_elements = 1
    mocker.patch("RUFAS.input_manager.ElementsCounter", return_value=mock_elements_counter)

    # Act
    result = input_manager._add_variable_to_pool(
        variable_name=variable_name,
        data=data,
        properties_blob_key=properties_blob_key,
        eager_termination=False,
        is_variable_dict=is_dict_variable,
    )

    # Assert
    assert result is False
    assert patch_for_add_warning.call_count == 0
    assert patch_for_add_error.call_count == 1

    if starting_im_pool:
        assert starting_im_pool[variable_name] == input_manager.get_data(variable_name)
    else:
        assert variable_name not in getattr(input_manager, "_InputManager__pool")


@pytest.mark.parametrize(
    "variable_name, data, properties_blob_key, starting_im_pool, is_dict_variable",
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
            True,
        ),
        (
            "array_of_int_data",
            {"array_of_int_data": [0, 1, 2]},
            "array_of_int_data",
            {},
            False,
        ),
        (
            "array_of_float_data",
            {"array_of_float_data": [0.0, 1.1, 2.2]},
            "array_of_float_data",
            {},
            False,
        ),
        (
            "array_of_str_data",
            {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]},
            "array_of_str_data",
            {},
            False,
        ),
        (
            "array_of_dict_data",
            {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]},
            "array_of_dict_data",
            {},
            False,
        ),
        (
            "dict_of_array_data",
            {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
            "dict_of_array_data",
            {},
            False,
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
            True,
        ),
        (
            "array_of_int_data",
            {"array_of_int_data": [0, 1, 2]},
            "array_of_int_data",
            {"array_of_int_data": [-1, 0, 1]},
            False,
        ),
        (
            "array_of_float_data",
            {"array_of_float_data": [0.0, 1.1, 2.2]},
            "array_of_float_data",
            {"array_of_float_data": [-1.0, 0.0, 1.0]},
            False,
        ),
        (
            "array_of_str_data",
            {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]},
            "array_of_str_data",
            {"array_of_str_data": ["a", "b", "c"]},
            False,
        ),
        (
            "array_of_dict_data",
            {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]},
            "array_of_dict_data",
            {"array_of_dict_data": [{"A": -1}, {"B": 0}, {"C": 1}]},
            False,
        ),
        (
            "dict_of_array_data",
            {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
            "dict_of_array_data",
            {"dict_of_array_data": {"a": [1, 2, 3]}},
            False,
        ),
    ],
)
def test_add_variable_to_pool_eager_termination(
    variable_name: str,
    data: Any,
    properties_blob_key: str,
    starting_im_pool: Dict[str, Any],
    is_dict_variable: bool,
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
    mocker.patch.object(input_manager, "_dict_type_validator", return_value=False)
    mocker.patch.object(input_manager, "_validate_tabular_element", return_value=False)
    mock_elements_counter = mocker.MagicMock()
    mock_elements_counter.invalid_elements = 1
    mocker.patch("RUFAS.input_manager.ElementsCounter", return_value=mock_elements_counter)
    patch_for_add_warning = mocker.patch("RUFAS.input_manager.om.add_warning")
    patch_for_add_error = mocker.patch("RUFAS.input_manager.om.add_error")

    # Act
    with pytest.raises(ValueError):
        input_manager._add_variable_to_pool(
            variable_name=variable_name,
            data=data,
            properties_blob_key=properties_blob_key,
            eager_termination=True,
            is_variable_dict=is_dict_variable,
        )

    # Assert
    assert patch_for_add_warning.call_count == 0
    assert patch_for_add_error.call_count == 1
    if starting_im_pool:
        assert starting_im_pool[variable_name] == input_manager.get_data(variable_name)
    else:
        assert variable_name not in getattr(input_manager, "_InputManager__pool")


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
        data=data,
        properties_blob_key=properties_blob_key,
        eager_termination=False,
        is_variable_dict=True,
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
            data=data,
            properties_blob_key=properties_blob_key,
            eager_termination=False,
            is_variable_dict=True,
        )

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
        data=expected_data_for_add_variable_to_pool,
        properties_blob_key=properties_blob_key,
        eager_termination=False,
        is_variable_dict=False,
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
            data=expected_data_for_add_variable_to_pool,
            properties_blob_key=properties_blob_key,
            eager_termination=False,
            is_variable_dict=False,
        )

        mock_input_manager.add_tabular_variable_to_pool = input_manager_original_method_states[
            "add_tabular_variable_to_pool"
        ]
        mock_input_manager._metadata_properties_exist = input_manager_original_method_states[
            "_metadata_properties_exist"
        ]
        mock_input_manager._add_variable_to_pool = input_manager_original_method_states["_add_variable_to_pool"]


# <<<<<<< HEAD
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
    mock_input_manager: InputManager, input_manager_original_method_states: Dict[str, Callable]
) -> None:
    mock_input_manager._InputManager__get_data_logs_pool = {
        "14-Feb-2024_Wed_06-15-56.692523": "InputManager.get_data() gets called for ['a'].",
        "14-Feb-2024_Wed_06-15-56.693523": "InputManager.get_data() gets called for ['b'].",
        "14-Feb-2024_Wed_06-15-56.696526": "InputManager.get_data() gets called for ['c'].",
    }
    with patch("RUFAS.output_manager.OutputManager.generate_file_name") as mock_generate_file_name:
        with patch("RUFAS.output_manager.OutputManager.dict_to_file_json") as mock_dict_to_file_json:
            with patch("os.path.join", return_value="dummy_path"):
                mock_input_manager.dump_get_data_logs(path=MagicMock(auto_spec=Path))

    mock_generate_file_name.assert_called_once_with(base_name="InputManager_get_data_log", extension="json")
    mock_dict_to_file_json.assert_called_once_with(mock_input_manager._InputManager__get_data_logs_pool, "dummy_path")


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
            {"key1": {"type": "string"}, "key2": {"type": "integer"}},
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
    mocker.patch.object(input_manager, "_extract_value_by_key_list", return_value=patch_extract_return)
    mocker.patch.object(input_manager, "_validate_input_by_type", return_value=patch_validate_return)
    mocker.patch("RUFAS.input_manager.om.add_warning", return_value=None)
    mock_elements_counter = mocker.MagicMock()

    # Act
    result = input_manager._object_type_validator(
        variable_path, variable_properties, input_data, eager_termination, properties_blob_key, mock_elements_counter
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
            "Validation: array container length less than minimum",
        ),
        # Input list's length exceeds the specified maximum length
        (
            ["data", "array"],
            {"maximum_length": 3, "minimum_length": 1},
            [1, 2, 3, 4],
            "blob_key",
            False,
            "Validation: array container length greater than maximum",
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
):
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
):
    """
    Unit test for the _array_type_validator() method of the InputManager class.
    """

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_extract_value_by_key_list", return_value=patch_extract_return)
    mocker.patch.object(input_manager, "_validate_array_container_properties", return_value=patch_container_valid)
    mocker.patch.object(input_manager, "_validate_input_by_type", return_value=patch_element_valid)
    mock_elements_counter = mocker.MagicMock()

    # Act
    result = input_manager._array_type_validator(
        variable_path, variable_properties, input_data, eager_termination, properties_blob_key, mock_elements_counter
    )

    # Assert
    assert result == expected_result


@pytest.mark.parametrize(
    "first_level_key, properties_blob_key, input_data, eager_termination,"
    "expected_result, metadata_properties, extract_mock_return, validate_mock_return",
    [
        # Test case: valid data without eager termination
        (
            "key1",
            "blob1",
            {"key1": "valid data"},
            False,
            True,
            {"blob1": {"key1": {"type": "string"}}},
            {"type": "string"},
            True,
        ),
        # Test case: invalid data with eager termination
        (
            "key2",
            "blob2",
            {"key2": "invalid data"},
            True,
            False,
            {"blob2": {"key2": {"type": "number"}}},
            {"type": "number"},
            False,
        ),
    ],
)
def test_dict_type_validator(
    mocker: MockerFixture,
    first_level_key: str,
    properties_blob_key: str,
    input_data: Dict[str, Any],
    eager_termination: bool,
    expected_result: bool,
    metadata_properties: Dict[str, Any],
    extract_mock_return: Dict[str, Any],
    validate_mock_return: bool,
) -> None:
    """
    Unit test for the _dict_type_validator() method of the InputManager class.
    """

    # Arrange
    input_manager = InputManager()
    mocker.patch.object(input_manager, "_InputManager__metadata", {"properties": metadata_properties})
    mocker.patch.object(input_manager, "_extract_value_by_key_list", return_value=extract_mock_return)
    mocker.patch.object(input_manager, "_validate_input_by_type", return_value=validate_mock_return)
    mock_elements_counter = mocker.MagicMock()

    # Act
    result = input_manager._dict_type_validator(
        first_level_key, properties_blob_key, input_data, eager_termination, mock_elements_counter
    )

    # Assert
    assert result == expected_result


@pytest.mark.parametrize(
    "first_level_key, properties_blob_key, input_data, eager_termination,expected_result, validate_input_returns",
    [
        # Test case where all elements are valid
        (
            "column1",
            "blobKey1",
            {"column1": ["data1", "data2", "data3"]},
            False,
            True,
            [True, True, True],
        ),
        # Test case where one element is invalid, without eager termination
        (
            "column2",
            "blobKey2",
            {"column2": ["data1", "invalid", "data3"]},
            False,
            False,
            [True, False, True],
        ),
        # Test case where one element is invalid, with eager termination
        (
            "column3",
            "blobKey3",
            {"column3": ["data1", "invalid", "data3"]},
            True,
            False,
            [True, False],
        ),
    ],
)
def test_validate_tabular_element(
    mocker: MockerFixture,
    first_level_key: str,
    properties_blob_key: str,
    input_data: Dict[str, Any],
    eager_termination: bool,
    expected_result: bool,
    validate_input_returns: List[bool],
):
    """
    Unit test for the _validate_tabular_element method.
    """
    # Arrange
    input_manager = InputManager()
    elements_counter = mocker.MagicMock()
    mocker.patch.object(input_manager, "_extract_value_by_key_list", return_value={"type": "string"})
    mocker.patch.object(input_manager, "_InputManager__metadata")
    patch_for_validate_input_by_type = mocker.patch.object(
        input_manager, "_validate_input_by_type", side_effect=validate_input_returns
    )

    # Act
    result = input_manager._validate_tabular_element(
        first_level_key, properties_blob_key, input_data, eager_termination, elements_counter
    )

    # Assert
    assert result == expected_result
    assert patch_for_validate_input_by_type.call_count == len(validate_input_returns)


@pytest.mark.parametrize(
    "data_type, input_value, expected_result, validator_return, fixable",
    [
        # Primitive data type: valid string
        ("string", "valid string", True, True, False),
        # Primitive data type: invalid string, fixable
        ("string", "invalid string", True, False, True),
        # Primitive data type: invalid string, not fixable
        ("string", "invalid string", False, False, False),
        # Primitive data type: valid number
        ("number", 123, True, True, False),
        # Primitive data type: invalid number, fixable
        ("number", "invalid number", True, False, True),
        # Primitive data type: invalid number, not fixable
        ("number", "invalid number", False, False, False),
        # Primitive data type: valid bool
        ("bool", True, True, True, False),
        # Primitive data type: invalid bool, fixable
        ("bool", "invalid bool", True, False, True),
        # Primitive data type: invalid bool, not fixable
        ("bool", "invalid bool", False, False, False),
        # Complex data type: object, valid
        ("object", {"key": "value"}, True, True, False),
        # Complex data type: object, invalid, fixable
        ("object", "not a dict", True, False, True),
        # Complex data type: object, invalid, not fixable
        ("object", "not a dict", False, False, False),
        # Complex data type: array, valid
        ("array", [1, 2, 3], True, True, False),
        # Complex data type: array, invalid, fixable
        ("array", "not a list", True, False, True),
        # Complex data type: array, invalid, not fixable
        ("array", "not a list", False, False, False),
    ],
)
def test_validate_input_by_type(
    mocker: MockerFixture,
    data_type: str,
    input_value: Any,
    expected_result: bool,
    validator_return: bool,
    fixable: bool,
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

    if data_type in ["string", "number", "bool"]:
        data_type = "num" if data_type == "number" else data_type
        validator_mock = mocker.patch.object(
            input_manager, f"_{data_type}_type_validator", return_value=validator_return
        )
    else:
        validator_mock = mocker.patch.object(
            input_manager, f"_{data_type}_type_validator", return_value=expected_result
        )

    # Act
    result = input_manager._validate_input_by_type(
        variable_properties, variable_path, input_data, eager_termination, properties_blob_key, elements_counter
    )

    # Assert
    assert result == expected_result
    validator_mock.assert_called_once()

    if data_type in ["string", "number", "bool"]:
        if not validator_return and fixable:
            patch_for_fix_data.assert_called_once()
            elements_counter.increment.assert_called_with(ElementState.FIXED)
        elif not validator_return and not fixable:
            elements_counter.increment.assert_called_with(ElementState.INVALID)
        elif validator_return:
            elements_counter.increment.assert_called_with(ElementState.VALID)


@pytest.mark.parametrize(
    "file_type, loader_return, validate_return, eager_termination, expected_result",
    [
        # Test case where all JSON data valid
        ("json", {"key": "value"}, True, True, True),
        # Test case with CSV data, one invalid element, no eager termination
        ("csv", {"column": ["valid", "invalid"]}, False, False, False),
        # Test case with JSON data, invalid element, eager termination
        ("json", {"key": "invalid"}, False, True, False),
        # Test case with unsupported file type
        ("unsupported", None, False, False, KeyError),
    ],
)
def test_populate_pool(
    mocker: MockerFixture,
    file_type: str,
    loader_return: Dict[str, Any],
    validate_return: bool,
    eager_termination: bool,
    expected_result: bool,
) -> None:
    """
    Unit test for the _populate_pool method of the InputManager class.
    """

    # Arrange
    input_manager = InputManager()
    elements_counter = ElementsCounter()
    elements_counter.invalid_elements = int(not validate_return) + int(not eager_termination)
    mocker.patch.object(input_manager, "elements_counter", elements_counter)
    metadata = {
        "files": {
            "file1": {
                "path": "path/to/file",
                "type": file_type,
                "properties": "properties_blob_key",
            },
        },
        "properties": {
            "properties_blob_key": {"key": {"type": "string"}},
        },
    }
    mocker.patch.object(input_manager, "_InputManager__metadata", metadata)
    mocker.patch.object(input_manager, "_InputManager__pool", {})
    if file_type in ["json", "csv"]:
        mocker.patch.object(input_manager, f"_load_data_from_{file_type}", return_value=loader_return)
    if file_type == "json":
        mocker.patch.object(input_manager, "_dict_type_validator", return_value=validate_return)
    elif file_type == "csv":
        mocker.patch.object(input_manager, "_validate_tabular_element", return_value=validate_return)
    mocker.patch.object(input_manager, "_add_default_values_to_missing_inputs", return_value=(loader_return, [], []))
    mocker.patch.object(input_manager, "_log_missing_keys", return_value=None)
    mocker.patch.object(input_manager, "_filter_input_data_by_metadata", return_value=loader_return)

    # Act and assert
    if expected_result is KeyError:
        with pytest.raises(KeyError):
            input_manager._populate_pool(eager_termination=eager_termination)
    else:
        result = input_manager._populate_pool(eager_termination=eager_termination)
        assert result == expected_result


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


def test_decrement_below_zero_raises_value_error() -> None:
    """
    Unit test for the decrement() method of the ElementsCounter class when attempting to decrement below 0.
    """
    # Arrange
    counter = ElementsCounter()

    # Act and Assert
    with pytest.raises(ValueError):
        counter.decrement(ElementState.VALID)


def test_decrement_in_elements_counter() -> None:
    """
    Unit test for the decrement() method of the ElementsCounter class.
    """

    # Arrange
    counter = ElementsCounter()
    counter.increment(ElementState.VALID)
    counter.increment(ElementState.INVALID)
    counter.increment(ElementState.FIXED)
    counter.increment(ElementState.VALID)

    # Act
    counter.decrement(ElementState.VALID)
    counter.decrement(ElementState.INVALID)

    # Assert
    assert counter.valid_elements == 1
    assert counter.invalid_elements == 0
    assert counter.fixed_elements == 1


def test_update_increments_correctly() -> None:
    """
    Unit test for the _update() method of the ElementsCounter class.
    """

    # Arrange
    counter = ElementsCounter()

    # Act
    counter._update(ElementState.INVALID, 2)
    counter._update(ElementState.VALID, 1)
    counter._update(ElementState.FIXED, 3)

    # Assert
    assert counter.valid_elements == 1
    assert counter.invalid_elements == 2
    assert counter.fixed_elements == 3


def test_update_decrements_correctly() -> None:
    """
    Unit test for the _update() method of the ElementsCounter class.
    """

    # Arrange
    counter = ElementsCounter()
    counter.valid_elements = 3
    counter.invalid_elements = 2
    counter.fixed_elements = 1

    # Act
    counter._update(ElementState.VALID, -1)
    counter._update(ElementState.INVALID, -1)
    counter._update(ElementState.FIXED, -1)

    assert counter.valid_elements == 2
    assert counter.invalid_elements == 1
    assert counter.fixed_elements == 0


def test_update_with_negative_value_raises_error() -> None:
    """
    Unit test for the _update() method of the ElementsCounter class when attempting to update with a negative value.
    """

    # Arrange
    counter = ElementsCounter()

    # Act and Assert
    with pytest.raises(ValueError):
        counter._update(ElementState.VALID, -1)


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


def test_check_negative_counts_raises_error() -> None:
    """
    Unit test for the _check_negative_counts() method of the ElementsCounter class.
    """

    # Arrange
    counter = ElementsCounter()

    # Act and Assert
    with pytest.raises(ValueError, match="Valid elements count is negative"):
        counter.valid_elements = -1
        counter._check_negative_counts()

    with pytest.raises(ValueError, match="Invalid elements count is negative"):
        counter.valid_elements = 0
        counter.invalid_elements = -1
        counter._check_negative_counts()

    with pytest.raises(ValueError, match="Fixed elements count is negative"):
        counter.invalid_elements = 0
        counter.invalid_elements = 0
        counter.fixed_elements = -1
        counter._check_negative_counts()


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
