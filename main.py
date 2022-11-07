# !/usr/bin/env python

"""
This file serves as a main entry point to RuFaS.

The main function run_rufas() will execute the model simulation(s). It accepts a path to the location of the input
file(s) or, if this input is not given, it will run in interactive mode and accept input from the user.
"""

import config.global_variables
import argparse
from RUFAS.simulation_engine import SimulationEngine
from RUFAS.user_prompt import get_files_from_input


def run_rufas(in_path=None, make_graphs=True, verbose=True):
    """ main function to run RuFaS, with options. If in_file is not provided, the interactive user prompt is triggered
    """
    set_global_variables(make_graphs, verbose)
    if verbose:
        print_rufas_intro()
    file_list = get_files_from_input(in_path, verbose)
    simulate_from_files(file_list)


def set_global_variables(make_graphs: bool, verbose: bool) -> None:
    """set values of global variables in config/global_variables.py"""
    config.global_variables.SUPPRESS_GRAPHICS = not make_graphs
    config.global_variables.PRINT_STATUS_MESSAGES = verbose  # TODO: this is currently unimplemented


def print_rufas_intro() -> None:
    """print introduction message"""
    print("RuFaS: Ruminant Farm Systems Model 2022")


def simulate_from_files(files) -> None:
    """execute simulations for each file"""
    for f in files:
        simulator = SimulationEngine(f)
        simulator.simulate()


def parse_gnu_args():
    """parse command line options, if applicable"""
    parser = argparse.ArgumentParser()
    parser.add_argument("in_path", type=str, metavar="path", nargs="?",
                        help="path to input .json file or directory of .json files")
    # TODO: rather than a string, this should probably be a file handle as in the link below, but that would affect
    #   the current input handler, file reader, etc.
    #   https://stackoverflow.com/questions/11540854/file-as-command-line-argument-for-argparse-error-message-if-argument-is-not-va

    parser.add_argument("--no-graphics", help="prevent graphics from generating", action="store_true")
    parser.add_argument("-v", "--verbose", help="print progress messages", action="store_true")
    # parser.add_argument("-i", "--interactive", help="run in interactive mode", action="store_true")

    return parser.parse_args()


if __name__ == '__main__':
    cmd_arguments = parse_gnu_args()
    run_rufas(in_path=cmd_arguments.in_path, make_graphs=not cmd_arguments.no_graphics, verbose=cmd_arguments.verbose)
