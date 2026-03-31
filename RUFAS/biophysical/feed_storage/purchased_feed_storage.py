from dataclasses import dataclass
from datetime import date

from RUFAS.data_structures.feed_storage_to_animal_connection import RUFAS_ID, Feed
from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits


@dataclass
class PurchasedFeed:
    """
    Stores the identifier, available mass and storage date of a purchased feed.

    Parameters
    ----------
    rufas_id : RUFAS_ID
        RuFaS ID of the feed.
    dry_matter_mass : RUFAS_ID
        Dry matter mass of the feed still available.
    storage_time : date
        Date on which this feed was purchased.

    """

    rufas_id: RUFAS_ID
    dry_matter_mass: float
    storage_time: date

    def remove_dry_matter_mass(self, mass_to_remove: float) -> None:
        """Removes the specified amount of dry matter mass from the crop."""
        self.dry_matter_mass -= mass_to_remove


class PurchasedFeedStorage:
    """
    Storage class which holds feeds which were purchased and are not stored alongside farm-grown feeds.
    """

    def __init__(self, available_feeds: list[Feed]) -> None:
        self.available_feeds: list[Feed] = available_feeds
        self.stored: list[PurchasedFeed] = []
        self._prefix = "Feed.PurchasedFeedStorage"
        self._om = OutputManager()

    def receive_feed(self, purchased_feed: PurchasedFeed) -> None:
        self.stored.append(purchased_feed)

    def remove_empty_crops(self) -> None:
        """Removes all feeds with no dry matter mass left."""
        self.stored = [feed for feed in self.stored if feed.dry_matter_mass >= 0.000_001]

    def report_stored_purchased_feeds(self, simulation_day: int, reporting_suffix: str) -> None:
        """Reports dry matter of stored feeds."""
        info_map = {
            "class": self.__class__.__name__,
            "function": self.report_stored_purchased_feeds.__name__,
            "simulation_day": simulation_day,
            "units": MeasurementUnits.KILOGRAMS,
            "suffix": reporting_suffix,
        }
        report = self.create_consolidated_feed_report()

        for rufas_id, mass in report.items():
            self._om.add_variable(f"stored_feed_{rufas_id}", mass, info_map)

    def create_consolidated_feed_report(self) -> dict[RUFAS_ID, float]:
        """Creates report of all stored feeds consolidated by type."""
        report = {}
        for feed in self.stored:
            if feed.rufas_id not in report:
                report[feed.rufas_id] = 0.0
            report[feed.rufas_id] += feed.dry_matter_mass
        for available_feed in self.available_feeds:
            if available_feed.rufas_id not in report:
                report[available_feed.rufas_id] = 0.0
        return report
