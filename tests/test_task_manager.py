import multiprocessing
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Generator, Type
from unittest.mock import MagicMock, call, patch

import pytest
from pytest_mock import MockerFixture
from packaging.version import Version

from RUFAS.e2e_test_results_handler import E2ETestResultsHandler
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import LogVerbosity, OutputManager
from RUFAS.task_manager import MINIMUM_PYTHON_VERSION, TaskManager, TaskType
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
        ("data collection app update", TaskType.DATA_COLLECTION_APP_UPDATE),
        ("update e2e test results", TaskType.UPDATE_E2E_TEST_RESULTS),
    ],
)
def test_task_type_from_string(input_str: str, expected: TaskType) -> None:
    """Unit test for TaskType.from_string() with valid task types."""
    assert TaskType.from_string(input_str) == expected


def test_invalid_task_type_from_string() -> None:
    """Unit test for TaskType.from_string() with invalid task type"""
    with pytest.raises(ValueError):
        TaskType.from_string("non existing task type")


def test_task_manager_init(
    task_manager: TaskManager,
    mock_output_manager: OutputManager,
) -> None:
    """Unit test for TaskManager.__init__()"""
    assert task_manager.output_manager is mock_output_manager


@pytest.mark.parametrize(
    "verbosity, exclude_info_maps, clear_output_directory, produce_graphics, suppress_log_files, metadata_depth_limit,"
    "workers, is_end_to_end_test_task",
    [
        (LogVerbosity.LOGS, True, True, True, True, 8, 1, False),
        (LogVerbosity.CREDITS, True, True, True, True, 8, 2, False),
        (LogVerbosity.ERRORS, True, True, True, True, 8, 3, False),
        (LogVerbosity.WARNINGS, True, True, True, True, 8, 4, False),
        (LogVerbosity.NONE, True, True, True, True, 8, 5, False),
        (LogVerbosity.LOGS, False, True, True, True, 8, 6, False),
        (LogVerbosity.CREDITS, False, True, True, True, 8, 7, False),
        (LogVerbosity.ERRORS, False, True, True, True, 8, 8, False),
        (LogVerbosity.WARNINGS, False, True, True, True, 8, 9, False),
        (LogVerbosity.NONE, False, True, True, True, 8, 10, False),
        (LogVerbosity.ERRORS, False, True, True, True, 8, 8, True),
    ],
)
def test_task_manager_start(
    verbosity: LogVerbosity,
    exclude_info_maps: bool,
    clear_output_directory: bool,
    produce_graphics: bool,
    suppress_log_files: bool,
    metadata_depth_limit: int,
    workers: int,
    mocker: MockerFixture,
    mock_output_manager: OutputManager,
    is_end_to_end_test_task: bool,
) -> None:
    """Unit test for TaskManager.start() with and without the e2e summary branch."""
    tm = TaskManager()
    tm.output_manager = mock_output_manager

    mock_im = mocker.MagicMock(auto_spec=InputManager)
    mocker.patch("RUFAS.task_manager.InputManager", return_value=mock_im)
    mock_start_data = mocker.patch.object(mock_im, "start_data_processing", return_value=True)
    mock_get_data = mocker.patch.object(
        mock_im,
        "get_data",
        return_value={
            "parallel_workers": workers,
            "input_data_csv_export_path": "",
            "input_data_csv_import_path": "",
            "export_input_data_to_csv": False,
        },
    )

    mock_run_startup_sequence = mocker.patch.object(mock_output_manager, "run_startup_sequence")
    mock_print_credits = mocker.patch.object(mock_output_manager, "print_credits")
    mock_add_log = mocker.patch.object(mock_output_manager, "add_log")
    mocker.patch.object(tm, "get_rufas_version", return_value="1.0.0")
    mock_check_dependencies = mocker.patch.object(tm, "check_dependencies")
    mock_check_python_version = mocker.patch.object(tm, "check_python_version")

    if not is_end_to_end_test_task:
        mock_parse_input_tasks = mocker.patch.object(tm, "_parse_input_tasks", return_value=([{}], [{}]))
        mock_expand_multi_runs_to_single_runs = mocker.patch.object(
            tm, "_expand_multi_runs_to_single_runs", return_value=[{}]
        )
    else:
        e2e_task = {
            "task_type": TaskType.END_TO_END_TESTING,
            "output_prefix": "test_prefix",
            "json_output_directory": Path("out/e2e"),
        }
        mock_parse_input_tasks = mocker.patch.object(tm, "_parse_input_tasks", return_value=([e2e_task], [{}]))
        mock_expand_multi_runs_to_single_runs = mocker.patch.object(
            tm, "_expand_multi_runs_to_single_runs", return_value=[]
        )

    mock_run_tasks = mocker.patch.object(tm, "_run_tasks")
    mock_summarize = mocker.patch.object(mock_output_manager, "summarize_e2e_test_results")

    tm.start(
        metadata_path=Path("metadata/path"),
        verbosity=verbosity,
        exclude_info_maps=exclude_info_maps,
        output_directory=Path("output/directory"),
        logs_directory=Path("logs/directory"),
        clear_output_directory=clear_output_directory,
        produce_graphics=produce_graphics,
        suppress_log_files=suppress_log_files,
        metadata_depth_limit=metadata_depth_limit,
    )

    mock_run_startup_sequence.assert_called_once_with(
        verbosity=verbosity,
        exclude_info_maps=exclude_info_maps,
        output_directory=Path("output/directory"),
        clear_output_directory=clear_output_directory,
        chunkification=False,
        max_memory_usage_percent=0,
        max_memory_usage=0,
        save_chunk_threshold_call_count=0,
        variables_file_path=Path(""),
        output_prefix="Task Manager",
        task_id="TASK MANAGER",
        is_end_to_end_testing_run=False,
    )

    info_map = {"class": TaskManager.__name__, "function": TaskManager.start.__name__}
    expanded_len = 1 if is_end_to_end_test_task else 2
    expected_add_log_calls = [
        call("Task Manager Start", "Task Manager Started.", info_map),
        call("Task Manager workers", f"Task Manager is going to run {workers} in parallel.", info_map),
        call("Task Manager parsed tasks", "Parsed 2 tasks args.", info_map),
        call("Task Manager expanded tasks", f"Expanded task args to {expanded_len}. Starting the tasks...", info_map),
    ]
    mock_add_log.assert_has_calls(expected_add_log_calls)

    mock_start_data.assert_called_once_with(Path("metadata/path"), Path(""))
    mock_get_data.assert_called_once_with("tasks")
    mock_parse_input_tasks.assert_called_once()
    mock_expand_multi_runs_to_single_runs.assert_called_once()

    if not is_end_to_end_test_task:
        mock_run_tasks.assert_called_once_with(
            [{"task_id": "1/2"}, {"task_id": "2/2"}],
            produce_graphics,
            metadata_depth_limit,
            workers,
            Path("metadata/path"),
        )
        mock_summarize.assert_not_called()
    else:
        args, _kwargs = mock_run_tasks.call_args
        runnable_passed = args[0]
        assert len(runnable_passed) == 1
        assert runnable_passed[0]["task_id"] == "1/1"
        assert args[1] == produce_graphics
        assert args[2] == metadata_depth_limit
        assert args[3] == workers
        assert args[4] == Path("metadata/path")

        mock_add_log.assert_any_call(
            "Summarizing e2e test results",
            "Gathering e2e results for ['test_prefix']...",
            info_map,
        )
        mock_summarize.assert_called_once_with(Path("out/e2e"), ["test_prefix"])

    mock_print_credits.assert_called_once_with("1.0.0")
    mock_check_dependencies.assert_called_once()
    mock_check_python_version.assert_called_once()


