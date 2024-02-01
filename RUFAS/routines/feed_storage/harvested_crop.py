from dataclasses import dataclass
from RUFAS.time import Time
from .enums import CropCategory, CropType


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
    harvest_time : Time
         The time at which the crop was harvested
    storage_time : Time
         The time at which the crop was stored
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
    harvest_time: Time
    storage_time: Time
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

    def __post_init__(self):
        """
        Validates that the type of the crop is consistent with its category.

        Raises
        ------
        ValueError
            If the crop type is not valid for the crop category.
        """
        category_to_type = {
            CropCategory.SMALL_GRAIN: [
                CropType.WHEAT,
                CropType.RYE,
                CropType.OAT,
                CropType.RICE,
            ],
            CropCategory.CORN: [
                CropType.HIGH_MOISTURE,
                CropType.SILAGE,
                CropType.WHOLE_PLANT,
                CropType.GRAIN,
            ],
            CropCategory.SOY: [CropType.FORAGE, CropType.GRAIN],
            CropCategory.ALFALFA: [CropType.ALFALFA],
            CropCategory.GRASS: [
                CropType.RYEGRASS,
                CropType.ORCHARDGRASS,
                CropType.FINE_FESCUE,
                CropType.TALL_FESCUE,
                CropType.MEADOW_FESCUE,
            ],
        }

        if self.type not in category_to_type[self.category]:
            raise ValueError(
                f"{self.type} is not a valid type for the category {self.category}."
            )
