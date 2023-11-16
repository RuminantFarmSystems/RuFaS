# !/usr/bin/env python3

"""
This file serves as a main entry point to RuFaS.

The main function run_rufas() will execute the model simulation(s). It accepts a path to the location of the input
file(s) or, if this input is not given, it will run in interactive mode and accept input from the user.
"""
import argparse
from pathlib import Path
import sys
from typing import List

from RUFAS.scenario_manager import METADATA_PATHS, MetadataPaths

import config.global_variables
from RUFAS.simulation_engine import SimulationEngine
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager, LogVerbosity
from RUFAS.util import Utility


def main():
    cmd_arguments = parse_gnu_args()
    if cmd_arguments.load_pool:
        load_pool = True
    else:
        load_pool = False
    run_rufas(
        load_pool,
        produce_graphics=not cmd_arguments.no_graphics,
        format_option=cmd_arguments.format_option,
        verbose=LogVerbosity(cmd_arguments.verbose),
        clear_output=cmd_arguments.clear_output,
        exclude_info_maps=cmd_arguments.exclude_info_maps,
        only_run_validation=cmd_arguments.only_run_validation,
        graphics_dir=Path(cmd_arguments.graphics_dir),
        vars_file_path=Path(cmd_arguments.load_pool),
        output_dir=Path(cmd_arguments.output_dir),
        filters_dir=Path(cmd_arguments.filters_dir),
        init_herd=cmd_arguments.init_herd,
        save_animals=cmd_arguments.save_animals,
        terminate_simulation_post_herd_generation=cmd_arguments.terminate_simulation_post_herd_generation
    )


def run_rufas(
    load_pool: bool = False,
    produce_graphics: bool = True,
    format_option: str = "verbose",
    verbose: LogVerbosity = LogVerbosity.NONE,
    clear_output: bool = False,
    exclude_info_maps: bool = False,
    only_run_validation: bool = False,
    graphics_dir: Path = Path(""),
    vars_file_path: Path = Path(""),
    output_dir: Path = Path("output/"),
    filters_dir: Path = Path("output/output_filters/"),
    init_herd: bool = False,
    save_animals: bool = False,
    terminate_simulation_post_herd_generation: bool = False
) -> None:
    """
    Main function to run RuFaS, with options.

    Parameters
    ----------
    load_pool : bool, optional, default=False
        Flag to load json file into Output Manager variables pool for processing.
    produce_graphics : bool, optional, default=True
        Produce graphics after simulation.
    format_option : str, optional, default="verbose"
        Format for variable_names.txt output file.
    verbose : bool, optional, default=True
        Print progress messages while simulation is running.
    clear_output : bool, optional, default=False
        Clear output directory before running the simulation.
    exclude_info_maps : bool, optional, default=False
        Exclude info_maps from the output.
    only_run_validation : bool, optional, default=False
        Validate input data and don't run a simulation.
    graphics_dir : Path, optional, default=Path("")
        The directory for saving graphics.
    vars_file_path : Path, optional, default=Path("")
        The path to the json file to load into Output Manager variables pool for processing.
    output_dir : Path, optional, default=Path("output/")
        The directory for saving output.
    filters_dir : Path, optional, default=Path("output/output_filters")
        The directory for the files containing the keys for filtering.
    init_herd: bool
        Initialize herd with simulation.
    save_animals: bool
        User input indicating whether to save the generated animals to CSV files.
    terminate_simulation_post_herd_generation: bool
        User input indicating whether to terminate the simulation after herd generation.
    """
    sys.stdout.write("RuFaS: Ruminant Farm Systems Model 2023\n")

    if load_pool:
        run_load_vars_pool(vars_file_path, exclude_info_maps, format_option,
                           produce_graphics, graphics_dir, clear_output, output_dir,
                           filters_dir)
        return

    if clear_output:
        clear_output_dir()

    metadata_files: List[MetadataPaths] = METADATA_PATHS
    if only_run_validation:
        run_validation(metadata_files, exclude_info_maps, format_option, verbose, output_dir)
    else:
        execute_simulations(
            metadata_files,
            exclude_info_maps,
            produce_graphics,
            graphics_dir,
            format_option,
            verbose,
            output_dir,
            filters_dir,
            init_herd,
            save_animals,
            terminate_simulation_post_herd_generation
        )


