from functools import partial
from typing import Any, Dict, List
import multiprocessing
from enum import Enum
from pathlib import Path

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager, LogVerbosity
from RUFAS.simulation_engine import SimulationEngine


class TaskType(Enum):
    """
    Enum different types of task that TaskManager handles.
    """

    HERD_INITIALIZATION = "Herd Initialization"
    SIMULATION_SIGNLE_RUN = "A single simulation run"
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
        return self in [TaskType.SIMULATION_MULTI_RUN, TaskType.SENSITIVITY_ANALYSIS]


class TaskManager:
    def __init__(self):
        self.input_manager = InputManager()
        self.output_manager = OutputManager()  # TODO use to log
        self.parsed_single_run_args: List[Dict[str, Any]] = []
        self.parsed_multi_run_args: List[Dict[str, Any]] = []

    def start(
        self,
        metadata_path: str,
        verbosity: LogVerbosity,
        exclude_info_maps: bool,
        output_directory: Path,
        clear_output_directory: bool,
        produce_graphics: bool,
    ) -> None:
        self.input_manager.start_data_processing(metadata_path)
        self.output_manager.run_startup_sequence(
            verbosity, exclude_info_maps, output_directory, clear_output_directory, Path("")
        )  # TODO get the correct value for self.output_manager.run_startup_sequence variables_file_path arg
        workers: int = self.input_manager.get_data("tasks.parallel_workers")
        self.pool = multiprocessing.Pool(
            workers, maxtasksperchild=1
        )  # maxtasksperchild=1 to maintain isolation between tasks and ensure no memory leaks happens in IO Managers
        self._parse_input_tasks()
        self._handle_single_run_tasks(produce_graphics)
        self._handle_multi_run_tasks(produce_graphics)

    def _parse_input_tasks(self) -> None:
        tasks_from_input: List[Dict[str, Any]] = self.input_manager.get_data("tasks.tasks")
        for input_task in tasks_from_input:
            input_task["task_type"] = TaskType.from_string(input_task["task_type"])
            if input_task["task_type"].is_multi_run():
                self.parsed_multi_run_args.append(input_task)
            else:
                self.parsed_single_run_args.append(input_task)

    def _handle_single_run_tasks(self, produce_graphics: bool) -> None:
        task_with_args = partial(self.task_single, produce_graphics=produce_graphics)
        results = self.pool.imap_unordered(task_with_args, self.parsed_single_run_args)
        for _ in results:
            pass

    def _handle_multi_run_tasks(self, produce_graphics: bool) -> None:
        # TODO use self.input_manager to read input and patch it for each task
        task_with_args = partial(self.task_multi, produce_graphics=produce_graphics)
        results = self.pool.imap_unordered(task_with_args, self.parsed_multi_run_args)
        for _ in results:
            pass

    @staticmethod
    def task_single(args: Dict[str, Any], produce_graphics: bool) -> None:
        output_manager = OutputManager()
        output_manager.run_startup_sequence(
            LogVerbosity(args["log_verbosity"]),
            args["exclude_info_maps"],
            Path(args["output_directory"]),
            False,
            Path(""),
        )
        input_manager = InputManager()

        task_type_to_handler_map = {
            TaskType.HERD_INITIALIZATION: TaskManager.handle_herd_initializaition,
            TaskType.SIMULATION_SIGNLE_RUN: TaskManager.handle_single_simulation_run,
            TaskType.INPUT_DATA_VALIDATION: TaskManager.handle_input_data_validation,
            TaskType.END_TO_END_TESTING: TaskManager.handle_end_to_end_testing,
            TaskType.POST_PROCESSING: TaskManager.handle_post_processing,
        }

        task_type_to_handler_map[args["task_type"]](input_manager, output_manager)

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
    def task_multi(args: Dict[str, Any], produce_graphics: bool) -> None:  # TODO imeplement
        output_manager = OutputManager()
        output_manager.run_startup_sequence(
            LogVerbosity(args["log_verbosity"]),
            args["exclude_info_maps"],
            Path(args["output_directory"]),
            False,
            Path(""),
        )
        input_manager = InputManager()
        if args["task_type"] == TaskType.SIMULATION_MULTI_RUN:
            pass
        elif args["task_type"] == TaskType.SENSITIVITY_ANALYSIS:
            pass
        else:
            print("error")

    @staticmethod
    def handle_herd_initializaition(input_manager: InputManager, output_manager: OutputManager) -> None:
        pass

    @staticmethod
    def handle_single_simulation_run(input_manager: InputManager, output_manager: OutputManager) -> None:
        pass

    @staticmethod
    def handle_input_data_validation(input_manager: InputManager, output_manager: OutputManager) -> None:
        pass

    @staticmethod
    def handle_end_to_end_testing(input_manager: InputManager, output_manager: OutputManager) -> None:
        pass

    @staticmethod
    def handle_post_processing(input_manager: InputManager, output_manager: OutputManager) -> None:
        pass

    @staticmethod  # TODO potential rename
    def handle_sensitivity_analysis(input_manager: InputManager, output_manager: OutputManager) -> None:
        pass

    @staticmethod  # TODO potential rename
    def handle_multi_simulation_run(input_manager: InputManager, output_manager: OutputManager) -> None:
        pass
