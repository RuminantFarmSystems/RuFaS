from datetime import date
from typing import Dict, List, Any

from RUFAS.data_structures.crop_soil_to_feed_storage_connection import (
    CropCategory,
    HarvestedCrop,
    StorageType,
)
from RUFAS.data_structures.feed_storage_to_animal_connection import (
    FeedCategorization,
    FeedComponentType,
    Feed,
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

from .baleage import Baleage
from .grain import Dry, Grain, HighMoisture
from .hay import Hay, ProtectedIndoors, ProtectedTarped, ProtectedWrapped, Unprotected
from .silage import Bag, Bunker, Pile, Silage
from .storage import Storage
from .purchased_feed_storage import PurchasedFeed, PurchasedFeedStorage


# Defines the compatibility between Crop Categories and Storage Types.
CROP_TO_STORAGE_MAPPING: dict[CropCategory, list[type[Storage]]] = {
    CropCategory.ALFALFA: [Hay, Silage, Baleage],
    CropCategory.CORN: [Grain, Silage],
    CropCategory.GRASS: [Hay, Silage, Baleage],
    CropCategory.SMALL_GRAIN: [Hay, Grain, Silage, Baleage],
    CropCategory.SOY: [Grain],
}


"""Maps each StorageType enum element to the associated Storage subclass."""
STORAGE_TYPE_TO_CLASS_MAP: dict[StorageType, type[Storage]] = {
    StorageType.PROTECTED_INDOORS: ProtectedIndoors,
    StorageType.PROTECTED_WRAPPED: ProtectedWrapped,
    StorageType.PROTECTED_TARPED: ProtectedTarped,
    StorageType.UNPROTECTED: Unprotected,
    StorageType.BALEAGE: Baleage,
    StorageType.DRY: Dry,
    StorageType.HIGH_MOISTURE: HighMoisture,
    StorageType.BUNKER: Bunker,
    StorageType.PILE: Pile,
    StorageType.BAG: Bag,
}


"""Ratio of the price of an on-farm price to the price of buying that feed from an off farm source."""
ON_FARM_TO_PURCHASED_PRICE_RATION = 0.01


QUERY_RESULT_DATA_TYPE = Dict[str, CropCategory | float]


class FeedManager:
    """
    Manages the feed storage, handling crop reception, purchasing, degradation processing, feed distribution,
    and querying available feeds.

    Attributes
    ----------
    Dict[StorageType, Storage]
        Containts the list of active storage units in the simulation and their mapping from StorageType(Enum).
    """

    def __init__(
        self,
        feed_config: dict[str, list[Any]],
        nutrient_standard: NutrientStandard,
        crop_to_rufas_ids_mapping: dict[str, list[RUFAS_ID]],
    ) -> None:
        self.active_storages: dict[StorageType, Storage] = {}
        self._available_feeds: list[Feed] = self._setup_available_feeds(feed_config, nutrient_standard)
        self.purchased_feed_storage: PurchasedFeedStorage = PurchasedFeedStorage()
        purchase_allowances: list[dict[str, int | float]] = feed_config["allowances"]
        self.planning_cycle_allowance: PlanningCycleAllowance = PlanningCycleAllowance(purchase_allowances)
        self.runtime_purchase_allowance: RuntimePurchaseAllowance = RuntimePurchaseAllowance(purchase_allowances)
        self._om = OutputManager()

        available_feed_ids = [feed.rufas_id for feed in self.available_feeds]
        self.crop_to_rufas_id: dict[str, RUFAS_ID] = {}
        for crop, rufas_ids in crop_to_rufas_ids_mapping.items():
            rufas_id = self._select_rufas_id_for_harvested_crop(rufas_ids, available_feed_ids)
            if rufas_id is None:
                continue
            self.crop_to_rufas_id[crop] = rufas_id

    @property
    def available_feeds(self) -> list[Feed]:
        """Returns the list of available feeds."""
        return self._available_feeds

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

    def _query_result_factory(self, crop_category: CropCategory, amount: float) -> QUERY_RESULT_DATA_TYPE:
        return {
            "category": crop_category,
            "amount": amount,
        }

    def receive_crop(
        self,
        harvested_crop: HarvestedCrop,
        storage_type: StorageType,
        simulation_day: int,
    ) -> None:
        """
        Receives a harvested crop and assigns it to a storage unit.

        Parameters
        ----------
        harvested_crop : HarvestedCrop
            The harvested crop to be stored.
        storage_type : StorageType
            The type of storage to use for this crop.
        simulation_day : int
            The current simulation day, used for tracking storage time.

        Raises
        ------
        ValueError
            If the crop type is not compatible with the storage type.
        """
        compatible_storage_classes = CROP_TO_STORAGE_MAPPING.get(harvested_crop.category, [])
        is_crop_compatible_with_storage = any(
            issubclass(STORAGE_TYPE_TO_CLASS_MAP[storage_type], storage_class)
            for storage_class in compatible_storage_classes
        )

        if not is_crop_compatible_with_storage:
            raise ValueError(
                f"Crop of category '{harvested_crop.category}' is not compatible with storage type '{storage_type}'. "
                f"Compatible storage types are: {', '.join([cls.__name__ for cls in compatible_storage_classes])}"
            )

        if storage_type not in self.active_storages:
            self.active_storages[storage_type] = STORAGE_TYPE_TO_CLASS_MAP[storage_type]()

        self.active_storages[storage_type].receive_crop(harvested_crop, simulation_day)

    def process_degradations(self, weather: Weather, time: RufasTime) -> None:
        """
        Processes the degradation of all stored feeds over time.
        """
        for _, storage in self.active_storages.items():
            storage.process_degradations(weather, time)

    def execute_daily_routine(self, time: RufasTime) -> None:
        """Executes daily routine of the Feed Manager."""
        self.report_stored_feeds(time)

    def report_stored_feeds(self, time: RufasTime) -> None:
        """Outputs total amounts of feeds currently stored by the FeedManager."""
        feed_report: dict[RUFAS_ID, float] = self.purchased_feed_storage.create_consolidated_feed_report()
        available_feed_ids = [feed.rufas_id for feed in self.available_feeds]
        for storage in self.active_storages.values():
            for crop in storage.stored:
                rufas_id = self._select_rufas_id_for_harvested_crop(crop.rufas_ids, available_feed_ids)
                if rufas_id is None:
                    continue
                if rufas_id in feed_report.keys():
                    feed_report[rufas_id] += crop.dry_matter_mass
                else:
                    feed_report[rufas_id] = crop.dry_matter_mass
        info_map = {
            "class": self.__class__.__name__,
            "function": self.report_stored_feeds.__name__,
            "simulation_day": time.simulation_day,
            "units": MeasurementUnits.DRY_KILOGRAMS,
        }
        for rufas_id, mass in feed_report.items():
            self._om.add_variable(
                f"stored_feed_{rufas_id}", [mass, time.simulation_day], {**info_map, "rufas_id": rufas_id, "mass": mass}
            )

    def manage_daily_feed_request(self, requested_feed: RequestedFeed, time: RufasTime) -> bool:
        """Returns true if requested feeds can be provided, either through on-farm feeds or by purchasing."""
        current_feed_totals = self._query_available_feed_totals(list(requested_feed.requested_feed.keys()))
        feeds_to_remove_from_inventory = {id: 0.0 for id in requested_feed.requested_feed.keys()}
        feeds_to_purchase = {id: 0.0 for id in requested_feed.requested_feed.keys()}
        for feed_id, amount_requested in requested_feed.requested_feed.items():
            self._om.add_variable(
                f"{feed_id}_requested_amount",
                [amount_requested, time.simulation_day],
                {
                    "class": self.__class__.__name__,
                    "function": self.manage_daily_feed_request.__name__,
                    "units": MeasurementUnits.DRY_KILOGRAMS,
                    "simulation_day": time.simulation_day,
                },
            )
            available_amount = current_feed_totals[feed_id]
            self._om.add_variable(
                f"{feed_id}_available_amount",
                [available_amount, time.simulation_day],
                {
                    "class": self.__class__.__name__,
                    "function": self.manage_daily_feed_request.__name__,
                    "units": MeasurementUnits.DRY_KILOGRAMS,
                    "simulation_day": time.simulation_day,
                },
            )
            tolerance = 1e-6
            is_fulfillable_with_inventory = amount_requested <= available_amount
            is_fulfillable_with_purchase = (
                amount_requested - available_amount
            ) <= self.runtime_purchase_allowance.allowances[feed_id] + tolerance
            is_request_unfulfillable = not is_fulfillable_with_inventory and not is_fulfillable_with_purchase
            if is_request_unfulfillable:
                return False
            feeds_to_remove_from_inventory[feed_id] = amount_requested
            if not is_fulfillable_with_inventory:
                feeds_to_purchase[feed_id] = amount_requested - available_amount

        self.purchase_feed(feeds_to_purchase, time, purchase_type="daily_feed_request")
        self._deduct_feeds_from_inventory(feeds_to_remove_from_inventory, time.simulation_day)
        self.report_stored_feeds(time)
        for storage in self.active_storages.values():
            storage.remove_empty_crops()
        self.purchased_feed_storage.remove_empty_crops()
        return True

    def get_total_inventory(self, inventory_date: date, weather: Weather, time: RufasTime) -> TotalInventory:
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
            projected_crops = []
            for storage in self.active_storages.values():
                projected_crops.extend(storage.project_degradations(storage.stored, weather, time))
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
        # TODO: respect things other than the Planning Allowance
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
            available_amount = current_feed_totals[feed_id]

            amount_to_purchase = max(amount_requested - available_amount, 0.0)
            feeds_to_purchase[feed_id] = amount_to_purchase

        self.purchase_feed(feeds_to_purchase, time, purchase_type="ration_interval")

    def _query_available_feed_totals(
        self, query_feed_ids: list[RUFAS_ID], stored_crops: list[HarvestedCrop] | None = None
    ) -> dict[RUFAS_ID, float]:
        """
        Gets the current dry matter mass of each feed ID currently in storage.

        Parameters
        ----------
        query_feed_ids : list[RUFAS_ID]
            List of RuFaS Feed IDs to get amounts of feed stored for.
        stored_crops : list[HarvestedCrop] | None, default None
            Stored crops to tally feed amounts from. If None, tallies feed amounts from all feeds currently stored.

        Returns
        -------
        dict[RUFAS_ID, float]
            Map of RuFaS Feed IDs to the amounts of each in storage (kg dry matter).

        """
        feed_totals = {rufas_id: 0.0 for rufas_id in query_feed_ids}

        all_farmgrown_feeds_held: list[HarvestedCrop] = []
        if stored_crops is None:
            for storage in self.active_storages.values():
                all_farmgrown_feeds_held.extend(storage.stored)
        else:
            all_farmgrown_feeds_held = stored_crops

        for farmgrown_feed in all_farmgrown_feeds_held:
            feed_id = self._select_rufas_id_for_harvested_crop(farmgrown_feed.rufas_ids, list(feed_totals.keys()))
            if feed_id is None:
                continue
            feed_totals[feed_id] += farmgrown_feed.dry_matter_mass

        for purchased_feed in self.purchased_feed_storage.stored:
            if purchased_feed.rufas_id in feed_totals:
                feed_totals[purchased_feed.rufas_id] += purchased_feed.dry_matter_mass

        return feed_totals

    def query_available_feeds(
        self,
        query_crop_categories: List[CropCategory] | None = None,
        query_storage_types: List[StorageType] | None = None,
    ) -> List[QUERY_RESULT_DATA_TYPE]:
        """
        Queries the available amount of feed in storage.

        Parameters
        ----------
        query_crop_categories : List[CropCategory], optional, default=None
            The categories of crop to query (if None, all crop categories are queried).
        query_storage_types : List[StorageType], optional, default=None
            The types of storage to query (if None, all storages types are queried).

        Returns
        -------
        List[QUERY_RESULT_DATA_TYPE]
            The amount of available feed, either as a total or for a specific crop type.
        """
        query_all_crop_categories = query_crop_categories is None
        query_all_storage_types = query_storage_types is None
        results: List[QUERY_RESULT_DATA_TYPE] = []

        for storage_type, storage in self.active_storages.items():
            is_storage_queryable = query_all_storage_types or storage_type in query_storage_types
            if not is_storage_queryable:
                continue
            for stored_crop in storage.stored:
                is_crop_category_queryable = query_all_crop_categories or stored_crop.category in query_crop_categories
                if not (is_crop_category_queryable):
                    continue
                for previous_result in results:
                    if stored_crop.category == previous_result["category"]:
                        previous_result["amount"] += stored_crop.fresh_mass
                        break
                else:
                    results.append(
                        self._query_result_factory(
                            stored_crop.category,
                            stored_crop.fresh_mass,
                        )
                    )

        return results

    def purchase_feed(self, feeds_to_purchase: dict[RUFAS_ID, float], time: RufasTime, purchase_type: str) -> None:
        """
        Records amounts and cost of feed purchased, and orchestrates storing them.

        Parameters
        ----------
        feeds_to_purchase : dict[RUFAS_ID, float]
            Mapping of RuFaS Feed IDs to the amounts of that feed to be purchased (kg dry matter).
        time : RufasTime
            RufasTime object.

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
                purchase_amount * feed_info.purchase_cost,
                info_map | {"units": MeasurementUnits.DOLLARS},
            )
            self._om.add_variable(
                f"{purchase_type}_{rufas_id}_amount_purchased",
                [purchase_amount, time.simulation_day],
                info_map | {"units": MeasurementUnits.KILOGRAMS},
            )
            self._store_purchased_feed(rufas_id, purchase_amount, time, purchase_type)

    def _adjust_for_shrink(
        self, purchased_feed: PurchasedFeed, purchase_type: str, simulation_day: int, shrink_factor: float = 0.1
    ) -> PurchasedFeed:
        """
        Adjusts the purchased feed to account for shrink loss in storage.

        Parameters
        ----------
        purhased_feed : PurchasedFeed
            PurchasedFeed object containing the feed to be adjusted.
        purchase_type : str
            Type of purchase being made, used for output variable naming.
        simulation_day : int
            The current simulation day, used for tracking feed adjustments.
        shrink_factor : float, optional
            The expected fraction of feed lost due to shrink (default is 0.1 for 10%).

        References
        ----------
        Feed Storage Scientific Documentation equation FS.CON.1.

        Returns
        -------
        PurchasedFeed
            Adjusted PurchasedFeed object with the dry matter mass reduced by the shrink factor.
        """
        # TODO get shrink factor from appropriate feed library source when that data becomes available.
        # Default 10% shrink factor for all purchased feeds for now.
        adjusted_mass = purchased_feed.dry_matter_mass * (1 - shrink_factor)
        self._om.add_variable(
            f"{purchase_type}_purchased_feed_{purchased_feed.rufas_id}_amount_lost_to_shrink",
            [purchased_feed.dry_matter_mass - adjusted_mass, simulation_day],
            {
                "class": self.__class__.__name__,
                "function": self._adjust_for_shrink.__name__,
                "units": MeasurementUnits.DRY_KILOGRAMS,
                "rufas_id": purchased_feed.rufas_id,
                "shrink_factor": shrink_factor,
            },
        )
        return PurchasedFeed(
            rufas_id=purchased_feed.rufas_id,
            dry_matter_mass=adjusted_mass,
            storage_time=purchased_feed.storage_time,
        )

    def _store_purchased_feed(
        self, rufas_id: RUFAS_ID, purchase_amount: float, time: RufasTime, purchase_type: str
    ) -> None:
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
        purchase_type : str
            Type of purchase being made, used for output variable naming.
        """
        purchased_feed = PurchasedFeed(rufas_id, purchase_amount, time.current_date.date())
        if purchase_type == "ration_interval":
            shrink_adjusted_purchased_feed = self._adjust_for_shrink(purchased_feed, purchase_type, time.simulation_day)
        else:
            shrink_adjusted_purchased_feed = purchased_feed
        self.purchased_feed_storage.receive_feed(shrink_adjusted_purchased_feed)

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
        all_available_feeds: list[HarvestedCrop | PurchasedFeed] = []
        for storage in self.active_storages.values():
            all_available_feeds.extend(storage.stored)
        all_available_feeds.extend(self.purchased_feed_storage.stored)

        all_available_feeds = sorted(all_available_feeds, key=lambda feed: feed.storage_time)

        total_purchased_feed_deductions: dict[RUFAS_ID, float] = {}
        total_farmgrown_feed_deductions: dict[RUFAS_ID, float] = {}

        for rufas_id, amount in feeds_to_deduct.items():
            available_feeds = [
                feed for feed in all_available_feeds if self._check_feed_availability(feeds_to_deduct, rufas_id, feed)
            ]

            for feed in available_feeds:
                amount_to_deduct = min(amount, feed.dry_matter_mass)
                amount -= amount_to_deduct

                if isinstance(feed, PurchasedFeed):
                    feed.remove_dry_matter_mass(amount_to_deduct)
                    total_purchased_feed_deductions[rufas_id] = (
                        total_purchased_feed_deductions.get(rufas_id, 0.0) + amount_to_deduct
                    )
                else:
                    feed.remove_feed_mass(amount_to_deduct)
                    harvested_rufas_id = self._select_rufas_id_for_harvested_crop(
                        feed.rufas_ids, list(feeds_to_deduct.keys())
                    )
                    total_farmgrown_feed_deductions[harvested_rufas_id] = (
                        total_farmgrown_feed_deductions.get(harvested_rufas_id, 0.0) + amount_to_deduct
                    )

                if amount == 0.0:
                    break

            if amount != 0.0:
                raise ValueError(f"Was not able to deduct remaining {amount} of feed {rufas_id}.")

        for feed_id, amount_deducted in total_farmgrown_feed_deductions.items():
            self._om.add_variable(
                f"farmgrown_feed_{feed_id}_total_amount_deducted",
                [amount_deducted, simulation_day],
                {
                    "class": self.__class__.__name__,
                    "function": self._deduct_feeds_from_inventory.__name__,
                    "units": MeasurementUnits.DRY_KILOGRAMS,
                    "simulation_day": simulation_day,
                },
            )

        for feed_id, amount_deducted in total_purchased_feed_deductions.items():
            self._om.add_variable(
                f"purchased_feed_{feed_id}_total_amount_deducted",
                [amount_deducted, simulation_day],
                {
                    "class": self.__class__.__name__,
                    "function": self._deduct_feeds_from_inventory.__name__,
                    "units": MeasurementUnits.DRY_KILOGRAMS,
                    "simulation_day": simulation_day,
                },
            )

    def _check_feed_availability(
        self, feeds_to_deduct: dict[RUFAS_ID, float], rufas_id: int, feed: HarvestedCrop | PurchasedFeed
    ) -> bool:
        """
        Helper function that checks if a feed can be fed to animals based on the RuFaS ID and the feeds to deduct.

        Parameters
        ----------
        feeds_to_deduct : dict[RUFAS_ID, float]
            Mapping of RuFaS Feed IDs to the amounts of feed that will be removed from storage (kg dry matter).
        rufas_id : RUFAS_ID
            RuFaS Feed ID of the feed that is being checked (unitless).
        feed : HarvestedCrop | PurchasedFeed
            The feed object to check for availability.

        Returns
        -------
        bool
            True if the feed can be fed to animals, False otherwise.
        """
        if isinstance(feed, HarvestedCrop):
            feed_id = self._select_rufas_id_for_harvested_crop(feed.rufas_ids, list(feeds_to_deduct.keys()))
            is_feedable = True if feed_id == rufas_id else False
        else:
            is_feedable = feed.rufas_id == rufas_id
        return is_feedable

    def _select_rufas_id_for_harvested_crop(
        self, crop_ids: list[RUFAS_ID], feed_ids: list[RUFAS_ID]
    ) -> RUFAS_ID | None:
        """
        Choose which feed a harvested crop will be fed as.

        Parameters
        ----------
        crop_ids : list[RUFAS_ID]
            All RuFaS IDs that a crop may be fed as.
        feed_ids : list[RUFAS_ID]
            List of RuFaS Feed IDs that are being selected from.

        Returns
        -------
        RUFAS_ID | None
            The RuFaS Feed ID that the harvested crop will be mapped to. If there is no feed that the crop can be fed as
            None will be returned.

        Notes
        -----
        Farm grown feeds can map to multiple RuFaS Feed IDs, this ensures they are only counted as a single ID.

        """
        overlapping_feed_ids = set(crop_ids) & set(feed_ids)
        if len(overlapping_feed_ids) == 0:
            return None
        elif len(overlapping_feed_ids) == 1:
            feed_id = list(overlapping_feed_ids)[0]
        else:
            feed_id = min(overlapping_feed_ids)
        return feed_id

    def _setup_available_feeds(
        self, feed_config: dict[str, list[Any]], nutrient_standard: NutrientStandard
    ) -> list[NASEMFeed | NRCFeed]:
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
        available_feeds = []
        feeds_to_parse = feed_config["purchased_feeds"]
        for feed in feeds_to_parse:
            rufas_id = feed["purchased_feed"]
            price = feed["purchased_feed_cost"]
            try:
                nutritive_properties = feed_library[rufas_id]
            except KeyError:
                raise KeyError(f"Feed with RUFAS ID '{rufas_id}' not found in the feed library.")
            new_feed = feed_representation(
                rufas_id=rufas_id,
                amount_available=0.0,
                on_farm_cost=price * ON_FARM_TO_PURCHASED_PRICE_RATION,
                purchase_cost=price,
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
