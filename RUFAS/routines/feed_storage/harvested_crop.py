from dataclasses import dataclass
from enum import Enum


class CropCategory(Enum):
    """
    Enum for Crop Categories.

    Attributes:
        SMALL_GRAIN: Represents small grain crops.
        CORN: Represents corn crops.
        SOY: Represents soy crops.
        GRASS: Represents grass crops.
        ALFALFA: Represents alfalfa crops.
    """

    SMALL_GRAIN = "Small grain"
    CORN = "Corn"
    SOY = "Soy"
    GRASS = "Grass"
    ALFALFA = "Alfalfa"
