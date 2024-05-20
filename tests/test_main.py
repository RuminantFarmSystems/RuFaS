import argparse
from pathlib import Path
import sys
import pytest
from mock import patch
from pytest_mock import MockerFixture

from main import CaseInsensitiveArgumentAction, main, parse_gnu_args
from RUFAS.output_manager import LogVerbosity


@pytest.fixture
def mock_task_manager():
    with patch("main.TaskManager") as mock:
        yield mock


def test_main_success(mock_task_manager, monkeypatch):
    mock_instance = mock_task_manager.return_value
    mock_instance.start.return_value = None

    # Simulating command line arguments
    test_args = ["program_name", "-v", "errors", "-o", "output/"]
    monkeypatch.setattr(sys, "argv", test_args)

    main()

    mock_instance.start.assert_called_once_with(
        Path("input/metadata/task_manager_metadata.json"),
        verbosity=LogVerbosity.ERRORS,
        exclude_info_maps=False,
        output_directory=Path("output"),
        clear_output_directory=False,
        produce_graphics=True,
        metadata_depth_limit=None,
    )


def test_parse_gnu_args(mocker: MockerFixture) -> None:
    """Checks that parse_gnu_args() correctly parses the user's input."""
    # Arrange
    mock_parser = mocker.MagicMock(auto_spec=argparse.ArgumentParser)
    mock_add_argument = mocker.patch.object(mock_parser, "add_argument")
    mock_parse_args = mocker.patch.object(mock_parser, "parse_args", return_value="test_args")
    mocker.patch("main.argparse.ArgumentParser", return_value=mock_parser)

    # Act
    actual_args = parse_gnu_args()

    # Assert
    assert mock_add_argument.call_count == 6
    assert mock_add_argument.call_args_list == [
        mocker.call(
            "-g",
            "--no-graphics",
            help="Prevents graphics from generating",
            action="store_true",
        ),
        mocker.call(
            "-v",
            "--verbose",
            choices=["errors", "warnings", "logs", "credits", "none"],
            default="credits",
            help="Specifies the log type to be printed",
        ),
        mocker.call(
            "-c",
            "--clear-output",
            help="CAUTION! Clears output directory before running the simulation",
            action="store_true",
        ),
        mocker.call(
            "-i",
            "--exclude_info_maps",
            help="Exclude info_maps from the output",
            action="store_true",
        ),
        mocker.call(
            "-o",
            "--output-dir",
            help="The saving directory for output",
            default="output/",
        ),
        mocker.call(
            "-m",
            "--metadata-depth-limit",
            type=int,
            help="Overrides the default metadata depth limit in the Input Manager",
        ),
    ]
    mock_parse_args.assert_called_once()
    assert actual_args == "test_args"


def test_case_insensitive_argument_action() -> None:
    parser = argparse.ArgumentParser()
    parser.register("action", "ci_action", CaseInsensitiveArgumentAction)

    namespace = argparse.Namespace()

    arguments = ["-f", "-F"]
    value = "test_value"

    for argument in arguments:
        action = parser.add_argument(argument, action="ci_action")
        action(parser, namespace, value, option_string=argument)

    for argument in arguments:
        assert hasattr(namespace, argument)
        assert getattr(namespace, argument) == value
