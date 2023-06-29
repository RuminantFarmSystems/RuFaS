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
    im1 = InputManager()
    im2 = InputManager()

    assert im1 is im2


def test_load_metadata(mock_input_manager: InputManager) -> None:
    with patch("builtins.open", mock_open(read_data='{"dummy_key1": "dummy_value1"}')):
        mock_input_manager._load_metadata("input/example_metadata.json")
        assert mock_input_manager.metadata == {"dummy_key1": "dummy_value1"}

    mock_open_func = Mock()
    mock_open_func.side_effect = Exception("Error opening file")

    with patch("builtins.open", mock_open_func):
        with pytest.raises(Exception):
            mock_input_manager._load_metadata("input/example_metadata.json")
