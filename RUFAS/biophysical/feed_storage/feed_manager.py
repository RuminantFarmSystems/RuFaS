from collections import Counter
from datetime import date
from typing import Any, Literal

from RUFAS.biophysical.feed_storage.feed_storage_enum import StorageType
from RUFAS.data_structures.crop_soil_to_feed_storage_connection import (
    HarvestedCrop,
)
from RUFAS.data_structures.feed_storage_to_animal_connection import (
    Feed,
    FeedCategorization,
    FeedComponentType,
    RUFAS_ID,
    NASEMFeed,
    NRCFeed,
    NutrientStandard,
    PlanningCycleAllowance,
    RuntimePurchaseAllowance,
    RequestedFeed,
    TotalInventory,
    IdealFeeds,
)
from RUFAS.input_manager import InputManager
from RUFAS.rufas_time import RufasTime
from RUFAS.weather import Weather
from RUFAS.util import Utility
from RUFAS.units import MeasurementUnits
from RUFAS.output_manager import OutputManager

from .storage import Storage
from .purchased_feed_storage import PurchasedFeed, PurchasedFeedStorage


"""Ratio of the price of an on-farm price to the price of buying that feed from an off farm source."""
ON_FARM_TO_PURCHASED_PRICE_RATION = 0.01

"""A type alias representing the context in which a feed purchase was initiated."""
PurchaseType = Literal["daily_feed_request", "ration_interval", "planning_cycle"]


