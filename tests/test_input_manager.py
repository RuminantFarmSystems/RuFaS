"""
RUFAS: Ruminant Farm Systems Model
File name: test_input_manager.py
Description: Implements test cases for Input Manager
Author(s): Niko Tomlinson, ndt2@cornell.edu
"""

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

    with patch("builtins.open", mock_open(read_data="key,value\na,1\nb,2\n")):
        mock_input_manager._load_data()
    assert mock_input_manager._InputManager__pool == {"dummy_data_file": [{"key": "a", "value": "1"},
                                                                          {"key": "b", "value": "2"}]}


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
        add_warning.assert_called_once_with(
            "InputManager load data file is not csv/json",
            "File for dummy_data_file data in path dummy_data.txt was not a csv nor json file and was not added to data pool",
            {"class": "InputManager", "function": "_load_data"}
            )


def test_load_data_raises_exception(mock_input_manager: InputManager) -> None:
    """Unit test for function _load_data raising an exception in file input_manager.py"""
    mock_open_func = Mock()
    mock_open_func.side_effect = Exception("Error opening file")

    with patch("builtins.open", mock_open_func):
        with pytest.raises(Exception):
            mock_input_manager._load_data("bad/path.csv")
