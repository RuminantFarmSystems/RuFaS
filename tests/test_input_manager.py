"""
RUFAS: Ruminant Farm Systems Model
File name: test_input_manager.py
Description: Implements test cases for Input Manager
Author(s): Niko Tomlinson, ndt2@cornell.edu
"""
from functools import reduce
from typing import Any, Callable, Dict
from mock import MagicMock, Mock, mock_open, patch
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
        "_load_data": mock_input_manager._load_data,
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


def test_load_data_json(mock_input_manager: InputManager) -> None:
    """Unit test for function _load_data with json file in file input_manager.py"""
    mock_input_manager._InputManager__metadata = {
        "files": {
            "dummy_data_file": {
                "path": "dummy_data.json",
                "type": "json"
            }
        }
    }

    with patch("builtins.open", mock_open(read_data='{"key": "value"}')):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            mock_input_manager._load_data()

    assert mock_input_manager._InputManager__pool == {"dummy_data_file": {"key": "value"}}
    assert add_log.call_count == 2


def test_load_data_csv(mock_input_manager: InputManager) -> None:
    """Unit test for function _load_data with csv file in file input_manager.py"""
    mock_input_manager._InputManager__metadata = {
        "files": {
            "dummy_data_file": {
                "path": "dummy_data.csv",
                "type": "csv"
            }
        }
    }
    with patch("builtins.open", mock_open(read_data="key1,key2\na,1\nb,2\n")):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            mock_input_manager._load_data()

    assert mock_input_manager._InputManager__pool == {"dummy_data_file": {"key1": ["a", "b"],
                                                                          "key2": [1, 2]}}
    assert add_log.call_count == 2


def test_load_data_wont_add_non_csv_non_json_file_data_to_pool(mock_input_manager: InputManager) -> None:
    """Unit test for function _load_data with a file that's neither a csv nor json in file input_manager.py"""
    mock_input_manager._InputManager__metadata = {
        "files": {
            "dummy_data_file": {
                "path": "dummy_data.txt",
                "type": "txt"
            }
        }
    }

    with patch("builtins.open", mock_open(read_data="key_and_value")):
        with patch("RUFAS.output_manager.OutputManager.add_warning") as add_warning:
            with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
                mock_input_manager._load_data()

    assert mock_input_manager._InputManager__pool == {}
    assert add_warning.call_count == 1
    assert add_log.call_count == 1


def test_load_data_raises_exception(mock_input_manager: InputManager) -> None:
    """Unit test for function _load_data raising an exception in file input_manager.py"""
    mock_open_func = Mock()
    mock_open_func.side_effect = Exception("Error opening file")

    with patch("builtins.open", mock_open_func):
        with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
            with pytest.raises(Exception):
                mock_input_manager._load_data("bad/path.csv")
                assert add_log.call_count == 1


def test_start_data_processing(mock_input_manager: InputManager,
                               input_manager_original_method_states: Dict[str, Callable], ) -> None:
    """Unit test for function start_data_processing in file input_manager.py"""
    mock_input_manager._load_metadata = MagicMock()
    mock_input_manager._load_data = MagicMock()
    mock_input_manager._validate_data = MagicMock(return_value=True)

    mock_input_manager.start_data_processing("mock/metadata/path")

    mock_input_manager._load_metadata.assert_called_once()
    mock_input_manager._load_data.assert_called_once()
    mock_input_manager._validate_data.assert_called_once()

    # Restore original methods
    mock_input_manager._load_metadata = input_manager_original_method_states["_load_metadata"]
    mock_input_manager._load_data = input_manager_original_method_states["_load_data"]
    mock_input_manager._validate_data = input_manager_original_method_states["_validate_data"]


