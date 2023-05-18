from enum import Enum


class HarvestOperation(Enum):
    """Enum of the supported harvest operations"""
    HARVEST = "default"
    HARVEST_NOKILL = "no_kill"


FINAL_HARVEST_OPERATIONS = ["default"]
"""This variable is a list of all the HarvestOperation instances that will terminate the Crop instance (either through
 via death. This list should be appended with any operation added to the HarvestOperation class that will ultimately
 kill the crop before another harvest operation can occur (a non-obvious example would be cutting the crop a final
 time, without harvesting, and allowing the un-cut portion to sit in the field to fallow."""
