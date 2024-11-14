from enum import Enum
from functools import partial
import multiprocessing
import numpy
from pathlib import Path
from threading import Thread, Event
import random
from time import sleep
from psutil import Process
import os
import docker
from re import match
from SALib.sample import ff as fractional_factorial_sampler
from SALib.sample import saltelli as saltelli_sampler
import traceback
from typing import Any, Dict, List, Tuple, Callable

from RUFAS.e2e_test_results_comparer import E2ETestResultsComparer
from RUFAS.general_constants import GeneralConstants
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager, LogVerbosity
from RUFAS.routines.animal.life_cycle.herd_factory import HerdFactory
from RUFAS.simulation_engine import SimulationEngine
from RUFAS.units import MeasurementUnits
from RUFAS.util import Utility

RUFAS_VERSION = "0.9.2"

"""These constants define the minimum and maximum integers that can be passed to Numpy's random.seed method."""
NUMPY_RANDOM_SEED_LOWER_BOUND = 0
NUMPY_RANDOM_SEED_UPPER_BOUND = 2**32 - 1


# TODO: should these values (CPU usage, system check interval, etc.) be made user inputs?
"""Time in seconds between checking the resources used by RuFaS in a Docker container."""
SYSTEM_CHECK_INTERVAL = 10

"""Percentage threshold below which CPU usage indicates an issue in RuFaS."""
LOW_CPU_USAGE_THRESHOLD = 10.0

"""Percentage threshold below which memory usage indicates an issue in RuFaS."""
LOW_MEMORY_USAGE_THRESHOLD = 8.0  # TODO: instead of lower memory usage threshold, would checking for static memory
                                  #       usage be better?
"""
If the number of times that CPU and memory usage are below their respective thresholds reaches this number then Task
Manager stops all simulations and raises an error.
"""
STALL_CONFIRMATION_THRESHOLD = 3

