from importlib.metadata import PackageNotFoundError, version as get_installed_version
import multiprocessing
import random
import sys
import traceback
from enum import Enum
from functools import partial
from packaging.requirements import Requirement, InvalidRequirement
from packaging.specifiers import SpecifierSet
from packaging.version import Version
from pathlib import Path
from typing import Any, Callable

import numpy
from SALib.sample import ff as fractional_factorial_sampler
from SALib.sample import sobol as sobol_sampler
from SALib.sample import morris as morris_sampler

from RUFAS.biophysical.animal.herd_factory import HerdFactory
from RUFAS.data_collection_app_updater import DataCollectionAppUpdater
from RUFAS.e2e_test_results_handler import E2ETestResultsHandler
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import LogVerbosity, OutputManager
from RUFAS.simulation_engine import SimulationEngine
from RUFAS.units import MeasurementUnits
from RUFAS.util import Utility

PYPROJECT_FILE_PATH = Path("pyproject.toml")
MINIMUM_PYTHON_VERSION = Version("3.12")

"""These constants define the minimum and maximum integers that can be passed to Numpy's random.seed method."""
NUMPY_RANDOM_SEED_LOWER_BOUND = 0
NUMPY_RANDOM_SEED_UPPER_BOUND = 2**32 - 1


class TaskType(Enum):
    """Enum for different task types handled by TaskManager."""

    HERD_INITIALIZATION = "Herd Initialization"
    SIMULATION_SINGLE_RUN = "A single simulation run"
    SIMULATION_MULTI_RUN = "Multiple simulation with different random seeds"
    SENSITIVITY_ANALYSIS = "Run sensitivity analysis"
    INPUT_DATA_AUDIT = "Validates input data and saves metadata properties as CSV"
    END_TO_END_TESTING = "Run e2e testing"
    POST_PROCESSING = "Bypass simulation engine and directly run Output Manager"
    COMPARE_METADATA_PROPERTIES = "Compares 2 metadata properties files and saves the differences in a .txt file"
    DATA_COLLECTION_APP_UPDATE = "Updates the schema and interface of the Data Collection App"
    UPDATE_E2E_TEST_RESULTS = "Updates end-to-end expected test results with new actual results"

    @staticmethod
    def from_string(input_str: str) -> "TaskType":
        """Converts a string to a TaskType enum."""
        normalized_input = "_".join(input_str.strip().upper().split())
        try:
            return TaskType[normalized_input]
        except KeyError:
            raise ValueError(f"The string '{input_str}' is not a match with any acceptable TaskType.")

    def is_multi_run(self) -> bool:
        """Checks if the task type involves multiple runs."""
        return self in [TaskType.SIMULATION_MULTI_RUN, TaskType.SENSITIVITY_ANALYSIS]