def clear_output_dir(vars_file_path: Path = None) -> None:
    """Clears the output directory if vars_file_path not in output directory.

    Parameters
    ----------
    vars_file_path : Path, optional, default=None
        Path to file used to load Output Manager vars pool.
    """
    info_map = {
        "class": "No caller class",
        "function": clear_output_dir.__name__,
    }
    output_manager = OutputManager()
    output_dir = Path(config.global_variables.OUT_DIR)
    is_file_found_in_dir = is_file_in_dir(output_dir, vars_file_path)
    if is_file_found_in_dir:
        output_manager.add_error("Can't clear output directory", f"{vars_file_path} in output directory.", info_map)
    else:
        keep_list = [".keep", "output_filters"]
        Utility.empty_dir(output_dir, keep=keep_list)
        output_manager.add_log("Output directory cleared", "No conflicts to clearing output directory.", info_map)


def is_file_in_dir(dir_path: Path = Path(config.global_variables.OUT_DIR), file_path: Path = None) -> bool:
    """Checks if a file path is in the provided directory.

    Parameters
    ----------
    dir_path : Path, optional, default=Path(config.global_variables.OUT_DIR)
        Path to the directory to be checked.
    file_path : Path, optional, default=None
        Path to file to be checked.
    """
    if file_path is None:
        return False
    file_path = file_path.resolve()
    directory_path = dir_path.resolve()

    return directory_path == file_path or directory_path in file_path.parents


def run_load_vars_pool(
    vars_file_path: Path = Path(""),
    exclude_info_maps: bool = False,
    format_option: str = "verbose",
    produce_graphics: bool = True,
    graphics_dir: Path = Path(""),
    clear_output: bool = False,
    output_dir: Path = Path("output/"),
    filters_dir: Path = Path("output/output_filters/")
) -> None:
    """Instantiates Output Manager and triggers loading of the variables pool from the provided file path
    for post-processing.

    Parameters
    ----------
    vars_file_path : Path, optional, default=Path("")
        The path to the json file to load into Output Manager variables pool for processing.
    exclude_info_maps : bool, optional
        Flag for whether or not the user wants to inlcude info_maps data in their results files.
    produce_graphics : bool, optional
        Flag for whether or not the user wants to produce graphs at after the simulation.
    graphics_dir : Path, optional
        The directory for saving graphics.
    clear_output : bool, optional
        Flag for whether or not the user wants to clear the output directory.
    output_dir : Path, optional, default=Path("output/")
        The directory for saving output.
    filters_dir : Path, optional, default=Path("output/output_filters")
        The directory for the files containing the keys for filtering.
    """
    if clear_output:
        clear_output_dir(vars_file_path)
    output_manager = OutputManager()
    output_manager.flush_pools()
    output_manager.load_variables_pool_from_file(vars_file_path)
    output_manager.set_metadata_prefix("reload")
    output_manager.save_results(
            output_dir,
            filters_dir,
            exclude_info_maps,
            produce_graphics,
            graphics_dir,
        )
    output_manager.dump_all_nondata_pools(
            output_dir, exclude_info_maps, format_option
        )


def run_validation(
    metadata_files: List[MetadataPaths],
    exclude_info_maps: bool = False,
    format_option: str = "verbose",
    verbose: LogVerbosity = LogVerbosity.NONE,
    output_dir: Path = Path("output/"),
) -> None:
    """Instantiates I/O Managers and triggers validation of input data.

    Parameters
    ----------
    metadata_files : List[MetadataPaths]
        The list of Paths to the metadata files the user entered with which to run the simulation.
    exclude_info_maps : bool, optional
        Flag for whether the user wants to include info_maps data in their results files.
    format_option : str
        The formatting option for select output files.
    verbose : LogVerbosity
        The verbose option set by the user.
    output_dir : Path, optional, default=Path("output/")
        The directory for saving output.
    """
    info_map = {
        "class": "No caller class",
        "function": run_validation.__name__,
    }
    output_manager = OutputManager()
    input_manager = InputManager()
    output_manager.add_log(
        "Validation only",
        "***Only validating data, no simulation will follow.***",
        info_map,
    )
    output_manager.set_log_verbose(verbose)
    for metadata_file in metadata_files:
        input_manager.flush_pool()
        output_manager.flush_pools()
        output_manager.add_log(
            "Validation start",
            f"Validating data for {str(metadata_file['path'])}...\n",
            info_map,
        )
        is_data_valid = input_manager.start_data_processing(
            str(metadata_file["path"]), False
        )
        if is_data_valid:
            output_manager.add_log("Validation", "Data is valid.\n\n", info_map)
        else:
            output_manager.add_warning(
                "Validation",
                f"Data not valid for {metadata_file['path']}.\n\n",
                info_map,
            )
        output_manager.dump_all_nondata_pools(
            output_dir, exclude_info_maps, format_option
        )


