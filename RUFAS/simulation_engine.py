################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: simulation_engine.py
Description: Contains the main routines that drive the simulation
Author(s): Kass Chupongstimun, kass_c@hotmail.com
           Jit Patil, spatil5@wisc.edu
"""
################################################################################

import json
import time as timer
from pathlib import Path

from RUFAS import routines, errors
from RUFAS.classes import Config, State, Weather, Time
from RUFAS.output import OutputHandler
from RUFAS.test import test_handler


# -------------------------------------------------------------------------------
# Function: simulate
# -------------------------------------------------------------------------------
def simulate(input_fPath: Path):
    """Executes the simulation with the json file specified.

    Executes the simulation with the json file at the path specified. Skips over
    the simulation (immediately returns) when an error is present in the json
    file. Prints out the error message to the console.
    The parameters of the simulation are all specified by the input file.

    Args:
        input_fPath (Path): Path to the json file that contains all the input
            parameters to the simulation. Passed to read_json_file().
    """

    #
    # Reads the json input file and uses the information to instantiate the
    # simulation global variables
    #
    try:
        read_json_file(input_fPath)
    except errors.InvalidJSONfile as e:
        print(e.msg)
        return

    #
    # Creates a new directory for the output files (if doesn't already exist)
    # Deletes existing output files of the same name from previous simulation
    # Transfer needed (initial) data from state to report handlers
    #
    output.initialize_output_dir(config.output_dir)
    output.initialize_diagnostic_dir(config.diagnostic_dir)
    output.initialize_reports(state)

    print("\nSimulating: {}".format(input_fPath.name))

    t_start_sim = timer.time()

    #
    # MAIN Simulation Loop
    #

    while not time.end_simulation():
        annual_simulation()

    output.produce_graphics()
    t_end_sim = timer.time()

    print("Simulation Successful: {}".format(input_fPath.name))
    print("Total Run Time: {} seconds\n".format(str(t_end_sim - t_start_sim)))


# -------------------------------------------------------------------------------
# Function: daily_simulation
# -------------------------------------------------------------------------------
def daily_simulation():
    """Executes the daily simulation routines."""

    #
    # Daily routines
    #
    routines.daily_animal_routine(state.animal_management, state.feed, weather, time)
    routines.daily_soil_routine(state.soil, state.crop, state.field_management, weather, time)
    routines.daily_crop_routine(state.crop, weather, time, state.soil)
    routines.daily_feed_routine(state.feed, state.crop)

    #
    # Daily Output Updates
    #
    output.daily_update(state, weather, time)

    # print("simulating: " + time.to_str()) # Print out current day of simulation
    time.advance()
    # have to increment simulation_day here so that the daily output has the correct simulation day
    state.animal_management.simulation_day += 1


# -------------------------------------------------------------------------------
# Function: annual_simulation
# -------------------------------------------------------------------------------
def annual_simulation():
    """Executes the annual simulation routines.

    Writes the annual report to the output files
    Flushes the data in the output object
    Resets the state for the following year
    """

    #
    # Pre-annual Routines
    #
    routines.annual_crop_routine(state.crop, time)
    routines.annual_feed_routine()

    while not time.end_year():
        daily_simulation()

    #
    # Post-Annual Routines
    #
    output.annual_updates(state, weather, time)
    output.write_annual_reports()
    output.annual_flushes()
    state.annual_reset()
    time.advance()


# -------------------------------------------------------------------------------
# Function: read_json_file
# -------------------------------------------------------------------------------
def read_json_file(fPath: Path):
    """Reads the json file, writes information to the simulation variables.

    Reads and inteprets the (json) file at the given path. Compiles the
    information into dictionaries and instantiates the simulation objects with
    them. Assigns the objects to the global simulation variables.

    Args:
        fPath (Path): Path to the input json file

    Raises:
        InvalidJSONfileError: If the json file at the given path does not
            conform with the format required
    """

    #
    # Designate as module-global variables
    #
    global config, state, output, weather, time

    with fPath.open('r') as f:
        data = json.load(f)

        # Instantiate objects using dictionary data from .json file
        try:
            config = Config(data['config'], data['weather'])

            if config.run_tests:
                test_handler.run_tests()

            weather = Weather(data['weather'], config.years, config.w_start_year,
                              config.w_start_day, config.start_year, config.start_day)
            time = Time(config.years, config.start_year)
            state = State(data['farm'], config, time)
            output = OutputHandler(data['output'], state)

        except errors.JSONfileData as e:
            print("JSON FILE ERROR: " +
                  "{} \n\t{} Section\n{}\n".format(fPath.name, e.section, e.msg))
            raise errors.InvalidJSONfile(fPath.name)


# =======================================================================================
