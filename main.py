# !/usr/bin/env python3

"""
This file serves as a main entry point to RuFaS.

The main function run_rufas() will execute the model simulation(s). It accepts a path to the location of the input
file(s) or, if this input is not given, it will run in interactive mode and accept input from the user.
"""
import argparse
import sys
import traceback
from pathlib import Path
from typing import Any

from RUFAS.output_manager import LogVerbosity, OutputManager
from RUFAS.task_manager import TaskManager


def main() -> None:
    cmd_arguments = parse_gnu_args(sys.argv[1:])
    try:
        task_manager = TaskManager()
        task_manager.start(
            metadata_path=Path(cmd_arguments.path_to_metadata),
            verbosity=LogVerbosity(cmd_arguments.verbose),
            exclude_info_maps=cmd_arguments.exclude_info_maps,
            output_directory=Path(cmd_arguments.output_dir),
            logs_directory=Path(cmd_arguments.logs_dir),
            clear_output_directory=cmd_arguments.clear_output,
            produce_graphics=not cmd_arguments.no_graphics,
            suppress_log_files=cmd_arguments.suppress_log_files,
            metadata_depth_limit=cmd_arguments.metadata_depth_limit,
        )
    except Exception as e:
        info_map = {
            "class": "No caller class",
            "function": main.__name__,
        }
        output_manager = OutputManager()
        error_message = "This terminal error occurred during runtime. "
        error_message += traceback.format_exc()
        output_manager.add_error(
            f"Dumping all logs from main.py because of error '{e}'",
            error_message,
            info_map,
        )
        output_manager.create_directory(Path(cmd_arguments.logs_dir))
        output_manager.dump_all_nondata_pools(
            Path(cmd_arguments.logs_dir),
            cmd_arguments.exclude_info_maps,
            "block",
        )
        output_manager.add_error(
            "Early termination",
            "Unexpected early termination of the simulation. Please see logs for details.\n",
            info_map,
        )
        is_data_valid = input_manager.start_data_processing(str(metadata_file["path"]), False)
        if is_data_valid:
            output_manager.add_log("Validation", "Data is valid.\n\n", info_map)
        else:
            output_manager.add_warning(
                "Validation",
                f"Data not valid for {metadata_file['path']}.\n\n",
                info_map,
            )
        output_manager.dump_all_nondata_pools(output_dir, exclude_info_maps, format_option)


def initialize_herd(
    simulation_config: Config,
    init_herd: bool = False,
    save_animals: bool = False,
    save_animals_dir: Path = Path("output/"),
    terminate_simulation_post_herd_generation: bool = False,
) -> None:
    """
    Initializes a herd based on the provided simulation configuration.

    Parameters
    ----------
    simulation_config : Config
        Config object containing parameters and settings for the simulation.
    init_herd: bool
        User input indicating whether to initialize herd with simulation.
    save_animals: bool
        User input indicating whether to save the generated animals to JSON files.
    save_animals_dir : Path
        User input indicating the save directory for generated animals.
    terminate_simulation_post_herd_generation: bool
        User input indicating whether to terminate the simulation after herd generation.

    Returns
    -------
    None

    Notes
    -----
    This function is responsible for setting up the initial state of the herd
    based on the given configuration. It can also save the initialized herd data
    to a specified directory.

    The function utilizes an `OutputManager` for logging various stages and events
    during the initialization process. It also respects the seed settings
    provided in the simulation configuration for consistent results.
    """
    info_map = {
        "class": "No caller class",
        "function": initialize_herd.__name__,
    }
    output_manager = OutputManager()

    if simulation_config.set_seed:
        random.seed(simulation_config.seed)
        numpy.random.seed(simulation_config.seed)

    output_manager.add_log("Herd initialization start", "Initializing herd data...\n", info_map)
    herd_factory = HerdFactory(
        init_herd=init_herd,
        save_animals=save_animals,
        save_animals_path=save_animals_dir,
    )
    herd_factory.initialize_herd()
    output_manager.add_log("Herd initialization complete", "Herd data initialized.\n", info_map)

    if terminate_simulation_post_herd_generation:
        output_manager.add_log(
            "Herd generation only",
            "***Only generating herd data, no simulation will follow.***",
            info_map,
        )


