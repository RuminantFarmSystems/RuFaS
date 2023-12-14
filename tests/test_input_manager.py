from functools import reduce
import json
from typing import Any, Callable, Dict, List

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
        "_filter_input_data_by_metadata": mock_input_manager._filter_input_data_by_metadata,
        "_populate_pool": mock_input_manager._populate_pool,
        "_validate_dict_element": mock_input_manager._validate_dict_element,
        "_array_type_validator": mock_input_manager._array_type_validator,
        "_num_type_validator": mock_input_manager._num_type_validator,
        "_string_type_validator": mock_input_manager._string_type_validator,
        "_bool_type_validator": mock_input_manager._bool_type_validator,
        "_fix_data": mock_input_manager._fix_data,
        "get_data": mock_input_manager.get_data,
        "get_metadata": mock_input_manager.get_metadata,
        "_validate_input_type_dynamic": mock_input_manager._validate_input_type_dynamic,
        "_validate_tabular_element": mock_input_manager._validate_tabular_element,
        "flush_pool": mock_input_manager.flush_pool,
        "_metadata_properties_exist": mock_input_manager._metadata_properties_exist,
        "_add_variable_to_pool": mock_input_manager._add_variable_to_pool,
        "add_dict_variable_to_pool": mock_input_manager.add_dict_variable_to_pool,
        "add_tabular_variable_to_pool": mock_input_manager.add_tabular_variable_to_pool
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


