# !/usr/bin/env python3

import time as timer
from enum import Enum

from RUFAS import routines
from RUFAS.data_structures.crop_soil_to_manure_connection import ManureEventNutrientRequestResults
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.animal_manager import AnimalManager
from RUFAS.routines.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.routines.feed.feed import Feed
from RUFAS.routines.feed_storage.feed_manager import FeedManager
from RUFAS.routines.field.manager.field_manager import FieldManager
from RUFAS.routines.manure.manure_manager import ManureManager
from RUFAS.time import Time
from RUFAS.units import MeasurementUnits
from RUFAS.weather import Weather

from .routines.EEE.EEE_manager import EEEManager

"""
Defines the number of days between degradations of stored homegrown feeds when running end-to-end testing.
TODO: remove this constant after Animal and Feed Storage modules are connected - #1878
"""
FEED_DEGRADATION_INTERVAL_LENGTH = 15


class SimulationEngine:
    """
    The SimulationEngine class is responsible for orchestrating the entire simulation
    process for RuFaS. It manages the simulation's lifecycle, advancing time, executing daily
    and annual routines, and logging simulation progress.

    Parameters
    ----------
    is_end_to_end_test_run : bool
        TODO: remove this attribute after Animal and Feed Storage modules are connected - #1878
        Indicates if a simulation is being run for end-to-end testing.

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
    is_end_to_end_test_run : bool
        TODO: remove this attribute after Animal and Feed Storage modules are connected - #1878
        Indicates if a simulation is being run for end-to-end testing. Set to True if end-to-end testing inputs are
        found in the Input Manager.

    Methods
    -------
    simulate()
        Execute the simulation process.
    """

    def __init__(self, is_end_to_end_test_run: bool) -> None:
        """
        Initializes the simulation engine.
        """
        self.om = OutputManager()
        self.im = InputManager()
        self.time = Time()

        # TODO: remove this attribute after Animal and Feed Storage modules are connected - #1878
        self.is_end_to_end_test_run = is_end_to_end_test_run

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
        AnimalModuleReporter.report_end_of_simulation(
            self.animal_manager.life_cycle_manager, self.time, self.animal_manager.heiferIIs, self.animal_manager.cows
        )
        available_feeds_on_final_day = [
            {k: v.value if isinstance(v, Enum) else v for k, v in feed.items()}
            for feed in self.feed_manager.query_available_feeds()
        ]
        available_feeds_units = {
            "category": MeasurementUnits.UNITLESS,
            "type": MeasurementUnits.UNITLESS,
            "amount": MeasurementUnits.KILOGRAMS,
        }
        for available_feed in available_feeds_on_final_day:
            self.om.add_variable(
                "available_feeds_on_final_day",
                available_feed,
                dict(info_map, **{"units": available_feeds_units}),
            )
        EEEManager.estimate_all()
        t_end_sim = timer.time()

        self.om.add_log("Simulation complete", "Simulation Completed.", info_map)
        total_simulation_time = t_end_sim - t_start_sim
        total_simulation_time_log = f"Total simulation time is: {total_simulation_time}"
        self.om.add_log("total_simulation_time", total_simulation_time_log, info_map)

    def _run_simulation_main_loop(self) -> None:
        """
        The main loop for simulation.
        """
        for simulation_year in range(self.time.simulation_length_years):
            self._annual_simulation()

    def _daily_simulation(self) -> None:
        """Executes the daily simulation routines."""

        # TODO: remove this code after Animal and Feed Storage modules are connected - #1878
        if self.is_end_to_end_test_run:
            process_degradations_today = self.time.current_julian_day % FEED_DEGRADATION_INTERVAL_LENGTH == 0
            if process_degradations_today:
                self.feed_manager.process_degradations(self.weather, self.time)

        self.animal_manager.daily_updates(self.feed, self.weather, self.time)
        all_pen_manure_data = self.animal_manager.collect_pen_manure_data()
        self.manure_manager.daily_update(all_pen_manure_data, self.animal_manager.simulation_day)
        manure_applications = self.generate_daily_manure_applications()
        harvested_crops = self.field_manager.daily_update_routine(self.weather, self.time)
        for harvested_crop in harvested_crops:
            self.feed_manager.receive_crop(harvested_crop.harvested_crop, harvested_crop.storage_type)
        routines.daily_feed_routine(self.feed, self.field_manager, self.animal_manager)

        self.time.record_time()
        self.weather.record_weather(self.time)

        self._advance_time()

    def generate_daily_manure_applications(self) -> dict[str, list[ManureEventNutrientRequestResults]]:
        """Requests nutrients from the manure manager for each field in the simulation.

        Returns
        -------
        dict[str, list[ManureEventNutrientRequestResults]]
            A dictionary containing the ManureEvents and corresponding NutrientRequestResults for each field in
            the simulation.
        """
        manure_applications: dict[str, list[ManureEventNutrientRequestResults]] = {}
        for field in self.field_manager.fields:
            manure_events_requests = self.field_manager.check_manure_schedules(field, self.time)
            manure_applications[field.field_data.name] = []
            for manure_event_request in manure_events_requests:
                event = manure_event_request.event
                manure_request = manure_event_request.nutrient_request
                manure_request_results = None
                if manure_request is not None:
                    manure_request_results = self.manure_manager.request_nutrients(manure_request)
                manure_applications[field.field_data.name].append(
                    ManureEventNutrientRequestResults(event, manure_request_results))
        return manure_applications

    def _advance_time(self) -> None:
        """
        Advances time and increments simulation_day.
        """

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

    def _annual_simulation(self) -> None:
        """
        Executes the annual simulation routines.
        """
        self._run_pre_annual_routines()
        for _ in range(self.time.year_start_day, self.time.year_end_day + 1):
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

        weather_data = self.im.get_data("weather")
        self.om.time = self.time
        self.weather = Weather(weather_data, self.time)
        self.feed_manager = FeedManager()

        feed_class_config = self.im.get_data("feed")
        self.feed = Feed(feed_class_config)

        manure_class_config = self.im.get_data("manure_management")
        animal_class_config = self.im.get_data("animal")
        animal_class_config["manure_management_scenarios"] = manure_class_config["manure_management_scenarios"]

        self.animal_manager = AnimalManager(animal_class_config, self.feed, self.weather, self.time)
        all_pen_manure_data = self.animal_manager.collect_pen_manure_data()
        simulate_animals: bool = self.im.get_data("config.simulate_animals")
        self.manure_manager = ManureManager(
            all_pen_manure_data, self.weather, self.time, manure_class_config, simulate_animals
        )

        self.field_manager = FieldManager()

        # TODO: remove the below code after Animal and Feed Storage modules are connected - #1878
        if self.is_end_to_end_test_run:
            end_to_end_testing_inputs = self.im.get_data("end_to_end_testing_inputs")
            self.feed_manager.setup_stored_feeds(end_to_end_testing_inputs, self.time)
