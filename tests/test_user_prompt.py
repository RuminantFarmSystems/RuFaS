import os.path
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from config import global_variables
from RUFAS.user_prompt import get_json_list_from_dir
from RUFAS.user_prompt import obtain_file_list

dir_path = os.path.join(global_variables.ROOT_DIR, "input")
file_path = os.path.join(dir_path, "input/ARL.json")


# TODO: Tests remain unimplemented - GitHub Issue #209

@pytest.mark.parametrize("path", [file_path, None])
def test_obtain_file_list(mocker: MockerFixture, path):
    """check that obtain_file_list correctly calls input_prompt or convert_path_string_to_list"""
    # Arrange
    verbose = True
    patch_for_user_prompt = mocker.patch("RUFAS.user_prompt.user_prompt")
    patch_for_convert_path_string_to_list = mocker.patch("RUFAS.user_prompt.convert_path_string_to_list",
                                                         return_value=[path])

    # Act
    obtain_file_list(path, verbose)

    # Assert
    if path is None:
        patch_for_user_prompt.assert_called_once()
        patch_for_convert_path_string_to_list.assert_not_called()
    else:
        patch_for_convert_path_string_to_list.assert_called_once()
        patch_for_user_prompt.assert_not_called()


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


def test_get_json_list_from_dir(mocker: MockerFixture,
                                capsys: pytest.CaptureFixture):
    """check that get_json_list_from_dir() properly detects all json files in a directory"""
    verbose = True

    # Case 1: Input path is not a directory
    # Arrange
    dummy_path = Path('dummy_path')

    # Act
    # check an error is raised
    with pytest.raises(IsADirectoryError) as e:
        get_json_list_from_dir(dummy_path, verbose)
        assert "specified path is not a directory" in str(e.value)

    # ------------------------------

    # Case 2: Input path is a directory, but contains no json files
    # Arrange
    # Print current directory
    dummy_dir = Path('dummy_dir')
    dummy_dir.mkdir()
    empty_json_paths = []
    patch_for_glob = mocker.patch("RUFAS.user_prompt.Path.glob", return_value=empty_json_paths)

    # Act
    with pytest.raises(FileExistsError) as e:
        get_json_list_from_dir(dummy_dir, verbose)
        assert "Directory contains no json files" in str(e.value)

    # Assert
    patch_for_glob.assert_called_once_with('*.json')

    # Cleanup
    dummy_dir.rmdir()

    # ------------------------------

    # Case 3: Input path is a directory, and contains json files
    # Arrange
    dummy_dir = Path('dummy_dir')
    dummy_dir.mkdir()
    expected_json_paths = ['dummy.json', 'dummy2.json']
    patch_for_glob = mocker.patch("RUFAS.user_prompt.Path.glob", return_value=expected_json_paths)

    # Act
    actual_json_paths = get_json_list_from_dir(dummy_dir, verbose)

    # Assert
    patch_for_glob.assert_called_once_with('*.json')
    captured = capsys.readouterr()
    assert f'{len(expected_json_paths)} json files detected...' in captured.out
    assert actual_json_paths == expected_json_paths

    # Cleanup
    dummy_dir.rmdir()


@pytest.mark.parametrize("path", [file_path])
def test_convert_json_path_to_list(path):
    """check that convert_json_path_to_list() properly returns a Path list from a json path string"""
    pass


@pytest.mark.parametrize("input", ["Q", "q", "dir", file_path, dir_path])
def test_prompt_user_for_input(input):
    """check that prompt_user_for_input correctly returns the users input and that other options work as expected"""
    pass