class FeedManager:
    """
    Manages the feed storage, handling crop reception, purchasing, degradation processing, feed distribution,
    feed purchase management and reporting, and querying available feeds.

    Parameters
    ----------
    feed_config : dict[str, list[Any]]
        Configuration for the feeds available in the simulation.
    nutrient_standard : NutrientStandard
        Nutrient standard used in the simulation (NASEM or NRC).
    crop_to_rufas_ids_mapping : dict[str, list[RUFAS_ID]]
        Mapping from crops to their corresponding RUFAS IDs.
    feed_storage_configs : dict[str, Any]
        Configurations for the feed storage units.
    feed_storage_instances : dict[str, list[str]]
        References to the specific feed storage units to be created.

    Attributes
    ----------
    _om : OutputManager
        Output manager for reporting feed-related data.
    _available_feeds : list[NASEMFeed | NRCFeed]
        List of feeds available for purchase and feeding in the simulation, including their nutritional properties
        and prices.
    active_storages : dict[StorageType, Storage]
        Contains the list of active farmgrown crop storage units in the simulation and their mapping from StorageType.
    purchased_feed_storage : PurchasedFeedStorage
        Storage for purchased feeds.
    planning_cycle_allowance : PlanningCycleAllowance
        Represents the allowances for feed purchases during a planning cycle.
    runtime_purchase_allowance : RuntimePurchaseAllowance
        Represents the allowances for feed purchases during runtime.
    crop_to_rufas_id : dict[str, RUFAS_ID]
        Maps crop configurations to their corresponding RUFAS IDs for harvested crops.
    _cumulative_feed_requests : dict[RUFAS_ID, float]
        Total amount of each feed requested over time (kg dry matter).
    _cumulative_purchased_feeds_fed : dict[RUFAS_ID, float]
        Total amount of purchased feeds fed to animals to date (kg dry matter).
    _cumulative_farmgrown_feeds_fed : dict[RUFAS_ID, float]
        Total amount of farmgrown feeds fed to animals to date (kg dry matter).
    _cumulative_purchased_feeds : dict[RUFAS_ID, float]
        Total amount of purchased feeds acquired to date (kg dry matter).

    """

    def __init__(
        self,
        feed_config: dict[str, list[Any]],
        nutrient_standard: NutrientStandard,
        feed_storage_configs: dict[str, Any],
        feed_storage_instances: dict[str, list[str]],
    ) -> None:
        self._om = OutputManager()
        self._available_feeds: list[Feed] = self._setup_available_feeds(feed_config, nutrient_standard)
        self.active_storages: dict[str, Storage] = {}

        self._create_all_storages(feed_storage_configs, feed_storage_instances)
        self.purchased_feed_storage: PurchasedFeedStorage = PurchasedFeedStorage(self._available_feeds)

        purchase_allowances: list[dict[str, int | float]] = feed_config["allowances"]
        self.planning_cycle_allowance: PlanningCycleAllowance = PlanningCycleAllowance(purchase_allowances)
        self.runtime_purchase_allowance: RuntimePurchaseAllowance = RuntimePurchaseAllowance(purchase_allowances)

        available_feed_ids = [feed.rufas_id for feed in self.available_feeds]
        self.crop_to_rufas_id: dict[str, RUFAS_ID] = {}
        for storage in self.active_storages.values():
            if storage.rufas_feed_id in available_feed_ids:
                self.crop_to_rufas_id[str(storage.crop_name)] = storage.rufas_feed_id

        self._cumulative_feed_requests: dict[RUFAS_ID, float] = {feed.rufas_id: 0.0 for feed in self.available_feeds}
        self._cumulative_purchased_feeds_fed: dict[RUFAS_ID, float] = {
            feed.rufas_id: 0.0 for feed in self.available_feeds
        }
        self._cumulative_farmgrown_feeds_fed: dict[RUFAS_ID, float] = {
            feed.rufas_id: 0.0 for feed in self.available_feeds
        }
        self._cumulative_purchased_feeds: dict[RUFAS_ID, float] = {feed.rufas_id: 0.0 for feed in self.available_feeds}

    @property
    def available_feeds(self) -> list[Feed]:
        """Returns the list of available feeds."""
        return self._available_feeds

    def _create_all_storages(
        self, feed_storage_configs: dict[str, Any], feed_storage_instances: dict[str, list[str]]
    ) -> None:
        """Creates all feed storage instances based on the provided configurations.

        Parameters
        ----------
        feed_storage_configs : dict[str, Any]
            A dictionary that contains configurations for all available feed storage types.
        feed_storage_instances : dict[str, list[str]]
            A dictionary that contains feed storage instance names.
        """
        all_configs: list[dict[str, Any]] = [
            storage_config
            for storage_config_list in feed_storage_configs.values()
            for storage_config in storage_config_list
        ]
        storage_name_counts = Counter(storage_config.get("name") for storage_config in all_configs)
        duplicate_names = [name for name, count in storage_name_counts.items() if count > 1]
        if duplicate_names:
            raise ValueError(
                f"Duplicate storage config names found: {duplicate_names}. Each storage config must have a unique name."
            )

        configs_by_name: dict[str, dict[str, Any]] = {
            config["name"]: config for config in all_configs if "name" in config
        }

        instance_names: list[str] = [name for names in feed_storage_instances.values() for name in names]

        available_rufas_ids: list[int] = [feed.rufas_id for feed in self.available_feeds]
        for instance_name in instance_names:
            storage_config = configs_by_name[instance_name]
            storage_type_str = storage_config["storage_type"]
            storage_class = StorageType.get_storage_class(storage_type_str)
            storage = storage_class(storage_config)
            self.active_storages[instance_name] = storage
            if storage.rufas_feed_id not in available_rufas_ids:
                self._om.add_warning(
                    "Storage RuFaS ID Warning",
                    f"Storage '{storage.storage_name}' has a RuFaS ID '{storage.rufas_feed_id}' that is not mapped "
                    "to any feed listed in the available feeds. This storage will not be used for feeding.",
                    {
                        "class": self.__class__.__name__,
                        "function": self.receive_crop.__name__,
                    },
                )

    def report_feed_manager_balance(self, simulation_day: int) -> None:
        """Reports the balance of feed purchased, requested, and fed to date."""
        info_map = {
            "class": self.__class__.__name__,
            "function": self.report_feed_manager_balance.__name__,
            "simulation_day": simulation_day,
            "units": MeasurementUnits.KILOGRAMS,
        }
        for rufas_id, amount in self._cumulative_feed_requests.items():
            self._om.add_variable(f"feed_{rufas_id}_requested_to_date", amount, info_map)
        for rufas_id, amount in self._cumulative_purchased_feeds_fed.items():
            self._om.add_variable(f"purchased_feed_{rufas_id}_fed_to_date", amount, info_map)
        for rufas_id, amount in self._cumulative_farmgrown_feeds_fed.items():
            self._om.add_variable(f"farmgrown_feed_{rufas_id}_fed_to_date", amount, info_map)
        for rufas_id, amount in self._cumulative_purchased_feeds.items():
            self._om.add_variable(f"purchased_feed_{rufas_id}_purchased_to_date", amount, info_map)
        self.report_feed_storage_levels(simulation_day, "balance_storage_levels")

    def update_available_feed_amounts(self) -> None:
        """Updates the amounts feeds available based on what is currently stored."""
        rufas_ids_to_query = [feed.rufas_id for feed in self.available_feeds]
        available_feed_amounts = self._query_available_feed_totals(rufas_ids_to_query)
        for feed in self.available_feeds:
            feed.amount_available = available_feed_amounts[feed.rufas_id]

    def translate_crop_config_name_to_rufas_id(
        self, next_harvest_dates: dict[str, date | None]
    ) -> dict[RUFAS_ID, date]:
        """Remaps crop configs and their next harvest date to RuFaS feed IDs and their next harvest date."""
        next_harvest_dates_rufas_ids = {}
        for crop_config, harvest_date in next_harvest_dates.items():
            if harvest_date is None:
                continue
            if crop_config in self.crop_to_rufas_id:
                next_harvest_dates_rufas_ids[self.crop_to_rufas_id[crop_config]] = harvest_date
        return next_harvest_dates_rufas_ids

    def receive_crop(
        self,
        harvested_crop: HarvestedCrop,
        simulation_day: int,
    ) -> None:
        """
        Receives a harvested crop and assigns it to the proper storage unit.

        Parameters
        ----------
        harvested_crop : HarvestedCrop
            The harvested crop to be stored.
        simulation_day : int
            The current simulation day, used for tracking storage time.
        """
        crop_name = harvested_crop.config_name
        field_name = harvested_crop.field_name
        for storage in self.active_storages.values():
            if storage.crop_name == crop_name and storage.field_name == field_name:
                storage.receive_crop(harvested_crop, simulation_day)
                return
        else:
            info_map = {
                "class": self.__class__.__name__,
                "function": self.receive_crop.__name__,
                "simulation_day": simulation_day,
            }
            self._om.add_warning(
                "No matching storage for crop",
                f"No storage found for crop '{crop_name}' from field '{field_name}'. Crop will be exported",
                info_map,
            )

    def process_degradations(self, weather: Weather, time: RufasTime) -> None:
        """
        Processes the degradation of all stored feeds over time.
        """
        for _, storage in self.active_storages.items():
            storage.process_degradations(weather, time)

    def report_feed_storage_levels(self, simulation_day: int, reporting_suffix: str) -> None:
        """Reports the daily storage levels of farm grown and purchased feeds."""
        self.report_stored_farmgrown_feeds(simulation_day, reporting_suffix)
        self.purchased_feed_storage.report_stored_purchased_feeds(simulation_day, reporting_suffix)

    def report_stored_farmgrown_feeds(self, simulation_day: int, reporting_suffix: str) -> None:
        """Outputs total amounts of farmgrown feeds currently stored by the FeedManager."""
        feed_report: dict[RUFAS_ID, dict[str, float]] = {
            feed.rufas_id: {"dry_matter_mass": 0.0, "fresh_mass": 0.0} for feed in self._available_feeds
        }

        for storage in self.active_storages.values():
            for crop in storage.stored:
                rufas_id = storage.rufas_feed_id
                if rufas_id not in feed_report:
                    continue
                feed_report[rufas_id]["dry_matter_mass"] += crop.dry_matter_mass
                feed_report[rufas_id]["fresh_mass"] += crop.fresh_mass
        info_map = {
            "class": self.__class__.__name__,
            "function": self.report_stored_farmgrown_feeds.__name__,
            "simulation_day": simulation_day,
            "units": MeasurementUnits.DRY_KILOGRAMS,
            "suffix": reporting_suffix,
        }

        for rufas_id, mass in feed_report.items():
            self._om.add_variable(f"stored_feed_{rufas_id}_dm", mass["dry_matter_mass"], info_map)
            self._om.add_variable(f"stored_feed_{rufas_id}_wet", mass["fresh_mass"], info_map)

    def manage_daily_feed_request(self, requested_feed: RequestedFeed, time: RufasTime) -> bool:
        """Returns true if requested feeds can be provided, either through on-farm feeds or by purchasing."""
        current_feed_totals = self._query_available_feed_totals(list(requested_feed.requested_feed.keys()))
        feeds_to_remove_from_inventory = {id: 0.0 for id in requested_feed.requested_feed.keys()}
        feeds_to_purchase = {id: 0.0 for id in requested_feed.requested_feed.keys()}
        for feed_id, amount_requested in requested_feed.requested_feed.items():
            available_amount = current_feed_totals[feed_id]
            tolerance = 1e-6
            is_fulfillable_with_inventory = amount_requested <= available_amount
            is_fulfillable_with_purchase = (
                amount_requested - available_amount
            ) <= self.runtime_purchase_allowance.allowances[feed_id] + tolerance
            is_request_unfulfillable = not is_fulfillable_with_inventory and not is_fulfillable_with_purchase
            if is_request_unfulfillable:
                return False
            self._om.add_variable(
                f"{feed_id}_requested_amount",
                amount_requested,
                {
                    "class": self.__class__.__name__,
                    "function": self.manage_daily_feed_request.__name__,
                    "units": MeasurementUnits.DRY_KILOGRAMS,
                    "simulation_day": time.simulation_day,
                },
            )
            self._cumulative_feed_requests[feed_id] += amount_requested
            self._om.add_variable(
                f"{feed_id}_available_amount",
                available_amount,
                {
                    "class": self.__class__.__name__,
                    "function": self.manage_daily_feed_request.__name__,
                    "units": MeasurementUnits.DRY_KILOGRAMS,
                    "simulation_day": time.simulation_day,
                },
            )
            feeds_to_remove_from_inventory[feed_id] = amount_requested
            if not is_fulfillable_with_inventory:
                feeds_to_purchase[feed_id] = amount_requested - available_amount

        self.purchase_feed(feeds_to_purchase, time, purchase_type="daily_feed_request")
        self._deduct_feeds_from_inventory(feeds_to_remove_from_inventory, time.simulation_day)
        for storage in self.active_storages.values():
            storage.remove_empty_crops()
        self.purchased_feed_storage.remove_empty_crops()
        return True

    def get_total_projected_inventory(self, inventory_date: date, weather: Weather, time: RufasTime) -> TotalInventory:
        """
        Gets the inventory expected to be held in storage at the specified date.

        Parameters
        ----------
        inventory_date : date
            Date at which inventory of feeds should be estimated for.
        weather : Weather
            Weather instance containing all weather data for the simulation.
        time : RufasTime
            RufasTime instance containing the current time of the simulation.

        Returns
        -------
        TotalInventory
            Total inventory of feeds projected to be held at the current date.

        Raises
        ------
        ValueError
            If the requested inventory date has already passed in the simulation.

        """
        days_in_the_future = (inventory_date - time.current_date.date()).days
        if days_in_the_future == 0:
            projected_crops = None
        elif days_in_the_future > 0:
            projected_crops = {storage.rufas_feed_id: 0.0 for storage in self.active_storages.values()}
            for storage in self.active_storages.values():
                projected_crop_amounts = storage.project_degradations(storage.stored, weather, time)
                feed_id_for_storage = storage.rufas_feed_id
                for crop in projected_crop_amounts:
                    projected_crops[feed_id_for_storage] += crop.dry_matter_mass
        else:
            raise ValueError(f"Current date {time.current_date} is after requested inventory date {inventory_date}")

        available_feed_rufas_ids = [feed.rufas_id for feed in self._available_feeds]

        available_feed_totals = self._query_available_feed_totals(available_feed_rufas_ids, projected_crops)

        inventory: dict[RUFAS_ID, float] = {}
        for feed in self._available_feeds:
            inventory[feed.rufas_id] = available_feed_totals.get(feed.rufas_id, 0.0)

        return TotalInventory(available_feeds=inventory, inventory_date=inventory_date)

    def manage_planning_cycle_purchases(self, ideal_feeds: IdealFeeds, time: RufasTime) -> None:
        """
        Purchases as much of the ideal feeds as possible, while respecting the Planning Allowance, storage capacity,
        future harvests, budget, etc.
        """
        # TODO: respect things other than the Planning Allowance. Issue #2483.
        feeds_to_purchase = {
            rufas_id: min(
                ideal_feeds.ideal_feeds[rufas_id], self.planning_cycle_allowance.allowances.get(rufas_id, 0.0)
            )
            for rufas_id in ideal_feeds.ideal_feeds.keys()
        }
        self.purchase_feed(feeds_to_purchase, time, purchase_type="planning_cycle")

    def manage_ration_interval_purchases(self, requested_feeds: RequestedFeed, time: RufasTime) -> None:
        """Manages the purchasing of feeds at the beginning of a ration interval."""
        current_feed_totals = self._query_available_feed_totals(list(requested_feeds.requested_feed.keys()))
        feeds_to_purchase = {id: 0.0 for id in requested_feeds.requested_feed.keys()}
        for feed_id, amount_requested in requested_feeds.requested_feed.items():
            feed_info = next(
                (available_feed for available_feed in self.available_feeds if available_feed.rufas_id == feed_id), None
            )
            if feed_info is None:
                raise ValueError(f"Trying to purchase unavailable feed {feed_id} during ration interval purchases.")
            available_amount = current_feed_totals[feed_id]

            amount_to_purchase = max(amount_requested - available_amount, 0.0) * (1 + feed_info.buffer)
            feeds_to_purchase[feed_id] = amount_to_purchase

        self.purchase_feed(feeds_to_purchase, time, purchase_type="ration_interval")

    def _query_available_feed_totals(
        self, query_feed_ids: list[RUFAS_ID], stored_crops: dict[RUFAS_ID, float] | None = None
    ) -> dict[RUFAS_ID, float]:
        """
        Gets the current dry matter mass of each feed ID currently in storage.

        Parameters
        ----------
        query_feed_ids : list[RUFAS_ID]
            List of RuFaS Feed IDs to get amounts of feed stored for.
        stored_crops : dict[RUFAS_ID, float] | None, default None
            Stored crops to tally feed amounts from. If None, tallies feed amounts from all feeds currently stored.

        Returns
        -------
        dict[RUFAS_ID, float]
            Map of RuFaS Feed IDs to the amounts of each in storage (kg dry matter).

        """
        feed_totals = {rufas_id: 0.0 for rufas_id in query_feed_ids}

        if stored_crops is None:
            for storage in self.active_storages.values():
                if storage.rufas_feed_id in feed_totals:
                    feed_totals[storage.rufas_feed_id] += sum(crop.dry_matter_mass for crop in storage.stored)
        else:
            for rufas_id in feed_totals.keys() & stored_crops.keys():
                feed_totals[rufas_id] += stored_crops[rufas_id]

        for purchased_feed in self.purchased_feed_storage.stored:
            if purchased_feed.rufas_id in feed_totals:
                feed_totals[purchased_feed.rufas_id] += purchased_feed.dry_matter_mass

        return feed_totals

    def purchase_feed(
        self, feeds_to_purchase: dict[RUFAS_ID, float], time: RufasTime, purchase_type: PurchaseType
    ) -> None:
        """
        Records amounts and cost of feed purchased, and orchestrates storing them.

        Parameters
        ----------
        feeds_to_purchase : dict[RUFAS_ID, float]
            Mapping of RuFaS Feed IDs to the amounts of that feed to be purchased (kg dry matter).
        time : RufasTime
            RufasTime object.
        purchase_type : PurchaseType
            Type of purchase being made, used for output variable naming.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.purchase_feed.__name__,
            "units": MeasurementUnits.DOLLARS,
            "simulation_day": time.simulation_day,
        }
        for rufas_id, purchase_amount in feeds_to_purchase.items():
            feed_info = next(
                (available_feed for available_feed in self.available_feeds if available_feed.rufas_id == rufas_id), None
            )
            if feed_info is None:
                raise ValueError(f"Trying to purchase unavailable feed {rufas_id}")

            total_cost = purchase_amount * feed_info.purchase_cost

            info_map = info_map | {
                "price": feed_info.purchase_cost,
                "amount_purchased": purchase_amount,
                "total_cost": total_cost,
            }
            self._om.add_variable(
                f"{purchase_type}_{rufas_id}_cost",
                total_cost,
                info_map | {"units": MeasurementUnits.DOLLARS},
            )
            self._om.add_variable(
                f"{purchase_type}_{rufas_id}_amount_purchased",
                purchase_amount,
                info_map | {"units": MeasurementUnits.KILOGRAMS},
            )
            self._cumulative_purchased_feeds[rufas_id] += purchase_amount
            self._store_purchased_feed(rufas_id, purchase_amount, time)

    def _store_purchased_feed(self, rufas_id: RUFAS_ID, purchase_amount: float, time: RufasTime) -> None:
        """
        Stores feeds which have been purchased and adjusts for shrink.

        Parameters
        ----------
        rufas_id : RUFAS_ID
            RuFaS Feed ID of the feed that is to be stored (unitless).
        purchase_amount : float
            Amount of feed that was purchased (kg dry matter).
        time : RufasTime
            RufasTime object.

        """
        purchased_feed = PurchasedFeed(rufas_id, purchase_amount, time.current_date.date())
        self.purchased_feed_storage.receive_feed(purchased_feed)

    def _deduct_feeds_from_inventory(self, feeds_to_deduct: dict[RUFAS_ID, float], simulation_day: int) -> None:
        """
        Removes feeds from storage in a FIFO manner.

        Parameters
        ----------
        feeds_to_deduct : dict[RUFAS_ID, float]
            Mapping of RuFaS Feed IDs to the amounts of feed that will be removed from storage (kg dry matter).
        simulation_day : int
            The current simulation day, used for tracking feed removal.

        Raises
        ------
        ValueError
            If the amount of feed to deduct is greater than the amount in storage.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._deduct_feeds_from_inventory.__name__,
            "units": MeasurementUnits.DRY_KILOGRAMS,
            "simulation_day": simulation_day,
        }

        total_purchased_feed_deductions: dict[RUFAS_ID, float] = {feed.rufas_id: 0.0 for feed in self._available_feeds}
        total_farmgrown_feed_deductions: dict[RUFAS_ID, float] = {feed.rufas_id: 0.0 for feed in self._available_feeds}

        all_available_feeds: list[HarvestedCrop | PurchasedFeed] = self._gather_available_feeds()

        for rufas_id, amount in feeds_to_deduct.items():
            available_feeds = [feed for feed in all_available_feeds if self._check_feed_availability(rufas_id, feed)]

            for feed in available_feeds:
                amount_to_deduct = min(amount, feed.dry_matter_mass)
                amount -= amount_to_deduct

                if isinstance(feed, PurchasedFeed):
                    feed.remove_dry_matter_mass(amount_to_deduct)
                    total_purchased_feed_deductions[rufas_id] = (
                        total_purchased_feed_deductions.get(rufas_id, 0.0) + amount_to_deduct
                    )
                    self._cumulative_purchased_feeds_fed[rufas_id] += amount_to_deduct
                elif isinstance(feed, HarvestedCrop):
                    feed.remove_feed_mass(amount_to_deduct)
                    harvested_rufas_id = self._lookup_storage_rufas_id(feed.config_name)
                    total_farmgrown_feed_deductions[harvested_rufas_id] = (
                        total_farmgrown_feed_deductions.get(harvested_rufas_id, 0.0) + amount_to_deduct
                    )
                    self._cumulative_farmgrown_feeds_fed[harvested_rufas_id] += amount_to_deduct
                else:
                    raise TypeError(f"Unsupported feed type: {type(feed)}.")

                if amount < 0.001:
                    amount = 0
                    break

            if amount >= 0.001:
                raise ValueError(f"Was not able to deduct remaining {amount} of feed {rufas_id}.")

        for rufas_id, amount in total_purchased_feed_deductions.items():
            self._om.add_variable(
                f"purchased_feed_{rufas_id}_fed",
                amount,
                info_map,
            )
        for rufas_id, amount in total_farmgrown_feed_deductions.items():
            self._om.add_variable(
                f"farmgrown_feed_{rufas_id}_fed",
                amount,
                info_map,
            )

    def _lookup_storage_rufas_id(self, crop_name: str) -> RUFAS_ID:
        """
        Looks up and returns the RuFaS Feed ID associated with a given crop name in storage.

        Parameters
        ----------
        crop_name : str
            The name of the crop to look up.

        Returns
        -------
        RUFAS_ID
            The RuFaS Feed ID associated with the crop in its appropriate storage.

        Raises
        ------
        ValueError
            If no storage with the given crop name is found or there is no rufas ID for the crop in this storage.

        """
        for storage in self.active_storages.values():
            if storage.crop_name == crop_name:
                return storage.rufas_feed_id
        raise ValueError(f"No rufas id found for crop name '{crop_name}'.")

    def _gather_available_feeds(self) -> list[HarvestedCrop | PurchasedFeed]:
        """
        Gathers all available feeds from active storages and purchased feed storage.

        Returns
        -------
        list[HarvestedCrop | PurchasedFeed]
            A list of all available feeds. The list is sorted by HarvestedCrops (oldest -> newest)
            followed by PurchasedFeeds in their original order.
        """
        all_available_feeds: list[HarvestedCrop | PurchasedFeed] = []
        for storage in self.active_storages.values():
            if storage.rufas_feed_id in self.crop_to_rufas_id.values():
                all_available_feeds.extend(storage.stored)
        all_available_feeds = sorted(all_available_feeds, key=lambda feed: feed.storage_time)
        all_available_feeds.extend(self.purchased_feed_storage.stored)

        return all_available_feeds

    def _check_feed_availability(self, target_rufas_id: int, feed: HarvestedCrop | PurchasedFeed) -> bool:
        """
        Helper function that checks if a feed can be fed to animals based on the RuFaS ID and the feeds to deduct.

        Parameters
        ----------
        target_rufas_id : RUFAS_ID
            RuFaS Feed ID of the feed that is being checked (unitless).
        feed : HarvestedCrop | PurchasedFeed
            The feed object to check for availability.

        Returns
        -------
        bool
            True if the feed can be fed to animals, False otherwise.
        """
        if isinstance(feed, PurchasedFeed):
            return feed.rufas_id == target_rufas_id and float(feed.dry_matter_mass) > 1e-6
        name = getattr(feed, "config_name", None) or getattr(feed, "crop_name", None)

        if not name:
            return False

        rufas_id = self.crop_to_rufas_id.get(name)
        if rufas_id is None:
            rufas_id = self._lookup_storage_rufas_id(name)
            if rufas_id is None:
                return False

        return rufas_id == target_rufas_id and float(feed.dry_matter_mass) > 1e-6

    def _setup_available_feeds(
        self, feed_config: dict[str, list[Any]], nutrient_standard: NutrientStandard
    ) -> list[Feed]:
        """
        Creates list of feeds available for use in the simulation.

        Parameters
        ----------
        feed_config : list[dict[str, Any]]
            Mapping of the feeds available for purchase to the prices of those feeds.
        nutrient_standard : NutrientStandard
            Indicates whether the NASEM or NRC nutrient standards is being used.

        Returns
        -------
        list[Feed]
            Nutrition and price information of feeds available in the simulation.

        """
        feed_library = self._process_feed_library(nutrient_standard)

        feed_representation = NASEMFeed if nutrient_standard is NutrientStandard.NASEM else NRCFeed
        available_feeds: list[Feed] = []
        feeds_to_parse = feed_config["purchased_feeds"]
        for feed in feeds_to_parse:
            rufas_id = feed["purchased_feed"]
            price = feed["purchased_feed_cost"]
            buffer = feed["buffer"]
            try:
                nutritive_properties = feed_library[rufas_id]
            except KeyError:
                raise KeyError(f"Feed with RUFAS ID '{rufas_id}' not found in the feed library.")
            new_feed = feed_representation(
                rufas_id=rufas_id,
                amount_available=0.0,
                on_farm_cost=price * ON_FARM_TO_PURCHASED_PRICE_RATION,
                purchase_cost=price,
                buffer=buffer,
                **nutritive_properties,
            )
            available_feeds.append(new_feed)

        return available_feeds

    def _process_feed_library(self, nutrient_standard: NutrientStandard) -> dict[RUFAS_ID, dict[str, Any]]:
        """
        Collects and processes the feed library input so that it can be translated into a simulation-friendly format.

        Parameters
        ----------
        nutrient_standard : NutrientStandard
            Indicates whether the NASEM or NRC nutrient standards is being used.

        Returns
        -------
        dict[RUFAS_ID, dict[str, Any]]
            Mapping of RuFaS feed IDs to the nutritional properties of those feeds.

        """
        im = InputManager()
        feed_library = (
            im.get_data("NASEM_Comp") if nutrient_standard is NutrientStandard.NASEM else im.get_data("NRC_Comp")
        )

        feed_library = Utility.convert_dict_of_lists_to_list_of_dicts(feed_library)

        feed_library = {feed["rufas_id"]: feed for feed in feed_library}
        for feed in feed_library.values():
            del feed["rufas_id"]
            feed["feed_type"] = FeedComponentType(feed["feed_type"])
            feed["Fd_Category"] = FeedCategorization(feed["Fd_Category"])
            feed["units"] = MeasurementUnits(feed["units"])
        return feed_library
