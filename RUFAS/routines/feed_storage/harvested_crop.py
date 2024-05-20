from copy import deepcopy
from dataclasses import dataclass, field
from RUFAS.general_constants import GeneralConstants
from RUFAS.time import Time
from .enums import CropCategory, CropType


"""This is the dry matter fraction above which an ensiled crop will not experience any effluent loss."""
EFFLUENT_MAXIMUM_DRY_MATTER_FRACTION = 0.3


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
        The time at which the crop was harvested.
    storage_time : Time
        The time at which the crop was stored.
    last_time_degraded : Time
        The last time at which the quality and mass of the crop was recalculated. This value is initially set to the
        storage time of the crop.
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
    estimated_maximum_effluent : float
        Total amount of mass that will be lost from this crop as effluent in kg. Note that this value is only used if
        this crop is stored in a `Silage` instance (or one of its child classes), and is calculated only once, when it
        is stored.
    dry_matter_mass

    Methods
    -------
    __post_init__():
        Validates the category and type relationship.

    """

    category: CropCategory
    type: CropType
    harvest_time: Time
    storage_time: Time
    last_time_degraded: Time = field(init=False)
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
    estimated_maximum_effluent: float = field(init=False)

    def __post_init__(self) -> None:
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
            raise ValueError(f"{self.type} is not a valid type for the category {self.category}.")

        self.estimated_maximum_effluent = self._estimate_maximum_effluent()
        self.last_time_degraded = deepcopy(self.storage_time)

    @property
    def dry_matter_mass(self) -> float:
        """
        Calculates the dry matter mass of this crop in kg.
        """
        dry_matter_fraction = self.dry_matter_percentage * GeneralConstants.PERCENTAGE_TO_FRACTION
        return dry_matter_fraction * self.fresh_mass

    def _estimate_maximum_effluent(self) -> float:
        """
        Calculates the total amount of effluent loss this crop will experience if it is ensiled.

        Returns
        -------
        float
            Estimated maximum amount of mass that will flow out of this crop in kg.

        References
        ----------
        .. [1] Feed Storage Scientific Documentation, section 1.3.1

        """
        dry_matter_fraction = self.dry_matter_percentage * GeneralConstants.PERCENTAGE_TO_FRACTION
        bounded_dry_matter_fraction = min(EFFLUENT_MAXIMUM_DRY_MATTER_FRACTION, dry_matter_fraction)
        effluent_fraction = 1.0 - bounded_dry_matter_fraction - (1 - EFFLUENT_MAXIMUM_DRY_MATTER_FRACTION)
        return self.fresh_mass * effluent_fraction
