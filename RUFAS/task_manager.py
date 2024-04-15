from functools import partial
from typing import Any, Dict, List, TypedDict
import multiprocessing
from pathlib import Path

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.simulation_engine import SimulationEngine


class MetadataPath(TypedDict):  # TODO: revisit docstring
    """
    Contains the path(s) to the metadata file(s) that will run when a user runs a simulation and the
    prefix(es) the user wants to use to designate the output files from this simulation.

    main.py will import the METADATA_PATHS variable and class and use it to provide execute_simulations() with
    the list of metadata files and prefixes that they want to be used to run simulations.

    Attributes
    ----------
    prefix : str
        The prefix specifying the metadata file used to run the scenario. Will be used to
        generate a name for each of the output files for the scenario run with this metadata path.
    path : Path
        The path to the metadata file used for a simulation.

    Examples
    --------
    Single simulation:
        METADATA_PATHS: List[MetadataPaths] = [{"prefix": "default_scenario",
                                                "path": Path('input/metadata/default_metadata.json')},
                                              ]
        This will use the default_metadata.json file to point to the input
        files specified for this simulation scenario. All output files will have the "default_scenario"
        prefix: e.g. "default_scenario_errors_09-Oct...", "default_scenario_logs_09-Oct...", etc.

    Multiple simulations:
        METADATA_PATHS: List[MetadataPaths] = [{"prefix": "default_scenario",
                                                "path": Path('input/metadata/default_metadata.json')},
                                               {"prefix": "ARL_scenario",
                                                "path": Path('input/metadata/ARL_metadata.json')},
                                              ]
        This will run 2 simulations back to back - the first simulation will use the default_metadata.json
        file to point to one set of input files and will save the generated output files with the "default_scenario"
        prefix. The second simulation will run immediately after with no extra input from the user and will
        use the ARL_metadata.json file and save its output files with the "ARL_scenario" prefix.
    """

    prefix: str
    path: Path


class TaskManager:
    def __init__(self, workers: int):
        self.pool = multiprocessing.Pool(workers, maxtasksperchild=1)

    @staticmethod
    def task(metadata_path: MetadataPath, input_manager_pool: Dict[str, Any], input_manager_metadata: Dict[str, Any]) -> None:
        input_manager = InputManager()

        print(f"{metadata_path=}, {input_manager=}")
        print(f"x={x}")
        print(f"y={y}")

    def run_simulation_with_variations(
        self,
        metadata_paths: List[MetadataPath],
        input_manager_pool: Dict[str, Any],
        input_manager_metadata: Dict[str, Any],
    ) -> None:
        """Runs the simulation each time with a new random seed"""
        task_with_args = partial(
            self.task, input_manager_pool=input_manager_pool, input_manager_metadata=input_manager_metadata
        )
        results = self.pool.imap_unordered(task_with_args, metadata_paths)
        for _ in results:
            pass


if __name__ == "__main__":
    task_manager = TaskManager(workers=4)
    metadata_paths : List[MetadataPath] = [
        {"prefix": "1", "path": Path("input/metadata/default_metadata1.json")},
        {"prefix": "2", "path": Path("input/metadata/default_metadata2.json")},
        {"prefix": "3", "path": Path("input/metadata/default_metadata3.json")},
        {"prefix": "4", "path": Path("input/metadata/default_metadata4.json")},
        {"prefix": "5", "path": Path("input/metadata/default_metadata5.json")},
        {"prefix": "6", "path": Path("input/metadata/default_metadata6.json")},
        {"prefix": "7", "path": Path("input/metadata/default_metadata7.json")},
    ]
    x = {"key1": "value1", "key2": "value2"}  # Example dictionary x
    y = {"keyA": "valueA", "keyB": "valueB"}  # Example dictionary y
    task_manager.run_tasks(metadata_paths, x, y)
    METADATA_PATHS: List[MetadataPath] = [
        {"prefix": "default", "path": Path("input/metadata/default_metadata.json")},
    ]
