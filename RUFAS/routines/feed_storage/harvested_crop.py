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


@dataclass
class HarvestedCrop:
    """
    A class to represent a harvested crop with its attributes.

    Attributes
    ----------
    category : CropCategory
        The category of the crop (enum).
    type : CropType
        The type of the crop (enum), a subdivision of crop category.
    fresh_mass : float
        The fresh mass of the crop in kg.
    dry_matter_percentage : float
        Percent of mass that is not water.
    dry_matter_digestibility : float
        Percent of mass that is digestible.
    crude_protein_percent : float
        Percent of mass that is dietary crude protein.
    non_protein_nitrogen : float
        Percent of mass that is non-protein nitrogen.
    starch : float
        Percent of mass that is starch.
    adf : float
        Percent of mass that is acid detergent fiber.
    ndf : float
        Percent of mass that is neutral detergent fiber.
    lignin : float
        Percent of mass that is lignin.
    sugar : float
        Percent of mass that is labile carbohydrate.
    ash : float
        Percent of mass that is ash.

    Methods
    -------
    __post_init__():
        Validates the category and type relationship.
    """

    category: CropCategory
    type: CropType
    fresh_mass: float
    dry_matter_percentage: float
    dry_matter_digestibility: float
    crude_protein_percent: float
    non_protein_nitrogen: float
    starch: float
    adf: float
    ndf: float
    lignin: float
    sugar: float
    ash: float

