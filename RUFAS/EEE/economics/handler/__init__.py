from RUFAS.EEE.economics.handler.base import Handler
from RUFAS.EEE.economics.handler.seed_costs import SeedCostHandler


SPECIAL_CASE_HANDLERS: list[type[Handler]] = [
    SeedCostHandler,
]

__all__ = ["Handler", "SeedCostHandler", ]
