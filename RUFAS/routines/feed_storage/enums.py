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


class StorageType(Enum):
    """
    Enumeration of storage types.

    Attributes
    ----------
    PROTECTED_INDOORS : str
        Represents a type of hay storage.
    PROTECTED_WRAPPED : str
        Represents a type of hay storage.
    PROTECTED_TARPED : str
        Represents a type of hay storage.
    UNPROTECTED : str
        Represents a type of hay storage.
    BALEAGE : str
        Represents a type of baleage storage.
    DRY : str
        Represents a type of grain storage.
    HIGH_MOISTURE : str
        Represents a type of grain storage.
    BUNKER : str
        Represents a type of silage storage.
    PILE : str
        Represents a type of silage storage.
    BAG : str
        Represents a type of silage storage.
    """

    PROTECTED_INDOORS = "Protected Indoors"
    PROTECTED_WRAPPED = "Protected Wrapped"
    PROTECTED_TARPED = "Protected Tarped"
    UNPROTECTED = "Unprotected"
    BALEAGE = "Baleage"
    DRY = "Dry"
    HIGH_MOISTURE = "High Moisture"
    BUNKER = "Bunker"
    PILE = "Pile"
    BAG = "Bag"