def test_populate_pool_valid(mock_input_manager: InputManager, mock_metadata: Dict[str, Dict[str, Any]],
                             input_manager_original_method_states: Dict[str, Callable], ) -> None:
    """Unit test for valid data for function _populate_pool in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata
    mock_input_manager._load_data_from_json = lambda _: {"element1": "value1", "element2": "value2"}
    mock_input_manager._load_data_from_csv = lambda _: {"element3": "value3", "element4": "value4"}
    mock_input_manager._validate_dict_element = lambda *args, **kwargs: {"fixed_elements": 1,
                                                                         "valid_elements": 1,
                                                                         "total_elements": 1,
                                                                         "invalid_elements": 0,
                                                                         "is_valid": True
                                                                         }
    mock_input_manager._validate_tabular_element = lambda *args, **kwargs: {"fixed_elements": 1,
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
    mock_input_manager._validate_dict_element = input_manager_original_method_states["_validate_dict_element"]
    mock_input_manager._validate_tabular_element = input_manager_original_method_states["_validate_tabular_element"]


def test_populate_pool_invalid(mock_input_manager: InputManager, mock_metadata: Dict[str, Dict[str, Any]],
                               input_manager_original_method_states: Dict[str, Callable], ):
    """Unit test for invalid data for function _populate_pool in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata

    mock_input_manager._load_data_from_json = lambda _: {"element1": "value1", "element2": "value2"}
    mock_input_manager._load_data_from_csv = lambda _: {"element3": "value3", "element4": "value4"}
    mock_input_manager._validate_dict_element = lambda *args, **kwargs: {"fixed_elements": 1,
                                                                         "valid_elements": 1,
                                                                         "total_elements": 1,
                                                                         "invalid_elements": 1,
                                                                         "is_valid": False
                                                                         }
    mock_input_manager._validate_tabular_element = lambda *args, **kwargs: {"fixed_elements": 1,
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
    mock_input_manager._validate_dict_element = input_manager_original_method_states["_validate_dict_element"]
    mock_input_manager._validate_tabular_element = input_manager_original_method_states["_validate_tabular_element"]


def test_populate_pool_eager_termination(mock_input_manager: InputManager, mock_metadata: Dict[str, Dict[str, Any]],
                                         input_manager_original_method_states: Dict[str, Callable], ):
    """Unit test for invalid data with eager termination for function
    _populate_pool in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata

    mock_input_manager._load_data_from_json = lambda _: {"element1": "value1", "element2": "value2"}
    mock_input_manager._load_data_from_csv = lambda _: {"element3": "value3", "element4": "value4"}
    mock_input_manager._validate_dict_element = lambda *args, **kwargs: {"fixed_elements": 1,
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
    mock_input_manager._validate_dict_element = input_manager_original_method_states["_validate_dict_element"]


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
    mock_input_manager._validate_dict_element = input_manager_original_method_states["_validate_dict_element"]


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
    dummy_properties_key = "dummy_variable_properties"

    result = mock_input_manager._validate_input_type_dynamic(variable_properties, var_name, input_data_value,
                                                             dummy_properties_key)
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
    dummy_properties_key = "dummy_variable_properties"

    with pytest.raises(KeyError, match="Invalid type invalid_type"):
        mock_input_manager._validate_input_type_dynamic(variable_properties, var_name, input_data_value,
                                                        dummy_properties_key)

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
    dummy_properties_key = "dummy_variable_properties"

    with pytest.raises(KeyError, match="Missing 'type' key in variable_properties"):
        mock_input_manager._validate_input_type_dynamic(variable_properties, var_name, input_data_value,
                                                        dummy_properties_key)

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


def test_validate_element_fixable_data(mock_input_manager: InputManager,
                                       mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
                                       input_manager_original_method_states: Dict[str, Callable], ) -> None:
    """Unit test for a fixable number type input_data for _validate_dict_element in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element
    mock_input_manager._num_type_validator = MagicMock(return_value=False)
    mock_input_manager._fix_data = MagicMock(return_value=True)
    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}

    input_data = {"element2": 123}
    result = mock_input_manager._validate_dict_element(["element2"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is True
    assert result["fixed_elements"] == 1
    assert result["total_elements"] == 1
    assert result["invalid_elements"] == 0
    assert result["valid_elements"] == 0

    mock_input_manager._validate_dict_element = input_manager_original_method_states["_validate_dict_element"]
    mock_input_manager._num_type_validator = input_manager_original_method_states["_num_type_validator"]
    mock_input_manager._fix_data = input_manager_original_method_states["_fix_data"]


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
    """Unit test for _validate_tabular_element function in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element
    dummy_property = property
    properties_blob_key = "property_map_key1"
    dummy_input_data = input_data
    eager_termination = True
    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}

    result = mock_input_manager._validate_tabular_element(dummy_property, properties_blob_key,
                                                          dummy_input_data, eager_termination,
                                                          mock_element_counter_and_validity)
    assert result["is_valid"] is True
    assert result["total_elements"] == total_elements
    assert result["valid_elements"] == valid_elements
    assert result["invalid_elements"] == invalid_elements
    assert result["fixed_elements"] == fixed_elements

    mock_input_manager._validate_tabular_element = input_manager_original_method_states["_validate_tabular_element"]


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

    result = mock_input_manager._validate_tabular_element(property, properties_blob_key,
                                                          input_data, eager_termination,
                                                          mock_element_counter_and_validity)
    assert result["is_valid"] is is_valid
    assert result["total_elements"] == total_elements
    assert result["valid_elements"] == valid_elements
    assert result["invalid_elements"] == invalid_elements
    assert result["fixed_elements"] == fixed_elements

    mock_input_manager._validate_tabular_element = input_manager_original_method_states["_validate_tabular_element"]
    mock_input_manager._fix_data = input_manager_original_method_states["_fix_data"]


def test_validate_json_element_string_type(mock_input_manager: InputManager,
                                           mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
                                           input_manager_original_method_states: Dict[str, Callable],
                                           ) -> None:
    """Unit test for string type input_data for _validate_dict_element in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element
    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}

    input_data = {"element1": "123-45-6789"}
    result = mock_input_manager._validate_dict_element(["element1"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is True
    assert result["fixed_elements"] == 0
    assert result["total_elements"] == 1
    assert result["invalid_elements"] == 0
    assert result["valid_elements"] == 1

    input_data = {"element1": "invalid_value"}
    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}
    result = mock_input_manager._validate_dict_element(["element1"], "property_map_key1", input_data, True,
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
        result = mock_input_manager._validate_dict_element(["element8"], "property_map_key1", input_data, False,
                                                           mock_element_counter_and_validity)

        assert add_warning.call_count == 3
        assert result["is_valid"] is False
        assert result["invalid_elements"] == 1
        assert result["fixed_elements"] == 0
        assert result["total_elements"] == 1
        assert result["valid_elements"] == 0

    mock_input_manager._validate_dict_element = input_manager_original_method_states["_validate_dict_element"]


def test_validate_json_element_number_type(mock_input_manager: InputManager,
                                           mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
                                           input_manager_original_method_states: Dict[str, Callable], ) -> None:
    """Unit test for number type input_data for _validate_dict_element in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element

    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}
    input_data = {"element2": 123}
    result = mock_input_manager._validate_dict_element(["element2"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is True
    assert result["invalid_elements"] == 0
    assert result["fixed_elements"] == 0
    assert result["total_elements"] == 1
    assert result["valid_elements"] == 1

    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}
    input_data = {"element2": 500}
    result = mock_input_manager._validate_dict_element(["element2"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is False
    assert result["invalid_elements"] == 1
    assert result["fixed_elements"] == 0
    assert result["total_elements"] == 1
    assert result["valid_elements"] == 0

    mock_input_manager._validate_dict_element = input_manager_original_method_states["_validate_dict_element"]


def test_validate_json_element_array_type(mock_input_manager: InputManager,
                                          mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
                                          input_manager_original_method_states: Dict[str, Callable], ) -> None:
    """Unit test for array type input_data for _validate_dict_element in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element

    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}
    input_data = {"element3": [1, 2, 3]}
    result = mock_input_manager._validate_dict_element(["element3"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is True
    assert result["invalid_elements"] == 0
    assert result["fixed_elements"] == 0
    assert result["total_elements"] == 1
    assert result["valid_elements"] == 1

    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}
    input_data = {"element3": [1, 2, 3, 6, 7, 8, 10]}
    result = mock_input_manager._validate_dict_element(["element3"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is False
    assert result["invalid_elements"] == 1
    assert result["fixed_elements"] == 0
    assert result["total_elements"] == 1
    assert result["valid_elements"] == 0

    mock_input_manager._validate_dict_element = input_manager_original_method_states["_validate_dict_element"]


def test_validate_json_element_valid_object_type(mock_input_manager: InputManager,
                                                 mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
                                                 input_manager_original_method_states: Dict[str, Callable], ) -> None:
    """Unit test for valid nested object type input_data for _validate_dict_element in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element

    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}
    input_data = {"element4": {"nested_element1": "value1", "nested_element2": 123}}
    result = mock_input_manager._validate_dict_element(["element4"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is True
    assert result["invalid_elements"] == 0
    assert result["fixed_elements"] == 0
    assert result["total_elements"] == 2
    assert result["valid_elements"] == 2

    mock_input_manager._validate_dict_element = input_manager_original_method_states["_validate_dict_element"]


def test_validate_json_element_invalid_object_type(mock_input_manager: InputManager,
                                                   mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
                                                   input_manager_original_method_states: Dict[str, Callable], ) -> None:
    """Unit test for nested invalid object type input_data for _validate_dict_element in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element

    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}
    input_data = {"element4": {"nested_element1": "value1", "nested_element2": 500}}
    result = mock_input_manager._validate_dict_element(["element4"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is False
    assert result["invalid_elements"] == 1
    assert result["fixed_elements"] == 0
    assert result["total_elements"] == 2
    assert result["valid_elements"] == 1

    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}
    input_data = {"element4": {"nested_element1": "value123456789value123456789", "nested_element2": 123}}
    result = mock_input_manager._validate_dict_element(["element4"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is False
    assert result["invalid_elements"] == 1
    assert result["fixed_elements"] == 0
    assert result["total_elements"] == 1
    assert result["valid_elements"] == 0

    mock_input_manager._validate_dict_element = input_manager_original_method_states["_validate_dict_element"]


def test_validate_element_valid_nested_object_type(mock_input_manager: InputManager,
                                                   mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
                                                   input_manager_original_method_states: Dict[str, Callable], ) -> None:
    """Unit test for valid object nested within another object type
    input_data for _validate_dict_element in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element

    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}
    input_data = {"element5": {"nested_element1": "value1", "nested_element2": 123,
                               "nested_element3": {"nested_sub_element1": "cows", "nested_sub_element2": [1, 2, 3]}}}
    result = mock_input_manager._validate_dict_element(["element5"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is True
    assert result["invalid_elements"] == 0
    assert result["fixed_elements"] == 0
    assert result["total_elements"] == 4
    assert result["valid_elements"] == 4

    mock_input_manager._validate_dict_element = input_manager_original_method_states["_validate_dict_element"]


def test_validate_element_invalid_nested_object_type(mock_input_manager: InputManager,
                                                     mock_metadata_for_validate_element: Dict[str, Dict[str, Any]],
                                                     input_manager_original_method_states: Dict[str, Callable],
                                                     ) -> None:
    """Unit test for invalid object nested within another object type
    input_data for _validate_dict_element in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata_for_validate_element

    input_data = {"element5": {"nested_element1": "value1", "nested_element2": 123,
                               "nested_element3": {"nested_sub_element1": "cows", "nested_sub_element2": []}}}
    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}
    result = mock_input_manager._validate_dict_element(["element5"], "property_map_key1", input_data, True,
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
    result = mock_input_manager._validate_dict_element(["element5"], "property_map_key1", input_data, True,
                                                       mock_element_counter_and_validity)

    assert result["is_valid"] is False
    assert result["invalid_elements"] == 1
    assert result["fixed_elements"] == 0
    assert result["total_elements"] == 3
    assert result["valid_elements"] == 2

    mock_input_manager._validate_dict_element = input_manager_original_method_states["_validate_dict_element"]


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
def test_bool_type_validator(input_data_value: bool, expected_result: bool, mock_input_manager: InputManager) -> None:
    """Unit test for function _bool_type_validator in file input_manager.py"""
    variable_properties = {}
    var_name = "dummy_var_name"
    dummy_properties_key = "dummy_variable_properties"

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._bool_type_validator(variable_properties, var_name, input_data_value,
                                                         dummy_properties_key)

    if not expected_result:
        add_warning.assert_called_once()
    else:
        add_warning.assert_not_called()
    assert result == expected_result


def test_validate_json_element_invalid_var_name_raises_metadata_keyerror(mock_input_manager: InputManager,
                                                                         input_manager_original_method_states:
                                                                         Dict[str, Callable],
                                                                         ) -> None:
    """Unit test for keyerror raised for invalid var name for _validate_dict_element in file input_manager.py"""
    element_hierarchy = ["valid_key", "invalid_key"]
    properties_blob_key = "dummy_properties_blob_key"
    input_data = {"valid_key": {"another_valid_key": "value"}}
    eager_termination = False
    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}

    with pytest.raises(KeyError):
        mock_input_manager._validate_dict_element(element_hierarchy, properties_blob_key, input_data,
                                                  eager_termination, mock_element_counter_and_validity)

    mock_input_manager._validate_dict_element = input_manager_original_method_states["_validate_dict_element"]


def test_validate_json_element_invalid_var_name_raises_input_data_keyerror(mock_input_manager: InputManager,
                                                                           input_manager_original_method_states:
                                                                           Dict[str, Callable],
                                                                           ) -> None:
    """Unit test for keyerror raised for invalid var name for _validate_dict_element in file input_manager.py"""
    mock_input_manager._InputManager__metadata = {
        "properties": {
            "dummy_properties_blob_key": {
                "valid_key": {
                    "type": "object",
                    "secondary_key": {
                        "type": "string"
                    }
                }
            }
        }
    }
    element_hierarchy = ["valid_key", "secondary_key"]
    properties_blob_key = "dummy_properties_blob_key"
    input_data = {"valid_key": {"another_valid_key": "value"}}
    eager_termination = False
    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}

    with patch("RUFAS.output_manager.OutputManager.add_error") as add_error, \
            patch.object(mock_input_manager, "_fix_data", new_callable=MagicMock, return_value=False) as fix_data:
        mock_input_manager._validate_dict_element(element_hierarchy, properties_blob_key, input_data,
                                                  eager_termination, mock_element_counter_and_validity)

        assert add_error.call_count == 1
        fix_data.assert_called_once_with({"type": "string"}, element_hierarchy, input_data, properties_blob_key)

    mock_input_manager._validate_dict_element = input_manager_original_method_states["_validate_dict_element"]


def test_validate_json_element_invalid_var_type_raises_keyerror(mock_input_manager: InputManager, mocker: MockerFixture,
                                                                input_manager_original_method_states:
                                                                Dict[str, Callable],
                                                                ) -> None:
    """Unit test for keyerror raised for invalid var type for _validate_dict_element in file input_manager.py"""
    element_hierarchy = ["valid_key"]
    properties_blob_key = "dummy_valid_key"
    input_data = {"valid_key": "some_value"}
    mock_input_manager._InputManager__metadata = {"properties": {
        properties_blob_key: {
            "valid_key": {
                "type": "invalid_type"
            }
        }
    }
    }
    eager_termination = False
    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}

    with pytest.raises(KeyError):
        mock_input_manager._validate_dict_element(element_hierarchy, properties_blob_key, input_data,
                                                  eager_termination, mock_element_counter_and_validity)

    mock_input_manager._validate_dict_element = input_manager_original_method_states["_validate_dict_element"]


def test_validate_json_element_missing_type_raises_keyerror(mock_input_manager: InputManager,
                                                            input_manager_original_method_states:
                                                            Dict[str, Callable],
                                                            ) -> None:
    """Unit test for missing data type raising a KeyError for function
    _validate_dict_element in file input_manager.py"""
    element_hierarchy = ["valid_key"]
    properties_blob_key = "dummy_valid_key"
    input_data = {"valid_key": "some_value"}
    mock_input_manager._InputManager__metadata = {
        "properties": {
            properties_blob_key: {
                "valid_key": {}
            }
        }
    }
    eager_termination = False
    mock_element_counter_and_validity = {"fixed_elements": 0, "total_elements": 0, "valid_elements": 0,
                                         "invalid_elements": 0, "is_valid": True}

    with pytest.raises(KeyError, match="Missing 'type' key in variable_properties"):
        mock_input_manager._validate_dict_element(element_hierarchy, properties_blob_key, input_data,
                                                  eager_termination, mock_element_counter_and_validity)

    mock_input_manager._validate_dict_element = input_manager_original_method_states["_validate_dict_element"]


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
    """Unit test for function _array_type_validator in file input_manager.py"""
    dummy_var_name = "dummy_array"
    dummy_properties_key = "dummy_variable_properties"

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._array_type_validator(dummy_variable_to_check, dummy_var_name, dummy_value,
                                                          dummy_properties_key)

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
        (None, {"maximum": 1, "minimum": 0}, False, 1),
        ("42", {"minimum": 4, "maximum": 32}, False, 1)
    ]
)
def test_num_type_validator(dummy_value: int,
                            dummy_variable_to_check: Dict[str, int],
                            expected_result: bool,
                            expected_warning_call_count: int,
                            mock_input_manager: InputManager) -> None:
    """Unit test for function _num_type_validator in file input_manager.py"""
    dummy_var_name = "dummy_num"
    dummy_properties_key = "dummy_variable_properties"

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._num_type_validator(dummy_variable_to_check, dummy_var_name, dummy_value,
                                                        dummy_properties_key)

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
        (None, {"pattern": r"cow", "minimum_length": 1}, False, 1),
        (42.0, {"pattern": r"cow", "maximum_length": 3}, False, 1)
    ]
)
def test_string_type_validator(dummy_value: int,
                               dummy_variable_to_check: Dict[str, int],
                               expected_result: bool,
                               expected_warning_call_count: int,
                               mock_input_manager: InputManager) -> None:
    """Unit test for _string_type_validator function in file input_manager.py"""
    dummy_var_name = "dummy_var"
    dummy_properties_key = "dummy_variable_properties"

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._string_type_validator(dummy_variable_to_check, dummy_var_name, dummy_value,
                                                           dummy_properties_key)

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
    dummy_properties_key = "dummy_variable_properties"

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(dummy_variable_properties, dummy_element_hierarchy, dummy_input_data,
                                              dummy_properties_key)

    variable_to_check = reduce(lambda d, key: d[key], dummy_element_hierarchy,
                               dummy_input_data)
    assert variable_to_check == expected_value
    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


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
    dummy_properties_key = "dummy_variable_properties"

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(dummy_variable_properties, dummy_element_hierarchy, dummy_input_data,
                                              dummy_properties_key)

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
    dummy_properties_key = "dummy_variable_properties"

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(dummy_variable_properties, dummy_element_hierarchy, dummy_input_data,
                                              dummy_properties_key)

    variable_to_check = reduce(lambda d, key: d[key], dummy_element_hierarchy,
                               dummy_input_data)
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
        result = mock_input_manager._fix_data(dummy_variable_properties, dummy_element_hierarchy, dummy_input_data,
                                              dummy_properties_key)

    fixed_variable = reduce(lambda d, key: d[key], dummy_element_hierarchy,
                            dummy_input_data)

    assert fixed_variable == 3
    assert result is True
    assert add_warning.call_count == 2


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
    dummy_properties_key = "dummy_variable_properties"

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(dummy_variable_properties, dummy_element_hierarchy, dummy_input_data,
                                              dummy_properties_key)

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
    dummy_properties_key = "dummy_variable_properties"

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(dummy_variable_properties, dummy_element_hierarchy, dummy_input_data,
                                              dummy_properties_key)

    variable_to_check = reduce(lambda d, key: d[key], dummy_element_hierarchy,
                               dummy_input_data)
    assert variable_to_check == expected_value
    assert result == expected_result
    assert add_warning.call_count == expected_warning_call_count


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
    dummy_properties_key = "dummy_variable_properties"

    with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
        result = mock_input_manager._fix_data(dummy_variable_properties, dummy_element_hierarchy, dummy_input_data,
                                              dummy_properties_key)

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


