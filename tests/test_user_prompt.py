import argparse
import os.path
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

import config.global_variables
from config import global_variables
from main import execute_simulations_from_files
from main import parse_gnu_args
from main import run_rufas
from main import set_global_variables
from RUFAS import errors
from RUFAS import SimulationEngine
from RUFAS.output_manager import OutputManager
from RUFAS.user_prompt import convert_json_path_to_list
from RUFAS.user_prompt import convert_path_string_to_list
from RUFAS.user_prompt import get_json_list_from_dir
from RUFAS.user_prompt import obtain_file_list
from RUFAS.user_prompt import prompt_user_for_input
from RUFAS.user_prompt import user_prompt

dir_path = os.path.join(global_variables.ROOT_DIR, "input")
file_path = os.path.join(dir_path, "input/ARL.json")


@pytest.mark.parametrize("path", [file_path, None])
def test_obtain_file_list(mocker: MockerFixture, path):
    """check that obtain_file_list correctly calls input_prompt or convert_path_string_to_list"""
    # Arrange
    verbose = True
    patch_for_user_prompt = mocker.patch("RUFAS.user_prompt.user_prompt")
    patch_for_convert_path_string_to_list = mocker.patch(
        "RUFAS.user_prompt.convert_path_string_to_list", return_value=[path]
    )

    # Act
    obtain_file_list(path, verbose)

    # Assert
    if path is None:
        patch_for_user_prompt.assert_called_once()
        patch_for_convert_path_string_to_list.assert_not_called()
    else:
        patch_for_convert_path_string_to_list.assert_called_once()
        patch_for_user_prompt.assert_not_called()


@pytest.mark.parametrize(
    "path, is_file, is_dir",
    [
        ("dummy_json.json", True, False),
        ("dummy_dir", False, True),
        ("valid_dummy_txt_file.txt", True, False),
        ("invalid_dummy_txt_file.txt", False, False),
        ("invalid_file_path", False, False),
    ],
)
def test_convert_path_string_to_list(
    path: str,
    is_file: bool,
    is_dir: bool,
    mocker: MockerFixture,
    capsys: pytest.CaptureFixture,
):
    """check that convert_path_string_to_list provides correct file lists"""
    # Arrange
    input_path = mocker.MagicMock(auto_spec=Path)
    input_path.__str__.return_value = path
    input_path.is_dir.return_value = is_dir
    input_path.is_file.return_value = is_file
    input_path.suffix = "." + path.split(".")[-1]
    verbose = True
    json_filename = "dummy.json"
    patch_for_path_init = mocker.patch(
        "RUFAS.user_prompt.Path", side_effect=[input_path, input_path]
    )
    patch_for_convert_to_json = mocker.patch(
        "RUFAS.user_prompt.fileReader.convert_to_json", return_value=json_filename
    )
    patch_for_convert_json_path_to_list = mocker.patch(
        "RUFAS.user_prompt.convert_json_path_to_list", return_value=[input_path]
    )
    patch_for_get_json_list_from_dir = mocker.patch(
        "RUFAS.user_prompt.get_json_list_from_dir", return_value=[json_filename]
    )
    patch_for_builtin_warning = mocker.patch("builtins.Warning")

    # Act
    if not is_file and not is_dir:
        if input_path.suffix == ".txt":
            with pytest.raises(errors.UserInput) as e:
                convert_path_string_to_list(path, verbose)
                assert "does not exist" in str(e.value)
        else:
            with pytest.raises(ValueError) as e:
                convert_path_string_to_list(path, verbose)
                assert "Invalid input path" in str(e.value)
        return

    actual_file_list = convert_path_string_to_list(path, verbose)

    # Assert
    if is_dir:
        patch_for_path_init.assert_called_once_with(path)
        input_path.is_dir.assert_called_once()
        patch_for_get_json_list_from_dir.assert_called_once_with(input_path, verbose)
    elif input_path.suffix == ".txt":
        patch_for_builtin_warning.assert_called_once()
        input_path.is_file.assert_called_once()
        patch_for_convert_to_json.assert_called_once_with(str(input_path))
        assert actual_file_list == [input_path]
        if verbose:
            captured = capsys.readouterr()
            assert "commented json file detected, stripping comments" in captured.out
    elif input_path.suffix == ".json":
        patch_for_path_init.assert_called_once_with(path)
        patch_for_convert_json_path_to_list.assert_called_once_with(input_path, verbose)


