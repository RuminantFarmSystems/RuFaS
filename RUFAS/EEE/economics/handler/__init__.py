from RUFAS.EEE.economics.handler.base import Handler
from RUFAS.EEE.economics.handler.bedding_requirements import BeddingRequirementsHandler
from RUFAS.EEE.economics.handler.digester_revenue import DigesterRevenueHandler
from RUFAS.EEE.economics.handler.purchased_feed_costs import PurchasedFeedCostHandler
from RUFAS.EEE.economics.handler.seed_costs import SeedCostHandler
from RUFAS.EEE.economics.handler.slurry_storage_cost import SlurryStorageCostHandler

SPECIAL_CASE_HANDLERS: list[type[Handler]] = [
    BeddingRequirementsHandler,
    PurchasedFeedCostHandler,
    SeedCostHandler,
    SlurryStorageCostHandler,
    DigesterRevenueHandler
]

__all__ = ["SPECIAL_CASE_HANDLERS", "Handler", "BeddingRequirementsHandler", "PurchasedFeedCostHandler",
           "SeedCostHandler", "SlurryStorageCostHandler", "DigesterRevenueHandler"]
