from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from RUFAS.output_manager import LogVerbosity
from main import launch_rufas


@pytest.fixture
def mock_task_manager(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("RUFAS.launching.TaskManager", autospec=True)


def test_launch_rufas_succeeds(mock_task_manager: MagicMock, monkeypatch: pytest.MonkeyPatch) -> None:
    mock_instance = mock_task_manager.return_value
    mock_instance.start.return_value = None

    launch_rufas(
        path_to_metadata=Path('input/task_manager_metadata.json'),
        verbose='errors',
        exclude_info_maps=False,
        output_dir=Path('output/'),
        logs_dir=Path('test_log_dir'),
        clear_output=False,
        no_graphics=False,
        suppress_log_files=True,
        metadata_depth_limit=None,
    )

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
