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
        Represents a type of type of Small Grain.
    RYE : str
        Represents a type of type of Small Grain.
    OAT : str
        Represents a type of type of Small Grain.
    RICE : str
        Represents a type of type of Small Grain.
    HIGH_MOISTURE : str
        Represents a type of type of Corn.
    SILAGE : str
        Represents a type of type of Corn.
    WHOLE_PLANT : str
        Represents a type of type of Corn.
    GRAIN : str
        Represents a type of type of Corn or Soy.
    FORAGE : str
        Represents a type of type of Soy.
    ALFALFA : str
        Represents a type of type of Alfalfa.
    RYEGRASS : str
        Represents a type of type of Grass.
    ORCHARDGRASS : str
        Represents a type of type of Grass.
    FINE_FESCUE : str
        Represents a type of type of Grass.
    TALL_FESCUE : str
        Represents a type of type of Grass.
    MEADOW_FESCUE : str
        Represents a type of type of Grass.
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
