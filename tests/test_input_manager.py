"""
RUFAS: Ruminant Farm Systems Model
File name: test_input_manager.py
Description: Implements test cases for Input Manager
Author(s): Niko Tomlinson, ndt2@cornell.edu
"""

from typing import Any, Dict
from mock import Mock, mock_open, patch
import pytest
from pytest_mock import MockerFixture

from RUFAS.input_manager import InputManager


@pytest.fixture
def mock_input_manager(mocker) -> InputManager:
    input_manager = InputManager()
    return input_manager


def test_input_manager_singleton(mocker: MockerFixture) -> None:
    """Unit test to ensure InputManager is a singleton"""
    im1 = InputManager()
    im2 = InputManager()

    assert im1 is im2


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


@pytest.fixture
def mock_metadata(mocker) -> Dict[str, Dict[str, Any]]:
    return {
            "dummyconfig": {},
            "files": {
                "animal": {"properties": "animal_properties"},
                "manure": {"properties": "manure_properties"},
                "crop": {"properties": "crop_properties"},
                },
            "properties": {
                "animal_properties": {"animal_var1": {"default": "dummyvalue1"},
                                      "animal_var2": {"default": "dummyvalue2"}
                                      },
                "manure_properties": {"manure_var1": {"default": "dummyvalue1"},
                                      "manure_var2": {"default": "dummyvalue2"},
                                      },
                "crop_properties": {"crop_var1": {"default": "dummyvalue1"},
                                    "crop_var2": {"default": "dummyvalue2"},
                                    }
                }
            }


@pytest.fixture
def mock_pool(mocker) -> Dict[str, Dict[str, Any]]:
    return {
            "animal": {"animal_var1": "dummyvalue1",
                       "animal_var2": "dummyvalue2"
                       },
            "manure": {"manure_var1": "dummyvalue3",
                       "manure_var2": "dummyvalue4"
                       },
            "crop": {"crop_var1": "dummyvalue5",
                     "crop_var2": "dummyvalue6"
                     },
            }


def test_validate_data_returns_true_with_valid_data(mocker, mock_input_manager: InputManager,
                                                    mock_metadata: Dict[str, Dict[str, Any]],
                                                    mock_pool: Dict[str, Dict[str, Any]]
                                                    ) -> None:
    """Unit test for valid data for function _validate_data in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata
    mock_input_manager._InputManager__pool = mock_pool
    mocker.patch.object(mock_input_manager, "_validate_element", return_value=True)

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        result = mock_input_manager._validate_data()

    assert result is True
    assert add_log.call_count == 5


def test_validate_data_returns_false_with_unfixable_invalid_data(mocker, mock_input_manager: InputManager,
                                                                 mock_metadata: Dict[str, Dict[str, Any]],
                                                                 mock_pool: Dict[str, Dict[str, Any]]
                                                                 ) -> None:
    """Unit test for invalid unfixable data for function _validate_data in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata
    mock_input_manager._InputManager__pool = mock_pool

    mocker.patch.object(mock_input_manager, "_validate_element", return_value=False)
    mocker.patch.object(mock_input_manager, "_fix_data", return_value=False)

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        result = mock_input_manager._validate_data()

    assert result is False
    assert add_log.call_count == 0  # will reach eager_termination prior to adding logs


def test_validate_data_returns_true_with_fixable_invalid_data(mocker, mock_input_manager: InputManager,
                                                              mock_metadata: Dict[str, Dict[str, Any]],
                                                              mock_pool: Dict[str, Dict[str, Any]]
                                                              ) -> None:
    """Unit test for invalid fixable data for function _validate_data in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata
    mock_input_manager._InputManager__pool = mock_pool
    mocker.patch.object(mock_input_manager, "_validate_element", return_value=False)
    mocker.patch.object(mock_input_manager, "_fix_data", return_value=True)

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        result = mock_input_manager._validate_data()

    assert result is True
    assert add_log.call_count == 5


def test_validate_data_returns_true_with_invalid_data_no_eager_termination(mocker, mock_input_manager: InputManager,
                                                                           mock_metadata: Dict[str, Dict[str, Any]],
                                                                           mock_pool: Dict[str, Dict[str, Any]]
                                                                           ) -> None:
    """Unit test for no eager termination with non-critical
    invalid data for function _validate_data in file input_manager.py"""
    mock_input_manager._InputManager__metadata = mock_metadata
    mock_input_manager._InputManager__pool = mock_pool
    mocker.patch.object(mock_input_manager, "_validate_element", return_value=False)
    mocker.patch.object(mock_input_manager, "_fix_data", return_value=True)

    with patch("RUFAS.output_manager.OutputManager.add_log") as add_log:
        result = mock_input_manager._validate_data(eager_termination=False)

    assert result is True
    assert add_log.call_count == 5