def test_task_manager_start_invalid_data(mocker: MockerFixture, mock_output_manager: OutputManager) -> None:
    """Test TaskManager.start() with invalid input data."""
    mock_task_manager = TaskManager()
    mocker.patch.object(mock_task_manager, "check_python_version")
    mocker.patch.object(mock_task_manager, "check_dependencies")
    mock_input_manager = mocker.MagicMock(auto_spec=InputManager)
    mocker.patch.object(mock_input_manager, "start_data_processing", return_value=False)
    mocker.patch("RUFAS.task_manager.InputManager", return_value=mock_input_manager)
    mock_add_log = mocker.patch.object(mock_output_manager, "add_log")
    mock_task_manager.output_manager = mock_output_manager

    with pytest.raises(Exception, match="Task Manager's input data is invalid."):
        mock_task_manager.start(
            Path("metadata/path"),
            LogVerbosity.NONE,
            False,
            Path("output/directory"),
            Path("logs/directory"),
            False,
            False,
            False,
            8,
        )

    mock_add_log.assert_called_with(
        "Validation counts",
        mocker.ANY,
        {"class": "TaskManager", "function": "handle_post_processing", "units": MeasurementUnits.UNITLESS},
    )


def test_set_random_seed(mock_output_manager: OutputManager, mocker: MockerFixture) -> None:
    """Unit test for TaskManager.set_random_seed() with no specified random seed."""
    mock_task_manager = TaskManager()
    mock_add_log = mocker.patch.object(mock_output_manager, "add_log")
    mock_task_manager.output_manager = mock_output_manager
    mock_task_manager.set_random_seed(1234, mock_output_manager)
    mock_add_log.assert_called_with(
        "Random seed used",
        "Seeded libaries with random_seed=1234",
        {"class": "TaskManager", "function": "set_random_seed", "units": MeasurementUnits.UNITLESS},
    )


def test_set_random_seed_zero(mock_output_manager: OutputManager, mocker: MockerFixture) -> None:
    """Unit test for TaskManager.set_random_seed() when 0 is passed as random seed."""
    mock_task_manager = TaskManager()
    mock_randint = mocker.patch("RUFAS.task_manager.random.randint", return_value=4321)
    mock_add_log = mocker.patch.object(mock_output_manager, "add_log")
    mock_task_manager.output_manager = mock_output_manager
    mock_task_manager.set_random_seed(0, mock_output_manager)
    mock_randint.assert_called_once_with(0, 2**32 - 1)
    mock_add_log.assert_called_with(
        "Random seed used",
        "Seeded libaries with random_seed=4321",
        {"class": "TaskManager", "function": "set_random_seed", "units": MeasurementUnits.UNITLESS},
    )


@pytest.mark.parametrize("seed, expected", [(12345, 12345), (0, 4321)])
def test_set_random_seed_with_parameters(
    seed: int, expected: int, mock_output_manager: OutputManager, mocker: MockerFixture
) -> None:
    """Unit test for TaskManager.set_random_seed() with specified random seed."""
    mock_task_manager = TaskManager()
    mock_randint = mocker.patch("RUFAS.task_manager.random.randint", return_value=4321)
    mock_add_log = mocker.patch.object(mock_output_manager, "add_log")
    mock_task_manager.output_manager = mock_output_manager
    mock_task_manager.set_random_seed(seed, mock_output_manager)
    if seed == 0:
        mock_randint.assert_called_once_with(0, 2**32 - 1)
    mock_add_log.assert_called_with(
        "Random seed used",
        f"Seeded libaries with random_seed={expected}",
        {"class": "TaskManager", "function": "set_random_seed", "units": MeasurementUnits.UNITLESS},
    )


def test_parse_input_tasks(task_manager: TaskManager, mocker: MockerFixture) -> None:
    """Unit test for TaskManager._parse_input_tasks()"""
    task_data = {
        "export_input_data_to_csv": False,
        "input_data_csv_export_path": "",
        "input_data_csv_import_path": "",
        "tasks": [
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
                "convert_variable_table_path": "dummy.csv",
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
                "convert_variable_table_path": "dummy.csv",
            },
        ],
    }
    mock_input_manager = mocker.MagicMock(auto_spec=InputManager)
    mock_get_data = mocker.patch.object(mock_input_manager, "get_data", return_value=task_data)
    mocker.patch("RUFAS.task_manager.InputManager", return_value=mock_input_manager)
    task_manager.input_manager = mock_input_manager

    single, multi = task_manager._parse_input_tasks()
    assert len(single) == 1
    assert len(multi) == 1
    assert single[0]["task_type"] == TaskType.HERD_INITIALIZATION
    assert multi[0]["task_type"] == TaskType.SIMULATION_MULTI_RUN
    mock_get_data.assert_called_once_with("tasks")


def test_expand_multi_runs_to_single_runs(task_manager: TaskManager) -> None:
    """Unit test for TaskManager._expand_multi_runs_to_single_runs()"""
    multi_run_args = [{"task_type": TaskType.SIMULATION_MULTI_RUN, "multi_run_counts": 3, "output_prefix": "sim"}]
    results = task_manager._expand_multi_runs_to_single_runs(multi_run_args)
    assert len(results) == 3
    assert all(arg["task_type"] == TaskType.SIMULATION_SINGLE_RUN for arg in results)


@pytest.mark.parametrize("suppress_logs", [True, False])
def test_handle_post_processing(
    task_manager: TaskManager,
    mock_output_manager: OutputManager,
    suppress_logs: bool,
    mocker: MockerFixture,
) -> None:
    """Unit test for TaskManager.handle_post_processing()"""
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
    mock_input_manager = mocker.MagicMock(auto_spec=InputManager)
    mock_flush_pool = mocker.patch.object(mock_input_manager, "flush_pool", return_value=None)
    mock_dump_data_logs = mocker.patch.object(mock_input_manager, "dump_get_data_logs", return_value=None)
    mock_dump_all_nondata_pools = mocker.patch.object(mock_output_manager, "dump_all_nondata_pools", return_value=None)
    task_manager.handle_post_processing(
        args=args,
        input_manager=mock_input_manager,
        output_manager=mock_output_manager,
        task_id="1/1",
        should_flush_im_pool=True,
    )
    mocker.patch("RUFAS.task_manager.InputManager", return_value=mock_input_manager)

    mocker.patch.object(mock_output_manager, "dict_to_file_json", return_value=None)
    if not suppress_logs:
        mock_dump_data_logs.call_count == 1
        mock_dump_all_nondata_pools.assert_called_with(args["logs_directory"], args["exclude_info_maps"], "verbose")
    else:
        mock_dump_data_logs.assert_not_called()
        mock_dump_all_nondata_pools.assert_not_called()

    mock_flush_pool.assert_called_once()


def test_handle_post_processing_export_input_tocsv(
    task_manager: TaskManager,
    mock_output_manager: OutputManager,
    mocker: MockerFixture,
) -> None:
    """Unit test for TaskManager.handle_post_processing() when load_pool_from_file is set to True."""
    mock_input_manager = mocker.MagicMock(auto_spec=InputManager)
    mocker.patch.object(mock_input_manager, "dump_get_data_logs", return_value=None)
    mocker.patch("RUFAS.task_manager.InputManager", return_value=mock_input_manager)

    mock_combine_saved_input_csv = mocker.patch.object(Utility, "combine_saved_input_csv", return_value=None)

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
        "suppress_log_files": True,
        "input_data_csv_export_path": Path("/fake/saved_input"),
        "input_data_csv_import_path": Path("/fake/saved_input"),
    }
    task_manager.handle_post_processing(
        args=args,
        input_manager=mock_input_manager,
        output_manager=mock_output_manager,
        task_id="1/1",
        should_flush_im_pool=False,
        export_input_data_to_csv=True,
    )

    mock_combine_saved_input_csv.assert_called_once_with(
        TaskManager.INPUT_DATA_CSV_WORKING_FOLDER,
        args["input_data_csv_export_path"],
        args["input_data_csv_import_path"],
    )


