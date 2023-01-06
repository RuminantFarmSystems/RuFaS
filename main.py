# !/usr/bin/env python3

"""
This file serves as a main entry point to RuFaS.

The main function run_rufas() will execute the model simulation(s). It accepts a path to the location of the input
file(s) or, if this input is not given, it will run in interactive mode and accept input from the user.
"""
import argparse
from pathlib import Path
from typing import List

import config.global_variables
from RUFAS.output_manager import OutputManager
from RUFAS.simulation_engine import SimulationEngine
from RUFAS.user_prompt import obtain_file_list


def run_rufas(input_path=None, make_graphs=True, verbose=True):
    """ main function to run RuFaS, with options. If input_path is not provided, the interactive user prompt is
    triggered.
    """
    set_global_variables(make_graphs, verbose)
    if verbose:
        print("RuFaS: Ruminant Farm Systems Model 2022")
    file_list = obtain_file_list(input_path, verbose)
    execute_simulations_from_files(file_list)


def set_global_variables(make_graphs: bool, verbose: bool) -> None:
    """sets values of global variables in config/global_variables.py"""
    config.global_variables.PRODUCE_GRAPHICS = make_graphs
    config.global_variables.PRINT_STATUS_MESSAGES = verbose  # TODO: this is currently unimplemented - GitHub Issue #211


def execute_simulations_from_files(files: List[Path]) -> None:
    """execute simulations for each file"""
    output_manager = OutputManager()
    input_file_list = files
    for input_file_path in input_file_list:
        output_manager.flush_pools()
        simulator = SimulationEngine(input_file_path)
        simulator.simulate()
        output_manager.save_all_pools(r'output')

def parse_gnu_args():
    """parse command line options, if applicable"""
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", type=str, metavar="path", nargs="?",
                        help="path to input .json file or directory of .json files")
    # TODO: rather than a string, this should probably be a file handle as in the link below, but that would affect
    #   the current input handler, file reader, etc.
    #   https://stackoverflow.com/questions/11540854/file-as-command-line-argument-for-argparse-error-message-if-argument-is-not-va

    parser.add_argument("-ng", "--no-graphics", help="prevent graphics from generating", action="store_true")
    parser.add_argument("-v", "--verbose", help="print progress messages", action="store_true")
    # parser.add_argument("-i", "--interactive", help="run in interactive mode", action="store_true")

    return parser.parse_args()


if __name__ == '__main__':
    cmd_arguments = parse_gnu_args()
    run_rufas(input_path=cmd_arguments.input_path, make_graphs=not cmd_arguments.no_graphics, verbose=cmd_arguments.verbose)
