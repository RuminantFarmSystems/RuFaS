from RUFAS.EEE.economics.handler.base import LineItemHandler
from RUFAS.EEE.economics.handler.bedding_requirements import BeddingRequirementsHandler
from RUFAS.EEE.economics.handler.purchased_feed_costs import PurchasedFeedCostHandler
from RUFAS.EEE.economics.handler.seed_costs import SeedCostHandler

SPECIAL_CASE_HANDLERS: list[type[LineItemHandler]] = [
    BeddingRequirementsHandler,
    PurchasedFeedCostHandler,
    SeedCostHandler
]

__all__ = ["SPECIAL_CASE_HANDLERS", "LineItemHandler", "BeddingRequirementsHandler", "PurchasedFeedCostHandler",
           "SeedCostHandler"]