def test_handle_end_to_end_testing(
    mock_output_manager: OutputManager, task_manager: TaskManager, mocker: MockerFixture
) -> None:
    """Test that end-to-end testing is executed correctly."""
    sim_engine_run_tasks = mocker.patch.object(TaskManager, "_handle_simulation_engine_run_tasks")
    post_processing = mocker.patch.object(TaskManager, "handle_post_processing")
    args = {
        "json_output_directory": "json_path",
        "convert_variable_table_path": "compare_path",
        "output_prefix": "dummy_prefix",
    }
    compare_outputs = mocker.patch(
        "RUFAS.e2e_test_results_handler.E2ETestResultsHandler.compare_actual_and_expected_test_results"
    )
    mock_input_manager = mocker.MagicMock()
    add_log = mocker.patch.object(mock_output_manager, "add_log")

    task_manager._handle_end_to_end_testing(args, mock_input_manager, mock_output_manager, "test_task", True, True)

    sim_engine_run_tasks.assert_called_once_with(
        args=args,
        input_manager=mock_input_manager,
        output_manager=mock_output_manager,
        task_id="test_task",
        produce_graphics=True,
        should_flush_im_pool=True,
    )
    compare_outputs.assert_called_once_with(
        args["json_output_directory"], args["convert_variable_table_path"], args["output_prefix"]
    )
    assert add_log.call_count == 2
    assert post_processing.call_count == 1


def test_handle_update_e2e_test_results(
    mock_output_manager: OutputManager, task_manager: TaskManager, mocker: MockerFixture
) -> None:
    """Test that updating end-to-end expected test results executes correctly."""

    # Arrange
    sim_engine_run_tasks = mocker.patch.object(TaskManager, "_handle_simulation_engine_run_tasks")
    update_test_results = mocker.patch.object(E2ETestResultsHandler, "update_expected_test_results")
    add_log = mocker.patch.object(mock_output_manager, "add_log")

    mock_input_manager = MagicMock()
    args = {"json_output_directory": "json_path", "output_prefix": "dummy_prefix"}

    # Act
    task_manager._handle_update_e2e_test_results(args, mock_input_manager, mock_output_manager, "test_task", True, True)

    # Assert
    sim_engine_run_tasks.assert_called_once_with(
        args=args,
        input_manager=mock_input_manager,
        output_manager=mock_output_manager,
        task_id="test_task",
        produce_graphics=True,
        should_flush_im_pool=True,
    )

    update_test_results.assert_called_once_with(args["json_output_directory"], args["output_prefix"])

    assert add_log.call_count == 2
    add_log.assert_any_call(
        "End-to-end testing",
        "Generating new set of end-to-end expected test results.",
        {"class": "TaskManager", "function": "_handle_update_e2e_test_results"},
    )
    add_log.assert_any_call(
        "End-to-end testing",
        "Completed generation of new set of end-to-end expected test results",
        {"class": "TaskManager", "function": "_handle_update_e2e_test_results"},
    )


def test_handle_post_processing_load_pool(
    task_manager: TaskManager,
    mock_output_manager: OutputManager,
    mocker: MockerFixture,
) -> None:
    """Unit test for TaskManager.handle_post_processing() when load_pool_from_file is set to True."""
    mock_input_manager = mocker.MagicMock(auto_spec=InputManager)
    mocker.patch.object(mock_input_manager, "dump_get_data_logs", return_value=None)
    mocker.patch("RUFAS.task_manager.InputManager", return_value=mock_input_manager)
    mock_flush_pools = mocker.patch.object(mock_output_manager, "flush_pools", return_value=None)
    mock_load_variables_pool_from_file = mocker.patch.object(
        mock_output_manager, "load_variables_pool_from_file", return_value=None
    )
    mock_set_metadata_prefix = mocker.patch.object(mock_output_manager, "set_metadata_prefix", return_value=None)

    mocker.patch.object(mock_output_manager, "dict_to_file_json", return_value=None)

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
        "suppress_log_files": True,
    }
    task_manager.handle_post_processing(
        args=args,
        input_manager=mock_input_manager,
        output_manager=mock_output_manager,
        task_id="1/1",
        should_flush_im_pool=False,
        load_pool_from_file=True,
    )

    mock_flush_pools.assert_called_once()
    mock_load_variables_pool_from_file.assert_called_once_with(args["output_pool_path"])
    mock_set_metadata_prefix.assert_called_once_with("reload")


def test_handle_post_processing_save_result(
    task_manager: TaskManager,
    mock_output_manager: OutputManager,
    mocker: MockerFixture,
) -> None:
    """Unit test for TaskManager.handle_post_processing() when save_result is set to True."""
    mock_input_manager = mocker.MagicMock(auto_spec=InputManager)
    mocker.patch.object(mock_input_manager, "dump_get_data_logs", return_value=None)
    mocker.patch("RUFAS.task_manager.InputManager", return_value=mock_input_manager)

    mocker.patch.object(mock_output_manager, "dict_to_file_json", return_value=None)
    mock_save_results = mocker.patch.object(mock_output_manager, "save_results", return_value=None)

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
        "suppress_log_files": True,
    }
    task_manager.handle_post_processing(
        args=args,
        input_manager=mock_input_manager,
        output_manager=mock_output_manager,
        task_id="1/1",
        should_flush_im_pool=False,
        save_results=True,
    )

    mock_save_results.assert_called_once_with(
        args["filters_directory"],
        args["exclude_info_maps"],
        False,
        args["report_directory"],
        args["graphics_directory"],
        args["csv_output_directory"],
        args["json_output_directory"],
    )


@pytest.mark.parametrize(
    "suppress_logs, export_input_data_to_csv", [(True, True), (False, True), (True, False), (False, False)]
)
def test_input_data_audit(
    suppress_logs: bool,
    export_input_data_to_csv: bool,
    mock_output_manager: OutputManager,
    task_manager: TaskManager,
    mocker: MockerFixture,
) -> None:
    """Unit test for TaskManager.handle_input_data_audit()"""
    args = {
        "metadata_file_path": Path("/fake/metadata"),
        "output_prefix": "test",
        "logs_directory": Path("/fake/output/logs"),
        "suppress_log_files": suppress_logs,
        "export_input_data_to_csv": export_input_data_to_csv,
        "input_data_csv_export_path": Path("/fake/output/saved_input"),
        "input_root": "",
    }
    mock_input_manager = mocker.MagicMock(auto_spec=InputManager)
    mocker.patch.object(mock_input_manager, "start_data_processing", return_value=True)
    mock_save_metadata_properties = mocker.patch.object(
        mock_input_manager, "save_metadata_properties", return_value=None
    )
    mocve_export_pool_to_csv = mocker.patch.object(mock_input_manager, "export_pool_to_csv", return_value=None)
    mocker.patch("RUFAS.task_manager.InputManager", return_value=mock_input_manager)
    task_manager.input_manager = mock_input_manager
    mock_add_log = mocker.patch.object(mock_output_manager, "add_log", return_value=None)

    result = task_manager.handle_input_data_audit(args, mock_input_manager, mock_output_manager, True)
    assert result
    if not suppress_logs:
        mock_add_log.assert_called_with(
            "Saving metadata properties",
            f"Saving metadata properties {args['metadata_file_path']} at {args['logs_directory']}",
            {"class": "TaskManager", "function": "handle_input_data_audit", "units": MeasurementUnits.UNITLESS},
        )
        mock_save_metadata_properties.assert_called_once()
    else:
        mock_save_metadata_properties.assert_not_called()

    if export_input_data_to_csv:
        mocve_export_pool_to_csv.assert_called_once_with(
            args["output_prefix"], TaskManager.INPUT_DATA_CSV_WORKING_FOLDER
        )
    else:
        mocve_export_pool_to_csv.assert_not_called()


