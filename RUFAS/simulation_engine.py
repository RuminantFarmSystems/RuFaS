# !/usr/bin/env python3

import time as timer
from datetime import date, timedelta

from RUFAS.EEE.EEE_manager import EEEManager
from RUFAS.EEE.emissions import EmissionsEstimator
from RUFAS.biophysical.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.feed_storage.feed_manager import FeedManager
from RUFAS.data_structures.feed_storage_to_animal_connection import NutrientStandard
from RUFAS.data_structures.manure_to_crop_soil_connection import ManureEventNutrientRequestResults
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.biophysical.field.manager.field_manager import FieldManager
from RUFAS.biophysical.manure.manure_manager import ManureManager
from RUFAS.rufas_time import RufasTime
from RUFAS.weather import Weather


class SimulationEngine:
    """
    The SimulationEngine class is responsible for orchestrating the entire simulation
    process for RuFaS. It manages the simulation's lifecycle, advancing time, executing daily
    and annual routines, and logging simulation progress.

    Attributes
    ----------
    weather : Weather
        The weather object that contains the weather data.
    time : RufasTime
        The RufasTime object that contains methods for accessing and manipulating the simulation time.
    feed: Feed
        The Feed object that stores the information for the feeds managed by the farm, and the methods for storage.
    herd_manager: HerdManager
        The HerdManager object that manages all animal in the herd.
    manure_manager: ManureManager
        The ManureManager object that sets up and manages different manure management components including manure
        handlers, reception pits, manure separators, and manure storage treatments.
    field_manager: FieldManager
        The FieldManager object that manages all fields in the simulation.
    simulate_animals: bool
        A boolean indicating whether user has chosen to simulate animals in config.

    Methods
    -------
    simulate()
        Execute the simulation process.
    """

    def __init__(self) -> None:
        """
        Initializes the simulation engine.
        """
        self.om = OutputManager()
        self.im = InputManager()
        self.time = RufasTime()

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
            self.herd_manager.herd_statistics,
            self.herd_manager.herd_reproduction_statistics,
            self.time,
            self.herd_manager.heiferII_events_by_id,
            self.herd_manager.cow_events_by_id,
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
        manure_applications = self.generate_daily_manure_applications()
        harvested_crops = self.field_manager.daily_update_routine(self.weather, self.time, manure_applications)
        next_harvest_dates: dict[str, date | None] = {}
        for harvested_crop in harvested_crops:
            self.feed_manager.receive_crop(harvested_crop, self.time.simulation_day)
            if harvested_crop.config_name not in next_harvest_dates:
                crop_config_name = harvested_crop.config_name
                next_harvest_date = self.field_manager.get_next_harvest_dates([crop_config_name])
                next_harvest_dates[harvested_crop.config_name] = next_harvest_date.get(crop_config_name)

        is_time_to_recalculate_max_daily_feeds = self.next_max_daily_feed_recalculation == self.time.current_date
        if is_time_to_recalculate_max_daily_feeds:
            crops_to_get_next_harvest_dates = [
                crop for crop in self.feed_manager.crop_to_rufas_id.keys() if crop not in next_harvest_dates.keys()
            ]
            next_harvest_dates = self.field_manager.get_next_harvest_dates(crops_to_get_next_harvest_dates)
            self.next_max_daily_feed_recalculation: date = self.time.current_date
            +self.max_daily_feed_recalculation_interval

        if next_harvest_dates != {}:
            total_projected_inventory = self.feed_manager.get_total_projected_inventory(
                self.time.current_date.date(), self.weather, self.time
            )

            next_harvest_dates_with_rufas_ids = self.feed_manager.translate_crop_config_name_to_rufas_id(
                next_harvest_dates
            )
            ideal_feeds_to_purchase = self.herd_manager.update_all_max_daily_feeds(
                total_projected_inventory, next_harvest_dates_with_rufas_ids, self.time
            )
            self.feed_manager.manage_planning_cycle_purchases(ideal_feeds_to_purchase, self.time)

        is_time_to_reformulate_ration = self.time.current_date.date() == self.next_ration_reformulation
        if is_time_to_reformulate_ration:
            self._formulate_ration()

        requested_feed = self.herd_manager.collect_daily_feed_request()
        self.feed_manager.report_feed_storage_levels(self.time.simulation_day, "daily_storage_levels")
        self.feed_manager.report_cumulative_purchased_feeds(self.time.simulation_day)
        is_ok_to_feed_animals, daily_feeds_fed = self.feed_manager.manage_daily_feed_request(requested_feed, self.time)

        daily_purchased_feeds_fed = daily_feeds_fed.get("purchased", {})
        self.emissions_estimator.calculate_purchased_feed_emissions(daily_purchased_feeds_fed)

        if not is_ok_to_feed_animals:
            info_map = {"class": self.__class__.__name__, "function": self._daily_simulation.__name__}
            self.om.add_warning("Value: not enough feed for the herd", "Reformulating ration for all pens", info_map)
            self._formulate_ration()

        total_inventory = self.feed_manager.get_total_projected_inventory(
            self.time.current_date.date(), self.weather, self.time
        )

        if self.simulate_animals:

            all_manure_data = self.herd_manager.daily_routines(
                self.feed_manager.available_feeds, self.time, self.weather, total_inventory
            )

            self.manure_manager.run_daily_update(
                all_manure_data, self.time, self.weather.get_current_day_conditions(self.time)
            )

        self.time.record_time()
        self.weather.record_weather(self.time)

        self._advance_time()

    def _formulate_ration(self) -> None:
        """Formulates the ration for the animals."""
        self.feed_manager.process_degradations(self.weather, self.time)
        self.next_ration_reformulation = (self.time.current_date + self.ration_formulation_interval_length).date()
        total_projected_inventory = self.feed_manager.get_total_projected_inventory(
            self.next_ration_reformulation, self.weather, self.time
        )
        current_temperature = self.weather.get_current_day_conditions(time=self.time).mean_air_temperature
        requested_feed = self.herd_manager.formulate_rations(
            self.feed_manager.available_feeds,
            current_temperature,
            self.ration_formulation_interval_length.days,
            total_projected_inventory,
            self.time.simulation_day,
        )
        self.feed_manager.manage_ration_interval_purchases(requested_feed, self.time)

        self.herd_manager.report_ration_interval_data(self.time.simulation_day)

        self.feed_manager.report_feed_manager_balance(self.time.simulation_day)

    def generate_daily_manure_applications(self) -> list[ManureEventNutrientRequestResults]:
        """Requests nutrients from the manure manager for each field in the simulation.

        Returns
        -------
        list[ManureEventNutrientRequestResults]
            A list containing the ManureEvents and corresponding NutrientRequestResults to be applied to fields.
        """
        manure_applications: list[ManureEventNutrientRequestResults] = []
        for field in self.field_manager.fields:
            manure_events_requests = self.field_manager.check_manure_schedules(field, self.time)
            for manure_event_request in manure_events_requests:
                field_name = manure_event_request.field_name
                event = manure_event_request.event
                manure_request = manure_event_request.nutrient_request
                manure_request_results = None
                if manure_request is not None:
                    simulate_animals: bool = self.simulate_animals
                    manure_request_results = self.manure_manager.request_nutrients(
                        manure_request, simulate_animals, self.time
                    )
                manure_applications.append(ManureEventNutrientRequestResults(field_name, event, manure_request_results))
        return manure_applications

    def _advance_time(self) -> None:
        """
        Advances time and increments simulation_day.
        """

        self.time.advance()

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
        for _ in range(self.time.year_start_day, self.time.year_end_day + 1):
            self._daily_simulation()

        self._run_post_annual_routines()

    def annual_reset(self) -> None:
        """
        Resets all annual variables that require reset.
        """
        self.field_manager.annual_update_routine()

    def annual_mass_balance(self, time: RufasTime) -> None:
        pass

    def _initialize_simulation(self) -> None:
        """
        Instantiates the simulation object by requesting data from the Input Manager.
        """
        weather_data = self.im.get_data("weather")
        self.om.time = self.time
        self.weather = Weather(weather_data, self.time)

        self.field_manager: FieldManager = FieldManager()

        nutrient_standard = NutrientStandard(self.im.get_data("config.nutrient_standard"))
        feeds_config = self.im.get_data("feed")
        feed_storage_configs = self.im.get_data("feed_storage_configurations")
        feed_storage_instances = self.im.get_data("feed_storage_instances")
        self.feed_manager: FeedManager = FeedManager(
            feeds_config,
            nutrient_standard,
            feed_storage_configs,
            feed_storage_instances,
        )

        self.simulate_animals = self.im.get_data("config.simulate_animals")
        ration_interval_length = self.im.get_data("animal.ration.formulation_interval")
        self.ration_formulation_interval_length = timedelta(days=ration_interval_length)
        self.next_ration_reformulation = self.time.current_date.date()
        self.is_ration_defined_by_user = self.im.get_data("animal.ration.user_input")
        max_daily_feed_recalculations_per_year: int = self.im.get_data("feed.max_daily_feed_recalculations_per_year")
        self.max_daily_feed_recalculation_interval = timedelta(days=round(365 / max_daily_feed_recalculations_per_year))
        self.next_max_daily_feed_recalculation = self.time.current_date + self.max_daily_feed_recalculation_interval

        self.herd_manager: HerdManager = HerdManager(
            self.weather,
            self.time,
            is_ration_defined_by_user=self.is_ration_defined_by_user,
            available_feeds=self.feed_manager.available_feeds,
        )

        self.manure_manager: ManureManager = ManureManager(
            self.weather.intercept_mean_temp, self.weather.phase_shift, self.weather.amplitude
        )

        self.emissions_estimator: EmissionsEstimator = EmissionsEstimator()
        feed_manager_available_feed_ids = [feed.rufas_id for feed in self.feed_manager.available_feeds]
        self.emissions_estimator.check_available_purchased_feed_data(feed_manager_available_feed_ids)
