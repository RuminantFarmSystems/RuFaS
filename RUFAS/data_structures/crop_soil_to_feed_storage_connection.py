from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import NamedTuple

from RUFAS.general_constants import GeneralConstants
from RUFAS.time import Time

from .feed_storage_to_animal_connection import RUFAS_ID


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
        Represents a type of Small Grain.
    RYE : str
        Represents a type of Small Grain.
    OAT : str
        Represents a type of Small Grain.
    RICE : str
        Represents a type of Small Grain.
    HIGH_MOISTURE : str
        Represents a type of Corn.
    SILAGE : str
        Represents a type of Corn.
    WHOLE_PLANT : str
        Represents a type of Corn.
    GRAIN : str
        Represents a type of Corn or Soy.
    FORAGE : str
        Represents a type of Soy.
    ALFALFA : str
        Represents a type of Alfalfa.
    RYEGRASS : str
        Represents a type of Grass.
    ORCHARDGRASS : str
        Represents a type of Grass.
    FINE_FESCUE : str
        Represents a type of Grass.
    TALL_FESCUE : str
        Represents a type of Grass.
    MEADOW_FESCUE : str
        Represents a type of Grass.

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


"""Maps the valid combinations of Crop Categories and Crop Types."""
CROP_CATEGORY_TO_CROP_TYPE_MAPPING = {
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


class StorageType(Enum):
    """
    Maps each storage type to its respective class.
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
    config_name : str
        Name of the crop configuration that produced this harvested crop.
    rufas_ids : list[RUFAS_ID]
        List of RUFAS_IDs that this Harvested Crop may be fed as (unitless).
    harvest_time : date
        The time at which the crop was harvested.
    storage_time : date
        The time at which the crop was stored.
    last_time_degraded : date
        The last time at which the quality and mass of the crop was recalculated. This value is initially set to the
        storage time of the crop.
    fresh_mass : float
        The fresh mass of the crop in kg.
    dry_matter_percentage : float
        Percent of mass that is not water.
    initial_dry_matter_percentage : float
        Percent of mass that is not water at the time this crop is stored.
    initial_dry_matter_mass : float
        Mass of dry matter initially stored (kg). Note that this value is only used if this crop is stored in a `Hay`
        instance (or one of its child classes), and is only calculated at the time of storage.
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
    bale_density : float
        Density of this crop if it is hayed in kg per cubic meter. Note that this value is only used if this crop is
        stored in a `Hay` instance (or one of its child classes), and is only calculated at the time of storage.
    total_sensible_heat_generated : float
        Heat generated by this crop if it is hayed in kJ per kg. Note that this value is only used if this crop is
        stored in a `Hay` instance (or one of its child classes), and is only calculated at the time of storage.
    dry_matter_mass

    Methods
    -------
    __post_init__():
        Validates the category and type relationship.

    """

    category: CropCategory
    type: CropType
    config_name: str
    rufas_ids: list[RUFAS_ID]
    harvest_time: date
    storage_time: date
    last_time_degraded: date = field(init=False)
    fresh_mass: float
    dry_matter_percentage: float
    initial_dry_matter_percentage: float = field(init=False)
    initial_dry_matter_mass: float = field(init=False)
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
    bale_density: float = field(init=False)
    total_sensible_heat_generated: float = field(init=False)

    def __post_init__(self) -> None:
        """
        Validates that the type of the crop is consistent with its category.

        Raises
        ------
        ValueError
            If the crop type is not valid for the crop category.

        """

        if self.type not in CROP_CATEGORY_TO_CROP_TYPE_MAPPING[self.category]:
            raise ValueError(f"{self.type} is not a valid type for the category {self.category}.")

        self.estimated_maximum_effluent = self._estimate_maximum_effluent()
        self.bale_density = self._calculate_bale_density()
        self.total_sensible_heat_generated = self._calculate_total_sensible_heat_generated()
        self.initial_dry_matter_percentage = self.dry_matter_percentage
        self.initial_dry_matter_mass = self.dry_matter_mass
        self.last_time_degraded = self.storage_time

        if isinstance(self.harvest_time, Time):
            self.harvest_time = self.harvest_time.current_date.date()
        if isinstance(self.storage_time, Time):
            self.storage_time = self.storage_time.current_date.date()

    @property
    def dry_matter_mass(self) -> float:
        """
        Calculates the dry matter mass of this crop in kg.
        """
        dry_matter_fraction = self.dry_matter_percentage * GeneralConstants.PERCENTAGE_TO_FRACTION
        return dry_matter_fraction * self.fresh_mass

    def remove_dry_matter_mass(self, mass_to_remove: float) -> None:
        """Removes the specified amount of dry matter mass from the crop."""
        new_dry_matter_mass = self.dry_matter_mass - mass_to_remove
        self.fresh_mass -= mass_to_remove
        if self.fresh_mass == 0.0:
            self.dry_matter_percentage = 0.0
            return
        self.dry_matter_percentage = (new_dry_matter_mass / self.fresh_mass) * GeneralConstants.FRACTION_TO_PERCENTAGE

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

    def _calculate_bale_density(self) -> float:
        """
        Calculates the bale density of hayed crop.

        Returns
        -------
        float
            Bale density of this crop (kg / cubic meter).

        References
        ----------
        .. [1] Feed Storage Scientific Documentation, equation 1.2.5

        """
        return 100 + 440 * (1.0 - self.dry_matter_percentage * GeneralConstants.PERCENTAGE_TO_FRACTION)

    def _calculate_total_sensible_heat_generated(self) -> float:
        """
        Calculates the total sensible heat generated by a hayed crop.

        Returns
        -------
        float
            Total sensible heat generated by this crop (kJ per kilogram).

        References
        ----------
        .. [1] Feed Storage Scientific Documentation, equation 1.2.4

        """
        moisture_frac = 1 - self.dry_matter_percentage * GeneralConstants.PERCENTAGE_TO_FRACTION
        heat: float = (
            104 * moisture_frac**2.18 * self.bale_density**0.5 + 5.72 * moisture_frac**1.23 * self.bale_density**0.94
        )
        return heat


class HarvestedCropStorageType(NamedTuple):
    """Used to couple a yield collected in the Crop and Soil module with the storage type it will be put in."""

    harvested_crop: HarvestedCrop
    storage_type: StorageType
