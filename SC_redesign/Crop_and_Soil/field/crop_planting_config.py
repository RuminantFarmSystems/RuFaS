from dataclasses import dataclass
from typing import Optional, List

from SC_redesign.Crop_and_Soil.crop.species_data_factory import CropSpecies


@dataclass
class CropPlantingConfig:
    """Configuration class that specifies how crops in a field should be initialized by the Field.plant_crops()
    method

    Details: this class should contain any and all attributes needed to setup and create a series of Crop objects,
    including their respective CropData objects.
    """
    species: Optional[List[CropSpecies]] = None
    """all the species to be planted in the field"""
    planting_day: int = 0  # perhaps a list option to specify each crop being planted separately in the field?
    """the (sequential) day of the simulation on which the crops should be planted in their field"""
    planting_year: int = 0  # perhaps a list option to specify each crop being planted separately in the field?
    """the (sequential) year of the simulation on which crops should be planted in their field"""
    # ...