@pytest.fixture
def mock_metadata(mocker: MockerFixture) -> Dict[str, Dict[str, Any]]:
    return {
        "dummyconfig": {},
        "files": {
            "animal": {"properties": "animal_properties"},
            "manure": {"properties": "manure_properties"},
            "crop": {"properties": "crop_properties"},
            "economy": {"properties": "economy_properties"},
        },
        "properties": {
            "animal_properties": {"animal_var1": {"default": "dummyvalue1", "type": "string"},
                                  "animal_var2": {"default": 5, "type": "number"},
                                  "animal_var3": {"type": "object",
                                                  "animal_nested1": {"default": "dummyvalue3",
                                                                     "type": "string"}, }
                                  },
            "manure_properties": {"manure_var1": {"default": [1, 2, 3], "type": "array"},
                                  "manure_var2": {"default": "dummyvalue2", "type": "string"},
                                  "manure_var3": {"type": "object",
                                                  "manure_nested1": {"default": True,
                                                                     "type": "bool", }},
                                  },
            "crop_properties": {"crop_var1": {"default": "dummyvalue1"},
                                "crop_var2": {"default": "dummyvalue2"},
                                "crop_var3": {"type": "object",
                                              "crop_nested1": {"type": "object",
                                                               "crop_nested2": {
                                                                   "default": "dummyvalue3",
                                                                   "type": "string", }},
                                              }
                                },
            "economy_properties": {"array_var1": {"type": "array",
                                                  "default": [1, 2, 3, 4, 5],
                                                  "minimum_length": 5,
                                                  "maximum_length": 10,
                                                  },
                                   "array_var2": {"type": "array",
                                                  "default": [],
                                                  "minimum_length": 0,
                                                  "maximum_length": 5,
                                                  },
                                   "array_var3": {"type": "array",
                                                  "default": [1, 2, 3],
                                                  "minimum_length": 2,
                                                  "maximum_length": 5,
                                                  },
                                   "array_var4": {"type": "object",
                                                  "array_var5": {"type": "array",
                                                                 "default": [1, 2, 3],
                                                                 "minimum_length": 2,
                                                                 "maximum_length": 5,
                                                                 },
                                                  },
                                   "array_var6": {"type": "array",
                                                  "minimum_length": 5,
                                                  "maximum_length": 10,
                                                  },
                                   "array_var7": {"type": "array",
                                                  "minimum_length": 0,
                                                  "maximum_length": 5,
                                                  },
                                   "array_var8": {"type": "array",
                                                  "minimum_length": 2,
                                                  "maximum_length": 5,
                                                  },
                                   "array_var9": {"type": "object",
                                                  "array_var10": {"type": "array",
                                                                  "minimum_length": 2,
                                                                  "maximum_length": 5,
                                                                  },
                                                  },
                                   "str_var1": {"type": "str",
                                                "default": "cow",
                                                "pattern": r"cow",
                                                "minimum_length": 1,
                                                "maximum_length": 5,
                                                },
                                   "str_var2": {"type": "str",
                                                "default": "",
                                                "minimum_length": 0,
                                                "maximum_length": 5,
                                                },
                                   "str_var3": {"type": "str",
                                                "default": "cow",
                                                "pattern": r"cow",
                                                "minimum_length": 2,
                                                "maximum_length": 5,
                                                },
                                   "str_var4": {"type": "object",
                                                "str_var5": {"type": "str",
                                                             "default": "cow",
                                                             "pattern": r"cow",
                                                             "minimum_length": 2,
                                                             "maximum_length": 5,
                                                             },
                                                },
                                   "str_var6": {"type": "str",
                                                "pattern": r"cow",
                                                "minimum_length": 1,
                                                "maximum_length": 5,
                                                },
                                   "str_var7": {"type": "str",
                                                "pattern": r"cow",
                                                "minimum_length": 1,
                                                "maximum_length": 5,
                                                },
                                   "str_var8": {"type": "str",
                                                "pattern": r"cow",
                                                "minimum_length": 1,
                                                "maximum_length": 5,
                                                },
                                   "str_var9": {"type": "object",
                                                "str_var10": {"type": "str",
                                                              "pattern": r"cow",
                                                              "minimum_length": 2,
                                                              "maximum_length": 5,
                                                              },
                                                },
                                   "num_var1": {"type": "number",
                                                "default": 5,
                                                "minimum": 0,
                                                "maximum": 10,
                                                },
                                   "num_var2": {"type": "number",
                                                "default": 0,
                                                "minimum": 0,
                                                "maximum": 10,
                                                },
                                   "num_var3": {"type": "number",
                                                "default": 5,
                                                "minimum": 1,
                                                "maximum": 10,
                                                },
                                   "num_var4": {"type": "object",
                                                "num_var5": {"type": "number",
                                                             "default": 5,
                                                             "minimum": 0,
                                                             "maximum": 10,
                                                             },
                                                },
                                   "num_var6": {"type": "number",
                                                "minimum": 0,
                                                "maximum": 10,
                                                },
                                   "num_var7": {"type": "number",
                                                "minimum": 0,
                                                "maximum": 10,
                                                },
                                   "num_var8": {"type": "number",
                                                "minimum": 1,
                                                "maximum": 10,
                                                },
                                   "num_var9": {"type": "object",
                                                "num_var10": {"type": "number",
                                                              "minimum": 0,
                                                              "maximum": 10,
                                                              },
                                                },
                                   "bool_var1": {"type": "bool",
                                                 "default": True
                                                 },
                                   "bool_var2": {"type": "bool",
                                                 "default": False
                                                 },
                                   "bool_var3": {"type": "object",
                                                 "bool_var4": {"type": "bool",
                                                               "default": True
                                                               },
                                                 },
                                   "bool_var5": {"type": "bool",
                                                 },
                                   "bool_var6": {"type": "bool",
                                                 },
                                   "bool_var7": {"type": "object",
                                                 "bool_var8": {"type": "bool",
                                                               },
                                                 },
                                   }
        }}


