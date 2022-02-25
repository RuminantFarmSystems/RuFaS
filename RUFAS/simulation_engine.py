# !/usr/bin/env python3

import sys
import time as timer
from pathlib import Path
from RUFAS import routines, errors, classes
from RUFAS.classes import Config, State, Weather, Time
from RUFAS.util import get_base_dir, read_json_file
from RUFAS.output_handler import OutputHandler
import random
import numpy
from typing import Dict, Any, Optional

global config, state, output, weather, time


class SimulationEngine:

    def __init__(self, input_file_path: Path) -> None:
        """
        Args:
            input_file_path (Path): Path to the json file that contains all the input
                parameters to the simulation. Passed to read_json_file().
        """
        self._initialize_simulation(input_file_path)

    def simulate(self) -> None:
        """Executes the simulation"""

        t_start_sim = timer.time()
        self._run_simulation_main_loop()
        output.finalize(state, weather, time)
        t_end_sim = timer.time()

        print("Simulation Successful")
        print(f"Total Simulation Time: {t_end_sim - t_start_sim} seconds")

        t_start_graphics = timer.time()
        sys.stdout.write('Producing Graphics ')
        output.produce_graphics()
        t_end_graphics = timer.time()

        graphics_prod_time = t_end_graphics - t_start_graphics
        total_runtime = (t_end_sim-t_start_sim) + \
            (t_end_graphics-t_start_graphics)
        self._show_final_messages(graphics_prod_time, total_runtime)

    def _run_simulation_main_loop(self) -> None:
        """
        The main loop for simulation
        """
        sys.stdout.write("Simulating  ")
        while not time.end_simulation():
            self._annual_simulation()

    def _show_final_messages(self, graphics_prod_time: float, total_runtime: float) -> None:
        """
        Shows the messages of the end of the simulation
        """
        sys.stdout.write(
            f"Output Successful. Graphics stored in: {config.graphic_dir}")
        sys.stdout.write(f"Time to produce graphics: {graphics_prod_time}.")
        sys.stdout.write(f"Total Run Time: {total_runtime} seconds")

    def _daily_simulation(self) -> None:
        """Executes the daily simulation routines."""

        routines.daily_animal_routine(
            state.animal_management, state.feed, weather, time)
        routines.daily_manure_storage_routine(
            state.manure_storage, state.animal_management)
        routines.daily_fields_routine(
            state.fields, state.manure_storage, weather, time)
        routines.daily_feed_routine(state.feed, state.fields, state.animal_management,
                                    output.reports['feed_storage_report'])

        output.daily_update(state, weather, time)
        self._advance_time()

    def _advance_time(self, print_day: Optional[bool] = False) -> None:
        """
        Advances time and increments simulation_day
        """
        if print_day:
            print("simulating: " + time.to_str())
        time.advance()
        state.animal_management.simulation_day += 1

    def _annual_simulation(self) -> None:
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

            self._daily_simulation()

        # Post-Annual Routines
        state.annual_mass_balance(time)
        output.annual_updates(state, weather, time)
        output.write_annual_reports()
        output.annual_flushes()
        state.annual_reset()
        time.advance()

    def _initialize_simulation(self, file_path: Path) -> None:
        """Reads the json file, writes information to the simulation variables.

        Reads and interprets the (json) file at the given path. Compiles the
        information into dictionaries and instantiates the simulation objects with
        them. Assigns the objects to the global simulation variables.

        Args:
            file_path (Path): Path to the input json file
            data (Dict[str, Any]): initial simulation data

        Raises:
            InvalidJSONFileError: If the json file at the given path does not
                conform with the format required
        """

        global config, state, output, weather, time

        print(f"Initializing simulation environemnt from {file_path}")
        try:
            data = read_json_file(file_path)
            config = Config(data['config'], data['weather'])

            if config.set_seed:
                random.seed(config.seed)
                numpy.random.seed(config.seed)

            weather = Weather(data['weather'], config)
            time = Time(config)
            state = State(data['farm'], config, weather, time)
            output = OutputHandler(classes.read_json_file(
                get_base_dir() / 'input/output' / data['output']), state)

        except errors.JSONfileData as e:
            print(
                f"JSON FILE ERROR: {file_path.name}\n\t{e.section} Section\n{e.msg}\n")
            raise errors.InvalidJSONfile(file_path.name)

        output.initialize_dir(config.csv_dir, config.graphic_dir)
        output.initialize_reports()
