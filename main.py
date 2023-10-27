# !/usr/bin/env python3

"""
This file serves as a main entry point to RuFaS.

The main function run_rufas() will execute the model simulation(s). It accepts a path to the location of the input
file(s) or, if this input is not given, it will run in interactive mode and accept input from the user.
"""
import argparse
from enum import Enum
from pathlib import Path
import sys
from typing import List
from RUFAS.scenario_manager import METADATA_PATHS, MetadataPaths

import config.global_variables
from RUFAS.simulation_engine import SimulationEngine
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.util import Utility


class LogType(Enum):
    """
    The different types of logs collected by Output Manager.

    Notes
    -----
    Selecting NONE will tell OutputManager not to print out anything during a simulation.
    Selecting ERRORS will tell OutputManager to print out all errors added during a simulation.
    Selecting WARNINGS will tell OutputManager to print out all warnings and errors added during a simulation.
    Selecting LOGS will tell OutputManager to print out all logs, warnings, and errors added during a simulation. 
    """
    NONE = "none"
    ERRORS = "errors"
    WARNINGS = "warnings"
    LOGS = "logs"


def main():
    cmd_arguments = parse_gnu_args()
    run_rufas(
        format_option=cmd_arguments.format_option,
        make_graphs=not cmd_arguments.no_graphics,
        verbose=cmd_arguments.verbose,
        clear_output=cmd_arguments.clear_output,
        exclude_info_maps=cmd_arguments.exclude_info_maps,
        only_run_validation=cmd_arguments.only_run_validation,
    )


def run_rufas(
    format_option: str = "verbose",
    make_graphs: bool = True,
    verbose: LogType = LogType("none"),
    clear_output: bool = False,
    exclude_info_maps: bool = False,
    only_run_validation: bool = False,
) -> None:
    """Main function to run RuFaS, with options.

    Args:
        format_option: format for variable_names.txt output file
        make_graphs: prevent graphics from generating
        verbose: print progress messages while simulation is running
        clear_output: lear output directory before running the simulation
        exclude_info_map: exclude info_maps from the output
        only_run_validation: validate input data and don't run a simulation
    """
    if clear_output:
        output_dir = Path(config.global_variables.OUT_DIR)
        keep_list = [".keep", "output_filters"]
        Utility.empty_dir(output_dir, keep=keep_list)

    set_global_variables(make_graphs, verbose)
    if verbose in LogType.LOGS:
        sys.stdout.write("RuFaS: Ruminant Farm Systems Model 2023\n")
    metadata_file_list: List[MetadataPaths] = METADATA_PATHS
    if only_run_validation:
        run_validation(metadata_file_list, exclude_info_maps, format_option)
    else:
        execute_simulations(metadata_file_list, exclude_info_maps, format_option)


def set_global_variables(make_graphs: bool) -> None:
    """Sets values of global variables in config/global_variables.py"""
    config.global_variables.PRODUCE_GRAPHICS = make_graphs


def run_validation(metadata_files: List[Path], exclude_info_maps: bool = False,
                   format_option: str = "verbose",) -> None:
    """Instantiates I/O Managers and triggers validation of input data.

    Parameters
    ----------
    metadata_files : List[Path]
        The list of Paths to the metadata files the user entered with which to run the simulation.
    exclude_info_maps : bool, optional
        Flag for whether or not the user wants to inlcude info_maps data in their results files.
    format_option : str
        The formatting option for select output files.
    """
    info_map = {"class": "No caller class",
                "function": run_validation.__name__,
                }
    output_manager = OutputManager()
    input_manager = InputManager()
    sys.stdout.write("***Only validating data, no simulation will follow.***\n\n")
    for metadata_file in metadata_files:
        input_manager.flush_pool()
        output_manager.flush_pools()
        output_manager.add_log("Validation start.", f"Validating data for {str(metadata_file['path'])}...\n", info_map)
        is_data_valid = input_manager.start_data_processing(str(metadata_file["path"]), False)
        if is_data_valid:
            output_manager.add_log("Data valid", "Data is valid.\n\n", info_map)
        else:
            output_manager.add_warning("Data not valid", f"Data not valid for {metadata_file['path']}.\n\n", info_map)
        output_manager.dump_all_nondata_pools(r"output", exclude_info_maps, format_option)


def execute_simulations(
    metadata_files: List[Path], exclude_info_maps: bool = False, format_option: str = "verbose",
) -> None:
    """Instantiates I/O Managers and processes the metadata files provided by the user to run the simulation.

    Parameters
    ----------
    metadata_files : MetadataPaths
        A list of custom TypedDict objects including the specified prefix for the save_variables output file
        and the path to the metadata file.
    exclude_info_maps : bool, optional
        Flag for whether or not the user wants to inlcude info_maps data in their results files.
    format_option : str
        The formatting option for select output files.
    """
    info_map = {"class": "No caller class",
                "function": execute_simulations.__name__,
                }
    output_manager = OutputManager()
    input_manager = InputManager()
    for metadata_file in metadata_files:
        input_manager.flush_pool()
        output_manager.flush_pools()
        if config.global_variables.PRINT_STATUS_MESSAGES:
            sys.stdout.write(f"Validating data for {str(metadata_file['path'])}...\n")
        output_manager.set_metadata_prefix(metadata_file['prefix'])
        is_data_valid = input_manager.start_data_processing(str(metadata_file["path"]), True)
        if is_data_valid:
            if config.global_variables.PRINT_STATUS_MESSAGES:
                sys.stdout.write("Data is valid. \nSimulating...\n")
            simulator = SimulationEngine()
            simulator.simulate()
        else:
            if config.global_variables.PRINT_STATUS_MESSAGES:
                sys.stdout.write(f"Data not valid for {metadata_file['path']}, simulation not run\n\n")
            output_manager.add_error("No simulation run",
                                     f"Data not valid for {str(metadata_file['path'])}, simulation not run", info_map)
        output_manager.save_variables(r"output", r"output/output_filters/", exclude_info_maps)
        output_manager.dump_all_nondata_pools(r"output", exclude_info_maps)


def parse_gnu_args():
    """Parse command line options, if applicable"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--format-option",
        choices=['block', 'inline', 'verbose', 'basic'],
        help="Select formatting option for variable_names.txt file",
    )
    parser.add_argument(
        "-ng",
        "--no-graphics",
        help="Prevent graphics from generating",
        action="store_true",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        choices=list(LogType),
        help="Specify the log type: ERRORS, WARNINGS, LOGS, NONE",
    )
    parser.add_argument(
        "-co",
        "--clear-output",
        help="Clear output directory before running the simulation",
        action="store_true",
    )
    parser.add_argument(
        "-ei",
        "--exclude_info_maps",
        help="Exclude info_maps from the output",
        action="store_true",
    )
    parser.add_argument(
        "-ov",
        "--only-run-validation",
        help="Only validate the data, don't run a simulation",
        action="store_true",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