@pytest.mark.parametrize('properties_blob_key', [
    "properties1",
    "properties2"
])
def test_metadata_properties_exist(properties_blob_key: str,
                                   mock_input_manager: InputManager,
                                   mock_metadata: Dict[str, Dict[str, Any]]) -> None:
    mock_input_manager._InputManager__metadata = mock_metadata

    result = mock_input_manager._metadata_properties_exist(variable_name="mock_variable",
                                                           properties_blob_key=properties_blob_key)

    assert result is True


def test_metadata_properties_exist_no_metadata(mock_input_manager: InputManager) -> None:
    mock_input_manager._InputManager__metadata = {}

    with pytest.raises(ValueError):
        mock_input_manager._metadata_properties_exist(
            variable_name="mock_variable",
            properties_blob_key="mock_properties_blob_key")


@pytest.mark.parametrize('variable_name, properties_blob_key', [
    ("variable1", "propertiesA"),
    ("variable2", "propertiesB")
])
def test_metadata_properties_exists_invalid_properties_blob_key(variable_name: str,
                                                                properties_blob_key: str,
                                                                mock_input_manager: InputManager,
                                                                mock_metadata: Dict[str, Dict[str, Any]]) -> None:
    mock_input_manager._InputManager__metadata = mock_metadata

    with pytest.raises(KeyError):
        mock_input_manager._metadata_properties_exist(
            variable_name=variable_name,
            properties_blob_key=properties_blob_key)


