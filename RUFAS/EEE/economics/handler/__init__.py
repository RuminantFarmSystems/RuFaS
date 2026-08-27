from RUFAS.EEE.economics.handler.base import Handler
from RUFAS.EEE.economics.handler.bedding_requirements import BeddingRequirementsHandler
from RUFAS.EEE.economics.handler.purchased_feed_costs import PurchasedFeedCostHandler


SPECIAL_CASE_HANDLERS: list[type[Handler]] = [
    BeddingRequirementsHandler,
    PurchasedFeedCostHandler,
]

__all__ = ["SPECIAL_CASE_HANDLERS", "Handler", "BeddingRequirementsHandler", "PurchasedFeedCostHandler", ]
