# !/usr/bin/env python3

import sys
import time as timer
from pathlib import Path
from RUFAS import routines, errors
from RUFAS.classes import Config, State, Weather, Time
from RUFAS.output_handler import OutputHandler
from RUFAS.output_manager import OutputManager
import random
import numpy
from typing import Optional

from RUFAS.routines.manure.manure_management import simulate_daily_manure_management
from RUFAS.util import Utility


om = OutputManager()

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
        info_map = {'caller_class': self.__class__.__name__, 
                    'caller_function': self.simulate.__name__,}
        t_start_sim = timer.time()
        
        self._run_simulation_main_loop()
        self.output.finalize(self.state, self.weather, self.time)
        t_end_sim = timer.time()

        print("Simulation Successful")
        print(f"Total Simulation Time: {t_end_sim - t_start_sim} seconds")
        total_simulation_time = t_end_sim - t_start_sim
        om.add_variable('total_simulation_time', total_simulation_time, info_map)


        t_start_graphics = timer.time()
        sys.stdout.write('Producing Graphics\n')
        self.output.produce_graphics()
        t_end_graphics = timer.time()

        graphics_prod_time = t_end_graphics - t_start_graphics
        om.add_variable('graphics_prod_time', graphics_prod_time, info_map)
        total_runtime = (t_end_sim-t_start_sim) + \
            (t_end_graphics-t_start_graphics)
        om.add_variable('total_runtime', total_runtime, info_map)
        self._show_final_messages(graphics_prod_time, total_runtime)
        
        #TODO delete this method call prior to merging
        om.print_pools()

    def _run_simulation_main_loop(self) -> None:
        """
        The main loop for simulation
        """
        sys.stdout.write("Simulating  ")
        while not self.time.end_simulation():
            self._annual_simulation()

    def _show_final_messages(self, graphics_prod_time: float, total_runtime: float) -> None:
        """
        Shows the messages of the end of the simulation
        """
        sys.stdout.write(
            f"Output Successful.\nGraphics stored in: {self.config.graphic_dir}\n")
        sys.stdout.write(f"Time to produce graphics: {graphics_prod_time}\n")
        sys.stdout.write(f"Total Run Time: {total_runtime} seconds\n")

    def _daily_simulation(self) -> None:
        """Executes the daily simulation routines."""

        routines.daily_animal_routine(
            self.state.animal_management, self.state.feed, self.weather, self.time)
        routines.daily_manure_storage_routine(
            self.state.manure_storage, self.state.animal_management)
        simulate_daily_manure_management(
            self.state.manure_management, self.state.animal_management)
        routines.daily_fields_routine(
            self.state.fields, self.state.manure_storage, self.weather, self.time)
        routines.daily_feed_routine(self.state.feed, self.state.fields, self.state.animal_management,
                                    self.output.reports['feed_storage_report'])

        self.output.daily_update(self.state, self.weather, self.time)
        self._advance_time()

    def _advance_time(self, print_day: Optional[bool] = False) -> None:
        """
        Advances time and increments simulation_day
        """
        if print_day:
            print(f"simulating day: {self.time.to_str()}")
        self.time.advance()
        self.state.animal_management.simulation_day += 1

    def _run_pre_annual_routines(self) -> None:
        """TODO GitHub issue #137"""
        routines.annual_fields_routine(self.state.fields, self.time)
        routines.annual_feed_routine(self.state.feed)

    def _run_post_annual_routines(self) -> None:
        """
        Writes the annual report to the output files
        Flushes the data in the output object
        Resets the state for the following year"""
        self.state.annual_mass_balance(self.time)
        self.output.annual_updates(self.state, self.weather, self.time)
        self.output.write_annual_reports()
        self.output.annual_flushes()
        self.state.annual_reset()
        self.time.advance()

    def _visualize_sim_progress(self, day: int, update_interval: int = 50) -> None:
        """
        Shows a rotating char on console to confirm simulation is alive.

        Args:
            day (int): day of year
            update_interval (int): the interval at which the char symbol is updated
        """
        chars = ['-', '\\', '|', '/']
        if day % update_interval == 0:
            sys.stdout.write("\b")
            sys.stdout.write(chars[(day//update_interval) % len(chars)])

    def _annual_simulation(self) -> None:
        """Executes the annual simulation routines."""

        self._run_pre_annual_routines()
        while not self.time.end_year():
            self._visualize_sim_progress(self.time.day)
            self._daily_simulation()

        self._run_post_annual_routines()

    def _initialize_simulation(self, file_path: Path) -> None:
        """Reads the json file, writes information to the simulation variables.

        Reads and interprets the (json) file at the given path. Compiles the
        information into dictionaries and instantiates the simulation objects with
        them. Assigns the objects to the global simulation variables.

        Args:
            file_path (Path): Path to the input json file

        Raises:
            InvalidJSONFile: If the json file at the given path does not conform 
            with the format required
        """
        info_map = {'caller_class': self.__class__.__name__, 
                    'caller_function': self._initialize_simulation.__name__,
                    'file_path': file_path,}
        print(f"Initializing simulation environment from {file_path}")
        om.add_variable('simulation_initialization_file_path', file_path, info_map)

        try:
            data = Utility.read_json_file(file_path)
            self.config = Config(data['config'], data['weather'])

            if self.config.set_seed:
                random.seed(self.config.seed)
                numpy.random.seed(self.config.seed)

            self.weather = Weather(data['weather'], self.config)
            self.time = Time(self.config)
            self.state = State(data['farm'], self.config,
                               self.weather, self.time)
            self.output = OutputHandler(Utility.read_json_file(
                Utility.get_base_dir() / 'input/output' / data['output']), self.state)

        except errors.JSONfileData as e:
            print(
                f"JSON FILE ERROR: {file_path.name}\n\t{e.section} Section\n{e.msg}\n")
            raise errors.InvalidJSONfile(file_path.name)

        self.output.initialize_dir(
            self.config.csv_dir, self.config.graphic_dir)
        self.output.initialize_reports()