@pytest.mark.parametrize(
    "task_type,pre_validate",
    [
        [TaskType.INPUT_DATA_AUDIT, True],
        [TaskType.COMPARE_METADATA_PROPERTIES, True],
        [TaskType.HERD_INITIALIZATION, False],
        [TaskType.SIMULATION_SINGLE_RUN, False],
        [TaskType.POST_PROCESSING, False],
        [TaskType.END_TO_END_TESTING, False],
    ],
)
def test_task(
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
        "chunkification": False,
        "save_chunk_threshold_call_count": 0,
        "maximum_memory_usage": 0,
        "maximum_memory_usage_percent": 0,
        "output_prefix": "test",
        "logs_directory": Path("/fake/logs"),
        "filters_directory": Path("/fake/filters"),
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
    mocker.patch.object(OutputManager, "validate_filter_constant_content")
    task_manager.task(args, produce_graphics, 2, 10, metadata_path=Path("metadata/path"))
    mock_im_init.assert_called_once_with(10)

    if pre_validate:
        mock_handler.assert_called_once()
    else:
        mock_handle_input_data_audit.assert_called_once()
        mock_set_random_seed.assert_called_once()
        mock_handler.assert_called_once()


def test_task_invalid_data(mocker: MockerFixture, mock_output_manager: OutputManager) -> None:
    """Unit test for TaskManager.task() with invalid data"""
    task_manager = TaskManager()
    mock_im_init = mocker.patch.object(InputManager, "__init__", return_value=None)

    mock_om_init = mocker.patch("RUFAS.task_manager.OutputManager", return_value=mock_output_manager)

    mock_handler = mocker.patch.object(TaskManager, "call_handler", return_value=None)
    mock_handle_input_data_audit = mocker.patch.object(TaskManager, "handle_input_data_audit", return_value=False)
    mock_handle_post_processing = mocker.patch.object(TaskManager, "handle_post_processing")
    mock_run_startup_sequence = mocker.patch.object(mock_output_manager, "run_startup_sequence")
    mock_add_error = mocker.patch.object(mock_output_manager, "add_error")
    task_manager.output_manager = mock_output_manager

    args = {
        "task_type": TaskType.SIMULATION_SINGLE_RUN,
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
        "chunkification": False,
        "maximum_memory_usage_percent": 0,
        "maximum_memory_usage": 0,
        "save_chunk_threshold_call_count": 0,
    }
    produce_graphics = False
    result = task_manager.task(args, produce_graphics, 1, 10, metadata_path=Path("metadata/path"))

    assert result is None

    mock_om_init.assert_called_once()
    mock_run_startup_sequence.assert_called_once_with(
        verbosity=LogVerbosity.LOGS,
        exclude_info_maps=args["exclude_info_maps"],
        output_directory=Path("output/"),
        clear_output_directory=False,
        chunkification=False,
        max_memory_usage_percent=0,
        max_memory_usage=0,
        save_chunk_threshold_call_count=0,
        variables_file_path=Path(""),
        output_prefix=args["output_prefix"],
        task_id=args["task_id"],
        is_end_to_end_testing_run=False,
    )
    mock_im_init.assert_called_once_with(10)
    mock_handler.assert_not_called()
    mock_handle_input_data_audit.assert_called_once()

    info_map = {
        "class": TaskManager.__name__,
        "function": TaskManager.task.__name__,
        "units": MeasurementUnits.UNITLESS,
    }
    mock_add_error.assert_called_once_with(
        "No task run", f"Data not valid for {args['output_prefix']}, task not run", info_map
    )

    mock_handle_post_processing.assert_called_once()


def test_task_failed(task_manager: TaskManager) -> None:
    """Tests that error were handled correctly"""
    args = {
        "task_type": "failure",
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
        "chunkification": False,
        "maximum_memory_usage_percent": 1,
        "maximum_memory_usage": 0,
        "save_chunk_threshold_call_count": 0,
    }
    produce_graphics = False
    result = task_manager.task(args, produce_graphics, 2, 10, metadata_path=Path("metadata/path"))
    assert result == "test (1)"


@pytest.mark.parametrize(
    "init_herd, save_animals, save_animals_directory",
    [
        (True, True, Path("dummy/path")),
        (True, False, Path("dummy/path")),
        (False, True, Path("dummy/path")),
        (False, False, Path("dummy/path")),
    ],
)
def test_handle_herd_initialization(
    init_herd: bool,
    save_animals: bool,
    save_animals_directory: Path,
    task_manager: TaskManager,
    mock_output_manager: OutputManager,
    mocker: MockerFixture,
) -> None:
    """Unit test for TaskManager.handle_herd_initializaition()"""
    args = {"init_herd": init_herd, "save_animals": save_animals, "save_animals_directory": save_animals_directory}
    mock_herd_factory = mocker.patch("RUFAS.biophysical.animal.herd_factory.HerdFactory")
    mock_herd_factory_init = mocker.patch("RUFAS.task_manager.HerdFactory", return_value=mock_herd_factory)
    mock_initialize_herd = mocker.patch.object(mock_herd_factory, "initialize_herd")
    mock_add_log = mocker.patch.object(mock_output_manager, "add_log", return_value=None)

    task_manager.handle_herd_initializaition(args, mock_output_manager)

    info_map = {
        "class": TaskManager.__name__,
        "function": TaskManager.handle_herd_initializaition.__name__,
        "units": MeasurementUnits.UNITLESS,
    }
    om_add_log_call_list = [
        call("Herd initialization start", "Initializing herd data...", info_map),
        call("Herd initialization complete", "Herd data initialized.", info_map),
    ]
    mock_add_log.assert_has_calls(om_add_log_call_list)

    mock_herd_factory_init.assert_called_once_with(init_herd, save_animals, save_animals_directory)
    mock_initialize_herd.assert_called_once()


def test_single_simulation_run(
    task_manager: TaskManager, mock_output_manager: OutputManager, mocker: MockerFixture
) -> None:
    """Unit test for TaskManager.handle_single_simulation_run()"""
    mock_handle_herd_initializaition = mocker.patch.object(TaskManager, "handle_herd_initializaition")

    args: dict[str, Any] = {"task_type": TaskType.SIMULATION_SINGLE_RUN}

    mock_simulation_engine = mocker.patch("RUFAS.simulation_engine.SimulationEngine")
    mock_simulation_engine_init = mocker.patch(
        "RUFAS.task_manager.SimulationEngine", return_value=mock_simulation_engine
    )
    mock_simulate = mocker.patch.object(mock_simulation_engine, "simulate")
    mock_add_log = mocker.patch.object(mock_output_manager, "add_log", return_value=None)

    task_manager.handle_single_simulation_run(args, mock_output_manager)

    mock_handle_herd_initializaition.assert_called_once_with(args, mock_output_manager)

    info_map = {
        "class": TaskManager.__name__,
        "function": TaskManager.handle_single_simulation_run.__name__,
        "units": MeasurementUnits.UNITLESS,
    }
    om_add_log_call_list = [
        call("Starting the simulation", "Starting the simulation", info_map),
        call("Simulation completed", "Simulation completed", info_map),
    ]
    mock_add_log.assert_has_calls(om_add_log_call_list)

    mock_simulation_engine_init.assert_called_once()
    mock_simulate.assert_called_once()


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
    should_flush_im_pool = True

    mock_compare_metadata_properties = mocker.patch.object(
        mock_input_manager, "compare_metadata_properties", return_value=None
    )

    TaskManager._handle_compare_metadata_properties_tasks(
        args, mock_input_manager, mock_output_manager, task_id, produce_graphic, should_flush_im_pool
    )

    mock_compare_metadata_properties.assert_called_once_with(
        args["properties_file_path"], args["comparison_properties_file_path"], args["logs_directory"]
    )


def test_herd_init_tasks(mocker: MockerFixture) -> None:
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
    should_flush_im_pool = True
    mock_handle_herd_initializaition = mocker.patch.object(
        TaskManager, "handle_herd_initializaition", return_value=None
    )
    mock_handle_post_processing = mocker.patch.object(TaskManager, "handle_post_processing", return_value=None)

    TaskManager._handle_herd_init_tasks(
        args, mock_input_manager, mock_output_manager, task_id, produce_graphic, should_flush_im_pool
    )
    mock_handle_herd_initializaition.assert_called_once_with(args=args, output_manager=mock_output_manager)
    mock_handle_post_processing.assert_called_once_with(
        args=args,
        input_manager=mock_input_manager,
        output_manager=mock_output_manager,
        task_id=task_id,
        should_flush_im_pool=should_flush_im_pool,
    )


@pytest.mark.parametrize("input_patch,produce_graphics", [(True, True), (False, True), (False, False), (True, False)])
def test_simulation_engine_run_tasks(input_patch: bool, produce_graphics: bool, mocker: MockerFixture) -> None:
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

    mock_handle_single_simulation_run = mocker.patch.object(
        TaskManager, "handle_single_simulation_run", return_value=None
    )
    mock_handle_post_processing = mocker.patch.object(TaskManager, "handle_post_processing", return_value=None)
    mock_deep_merge = mocker.patch.object(Utility, "deep_merge", return_value=None)

    TaskManager._handle_simulation_engine_run_tasks(
        args, mock_input_manager, mock_output_manager, task_id, produce_graphics, should_flush_im_pool=True
    )
    if input_patch:
        mock_deep_merge.assert_called_once_with(mock_input_manager.pool, args["input_patch"])
    else:
        mock_deep_merge.assert_not_called()

    mock_handle_single_simulation_run.assert_called_once_with(args, mock_output_manager)
    mock_handle_post_processing.assert_called_once_with(
        args=args,
        input_manager=mock_input_manager,
        output_manager=mock_output_manager,
        task_id=task_id,
        should_flush_im_pool=True,
        produce_graphics=produce_graphics,
        save_results=True,
    )


@pytest.mark.parametrize("produce_graphics", [True, False])
def test_postprocessing_tasks(produce_graphics: bool, mocker: MockerFixture) -> None:
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
    should_flush_im_pool = True

    mock_handle_post_processing = mocker.patch.object(TaskManager, "handle_post_processing", return_value=None)

    TaskManager._handle_postprocessing_tasks(
        args, mock_input_manager, mock_output_manager, task_id, produce_graphics, should_flush_im_pool
    )
    mock_handle_post_processing.assert_called_once_with(
        args=args,
        input_manager=mock_input_manager,
        output_manager=mock_output_manager,
        task_id=task_id,
        should_flush_im_pool=True,
        produce_graphics=produce_graphics,
    )


@pytest.mark.filterwarnings("ignore::DeprecationWarning", "ignore::UserWarning")
@pytest.mark.parametrize(
    "multi_run_args, expected_output_prefixes, expected_input_patches",
    [
        (
            {
                "task_type": "SENSITIVITY_ANALYSIS",
                "output_prefix": "Task 2",
                "log_verbosity": "errors",
                "sampler": "fractional_factorial",
                "random_seed": 42,
                "SA_load_balancing_start": 0,
                "SA_load_balancing_stop": 1,
                "skip_values": 0,
                "sampler_n": 2,
                "SA_input_variables": [
                    {
                        "variable_name": "animal.herd_information.calf_num",
                        "lower_bound": 6,
                        "upper_bound": 10,
                        "data_type": "int",
                    },
                    {
                        "variable_name": "animal.herd_information.cow_num",
                        "lower_bound": 98,
                        "upper_bound": 102,
                        "data_type": "int",
                    },
                    {
                        "variable_name": "animal.animal_config.management_decisions.breeding_start_day_h",
                        "lower_bound": 378,
                        "upper_bound": 382,
                        "data_type": "int",
                    },
                ],
            },
            [
                "Task 2 run 1",
                "Task 2 run 2",
                "Task 2 run 3",
                "Task 2 run 4",
                "Task 2 run 5",
                "Task 2 run 6",
                "Task 2 run 7",
                "Task 2 run 8",
            ],
            [
                {
                    "animal": {
                        "herd_information": {"calf_num": 10, "cow_num": 102},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 382}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 10, "cow_num": 98},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 382}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 10, "cow_num": 102},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 378}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 10, "cow_num": 98},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 378}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 6, "cow_num": 98},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 378}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 6, "cow_num": 102},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 378}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 6, "cow_num": 98},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 382}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 6, "cow_num": 102},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 382}},
                    }
                },
            ],
        ),
        (
            {
                "task_type": "SENSITIVITY_ANALYSIS",
                "output_prefix": "Task 3",
                "log_verbosity": "errors",
                "sampler": "sobol",
                "random_seed": 42,
                "SA_load_balancing_start": 0,
                "SA_load_balancing_stop": 1,
                "skip_values": 0,
                "sampler_n": 2,
                "SA_input_variables": [
                    {
                        "variable_name": "animal.herd_information.calf_num",
                        "lower_bound": 6,
                        "upper_bound": 10,
                        "data_type": "int",
                    },
                    {
                        "variable_name": "animal.herd_information.cow_num",
                        "lower_bound": 98,
                        "upper_bound": 102,
                        "data_type": "int",
                    },
                    {
                        "variable_name": "animal.animal_config.management_decisions.breeding_start_day_h",
                        "lower_bound": 378,
                        "upper_bound": 382,
                        "data_type": "int",
                    },
                ],
            },
            [
                "Task 3 run 01",
                "Task 3 run 02",
                "Task 3 run 03",
                "Task 3 run 04",
                "Task 3 run 05",
                "Task 3 run 06",
                "Task 3 run 07",
                "Task 3 run 08",
                "Task 3 run 09",
                "Task 3 run 10",
                "Task 3 run 11",
                "Task 3 run 12",
                "Task 3 run 13",
                "Task 3 run 14",
                "Task 3 run 15",
                "Task 3 run 16",
            ],
            [
                {
                    "animal": {
                        "herd_information": {"calf_num": 7, "cow_num": 101},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 381}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 6, "cow_num": 101},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 381}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 7, "cow_num": 99},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 381}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 7, "cow_num": 101},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 381}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 7, "cow_num": 99},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 381}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 6, "cow_num": 101},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 381}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 6, "cow_num": 99},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 381}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 6, "cow_num": 99},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 381}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 9, "cow_num": 98},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 379}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 8, "cow_num": 98},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 379}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 9, "cow_num": 101},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 379}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 9, "cow_num": 98},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 379}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 9, "cow_num": 101},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 379}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 8, "cow_num": 98},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 379}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 8, "cow_num": 101},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 379}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 8, "cow_num": 101},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 379}},
                    }
                },
            ],
        ),
        (
            {
                "task_type": "SENSITIVITY_ANALYSIS",
                "output_prefix": "Task 4",
                "log_verbosity": "errors",
                "sampler": "morris",
                "random_seed": 42,
                "SA_load_balancing_start": 0,
                "SA_load_balancing_stop": 1,
                "skip_values": 0,
                "sampler_n": 2,
                "SA_input_variables": [
                    {
                        "variable_name": "animal.herd_information.calf_num",
                        "lower_bound": 6,
                        "upper_bound": 10,
                        "data_type": "int",
                    },
                    {
                        "variable_name": "animal.herd_information.cow_num",
                        "lower_bound": 98,
                        "upper_bound": 102,
                        "data_type": "int",
                    },
                    {
                        "variable_name": "animal.animal_config.management_decisions.breeding_start_day_h",
                        "lower_bound": 378,
                        "upper_bound": 382,
                        "data_type": "int",
                    },
                ],
            },
            [
                "Task 4 run 1",
                "Task 4 run 2",
                "Task 4 run 3",
                "Task 4 run 4",
                "Task 4 run 5",
                "Task 4 run 6",
                "Task 4 run 7",
                "Task 4 run 8",
            ],
            [
                {
                    "animal": {
                        "herd_information": {"calf_num": 10, "cow_num": 100},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 380}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 7, "cow_num": 100},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 380}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 7, "cow_num": 98},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 380}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 7, "cow_num": 98},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 378}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 8, "cow_num": 102},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 380}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 6, "cow_num": 102},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 380}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 6, "cow_num": 99},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 380}},
                    }
                },
                {
                    "animal": {
                        "herd_information": {"calf_num": 6, "cow_num": 99},
                        "animal_config": {"management_decisions": {"breeding_start_day_h": 378}},
                    }
                },
            ],
        ),
    ],
)
def test_expand_sensitivity_analysis_args(
    multi_run_args: dict[str, Any],
    expected_output_prefixes: list[str],
    expected_input_patches: list[dict[str, dict[str, dict[str, Any]]]],
    task_manager: TaskManager,
) -> None:
    """Unit test for TaskManager._expand_sensitivity_analysis_args() with fractional_factorial and sobol methods
    as samplers."""
    result = task_manager._expand_sensitivity_analysis_args(multi_run_args)
    expected_output = [
        {
            "task_type": TaskType.SIMULATION_SINGLE_RUN,
            "output_prefix": expected_output_prefixes[i],
            "log_verbosity": "errors",
            "sampler": multi_run_args["sampler"],
            "random_seed": 42,
            "SA_load_balancing_start": 0,
            "SA_load_balancing_stop": 1,
            "skip_values": 0,
            "sampler_n": 2,
            "SA_input_variables": [
                {
                    "variable_name": "animal.herd_information.calf_num",
                    "lower_bound": 6,
                    "upper_bound": 10,
                    "data_type": "int",
                },
                {
                    "variable_name": "animal.herd_information.cow_num",
                    "lower_bound": 98,
                    "upper_bound": 102,
                    "data_type": "int",
                },
                {
                    "variable_name": "animal.animal_config.management_decisions.breeding_start_day_h",
                    "lower_bound": 378,
                    "upper_bound": 382,
                    "data_type": "int",
                },
            ],
            "input_patch": expected_input_patches[i],
        }
        for i in range(len(expected_output_prefixes))
    ]

    assert result == expected_output


