from functools import partial
from typing import Any, Dict, List
import multiprocessing
from enum import Enum

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
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

    def start(self, metadata_path: str) -> None:
        self.input_manager.start_data_processing(metadata_path)
        workers: int = self.input_manager.get_data("tasks.parallel_workers")
        self.pool = multiprocessing.Pool(
            workers, maxtasksperchild=1
        )  # maxtasksperchild=1 to maintain isolation between tasks and ensure no memory leaks happens in IO Managers
        self._parse_input_tasks()
        self._handle_single_run_tasks()
        self._handle_multi_run_tasks()

    def _parse_input_tasks(self) -> None:
        tasks_from_input: List[Dict[str, Any]] = self.input_manager.get_data("tasks.tasks")
        for input_task in tasks_from_input:
            input_task["task_type"] = TaskType.from_string(input_task["task_type"])
            if input_task["task_type"].is_multi_run():
                self.parsed_multi_run_args.append(input_task)
            else:
                self.parsed_single_run_args.append(input_task)

    def _handle_single_run_tasks(self) -> None:
        results = self.pool.imap_unordered(self.task_single, self.parsed_single_run_args)
        for _ in results:
            pass

    def _handle_multi_run_tasks(self) -> None:
        # TODO use self.input_manager to read input and patch it for each task
        task_with_args = partial(self.task_multi, const_var=1)
        results = self.pool.imap_unordered(task_with_args, self.parsed_multi_run_args)
        for _ in results:
            pass

    @staticmethod
    def task_single(args: Dict[str, Any]) -> None:  # TODO imeplement
        input_manager = InputManager()
        if args["task_type"] == TaskType.HERD_INITIALIZATION:
            pass
        elif args["task_type"] == TaskType.SIMULATION_SIGNLE_RUN:
            pass
        elif args["task_type"] == TaskType.INPUT_DATA_VALIDATION:
            pass
        elif args["task_type"] == TaskType.END_TO_END_TESTING:
            pass
        elif args["task_type"] == TaskType.POST_PROCESSING:
            pass
        else:
            print("error")

    @staticmethod
    def task_multi(args: Dict[str, Any], const_var: int) -> None:  # TODO imeplement
        input_manager = InputManager()
        if args["task_type"] == TaskType.SIMULATION_MULTI_RUN:
            pass
        elif args["task_type"] == TaskType.SENSITIVITY_ANALYSIS:
            pass
        else:
            print("error")

    @staticmethod
    def bar1(args: Dict[str, Any], const_var: int, input_manager: InputManager) -> None:  # TODO remove
        print(f"bar 1 {args['task_type']=}, {const_var=}, {input_manager=}")
        print(args["task_type"].is_multi_run())

    @staticmethod
    def bar2(args: Dict[str, Any], const_var: int, input_manager: InputManager) -> None:  # TODO remove
        print(f"bar 2 {args['task_type']=}, {const_var=}, {input_manager=}")
        print(args["task_type"].is_multi_run())
