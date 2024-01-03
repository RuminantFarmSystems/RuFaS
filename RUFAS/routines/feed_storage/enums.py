from enum import Enum


class CropCategory(Enum):
    """
    Enum for Crop Categories.

    Attributes
    ----------
    SMALL_GRAIN : str
        Represents small grain crops.
    CORN : str
        Represents corn crops.
    SOY : str
        Represents soy crops.
    GRASS : str
        Represents grass crops.
    ALFALFA : str
        Represents alfalfa crops.
    """

    SMALL_GRAIN = "Small grain"
    CORN = "Corn"
    SOY = "Soy"
    GRASS = "Grass"
    ALFALFA = "Alfalfa"


class CropType(Enum):
    """
    Enum for subdivisions of Crop Categories.

    Attributes
    ----------
    WHEAT : str
        Type of Small Grain.
    RYE : str
        Type of Small Grain.
    OAT : str
        Type of Small Grain.
    RICE : str
        Type of Small Grain.
    HIGH_MOISTURE : str
        Type of Corn.
    SILAGE : str
        Type of Corn.
    WHOLE_PLANT : str
        Type of Corn.
    GRAIN : str
        Type of Corn or Soy.
    FORAGE : str
        Type of Soy.
    ALFALFA : str
        Type of Alfalfa.
    RYEGRASS : str
        Type of Grass.
    ORCHARDGRASS : str
        Type of Grass.
    FINE_FESCUE : str
        Type of Grass.
    TALL_FESCUE : str
        Type of Grass.
    MEADOW_FESCUE : str
        Type of Grass.
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