@pytest.mark.parametrize(
    "multi_run_args",
    [
        {
            "task_type": "SENSITIVITY_ANALYSIS",
            "output_prefix": "Task 4",
            "log_verbosity": "errors",
            "sampler": "invalid_sampler",
            "SA_load_balancing_start": 0,
            "SA_load_balancing_stop": 1,
            "SA_input_variables": [
                {
                    "variable_name": "animal.herd_information.calf_num",
                    "lower_bound": 6,
                    "upper_bound": 10,
                    "data_type": "int",
                },
                {
                    "variable_name": "animal.herd_information.cow_num",
                    "lower_bound": 98,
                    "upper_bound": 102,
                    "data_type": "int",
                },
                {
                    "variable_name": "animal.animal_config.management_decisions.breeding_start_day_h",
                    "lower_bound": 378,
                    "upper_bound": 382,
                    "data_type": "int",
                },
            ],
        },
        {
            "task_type": "SENSITIVITY_ANALYSIS",
            "output_prefix": "Task 5",
            "log_verbosity": "warning",
            "sampler": "random_sampler",
            "SA_load_balancing_start": 0,
            "SA_load_balancing_stop": 1,
            "SA_input_variables": [
                {
                    "variable_name": "animal.herd_information.calf_num",
                    "lower_bound": 6,
                    "upper_bound": 10,
                    "data_type": "int",
                },
                {
                    "variable_name": "animal.herd_information.cow_num",
                    "lower_bound": 98,
                    "upper_bound": 102,
                    "data_type": "int",
                },
                {
                    "variable_name": "animal.animal_config.management_decisions.breeding_start_day_h",
                    "lower_bound": 378,
                    "upper_bound": 382,
                    "data_type": "int",
                },
            ],
        },
    ],
)
def test_expand_sensitivity_analysis_args_invalid_sampler(
    multi_run_args: dict[str, Any],
    mock_output_manager: OutputManager,
    task_manager: TaskManager,
    mocker: MockerFixture,
) -> None:
    """Unit test for TaskManager._expand_sensitivity_analysis_args() with invalid sampler"""
    mock_add_log = mocker.patch.object(mock_output_manager, "add_log")
    task_manager.output_manager = mock_output_manager

    with pytest.raises(ValueError) as exception_raised:
        task_manager._expand_sensitivity_analysis_args(multi_run_args)

    mock_add_log.assert_called_once_with(
        "Invalid sampler",
        f"The sampler {multi_run_args['sampler']} is not supported",
        {
            "class": TaskManager.__name__,
            "function": TaskManager.task.__name__,
            "units": MeasurementUnits.UNITLESS,
            "output_prefix": multi_run_args["output_prefix"],
        },
    )
    assert str(exception_raised.value) == f"INVALID SAMPLER: The sampler {multi_run_args['sampler']} is not supported"


