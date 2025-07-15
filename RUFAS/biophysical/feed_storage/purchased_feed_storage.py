from copy import deepcopy
from dataclasses import dataclass, replace
from datetime import date

from RUFAS.data_structures.feed_storage_to_animal_connection import RUFAS_ID, NRCFeed, NASEMFeed
from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits
from RUFAS.rufas_time import RufasTime


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
    Storage child class which holds feeds which were purchased and are not stored alongside farm-grown feeds.
    """

    def __init__(self) -> None:
        self.stored: list[PurchasedFeed] = []
        self._om = OutputManager()

    def project_shrinkage(
            self,
            days_interval: int,
            available_feeds: list[NASEMFeed | NRCFeed]
    ) -> list[PurchasedFeed]:
        """
        Projects the state of purchased feeds at a given future date,
        without mutating self.stored.

        Parameters
        ----------
        days_interval: int
            Days to project.
        available_feeds : list[NASEMFeed | NRCFeed]
            List of feed metadata to look up shrink factors.

        Returns
        -------
        list[PurchasedFeed]
            Cloned feeds in their projected post‑shrinkage state.
        """
        projected_feeds: list[PurchasedFeed] = []

        for feed in self.stored:
            feed_info = next(
                (af for af in available_feeds if af.rufas_id == feed.rufas_id),
                None
            )
            if feed_info is None:
                raise ValueError(
                    f"Trying to shrink unavailable feed {feed.rufas_id}."
                )
            if days_interval > 3:
                new_dm = feed.dry_matter_mass * (1 - feed_info.shrink_factor)
                new_feed = replace(feed, dry_matter_mass=new_dm)
            else:
                new_feed = replace(feed)

            projected_feeds.append(new_feed)

        return projected_feeds

    def process_shrinkage(self, time: RufasTime, available_feeds: list[NASEMFeed | NRCFeed]) -> None:
        """Process the shrinkage of purchased feed."""
        for feed in self.stored:
            feed_id = feed.rufas_id
            feed_info = next(
                (available_feed for available_feed in available_feeds if available_feed.rufas_id == feed_id), None
            )
            if feed_info is None:
                raise ValueError(f"Trying to shrink unavailable feed {feed_id} during purchased feed shrinkage.")

            shrink_factor = feed_info.shrink_factor
            delta = time.current_date.date() - feed.storage_time
            if delta.days > 3:
                feed.dry_matter_mass = feed.dry_matter_mass * (1 - shrink_factor)

    def receive_feed(self, purchased_feed: PurchasedFeed) -> None:
        self.stored.append(purchased_feed)

    def remove_empty_crops(self) -> None:
        """Removes all feeds with no dry matter mass left."""
        self.stored = [feed for feed in self.stored if feed.dry_matter_mass >= 0.000_001]

    def report_stored_purchased_feeds(self, time: RufasTime) -> None:
        """Reports dry matter of stored feeds."""
        info_map = {
            "class": self.__class__.__name__,
            "function": self.report_stored_purchased_feeds.__name__,
            "simulation_day": time.simulation_day,
            "units": MeasurementUnits.KILOGRAMS,
        }
        report = self.create_consolidated_feed_report()

        for rufas_id, mass in report.items():
            info_map["rufas_id"] = rufas_id
            info_map["mass"] = mass
            self._om.add_variable(f"stored_feed_{rufas_id}", mass, info_map)

    def create_consolidated_feed_report(self) -> dict[RUFAS_ID, float]:
        """Creates report of all stored feeds consolidated by type."""
        report = {}
        for feed in self.stored:
            if feed.rufas_id not in report:
                report[feed.rufas_id] = 0.0
            report[feed.rufas_id] += feed.dry_matter_mass
        return report
