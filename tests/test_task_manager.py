from typing import Any, Generator
import pytest
from unittest.mock import patch, MagicMock
from pytest_mock import MockerFixture
from pathlib import Path

from RUFAS.end_to_end_tester import EndToEndTester
from RUFAS.input_manager import InputManager
from RUFAS.task_manager import TaskManager, TaskType
from RUFAS.output_manager import LogVerbosity, OutputManager
from RUFAS.units import MeasurementUnits
from RUFAS.util import Utility


@pytest.fixture
def mock_output_manager() -> Generator[Any, Any, Any]:
    with patch("RUFAS.task_manager.OutputManager") as mock:
        yield mock


@pytest.fixture
def task_manager(mock_output_manager: MagicMock) -> TaskManager:
    tm = TaskManager()
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
        ("Compare metadata properties", TaskType.COMPARE_METADATA_PROPERTIES),
    ],
)
def test_task_type_from_string(input_str: str, expected: TaskType) -> None:
    assert TaskType.from_string(input_str) == expected


def test_invalid_task_type_from_string() -> None:
    with pytest.raises(ValueError):
        TaskType.from_string("non existing task type")


def test_task_manager_init(
    task_manager: TaskManager,
    mock_output_manager: Generator[Any, Any, Any],
) -> None:
    assert task_manager.output_manager is mock_output_manager


def test_task_manager_start_exception(mocker: MockerFixture, mock_output_manager: Generator[Any, Any, Any]) -> None:
    mock_task_manager = TaskManager()
    mock_input_manager = InputManager()
    mock_start_data = mocker.patch.object(mock_input_manager, "start_data_processing", return_value=False)
    mock_dump_get_data = mocker.patch.object(mock_input_manager, "dump_get_data_logs", return_value=None)
    mock_task_manager.output_manager = mock_output_manager
    with pytest.raises(Exception) as exc_info:
        mock_task_manager.start(
            Path("/fake/path"),
            LogVerbosity.LOGS,
            False,
            Path("/fake/output"),
            Path("fake/logs"),
            True,
            False,
            False,
            None,
        )
    assert "Task Manager's input data is invalid." in str(exc_info.value)
    mock_start_data.assert_called_once_with(Path("/fake/path"))
    mock_dump_get_data.assert_called()


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


def test_parse_input_tasks(task_manager: TaskManager, mocker: MockerFixture) -> None:
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
            "suppress_log_files": True,
            "properties_file_path": "path/to/properties",
            "comparison_properties_file_path": "path/to/comparison/properties",
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
            "suppress_log_files": False,
            "properties_file_path": "path/to/properties",
            "comparison_properties_file_path": "path/to/comparison/properties",
        },
    ]
    mock_input_manager = InputManager()
    task_manager.input_manager = mock_input_manager
    mock_get_data = mocker.patch.object(mock_input_manager, "get_data", return_value=task_data)
    single, multi = task_manager._parse_input_tasks()
    assert len(single) == 1
    assert len(multi) == 1
    assert single[0]["task_type"] == TaskType.HERD_INITIALIZATION
    assert multi[0]["task_type"] == TaskType.SIMULATION_MULTI_RUN
    mock_get_data.assert_called_once()


def test_expand_multi_runs_to_single_runs(task_manager: TaskManager) -> None:
    multi_run_args = [{"task_type": TaskType.SIMULATION_MULTI_RUN, "multi_run_counts": 3, "output_prefix": "sim"}]
    results = task_manager._expand_multi_runs_to_single_runs(multi_run_args)
    assert len(results) == 3
    assert all(arg["task_type"] == TaskType.SIMULATION_SINGLE_RUN for arg in results)


