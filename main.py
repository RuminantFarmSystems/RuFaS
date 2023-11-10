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
    run_rufas(
        produce_graphics=not cmd_arguments.no_graphics,
        format_option=cmd_arguments.format_option,
        verbose=LogVerbosity(cmd_arguments.verbose),
        clear_output=cmd_arguments.clear_output,
        exclude_info_maps=cmd_arguments.exclude_info_maps,
        only_run_validation=cmd_arguments.only_run_validation,
        graphics_dir=Path(cmd_arguments.graphics_dir),
    )


def run_rufas(
    produce_graphics: bool = True,
    format_option: str = "verbose",
    verbose: LogVerbosity = LogVerbosity.NONE,
    clear_output: bool = False,
    exclude_info_maps: bool = False,
    only_run_validation: bool = False,
    graphics_dir: Path = Path(""),
) -> None:
    """Main function to run RuFaS, with options.

    Args:
        produce_graphics: produce graphics after simulation
        verbose: print progress messages while simulation is running
        clear_output: lear output directory before running the simulation
        exclude_info_map: exclude info_maps from the output
        graphics_dir : Path, optional
            The directory for saving graphics.
        produce_graphics: produce graphics after simulation
        format_option: format for variable_names.txt output file
        verbose: print errors, warnings, and/or logs during the simulation
        clear_output: lear output directory before running the simulation
        exclude_info_map: exclude info_maps from the output
        only_run_validation: validate input data and don't run a simulation
        graphics_dir : Path, optional
            The directory for saving graphics.
    """
    if clear_output:
        output_dir = Path(config.global_variables.OUT_DIR)
        keep_list = [".keep", "output_filters"]
        Utility.empty_dir(output_dir, keep=keep_list)

    sys.stdout.write("RuFaS: Ruminant Farm Systems Model 2023\n")
    metadata_file_list: List[MetadataPaths] = METADATA_PATHS
    if only_run_validation:
        run_validation(metadata_file_list, exclude_info_maps, format_option, verbose)
    else:
        execute_simulations(
            metadata_file_list,
            exclude_info_maps,
            produce_graphics,
            graphics_dir,
            format_option,
            verbose,
        )


def run_validation(
    metadata_files: List[Path],
    exclude_info_maps: bool = False,
    format_option: str = "verbose",
    verbose: LogVerbosity = LogVerbosity.NONE,
) -> None:
    """Instantiates I/O Managers and triggers validation of input data.

    Parameters
    ----------
    metadata_files : List[Path]
        The list of Paths to the metadata files the user entered with which to run the simulation.
    exclude_info_maps : bool, optional
        Flag for whether or not the user wants to inlcude info_maps data in their results files.
    format_option : str
        The formatting option for select output files.
    verbose : LogVerbosity
        The verbose option set by the user.
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
            r"output", exclude_info_maps, format_option
        )


def execute_simulations(
    metadata_files: List[MetadataPaths],
    exclude_info_maps: bool = False,
    produce_graphics: bool = True,
    graphics_dir: Path = Path(""),
    format_option: str = "verbose",
    verbose: LogVerbosity = LogVerbosity.NONE,
) -> None:
    """Instantiates I/O Managers and processes the metadata files provided by the user to run the simulation.

    Parameters
    ----------
    metadata_files : List[MetadataPaths]
        A list of custom TypedDict objects including the specified prefix for the save_results output file
        and the path to the metadata file.

    exclude_info_maps : bool, optional
        Flag for whether or not the user wants to inlcude info_maps data in their results files.
    produce_graphics: bool, optional
        Flag for whether or not the user wants to produce graphs at after the simulation.

    graphics_dir : Path, optional
        The directory for saving graphics.
    format_option : str
        The formatting option for select output files.
    verbose : LogVerbosity
        The verbose option set by the user.
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
        output_manager.save_results(
            Path(r"output"),
            Path(r"output/output_filters/"),
            exclude_info_maps,
            produce_graphics,
            graphics_dir,
        )
        output_manager.dump_all_nondata_pools(
            r"output", exclude_info_maps, format_option
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
    return parser.parse_args()


if __name__ == "__main__":
    main()