@pytest.fixture
def mock_metadata_for_add_variable_to_pool() -> Dict[str, Dict[str, Any]]:
    return {
        "files": {
            "file1": {"type": "json", "path": "path/to/json/file1.json", "properties": "properties1"},
            "file2": {"type": "csv", "path": "path/to/csv/file2.csv", "properties": "properties2"},
        },
        "properties": {
            "dict_data": {"int": "some_value1",
                          "str": "some_value2",
                          "float": "some_value1",
                          "int_array": "some_value2",
                          "float_array": "some_value1",
                          "str_arr": "some_value2"},
            "array_of_int_data": {"array_of_int_data": "some_value3"},
            "array_of_float_data": {"array_of_float_data": "some_value3"},
            "array_of_str_data": {"array_of_str_data": "some_value3"},
            "array_of_dict_data": {"array_of_dict_data": "some_value3"},
            "dict_of_array_data": {"array1": "some_value1",
                                   "array2": "some_value2",
                                   "array3": "some_value1"}
        }
    }


@pytest.mark.parametrize('variable_name, data, properties_blob_key, starting_im_pool, is_dict_variable', [
    ("dict_data",
     {"int": 0, "str": "", "float": 0.0, "int_array": [0, 1, 2], "float_array": [0.0, 1.1, 2.2],
      "str_arr": ["example_str1", "example_str2", "example_str3"]}, "dict_data", {}, True),
    ("array_of_int_data", {"array_of_int_data": [0, 1, 2]}, "array_of_int_data", {}, False),
    ("array_of_float_data", {"array_of_float_data": [0.0, 1.1, 2.2]}, "array_of_float_data", {}, False),
    ("array_of_str_data", {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]}, "array_of_str_data",
     {}, False),
    ("array_of_dict_data", {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]}, "array_of_dict_data", {}, False),
    ("dict_of_array_data", {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
     "dict_of_array_data", {}, False),
    ("dict_data",
     {"int": 0, "str": "", "float": 0.0, "int_array": [0, 1, 2], "float_array": [0.0, 1.1, 2.2],
      "str_arr": ["example_str1", "example_str2", "example_str3"]}, "dict_data",
     {"dict_data": {"1": 1}}, True),
    ("array_of_int_data", {"array_of_int_data": [0, 1, 2]}, "array_of_int_data", {"array_of_int_data": [-1, 0, 1]},
     False),
    ("array_of_float_data", {"array_of_float_data": [0.0, 1.1, 2.2]}, "array_of_float_data",
     {"array_of_float_data": [-1.0, 0.0, 1.0]},
     False),
    ("array_of_str_data", {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]}, "array_of_str_data",
     {"array_of_str_data": ["a", "b", "c"]}, False),
    ("array_of_dict_data", {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]}, "array_of_dict_data",
     {"array_of_dict_data": [{"A": -1}, {"B": 0}, {"C": 1}]}, False),
    ("dict_of_array_data", {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
     "dict_of_array_data", {"dict_of_array_data": {"a": [1, 2, 3]}}, False),
])
def test_add_variable_to_pool_valid(variable_name: str,
                                    data: Any,
                                    properties_blob_key: str,
                                    starting_im_pool: Dict[str, Any],
                                    is_dict_variable: bool,
                                    mock_input_manager: InputManager,
                                    mock_metadata_for_add_variable_to_pool: Dict[str, Dict[str, Any]],
                                    input_manager_original_method_states: Dict[str, Callable]) -> None:
    mock_input_manager._InputManager__metadata = mock_metadata_for_add_variable_to_pool
    mock_input_manager._InputManager__pool = starting_im_pool
    mock_input_manager._validate_dict_element = lambda *args, **kwargs: {"fixed_elements": 1,
                                                                         "valid_elements": 1,
                                                                         "total_elements": 1,
                                                                         "invalid_elements": 0,
                                                                         "is_valid": True
                                                                         }
    mock_input_manager._validate_tabular_element = lambda *args, **kwargs: {"fixed_elements": 1,
                                                                            "valid_elements": 1,
                                                                            "total_elements": 1,
                                                                            "invalid_elements": 0,
                                                                            "is_valid": True
                                                                            }
    expected_add_warning_count = 1 if starting_im_pool else 0

    with patch("RUFAS.output_manager.OutputManager.add_log") as mock_om_add_log:
        with patch("RUFAS.output_manager.OutputManager.add_warning") as mock_om_add_warning:
            with patch("RUFAS.output_manager.OutputManager.add_error") as mock_om_add_error:
                result = mock_input_manager._add_variable_to_pool(
                    variable_name=variable_name,
                    data=data,
                    properties_blob_key=properties_blob_key,
                    eager_termination=False,
                    is_variable_dict=is_dict_variable)

    assert result is True
    assert mock_om_add_log.call_count == 4
    assert mock_om_add_warning.call_count == expected_add_warning_count
    assert mock_om_add_error.call_count == 0
    assert variable_name in mock_input_manager._InputManager__pool
    assert mock_input_manager.get_data(variable_name) == data

    mock_input_manager._add_variable_to_pool = input_manager_original_method_states["_add_variable_to_pool"]
    mock_input_manager._validate_dict_element = input_manager_original_method_states["_validate_dict_element"]
    mock_input_manager._validate_tabular_element = input_manager_original_method_states["_validate_tabular_element"]