@pytest.fixture
def mock_pool(mocker: MockerFixture) -> Dict[str, Dict[str, Any]]:
    return {
        "animal": {"animal_var1": "dummyvalue1",
                   "animal_var2": "dummyvalue2",
                   "animal_var3": {
                       "animal_nested1": "dummyvalue3"
                   },
                   },
        "manure": {"manure_var1": "dummyvalue3",
                   "manure_var2": "dummyvalue4",
                   "manure_var3": {
                       "manure_nested1": "dummyvalue3"
                   },
                   },
        "crop": {"crop_var1": "dummyvalue5",
                 "crop_var2": "dummyvalue6",
                 "crop_var3": {
                     "crop_nested1": "dummyvalue3"
                 },
                 },
        "economy": {"array_var1": [1, 2, 3],
                    "array_var2": [1, 2, 3, 4, 5],
                    "array_var3": [],
                    "array_var4": {
                        "array_var5": [1, 2],
                    },
                    "array_var6": [1, 2, 3],
                    "array_var7": [1, 2, 3, 4, 5],
                    "array_var8": [],
                    "array_var9": {
                        "array_var10": [1, 2],
                    },
                    "str_var1": "muu",
                    "str_var2": "muumuu",
                    "str_var3": "",
                    "str_var4": {
                        "str_var5": "muu",
                    },
                    "str_var6": "muu",
                    "str_var7": "muumuu",
                    "str_var8": "",
                    "str_var9": {
                        "str_var10": "muu",
                    },
                    "num_var1": -1,
                    "num_var2": -1,
                    "num_var3": 0,
                    "num_var4": {
                        "num_var5": 15,
                    },
                    "num_var6": -1,
                    "num_var7": -1,
                    "num_var8": 0,
                    "num_var9": {
                        "num_var10": 15,
                    },
                    "bool_var1": False,
                    "bool_var2": True,
                    "bool_var3": {
                        "bool_var4": False,
                    },
                    "bool_var5": False,
                    "bool_var6": True,
                    "bool_var7": {
                        "bool_var8": False,
                    },
                    },

    }


def test_validate_data_returns_true_with_valid_data(mocker: MockerFixture,
                                                    mock_input_manager: InputManager,
                                                    mock_metadata: Dict[str, Dict[str, Any]],
                                                    mock_pool: Dict[str, Dict[str, Any]],
                                                    ) -> None:
    """Unit test for valid data for function _validate_data in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata
    mock_input_manager._InputManager__pool = mock_pool
    mocker.patch.object(mock_input_manager, "_validate_element", return_value=True)

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        result = mock_input_manager._validate_data(eager_termination=True)

    assert result is True
    assert add_log.call_count == 3


def test_validate_data_returns_false_with_unfixable_invalid_data(mocker: MockerFixture,
                                                                 mock_input_manager: InputManager,
                                                                 mock_metadata: Dict[str, Dict[str, Any]],
                                                                 mock_pool: Dict[str, Dict[str, Any]],
                                                                 ) -> None:
    """Unit test for invalid unfixable data for function _validate_data in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata
    mock_input_manager._InputManager__pool = mock_pool

    mocker.patch.object(mock_input_manager, "_validate_element", return_value=False)

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        result = mock_input_manager._validate_data(eager_termination=True)

    assert result is False
    assert add_log.call_count == 0  # will reach eager_termination prior to adding logs