@pytest.mark.parametrize("suppress_logs", [True, False])
def test_handle_post_processing(
    task_manager: TaskManager,
    mock_output_manager: Generator[Any, Any, Any],
    suppress_logs: bool,
    mocker: MockerFixture,
) -> None:
    args = {
        "filters_directory": Path("/fake/filters"),
        "exclude_info_maps": False,
        "variable_name_style": "verbose",
        "graphics_directory": Path("/fake/graphics"),
        "csv_output_directory": Path("/fake/CSV"),
        "json_output_directory": Path("/fake/JSON"),
        "report_directory": Path("/fake/reports"),
        "output_pool_path": Path("/fake/pool"),
        "logs_directory": Path("/fake/logs"),
        "suppress_log_files": suppress_logs,
    }
    mock_input_manager = InputManager()
    mock_dump_data_logs = mocker.patch.object(mock_input_manager, "dump_get_data_logs", return_value=None)
    task_manager.handle_post_processing(args, mock_input_manager, mock_output_manager, "1/1")
    mocker.patch.object(mock_output_manager, "dict_to_file_json", return_value=None)
    if not suppress_logs:
        mock_dump_data_logs.call_count == 1
        mock_output_manager.dump_all_nondata_pools.assert_called_with(
            args["logs_directory"], args["exclude_info_maps"], "verbose"
        )
    else:
        mock_dump_data_logs.assert_not_called()
        mock_output_manager.dump_all_nondata_pools.assert_not_called()


def test_handle_end_to_end_testing(
    mock_output_manager: Generator[Any, Any, Any], task_manager: TaskManager, mocker: MockerFixture
) -> None:
    """Test that end-to-end testing is executed correctly."""
    mocker.patch.object(EndToEndTester, "__init__", return_value=None)
    tester = mocker.patch.object(EndToEndTester, "run_end_to_end_testing")
    add_log = mocker.patch.object(mock_output_manager, "add_log")

    task_manager.handle_end_to_end_testing({}, mock_output_manager)

    tester.assert_called_once()
    assert add_log.call_count == 2


@pytest.mark.parametrize("suppress_logs", [True, False])
def test_input_data_audit(
    mock_output_manager: Generator[Any, Any, Any], task_manager: TaskManager, suppress_logs: bool, mocker: MockerFixture
) -> None:
    args = {
        "metadata_file_path": Path("/fake/metadata"),
        "output_prefix": "test",
        "logs_directory": Path("/fake/output/logs"),
        "suppress_log_files": suppress_logs,
    }
    mock_input_manager = InputManager()
    task_manager.input_manager = mock_input_manager
    mocker.patch.object(mock_input_manager, "start_data_processing", return_value=True)
    mock_save_metadata_properties = mocker.patch.object(
        mock_input_manager, "save_metadata_properties", return_value=None
    )

    result = task_manager.handle_input_data_audit(args, mock_input_manager, mock_output_manager, True)
    assert result
    if not suppress_logs:
        mock_output_manager.add_log.assert_called_with(
            "Saving metadata properties",
            f"Saving metadata properties {args['metadata_file_path']} at {args['logs_directory']}",
            {"class": "TaskManager", "function": "handle_input_data_audit", "units": MeasurementUnits.UNITLESS},
        )
        mock_save_metadata_properties.assert_called_once()
    else:
        mock_save_metadata_properties.assert_not_called()


@pytest.mark.parametrize(
    "task_type,pre_validate",
    [
        [TaskType.INPUT_DATA_AUDIT, True],
        [TaskType.COMPARE_METADATA_PROPERTIES, True],
        [TaskType.HERD_INITIALIZATION, False],
        [TaskType.SIMULATION_SINGLE_RUN, False],
        [TaskType.POST_PROCESSING, False],
    ],
)
def test_task(
    mock_output_manager: Generator[Any, Any, Any],
    task_manager: TaskManager,
    mocker: MockerFixture,
    task_type: TaskType,
    pre_validate: bool,
) -> None:
    """Tests that all available tasks were able to be mapped and run"""
    args = {
        "task_type": task_type,
        "log_verbosity": LogVerbosity.LOGS,
        "exclude_info_maps": False,
        "output_prefix": "test",
        "logs_directory": Path("/fake/logs"),
        "task_id": 1,
        "random_seed": 924,
        "suppress_log_files": True,
        "metadata_file_path": Path("/fake/logs"),
        "properties_file_path": Path("more/fake/paths"),
        "produce_graphics": False,
    }

    mock_im_init = mocker.patch.object(InputManager, "__init__", return_value=None)
    produce_graphics = False

    mock_handler = mocker.patch.object(TaskManager, "call_handler", return_value=None)
    mock_handle_input_data_audit = mocker.patch.object(TaskManager, "handle_input_data_audit", return_value=True)
    mock_set_random_seed = mocker.patch.object(TaskManager, "set_random_seed", return_value=None)
    task_manager.task(args, produce_graphics, 10)
    mock_im_init.assert_called_once_with(10)

    if pre_validate:
        mock_handler.assert_called_once()
    else:
        mock_handle_input_data_audit.assert_called_once()
        mock_set_random_seed.assert_called_once()
        mock_handler.assert_called_once()


