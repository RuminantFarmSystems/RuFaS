# !/usr/bin/env python
import config.definitions
from sys import argv
import argparse
from RUFAS.simulation_engine import SimulationEngine
from RUFAS import user_prompt
from pathlib import Path


def validate(inpath="input/ARL.json", make_graphs=True, verbose=True, interactive=False):
    """
    Variation of the main RUFAS function, through which model calibration, validation, sensitivity analyses, and testing
    can be conducted.
    """

    # Handle flags
    config.definitions.SUPPRESS_GRAPHICS = not make_graphs
    config.definitions.PRINT_STATUS_MESSAGES = verbose

    if verbose:
        print("RUFAS: Ruminant Farm Systems Model 2022")

    # Handle input file
    if not interactive:
        input_file_list = user_prompt.handle_input_file(path=inpath)
    else:
        input_file_list = user_prompt.input_prompt()



    # Run simulation
    for input_file_path in input_file_list:
        simulator = SimulationEngine(input_file_path)
        simulator.simulate()

    # compare simulation to observed outputs
    ## TODO --- neat comparison stuff ---


if __name__ == '__main__':

    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-graphics", help="prevent graphics from generating", action="store_true")
    parser.add_argument("-i", "--interactive", help="run in interactive mode", action="store_true")
    parser.add_argument("-v", "--verbose", help="print progress messages", action="store_true")
    parser.add_argument("-f", "--infile", dest="infile", metavar="path", help="specify the .json input file or directory",
                        type=str)
    pargs = parser.parse_args()

    # check for interactive usage
    isInteractive = len(argv) <= 1 or pargs.interactive
    makeGraphics = not pargs.no_graphics
    showMessages = not pargs.verbose

    # run validate function, passing appropriate arguments
    validate(inpath=pargs.infile, interactive=isInteractive, make_graphs=makeGraphics, verbose=showMessages)