def execute_simulations(
    metadata_files: List[MetadataPaths],
    exclude_info_maps: bool = False,
    produce_graphics: bool = True,
    graphics_dir: Path = Path(""),
    format_option: str = "verbose",
    verbose: LogVerbosity = LogVerbosity.NONE,
    output_dir: Path = Path("output/"),
    filters_dir: Path = Path("output/output_filters/"),
    init_herd: bool = False,
    save_animals: bool = False,
    terminate_simulation_post_herd_generation: bool = False
) -> None:
    """Instantiates I/O Managers and processes the metadata files provided by the user to run the simulation.

    Parameters
    ----------
    metadata_files : List[MetadataPaths]
        A list of custom TypedDict objects including the specified prefix for the save_results output file
        and the path to the metadata file.

    exclude_info_maps : bool, optional
        Flag for whether the user wants to include info_maps data in their results files.
    produce_graphics: bool, optional
        Flag for whether or not the user wants to produce graphs at after the simulation.
    graphics_dir : Path, optional
        The directory for saving graphics.
    format_option : str
        The formatting option for select output files.
    verbose : LogVerbosity
        The verbose option set by the user.
    output_dir : Path, optional, default=Path("output/")
        The directory for saving output.
    filters_dir : Path, optional, default=Path("output/output_filters")
        The directory for the files containing the keys for filtering.
    init_herd: bool
        Initialize herd with simulation.
    save_animals: bool
        User input indicating whether to save the generated animals to CSV files.
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
        is_data_valid = input_manager.start_data_processing(
            str(metadata_file["path"]), True
        )
        if is_data_valid:
            output_manager.add_log(
                "Validation complete", "Data is valid. \nSimulating...\n", info_map
            )
            simulator = SimulationEngine(init_herd,
                                         save_animals,
                                         terminate_simulation_post_herd_generation)
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
        output_manager.save_results(
            output_dir,
            filters_dir,
            exclude_info_maps,
            produce_graphics,
            graphics_dir,
        )
        output_manager.dump_all_nondata_pools(
            output_dir, exclude_info_maps, format_option
        )


class CaseInsensitiveArgumentAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None) -> None:
        for action in self.option_strings:
            setattr(namespace, action, values)


def parse_gnu_args() -> argparse.Namespace:
    """Parse command line options, if applicable"""
    parser = argparse.ArgumentParser(description="RuFaS: Whole dairy farm simulation")
    parser.register("action", "ci_action", CaseInsensitiveArgumentAction)
    parser.add_argument(
        "-f",
        "--format-option",
        choices=["block", "inline", "verbose", "basic"],
        help="Select formatting option for variable_names.txt file",
    )
    parser.add_argument(
        "-g",
        "--no-graphics",
        help="Prevent graphics from generating",
        action="store_true",
    )
    parser.add_argument(
        "-G",
        "--graphics_dir",
        help="The saving directory for graphics",
        default="graphics",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        choices=["errors", "warnings", "logs", "none"],
        default="none",
        help="Specify the log type to be printed",
    )
    parser.add_argument(
        "-c",
        "--clear-output",
        help="Clear output directory before running the simulation",
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
        "--only-run-validation",
        help="Only validate the data, don't run a simulation",
        action="store_true",
    )
    parser.add_argument(
        "-l",
        "--load-pool",
        help="Load the output manager's variables pool from provided path",
        default="",
    )
    parser.add_argument(
        "-O",
        "--output-dir",
        help="The saving directory for output",
        default="output/",
    )
    parser.add_argument(
        "-F",
        "--filters-dir",
        help="The directory for the files containing the keys for filtering",
        default="output/output_filters/",
    )
    parser.add_argument(
        "-I",
        "--init_herd",
        help="Initialize herd with simulation",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--save_animals",
        help="Save animals to CSV files",
        action="store_true",
    )
    parser.add_argument(
        "-t",
        "--terminate_simulation_post_herd_generation",
        help="Save generated animals to CSV files",
        action="store_true",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