@pytest.mark.parametrize('variable_name, data, properties_blob_key, starting_im_pool, is_dict_variable', [
    ("dict_data",
     {"int": 0, "str": "", "float": 0.0, "int_array": [0, 1, 2], "float_array": [0.0, 1.1, 2.2],
      "str_arr": ["example_str1", "example_str2", "example_str3"]}, "dict_data", {}, True),
    ("array_of_int_data", {"array_of_int_data": [0, 1, 2]}, "array_of_int_data", {}, False),
    ("array_of_float_data", {"array_of_float_data": [0.0, 1.1, 2.2]}, "array_of_float_data", {}, False),
    ("array_of_str_data", {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]}, "array_of_str_data",
     {}, False),
    ("array_of_dict_data", {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]}, "array_of_dict_data", {}, False),
    ("dict_of_array_data", {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
     "dict_of_array_data", {}, False),
    ("dict_data",
     {"int": 0, "str": "", "float": 0.0, "int_array": [0, 1, 2], "float_array": [0.0, 1.1, 2.2],
      "str_arr": ["example_str1", "example_str2", "example_str3"]}, "dict_data",
     {"dict_data": {"1": 1}}, True),
    ("array_of_int_data", {"array_of_int_data": [0, 1, 2]}, "array_of_int_data", {"array_of_int_data": [-1, 0, 1]},
     False),
    ("array_of_float_data", {"array_of_float_data": [0.0, 1.1, 2.2]}, "array_of_float_data",
     {"array_of_float_data": [-1.0, 0.0, 1.0]},
     False),
    ("array_of_str_data", {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]}, "array_of_str_data",
     {"array_of_str_data": ["a", "b", "c"]}, False),
    ("array_of_dict_data", {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]}, "array_of_dict_data",
     {"array_of_dict_data": [{"A": -1}, {"B": 0}, {"C": 1}]}, False),
    ("dict_of_array_data", {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
     "dict_of_array_data", {"dict_of_array_data": {"a": [1, 2, 3]}}, False),
])
def test_add_variable_to_pool_invalid(variable_name: str,
                                      data: Any,
                                      properties_blob_key: str,
                                      starting_im_pool: Dict[str, Any],
                                      is_dict_variable: bool,
                                      mock_input_manager: InputManager,
                                      mock_metadata_for_add_variable_to_pool: Dict[str, Dict[str, Any]],
                                      input_manager_original_method_states: Dict[str, Callable]) -> None:
    mock_input_manager._InputManager__metadata = mock_metadata_for_add_variable_to_pool
    mock_input_manager._InputManager__pool = starting_im_pool
    mock_input_manager._validate_dict_element = lambda *args, **kwargs: {"fixed_elements": 1,
                                                                         "valid_elements": 1,
                                                                         "total_elements": 1,
                                                                         "invalid_elements": 1,
                                                                         "is_valid": False
                                                                         }
    mock_input_manager._validate_tabular_element = lambda *args, **kwargs: {"fixed_elements": 1,
                                                                            "valid_elements": 1,
                                                                            "total_elements": 1,
                                                                            "invalid_elements": 1,
                                                                            "is_valid": False
                                                                            }

    with patch("RUFAS.output_manager.OutputManager.add_log") as mock_om_add_log:
        with patch("RUFAS.output_manager.OutputManager.add_warning") as mock_om_add_warning:
            with patch("RUFAS.output_manager.OutputManager.add_error") as mock_om_add_error:
                result = mock_input_manager._add_variable_to_pool(
                    variable_name=variable_name,
                    data=data,
                    properties_blob_key=properties_blob_key,
                    eager_termination=False,
                    is_variable_dict=is_dict_variable)

    assert result is False
    assert mock_om_add_log.call_count == 4
    assert mock_om_add_warning.call_count == 0
    assert mock_om_add_error.call_count == 1

    if starting_im_pool:
        assert starting_im_pool[variable_name] == mock_input_manager.get_data(variable_name)
    else:
        assert variable_name not in mock_input_manager._InputManager__pool

    mock_input_manager._add_variable_to_pool = input_manager_original_method_states["_add_variable_to_pool"]
    mock_input_manager._validate_dict_element = input_manager_original_method_states["_validate_dict_element"]
    mock_input_manager._validate_tabular_element = input_manager_original_method_states["_validate_tabular_element"]


