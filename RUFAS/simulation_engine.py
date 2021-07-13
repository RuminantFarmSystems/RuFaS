"""
RUFAS: Ruminant Farm Systems Model
File name: simulation_engine.py

Description: Contains the main routines that drive the simulation

Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Jit Patil, spatil5@wisc.edu
"""

import sys
import time as timer
from pathlib import Path
from RUFAS import routines, errors, classes
from RUFAS.classes import Config, State, Weather, Time
from RUFAS.util import get_base_dir, read_json_file
from RUFAS.output_handler import OutputHandler
from RUFAS.test import test_handler
import random
import numpy

global config, state, output, weather, time


def simulate(input_file_path: Path):
    """Executes the simulation with the json file specified.

    Executes the simulation with the json file at the path specified. Skips over
    the simulation (immediately returns) when an error is present in the json
    file. Prints out the error message to the console.
    The parameters of the simulation are all specified by the input file.

    Args:
        input_file_path (Path): Path to the json file that contains all the input
            parameters to the simulation. Passed to read_json_file().
    """

    # Reads the json input file and uses the information to instantiate the
    # simulation global variables
    initialize_simulation(input_file_path, read_json_file(input_file_path))

    # Creates a new directory for the output files (if doesn't already exist)
    # Deletes existing output files of the same name from previous simulation
    # Transfer needed (initial) data from state to report handlers
    output.initialize_dir(config.csv_dir, config.graphic_dir)
    output.initialize_reports()

    t_start_sim = timer.time()

    sys.stdout.write("Simulating  ")
    # MAIN Simulation Loop
    while not time.end_simulation():
        annual_simulation()

    output.finalize(state, weather, time)
    t_end_sim = timer.time()
    print("\nSimulation Successful: {}".format(input_file_path.name))
    print("Total Simulation Time: {} seconds\n".format(str(t_end_sim - t_start_sim)))

    t_start_graphics = timer.time()
    sys.stdout.write('\nProducing Graphics ')
    output.produce_graphics()
    t_end_graphics = timer.time()
    sys.stdout.write("\nOutput Successful. Graphics stored in: {}".format(config.graphic_dir))
    sys.stdout.write(
        "\nTime to produce graphics: {}. Total Run Time: {} seconds".format(str(t_end_graphics - t_start_graphics),
                                                                            str((t_end_sim - t_start_sim) +
                                                                                (t_end_graphics - t_start_graphics))))


def daily_simulation():
    """Executes the daily simulation routines."""

    # Daily routines
    routines.daily_animal_routine(state.animal_management, state.feed, weather, time)
    routines.daily_manure_storage_routine(state.manure_storage, state.animal_management)
    routines.daily_fields_routine(state.fields, state.manure_storage, weather, time)
    routines.daily_feed_routine(state.feed, state.fields, state.animal_management,
                                output.reports['feed_storage_report'])

    #
    # Daily Output Updates
    #
    output.daily_update(state, weather, time)

    # print("simulating: " + time.to_str()) # Print out current day of simulation
    time.advance()
    # have to increment simulation_day here so that the daily output has the correct simulation day
    state.animal_management.simulation_day += 1


def annual_simulation():
    """Executes the annual simulation routines.

    Writes the annual report to the output files
    Flushes the data in the output object
    Resets the state for the following year
    """

    # Pre-annual routines
    routines.annual_fields_routine(state.fields, time)
    routines.annual_feed_routine(state.feed)

    case = 0
    while not time.end_year():
        if time.day % 50 == 0:
            sys.stdout.write("\b")
            if case == 0:
                sys.stdout.write("—")
                case += 1
            elif case == 1:
                sys.stdout.write("\\")
                case += 1
            elif case == 2:
                sys.stdout.write("|")
                case += 1
            else:
                sys.stdout.write("/")
                case = 0

        daily_simulation()

    # Post-Annual Routines
    state.annual_mass_balance(time)
    output.annual_updates(state, weather, time)
    output.write_annual_reports()
    output.annual_flushes()
    state.annual_reset()
    time.advance()


def initialize_simulation(file_path: Path, data):
    """Reads the json file, writes information to the simulation variables.

    Reads and interprets the (json) file at the given path. Compiles the
    information into dictionaries and instantiates the simulation objects with
    them. Assigns the objects to the global simulation variables.

    Args:
        file_path (Path): Path to the input json file
        data: initial simulation data

    Raises:
        InvalidJSONFileError: If the json file at the given path does not
            conform with the format required
    """

    # Designate as module-global variables
    global config, state, output, weather, time

    # Instantiate objects using dictionary data from .json file
    try:
        config = Config(data['config'], data['weather'])

        if config.set_seed:
            random.seed(config.seed)
            numpy.random.seed(config.seed)

        if config.run_tests:
            test_handler.run_tests()

        weather = Weather(data['weather'], config)
        time = Time(config)
        state = State(data['farm'], config, weather, time)
        output = OutputHandler(classes.read_json_file(get_base_dir() / 'input/output' / data['output']), state)

    except errors.JSONfileData as e:
        print("JSON FILE ERROR: " +
              "{} \n\t{} Section\n{}\n".format(file_path.name, e.section, e.msg))
        raise errors.InvalidJSONfile(file_path.name)
