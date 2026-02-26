# !/usr/bin/env python3

import time as timer
from datetime import date, timedelta

from RUFAS.EEE.EEE_manager import EEEManager
from RUFAS.EEE.emissions import EmissionsEstimator
from RUFAS.biophysical.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.feed_storage.feed_manager import FeedManager
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.data_structures.crop_soil_to_feed_storage_connection import HarvestedCrop
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
    """

    def __init__(self) -> None:
        """
        Initializes the simulation engine.
        """
        self.om = OutputManager()
        self.im = InputManager()
        self.time = RufasTime()

        self._simulation_type_to_daily_simulation_function = {
            "full_farm": self._execute_full_farm_daily_simulation,
            "no_animals": self._execute_no_animals_daily_simulation,
        }

        self._initialize_simulation()

    def simulate(self, simulation_type: str) -> None:
        """
        Executes the simulation.

        Parameters
        ----------
        simulation_type : str
            The type of simulation to run. Determines which daily simulation function to execute.
        """

        info_map = {
            "class": self.__class__.__name__,
            "function": self.simulate.__name__,
        }
        t_start_sim = timer.time()

        self._run_simulation_main_loop(simulation_type)

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

    def _run_simulation_main_loop(self, simulation_type: str) -> None:
        """
        The main loop for simulation.

        Parameters
        ----------
        simulation_type : str
            The type of simulation to run. Determines which daily simulation function to execute.

        """
        for simulation_year in range(self.time.simulation_length_years):
            self._annual_simulation(simulation_type)

    def _execute_full_farm_daily_simulation(self) -> None:
        """
        Executes the daily simulation routines for a full farm with all sub-modules.

        Daily Full Farm Simulation Process:
        1. Field operations (manure applications, harvesting)
        2. Feed planning (recalculate feed availability, update purchase plans)
        3. Ration planning (periodic reformulation check, estimate future inventory, formulate ration,
        update purchase plans)
        4. Animal operations (distribute feed to herd)
        5. Manure operations (collect and manage manure)
        6. Record keeping (time, weather, purchased feeds fed emissions)
        7. Advance simulation date

        """
        daily_harvested_crops = self._execute_daily_field_operations()

        harvest_schedule = self._build_harvest_schedule(daily_harvested_crops)
        self._execute_feed_planning(harvest_schedule)

        self._execute_ration_planning()

        daily_manure_data, daily_purchased_feeds_fed = self._execute_daily_animal_operations()

        self._execute_daily_manure_operations(daily_manure_data)

        self._report_daily_records(daily_purchased_feeds_fed)

        self._advance_time()

    def _execute_no_animals_daily_simulation(self) -> None:
        """
        Executes the daily simulation routines for a farm with no animals.

        Daily No Animals Simulation Process:
        1. Field operations (manure applications, harvesting)
        2. Feed planning (recalculate feed availability, update purchase plans)
        3. Ration planning (periodic reformulation check, estimate future inventory, formulate ration,
        update purchase plans)
        4. Record keeping (time, weather, purchased feeds fed emissions)
        5. Advance simulation date

        """
        daily_harvested_crops = self._execute_daily_field_operations()

        harvest_schedule = self._build_harvest_schedule(daily_harvested_crops)
        self._execute_feed_planning(harvest_schedule)

        self._execute_ration_planning()

        self._report_daily_records(daily_purchased_feeds_fed={})

        self._advance_time()

    def _execute_daily_field_operations(self) -> list[HarvestedCrop]:
        """Handles daily field operations including manure applications and crop harvesting/receiving."""
        manure_applications: list[ManureEventNutrientRequestResults] = self.generate_daily_manure_applications()
        harvested_crops: list[HarvestedCrop] = self.field_manager.daily_update_routine(
            self.weather, self.time, manure_applications
        )

        for crop in harvested_crops:
            self.feed_manager.receive_crop(crop, self.time.simulation_day)

        return harvested_crops

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

    def _build_harvest_schedule(self, harvested_crops: list[HarvestedCrop]) -> dict[str, date | None]:
        """
        Builds a schedule of next harvest dates for all crop types.

        Parameters
        ----------
        harvested_crops : list[HarvestedCrop]
            A list of crops that were harvested on the current day.


        Returns
        -------
        dict[str, date | None]
            A dictionary mapping crops to their next harvest dates.
            If a crop does not have a scheduled next harvest, the value will be None.

        Notes
        -----
        - The method checks if it's time to recalculate feed planning, which is done at a user-specified interval.
        If it is time, it will include all crops that are relevant for feed planning in the harvest schedule,
        even if they were not harvested today.
        """
        harvest_schedule_crops = set(crop.config_name for crop in harvested_crops)

        if self._should_recalculate_feed_planning():
            crops_to_get_next_harvest_dates = [
                crop for crop in self.feed_manager.crop_to_rufas_id.keys() if crop not in harvest_schedule_crops
            ]
            harvest_schedule_crops = harvest_schedule_crops.union(crops_to_get_next_harvest_dates)
            self.next_max_daily_feed_recalculation = self.time.current_date + self.max_daily_feed_recalculation_interval

        harvest_schedule = self.field_manager.get_next_harvest_dates(list(harvest_schedule_crops))

        return harvest_schedule

    def _should_recalculate_feed_planning(self) -> bool:
        """Check if it's time to recalculate maximum daily feed allocations."""
        return self.next_max_daily_feed_recalculation == self.time.current_date

    def _execute_feed_planning(self, harvest_schedule: dict[str, date | None]) -> None:
        """
        Recalculates maximum daily feed allocations if it's time.

        Parameters
        ----------
        harvest_schedule : dict[str, date | None]
            A dictionary mapping crop config names to their next harvest dates, used to inform feed planning.
        """
        if harvest_schedule == {}:
            return

        total_projected_inventory = self.feed_manager.get_total_projected_inventory(
            self.time.current_date.date(), self.weather, self.time
        )
        next_harvest_dates_with_rufas_ids = self.feed_manager.translate_crop_config_name_to_rufas_id(harvest_schedule)

        ideal_feeds_to_purchase = self.herd_manager.update_all_max_daily_feeds(
            total_projected_inventory, next_harvest_dates_with_rufas_ids, self.time
        )
        self.feed_manager.manage_planning_cycle_purchases(ideal_feeds_to_purchase, self.time)

    def _execute_ration_planning(self) -> None:
        """Checks if it's time to reformulate the ration and executes ration formulation if needed."""
        if self._is_time_to_reformulate_ration():
            self._formulate_ration()

    def _is_time_to_reformulate_ration(self) -> bool:
        """Checks if it's time to reformulate the ration based on the user-defined interval."""
        return self.time.current_date.date() >= self.next_ration_reformulation

    def _execute_daily_animal_operations(self) -> tuple[dict[str, ManureStream], dict[str, float]]:
        """
        Executes the daily animal routines.

        Returns
        -------
        tuple[dict[str, ManureStream] | None, dict[str, float]]
            A tuple containing:
            - A dictionary mapping pens to their corresponding ManureStream objects generated
              from the daily routines. If animals are not being simulated, this will be None.
            - A dictionary mapping feed types to the amount of purchased feed fed to the herd.
        """
        requested_feed = self.herd_manager.collect_daily_feed_request()
        self.feed_manager.report_feed_storage_levels(self.time.simulation_day, "daily_storage_levels")
        self.feed_manager.report_cumulative_purchased_feeds(self.time.simulation_day)
        is_ok_to_feed_animals, daily_feeds_fed = self.feed_manager.manage_daily_feed_request(requested_feed, self.time)

        daily_purchased_feeds_fed = daily_feeds_fed.get("purchased", {})

        if not is_ok_to_feed_animals:
            info_map = {"class": self.__class__.__name__, "function": self._execute_daily_animal_operations.__name__}
            self.om.add_warning("Value: not enough feed for the herd", "Reformulating ration for all pens", info_map)
            self._formulate_ration()

        total_inventory = self.feed_manager.get_total_projected_inventory(
            self.time.current_date.date(), self.weather, self.time
        )

        all_manure_data = self.herd_manager.daily_routines(
            self.feed_manager.available_feeds, self.time, self.weather, total_inventory
        )

        return all_manure_data, daily_purchased_feeds_fed

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

    def _execute_daily_manure_operations(self, daily_manure_data: dict[str, ManureStream] | None) -> None:
        """
        Executes the daily manure operations routine.

        Parameters
        ----------
        daily_manure_data : dict[str, ManureStream] | None
            A list of dictionaries containing manure data for each pen in the herd.
            If animals are not being simulated, this will be None.
        """
        if daily_manure_data is not None:
            self.manure_manager.run_daily_update(
                daily_manure_data, self.time, self.weather.get_current_day_conditions(self.time)
            )

    def _report_daily_records(self, daily_purchased_feeds_fed: dict[str, float]) -> None:
        """
        Reports the daily records for the simulation to OutputManager.

        Parameters
        ----------
        daily_purchased_feeds_fed : dict[str, float]
            A dictionary mapping feed types to the amount of purchased feed fed to the herd on the current day.
        """
        self.emissions_estimator.calculate_purchased_feed_emissions(daily_purchased_feeds_fed)
        self.time.record_time()
        self.weather.record_weather(self.time)

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

    def _annual_simulation(self, simulation_type: str) -> None:
        """
        Executes the annual simulation routines.

        Parameters
        ----------
        simulation_type : str
            The type of simulation to run. Determines which daily simulation function to execute.
        """
        for _ in range(self.time.year_start_day, self.time.year_end_day + 1):
            self._simulation_type_to_daily_simulation_function[simulation_type]()

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

        self.simulate_animals = self.im.get_data("config.simulation_type") != "no_animals"
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
