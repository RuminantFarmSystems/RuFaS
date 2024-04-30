from functools import partial
from typing import Any, Dict, List, Tuple
import multiprocessing
from enum import Enum
from pathlib import Path
import numpy
import random

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager, LogVerbosity
from RUFAS.units import MeasurementUnits
from RUFAS.simulation_engine import SimulationEngine
from RUFAS.routines.animal.life_cycle.herd_factory import HerdFactory

"""These constants define the minimum and maximum integers that can be passed to Numpy's random.seed method."""
NUMPY_RANDOM_SEED_LOWER_BOUND = 0
NUMPY_RANDOM_SEED_UPPER_BOUND = 2**32 - 1


class TaskType(Enum):
    """
    Enum different types of task that TaskManager handles.
    """

    HERD_INITIALIZATION = "Herd Initialization"
    SIMULATION_SINGLE_RUN = "A single simulation run"
    SIMULATION_MULTI_RUN = "Multiple simulation with different random seeds"
    SENSITIVITY_ANALYSIS = "Run sensitivity analysis"
    INPUT_DATA_VALIDATION = "Input data validation"
    END_TO_END_TESTING = "Run e2e testing"
    POST_PROCESSING = "Bypass simulation engine and directly run Output Manager"

    @staticmethod
    def from_string(input_str: str) -> "TaskType":
        """
        Converts a string to a corresponding TaskType enum member.

        Parameters
        ----------
        input_str : str
            The string representing a task type.

        Returns
        -------
        TaskType
            The corresponding TaskType enum member.

        Raises
        ------
        ValueError
            If the input string does not correspond to any TaskType enum member.
        """
        normalized_input = "_".join(input_str.strip().upper().split())
        try:
            return TaskType[normalized_input]
        except KeyError:
            raise ValueError(f"The string '{input_str}' is not a match with any acceptable TaskType.")

    def is_multi_run(self) -> bool:
        """returns True if the task type requires multiple simulation runs; otherwise false"""
        return self in [TaskType.SIMULATION_MULTI_RUN, TaskType.SENSITIVITY_ANALYSIS, TaskType.END_TO_END_TESTING]