@pytest.mark.parametrize(
    "single_run_tasks, produce_graphics, metadata_depth_limit",
    [
        (
            [
                {
                    "task_type": TaskType.SIMULATION_SINGLE_RUN,
                    "metadata_file_path": Path("input/metadata/default_metadata.json"),
                    "output_prefix": "default",
                    "log_verbosity": LogVerbosity.LOGS,
                    "random_seed": 42,
                    "properties_file_path": Path("input/metadata/properties/default.json"),
                    "comparison_properties_file_path": Path("input/metadata/properties/default.json"),
                    "variable_name_style": "basic",
                    "exclude_info_maps": False,
                    "init_herd": False,
                    "save_animals": False,
                    "save_animals_directory": Path("output"),
                    "filters_directory": Path("output/output_filters"),
                    "csv_output_directory": Path("output/CSVs"),
                    "json_output_directory": Path("output/JSONs"),
                    "report_directory": Path("output/reports"),
                    "graphics_directory": Path("output/graphics"),
                    "logs_directory": Path("output/logs"),
                    "suppress_log_files": False,
                    "output_pool_path": Path("."),
                    "multi_run_counts": 4,
                    "sampler": "sobol",
                    "skip_values": 0,
                    "sampler_n": 2,
                    "SA_load_balancing_start": 0,
                    "SA_load_balancing_stop": 1,
                    "input_patch": None,
                    "task_id": 1,
                },
                {
                    "task_type": TaskType.SIMULATION_SINGLE_RUN,
                    "metadata_file_path": Path("input/metadata/default_metadata.json"),
                    "output_prefix": "default",
                    "log_verbosity": LogVerbosity.WARNINGS,
                    "random_seed": 31415,
                    "properties_file_path": Path("input/metadata/properties/default.json"),
                    "comparison_properties_file_path": Path("input/metadata/properties/default.json"),
                    "variable_name_style": "basic",
                    "exclude_info_maps": False,
                    "init_herd": False,
                    "save_animals": False,
                    "save_animals_directory": Path("output"),
                    "filters_directory": Path("output/output_filters"),
                    "csv_output_directory": Path("output/CSVs"),
                    "json_output_directory": Path("output/JSONs"),
                    "report_directory": Path("output/reports"),
                    "graphics_directory": Path("output/graphics"),
                    "logs_directory": Path("output/logs"),
                    "suppress_log_files": False,
                    "output_pool_path": Path("."),
                    "multi_run_counts": 4,
                    "sampler": "sobol",
                    "skip_values": 0,
                    "sampler_n": 2,
                    "SA_load_balancing_start": 0,
                    "SA_load_balancing_stop": 1,
                    "input_patch": None,
                    "task_id": 1,
                },
            ],
            True,
            10,
        ),
        (
            [
                {
                    "task_type": "HERD_INITIALIZATION",
                    "metadata_file_path": "input/metadata/default_metadata.json",
                    "output_prefix": "herd_init",
                    "save_animals": True,
                    "log_verbosity": "errors",
                    "random_seed": 42,
                },
                {
                    "task_type": "SENSITIVITY_ANALYSIS",
                    "output_prefix": "Task 5",
                    "log_verbosity": "errors",
                    "sampler": "fractional_factorial",
                    "random_seed": 42,
                    "SA_load_balancing_start": 0,
                    "SA_load_balancing_stop": 1,
                    "SA_input_variables": [
                        {
                            "variable_name": "animal.herd_information.calf_num",
                            "lower_bound": 6,
                            "upper_bound": 10,
                            "data_type": "int",
                        },
                        {
                            "variable_name": "animal.herd_information.cow_num",
                            "lower_bound": 98,
                            "upper_bound": 102,
                            "data_type": "int",
                        },
                        {
                            "variable_name": "animal.animal_config.management_decisions.breeding_start_day_h",
                            "lower_bound": 378,
                            "upper_bound": 382,
                            "data_type": "int",
                        },
                    ],
                },
            ],
            False,
            8,
        ),
    ],
)
def test_run_tasks(
    single_run_tasks: list[dict[str, Any]],
    produce_graphics: bool,
    metadata_depth_limit: int,
    task_manager: TaskManager,
    mocker: MockerFixture,
) -> None:
    """Unit tests for TaskManager._run_tasks() with all tasks run successfully"""
    task_manager = TaskManager()
    mock_task = mocker.patch.object(task_manager, "task")
    mock_task.return_value = None

    mock_pool = mocker.patch("multiprocessing.Pool")
    mock_pool.return_value.imap = lambda func, args: map(func, args)
    task_manager.pool = multiprocessing.Pool(len(single_run_tasks), maxtasksperchild=1)

    task_manager._run_tasks(
        single_run_tasks,
        produce_graphics=produce_graphics,
        metadata_depth_limit=metadata_depth_limit,
        workers=1,
        metadata_path=Path("metadata/path"),
    )

    mock_task_call_list = [
        call(
            single_run_task,
            metadata_path=Path("metadata/path"),
            produce_graphics=produce_graphics,
            metadata_depth_limit=metadata_depth_limit,
            workers=1,
        )
        for single_run_task in single_run_tasks
    ]
    mock_task.assert_has_calls(mock_task_call_list)