@pytest.mark.parametrize("user_input", [file_path, dir_path])
def test_user_prompt(user_input: str, mocker: MockerFixture):
    """check that user_prompt() correctly accepts user input and returns a Path list"""
    # Arrange
    patch_for_prompt_user_for_input = mocker.patch(
        "RUFAS.user_prompt.prompt_user_for_input", return_value=user_input
    )
    patch_for_convert_path_string_to_list = mocker.patch(
        "RUFAS.user_prompt.convert_path_string_to_list", return_value=[user_input]
    )

    # Act
    actual = user_prompt()

    # Assert
    patch_for_prompt_user_for_input.assert_called_once()
    patch_for_convert_path_string_to_list.assert_called_once_with(path=user_input)
    assert actual == [user_input]


def test_get_json_list_from_dir(mocker: MockerFixture, capsys: pytest.CaptureFixture):
    """check that get_json_list_from_dir() properly detects all json files in a directory"""
    verbose = True

    # Case 1: Input path is not a directory
    # Arrange
    mock_dir_path = mocker.MagicMock(auto_spec=Path)
    mock_dir_path.is_dir.return_value = False

    # Act
    # check an error is raised
    with pytest.raises(IsADirectoryError) as e:
        get_json_list_from_dir(mock_dir_path, verbose)
        assert "specified path is not a directory" in str(e.value)

    # ------------------------------

    # Case 2: Input path is a directory, but contains no json files
    # Arrange
    mock_dir_path = mocker.MagicMock(auto_spec=Path)
    mock_dir_path.is_dir.return_value = True
    mock_dir_path.glob.return_value = []

    # Act
    with pytest.raises(FileExistsError) as e:
        get_json_list_from_dir(mock_dir_path, verbose)
        assert "Directory contains no json files" in str(e.value)

    # Assert
    mock_dir_path.is_dir.assert_called_once()
    mock_dir_path.glob.assert_called_once_with("*.json")

    # ------------------------------

    # Case 3: Input path is a directory, and contains json files
    # Arrange
    mock_dir_path = mocker.MagicMock(auto_spec=Path)
    mock_dir_path.is_dir.return_value = True
    expected_json_paths = ["dummy.json", "dummy2.json"]
    mock_dir_path.glob.return_value = expected_json_paths

    # Act
    actual_json_paths = get_json_list_from_dir(mock_dir_path, verbose)

    # Assert
    mock_dir_path.glob.assert_called_once_with("*.json")
    captured = capsys.readouterr()
    assert f"{len(expected_json_paths)} json files detected..." in captured.out
    assert actual_json_paths == expected_json_paths


def test_convert_json_path_to_list(
    mocker: MockerFixture, capsys: pytest.CaptureFixture
):
    """check that convert_json_path_to_list() properly returns a Path list from a json path string"""
    # Case 1: Input path is not a json file
    # Arrange
    mock_json_path = mocker.MagicMock(auto_spec=Path)
    mock_json_path.is_file.return_value = False
    verbose = True

    # Act
    with pytest.raises(errors.UserInput) as e:
        convert_json_path_to_list(mock_json_path, verbose)
        assert "Specified file does not exist" in str(e.value)

    # ------------------------------

    # Case 2: Input path is a json file
    # Arrange
    mock_json_path = mocker.MagicMock(auto_spec=Path)
    mock_json_path.is_file.return_value = True
    verbose = True

    # Act
    actual = convert_json_path_to_list(mock_json_path, verbose)

    # Assert
    mock_json_path.is_file.assert_called_once()
    captured = capsys.readouterr()
    assert "json file detected" in captured.out
    assert actual == [mock_json_path]