def execute_simulations(
    metadata_files: List[MetadataPaths],
    exclude_info_maps: bool,
    produce_graphics: bool,
    graphics_dir: Path,
    format_option: str,
    verbose: LogVerbosity,
    output_dir: Path,
    filters_dir: Path,
    csv_dir: Path,
    init_herd: bool,
    save_animals: bool,
    save_animals_dir: Path,
    terminate_simulation_post_herd_generation: bool,
) -> None:
    """Instantiates I/O Managers and processes the metadata files provided by the user to run the simulation.

    Parameters
    ----------
    metadata_files : List[MetadataPaths]
        A list of custom TypedDict objects including the specified prefix for the save_results output file
        and the path to the metadata file.
    exclude_info_maps : bool
        Flag for whether or not the user wants to inlcude info_maps data in their results files.
    produce_graphics: bool
        Flag for whether or not the user wants to produce graphs at after the simulation.
    graphics_dir : Path
        The directory for saving graphics.
    format_option : str
        The formatting option for select output files.
    verbose : LogVerbosity
        The verbose option set by the user.
    output_dir : Path
        The directory for saving output.
    filters_dir : Path
        The directory for the files containing the keys for filtering.
    csv_dir : Path
        The directory for the csv output files to be saved.
    init_herd: bool
        Initialize herd with simulation.
    save_animals: bool
        User input indicating whether to save the generated animals to JSON files.
    save_animals_dir : Path
        User input indicating the save directory for generated animals.
    terminate_simulation_post_herd_generation: bool
        User input indicating whether to terminate the simulation after herd generation.
    """
    info_map = {
        "class": "No caller class",
        "function": execute_simulations.__name__,
    }
    sys.stdout.write("Simulating...\n")
    output_manager = OutputManager()
    input_manager = InputManager()
    output_manager.set_log_verbose(verbose)
    for metadata_file in metadata_files:
        input_manager.flush_pool()
        output_manager.flush_pools()
        output_manager.add_log(
            "Validation start",
            f"Validating data for {str(metadata_file['path'])}...\n",
            info_map,
        )
        output_manager.set_metadata_prefix(metadata_file["prefix"])
        is_data_valid = input_manager.start_data_processing(str(metadata_file["path"]), True)
        if is_data_valid:
            output_manager.add_log("Validation complete", "Data is valid. \nSimulating...\n", info_map)
            simulation_config = Config(input_manager.get_data("config"))
            # herd_size = input_manager.get_data("animal.herd_information.herd_num")
            # print(f"herd from main: {herd_size}")
            # from RUFAS.routines.temp import Temp

            # t = Temp()
            # t.test(input_manager)
            # exit()
            try:
                initialize_herd(
                    simulation_config=simulation_config,
                    init_herd=init_herd,
                    save_animals=save_animals,
                    save_animals_dir=save_animals_dir,
                    terminate_simulation_post_herd_generation=terminate_simulation_post_herd_generation,
                )
            except Exception as e:
                output_manager.dump_all_nondata_pools(
                    path=output_dir,
                    exclude_info_maps=exclude_info_maps,
                    format_option=format_option,
                )
                raise e

            if not terminate_simulation_post_herd_generation:
                simulator = SimulationEngine()
                simulator.simulate()
        else:
            output_manager.add_error(
                "Validation complete",
                f"Data not valid for {str(metadata_file['path'])}, simulation not run",
                info_map,
            )
            output_manager.add_error(
                "No simulation run",
                f"Data not valid for {str(metadata_file['path'])}, simulation not run",
                info_map,
            )
        from RUFAS.routines.EEE.energy import EnergyEstimator

        EnergyEstimator.estimate_all()
        diesel_filter = {
            "name": "Diesel Consumption",
            "filters": ["total_diesel_consumption_tractor_implement"],
            "variables": [".*"],
        }
        deisel_consumption = output_manager.filter_variables_pool_complex(diesel_filter)
        print(deisel_consumption)
        diesel_filter = {
            "name": "Diesel Consumption",
            "filters": ["diesel_consumption_tractor_implement"],
            "variables": [".*"],
        }
        deisel_consumption = output_manager.filter_variables_pool_complex(diesel_filter)
        print(deisel_consumption)
        output_manager.save_results(output_dir, filters_dir, exclude_info_maps, produce_graphics, graphics_dir, csv_dir)
        input_manager.dump_get_data_logs(path=output_dir)
        output_manager.dump_all_nondata_pools(output_dir, exclude_info_maps, format_option)


class CaseInsensitiveArgumentAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None) -> None:
        for action in self.option_strings:
            setattr(namespace, action, values)


def parse_gnu_args(args: Any | None = None) -> argparse.Namespace:
    """Parse command line options, if applicable"""
    parser = argparse.ArgumentParser(description="RuFaS: Whole dairy farm simulation")
    parser.register("action", "ci_action", CaseInsensitiveArgumentAction)
    parser.add_argument(
        "-g",
        "--no-graphics",
        help="Prevents graphics from generating",
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        choices=["errors", "warnings", "logs", "credits", "none"],
        default="credits",
        help="Specifies the log type to be printed",
    )
    parser.add_argument(
        "-c",
        "--clear-output",
        help="CAUTION! Clears output directory before running the simulation",
        action="store_true",
    )
    parser.add_argument(
        "-i",
        "--exclude_info_maps",
        help="Exclude info_maps from the output",
        action="store_true",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        help="The saving directory for output",
        default="output/",
    )
    parser.add_argument(
        "-s",
        "--suppress-log-files",
        help="Prevents logs from the Task Manager being written to files",
        action="store_true",
    )
    parser.add_argument(
        "-l",
        "--logs-dir",
        help="The directory for saving log files too",
        default="output/logs",
    )
    parser.add_argument(
        "-m", "--metadata-depth-limit", help="Overrides the default metadata depth limit in the Input Manager", type=int
    )
    parser.add_argument(
        "-p",
        "--path-to-metadata",
        help="Path to the task manager metadata that will determine the tasks run",
        default="input/metadata/task_manager_metadata.json",
    )
    return parser.parse_args(args)


if __name__ == "__main__":
    main()