@pytest.mark.parametrize('variable_name, data, properties_blob_key, starting_im_pool, is_dict_variable', [
    ("dict_data",
     {"int": 0, "str": "", "float": 0.0, "int_array": [0, 1, 2], "float_array": [0.0, 1.1, 2.2],
      "str_arr": ["example_str1", "example_str2", "example_str3"]}, "dict_data", {}, True),
    ("array_of_int_data", {"array_of_int_data": [0, 1, 2]}, "array_of_int_data", {}, False),
    ("array_of_float_data", {"array_of_float_data": [0.0, 1.1, 2.2]}, "array_of_float_data", {}, False),
    ("array_of_str_data", {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]}, "array_of_str_data",
     {}, False),
    ("array_of_dict_data", {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]}, "array_of_dict_data", {}, False),
    ("dict_of_array_data", {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
     "dict_of_array_data", {}, False),
    ("dict_data",
     {"int": 0, "str": "", "float": 0.0, "int_array": [0, 1, 2], "float_array": [0.0, 1.1, 2.2],
      "str_arr": ["example_str1", "example_str2", "example_str3"]}, "dict_data", {"dict_data": {"1": 1}}, True),
    ("array_of_int_data", {"array_of_int_data": [0, 1, 2]}, "array_of_int_data", {"array_of_int_data": [-1, 0, 1]},
     False),
    ("array_of_float_data", {"array_of_float_data": [0.0, 1.1, 2.2]}, "array_of_float_data",
     {"array_of_float_data": [-1.0, 0.0, 1.0]}, False),
    ("array_of_str_data", {"array_of_str_data": ["example_str1", "example_str2", "example_str3"]}, "array_of_str_data",
     {"array_of_str_data": ["a", "b", "c"]}, False),
    ("array_of_dict_data", {"array_of_dict_data": [{"a": 0}, {"b": 1}, {"c": 2}]}, "array_of_dict_data",
     {"array_of_dict_data": [{"A": -1}, {"B": 0}, {"C": 1}]}, False),
    ("dict_of_array_data", {"array1": [1, 2, 3], "array2": ["a", "b", "c"], "array3": [0.0, 1.1, 2.2]},
     "dict_of_array_data", {"dict_of_array_data": {"a": [1, 2, 3]}}, False),
])
def test_add_variable_to_pool_eager_termination(variable_name: str,
                                                data: Any,
                                                properties_blob_key: str,
                                                starting_im_pool: Dict[str, Any],
                                                is_dict_variable: bool,
                                                mock_input_manager: InputManager,
                                                mock_metadata_for_add_variable_to_pool: Dict[str, Dict[str, Any]],
                                                input_manager_original_method_states: Dict[str, Callable]) -> None:
    mock_input_manager._InputManager__metadata = mock_metadata_for_add_variable_to_pool
    mock_input_manager._InputManager__pool = starting_im_pool
    mock_input_manager._validate_dict_element = lambda *args, **kwargs: {"fixed_elements": 1,
                                                                         "valid_elements": 1,
                                                                         "total_elements": 1,
                                                                         "invalid_elements": 1,
                                                                         "is_valid": False
                                                                         }
    mock_input_manager._validate_tabular_element = lambda *args, **kwargs: {"fixed_elements": 1,
                                                                            "valid_elements": 1,
                                                                            "total_elements": 1,
                                                                            "invalid_elements": 1,
                                                                            "is_valid": False
                                                                            }

    with patch("RUFAS.output_manager.OutputManager.add_log") as mock_om_add_log:
        with patch("RUFAS.output_manager.OutputManager.add_warning") as mock_om_add_warning:
            with patch("RUFAS.output_manager.OutputManager.add_error") as mock_om_add_error:
                with pytest.raises(ValueError):
                    mock_input_manager._add_variable_to_pool(
                        variable_name=variable_name,
                        data=data,
                        properties_blob_key=properties_blob_key,
                        eager_termination=True,
                        is_variable_dict=is_dict_variable)

    assert mock_om_add_log.call_count == 4
    assert mock_om_add_warning.call_count == 0
    assert mock_om_add_error.call_count == 1

    if starting_im_pool:
        assert starting_im_pool[variable_name] == mock_input_manager.get_data(variable_name)
    else:
        assert variable_name not in mock_input_manager._InputManager__pool
    mock_input_manager._add_variable_to_pool = input_manager_original_method_states["_add_variable_to_pool"]
    mock_input_manager._validate_dict_element = input_manager_original_method_states["_validate_dict_element"]
    mock_input_manager._validate_tabular_element = input_manager_original_method_states["_validate_tabular_element"]