@pytest.mark.parametrize("user_input", ["Q", "q", file_path, dir_path, "dir", "error"])
def test_prompt_user_for_input(
    mocker: MockerFixture, capsys: pytest.CaptureFixture, user_input: str
) -> None:
    """check that prompt_user_for_input correctly returns the users input and that other options work as expected"""

    # Arrange
    def mock_user_input_error_side_effect(*args, **kwargs):
        raise errors.UserInput("test error")

    side_effect_by_user_input = {
        "dir": ["dir", "Q"],
        "error": mock_user_input_error_side_effect,
    }
    patch_for_input = mocker.patch(
        "builtins.input",
        side_effect=side_effect_by_user_input.get(user_input, [user_input]),
    )

    patch_for_exit = mocker.patch("sys.exit")
    current_dir_path = Path.cwd()
    patch_for_get_base_dir = mocker.patch(
        "RUFAS.user_prompt.Utility.get_base_dir", return_value=current_dir_path
    )

    # Act
    actual_user_input = prompt_user_for_input()

    # Assert
    captured = capsys.readouterr().out.split("\n")

    if user_input in ["Q", "q"]:
        patch_for_input.assert_called_once_with("\nEnter RUFAS Input: ")
        patch_for_exit.assert_called_once()
        assert "Exiting RUFAS..." in captured
    elif user_input == "dir":
        assert patch_for_input.call_count == 2
        patch_for_get_base_dir.assert_called_once()
        patch_for_exit.assert_called_once()
        assert "Exiting RUFAS..." in captured
        assert str(current_dir_path) in captured
    elif user_input == "error":
        assert "USER INPUT ERROR: test error" in captured
    else:
        patch_for_input.assert_called_once_with("\nEnter RUFAS Input: ")
        assert actual_user_input == "input/" + user_input


@pytest.mark.parametrize(
    "input_path, make_graphs, verbose, clear_output, exclude_info_maps",
    [
        ("dummy_path", True, True, True, True),
        ("dummy_path", False, True, True, True),
        ("dummy_path", True, False, True, True),
        ("dummy_path", False, False, True, True),
        ("dummy_path", False, False, False, True),
        ("dummy_path", False, False, True, False),
        ("dummy_path", False, False, False, False),
        ("dummy_path", True, True, False, False),
    ],
)
def test_run_rufas(
    input_path: str,
    make_graphs: bool,
    verbose: bool,
    clear_output: bool,
    exclude_info_maps: bool,
    mocker: MockerFixture,
) -> None:
    """Checks that run_rufas() calls the correct functions in the correct order"""
    # Arrange
    patch_set_global_variables = mocker.patch("main.set_global_variables")
    file_list = ["file1.json", "file2.json"]
    patch_obtain_file_list = mocker.patch(
        "main.obtain_file_list", return_value=file_list
    )
    patch_execute_simulations_from_files = mocker.patch(
        "main.execute_simulations_from_files"
    )
    patch_empty_dir = mocker.patch("RUFAS.util.Utility.empty_dir")

    # Act
    run_rufas(input_path, make_graphs, verbose, clear_output, exclude_info_maps)

    # Assert
    patch_set_global_variables.assert_called_once_with(make_graphs, verbose)
    patch_obtain_file_list.assert_called_once_with(input_path, verbose)
    patch_execute_simulations_from_files.assert_called_once_with(
        file_list, exclude_info_maps
    )
    if clear_output:
        patch_empty_dir.assert_called_once()
    else:
        patch_empty_dir.assert_not_called()


