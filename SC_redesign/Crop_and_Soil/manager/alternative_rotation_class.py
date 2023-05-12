from dataclasses import dataclass
from typing import Optional, List


@dataclass
class PlantingSpec:
    year: int
    """the year (after the start of the simulation) on which a crop should be planted"""
    day: int
    """the julian day (after the start of the simulation) on which a crop should be planted"""


@dataclass
class HarvestSpec:
    year: int
    """the year (after the start of the simulation) on which a crop should be harvested"""
    day: int
    """the julian day (after the start of the simulation) on which a crop should be harvested"""
    operation: Optional[str] = "default"
    """the type of harvest operation that should be conducted"""


@dataclass
class CropRotation:
    crop_ids: List[str]
    """the identifier referencing the crop to initialize. Either a supported `CropSpecies` or the name of a 
    user-defined crop configuration."""
    planting_specs: List[PlantingSpec]
    """the `PlantingSpec` objects that determine when each crop gets initialized"""
    harvest_specs: List[HarvestSpec]
    """the `HarvestSpec` objects that determine when (and how) each crop gets harvested"""

    def __post_init__(self):
        """"
        Raises
        ------
        Exception
            if the attributes are not equal length
        """
        if not len(self.crop_ids) == len(self.planting_specs) == len(self.harvest_specs):
            raise Exception("crop_ids, planting_specs, and harvest_specs must all be the same length")
