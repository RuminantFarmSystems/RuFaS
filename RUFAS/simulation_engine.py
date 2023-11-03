# !/usr/bin/env python3

import random
import sys
import time as timer
from typing import Optional

import numpy

from RUFAS import routines
from RUFAS.config import Config
from RUFAS.state import State
from RUFAS.weather import Weather
from RUFAS.time import Time
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.routines.manure.manure_manager import simulate_daily_manure_manager

om = OutputManager()
im = InputManager()


class SimulationEngine:

    def __init__(self) -> None:
        self._initialize_simulation()

    def simulate(self) -> None:
        """
        Executes the simulation.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self.simulate.__name__, }
        t_start_sim = timer.time()

        self._run_simulation_main_loop()
        t_end_sim = timer.time()

        sys.stdout.write("\nSimulation Successful\n\n")
        total_simulation_time = t_end_sim - t_start_sim
        total_simulation_time_log = f"Total simulation time is: {total_simulation_time}"
        om.add_log("total_simulation_time",
                   total_simulation_time_log, info_map)

    def _run_simulation_main_loop(self) -> None:
        """
        The main loop for simulation.
        """
        while not self.time.end_simulation():
            self._annual_simulation()

    def _daily_simulation(self) -> None:
        """Executes the daily simulation routines."""
        routines.daily_animal_routine(
            self.state.animal_manager, self.state.feed, self.weather, self.time)
        simulate_daily_manure_manager(
            self.state.manure_manager, self.state.animal_manager)
        self.state.field_manager.daily_update_routine(self.weather, self.time)
        routines.daily_feed_routine(self.state.feed, self.state.field_manager, self.state.animal_manager)

        self.time.record_time()
        self.weather.record_weather(self.time)

        self._advance_time()

    def _advance_time(self, print_day: Optional[bool] = False) -> None:
        """
        Advances time and increments simulation_day.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self._advance_time.__name__,
                    "print_day": print_day, }
        if print_day:
            simulating_day_log = f"simulating day: {self.time.to_str()}"
            om.add_log("simulation_day",
                       simulating_day_log,
                       info_map)
        self.time.advance()
        self.state.animal_manager.simulation_day += 1

    def _run_pre_annual_routines(self) -> None:
        """TODO GitHub issue #137"""
        routines.annual_feed_routine(self.state.feed)

    def _run_post_annual_routines(self) -> None:
        """
        Writes the annual report to the output files
        Flushes the data in the output object
        Resets the state for the following year"""
        self.state.annual_mass_balance(self.time)
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
        """
        Executes the annual simulation routines.
        """
        self._run_pre_annual_routines()
        while not self.time.end_year():
            self._visualize_sim_progress(self.time.day)
            self._daily_simulation()

        self._run_post_annual_routines()

    def _initialize_simulation(self) -> None:
        """
        Instantiates the simulation object by requesting data from the Input Manager.
        """
        data_config = im.get_data('config')
        data_weather = im.get_data('weather')
        self.config = Config(data_config)

        if self.config.set_seed:
            random.seed(self.config.seed)
            numpy.random.seed(self.config.seed)

        self.weather = Weather(data_weather, self.config)
        self.time = Time(self.config)
        self.state = State(self.config, self.weather, self.time)
