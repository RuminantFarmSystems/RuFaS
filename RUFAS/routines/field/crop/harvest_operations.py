from enum import Enum


class HarvestOperation(Enum):
    """Enum of the supported harvest operations"""
    HARVEST_KILL = "harvest"
    HARVEST_NO_KILL = "harvest_no_kill"
    KILL_NO_HARVEST = "kill"


FINAL_HARVEST_OPERATIONS = [HarvestOperation.HARVEST_KILL, HarvestOperation.KILL_NO_HARVEST]
"""This variable is a list of all the HarvestOperation instances that will terminate the Crop instance (either through
 via death. This list should be appended with any operation added to the HarvestOperation class that will ultimately
 kill the crop before another harvest operation can occur (a non-obvious example would be cutting the crop a final
 time, without harvesting, and allowing the un-cut portion to sit in the field to fallow."""
