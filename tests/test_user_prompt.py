import os.path

import pytest
import unittest.mock

from RUFAS.user_prompt import *

dir_path = os.path.join(config.global_variables.ROOT_DIR, "input")
file_path = os.path.join(dir_path, "input/ARL.json")

# TODO: Tests remain unimplemented - GitHub Issue #209

@pytest.mark.parametrize("path", [file_path, None])
def test_obtain_file_list(path):
    """check that obtain_file_list correctly calls input_prompt or convert_path_string_to_list"""
    pass

@pytest.mark.parametrize("path", [file_path, dir_path])
def test_convert_path_string_to_list(path):
    """check that convert_path_string_to_list provides correct file lists"""
    pass

@pytest.mark.parametrize("user_input", [file_path, dir_path])
def test_user_prompt(user_input):
    """check that user_prompt() correctly accepts user input and returns a Path list"""
    pass

@pytest.mark.parametrize("path", [file_path, dir_path])
def test_convert_path_string_to_list(path):
    """check that convert_path_string_to_list() properly returns a Path list"""
    pass

@pytest.mark.parametrize("path", [dir_path])
def test_get_json_list_from_dir(path):
    """check that get_json_list_from_dir() properly detects all json files in a directory"""
    pass

@pytest.mark.parametrize("path", [file_path])
def test_convert_json_path_to_list(path):
    """check that convert_json_path_to_list() properly returns a Path list from a json path string"""
    pass

@pytest.mark.parametrize("input", ["Q", "q", "dir", file_path, dir_path])
def test_prompt_user_for_input(input):
    """check that prompt_user_for_input correctly returns the users input and that other options work as expected"""
    pass