def test_validate_data_returns_false_with_invalid_data_no_eager_termination(mocker: MockerFixture,
                                                                            mock_input_manager: InputManager,
                                                                            mock_metadata: Dict[str, Dict[str, Any]],
                                                                            mock_pool: Dict[str, Dict[str, Any]],
                                                                            ) -> None:
    """Unit test for no eager termination with non-critical
    invalid data for function _validate_data in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata
    mock_input_manager._InputManager__pool = mock_pool
    mocker.patch.object(mock_input_manager, "_validate_element", return_value=False)

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        result = mock_input_manager._validate_data(eager_termination=False)

    assert result is False
    assert add_log.call_count == 3


def test_validate_element_valid_element_returns_true(mocker: MockerFixture,
                                                     mock_input_manager: InputManager,
                                                     mock_metadata: Dict[str, Dict[str, Any]],
                                                     mock_pool: Dict[str, Dict[str, Any]],
                                                     ) -> None:
    """Unit test for function _validate_element function with valid element in file input_manager.py"""
    dummy_module_key = "animal"
    dummy_valid_element = "animal_var1"
    dummy_property_map_key = "animal_properties"
    mock_input_manager._InputManager__metadata = mock_metadata
    mock_input_manager._InputManager__pool = mock_pool
    eager_termination = True

    result = mock_input_manager._validate_element(dummy_module_key, dummy_valid_element,
                                                  dummy_property_map_key, eager_termination)

    assert result is True


def test_validate_element_unfixable_invalid_element_returns_false(mocker: MockerFixture,
                                                                  mock_input_manager: InputManager,
                                                                  mock_metadata: Dict[str, Dict[str, Any]],
                                                                  mock_pool: Dict[str, Dict[str, Any]],
                                                                  ) -> None:
    """Unit test for function _validate_element function with invalid element in file input_manager.py"""
    dummy_module_key = "animal"
    dummy_valid_element = "animal_var1"
    dummy_property_map_key = "animal_properties"
    mock_input_manager._InputManager__metadata = mock_metadata
    mock_input_manager._InputManager__pool = mock_pool
    mocker.patch.object(mock_input_manager, "_validate_string_type_element", return_value=False)
    mocker.patch.object(mock_input_manager, "_fix_data", return_value=False)
    eager_termination = True

    result = mock_input_manager._validate_element(dummy_module_key, dummy_valid_element,
                                                  dummy_property_map_key, eager_termination)

    assert result is False


def test_validate_element_with_element_no_type_or_bad_type_raises_exception(mocker: MockerFixture,
                                                                            mock_input_manager: InputManager,
                                                                            mock_metadata: Dict[str, Dict[str, Any]],
                                                                            mock_pool: Dict[str, Dict[str, Any]],
                                                                            ) -> None:
    """Unit test for function _validate_element function with invalid element in file input_manager.py"""
    dummy_module_key = "animal"
    dummy_valid_element = "animal_var1"
    dummy_property_map_key = "animal_properties"
    mock_input_manager._InputManager__metadata = mock_metadata
    mock_input_manager._InputManager__pool = mock_pool
    eager_termination = True

    # set type to empty string
    mock_metadata["properties"]["animal_properties"]["animal_var1"]["type"] = ""

    with pytest.raises(Exception):
        mock_input_manager._validate_element(dummy_module_key, dummy_valid_element,
                                             dummy_property_map_key, eager_termination)
        error_message = "Element must be type number, array, string, or bool"
        assert error_message in Exception.message

    # update type to unsupported type
    mock_metadata["properties"]["animal_properties"]["animal_var1"]["type"] = "dict"

    with pytest.raises(Exception):
        mock_input_manager._validate_element(dummy_module_key, dummy_valid_element,
                                             dummy_property_map_key, eager_termination)
        error_message = "Element must be type number, array, string, or bool"
        assert error_message in Exception.message


def test_validate_element_with_element_not_in_pool_raises_exception(mocker: MockerFixture,
                                                                    mock_input_manager: InputManager,
                                                                    mock_metadata: Dict[str, Dict[str, Any]],
                                                                    mock_pool: Dict[str, Dict[str, Any]],
                                                                    ) -> None:
    """Unit test for function _validate_element function with element missing from pool in file input_manager.py"""
    dummy_module_key = "animal"
    dummy_valid_element = "animal_var1"
    dummy_property_map_key = "animal_properties"
    mock_input_manager._InputManager__metadata = mock_metadata
    mock_input_manager._InputManager__pool = mock_pool
    eager_termination = True
    var_name = "crop_var1"

    # remove crop_var1 variable from mock_pool
    mock_pool["crop"] = {"crop_var2": "dummyvalue6",
                         "crop_var3": {"crop_nested1": "dummyvalue3"},
                         },

    with pytest.raises(Exception) as KeyError:
        mock_input_manager._validate_element(dummy_module_key, dummy_valid_element,
                                             dummy_property_map_key, eager_termination)
        error_message = f"Key {var_name} not found in pool"
        assert error_message in KeyError


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