@pytest.mark.parametrize('variable_name, data, properties_blob_key', [
    ("var1", {}, "key1"),
    ("var2", {"a": 1}, "key2"),
    ("var3", {"a": "A", "b": 2, "c": True}, "key3"),
])
def test_add_dict_variable_to_pool(variable_name: str,
                                   data: Dict[str, Any],
                                   properties_blob_key: str,
                                   mock_input_manager: InputManager,
                                   input_manager_original_method_states: Dict[str, Callable]) -> None:
    mock_input_manager._metadata_properties_exist = MagicMock(return_value=True)
    mock_input_manager._add_variable_to_pool = MagicMock(return_value=True)

    with patch("RUFAS.output_manager.OutputManager.add_error") as mock_om_add_error:
        result = mock_input_manager.add_dict_variable_to_pool(
            variable_name=variable_name,
            data=data,
            properties_blob_key=properties_blob_key,
            eager_termination=False
        )

    assert result is True
    assert mock_om_add_error.call_count == 0
    mock_input_manager._metadata_properties_exist.assert_called_once_with(
        variable_name=variable_name,
        properties_blob_key=properties_blob_key)
    mock_input_manager._add_variable_to_pool.assert_called_once_with(
        variable_name=variable_name,
        data=data,
        properties_blob_key=properties_blob_key,
        eager_termination=False,
        is_variable_dict=True
    )

    mock_input_manager.add_dict_variable_to_pool = input_manager_original_method_states["add_dict_variable_to_pool"]
    mock_input_manager._metadata_properties_exist = input_manager_original_method_states["_metadata_properties_exist"]
    mock_input_manager._add_variable_to_pool = input_manager_original_method_states["_add_variable_to_pool"]


@pytest.mark.parametrize('variable_name, data, properties_blob_key', [
    ("var1", "a", "key1"),
    ("var2", [1, 2, 3], "key2"),
    ("var3", 5, "key3"),
])
def test_add_dict_variable_to_pool_type_error(variable_name: str,
                                              data: Dict[str, Any],
                                              properties_blob_key: str,
                                              mock_input_manager: InputManager,
                                              input_manager_original_method_states: Dict[str, Callable]) -> None:
    mock_input_manager._metadata_properties_exist = MagicMock(return_value=True)
    mock_input_manager._add_variable_to_pool = MagicMock(return_value=True)

    with patch("RUFAS.output_manager.OutputManager.add_error") as mock_om_add_error:
        with pytest.raises(TypeError):
            mock_input_manager.add_dict_variable_to_pool(
                variable_name=variable_name,
                data=data,
                properties_blob_key=properties_blob_key,
                eager_termination=False
            )

        assert mock_om_add_error.call_count == 1
        mock_input_manager._metadata_properties_exist.assert_not_called()
        mock_input_manager._add_variable_to_pool.assert_not_called()

        mock_input_manager.add_dict_variable_to_pool = \
            input_manager_original_method_states["add_dict_variable_to_pool"]
        mock_input_manager._metadata_properties_exist = \
            input_manager_original_method_states["_metadata_properties_exist"]
        mock_input_manager._add_variable_to_pool = input_manager_original_method_states["_add_variable_to_pool"]


@pytest.mark.parametrize('variable_name, data, properties_blob_key', [
    ("var1", {}, "key1"),
    ("var2", {"a": 1}, "key2"),
    ("var3", {"a": "A", "b": 2, "c": True}, "key3"),
])
def test_add_dict_variable_to_pool_invalid_data(variable_name: str,
                                                data: Dict[str, Any],
                                                properties_blob_key: str,
                                                mock_input_manager: InputManager,
                                                input_manager_original_method_states: Dict[str, Callable]) -> None:
    mock_input_manager._metadata_properties_exist = MagicMock(return_value=True)
    mock_input_manager._add_variable_to_pool = MagicMock(return_value=False)

    with patch("RUFAS.output_manager.OutputManager.add_error") as mock_om_add_error:
        result = mock_input_manager.add_dict_variable_to_pool(
            variable_name=variable_name,
            data=data,
            properties_blob_key=properties_blob_key,
            eager_termination=False
        )

        assert result is False
        assert mock_om_add_error.call_count == 0
        mock_input_manager._metadata_properties_exist.assert_called_once_with(
            variable_name=variable_name,
            properties_blob_key=properties_blob_key)
        mock_input_manager._add_variable_to_pool.assert_called_once_with(
            variable_name=variable_name,
            data=data,
            properties_blob_key=properties_blob_key,
            eager_termination=False,
            is_variable_dict=True
        )

        mock_input_manager.add_dict_variable_to_pool = \
            input_manager_original_method_states["add_dict_variable_to_pool"]
        mock_input_manager._metadata_properties_exist = \
            input_manager_original_method_states["_metadata_properties_exist"]
        mock_input_manager._add_variable_to_pool = input_manager_original_method_states["_add_variable_to_pool"]



