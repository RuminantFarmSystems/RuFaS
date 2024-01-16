from dataclasses import dataclass

from RUFAS.routines.feed_storage.enums import CropCategory, CropType
from RUFAS.routines.feed_storage.feed_manager import StorageType
from RUFAS.routines.field.crop.crop_data import (
    CropData,
    PlantCategory
)


@dataclass(kw_only=True)
class Corn(CropData):
    """Crop data class with default values for corn."""
    species: str = "corn"
    name: str = "default corn"
    plant_code: str = "CORN"
    scientific_name: str = "Zea mays"
    plant_category: PlantCategory = PlantCategory("warm_annual")
    is_nitrogen_fixer: bool = False

    crop_category: CropCategory = CropCategory.CORN

    minimum_temperature: float = 8.0
    optimal_temperature: float = 25.0

    potential_heat_units: float = 1150

    max_leaf_area_index: float = 3.0
    first_heat_fraction_point: float = 0.15
    first_leaf_fraction_point: float = 0.05
    second_heat_fraction_point: float = 0.50
    second_leaf_fraction_point: float = 0.95
    senescent_heat_fraction: float = 0.90

    light_use_efficiency: float = 39.0

    emergence_nitrogen_fraction: float = 0.0470
    half_mature_nitrogen_fraction: float = 0.0177
    mature_nitrogen_fraction: float = 0.0138
    emergence_phosphorus_fraction: float = 0.0048
    half_mature_phosphorus_fraction: float = 0.0018
    mature_phosphorus_fraction: float = 0.0014

    max_root_depth: float = 2_000


@dataclass(kw_only=True)
class CornGrain(Corn):
    """
    Crop data class with yield-related properties for Corn silage.

    Attributes
    ----------
    optimal_harvest_index: float, default=0.50
        Fraction of crop biomass that is harvested in optimal growing conditions (unitless).
    min_harvest_index: float, default=0.30
        Fraction of crop biomass that is harvested in water-stressed growing conditions (unitless).
    dry_matter_percentage: float, default=86.0907
        Percentage of harvested crop biomass that is dry matter (unitless).
    lignin_dry_matter_percentage: float, default=1.37
        Percentage of dry matter yield that is lignin (unitless).
    yield_nitrogen_fraction: float, default=0.0140
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00309
        Fraction of dry matter crop yield that is phosphorus (unitless).

    """
    species: str = "corn_grain"
    name: str = "corn grain"

    crop_type: CropType = CropType.GRAIN
    storage_type: StorageType = StorageType.DRY

    optimal_harvest_index: float = 0.60
    min_harvest_index: float = 0.40
    dry_matter_percentage: float = 86.0907
    lignin_dry_matter_percentage: float = 1.37
    yield_nitrogen_fraction: float = 0.0140
    yield_phosphorus_fraction: float = 0.00309


@dataclass(kw_only=True)
class CornSilage(Corn):
    """
    Crop data class with yield-related properties for Corn silage.

    Attributes
    ----------
    optimal_harvest_index: float, default=0.90
        Fraction of crop biomass that is harvested in optimal growing conditions (unitless).
    min_harvest_index: float, default=0.90
        Fraction of crop biomass that is harvested in water-stressed growing conditions (unitless).
    dry_matter_percentage: float, default=35.361
        Percentage of harvested crop biomass that is dry matter (unitless).
    lignin_dry_matter_percentage: float, default=3.054
        Percentage of dry matter yield that is lignin (unitless).
    yield_nitrogen_fraction: float, default=0.0140
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00232
        Fraction of wet crop yield that is phosphorus (unitless).

    """
    species: str = "corn_silage"
    name: str = "corn silage"

    crop_type: CropType = CropType.SILAGE
    storage_type: StorageType = StorageType.BUNKER

    max_leaf_area_index: float = 4.0

    optimal_harvest_index: float = 0.90
    min_harvest_index: float = 0.68
    dry_matter_percentage: float = 35.361
    lignin_dry_matter_percentage: float = 3.054
    yield_nitrogen_fraction: float = 0.0140
    yield_phosphorus_fraction: float = 0.00232