def test_compare_metadata_properties_tasks(mocker: MockerFixture) -> None:
    """Tests that all compare metadata properties tasks were handled"""
    args = {
        "properties_file_path": Path("fake/properties/path"),
        "comparison_properties_file_path": Path("fake/comparison/properties/path"),
        "logs_directory": Path("/fake/logs"),
    }
    mock_input_manager = MagicMock(name="InputManager")
    mock_output_manager = MagicMock(name="OutputManager")
    produce_graphic = False
    task_id = 6

    mock_compare_metadata_properties = mocker.patch.object(
        mock_input_manager, "compare_metadata_properties", return_value=None
    )

    TaskManager._handle_compare_metadata_properties_tasks(
        args, mock_input_manager, mock_output_manager, task_id, produce_graphic
    )

    mock_compare_metadata_properties.assert_called_once_with(
        args["properties_file_path"], args["comparison_properties_file_path"], args["logs_directory"]
    )


def test_herd_init_tasks() -> None:
    """Tests that all herd initialization tasks were handled"""
    args = {
        "log_verbosity": "logs",
        "exclude_info_maps": False,
        "output_prefix": "test",
        "logs_directory": "/fake/logs",
        "task_id": 1,
        "random_seed": 924,
        "suppress_log_files": True,
        "metadata_file_path": "/fake/logs",
        "properties_file_path": "more/fake/paths",
    }
    task_id = 5

    # Create mocks for InputManager and OutputManager
    mock_input_manager = MagicMock(name="InputManager")
    mock_output_manager = MagicMock(name="OutputManager")
    produce_graphic = False
    with (
        patch.object(TaskManager, "handle_herd_initializaition", return_value=None) as mock_handle_herd_initializaition,
        patch.object(TaskManager, "handle_post_processing", return_value=None) as mock_handle_post_processing,
    ):
        TaskManager._handle_herd_init_tasks(args, mock_input_manager, mock_output_manager, task_id, produce_graphic)
        mock_handle_herd_initializaition.assert_called_once_with(args, mock_output_manager)
        mock_handle_post_processing.assert_called_once_with(args, mock_input_manager, mock_output_manager, task_id)


@pytest.mark.parametrize("input_patch,produce_graphics", [(True, True), (False, True), (False, False), (True, False)])
def test_simulation_engine_run_tasks(input_patch: bool, produce_graphics: bool) -> None:
    """Tests that all simulation engine run tasks were handled"""
    args = {
        "log_verbosity": "logs",
        "exclude_info_maps": False,
        "output_prefix": "test",
        "logs_directory": "/fake/logs",
        "task_id": 1,
        "random_seed": 924,
        "suppress_log_files": True,
        "metadata_file_path": "/fake/logs",
        "properties_file_path": "more/fake/paths",
        "input_patch": input_patch,
    }
    task_id = 5
    mock_input_manager = MagicMock(name="InputManager")
    mock_output_manager = MagicMock(name="OutputManager")
    with (
        patch.object(
            TaskManager, "handle_single_simulation_run", return_value=None
        ) as mock_handle_single_simulation_run,
        patch.object(TaskManager, "handle_post_processing", return_value=None) as mock_handle_post_processing,
        patch.object(Utility, "deep_merge", return_value=None) as mock_deep_merge,
    ):

        TaskManager._handle_simulation_engine_run_tasks(
            args, mock_input_manager, mock_output_manager, task_id, produce_graphics
        )
        if input_patch:
            mock_deep_merge.assert_called_once_with(mock_input_manager.pool, args["input_patch"])
        else:
            mock_deep_merge.assert_not_called()

        mock_handle_single_simulation_run.assert_called_once_with(args, mock_output_manager)
        mock_handle_post_processing.assert_called_once_with(
            args, mock_input_manager, mock_output_manager, task_id, produce_graphics, True
        )


