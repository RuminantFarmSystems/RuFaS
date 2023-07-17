"""
RUFAS: Ruminant Farm Systems Model
File name: test_input_manager.py
Description: Implements test cases for Input Manager
Author(s): Niko Tomlinson, ndt2@cornell.edu
"""

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
        "start_data_pipeline": mock_input_manager.start_data_pipeline,
        "_load_metadata": mock_input_manager._load_metadata,
        "_load_data": mock_input_manager._load_data,
        "_validate_data": mock_input_manager._validate_data,
        "_validate_element": mock_input_manager._validate_element,
        "_validate_array_type_element": mock_input_manager._validate_array_type_element,
        "_validate_bool_type_element": mock_input_manager._validate_bool_type_element,
        "_validate_num_type_element": mock_input_manager._validate_num_type_element,
        "_validate_string_type_element": mock_input_manager._validate_string_type_element,
    }


def test_load_metadata(mock_input_manager: InputManager) -> None:
    """Unit test for function _load_metadata in file input_manager.py"""
    with patch("builtins.open", mock_open(read_data='{"dummy_key1": "dummy_value1", "dummy_key2": "dummy_value2"}')):
        mock_input_manager._load_metadata("path/dummy_metadata.json")
        assert mock_input_manager._InputManager__metadata == {"dummy_key1": "dummy_value1",
                                                              "dummy_key2": "dummy_value2"}


def test_load_metadata_raises_exception(mock_input_manager: InputManager) -> None:
    """Unit test for function _load_metadata raising an exception in file input_manager.py"""
    mock_open_func = Mock()
    mock_open_func.side_effect = Exception("Error opening file")

    with patch("builtins.open", mock_open_func):
        with pytest.raises(Exception):
            mock_input_manager._load_metadata("path/dummy_metadata.json")


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
        mock_input_manager._load_data()
    assert mock_input_manager._InputManager__pool == {"dummy_data_file": {"key": "value"}}


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
        mock_input_manager._load_data()
    assert mock_input_manager._InputManager__pool == {"dummy_data_file": {"key1": ["a", "b"],
                                                                          "key2": [1, 2]}}


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
            mock_input_manager._load_data()
        assert mock_input_manager._InputManager__pool == {}
        assert add_warning.call_count == 1


def test_load_data_raises_exception(mock_input_manager: InputManager) -> None:
    """Unit test for function _load_data raising an exception in file input_manager.py"""
    mock_open_func = Mock()
    mock_open_func.side_effect = Exception("Error opening file")

    with patch("builtins.open", mock_open_func):
        with pytest.raises(Exception):
            mock_input_manager._load_data("bad/path.csv")


def test_start_data_pipeline(mock_input_manager: InputManager,
                             input_manager_original_method_states: Dict[str, Callable],) -> None:
    """Unit test for function start_data_pipeline in file input_manager.py"""
    mock_input_manager._load_metadata = MagicMock()
    mock_input_manager._load_data = MagicMock()
    mock_input_manager._validate_data = MagicMock(return_value=True)

    mock_input_manager.start_data_pipeline()

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
                },
            "properties": {
                "animal_properties": {"animal_var1": {"default": "dummyvalue1"},
                                      "animal_var2": {"default": "dummyvalue2"},
                                      "animal_var3": {"animal_nested1": {"default": "dummyvalue3"}}
                                      },
                "manure_properties": {"manure_var1": {"default": "dummyvalue1"},
                                      "manure_var2": {"default": "dummyvalue2"},
                                      "manure_var3": {"manure_nested1": {"default": "dummyvalue3"}},
                                      },
                "crop_properties": {"crop_var1": {"default": "dummyvalue1"},
                                    "crop_var2": {"default": "dummyvalue2"},
                                    "crop_var3": {"crop_nested1": {"default": "dummyvalue3"}},
                                    }
                }
            }


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
            }


def test_validate_data_returns_true_with_valid_data(mocker, mock_input_manager: InputManager,
                                                    mock_metadata: Dict[str, Dict[str, Any]],
                                                    mock_pool: Dict[str, Dict[str, Any]],
                                                    ) -> None:
    """Unit test for valid data for function _validate_data in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata
    mock_input_manager._InputManager__pool = mock_pool
    mocker.patch.object(mock_input_manager, "_validate_element", return_value=True)

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        result = mock_input_manager._validate_data()

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
        result = mock_input_manager._validate_data()

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
    mocker.patch.object(mock_input_manager, "_check_variable_nested", return_value=False)
    mocker.patch.object(mock_input_manager, "_get_variable_type", return_value="string")
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
    mocker.patch.object(mock_input_manager, "_check_variable_nested", return_value=False)
    mocker.patch.object(mock_input_manager, "_get_variable_type", return_value="number")
    mocker.patch.object(mock_input_manager, "_validate_num_type_element", return_value=False)
    mocker.patch.object(mock_input_manager, "_fix_data", return_value=False)
    eager_termination = True

    result = mock_input_manager._validate_element(dummy_module_key, dummy_valid_element,
                                                  dummy_property_map_key, eager_termination)

    assert result is False


def test_validate_element_with_element_no_type_returns_false(mocker: MockerFixture,
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
    mocker.patch.object(mock_input_manager, "_check_variable_nested", return_value=False)
    mocker.patch.object(mock_input_manager, "_get_variable_type", return_value=None)
    eager_termination = True

    result = mock_input_manager._validate_element(dummy_module_key, dummy_valid_element,
                                                  dummy_property_map_key, eager_termination)

    assert result is False


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
    'dummy_bool_value, expected_result',
    [
        (True, True),
        (False, True),
        ('', False)
    ]
)
def test_validate_bool_type_element(dummy_bool_value: bool,
                                    expected_result: bool,
                                    mock_input_manager: InputManager) -> None:
    """Unit test for function _validate_bool_type_element function in file input_manager.py"""
    result = mock_input_manager._validate_bool_type_element(dummy_bool_value)

    assert result == expected_result


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
