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
    purchase_date : date
        Date on which this feed was purchased.

    """
    rufas_id: RUFAS_ID
    dry_matter_mass: float
    purchase_date: date


class PurchasedFeedStorage():
    """
    Storage child class which holds feeds which were purchased and are not stored alongside farm-grown feeds.
    """

    def __init__(self) -> None:
        self.stored: list[PurchasedFeed] = []

    def receive_feed(self, purchased_feed: PurchasedFeed) -> None:
        self.stored.append(purchased_feed)