@pytest.mark.parametrize(
    "make_graphs, verbose", [(True, True), (False, True), (True, False), (False, False)]
)
def test_set_global_variables(make_graphs: bool, verbose: bool) -> None:
    """Checks that set_global_variables() sets the global variables correctly"""
    # Arrange
    old_make_graphs = config.global_variables.PRODUCE_GRAPHICS
    old_verbose = config.global_variables.PRINT_STATUS_MESSAGES

    # Act
    set_global_variables(make_graphs, verbose)

    # Assert
    assert config.global_variables.PRODUCE_GRAPHICS == make_graphs
    assert config.global_variables.PRINT_STATUS_MESSAGES == verbose

    # Cleanup
    config.global_variables.PRODUCE_GRAPHICS = old_make_graphs
    config.global_variables.PRINT_STATUS_MESSAGES = old_verbose


def test_execute_simulations_from_files(mocker: MockerFixture) -> None:
    """Checks that execute_simulations_from_files() calls the correct functions in the correct order"""
    # Arrange
    mock_output_manager = mocker.MagicMock(auto_spec=OutputManager)
    mock_output_manager.flush_pools.return_value = None
    mock_output_manager.dump_all_pools.return_value = None
    mock_output_manager.save_variables.return_value = None
    mocker.patch("main.OutputManager", return_value=mock_output_manager)
    file_path1 = Path("file1.json")
    file_path2 = Path("file2.json")
    file_list = [file_path1, file_path2]
    mock_simulator = mocker.MagicMock(auto_spec=SimulationEngine)
    mock_simulator.simulate.return_value = None
    patch_for_simulation_engine_init = mocker.patch(
        "main.SimulationEngine", return_value=mock_simulator
    )

    # Act
    execute_simulations_from_files(file_list, True)

    # Assert
    assert patch_for_simulation_engine_init.call_count == len(file_list)
    assert patch_for_simulation_engine_init.call_args_list == [
        mocker.call(file_path1),
        mocker.call(file_path2),
    ]
    assert mock_simulator.simulate.call_count == len(file_list)
    assert mock_output_manager.flush_pools.call_count == len(file_list)
    assert mock_output_manager.dump_all_pools.call_count == len(file_list)
    assert mock_output_manager.dump_all_pools.call_args_list == [
        mocker.call("output", True)
    ] * len(file_list)
    assert mock_output_manager.save_variables.call_count == len(file_list)
    assert mock_output_manager.save_variables.call_args_list == [
        mocker.call("output", "input/output_filters/", True)
    ] * len(file_list)


def test_parse_gnu_args(mocker: MockerFixture) -> None:
    """Checks that parse_gnu_args() correctly parses the user's input."""
    # Arrange
    mock_parser = mocker.MagicMock(auto_spec=argparse.ArgumentParser)
    mock_add_argument = mocker.patch.object(mock_parser, "add_argument")
    mock_parse_args = mocker.patch.object(
        mock_parser, "parse_args", return_value="test_args"
    )
    mocker.patch("main.argparse.ArgumentParser", return_value=mock_parser)

    # Act
    actual_args = parse_gnu_args()

    # Assert
    assert mock_add_argument.call_count == 5
    assert mock_add_argument.call_args_list == [
        mocker.call(
            "input_path",
            type=str,
            metavar="path",
            nargs="?",
            help="path to input .json file or directory of .json files",
        ),
        mocker.call(
            "-ng",
            "--no-graphics",
            help="Prevent graphics from generating",
            action="store_true",
        ),
        mocker.call(
            "-v",
            "--verbose",
            help="Print progress messages while simulation is running",
            action="store_true",
        ),
        mocker.call(
            "-co",
            "--clear-output",
            help="Clear output directory before running the simulation",
            action="store_true",
        ),
        mocker.call(
            "-ei",
            "--exclude_info_maps",
            help="Exclude info_maps from the output",
            action="store_true",
        ),
    ]
    mock_parse_args.assert_called_once()
    assert actual_args == "test_args"