class TaskManager:
    """Manager class for handling tasks related to simulations and analyses."""

    INPUT_DATA_CSV_WORKING_FOLDER = Path("output/saved_pool_working_folder/")

    def __init__(self) -> None:
        self.output_manager = OutputManager()

    def start(
        self,
        metadata_path: Path,
        verbosity: LogVerbosity,
        exclude_info_maps: bool,
        output_directory: Path,
        logs_directory: Path,
        clear_output_directory: bool,
        produce_graphics: bool,
        suppress_log_files: bool,
        metadata_depth_limit: int,
    ) -> None:
        """
        Initializes and starts the task management process.

        Parameters
        ----------
        metadata_path : Path
            Path to the metadata file that contains task management inputs.
        verbosity : LogVerbosity
            Level of verbosity for logging.
        exclude_info_maps : bool
            Flag to exclude information maps.
        output_directory : Path
            Path to the directory where outputs will be saved.
        logs_directory : Path
            Path to the directory where logs from the Task Manager will be saved.
        clear_output_directory : bool
            Whether to clear the output directory.
        produce_graphics : bool
            Whether to produce graphics.
        suppress_log_files : bool
            Whether to write logs from the Task Manager to output files.
        metadata_depth_limit : int
            Override value for maximum metadata properties depth set in Input Manager.

        """
        self.input_manager = InputManager(metadata_depth_limit)
        self.output_manager.run_startup_sequence(
            verbosity=verbosity,
            exclude_info_maps=exclude_info_maps,
            output_directory=output_directory,
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
        self.check_python_version()
        self.check_dependencies()
        rufas_version = self.get_rufas_version()
        self.output_manager.print_credits(rufas_version)
        info_map = {
            "class": TaskManager.__name__,
            "function": TaskManager.start.__name__,
        }
        self.output_manager.add_log("Task Manager Start", "Task Manager Started.", info_map)
        is_data_valid = self.input_manager.start_data_processing(metadata_path, Path(""))
        task_config: dict[str, Any] = self.input_manager.get_data("tasks")
        for task in task_config.get("tasks", []):
            filters_path = Path(task["filters_directory"])
            self.output_manager.validate_filter_content(filters_path)

        if not is_data_valid:
            TaskManager.handle_post_processing(
                args={
                    "exclude_info_maps": exclude_info_maps,
                    "variable_name_style": "verbose",
                    "logs_directory": logs_directory,
                    "suppress_log_files": suppress_log_files,
                },
                input_manager=self.input_manager,
                output_manager=self.output_manager,
                task_id="TASK_MANAGER",
                should_flush_im_pool=True,
            )
            raise Exception("Task Manager's input data is invalid.")

        workers: int = task_config["parallel_workers"]
        self.output_manager.add_log(
            "Task Manager workers", f"Task Manager is going to run {workers} in parallel.", info_map
        )
        self.pool = multiprocessing.Pool(
            workers, maxtasksperchild=1
        )  # maxtasksperchild=1 to maintain isolation between tasks and ensure no memory leaks happens in IO Managers
        parsed_single_run_args, parsed_multi_run_args = self._parse_input_tasks()
        self.output_manager.add_log(
            "Task Manager parsed tasks",
            f"Parsed {len(parsed_single_run_args) + len(parsed_multi_run_args)} tasks args.",
            info_map,
        )
        expanded_args = self._expand_multi_runs_to_single_runs(parsed_multi_run_args)
        runnable_args = parsed_single_run_args + expanded_args
        self.output_manager.add_log(
            "Task Manager expanded tasks",
            f"Expanded task args to {len(runnable_args)}. Starting the tasks...",
            info_map,
        )
        for i in range(len(runnable_args)):
            runnable_args[i]["task_id"] = f"{i + 1}/{len(runnable_args)}"
        self._run_tasks(runnable_args, produce_graphics, metadata_depth_limit, workers, metadata_path)

        export_input_data_to_csv: bool = task_config.get("export_input_data_to_csv", False)
        input_data_csv_export_path: str = task_config.get("input_data_csv_export_path", "")
        input_data_csv_import_path: str = task_config.get("input_data_csv_import_path", "")
        is_end_to_end_test_task = any(task.get("task_type") == TaskType.END_TO_END_TESTING for task in runnable_args)
        if is_end_to_end_test_task:
            output_prefixes: list[str] = [runnable_args[i]["output_prefix"] for i in range(len(runnable_args))]
            self.output_manager.add_log(
                "Summarizing e2e test results",
                f"Gathering e2e results for {output_prefixes}...",
                info_map,
            )
            json_output_directory = runnable_args[0]["json_output_directory"]
            self.output_manager.summarize_e2e_test_results(json_output_directory, output_prefixes)

        TaskManager.handle_post_processing(
            args={
                "exclude_info_maps": exclude_info_maps,
                "variable_name_style": "verbose",
                "logs_directory": logs_directory,
                "suppress_log_files": suppress_log_files,
                "input_data_csv_export_path": Path(input_data_csv_export_path),
                "input_data_csv_import_path": Path(input_data_csv_import_path),
            },
            input_manager=self.input_manager,
            output_manager=self.output_manager,
            task_id="TASK_MANAGER",
            should_flush_im_pool=False,
            export_input_data_to_csv=export_input_data_to_csv,
        )

    def get_rufas_version(self) -> str:
        """
        Returns the current version of RUFAS.

        Returns
        -------
        str
            Version of RUFAS or "Unknown" if the version of Python version earlier than 3.12.
        """
        try:
            with open(PYPROJECT_FILE_PATH, "rb") as pyproject_file:
                import tomllib

                rufas_version = tomllib.load(pyproject_file)["project"]["version"]
        except Exception as e:
            self.output_manager.add_error(
                "Error reading RUFAS version",
                f"Unable to read RUFAS version from pyproject.toml file. {e}",
                {"class": self.__class__.__name__, "function": self.get_rufas_version.__name__},
            )
            return "Unknown"
        return str(rufas_version)

    def check_dependencies(self) -> None:
        """
        Checks if the required dependencies are installed.

        Raises
        ------
        ImportError
            If a required dependency is not installed.
        """
        import tomllib

        with open(PYPROJECT_FILE_PATH, "rb") as pyproject_file:
            project_data = tomllib.load(pyproject_file)

        dependencies = project_data.get("project", {}).get("dependencies", [])
        for dependency in dependencies:
            try:
                requirement = Requirement(dependency)
            except InvalidRequirement as e:
                self.output_manager.add_error(
                    "Invalid requirement syntax",
                    f"The dependency string '{dependency}' is invalid. Error: {e}",
                    {"class": TaskManager.__name__, "function": TaskManager.check_dependencies.__name__},
                )
                raise RuntimeError(f"Invalid dependency string in pyproject.toml: {dependency!r}") from e

            package_name = requirement.name

            try:
                installed_version = get_installed_version(package_name)
            except PackageNotFoundError as e:
                self.output_manager.add_error(
                    "Missing dependency",
                    f"Required package '{package_name}' is not installed. We suggest running 'pip install .'"
                    " to install all dependencies at required minimum levels.",
                    {"class": TaskManager.__name__, "function": TaskManager.check_dependencies.__name__},
                )
                raise RuntimeError(f"[ERROR] Required package '{package_name}' is not installed.") from e

            if requirement.specifier and not requirement.specifier.contains(installed_version):
                self.output_manager.add_error(
                    "Dependency version doesn't meet requirements",
                    f"Required package '{package_name}' version does not match. Installed: {installed_version}, "
                    f"Required: {requirement.specifier}. We suggest running 'pip install .' to install all"
                    " dependencies at required minimum levels.",
                    {"class": TaskManager.__name__, "function": TaskManager.check_dependencies.__name__},
                )
                raise RuntimeError(
                    f"[ERROR] {package_name}=={installed_version} does not satisfy required version:"
                    f" {requirement.specifier}"
                )

    def check_python_version(self) -> None:
        """
        Checks if the Python version meets version range set in pyproject.toml.
        """
        user_python_version = Version(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        try:
            import tomllib

            with open(PYPROJECT_FILE_PATH, "rb") as pyproject_file:
                pyproject_data = tomllib.load(pyproject_file)
            requires_python = pyproject_data["project"]["requires-python"]
            specifier = SpecifierSet(requires_python)
            if user_python_version not in specifier:
                self.output_manager.add_error(
                    "Python version mismatch",
                    f"RUFAS requires Python {requires_python}, but you are using Python {user_python_version}. "
                    "Please upgrade or downgrade your Python version to match the required version range.",
                    {"class": TaskManager.__name__, "function": TaskManager.check_python_version.__name__},
                )
                raise RuntimeError(f"Please check your Python version. RUFAS requires Python {requires_python}.")
            if MINIMUM_PYTHON_VERSION not in specifier:
                self.output_manager.add_error(
                    "Python pyproject.toml version mismatch",
                    f"The pyproject.toml file says RUFAS requires Python {requires_python}, but the minimum version set"
                    f" in TM is {MINIMUM_PYTHON_VERSION}. Please check both versions and make sure they agree on"
                    " the correct version range.",
                    {"class": TaskManager.__name__, "function": TaskManager.check_python_version.__name__},
                )
        except ImportError:
            raise RuntimeError(
                f"RUFAS requires Python {str(MINIMUM_PYTHON_VERSION)} or later. Please upgrade your Python version."
            )
        except FileNotFoundError:
            raise RuntimeError(
                f"pyproject.toml file not found. Ensure the file exists at the specified path: {PYPROJECT_FILE_PATH}."
            )
        except KeyError:
            raise RuntimeError("The 'requires-python' field is missing in pyproject.toml.")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred while checking the Python version: {e}")

    def _parse_input_tasks(self) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """
        Parses input tasks into single and multiple run tasks.

        Returns
        -------
        tuple[list[dict[str, Any]], list[dict[str, Any]]]
            Parsed single run and multi-run task arguments.
        """
        parsed_single_run_args: list[dict[str, Any]] = []
        parsed_multi_run_args: list[dict[str, Any]] = []
        task_config: dict[str, Any] = self.input_manager.get_data("tasks")
        tasks_from_input: list[dict[str, Any]] = task_config.get("tasks")
        task_manager_metadata_properties = self.input_manager.get_metadata("properties")
        export_input_data_to_csv = task_config.get("export_input_data_to_csv")
        input_data_csv_export_path = Path(task_config.get("input_data_csv_export_path"))
        input_data_csv_import_path = Path(task_config.get("input_data_csv_import_path"))
        for input_task in tasks_from_input:
            input_task["task_type"] = TaskType.from_string(input_task["task_type"])
            input_task["input_patch"] = None
            input_task["metadata_file_path"] = Path(input_task["metadata_file_path"])
            input_task["properties_file_path"] = Path(input_task["properties_file_path"])
            input_task["comparison_properties_file_path"] = Path(input_task["comparison_properties_file_path"])
            input_task["convert_variable_table_path"] = (
                Path(input_task["convert_variable_table_path"]) if "convert_variable_table_path" in input_task else None
            )
            input_task["logs_directory"] = Path(input_task["logs_directory"])
            input_task["suppress_log_files"] = input_task["suppress_log_files"]
            input_task["save_animals_directory"] = Path(input_task["save_animals_directory"])
            input_task["filters_directory"] = Path(input_task["filters_directory"])
            input_task["csv_output_directory"] = Path(input_task["csv_output_directory"])
            input_task["json_output_directory"] = Path(input_task["json_output_directory"])
            input_task["report_directory"] = Path(input_task["report_directory"])
            input_task["graphics_directory"] = Path(input_task["graphics_directory"])
            input_task["output_pool_path"] = Path(input_task["output_pool_path"])
            saved_output_pools = []
            for saved_pool in input_task.get("saved_output_pools", []):
                saved_output_pools.append({"name": saved_pool["name"], "path": Path(saved_pool["path"])})
            input_task["saved_output_pools"] = saved_output_pools
            input_task["export_input_data_to_csv"] = export_input_data_to_csv
            input_task["input_data_csv_export_path"] = input_data_csv_export_path
            input_task["input_data_csv_import_path"] = input_data_csv_import_path
            input_task["task_manager_metadata_properties"] = task_manager_metadata_properties
            if input_task["task_type"].is_multi_run():
                parsed_multi_run_args.append(input_task)
            else:
                parsed_single_run_args.append(input_task)
        return parsed_single_run_args, parsed_multi_run_args

    def _expand_multi_runs_to_single_runs(self, multi_run_args: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Expands multi-run tasks into single-run tasks for execution.

        Parameters
        ----------
        multi_run_args : list[dict[str, Any]]
            list of multi-run task arguments.

        Returns
        -------
        list[dict[str, Any]]
            Expanded list of single-run tasks.
        """
        expanded_args: list[dict[str, Any]] = []
        task_type_to_expander_map = {
            TaskType.SIMULATION_MULTI_RUN: self._expand_simulation_multi_run_args,
            TaskType.SENSITIVITY_ANALYSIS: self._expand_sensitivity_analysis_args,
        }
        for multi_run_arg in multi_run_args:
            task_type = multi_run_arg["task_type"]
            expanded_args += task_type_to_expander_map[task_type](multi_run_arg)

        return expanded_args

    def _expand_simulation_multi_run_args(self, multi_run_args: dict[str, Any]) -> list[dict[str, Any]]:
        single_run_args = []
        for i in range(multi_run_args["multi_run_counts"]):
            new_args = multi_run_args.copy()
            new_args["task_type"] = TaskType.SIMULATION_SINGLE_RUN
            new_args["random_seed"] = random.randint(NUMPY_RANDOM_SEED_LOWER_BOUND, NUMPY_RANDOM_SEED_UPPER_BOUND)
            new_args["output_prefix"] = f"{new_args['output_prefix']} run {i + 1}"
            single_run_args.append(new_args)

        return single_run_args

    def _expand_sensitivity_analysis_args(self, multi_run_args: dict[str, Any]) -> list[dict[str, Any]]:
        """Expands sensitivity analysis multi-run tasks into single-run tasks."""

        SA_input_variables: list[dict[str, float | str]] = multi_run_args["SA_input_variables"]

        names: list[str] = [str(input_variable["variable_name"]) for input_variable in SA_input_variables]
        variables_count = len(names)
        bounds: list[list[float]] = [
            [float(input_variable["lower_bound"]), float(input_variable["upper_bound"])]
            for input_variable in SA_input_variables
        ]
        parsed_SA_input_variables = {
            "num_vars": variables_count,
            "names": names,
            "bounds": bounds,
            "sample_scaled": True,
        }

        data_type_str_to_class_map = {"float": float, "int": int}
        data_types = [data_type_str_to_class_map[input_variable["data_type"]] for input_variable in SA_input_variables]

        if multi_run_args["sampler"] == "fractional_factorial":
            sampled_values = fractional_factorial_sampler.sample(
                parsed_SA_input_variables, seed=multi_run_args["random_seed"]
            )
        elif multi_run_args["sampler"] == "sobol":
            sampled_values = sobol_sampler.sample(
                parsed_SA_input_variables,
                multi_run_args["sampler_n"],
                skip_values=multi_run_args["skip_values"],
                seed=multi_run_args["random_seed"],
            )
        elif multi_run_args["sampler"] == "morris":
            sampled_values = morris_sampler.sample(
                parsed_SA_input_variables, multi_run_args["sampler_n"], seed=multi_run_args["random_seed"]
            )
        else:
            self.output_manager.add_log(
                "Invalid sampler",
                f"The sampler {multi_run_args['sampler']} is not supported",
                {
                    "class": TaskManager.__name__,
                    "function": TaskManager.task.__name__,
                    "units": MeasurementUnits.UNITLESS,
                    "output_prefix": multi_run_args["output_prefix"],
                },
            )
            raise ValueError(f"INVALID SAMPLER: The sampler {multi_run_args['sampler']} is not supported")

        single_run_args = []

        digits = len(str(len(sampled_values)))
        start_sample = int(multi_run_args["SA_load_balancing_start"] * len(sampled_values))
        stop_sample = int(multi_run_args["SA_load_balancing_stop"] * len(sampled_values))

        for sample_number in range(start_sample, stop_sample):
            new_args = multi_run_args.copy()
            new_args["task_type"] = TaskType.SIMULATION_SINGLE_RUN
            run_number = f"{sample_number + 1}".zfill(digits)
            new_args["output_prefix"] = f"{new_args['output_prefix']} run {run_number}"
            new_args["input_patch"] = {
                names[variable_number]: data_types[variable_number](sampled_values[sample_number, variable_number])
                for variable_number in range(variables_count)
            }
            new_args["input_patch"] = Utility.flatten_keys_to_nested_structure(new_args["input_patch"])
            single_run_args.append(new_args)

        return single_run_args

    def _run_tasks(
        self,
        single_run_args: list[dict[str, Any]],
        produce_graphics: bool,
        metadata_depth_limit: int,
        workers: int,
        metadata_path: Path,
    ) -> None:
        """Runs the tasks based on the provided arguments."""
        task_with_args = partial(
            self.task,
            produce_graphics=produce_graphics,
            metadata_depth_limit=metadata_depth_limit,
            workers=workers,
            metadata_path=metadata_path,
        )
        results = self.pool.imap(task_with_args, single_run_args)
        failed = []
        for result in results:
            if result is not None:
                failed.append(result)

        if len(failed) > 0:
            info_map = {"class": TaskManager.__name__, "function": TaskManager._run_tasks.__name__}
            om = OutputManager()
            om.add_error("Task(s) failed", f"Failed task(s) and output prefix are: {failed}", info_map)

    @staticmethod
    def call_handler(
        handler: Callable[..., None],
        args: dict[str, Any],
        input_manager: InputManager,
        output_manager: OutputManager,
        task_id: Any,
        produce_graphics: bool,
        should_flush_im_pool: bool,
    ) -> None:
        """Wrapper function to call the function map with each of its arguments."""
        handler(args, input_manager, output_manager, task_id, produce_graphics, should_flush_im_pool)

    @staticmethod
    def task(
        args: dict[str, Any],
        produce_graphics: bool,
        workers: int,
        metadata_depth_limit: int | None,
        metadata_path: Path,
    ) -> str | None:
        """Executes a single task with specified arguments."""
        info_map = {
            "class": TaskManager.__name__,
            "function": TaskManager.task.__name__,
            "units": MeasurementUnits.UNITLESS,
        }
        task_id = args["task_id"]
        output_manager = OutputManager()

        validation_and_comparison_handlers = {
            TaskType.INPUT_DATA_AUDIT: TaskManager._handle_input_data_audit_tasks,
            TaskType.COMPARE_METADATA_PROPERTIES: TaskManager._handle_compare_metadata_properties_tasks,
        }
        simulation_and_analysis_handlers = {
            TaskType.HERD_INITIALIZATION: TaskManager._handle_herd_init_tasks,
            TaskType.SIMULATION_SINGLE_RUN: TaskManager._handle_simulation_engine_run_tasks,
            TaskType.POST_PROCESSING: TaskManager._handle_postprocessing_tasks,
            TaskType.END_TO_END_TESTING: TaskManager._handle_end_to_end_testing,
            TaskType.DATA_COLLECTION_APP_UPDATE: TaskManager._handle_data_collection_app_update,
            TaskType.UPDATE_E2E_TEST_RESULTS: TaskManager._handle_update_e2e_test_results,
        }
        try:
            task_type: TaskType = args["task_type"]
            is_end_to_end_test = (
                True if task_type in [TaskType.END_TO_END_TESTING, TaskType.UPDATE_E2E_TEST_RESULTS] else False
            )
            should_flush_im_pool = (
                False if task_type in [TaskType.END_TO_END_TESTING, TaskType.UPDATE_E2E_TEST_RESULTS] else True
            )
            output_manager.run_startup_sequence(
                verbosity=LogVerbosity(args["log_verbosity"]),
                exclude_info_maps=args["exclude_info_maps"],
                output_directory=Path("output/"),
                clear_output_directory=False,
                chunkification=args["chunkification"],
                max_memory_usage_percent=int(args["maximum_memory_usage_percent"] / workers),
                max_memory_usage=int(args["maximum_memory_usage"] / workers),
                save_chunk_threshold_call_count=args["save_chunk_threshold_call_count"],
                variables_file_path=Path(""),
                output_prefix=args["output_prefix"],
                task_id=task_id,
                is_end_to_end_testing_run=is_end_to_end_test,
            )
            input_manager = InputManager(metadata_depth_limit)

            handler = validation_and_comparison_handlers.get(task_type)
            if handler:
                TaskManager.call_handler(
                    handler,
                    args=args,
                    input_manager=input_manager,
                    output_manager=output_manager,
                    task_id=task_id,
                    produce_graphics=produce_graphics,
                    should_flush_im_pool=should_flush_im_pool,
                )
                return None

            is_data_valid = TaskManager.handle_input_data_audit(args, input_manager, output_manager, True)

            if not is_data_valid:
                output_manager.add_error(
                    "No task run",
                    f"Data not valid for {args['output_prefix']}, task not run",
                    info_map,
                )
                TaskManager.handle_post_processing(args, input_manager, output_manager, task_id, False)
                return None

            filters_path = Path(args["filters_directory"])
            output_manager.validate_filter_constant_content(filters_path)

            TaskManager.set_random_seed(args["random_seed"], output_manager)

            handler = simulation_and_analysis_handlers.get(task_type)
            if handler:
                TaskManager.call_handler(
                    handler,
                    args=args,
                    input_manager=input_manager,
                    output_manager=output_manager,
                    task_id=task_id,
                    produce_graphics=produce_graphics,
                    should_flush_im_pool=should_flush_im_pool,
                )
                return None
            return None

        except Exception as e:
            output_prefix = args["output_prefix"]
            info_map.update(args)
            output_manager.add_error(
                f"Failed to finish task: {task_id} with output prefix: {output_prefix}",
                f"Failed to recover from error: {e}; traceback: {traceback.format_exc()}",
                info_map,
            )
            output_manager.dump_all_nondata_pools(args["logs_directory"], args["exclude_info_maps"], "block")
            output_manager.add_log(
                "Early termination", "Unexpected early termination. Please see logs for details.", info_map
            )
            return f"{output_prefix} ({task_id})"

    @staticmethod
    def handle_herd_initializaition(args: dict[str, Any], output_manager: OutputManager) -> None:
        """Handles initialization of the herd based on specified arguments."""
        info_map = {
            "class": TaskManager.__name__,
            "function": TaskManager.handle_herd_initializaition.__name__,
            "units": MeasurementUnits.UNITLESS,
        }
        output_manager.add_log("Herd initialization start", "Initializing herd data...", info_map)
        herd_factory = HerdFactory(args["init_herd"], args["save_animals"], args["save_animals_directory"])
        herd_factory.initialize_herd()
        output_manager.add_log("Herd initialization complete", "Herd data initialized.", info_map)

    @staticmethod
    def handle_single_simulation_run(args: dict[str, Any], output_manager: OutputManager) -> None:
        """Conducts a single simulation run based on provided arguments."""
        info_map = {
            "class": TaskManager.__name__,
            "function": TaskManager.handle_single_simulation_run.__name__,
            "units": MeasurementUnits.UNITLESS,
        }
        TaskManager.handle_herd_initializaition(args, output_manager)

        output_manager.add_log("Starting the simulation", "Starting the simulation", info_map)
        simulator = SimulationEngine()

        simulator.simulate()
        output_manager.add_log("Simulation completed", "Simulation completed", info_map)

    @staticmethod
    def _handle_end_to_end_testing(
        args: dict[str, Any],
        input_manager: InputManager,
        output_manager: OutputManager,
        task_id: str,
        produce_graphics: bool,
        should_flush_im_pool: bool,
    ) -> None:
        """Runs end-to-end testing routine."""
        info_map = {
            "class": TaskManager.__name__,
            "function": TaskManager._handle_end_to_end_testing.__name__,
            "task_id": task_id,
            "produce_graphics": produce_graphics,
        }

        output_manager.add_log("End-to-end testing", "Starting simulation for end-to-end testing.", info_map)
        TaskManager._handle_simulation_engine_run_tasks(
            args=args,
            input_manager=input_manager,
            output_manager=output_manager,
            task_id=task_id,
            produce_graphics=produce_graphics,
            should_flush_im_pool=should_flush_im_pool,
        )

        output_manager.add_log("End-to-end testing", "Completed simulation for end-to-end testing", info_map)

        output_manager.flush_pools()
        output_manager.is_first_post_processing = False
        E2ETestResultsHandler.compare_actual_and_expected_test_results(
            args["json_output_directory"], args["convert_variable_table_path"], args["output_prefix"]
        )

        TaskManager.handle_post_processing(
            args=args,
            input_manager=input_manager,
            output_manager=output_manager,
            task_id=task_id,
            should_flush_im_pool=True,
            produce_graphics=produce_graphics,
            save_results=True,
        )

    @staticmethod
    def _handle_update_e2e_test_results(
        args: dict[str, Any],
        input_manager: InputManager,
        output_manager: OutputManager,
        task_id: str,
        produce_graphics: bool,
        should_flush_im_pool: bool,
    ) -> None:
        """Generates a new set of end-to-end expected test results."""
        info_map = {
            "class": TaskManager.__name__,
            "function": TaskManager._handle_update_e2e_test_results.__name__,
        }

        output_manager.add_log(
            "End-to-end testing", "Generating new set of end-to-end expected test results.", info_map
        )

        TaskManager._handle_simulation_engine_run_tasks(
            args=args,
            input_manager=input_manager,
            output_manager=output_manager,
            task_id=task_id,
            produce_graphics=produce_graphics,
            should_flush_im_pool=should_flush_im_pool,
        )

        E2ETestResultsHandler.update_expected_test_results(args["json_output_directory"], args["output_prefix"])

        output_manager.add_log(
            "End-to-end testing", "Completed generation of new set of end-to-end expected test results", info_map
        )

    @staticmethod
    def handle_input_data_audit(
        args: dict[str, Any], input_manager: InputManager, output_manager: OutputManager, eager_termination: bool
    ) -> bool:
        """Validates input data saves metadata properties to CSV."""
        info_map = {
            "class": TaskManager.__name__,
            "function": TaskManager.handle_input_data_audit.__name__,
            "units": MeasurementUnits.UNITLESS,
        }
        output_manager.add_log("Validation start", f"Validating data for {args['metadata_file_path']}...", info_map)
        is_data_valid = input_manager.start_data_processing(
            Path(args["metadata_file_path"]), Path(args["input_root"]), eager_termination
        )
        output_manager.add_log(
            "Validation complete", f"{args['output_prefix']} validation status: {is_data_valid}", info_map
        )

        if not args["suppress_log_files"]:
            output_manager.add_log(
                "Saving metadata properties",
                f"Saving metadata properties {args['metadata_file_path']} at {args['logs_directory']}",
                info_map,
            )
            input_manager.save_metadata_properties(args["logs_directory"])

        if args["export_input_data_to_csv"]:
            input_manager.export_pool_to_csv(args["output_prefix"], TaskManager.INPUT_DATA_CSV_WORKING_FOLDER)

        return is_data_valid

    @staticmethod
    def handle_post_processing(
        args: dict[str, Any],
        input_manager: InputManager,
        output_manager: OutputManager,
        task_id: str,
        should_flush_im_pool: bool,
        produce_graphics: bool = False,
        save_results: bool = False,
        load_pool_from_file: bool = False,
        export_input_data_to_csv: bool = False,
    ) -> None:
        """
        Handles post-processing tasks based on specified arguments.

        Parameters
        ----------
        args : dict[str, Any]
            Arguments for post-processing.
        input_manager : InputManager
            Manager to handle input processing.
        output_manager : OutputManager
            Manager to handle output logging and errors.
        task_id: str
            The ID that Task Manager has assigned to this task.
        produce_graphics : bool
            Whether to produce graphics during post-processing.
        save_results : bool
            Whether to save results after processing.
        load_pool_from_file : bool
            Whether to load data pool from file.
        load_saved_output_pools : bool, optional
            Whether to load multiple saved pools as defined by ``saved_output_pools`` before
            continuing with post-processing.
        export_input_data_to_csv: bool
            Whether to export the input data to a CSV file.
        should_flush_im_pool: bool
            Whether to flush the input manager pool.

        Notes
        -----
        - For args, when the optional ``run_eee`` key is set to ``True``, the Emissions, Energy, and Economics
        estimators are executed before the remaining post-processing steps. When ``load_saved_output_pools`` is
        ``True`` the saved pools defined in ``saved_output_pools`` are loaded and namespaced prior to
        post-processing.
        """
        info_map = {
            "class": TaskManager.__name__,
            "function": TaskManager.handle_post_processing.__name__,
            "units": MeasurementUnits.UNITLESS,
        }
        output_manager.add_log("Validation counts", f"{str(input_manager.elements_counter)}", info_map)

        if args.get("run_eee", False):
            pass
            # TODO update path to `RUFAS.EEE.EEE_manager` when EEE is finalized and moved in either PR #2524 or #1299
            # TODO update to be able to run EEE once farmgrown feed emissions are finalized #2580
            # eee_manager_module = import_module("RUFAS.routines.EEE.EEE_manager")
            # eee_manager_module.EEEManager.estimate_all()

        if export_input_data_to_csv:
            output_manager.create_directory(args["input_data_csv_export_path"])
            Utility.combine_saved_input_csv(
                TaskManager.INPUT_DATA_CSV_WORKING_FOLDER,
                args["input_data_csv_export_path"],
                args["input_data_csv_import_path"],
            )

        if args.get("load_saved_output_pools", False):
            saved_pools: list[dict[str, Any]] = args.get("saved_output_pools", [])
            if saved_pools:
                output_manager.flush_pools()
                output_manager.load_multiple_variables_pools_from_files(saved_pools)
                output_manager.set_metadata_prefix("reload")
            else:
                output_manager.add_warning(
                    "No saved pools provided",
                    "load_saved_output_pools was enabled, but no saved_output_pools were supplied.",
                    info_map,
                )
        elif load_pool_from_file:
            output_manager.flush_pools()
            output_manager.load_variables_pool_from_file(args["output_pool_path"])
            output_manager.set_metadata_prefix("reload")

        output_manager.print_errors_warnings_logs_counts(task_id)
        if should_flush_im_pool:
            input_manager.flush_pool()
        if args.get("task_type") == TaskType.POST_PROCESSING:
            save_results = True
            produce_graphics = True
        if save_results:
            output_manager.save_results(
                args["filters_directory"],
                args["exclude_info_maps"],
                produce_graphics,
                args["report_directory"],
                args["graphics_directory"],
                args["csv_output_directory"],
                args["json_output_directory"],
            )

        if not args["suppress_log_files"]:
            input_manager.dump_get_data_logs(args["logs_directory"])
            input_manager.dump_delete_data_logs(args["logs_directory"])
            output_manager.dump_all_nondata_pools(
                args["logs_directory"], args["exclude_info_maps"], args["variable_name_style"]
            )

    @staticmethod
    def set_random_seed(random_seed: int | None, output_manager: OutputManager) -> None:
        """Sets the random seed for the task run."""
        info_map: dict[str, str | MeasurementUnits] = {
            "class": TaskManager.__name__,
            "function": TaskManager.set_random_seed.__name__,
            "units": MeasurementUnits.UNITLESS,
        }
        output_manager.add_log("Random seed received", f"Received {random_seed} as random seed.", info_map)
        if random_seed == 0:
            random_seed = random.randint(NUMPY_RANDOM_SEED_LOWER_BOUND, NUMPY_RANDOM_SEED_UPPER_BOUND)

        random.seed(random_seed)
        numpy.random.seed(random_seed)

        output_manager.add_variable("random_seed", random_seed, info_map)
        output_manager.add_log("Random seed used", f"Seeded libaries with {random_seed=}", info_map)

    @staticmethod
    def _handle_input_data_audit_tasks(
        args: dict[str, Any],
        input_manager: InputManager,
        output_manager: OutputManager,
        task_id: Any,
        produce_grahics: bool,
        should_flush_im_pool: bool,
    ) -> None:
        """Handler for all methods related to metadata property comparison."""
        TaskManager.handle_input_data_audit(
            args=args, input_manager=input_manager, output_manager=output_manager, eager_termination=False
        )
        TaskManager.handle_post_processing(
            args=args,
            input_manager=input_manager,
            output_manager=output_manager,
            task_id=task_id,
            should_flush_im_pool=should_flush_im_pool,
        )

    @staticmethod
    def _handle_compare_metadata_properties_tasks(
        args: dict[str, Any],
        input_manager: InputManager,
        output_manager: OutputManager,
        task_id: Any,
        produce_grahics: bool,
        should_flush_im_pool: bool,
    ) -> None:
        """Handler for all methods related to metadata property comparison."""
        input_manager.compare_metadata_properties(
            args["properties_file_path"], args["comparison_properties_file_path"], args["logs_directory"]
        )

    @staticmethod
    def _handle_herd_init_tasks(
        args: dict[str, Any],
        input_manager: InputManager,
        output_manager: OutputManager,
        task_id: Any,
        produce_grahics: bool,
        should_flush_im_pool: bool,
    ) -> None:
        """Handler for all methods related to herd initialization."""
        args["init_herd"] = True
        TaskManager.handle_herd_initializaition(args=args, output_manager=output_manager)
        TaskManager.handle_post_processing(
            args=args,
            input_manager=input_manager,
            output_manager=output_manager,
            task_id=task_id,
            should_flush_im_pool=should_flush_im_pool,
        )

    @staticmethod
    def _handle_simulation_engine_run_tasks(
        args: dict[str, Any],
        input_manager: InputManager,
        output_manager: OutputManager,
        task_id: Any,
        produce_graphics: bool,
        should_flush_im_pool: bool,
    ) -> None:
        """Handler for all methods related to simulation run."""
        if args["input_patch"]:
            Utility.deep_merge(input_manager.pool, args["input_patch"])

        TaskManager.handle_single_simulation_run(args, output_manager)
        TaskManager.handle_post_processing(
            args=args,
            input_manager=input_manager,
            output_manager=output_manager,
            task_id=task_id,
            should_flush_im_pool=should_flush_im_pool,
            produce_graphics=produce_graphics,
            save_results=True,
        )

    @staticmethod
    def _handle_postprocessing_tasks(
        args: dict[str, Any],
        input_manager: InputManager,
        output_manager: OutputManager,
        task_id: Any,
        produce_graphics: bool,
        should_flush_im_pool: bool,
    ) -> None:
        """Handler for all methods related to postprocessing."""
        TaskManager.handle_post_processing(
            args=args,
            input_manager=input_manager,
            output_manager=output_manager,
            task_id=task_id,
            should_flush_im_pool=should_flush_im_pool,
            produce_graphics=produce_graphics,
        )

    @staticmethod
    def _handle_data_collection_app_update(
        args: dict[str, Any],
        input_manager: InputManager,
        output_manager: OutputManager,
        task_id: Any,
        produce_graphics: bool,
        should_flush_im_pool: bool,
    ) -> None:
        """Handler for all methods related to updating the Data Collection App."""
        dca_updater = DataCollectionAppUpdater()

        task_metadata_properties = args["task_manager_metadata_properties"]
        dca_updater.update_data_collection_app(task_metadata_properties)