@pytest.mark.parametrize("produce_graphics", [True, False])
def test_postprocessing_tasks(produce_graphics: bool) -> None:
    """Tests that all postprocessing tasks were handled"""
    args = {
        "log_verbosity": "logs",
        "exclude_info_maps": False,
        "output_prefix": "test",
        "logs_directory": "/fake/logs",
        "task_id": 1,
        "random_seed": 924,
        "suppress_log_files": True,
        "metadata_file_path": "/fake/logs",
        "properties_file_path": "more/fake/paths",
    }
    task_id = 5
    mock_input_manager = MagicMock(name="InputManager")
    mock_output_manager = MagicMock(name="OutputManager")
    with patch.object(TaskManager, "handle_post_processing", return_value=None) as mock_handle_post_processing:
        TaskManager._handle_postprocessing_tasks(
            args, mock_input_manager, mock_output_manager, task_id, produce_graphics
        )
        mock_handle_post_processing.assert_called_once_with(
            args, mock_input_manager, mock_output_manager, task_id, produce_graphics, True, True
        )


def test_call_handler():
    """Tests that wrapper handler function were handled"""
    args = {
        "log_verbosity": "logs",
        "exclude_info_maps": False,
        "output_prefix": "test",
        "logs_directory": "/fake/logs",
        "task_id": 1,
        "random_seed": 924,
        "suppress_log_files": True,
        "metadata_file_path": "/fake/logs",
        "properties_file_path": "more/fake/paths",
    }
    task_id = 5
    mock_input_manager = MagicMock(name="InputManager")
    mock_output_manager = MagicMock(name="OutputManager")
    produce_graphics = False

    # Call the call_handler method
    with patch.object(TaskManager, "_handle_postprocessing_tasks", return_value=None) as mock_handle_post_processing:
        TaskManager.call_handler(
            mock_handle_post_processing,
            args=args,
            input_manager=mock_input_manager,
            output_manager=mock_output_manager,
            task_id=task_id,
            produce_graphics=produce_graphics,
        )

        mock_handle_post_processing.assert_called_once_with(
            args, mock_input_manager, mock_output_manager, task_id, produce_graphics
        )


def test_input_data_audit_tasks() -> None:
    """Tests that all input data audit tasks were handled"""
    args = {
        "log_verbosity": LogVerbosity.LOGS,
        "exclude_info_maps": False,
        "output_prefix": "test",
        "logs_directory": Path("/fake/logs"),
        "task_id": 1,
        "random_seed": 924,
        "suppress_log_files": True,
        "metadata_file_path": Path("/fake/logs"),
        "properties_file_path": Path("more/fake/paths"),
    }
    task_id = 5
    im = InputManager()
    om = OutputManager()
    produce_graphic = False

    with (
        patch.object(TaskManager, "handle_input_data_audit", return_value=None) as mock_handle_input_data_audit,
        patch.object(TaskManager, "handle_post_processing", return_value=None) as mock_handle_post_processing,
    ):
        TaskManager._handle_input_data_audit_tasks(args, im, om, task_id, produce_graphic)

        mock_handle_input_data_audit.assert_called_once_with(args, im, om, False)
        mock_handle_post_processing.assert_called_once_with(args, im, om, task_id)