@pytest.mark.parametrize('variable_name, data, properties_blob_key', [
    ("var1", [1, 2, 3], "key1"),
    ("var2", ["a", "b", "c"], "key2"),
    ("var3", [0.0, 1.1, 2.2], "key3"),
    ("var4", {"a": [1, 2, 3], "b": ["a", "b", "c"], "c": [0.0, 1.1, 2.2]}, "key4")
])
def test_add_tabular_variable_to_pool(variable_name: str,
                                      data: Dict[str, List[Any]] | List[Any],
                                      properties_blob_key: str,
                                      mock_input_manager: InputManager,
                                      input_manager_original_method_states: Dict[str, Callable]) -> None:
    """Test for InputManager.add_tabular_variable_to_pool() for valid data"""
    mock_input_manager._metadata_properties_exist = MagicMock(return_value=True)
    mock_input_manager._add_variable_to_pool = MagicMock(return_value=True)

    expected_data_for_add_variable_to_pool = {variable_name: data} if isinstance(data, List) else data

    with patch("RUFAS.output_manager.OutputManager.add_error") as mock_om_add_error:
        result = mock_input_manager.add_tabular_variable_to_pool(
            variable_name=variable_name,
            data=data,
            properties_blob_key=properties_blob_key,
            eager_termination=False
        )

    assert result is True
    assert mock_om_add_error.call_count == 0
    mock_input_manager._metadata_properties_exist.assert_called_once_with(
        variable_name=variable_name,
        properties_blob_key=properties_blob_key)
    mock_input_manager._add_variable_to_pool.assert_called_once_with(
        variable_name=variable_name,
        data=expected_data_for_add_variable_to_pool,
        properties_blob_key=properties_blob_key,
        eager_termination=False,
        is_variable_dict=False
    )

    mock_input_manager.add_tabular_variable_to_pool = \
        input_manager_original_method_states["add_tabular_variable_to_pool"]
    mock_input_manager._metadata_properties_exist = input_manager_original_method_states["_metadata_properties_exist"]
    mock_input_manager._add_variable_to_pool = input_manager_original_method_states["_add_variable_to_pool"]


@pytest.mark.parametrize('variable_name, data, properties_blob_key', [
    ("var1", "a", "key1"),
    ("var2", True, "key2"),
    ("var3", 5, "key3"),
])
def test_add_tabular_variable_to_pool_type_error(variable_name: str,
                                                 data: Dict[str, List[Any]] | List[Any],
                                                 properties_blob_key: str,
                                                 mock_input_manager: InputManager,
                                                 input_manager_original_method_states: Dict[str, Callable]) -> None:
    """Test for InputManager.add_tabular_variable_to_pool() for incorrect data type is received"""
    mock_input_manager._metadata_properties_exist = MagicMock(return_value=True)
    mock_input_manager._add_variable_to_pool = MagicMock(return_value=True)

    with patch("RUFAS.output_manager.OutputManager.add_error") as mock_om_add_error:
        with pytest.raises(TypeError):
            mock_input_manager.add_tabular_variable_to_pool(
                variable_name=variable_name,
                data=data,
                properties_blob_key=properties_blob_key,
                eager_termination=False
            )

        assert mock_om_add_error.call_count == 1
        mock_input_manager._metadata_properties_exist.assert_not_called()
        mock_input_manager._add_variable_to_pool.assert_not_called()

        mock_input_manager.add_tabular_variable_to_pool = \
            input_manager_original_method_states["add_tabular_variable_to_pool"]
        mock_input_manager._metadata_properties_exist = \
            input_manager_original_method_states["_metadata_properties_exist"]
        mock_input_manager._add_variable_to_pool = input_manager_original_method_states["_add_variable_to_pool"]


@pytest.mark.parametrize('variable_name, data, properties_blob_key', [
    ("var1", [1, 2, 3], "key1"),
    ("var2", ["a", "b", "c"], "key2"),
    ("var3", [0.0, 1.1, 2.2], "key3"),
    ("var4", {"a": [1, 2, 3], "b": ["a", "b", "c"], "c": [0.0, 1.1, 2.2]}, "key4")
])
def test_add_tabular_variable_to_pool_invalid_data(variable_name: str,
                                                   data: Dict[str, List[Any]] | List[Any],
                                                   properties_blob_key: str,
                                                   mock_input_manager: InputManager,
                                                   input_manager_original_method_states: Dict[str, Callable]) -> None:
    """Test for InputManager.add_tabular_variable_to_pool() for invalid data and eager_termination set to False"""
    mock_input_manager._metadata_properties_exist = MagicMock(return_value=True)
    mock_input_manager._add_variable_to_pool = MagicMock(return_value=False)

    expected_data_for_add_variable_to_pool = {variable_name: data} if isinstance(data, List) else data

    with patch("RUFAS.output_manager.OutputManager.add_error") as mock_om_add_error:
        result = mock_input_manager.add_tabular_variable_to_pool(
            variable_name=variable_name,
            data=data,
            properties_blob_key=properties_blob_key,
            eager_termination=False
        )

        assert result is False
        assert mock_om_add_error.call_count == 0
        mock_input_manager._metadata_properties_exist.assert_called_once_with(
            variable_name=variable_name,
            properties_blob_key=properties_blob_key)
        mock_input_manager._add_variable_to_pool.assert_called_once_with(
            variable_name=variable_name,
            data=expected_data_for_add_variable_to_pool,
            properties_blob_key=properties_blob_key,
            eager_termination=False,
            is_variable_dict=False
        )

        mock_input_manager.add_tabular_variable_to_pool = \
            input_manager_original_method_states["add_tabular_variable_to_pool"]
        mock_input_manager._metadata_properties_exist = \
            input_manager_original_method_states["_metadata_properties_exist"]
        mock_input_manager._add_variable_to_pool = input_manager_original_method_states["_add_variable_to_pool"]
