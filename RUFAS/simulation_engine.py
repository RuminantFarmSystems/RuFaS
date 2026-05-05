# !/usr/bin/env python3

from enum import Enum
import time as timer
from datetime import date, timedelta

from RUFAS.EEE.EEE_manager import EEEManager
from RUFAS.EEE.emissions import EmissionsEstimator
from RUFAS.biophysical.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.biophysical.animal.digestive_system.manure_excretion_calculator import ManureExcretionCalculator
from RUFAS.biophysical.animal.herd_manager import HerdManager
from RUFAS.biophysical.feed_storage.feed_manager import FeedManager
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.data_structures.crop_soil_to_feed_storage_connection import HarvestedCrop
from RUFAS.data_structures.feed_storage_to_animal_connection import (
    RUFAS_ID,
    AvailableFeedsBuilder,
    FeedFulfillmentResults,
    IdealFeeds,
    NutrientStandard,
    RequestedFeed,
    TotalInventory,
)
from RUFAS.data_structures.manure_to_crop_soil_connection import FieldManureSupplier, ManureEventNutrientRequestResults
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.biophysical.field.manager.field_manager import FieldManager
from RUFAS.biophysical.manure.manure_manager import ManureManager
from RUFAS.rufas_time import RufasTime
from RUFAS.weather import Weather

DEFAULT_FEED_DEGRADATIONS_PROCESSING_INTERVAL = 30


class SimulationType(Enum):
    """
    An enumeration for the different types of simulations that can be run in RuFaS.

    Attributes
    ----------
    FULL_FARM : str
        Represents a full farm simulation with all sub-modules active.
    FIELD_AND_FEED : str
        Represents a simulation that includes only field and feed modules, no animal and manure modules.
    """

    FULL_FARM = "full_farm"
    FIELD_AND_FEED = "field_and_feed"

    @property
    def simulate_animals(self) -> bool:
        """Return whether this simulation type includes the animal module."""
        return self in self._animal_simulation_types()

    @property
    def simulate_manure(self) -> bool:
        """Return whether this simulation type includes the manure module."""
        return self in self._manure_simulation_types()

    @property
    def simulate_fields(self) -> bool:
        """Return whether this simulation type includes the crop, soil, and field module."""
        return self in self._fields_simulation_types()

    @property
    def simulate_feed(self) -> bool:
        """Return whether this simulation type includes the feed module."""
        return self in self._feed_simulation_types()

    @classmethod
    def _animal_simulation_types(cls) -> set["SimulationType"]:
        """Return the set of simulation types that simulate animals."""
        return {
            cls.FULL_FARM,
        }

    @classmethod
    def _manure_simulation_types(cls) -> set["SimulationType"]:
        """Return the set of simulation types that simulate manure processing."""
        return {
            cls.FULL_FARM,
        }

    @classmethod
    def _fields_simulation_types(cls) -> set["SimulationType"]:
        """Return the set of simulation types that simulate crops, soil, and fields."""
        return {cls.FULL_FARM, cls.FIELD_AND_FEED}

    @classmethod
    def _feed_simulation_types(cls) -> set["SimulationType"]:
        """Return the set of simulation types that simulate feed storage and management."""
        return {cls.FULL_FARM, cls.FIELD_AND_FEED}

    @classmethod
    def get_simulation_type(cls, simulation_type: str) -> "SimulationType":
        """
        Gets the simulation type.

        Parameters
        ----------
        simulation_type : str
            The type of simulation as a string.

        Raises
        ------
        ValueError
            If the simulation type is not recognized.
        """
        try:
            return cls(simulation_type)
        except ValueError as ve:
            valid_simulation_types = ", ".join([e.value for e in cls])
            raise ValueError(
                f"Unknown simulation type: {simulation_type}. Expected one of: {valid_simulation_types}."
            ) from ve


