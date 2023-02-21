from enum import Enum

class HarvestOperation(Enum):
    """Enum of the supported harvest operations"""
    HARVEST = "default"
    HARVEST_NOKILL = "no_kill"
