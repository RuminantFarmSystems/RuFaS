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


class CropType(Enum):
    """
    Enum for subdivisions of Crop Categories.

    Attributes:
        WHEAT: Type of Small Grain.
        RYE: Type of Small Grain.
        OAT: Type of Small Grain.
        RICE: Type of Small Grain.
        HIGH_MOISTURE: Type of Corn.
        SILAGE: Type of Corn.
        WHOLE_PLANT: Type of Corn.
        GRAIN: Type of Corn or Soy.
        FORAGE: Type of Soy.
        ALFALFA: Type of Alfalfa.
        RYEGRASS: Type of Grass.
        ORCHARDGRASS: Type of Grass.
        FINE_FESCUE: Type of Grass.
        TALL_FESCUE: Type of Grass.
        MEADOW_FESCUE: Type of Grass.
    """

    WHEAT = "Wheat"
    RYE = "Rye"
    OAT = "Oat"
    RICE = "Rice"
    HIGH_MOISTURE = "High-moisture"
    SILAGE = "Silage"
    WHOLE_PLANT = "Whole-plant"
    GRAIN = "Grain"
    FORAGE = "Forage"
    ALFALFA = "Alfalfa"
    RYEGRASS = "Ryegrass"
    ORCHARDGRASS = "Orchardgrass"
    FINE_FESCUE = "Fine Fescue"
    TALL_FESCUE = "Tall Fescue"
    MEADOW_FESCUE = "Meadow Fescue"