class SimulationEngine:
    """
    The SimulationEngine class is responsible for orchestrating the entire simulation
    process for RuFaS. It manages the simulation's lifecycle, advancing time, executing daily
    and annual routines, and logging simulation progress.

    Attributes
    ----------
    om : OutputManager
        An instance of OutputManager.
    im : InputManager
        An instnace of InputManager.
    simulation_type : SimulationType
        The type of simulation that will be run.
    simulate_animals : bool
        Whether or not the simulation will have a HerdManager.
    simulate_fields : bool
        Whether or not the simulation will have a FieldManager.
    simulate_manure : bool
        Whether or not the simulation will have a ManureManager.
    simulate_feed : bool
        Whether or not the simulation will have a FeedManager.
    _simulation_type_to_daily_simulation_function : dict[SimulationType, Callable]
        A dictionary mapping the simulation type to the appropriate daily simulation function.
    time : RufasTime
        The RufasTime object that contains methods for accessing and manipulating the simulation time.
    weather : Weather
        The weather object that contains the weather data.
    emissions_estimator : EmissionsEstimator
        The engine used to estimate emissions associated with purchased feeds used for animals.
    field_manager: FieldManager
        The FieldManager object that manages all fields in the simulation.
    feed_manager: FeedManager
        The FeedManager object that stores the information for the feeds managed by the farm
        and the methods for storage.
    herd_manager: HerdManager
        The HerdManager object that manages all animal in the herd.
    manure_manager: ManureManager
        The ManureManager object that sets up and manages different manure management components including manure
        handlers, reception pits, manure separators, and manure storage treatments.
    available_feeds : list[Feed]
        The feeds set to be available for the simulation in the feed input.
    max_daily_feed_recalculation_interval : timedelta
        The interval on which `max_daily_feed_recalculation` should occur.
    next_max_daily_feed_recalculation : datetime
        The date on which the next max daily feed recalculation should occur.
    feed_degradations_interval_length : timedelta
        The interval on which feed degradations should occur.
    next_degredations_process : datetime
        The date on which the next feed degradations processing should occur.
    ration_formulation_interval_length : timedelta
        The interval on which ration reformulation should occur.
    next_ration_reformulation : datetime
        The date on which the next ration reformulation should occur.
    is_ration_defined_by_user : bool
        Whether or not the ration is user-defined.
    """

    def __init__(self, simulation_type: SimulationType) -> None:
        """
        Initializes the simulation engine.
        """
        self.om = OutputManager()
        self.im = InputManager()
        self.time = RufasTime()
        self.simulation_type = simulation_type
        self.simulate_animals = self.simulation_type.simulate_animals
        self.simulate_fields = self.simulation_type.simulate_fields
        self.simulate_manure = self.simulation_type.simulate_manure
        self.simulate_feed = self.simulation_type.simulate_feed
        self._simulation_type_to_daily_simulation_function = {
            SimulationType.FULL_FARM: self._execute_full_farm_daily_simulation,
            SimulationType.FIELD_AND_FEED: self._execute_field_and_feed_daily_simulation,
        }

        self._setup_simulation_modules()

    def _setup_simulation_modules(self) -> None:
        """
        Instantiates the requested biophysical modules based on simulation type.
        """
        weather_data = self.im.get_data("weather")
        self.om.time = self.time
        self.weather = Weather(weather_data, self.time)
        self.emissions_estimator: EmissionsEstimator = EmissionsEstimator()

        if self.simulate_fields:
            self.field_manager: FieldManager = FieldManager()

        if self.simulate_animals or self.simulate_feed:
            feeds_config = self.im.get_data("feed")
            nutrient_standard = NutrientStandard(self.im.get_data("config.nutrient_standard"))
            self.available_feeds = AvailableFeedsBuilder.setup_available_feeds(feeds_config, nutrient_standard)

        if self.simulate_feed:
            feed_storage_configs = self.im.get_data("feed_storage_configurations")
            feed_storage_instances = self.im.get_data("feed_storage_instances")
            self.feed_manager: FeedManager = FeedManager(
                feeds_config,
                self.available_feeds,
                feed_storage_configs,
                feed_storage_instances,
            )
            feed_manager_available_feed_ids = [feed.rufas_id for feed in self.available_feeds]
            self.emissions_estimator.check_available_purchased_feed_data(feed_manager_available_feed_ids)
            max_daily_feed_recalculations_per_year: int = feeds_config["ration_formulation_parameters"][
                "max_daily_feed_recalculations_per_year"
            ]
            self.max_daily_feed_recalculation_interval = timedelta(
                days=round(365 / max_daily_feed_recalculations_per_year)
            )
            self.next_max_daily_feed_recalculation = self.time.current_date + self.max_daily_feed_recalculation_interval
            self.feed_degradations_interval_length = timedelta(days=DEFAULT_FEED_DEGRADATIONS_PROCESSING_INTERVAL)
            self.next_degradations_processing = self.time.current_date.date()

        if self.simulate_animals:
            ration_config = self.im.get_data("animal.ration")
            ration_interval_length = ration_config["formulation_interval"]
            self.ration_formulation_interval_length = timedelta(days=ration_interval_length)
            self.next_ration_reformulation = self.time.current_date.date()
            self.is_ration_defined_by_user = ration_config["user_input"]

            self.herd_manager: HerdManager = HerdManager(
                self.weather,
                self.time,
                is_ration_defined_by_user=self.is_ration_defined_by_user,
                available_feeds=self.available_feeds,
                simulate_animals=self.simulate_animals,
            )

        if self.simulate_manure:
            self.manure_manager: ManureManager = ManureManager(
                self.weather.intercept_mean_temp, self.weather.phase_shift, self.weather.amplitude
            )

    def simulate(self) -> None:
        """Executes the simulation."""

        info_map = {
            "class": self.__class__.__name__,
            "function": self.simulate.__name__,
        }
        t_start_sim = timer.time()

        self._run_simulation_main_loop()

        if self.simulate_animals:
            AnimalModuleReporter.report_end_of_simulation(
                self.herd_manager.herd_statistics,
                self.herd_manager.herd_reproduction_statistics,
                self.time,
                self.herd_manager.heiferII_events_by_id,
                self.herd_manager.cow_events_by_id,
                self.herd_manager.animal_genetic_history_by_id,
            )

        if self.simulate_manure:
            ManureExcretionCalculator.emit_dmi_below_min_summary(info_map)

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

    def _execute_full_farm_daily_simulation(self) -> None:
        """
        Executes the daily simulation routines for a full farm with all sub-modules.

        Daily Full Farm Simulation Process:
        1. Field operations (manure applications, harvesting)
        2. Feed planning (recalculate feed availability, update purchase plans)
        3. Ration planning (periodic reformulation check, estimate future inventory, formulate ration,
        update purchase plans)
        4. Animal operations (feeding, growth, reproduction, and milk production routines)
        5. Manure operations (collect and process manure)
        6. Record keeping (time, weather, purchased feeds fed emissions)
        7. Advance simulation date

        """
        daily_harvested_crops = self._execute_daily_field_operations()

        self._receive_daily_harvested_crops(daily_harvested_crops)
        harvest_schedule = self._build_harvest_schedule(daily_harvested_crops)

        self._execute_feed_planning(harvest_schedule)

        self._execute_ration_planning()

        daily_manure_data, daily_purchased_feeds_fed = self._execute_daily_animal_operations()

        self._execute_daily_manure_operations(daily_manure_data)

        self._report_daily_records(daily_purchased_feeds_fed)

        self._advance_time()

    def _execute_field_and_feed_daily_simulation(self) -> None:
        """
        Executes the daily simulation routines for a farm with only the field and feed modules.

        Daily Field and Feed Simulation Process:
        1. Field operations (manure applications, harvesting)
        2. Feed planning (recalculate feed availability, update purchase plans)
        3. Ration planning (periodic reformulation check, estimate future inventory, formulate ration,
        update purchase plans)
        4. Record keeping (time, weather, purchased feeds fed emissions)
        5. Advance simulation date

        """
        daily_harvested_crops = self._execute_daily_field_operations()

        self._receive_daily_harvested_crops(daily_harvested_crops)
        harvest_schedule = self._build_harvest_schedule(daily_harvested_crops)

        self._execute_feed_planning(harvest_schedule)

        self._report_daily_records()

        self._advance_time()

    def _execute_daily_field_operations(self) -> list[HarvestedCrop]:
        """Handles daily field operations including manure applications and crop harvesting/receiving."""
        manure_applications: list[ManureEventNutrientRequestResults] = self._generate_daily_manure_applications()
        harvested_crops: list[HarvestedCrop] = self.field_manager.daily_update_routine(
            self.weather, self.time, manure_applications
        )

        return harvested_crops

    def _generate_daily_manure_applications(self) -> list[ManureEventNutrientRequestResults]:
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
                    if self.simulate_manure:
                        manure_request_results = self.manure_manager.request_nutrients(manure_request, self.time)
                    else:
                        manure_request_results = FieldManureSupplier.request_nutrients(manure_request)
                manure_applications.append(ManureEventNutrientRequestResults(field_name, event, manure_request_results))
        return manure_applications

    def _receive_daily_harvested_crops(self, harvested_crops: list[HarvestedCrop]) -> None:
        """Receives and stores the crops harvested."""
        for crop in harvested_crops:
            self.feed_manager.receive_crop(crop, self.time.simulation_day)

        if self._should_recalculate_feed_planning:
            harvest_schedule_crops = set(crop.config_name for crop in harvested_crops)
            crops_to_get_next_harvest_dates = [
                crop for crop in self.feed_manager.crop_to_rufas_id.keys() if crop not in harvest_schedule_crops
            ]
            harvest_schedule_crops = harvest_schedule_crops.union(crops_to_get_next_harvest_dates)
            self.next_max_daily_feed_recalculation = self.time.current_date + self.max_daily_feed_recalculation_interval

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
        harvest_schedule = self.field_manager.get_next_harvest_dates(list(harvest_schedule_crops))

        return harvest_schedule

    @property
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

        ideal_feeds_to_purchase = (
            IdealFeeds({})
            if not self.simulate_animals
            else self._update_all_max_daily_feeds(total_projected_inventory, next_harvest_dates_with_rufas_ids)
        )
        self.feed_manager.manage_planning_cycle_purchases(ideal_feeds_to_purchase, self.time)
        self.feed_manager.report_feed_storage_levels(self.time.simulation_day, "daily_storage_levels")
        self.feed_manager.report_cumulative_purchased_feeds(self.time.simulation_day)

        if self._is_time_to_process_feed_degradations:
            self.next_degradations_processing = (self.time.current_date + self.feed_degradations_interval_length).date()
            self.feed_manager.process_degradations(self.weather, self.time)

    def _update_all_max_daily_feeds(
        self,
        total_projected_inventory: TotalInventory,
        next_harvest_dates_with_rufas_ids: dict[RUFAS_ID, date],
    ) -> IdealFeeds:
        """Wrapper function for HerdManager daily max feeds update."""
        return self.herd_manager.update_all_max_daily_feeds(
            total_projected_inventory, next_harvest_dates_with_rufas_ids, self.time
        )

    @property
    def _is_time_to_process_feed_degradations(self) -> bool:
        """Checks if it's time to process feed degradations"""
        return self.time.current_date.date() >= self.next_degradations_processing

    def _execute_ration_planning(self) -> None:
        """Checks if it's time to reformulate the ration and executes ration formulation if needed."""
        if self._is_time_to_reformulate_ration:
            self.next_ration_reformulation = (self.time.current_date + self.ration_formulation_interval_length).date()
            self._formulate_ration()

    @property
    def _is_time_to_reformulate_ration(self) -> bool:
        """Checks if it's time to reformulate the ration based on the user-defined interval."""
        return self.time.current_date.date() >= self.next_ration_reformulation

    def _formulate_ration(self) -> None:
        """Formulates the ration for the animals."""
        current_temperature = self.weather.get_current_day_conditions(time=self.time).mean_air_temperature
        requested_feed = self.herd_manager.formulate_rations(
            self.available_feeds,
            current_temperature,
            self.ration_formulation_interval_length.days,
            self.time.simulation_day,
        )
        if self.simulate_feed:
            self.feed_manager.manage_ration_interval_purchases(requested_feed, self.time)
            self.feed_manager.report_feed_manager_balance(self.time.simulation_day)

        self.herd_manager.report_ration_interval_data(self.time.simulation_day)

    def _execute_daily_animal_operations(self) -> tuple[dict[str, ManureStream], dict[int, float]]:
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
        requested_feed: RequestedFeed = self.herd_manager.collect_daily_feed_request()
        if self.simulate_feed:
            is_ok_to_feed_animals, daily_feeds_fed = self.feed_manager.manage_daily_feed_request(
                requested_feed,
                self.time,
            )
        else:
            is_ok_to_feed_animals = True
            daily_feeds_fed = FeedFulfillmentResults.fulfill_feed_request_as_purchased(requested_feed)

        daily_purchased_feeds_fed = daily_feeds_fed.purchased

        if not is_ok_to_feed_animals:
            info_map = {"class": self.__class__.__name__, "function": self._execute_daily_animal_operations.__name__}
            self.om.add_warning("Value: not enough feed for the herd", "Reformulating ration for all pens", info_map)
            self._formulate_ration()

        all_manure_data = self.herd_manager.execute_daily_routines(
            self.available_feeds,
            self.time,
            self.weather,
        )

        return all_manure_data, daily_purchased_feeds_fed

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

    def _report_daily_records(self, daily_purchased_feeds_fed: dict[int, float] | None = None) -> None:
        """
        Reports the daily records for the simulation to OutputManager.

        Parameters
        ----------
        daily_purchased_feeds_fed : dict[int, float] | None
            A dictionary mapping feed types to the amount of purchased feed fed to the herd on the current day.
            If no purchased feed was fed, this will be None.
        """
        if daily_purchased_feeds_fed:
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

    def _annual_simulation(self) -> None:
        """
        Executes the annual simulation routines.
        """
        for _ in range(self.time.year_start_day, self.time.year_end_day + 1):
            self._simulation_type_to_daily_simulation_function[self.simulation_type]()

        self._run_post_annual_routines()

    def annual_reset(self) -> None:
        """
        Resets all annual variables that require reset.
        """
        self.field_manager.annual_update_routine()

    def annual_mass_balance(self, time: RufasTime) -> None:
        pass
