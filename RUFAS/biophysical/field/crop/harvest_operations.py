from enum import Enum


class HarvestOperation(Enum):
    """Enum of the supported harvest operations"""

    HARVEST_KILL = "harvest_kill"
    HARVEST_ONLY = "harvest_only"
    KILL_ONLY = "kill_only"


VALID_HARVEST_OPERATIONS: frozenset[HarvestOperation] = frozenset({
    HarvestOperation.HARVEST_KILL,
    HarvestOperation.HARVEST_ONLY,
    HarvestOperation.KILL_ONLY,
})

FINAL_HARVEST_OPERATIONS: frozenset[HarvestOperation] = frozenset({
    HarvestOperation.HARVEST_KILL,
    HarvestOperation.KILL_ONLY,
})
"""This variable is a list of all the HarvestOperation instances that will terminate the Crop instance (either through
 via death. This list should be appended with any operation added to the HarvestOperation class that will ultimately
 kill the crop before another harvest operation can occur (a non-obvious example would be cutting the crop a final
 time, without harvesting, and allowing the un-cut portion to sit in the field to fallow."""
