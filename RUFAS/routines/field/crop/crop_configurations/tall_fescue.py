from dataclasses import dataclass

from RUFAS.routines.feed_storage.enums import CropCategory, CropType
from RUFAS.routines.feed_storage.feed_manager import StorageType
from RUFAS.routines.field.crop.crop_data import (
    CropData,
    PlantCategory
)


@dataclass(kw_only=True)
class TallFescue(CropData):
    """crop data class with default values for tall fescue"""
    species: str = "tall_fescue"
    name: str = "default tall_fescue"
    plant_code: str = "FESC"
    scientific_name: str = "Festuca arundinaceae"
    plant_category: PlantCategory = PlantCategory("perennial")
    is_nitrogen_fixer: bool = False

    crop_category: CropCategory = CropCategory.GRASS
    crop_type: CropType = CropType.TALL_FESCUE

    minimum_temperature: float = 0.0
    optimal_temperature: float = 15.0

    max_leaf_area_index: float = 4.0
    first_heat_fraction_point: float = 0.15
    first_leaf_fraction_point: float = 0.01
    second_heat_fraction_point: float = 0.50
    second_leaf_fraction_point: float = 0.95
    senescent_heat_fraction: float = 0.80

    light_use_efficiency: float = 30.0

    emergence_nitrogen_fraction: float = 0.0560
    half_mature_nitrogen_fraction: float = 0.0210
    mature_nitrogen_fraction: float = 0.0120
    emergence_phosphorus_fraction: float = 0.0099
    half_mature_phosphorus_fraction: float = 0.0022
    mature_phosphorus_fraction: float = 0.0019

    max_root_depth: float = 2_000


@dataclass(kw_only=True)
class TallFescueSilage(TallFescue):
    """
    Crop data class with yield-related properties for Tall Fescue silage.

    Attributes
    ----------
    optimal_harvest_index: float, default=0.90
        Fraction of crop biomass that is harvested in optimal growing conditions (unitless).
    min_harvest_index: float, default=0.4
        Fraction of crop biomass that is harvested in water-stressed growing conditions (unitless).
    dry_matter_percentage: float, default=39.612
        Percentage of harvested crop biomass that is dry matter (unitless).
    lignin_dry_matter_percentage: float, default=5.616
        Percentage of dry matter yield that is lignin (unitless).
    yield_nitrogen_fraction: float, default=0.0229376
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00302
        Fraction of wet crop yield that is phosphorus (unitless).

    """
    species: str = "tall_fescue_silage"
    name: str = "tall_fescue silage"

    storage_type: StorageType = StorageType.BUNKER

    optimal_harvest_index: float = 0.90
    min_harvest_index: float = 0.4
    dry_matter_percentage: float = 39.612
    lignin_dry_matter_percentage: float = 5.616
    yield_nitrogen_fraction: float = 0.0229376
    yield_phosphorus_fraction: float = 0.00302


@dataclass(kw_only=True)
class TallFescueBaleage(TallFescueSilage):
    """
    Crop data class with yield-related properties for Tall Fescue baleage.

    Attributes
    ----------
    optimal_harvest_index: float, default=0.90
        Fraction of crop biomass that is harvested in optimal growing conditions (unitless).
    min_harvest_index: float, default=0.4
        Fraction of crop biomass that is harvested in water-stressed growing conditions (unitless).
    dry_matter_percentage: float, default=39.612
        Percentage of harvested crop biomass that is dry matter (unitless).
    lignin_dry_matter_percentage: float, default=5.616
        Percentage of dry matter yield that is lignin (unitless).
    yield_nitrogen_fraction: float, default=0.0229376
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00302
        Fraction of wet crop yield that is phosphorus (unitless).

    Notes
    -----
    Tall fescue baleage currently has the same harvest and quality properties as Tall Fescue silage.

    """
    species: str = "tall_fescue_baleage"
    name: str = "tall_fescue baleage"

    storage_type: StorageType = StorageType.BALEAGE


@dataclass(kw_only=True)
class TallFescueHay(TallFescue):
    """
    Crop data class with yield-related properties for Tall Fescue hay.

    Attributes
    ----------
    optimal_harvest_index: float, default=0.85
        Fraction of crop biomass that is harvested in optimal growing conditions (unitless).
    min_harvest_index: float, default=0.37
        Fraction of crop biomass that is harvested in water-stressed growing conditions (unitless).
    dry_matter_percentage: float, default=88.331
        Percentage of harvested crop biomass that is dry matter (unitless).
    lignin_dry_matter_percentage: float, default=4.167
        Percentage of dry matter yield that is lignin (unitless).
    yield_nitrogen_fraction: float, default=0.021248
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00281
        Fraction of wet crop yield that is phosphorus (unitless).

    """
    species: str = "tall_fescue_hay"
    name: str = "tall_fescue hay"

    storage_type: StorageType = StorageType.PROTECTED_TARPED

    optimal_harvest_index: float = 0.85
    min_harvest_index: float = 0.37
    dry_matter_percentage: float = 88.331
    lignin_dry_matter_percentage: float = 4.167
    yield_nitrogen_fraction: float = 0.021248
    yield_phosphorus_fraction: float = 0.00281
