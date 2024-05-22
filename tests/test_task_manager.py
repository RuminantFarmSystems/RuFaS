from typing import Any, Generator
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from RUFAS.task_manager import TaskManager, TaskType
from RUFAS.output_manager import LogVerbosity
from RUFAS.units import MeasurementUnits


@pytest.fixture
def mock_input_manager() -> Generator[Any, Any, Any]:
    with patch("RUFAS.task_manager.InputManager") as mock:
        yield mock


@pytest.fixture
def mock_output_manager() -> Generator[Any, Any, Any]:
    with patch("RUFAS.task_manager.OutputManager") as mock:
        yield mock


@pytest.fixture
def task_manager(mock_input_manager: MagicMock, mock_output_manager: MagicMock) -> TaskManager:
    tm = TaskManager()
    tm.input_manager = mock_input_manager
    tm.output_manager = mock_output_manager
    return tm


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("Herd Initialization", TaskType.HERD_INITIALIZATION),
        ("simulation single run", TaskType.SIMULATION_SINGLE_RUN),
        ("simulation multi RUN", TaskType.SIMULATION_MULTI_RUN),
        ("sensitivity analysis", TaskType.SENSITIVITY_ANALYSIS),
        ("input data Audit", TaskType.INPUT_DATA_AUDIT),
        ("end to END testing", TaskType.END_TO_END_TESTING),
        ("post_processing", TaskType.POST_PROCESSING),
    ],
)
def test_task_type_from_string(input_str: str, expected: TaskType) -> None:
    assert TaskType.from_string(input_str) == expected


def test_invalid_task_type_from_string() -> None:
    with pytest.raises(ValueError):
        TaskType.from_string("non existing task type")


def test_task_manager_init(
    task_manager: TaskManager,
    mock_input_manager: Generator[Any, Any, Any],
    mock_output_manager: Generator[Any, Any, Any],
) -> None:
    assert task_manager.input_manager is mock_input_manager
    assert task_manager.output_manager is mock_output_manager


def test_task_manager_start_exception(task_manager):
    task_manager.input_manager.start_data_processing = MagicMock(return_value=False)
    with pytest.raises(Exception) as exc_info:
        task_manager.start(Path("/fake/path"), LogVerbosity.LOGS, False, Path("/fake/output"), True, False, None)
    assert "Task Manager's input data is invalid." in str(exc_info.value)


def test_set_random_seed(mock_output_manager: Generator[Any, Any, Any]) -> None:
    TaskManager.set_random_seed(1234, mock_output_manager)
    mock_output_manager.add_log.assert_called_with(
        "Random seed used",
        "Seeded libaries with random_seed=1234",
        {"class": "TaskManager", "function": "set_random_seed", "units": MeasurementUnits.UNITLESS},
    )


def test_set_random_seed_zero(mock_output_manager: Generator[Any, Any, Any]) -> None:
    with patch("RUFAS.task_manager.random.randint", return_value=4321) as mock_randint:
        TaskManager.set_random_seed(0, mock_output_manager)
        mock_randint.assert_called_once_with(0, 2**32 - 1)
        mock_output_manager.add_log.assert_called_with(
            "Random seed used",
            "Seeded libaries with random_seed=4321",
            {"class": "TaskManager", "function": "set_random_seed", "units": MeasurementUnits.UNITLESS},
        )


@pytest.mark.parametrize("seed, expected", [(12345, 12345), (0, 4321)])
def test_set_random_seed_with_parameters(
    seed: int, expected: int, mock_output_manager: Generator[Any, Any, Any]
) -> None:
    with patch("RUFAS.task_manager.random.randint", return_value=4321) as mock_randint:
        TaskManager.set_random_seed(seed, mock_output_manager)
        if seed == 0:
            mock_randint.assert_called_once_with(0, 2**32 - 1)
        mock_output_manager.add_log.assert_called_with(
            "Random seed used",
            f"Seeded libaries with random_seed={expected}",
            {"class": "TaskManager", "function": "set_random_seed", "units": MeasurementUnits.UNITLESS},
        )


def test_parse_input_tasks(task_manager: TaskManager, mock_input_manager: Generator[Any, Any, Any]) -> None:
    task_data = [
        {
            "task_type": "Herd Initialization",
            "metadata_file_path": "/path/to/herd",
            "output_directory": "/output",
            "filters_directory": "/output/filters",
            "csv_output_directory": "/output/CSV",
            "json_output_directory": "/output/JSON",
            "report_directory": "/output/reports",
            "graphics_directory": "/output/graphics",
            "output_pool_path": "/output",
            "save_animals_directory": "/output/herd",
            "logs_directory": "/output/logs",
        },
        {
            "task_type": "SIMULATION_MULTI_RUN",
            "metadata_file_path": "/path/to/sim",
            "output_directory": "/output",
            "filters_directory": "/output/filters",
            "csv_output_directory": "/output/CSV",
            "json_output_directory": "/output/JSON",
            "report_directory": "/output/reports",
            "graphics_directory": "/output/graphics",
            "output_pool_path": "/output",
            "save_animals_directory": "/output/herd",
            "logs_directory": "/output/logs",
        },
    ]
    mock_input_manager.get_data.return_value = task_data
    single, multi = task_manager._parse_input_tasks()
    assert len(single) == 1
    assert len(multi) == 1
    assert single[0]["task_type"] == TaskType.HERD_INITIALIZATION
    assert multi[0]["task_type"] == TaskType.SIMULATION_MULTI_RUN


def test_expand_multi_runs_to_single_runs(task_manager: TaskManager) -> None:
    multi_run_args = [{"task_type": TaskType.SIMULATION_MULTI_RUN, "multi_run_counts": 3, "output_prefix": "sim"}]
    results = task_manager._expand_multi_runs_to_single_runs(multi_run_args)
    assert len(results) == 3
    assert all(arg["task_type"] == TaskType.SIMULATION_SINGLE_RUN for arg in results)


def test_handle_post_processing(
    mock_input_manager: Generator[Any, Any, Any], mock_output_manager: Generator[Any, Any, Any]
) -> None:
    args = {
        "output_directory": Path("/fake/output"),
        "filters_directory": Path("/fake/filters"),
        "exclude_info_maps": False,
        "variable_name_style": "verbose",
        "graphics_directory": Path("/fake/graphics"),
        "csv_output_directory": Path("/fake/CSV"),
        "json_output_directory": Path("/fake/JSON"),
        "report_directory": Path("/fake/reports"),
        "output_pool_path": Path("/fake/pool"),
        "logs_directory": Path("/fake/logs"),
    }
    TaskManager.handle_post_processing(args, mock_input_manager, mock_output_manager, "1/1")
    mock_output_manager.dump_all_nondata_pools.assert_called_with(
        args["logs_directory"], args["exclude_info_maps"], "verbose"
    )


def test_input_data_audit(
    mock_input_manager: Generator[Any, Any, Any], mock_output_manager: Generator[Any, Any, Any]
) -> None:
    args = {
        "metadata_file_path": Path("/fake/metadata"),
        "output_directory": Path("/fake/output"),
        "output_prefix": "test",
        "logs_directory": Path("/fake/output/logs"),
    }
    mock_input_manager.start_data_processing.return_value = True
    result = TaskManager.handle_input_data_audit(args, mock_input_manager, mock_output_manager, True)
    assert result
    mock_output_manager.add_log.assert_called_with(
        "Saving metadata properties",
        f"Saving metadata properties {args['metadata_file_path']} at {args['logs_directory']}",
        {"class": "TaskManager", "function": "handle_input_data_audit", "units": MeasurementUnits.UNITLESS},
    )
