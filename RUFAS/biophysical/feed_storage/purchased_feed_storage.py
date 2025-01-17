from dataclasses import dataclass
from datetime import date

from RUFAS.data_structures.feed_storage_to_animal_connection import RUFAS_ID


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


class PurchasedFeedStorage():
    """
    Storage child class which holds feeds which were purchased and are not stored alongside farm-grown feeds.
    """

    def __init__(self) -> None:
        self.stored: list[PurchasedFeed] = []

    def receive_feed(self, purchased_feed: PurchasedFeed) -> None:
        self.stored.append(purchased_feed)
