"""
RUFAS: Ruminant Farm Systems Model
File name: test_input_manager.py
Description: Implements test cases for Input Manager
Author(s): Niko Tomlinson, ndt2@cornell.edu
"""

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
