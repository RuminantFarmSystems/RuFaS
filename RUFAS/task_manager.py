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


class TaskManager:
    def __init__(self):
        self.input_manager = InputManager()
        self.output_manager = OutputManager()
        self.parsed_task_args: List[Dict[str, Any]] = []

    def start(self, metadata_path: str) -> None:
        self.input_manager.start_data_processing(metadata_path)
        workers: int = self.input_manager.get_data("tasks.parallel_workers")
        self.pool = multiprocessing.Pool(
            workers, maxtasksperchild=1
        )  # maxtasksperchild=1 to maintain isolation between tasks and ensure no memory leaks happens in IO Managers
        self._parse_input_tasks()
        print(f"{self.input_manager=}")
        task_with_args = partial(self.task, const_var=1)  # TODO remove or fix const_var
        results = self.pool.imap_unordered(task_with_args, self.parsed_task_args)
        for _ in results:
            pass

    def _parse_input_tasks(self) -> None:
        tasks_from_input: Dict[str, Any] = self.input_manager.get_data("tasks.tasks")
        for input_task in tasks_from_input:
            parsed_task_arg = {
                "task_type": TaskType.from_string(input_task["task_type"]),
            }
            self.parsed_task_args.append(parsed_task_arg)

    @staticmethod
    def bar1(args: Dict[str, Any], const_var: int, input_manager: InputManager) -> None:
        print(f"bar 1 {args['task_type']=}, {const_var=}, {input_manager=}")

    @staticmethod
    def bar2(args: Dict[str, Any], const_var: int, input_manager: InputManager) -> None:
        print(f"bar 2 {args['task_type']=}, {const_var=}, {input_manager=}")

    @staticmethod
    def task(args: Dict[str, Any], const_var: int) -> None:
        input_manager = InputManager()
        if args["task_type"] == TaskType.SIMULATION_SIGNLE_RUN:
            TaskManager.bar1(args, const_var, input_manager)
        elif args["task_type"] == TaskType.HERD_INITIALIZATION:
            TaskManager.bar2(args, const_var, input_manager)
        else:
            print("error")
