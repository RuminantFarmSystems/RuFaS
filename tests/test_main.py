import argparse
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from main import CaseInsensitiveArgumentAction, main, parse_gnu_args
from RUFAS.output_manager import LogVerbosity


@pytest.fixture
def mock_task_manager(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("main.TaskManager", autospec=True)


def test_main_success(mock_task_manager: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
    mock_instance = mock_task_manager.return_value
    mock_instance.start.return_value = None

    # Simulating command line arguments
    test_args = ["program_name", "-v", "errors", "-o", "output/", "-s", "-l", "test_log_dir"]
    monkeypatch.setattr(sys, "argv", test_args)

    main()

    mock_instance.start.assert_called_once_with(
        metadata_path=Path("input/task_manager_metadata.json"),
        verbosity=LogVerbosity.ERRORS,
        exclude_info_maps=False,
        output_directory=Path("output"),
        logs_directory=Path("test_log_dir"),
        clear_output_directory=False,
        produce_graphics=True,
        suppress_log_files=True,
        metadata_depth_limit=None,
    )


def test_main_exception_path(monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
    """
    Forces an exception in TaskManager.start() to test main exception path.
    """
    mock_tm_cls = mocker.patch("main.TaskManager")
    mock_tm = mock_tm_cls.return_value
    mock_tm.start.side_effect = Exception("main error")
    mock_om_cls = mocker.patch("main.OutputManager")
    mock_om = mock_om_cls.return_value

    mocker.patch("main.traceback.format_exc", return_value="FAKE_TRACEBACK")
    monkeypatch.setattr(sys, "argv", ["prog", "-l", "err_logs", "-i"])

    with pytest.raises(RuntimeError) as excinfo:
        main()

    mock_om_cls.assert_called_once()

    assert mock_om.add_error.call_count == 2
    first_title, first_message, first_info = mock_om.add_error.call_args_list[0].args
    assert first_title.startswith("Dumping all logs from main.py because of error 'main error'")
    assert first_message.startswith("This terminal error occurred during runtime. ")
    assert "FAKE_TRACEBACK" in first_message
    assert first_info == {"class": "No caller class", "function": "main"}

    mock_om.create_directory.assert_called_once_with(Path("err_logs"))
    mock_om.dump_all_nondata_pools.assert_called_once_with(Path("err_logs"), True, "block")

    second_title, second_message, second_info = mock_om.add_error.call_args_list[1].args
    assert second_title == "Early termination"
    assert "Unexpected early termination of the simulation." in second_message
    assert second_info == {"class": "No caller class", "function": "main"}

    assert "main error" in str(excinfo.value)
    assert "check error logs" in str(excinfo.value)


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
    assert mock_add_argument.call_count == 9
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
            "-s",
            "--suppress-log-files",
            help="Prevents logs from the Task Manager being written to files",
            action="store_true",
        ),
        mocker.call(
            "-l",
            "--logs-dir",
            help="The directory for saving log files too",
            default="output/logs",
        ),
        mocker.call(
            "-m",
            "--metadata-depth-limit",
            type=int,
            help="Overrides the default metadata depth limit in the Input Manager",
        ),
        mocker.call(
            "-p",
            "--path-to-metadata",
            help="Path to the task manager metadata that will determine the tasks run",
            default="input/task_manager_metadata.json",
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