@pytest.mark.parametrize(
    "single_run_tasks, produce_graphics, metadata_depth_limit, task_return_values",
    [
        (
            [
                {"dummy": "task"},
                {
                    "task_type": TaskType.SIMULATION_SINGLE_RUN,
                    "metadata_file_path": Path("input/metadata/default_metadata.json"),
                    "output_prefix": "default",
                    "log_verbosity": LogVerbosity.WARNINGS,
                    "random_seed": 42,
                    "properties_file_path": Path("input/metadata/properties/default.json"),
                    "comparison_properties_file_path": Path("input/metadata/properties/default.json"),
                    "variable_name_style": "verbose",
                    "exclude_info_maps": False,
                    "init_herd": False,
                    "save_animals": False,
                    "save_animals_directory": Path("output"),
                    "filters_directory": Path("output/output_filters"),
                    "csv_output_directory": Path("output/CSVs"),
                    "json_output_directory": Path("output/JSONs"),
                    "report_directory": Path("output/reports"),
                    "graphics_directory": Path("output/graphics"),
                    "logs_directory": Path("output/logs"),
                    "suppress_log_files": False,
                    "output_pool_path": Path("."),
                    "multi_run_counts": 4,
                    "sampler": "sobol",
                    "skip_values": 0,
                    "sampler_n": 2,
                    "SA_load_balancing_start": 0,
                    "SA_load_balancing_stop": 1,
                    "input_patch": None,
                    "task_id": 1,
                },
            ],
            True,
            10,
            ["default (1)", None],
        ),
        (
            [
                {"dummy": "task"},
                {
                    "task_type": "SENSITIVITY_ANALYSIS",
                    "output_prefix": "Task 1",
                    "log_verbosity": "errors",
                    "sampler": "fractional_factorial",
                    "random_seed": 42,
                    "SA_load_balancing_start": 0,
                    "SA_load_balancing_stop": 1,
                    "SA_input_variables": [
                        {
                            "variable_name": "animal.herd_information.calf_num",
                            "lower_bound": 6,
                            "upper_bound": 10,
                            "data_type": "int",
                        },
                        {
                            "variable_name": "animal.herd_information.cow_num",
                            "lower_bound": 98,
                            "upper_bound": 102,
                            "data_type": "int",
                        },
                        {
                            "variable_name": "animal.animal_config.management_decisions.breeding_start_day_h",
                            "lower_bound": 378,
                            "upper_bound": 382,
                            "data_type": "int",
                        },
                    ],
                },
            ],
            False,
            8,
            ["default (1)", None],
        ),
        (
            [
                {"dummy": "task"},
                {"dummy": "task"},
                {
                    "task_type": "SIMULATION_SINGLE_RUN",
                    "metadata_file_path": "input/metadata/default_metadata.json",
                    "output_prefix": "Task 2",
                    "log_verbosity": "errors",
                    "random_seed": 42,
                },
            ],
            False,
            8,
            ["default (1)", "default (2)", None],
        ),
    ],
)
def test_run_tasks_fail(
    single_run_tasks: list[dict[str, Any]],
    produce_graphics: bool,
    metadata_depth_limit: int,
    task_return_values: list[str | None],
    mock_output_manager: OutputManager,
    task_manager: TaskManager,
    mocker: MockerFixture,
) -> None:
    """Unit tests for TaskManager._run_tasks() with failed tasks."""
    task_manager = TaskManager()
    mock_task = mocker.patch.object(task_manager, "task")
    mock_task.side_effect = task_return_values

    mock_om_init = mocker.patch("RUFAS.task_manager.OutputManager", return_value=mock_output_manager)
    mock_add_error = mocker.patch.object(mock_output_manager, "add_error", return_value=None)

    mock_pool = mocker.patch("multiprocessing.Pool")

    mock_pool.return_value.imap = lambda func, args: map(func, args)
    task_manager.pool = multiprocessing.Pool(len(single_run_tasks), maxtasksperchild=1)

    task_manager._run_tasks(
        single_run_tasks,
        produce_graphics=produce_graphics,
        metadata_depth_limit=metadata_depth_limit,
        workers=1,
        metadata_path=Path("metadata/path"),
    )

    mock_om_init.assert_called_once()
    info_map = {"class": TaskManager.__name__, "function": TaskManager._run_tasks.__name__}
    failed = [fail for fail in task_return_values if fail is not None]
    mock_add_error.assert_called_once_with(
        "Task(s) failed", f"Failed task(s) and output prefix are: {failed}", info_map
    )


def test_call_handler(mocker: MockerFixture) -> None:
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
    should_flush_im_pool = True

    # Call the call_handler method
    mock_handle_post_processing = mocker.patch.object(TaskManager, "_handle_postprocessing_tasks", return_value=None)

    TaskManager.call_handler(
        mock_handle_post_processing,
        args=args,
        input_manager=mock_input_manager,
        output_manager=mock_output_manager,
        task_id=task_id,
        produce_graphics=produce_graphics,
        should_flush_im_pool=should_flush_im_pool,
    )

    mock_handle_post_processing.assert_called_once_with(
        args, mock_input_manager, mock_output_manager, task_id, produce_graphics, should_flush_im_pool
    )


def test_input_data_audit_tasks(mocker: MockerFixture) -> None:
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

    mock_handle_input_data_audit = mocker.patch.object(TaskManager, "handle_input_data_audit", return_value=None)
    mock_handle_post_processing = mocker.patch.object(TaskManager, "handle_post_processing", return_value=None)

    mock_input_manager = mocker.MagicMock(auto_spec=InputManager)
    mocker.patch("RUFAS.task_manager.InputManager", return_value=mock_input_manager)

    mock_output_manager = mocker.MagicMock(auto_spec=OutputManager)
    produce_graphic = False
    should_flush_im_pool = True

    TaskManager._handle_input_data_audit_tasks(
        args=args,
        input_manager=mock_input_manager,
        output_manager=mock_output_manager,
        task_id=task_id,
        produce_grahics=produce_graphic,
        should_flush_im_pool=should_flush_im_pool,
    )

    mock_handle_input_data_audit.assert_called_once_with(
        args=args, input_manager=mock_input_manager, output_manager=mock_output_manager, eager_termination=False
    )
    mock_handle_post_processing.assert_called_once_with(
        args=args,
        input_manager=mock_input_manager,
        output_manager=mock_output_manager,
        task_id=task_id,
        should_flush_im_pool=True,
    )


