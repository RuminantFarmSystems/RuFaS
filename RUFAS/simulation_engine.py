# !/usr/bin/env python3

import random
import sys
import time as timer
from enum import Enum
from typing import Optional, Dict, Any

import numpy

from RUFAS import routines
from RUFAS.weather import Weather
from RUFAS.time import Time
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.routines.manure.manure_manager import simulate_daily_manure_manager, ManureManager
from RUFAS.routines.feed.feed import Feed
from RUFAS.routines.animal.animal_manager import AnimalManager
from RUFAS.routines.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.routines.feed_storage.feed_manager import FeedManager
from RUFAS.routines.field.manager.field_manager import FieldManager

om = OutputManager()
im = InputManager()


class SimulationEngine:
    """
    The SimulationEngine class is responsible for orchestrating the entire simulation
    process for RuFaS. It manages the simulation's lifecycle, advancing time, executing daily
    and annual routines, and logging simulation progress.

    Attributes
    ----------
    weather : Weather
        The weather object that contains the weather data.
    time : Time
        The time object that contains methods for accessing and manipulating the simulation time.
    feed: Feed
        The Feed object that stores the information for the feeds managed by the farm, and the methods for storage.
    animal_manager: AnimalManager
        The AnimalManager object that manages all animal routines.
    manure_manager: ManureManager
        The ManureManager object that sets up and manages different manure management components including manure
        handlers, reception pits, manure separators, and manure storage treatments.
    field_manager: FieldManager
        The FieldManager object that manages all fields in the simulation.

    Methods
    -------
    simulate()
        Execute the simulation process.
    """

    def __init__(self) -> None:
        """
        Initializes the simulation engine.
        """
        self.day_counter: int = 0
        self._initialize_simulation()

    def simulate(self) -> None:
        """
        Executes the simulation.
        """

        info_map = {
            "class": self.__class__.__name__,
            "function": self.simulate.__name__,
        }
        t_start_sim = timer.time()
        self._run_simulation_main_loop()
        AnimalModuleReporter.report_end_of_simulation(self.animal_manager, self.day_counter)
        om.add_variable(
            "available_feeds_on_final_day",
            [
                {k: v.value if isinstance(v, Enum) else v for k, v in feed.items()}
                for feed in self.feed_manager.query_available_feeds()
            ],
            info_map,
        )
        t_end_sim = timer.time()

        sys.stdout.write("\nSimulation Completed.\n\n")
        total_simulation_time = t_end_sim - t_start_sim
        total_simulation_time_log = f"Total simulation time is: {total_simulation_time}"
        om.add_log("total_simulation_time", total_simulation_time_log, info_map)
        om.add_variable(
            "day_counter_final_value",
            self.day_counter,
            {
                "class": self.__class__.__name__,
                "function": self.simulate.__name__,
            },
        )

        error_count, warning_count = om.get_error_and_warning_counts()
        sys.stdout.write(f"{error_count} error(s) and {warning_count} warning(s) found.\n")

    def _run_simulation_main_loop(self) -> None:
        """
        The main loop for simulation.
        """

        while not self.time.end_simulation():
            self._annual_simulation()

    def _daily_simulation(self) -> None:
        """Executes the daily simulation routines."""
        self.day_counter += 1
        self.animal_manager.daily_updates(self.feed, self.weather, self.time)
        simulate_daily_manure_manager(self.manure_manager, self.animal_manager)
        self.field_manager.daily_update_routine(self.weather, self.time)
        routines.daily_feed_routine(self.feed, self.field_manager, self.animal_manager)

        self.time.record_time()
        self.weather.record_weather(self.time)

        self._advance_time()

    def _advance_time(self, print_day: Optional[bool] = False) -> None:
        """
        Advances time and increments simulation_day.
        """

        info_map = {
            "class": self.__class__.__name__,
            "function": self._advance_time.__name__,
            "print_day": print_day,
        }
        if print_day:
            simulating_day_log = f"simulating day: {self.time.to_str()}"
            om.add_log("simulation_day", simulating_day_log, info_map)
        self.time.advance()
        self.animal_manager.simulation_day += 1

    def _run_pre_annual_routines(self) -> None:
        """TODO GitHub issue #137"""
        routines.annual_feed_routine(self.feed)

    def _run_post_annual_routines(self) -> None:
        """
        Writes the annual report to the output files
        Flushes the data in the output object
        Resets the state for the following year
        """

        self.annual_mass_balance(self.time)
        self.annual_reset()
        self.time.advance()

    @staticmethod
    def _visualize_sim_progress(day: int, update_interval: int = 50) -> None:
        """
        Shows a rotating char on console to confirm simulation is alive.

        Parameters
        ----------
        day : int
            day of year
        update_interval : int, optional, default=50
            the interval at which the char symbol is updated. Default is 50 days.
        """

        chars = ["-", "\\", "|", "/"]
        if day % update_interval == 0:
            sys.stdout.write("\b")
            sys.stdout.write(chars[(day // update_interval) % len(chars)])

    def _annual_simulation(self) -> None:
        """
        Executes the annual simulation routines.
        """

        self._run_pre_annual_routines()
        while not self.time.end_year():
            self._visualize_sim_progress(self.time.day)
            self._daily_simulation()

        self._run_post_annual_routines()

    def annual_reset(self) -> None:
        """
        Resets all annual variables that require reset.
        """
        self.field_manager.annual_update_routine()

    def annual_mass_balance(self, time) -> None:
        pass

    def _initialize_simulation(self) -> None:
        """
        Instantiates the simulation object by requesting data from the Input Manager.
        """

        config_data: Dict[str, Any] = im.get_data("config")
        weather_data = im.get_data("weather")

        if config_data.get("set_seed"):
            random.seed(config_data["random_seed"])
            numpy.random.seed(config_data["random_seed"])

        self.time = Time()
        self.weather = Weather(weather_data, self.time)
        self.feed_manager = FeedManager()

        feed_class_config = im.get_data("feed")
        self.feed = Feed(feed_class_config)

        manure_class_config = im.get_data("manure_management")
        animal_class_config = im.get_data("animal")
        animal_class_config["manure_management_scenarios"] = manure_class_config["manure_management_scenarios"]

        self.animal_manager = AnimalManager(animal_class_config, self.feed, self.weather, self.time)
        self.manure_manager = ManureManager(self.animal_manager, self.weather, self.time, manure_class_config)

        self.field_manager = FieldManager(manure_manager=self.manure_manager, feed_manager=self.feed_manager)