"""Name of the environment variable that Task Manager expects to be present if running in a Docker container."""
CONTAINER_NAME = "CONTAINER_NAME"


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
    """
    Manager class for handling tasks related to simulations and analyses.

    Attributes
    ----------
    output_manager : OutputManager
        Task Manager's OutputManager instance.
    _consecutive_low_cpu_usage_count : int, default 0
        Number of consecutive system resource checks that CPU usage has been below threshold for.
    _consecutive_low_memory_usage_count : int, default 0
        Number of consecutive system resource checks that memory usage has below threshold low for.
    _docker_container_name : str | None, default None
        Identifier for the Docker container that in which RuFaS is running. None if RuFaS is not
        running inside a Docker container.

    """

    def __init__(self) -> None:
        self.output_manager = OutputManager()
        self._consecutive_low_cpu_usage_count = 0
        self._consecutive_low_memory_usage_count = 0
        self._docker_container_name: str | None = None
        self._get_container_info()

    def _get_container_info(self) -> None:
        """
        Looks for an environment variable specifying the Docker container name that RuFaS is running in.
        If this variable is found, the corresponding container is looked for in the Docker client. Otherwise,
        it is assumed that RuFaS is not running in a Docker container.
        """
        container_name = os.getenv(CONTAINER_NAME)
        info_map = {"class": self.__class__.__name__, "function": self._get_container_info.__name__}
        if container_name is None:
            self.output_manager.add_warning(
                "Docker container name not found",
                "Stalled simulations will not be stopped",
                info_map
            )
            return
        client = docker.from_env()
        for container in client.containers.list():
            env_variables = container.attrs["Config"]["Env"]
            for var in env_variables:
                if match(f"^{CONTAINER_NAME}=.*", var):  # TODO: handle case where multiple containers have the same name
                    self._docker_container_name = container.attrs.get("Name")
                    self.output_manager.add_log(
                        f"Found Docker container with name matching environment variable '{CONTAINER_NAME}'",
                        f"Using container with Name='{self._docker_container_name}' and {CONTAINER_NAME}='{container_name}'",
                        {"name": self._docker_container_name, "container_name": container_name, **info_map}
                    )
                    return
        err_name = f"No Docker container with name matching {CONTAINER_NAME}='{container_name}' found"
        err_msg = "Halting simulation"
        self.output_manager.add_error(err_name, err_msg, {"container_name": container_name, **info_map})
        raise RuntimeError(f"{err_name}. {err_msg}")  # TODO: instead of crashing, raise error to OM and continue?

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
            verbosity,
            exclude_info_maps,
            output_directory,
            clear_output_directory,
            Path(""),
            "Task Manager",
            RUFAS_VERSION,
            "TASK MANAGER",
            False,
        )
        info_map = {
            "class": TaskManager.__name__,
            "function": TaskManager.start.__name__,
            "units": MeasurementUnits.UNITLESS,
        }
        self.output_manager.add_log("Task Manager Start", "Task Manager Started.", info_map)
        is_data_valid = self.input_manager.start_data_processing(metadata_path)
        if not is_data_valid:
            TaskManager.handle_post_processing(
                {
                    "exclude_info_maps": exclude_info_maps,
                    "variable_name_style": "verbose",
                    "logs_directory": logs_directory,
                    "suppress_log_files": suppress_log_files,
                },
                self.input_manager,
                self.output_manager,
                "TASK_MANAGER",
            )
            raise Exception("Task Manager's input data is invalid.")
        workers: int = self.input_manager.get_data("tasks.parallel_workers")
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
        self._run_tasks(runnable_args, produce_graphics, metadata_depth_limit)
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
        )

    def _parse_input_tasks(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Parses input tasks into single and multiple run tasks.

        Returns
        -------
        Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]
            Parsed single run and multi-run task arguments.
        """
        parsed_single_run_args: List[Dict[str, Any]] = []
        parsed_multi_run_args: List[Dict[str, Any]] = []
        tasks_from_input: List[Dict[str, Any]] = self.input_manager.get_data("tasks.tasks")
        for input_task in tasks_from_input:
            input_task["task_type"] = TaskType.from_string(input_task["task_type"])
            input_task["input_patch"] = None
            input_task["metadata_file_path"] = Path(input_task["metadata_file_path"])
            input_task["properties_file_path"] = Path(input_task["properties_file_path"])
            input_task["comparison_properties_file_path"] = Path(input_task["comparison_properties_file_path"])
            input_task["logs_directory"] = Path(input_task["logs_directory"])
            input_task["suppress_log_files"] = input_task["suppress_log_files"]
            input_task["save_animals_directory"] = Path(input_task["save_animals_directory"])
            input_task["filters_directory"] = Path(input_task["filters_directory"])
            input_task["csv_output_directory"] = Path(input_task["csv_output_directory"])
            input_task["json_output_directory"] = Path(input_task["json_output_directory"])
            input_task["report_directory"] = Path(input_task["report_directory"])
            input_task["graphics_directory"] = Path(input_task["graphics_directory"])
            input_task["output_pool_path"] = Path(input_task["output_pool_path"])
            if input_task["task_type"].is_multi_run():
                parsed_multi_run_args.append(input_task)
            else:
                parsed_single_run_args.append(input_task)
        return parsed_single_run_args, parsed_multi_run_args

    def _expand_multi_runs_to_single_runs(self, multi_run_args: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Expands multi-run tasks into single-run tasks for execution.

        Parameters
        ----------
        multi_run_args : List[Dict[str, Any]]
            List of multi-run task arguments.

        Returns
        -------
        List[Dict[str, Any]]
            Expanded list of single-run tasks.
        """
        expanded_args: List[Dict[str, Any]] = []
        task_type_to_expander_map = {
            TaskType.SIMULATION_MULTI_RUN: self._expand_simulation_multi_run_args,
            TaskType.SENSITIVITY_ANALYSIS: self._expand_sensitivity_analysis_args,
        }
        for multi_run_arg in multi_run_args:
            task_type = multi_run_arg["task_type"]
            expanded_args += task_type_to_expander_map[task_type](multi_run_arg)

        return expanded_args

    def _expand_simulation_multi_run_args(self, multi_run_args: Dict[str, Any]) -> List[Dict[str, Any]]:
        single_run_args = []
        for i in range(multi_run_args["multi_run_counts"]):
            new_args = multi_run_args.copy()
            new_args["task_type"] = TaskType.SIMULATION_SINGLE_RUN
            new_args["random_seed"] = random.randint(NUMPY_RANDOM_SEED_LOWER_BOUND, NUMPY_RANDOM_SEED_UPPER_BOUND)
            new_args["output_prefix"] = f"{new_args['output_prefix']} run {i + 1}"
            single_run_args.append(new_args)

        return single_run_args

    def _expand_sensitivity_analysis_args(self, multi_run_args: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Expands sensitivity analysis multi-run tasks into single-run tasks."""

        SA_input_variables: List[Dict[str, float | str]] = multi_run_args["SA_input_variables"]

        names: List[str] = [str(input_variable["variable_name"]) for input_variable in SA_input_variables]
        variables_count = len(names)
        bounds: List[List[float]] = [
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
            sampled_values = fractional_factorial_sampler.sample(parsed_SA_input_variables)
        elif multi_run_args["sampler"] == "saltelli_sobol":
            sampled_values = saltelli_sampler.sample(
                parsed_SA_input_variables,
                multi_run_args["saltelli_number"],
                skip_values=multi_run_args["saltelli_skip"],
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
        self, single_run_args: List[Dict[str, Any]], produce_graphics: bool, metadata_depth_limit: int
    ) -> None:
        """Runs the tasks based on the provided arguments."""
        if self._docker_container_name is not None:
            stop_event = Event()
            monitor_thread = Thread(target=self._monitor_resources_for_stall, args=(stop_event,))
            monitor_thread.start()

        task_with_args = partial(
            self.task, produce_graphics=produce_graphics, metadata_depth_limit=metadata_depth_limit
        )
        results = self.pool.imap_unordered(task_with_args, single_run_args)
        failed = []
        info_map = {"class": TaskManager.__name__, "function": TaskManager._run_tasks.__name__}

        while True:
            if self._docker_container_name is not None and stop_event.is_set():
                name = "All tasks stalled"
                msg = "Task Manager halting all simulations and raising error."
                self.output_manager.add_error(name, msg, info_map)
                raise RuntimeError(f"{name}. {msg}")

            try:
                result = results.next(timeout=SYSTEM_CHECK_INTERVAL)
            except multiprocessing.TimeoutError:
                continue

            if result is None:
                break
            else:
                failed.append(result)

        if self._docker_container_name is not None:
            stop_event.set()
            monitor_thread.join()

        if len(failed) > 0:
            self.output_manager.add_error("Task(s) failed", f"Failed task(s) and output prefix are: {failed}", info_map)

    def _monitor_resources_for_stall(self, stop_event: Event) -> None:
        """
        Monitors system resources for signs of stalled processes.

        Parameters
        ----------
        stop_event : Event
            Event that indicates resource monitoring should stop for RuFaS, either because all simulations have finished
            or simulations have stalled.

        """
        parent = Process()

        docker_client = docker.from_env()
        container = docker_client.containers.get(self._docker_container_name)

        info_map = {"class": self.__class__.__name__, "function": self._monitor_resources_for_stall.__name__}
        while not stop_event.is_set():
            children = parent.children(recursive=True)
            info_map = {"class": self.__class__.__name__, "function": self._monitor_resources_for_stall.__name__}
            if not children:
                self.output_manager.add_warning("No worker processes found", "Task Manager continuing operations as normal", info_map)
                continue
            worker_count = len(children)

            container_stats = container.stats(stream=False)

            cpu_usage = container_stats['cpu_stats']['cpu_usage']['total_usage']
            system_cpu_usage = container_stats['cpu_stats']['system_cpu_usage']
            online_cpus = container_stats['cpu_stats'].get('online_cpus', 1)  # Fallback if not provided

            # Calculate CPU percentage (Docker provides raw CPU values, so calculation is needed)
            cpu_delta = cpu_usage - container_stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = system_cpu_usage - container_stats['precpu_stats']['system_cpu_usage']
            cpu_usage = (cpu_delta / system_delta) * online_cpus * GeneralConstants.FRACTION_TO_PERCENTAGE if system_delta > 0 else 0.0

            mem_usage = container_stats['memory_stats']['usage']
            mem_limit = container_stats['memory_stats']['limit']

            memory_usage = (mem_usage / mem_limit) * GeneralConstants.FRACTION_TO_PERCENTAGE if mem_limit > 0 else 0.0

            info_map = {"cpu_usage": cpu_usage, "memory_usage": memory_usage, "worker_count": worker_count, **info_map}

            name = "System resource usage"
            msg = f"{worker_count} worker process(es), CPU usage: {cpu_usage:.2f}%, memory usage: {memory_usage:.2f}%"
            info_map = {"cpu_usage": cpu_usage, "memory_usage": memory_usage, "worker_count": worker_count, **info_map}

            self.output_manager.add_log(name, msg, info_map)

            if cpu_usage < LOW_CPU_USAGE_THRESHOLD:
                self._consecutive_low_cpu_usage_count += 1
            else:
                self._consecutive_low_cpu_usage_count = 0

            if memory_usage < LOW_MEMORY_USAGE_THRESHOLD:
                self._consecutive_low_memory_usage_count += 1
            else:
                self._consecutive_low_memory_usage_count = 0

            is_cpu_usage_stalled = self._consecutive_low_cpu_usage_count >= STALL_CONFIRMATION_THRESHOLD
            is_memory_usage_stalled = self._consecutive_low_memory_usage_count >= STALL_CONFIRMATION_THRESHOLD
            is_stalled = is_cpu_usage_stalled and is_memory_usage_stalled
            if is_stalled:
                self.output_manager.add_error(name, msg, info_map)
                stop_event.set()
            sleep(SYSTEM_CHECK_INTERVAL)

        return

    @staticmethod
    def call_handler(
        handler: Callable[..., None],
        args: Dict[str, Any],
        input_manager: InputManager,
        output_manager: OutputManager,
        task_id: Any,
        produce_graphics: bool,
    ) -> None:
        """Wrapper function to call the function map with each of its arguments."""
        handler(args, input_manager, output_manager, task_id, produce_graphics)

    @staticmethod
    def task(args: Dict[str, Any], produce_graphics: bool, metadata_depth_limit: int | None) -> str | None:
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
        }
        try:
            task_type = args.get("task_type")
            is_end_to_end_test = True if task_type is TaskType.END_TO_END_TESTING else False
            output_manager.run_startup_sequence(
                LogVerbosity(args["log_verbosity"]),
                args["exclude_info_maps"],
                Path(""),
                False,
                Path(""),
                args["output_prefix"],
                RUFAS_VERSION,
                task_id,
                is_end_to_end_test,
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
                )
                return

            is_data_valid = TaskManager.handle_input_data_audit(args, input_manager, output_manager, True)

            if not is_data_valid:
                output_manager.add_error(
                    "No task run",
                    f"Data not valid for {args['output_prefix']}, task not run",
                    info_map,
                )
                TaskManager.handle_post_processing(args, input_manager, output_manager, task_id)
                return

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
                )
                return

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
    def handle_herd_initializaition(args: Dict[str, Any], output_manager: OutputManager) -> None:
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
    def handle_single_simulation_run(args: Dict[str, Any], output_manager: OutputManager) -> None:
        """Conducts a single simulation run based on provided arguments."""
        info_map = {
            "class": TaskManager.__name__,
            "function": TaskManager.handle_single_simulation_run.__name__,
            "units": MeasurementUnits.UNITLESS,
        }
        TaskManager.handle_herd_initializaition(args, output_manager)

        # TODO: Remove this if-else block and argument to SimulationEngine init when Animal and Feed Storage modules are
        # completed - #1878.
        if args["task_type"] == TaskType.END_TO_END_TESTING:
            is_end_to_end_test_run = True
        else:
            is_end_to_end_test_run = False

        output_manager.add_log("Starting the simulation", "Starting the simulation", info_map)
        simulator = SimulationEngine(is_end_to_end_test_run=is_end_to_end_test_run)

        simulator.simulate()
        output_manager.add_log("Simulation completed", "Simulation completed", info_map)

    @staticmethod
    def _handle_end_to_end_testing(
        args: Dict[str, Any],
        input_manager: InputManager,
        output_manager: OutputManager,
        task_id: str,
        produce_graphics: bool,
    ) -> None:
        """Runs end-to-end testing routine."""
        info_map = {
            "class": TaskManager.__name__,
            "function": TaskManager._handle_end_to_end_testing.__name__,
            "task_id": task_id,
            "produce_graphics": produce_graphics,
        }

        output_manager.add_log("End-to-end testing", "Starting simulation for end-to-end testing.", info_map)

        TaskManager._handle_simulation_engine_run_tasks(args, input_manager, output_manager, task_id, produce_graphics)

        output_manager.add_log("End-to-end testing", "Completed simulation for end-to-end testing", info_map)

        output_manager.flush_pools()
        output_manager.is_first_post_processing = False

        E2ETestResultsComparer.compare_actual_and_expected_test_results(args["json_output_directory"])

        TaskManager.handle_post_processing(
            args, input_manager, output_manager, task_id, produce_graphics, save_results=True
        )

    @staticmethod
    def handle_input_data_audit(
        args: Dict[str, Any], input_manager: InputManager, output_manager: OutputManager, eager_termination: bool
    ) -> bool:
        """Validates input data saves metadata properties to CSV."""
        info_map = {
            "class": TaskManager.__name__,
            "function": TaskManager.handle_input_data_audit.__name__,
            "units": MeasurementUnits.UNITLESS,
        }
        output_manager.add_log("Validation start", f"Validating data for {args['metadata_file_path']}...", info_map)
        is_data_valid = input_manager.start_data_processing(Path(args["metadata_file_path"]), eager_termination)
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

        return is_data_valid

    @staticmethod
    def handle_post_processing(
        args: Dict[str, Any],
        input_manager: InputManager,
        output_manager: OutputManager,
        task_id: str,
        produce_graphics: bool = False,
        save_results: bool = False,
        load_pool_from_file: bool = False,
    ) -> None:
        """
        Handles post-processing tasks based on specified arguments.

        Parameters
        ----------
        args : Dict[str, Any]
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

        """
        info_map = {
            "class": TaskManager.__name__,
            "function": TaskManager.handle_post_processing.__name__,
            "units": MeasurementUnits.UNITLESS,
        }
        output_manager.add_log("Validation counts", f"{str(input_manager.elements_counter)}", info_map)

        if load_pool_from_file:
            output_manager.flush_pools()
            output_manager.load_variables_pool_from_file(args["output_pool_path"])
            output_manager.set_metadata_prefix("reload")

        output_manager.print_errors_warnings_logs_counts(task_id)
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
        args: Dict[str, Any],
        input_manager: InputManager,
        output_manager: OutputManager,
        task_id: Any,
        produce_grahics: bool,
    ) -> None:
        """Handler for all methods related to metadata property comparison."""
        TaskManager.handle_input_data_audit(args, input_manager, output_manager, False)
        TaskManager.handle_post_processing(args, input_manager, output_manager, task_id)

    @staticmethod
    def _handle_compare_metadata_properties_tasks(
        args: Dict[str, Any],
        input_manager: InputManager,
        output_manager: OutputManager,
        task_id: Any,
        produce_grahics: bool,
    ) -> None:
        """Handler for all methods related to metadata property comparison."""
        input_manager.compare_metadata_properties(
            args["properties_file_path"], args["comparison_properties_file_path"], args["logs_directory"]
        )

    @staticmethod
    def _handle_herd_init_tasks(
        args: Dict[str, Any],
        input_manager: InputManager,
        output_manager: OutputManager,
        task_id: Any,
        produce_grahics: bool,
    ) -> None:
        """Handler for all methods related to herd initialization."""
        args["init_herd"] = True
        TaskManager.handle_herd_initializaition(args, output_manager)
        TaskManager.handle_post_processing(args, input_manager, output_manager, task_id)

    @staticmethod
    def _handle_simulation_engine_run_tasks(
        args: Dict[str, Any],
        input_manager: InputManager,
        output_manager: OutputManager,
        task_id: Any,
        produce_graphics: bool,
    ) -> None:
        """Handler for all methods related to simulation run."""
        if args["input_patch"]:
            Utility.deep_merge(input_manager.pool, args["input_patch"])

        TaskManager.handle_single_simulation_run(args, output_manager)
        TaskManager.handle_post_processing(args, input_manager, output_manager, task_id, produce_graphics, True)

    @staticmethod
    def _handle_postprocessing_tasks(
        args: Dict[str, Any],
        input_manager: InputManager,
        output_manager: OutputManager,
        task_id: Any,
        produce_graphics: bool,
    ) -> None:
        """Handler for all methods related to postprocessing."""
        TaskManager.handle_post_processing(args, input_manager, output_manager, task_id, produce_graphics, True, True)