def test_handle_data_collection_app_update(mocker: MockerFixture, task_manager: TaskManager) -> None:
    """Tests that the DataCollectionAppUpdater is initialized and called correctly."""
    mock_init = mocker.patch("RUFAS.data_collection_app_updater.DataCollectionAppUpdater.__init__", return_value=None)
    mock_update = mocker.patch(
        "RUFAS.data_collection_app_updater.DataCollectionAppUpdater.update_data_collection_app", return_value=None
    )
    args = {"task_manager_metadata_properties": {"task_properties": {"dummy": "property"}}}

    task_manager._handle_data_collection_app_update(args, mocker.MagicMock(), mocker.MagicMock(), "test", False, False)

    mock_init.assert_called_once()
    mock_update.assert_called_once()


@pytest.mark.parametrize(
    "dependencies, installed_versions, missing_package, expected_error, error_message_part",
    [
        # Case 1: all dependencies are satisfied
        (
            ["numpy==2.2.0"],
            {"numpy": "2.2.0"},
            None,
            None,
            None,
        ),
        # Case 2: missing package
        (
            ["numpy>=1.24.0"],
            {},
            "numpy",
            RuntimeError,
            "Required package 'numpy' is not installed",
        ),
        # Case 3: wrong version
        (
            ["numpy>=2.0.0"],
            {"numpy": "1.24.0"},
            None,
            RuntimeError,
            "does not satisfy required version",
        ),
    ],
)
def test_check_dependencies(
    dependencies: list[str],
    installed_versions: dict[str, str],
    missing_package: str | None,
    expected_error: type[Exception] | None,
    error_message_part: str | None,
    mocker: MockerFixture,
) -> None:
    """Test the check_dependencies method of TaskManager."""
    task_manager = TaskManager()
    mock_log_error = mocker.patch.object(task_manager.output_manager, "add_error")
    mocker.patch("builtins.open", mocker.mock_open(read_data=b""))
    mock_tomllib_load = mocker.patch("tomllib.load")
    mock_tomllib_load.return_value = {"project": {"dependencies": dependencies}}

    mocker.patch(
        "RUFAS.task_manager.get_installed_version",
        side_effect=lambda pkg: (
            (_ for _ in ()).throw(PackageNotFoundError()) if pkg == missing_package else installed_versions[pkg]
        ),
    )

    if expected_error:
        with pytest.raises(expected_error, match=error_message_part):
            task_manager.check_dependencies()
        assert mock_log_error.called
    else:
        task_manager.check_dependencies()
        mock_log_error.assert_not_called()


def test_check_dependencies_invalid_requirement(mocker: MockerFixture) -> None:
    """Test that check_dependencies raises an error for invalid dependency strings."""
    task_manager = TaskManager()
    mock_log_error = mocker.patch.object(task_manager.output_manager, "add_error")
    mocker.patch("builtins.open", mocker.mock_open(read_data=b""))
    mock_tomllib_load = mocker.patch("tomllib.load")
    mock_tomllib_load.return_value = {"project": {"dependencies": ["numpy>>1.0"]}}

    with pytest.raises(RuntimeError, match="Invalid dependency string"):
        task_manager.check_dependencies()

    mock_log_error.assert_called_once()


@pytest.mark.parametrize(
    "python_version, pyproject_data, open_side_effect, load_side_effect, expected_error, error_message",
    [
        # Valid case, no exception expected
        ((3, 12, 1), {"project": {"requires-python": ">=3.12, <=3.13"}}, None, None, None, None),
        # tomllib not available (Python 3.10 or earlier)
        (
            (3, 10, 0),
            None,
            None,
            ImportError,
            RuntimeError,
            f"RUFAS requires Python {str(MINIMUM_PYTHON_VERSION)} or later. Please upgrade your Python version.",
        ),
        # pyproject.toml not found
        ((3, 12, 1), None, FileNotFoundError, None, RuntimeError, "pyproject.toml file not found"),
        # Missing requires-python field
        ((3, 12, 1), {"project": {}}, None, None, RuntimeError, "The 'requires-python' field is missing"),
        # Incompatible Python version
        (
            (3, 11, 0),
            {"project": {"requires-python": ">=3.12, <=3.13"}},
            None,
            None,
            RuntimeError,
            "RUFAS requires Python >=3.12, <=3.13",
        ),
        # Unexpected error
        (
            (3, 12, 1),
            None,
            RuntimeError("Unexpected error"),
            None,
            RuntimeError,
            "An unexpected error occurred while checking the Python version",
        ),
        # Python version mismatch
        (
            (3, 12, 1),
            {"project": {"requires-python": ">=3.12"}},
            None,
            None,
            None,
            "RUFAS requires Python >=3.12",
        ),
    ],
)
def test_check_python_version(
    mocker: MockerFixture,
    python_version: tuple[int, int, int],
    pyproject_data: dict[str, Any],
    open_side_effect: Exception | None,
    load_side_effect: Exception | None,
    expected_error: Type[Exception] | None,
    error_message: str | None,
) -> None:
    """Test the check_python_version method of TaskManager."""
    task_manager = TaskManager()
    version_mock = SimpleNamespace(major=python_version[0], minor=python_version[1], micro=python_version[2])
    mocker.patch("sys.version_info", version_mock)
    mock_tomllib_load = mocker.patch("tomllib.load")
    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data=b""))
    mock_log_error = mocker.patch.object(task_manager.output_manager, "add_error")

    if open_side_effect:
        mock_open.side_effect = open_side_effect
    if load_side_effect:
        mock_tomllib_load.side_effect = load_side_effect
    if pyproject_data:
        mock_tomllib_load.return_value = pyproject_data

    if expected_error:
        with pytest.raises(expected_error, match=error_message):
            task_manager.check_python_version()
    else:
        if error_message and "RUFAS requires Python >=3.12" in error_message:
            mocker.patch("RUFAS.task_manager.MINIMUM_PYTHON_VERSION", Version("3.11"))
            task_manager.check_python_version()
            mock_log_error.assert_called_once_with(
                "Python pyproject.toml version mismatch",
                mocker.ANY,
                {"class": TaskManager.__name__, "function": "check_python_version"},
            )
        else:
            task_manager.check_python_version()
            mock_log_error.assert_not_called()


@pytest.mark.parametrize(
    "pyproject_data, open_side_effect, load_side_effect, expected_version, expected_log_error",
    [
        # Valid case: RUFAS version is successfully read
        ({"project": {"version": "1.2.3"}}, None, None, "1.2.3", None),
        # pyproject.toml file not found
        (None, FileNotFoundError, None, "Unknown", "Unable to read RUFAS version from pyproject.toml file."),
        # Missing 'version' field in pyproject.toml
        ({"project": {}}, None, None, "Unknown", "Unable to read RUFAS version from pyproject.toml file."),
        # Unexpected error during file read or parsing
        (
            None,
            None,
            RuntimeError("Unexpected error"),
            "Unknown",
            "Unable to read RUFAS version from pyproject.toml file.",
        ),
    ],
)
def test_get_rufas_version(
    mocker: MockerFixture,
    pyproject_data: dict[str, Any] | None,
    open_side_effect: Exception | None,
    load_side_effect: Exception | None,
    expected_version: str,
    expected_log_error: str | None,
) -> None:
    """Test the get_rufas_version method of TaskManager."""
    task_manager = TaskManager()
    mock_tomllib_load = mocker.patch("tomllib.load")
    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data=b""))
    mock_log_error = mocker.patch.object(task_manager.output_manager, "add_error")

    if open_side_effect:
        mock_open.side_effect = open_side_effect
    if load_side_effect:
        mock_tomllib_load.side_effect = load_side_effect
    if pyproject_data:
        mock_tomllib_load.return_value = pyproject_data

    version = task_manager.get_rufas_version()

    assert version == expected_version

    if expected_log_error:
        mock_log_error.assert_called_once_with(
            "Error reading RUFAS version",
            mocker.ANY,
            {"class": TaskManager.__name__, "function": "get_rufas_version"},
        )
    else:
        mock_log_error.assert_not_called()
