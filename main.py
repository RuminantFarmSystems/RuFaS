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
from RUFAS.scenario_manager import METADATA_PATHS

import config.global_variables
from RUFAS.simulation_engine import SimulationEngine
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.util import Utility


def run_rufas(
    produce_graphics: bool = True,
    verbose: bool = True,
    clear_output: bool = False,
    exclude_info_maps: bool = True,
) -> None:
    """Main function to run RuFaS, with options.

    Args:
        produce_graphics: produce graphics after simulation
        verbose: print progress messages while simulation is running
        clear_output: lear output directory before running the simulation
        exclude_info_map: exclude info_maps from the output
    """
    if clear_output:
        output_dir = Path(config.global_variables.OUT_DIR)
        keep_list = [".keep", "output_filters"]
        Utility.empty_dir(output_dir, keep=keep_list)

    set_global_variables(verbose)
    if verbose:
        print("RuFaS: Ruminant Farm Systems Model 2023")
    metadata_file_list = METADATA_PATHS
    execute_simulations(metadata_file_list, exclude_info_maps, produce_graphics)


def set_global_variables(verbose: bool) -> None:
    """Sets values of global variables in config/global_variables.py"""
    config.global_variables.PRINT_STATUS_MESSAGES = (
        verbose  # TODO: this is currently unimplemented - GitHub Issue #211
    )


def execute_simulations(
    metadata_files: List[Path],
    exclude_info_maps: bool = True,
    produce_graphics: bool = True,
) -> None:
    """Instantiates I/O Managers and processes the metadata files provided by the user to run the simulation.

    Parameters
    ----------
    metadata_files : List[Path]
        The list of Paths to the metadata files the user entered with which to run the simulation.

    exclude_info_maps : bool, optional
        Flag for whether or not the user wants to inlcude info_maps data in their results files.

    produce_graphics: bool, optional
        Flag for whether or not the user wants to produce graphs at after the simulation.
    """
    info_map = {
        "class": "No caller class",
        "function": execute_simulations.__name__,
    }
    sys.stdout.write("Simulating...\n")
    output_manager = OutputManager()
    input_manager = InputManager()
    metadata_file_list = metadata_files
    for metadata_file_path in metadata_file_list:
        input_manager.flush_pool()
        output_manager.flush_pools()
        is_data_valid = input_manager.start_data_processing(
            str(metadata_file_path), True
        )
        if is_data_valid:
            simulator = SimulationEngine()
            simulator.simulate()
        else:
            output_manager.add_error(
                "No simulation run",
                f"Data not valid for {metadata_file_path}, simulation not run",
                info_map,
            )
        output_manager.save_variables(
            r"output", r"output/output_filters/", exclude_info_maps, produce_graphics
        )
        output_manager.dump_all_nondata_pools(r"output", exclude_info_maps)


class CaseInsensitiveArgumentAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        for action in self.option_strings:
            setattr(namespace, action, values)


def parse_gnu_args() -> argparse.Namespace:
    """Parse command line options, if applicable"""
    parser = argparse.ArgumentParser(description="RuFaS: Whole dairy farm simulation")
    parser.register("action", "ci_action", CaseInsensitiveArgumentAction)
    parser.add_argument(
        "-g",
        "--no_graphics",
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
        help="Print progress messages while simulation is running",
        action="store_true",
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

    return parser.parse_args()


if __name__ == "__main__":
    cmd_arguments = parse_gnu_args()
    run_rufas(
        make_graphs=not cmd_arguments.no_graphics,
        verbose=cmd_arguments.verbose,
        clear_output=cmd_arguments.clear_output,
        exclude_info_maps=cmd_arguments.exclude_info_maps,
    )