class TaskManager:
    def __init__(self):
        self.input_manager = InputManager()
        self.output_manager = OutputManager()

    def start(
        self,
        metadata_path: str,
        verbosity: LogVerbosity,
        exclude_info_maps: bool,
        output_directory: Path,
        clear_output_directory: bool,
        produce_graphics: bool,
    ) -> None:
        self.output_manager.run_startup_sequence(
            verbosity, exclude_info_maps, output_directory, clear_output_directory, Path(""), "Task Manager"
        )  # TODO get the correct value for self.output_manager.run_startup_sequence variables_file_path arg
        is_data_valid = self.input_manager.start_data_processing(metadata_path)
        if not is_data_valid:
            TaskManager.handle_post_processing(
                {
                    "output_directory": output_directory,
                    "exclude_info_maps": exclude_info_maps,
                    "variable_name_style": "verbose",
                },
                self.input_manager,
                self.output_manager,
            )
            raise Exception("Task Manager's input data is invalid.")
        workers: int = self.input_manager.get_data("tasks.parallel_workers")
        self.pool = multiprocessing.Pool(
            workers, maxtasksperchild=1
        )  # maxtasksperchild=1 to maintain isolation between tasks and ensure no memory leaks happens in IO Managers
        parsed_single_run_args, parsed_multi_run_args = self._parse_input_tasks()
        expanded_args = self._expand_multi_runs_to_single_runs(parsed_multi_run_args)
        runnable_args = parsed_single_run_args + expanded_args
        self._run_tasks(runnable_args, produce_graphics)

    def _parse_input_tasks(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        parsed_single_run_args: List[Dict[str, Any]] = []
        parsed_multi_run_args: List[Dict[str, Any]] = []
        tasks_from_input: List[Dict[str, Any]] = self.input_manager.get_data("tasks.tasks")
        for input_task in tasks_from_input:
            input_task["task_type"] = TaskType.from_string(input_task["task_type"])
            if input_task["task_type"].is_multi_run():
                parsed_multi_run_args.append(input_task)
            else:
                parsed_single_run_args.append(input_task)
        return parsed_single_run_args, parsed_multi_run_args

    def _expand_multi_runs_to_single_runs(self, multi_run_args: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        expanded_args: List[Dict[str, Any]] = []
        task_type_to_expander_map = {
            TaskType.SIMULATION_MULTI_RUN: self._expand_simulation_multi_run_args,
            TaskType.SENSITIVITY_ANALYSIS: self._expand_sensitivity_analysis_args,
            TaskType.END_TO_END_TESTING: self._expand_end_to_end_testing_args,
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
            new_args["output_prefix"] = f"{new_args['output_prefix']}_run_{i+1}"
            single_run_args.append(new_args)

        return single_run_args

    def _expand_sensitivity_analysis_args(self, multi_run_args: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

    def _expand_end_to_end_testing_args(self, multi_run_args: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

    def _run_tasks(self, single_run_args: List[Dict[str, Any]], produce_graphics: bool) -> None:
        task_with_args = partial(self.task, produce_graphics=produce_graphics)
        results = self.pool.imap_unordered(task_with_args, single_run_args)
        for _ in results:
            pass

    @staticmethod
    def task(args: Dict[str, Any], produce_graphics: bool) -> None:
        info_map = {
            "class": TaskManager.__name__,
            "function": TaskManager.task.__name__,
            "units": MeasurementUnits.UNITLESS,
        }
        output_manager = OutputManager()
        output_manager.run_startup_sequence(
            LogVerbosity(args["log_verbosity"]),
            args["exclude_info_maps"],
            Path(args["output_directory"]),
            False,
            Path(""),
            args["output_prefix"],
        )
        input_manager = InputManager()
        if args["task_type"] == TaskType.INPUT_DATA_VALIDATION:
            TaskManager.handle_input_data_validation(args, input_manager, output_manager, False)
            TaskManager.handle_post_processing(args, input_manager, output_manager)
            return

        is_data_valid = TaskManager.handle_input_data_validation(args, input_manager, output_manager, True)
        if not is_data_valid:
            output_manager.add_error(
                "No task run",
                f"Data not valid for {args['output_prefix']}, task not run",
                info_map,
            )
            TaskManager.handle_post_processing(args, input_manager, output_manager)
            return

        TaskManager.set_random_seed(args["random_seed"], output_manager)

        if args["task_type"] == TaskType.HERD_INITIALIZATION:
            args["init_herd"] = True
            TaskManager.handle_herd_initializaition(args, input_manager, output_manager)
            TaskManager.handle_post_processing(args, input_manager, output_manager)

        if args["task_type"] == TaskType.SIMULATION_SINGLE_RUN:
            TaskManager.handle_single_simulation_run(args, input_manager, output_manager)
            TaskManager.handle_post_processing(args, input_manager, output_manager, produce_graphics, True)

        if args["task_type"] == TaskType.POST_PROCESSING:
            TaskManager.handle_post_processing(args, input_manager, output_manager, produce_graphics, True, True)

    @staticmethod
    def handle_herd_initializaition(
        args: Dict[str, Any], input_manager: InputManager, output_manager: OutputManager
    ) -> None:
        info_map = {
            "class": TaskManager.__name__,
            "function": TaskManager.handle_herd_initializaition.__name__,
            "units": MeasurementUnits.UNITLESS,
        }
        output_manager.add_log("Herd initialization start", "Initializing herd data...", info_map)
        herd_factory = HerdFactory(args["init_herd"], args["save_animals"], Path(args["save_animals_directory"]))
        herd_factory.initialize_herd()
        output_manager.add_log("Herd initialization complete", "Herd data initialized.", info_map)

    @staticmethod
    def handle_single_simulation_run(
        args: Dict[str, Any], input_manager: InputManager, output_manager: OutputManager
    ) -> None:
        info_map = {
            "class": TaskManager.__name__,
            "function": TaskManager.handle_single_simulation_run.__name__,
            "units": MeasurementUnits.UNITLESS,
        }
        TaskManager.handle_herd_initializaition(args, input_manager, output_manager)

        output_manager.add_log("Starting the simulation", "Starting the simulation", info_map)
        simulator = SimulationEngine()
        simulator.simulate()
        output_manager.add_log("Simulation completed", "Simulation completed", info_map)

    @staticmethod
    def handle_input_data_validation(
        args: Dict[str, Any], input_manager: InputManager, output_manager: OutputManager, eager_termination: bool
    ) -> bool:
        info_map = {
            "class": TaskManager.__name__,
            "function": TaskManager.handle_input_data_validation.__name__,
            "units": MeasurementUnits.UNITLESS,
        }
        output_manager.add_log("Validation start", f"Validating data for {args['metadata_file_path']}...\n", info_map)
        is_data_valid = input_manager.start_data_processing(args["metadata_file_path"], eager_termination)
        output_manager.add_log(
            "Validation complete", f"{args['output_prefix']} validation status: {is_data_valid}", info_map
        )
        return is_data_valid

    @staticmethod
    def handle_post_processing(
        args: Dict[str, Any],
        input_manager: InputManager,
        output_manager: OutputManager,
        produce_graphics: bool = False,
        save_results: bool = False,
        load_pool_from_file: bool = False,
    ) -> None:
        info_map = {
            "class": TaskManager.__name__,
            "function": TaskManager.handle_post_processing.__name__,
            "units": MeasurementUnits.UNITLESS,
        }
        output_manager.add_log("Validation counts", f"{str(input_manager.elements_counter)}", info_map)
        input_manager.dump_get_data_logs(Path(args["output_directory"]))

        if load_pool_from_file:
            output_manager.flush_pools()
            output_manager.load_variables_pool_from_file(Path(args["output_pool_path"]))
            output_manager.set_metadata_prefix("reload")

        output_manager.print_errors_warnings_logs_counts()

        if save_results:
            output_manager.save_results(
                Path(args["output_directory"]),
                Path(args["filters_directory"]),
                args["exclude_info_maps"],
                produce_graphics,
                Path(args["graphics_directory"]),
                Path(args["CSV_directory"]),
            )
        output_manager.dump_all_nondata_pools(
            Path(args["output_directory"]), args["exclude_info_maps"], args["variable_name_style"]
        )

    @staticmethod
    def set_random_seed(random_seed: int | None, output_manager: OutputManager) -> None:
        info_map: dict[str, str | MeasurementUnits] = {
            "class": TaskManager.__name__,
            "function": TaskManager.set_random_seed.__name__,
            "units": MeasurementUnits.UNITLESS,
        }
        output_manager.add_log("Random seed recieved", f"Received {random_seed} as random seed.", info_map)
        if random_seed is None:
            random_seed = random.randint(NUMPY_RANDOM_SEED_LOWER_BOUND, NUMPY_RANDOM_SEED_UPPER_BOUND)

        random.seed(random_seed)
        numpy.random.seed(random_seed)

        output_manager.add_variable("random_seed", random_seed, info_map)
        output_manager.add_log("Random seed used", f"Seeded libaries with {random_seed=}", info_map)
