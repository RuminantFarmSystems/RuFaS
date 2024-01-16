from dataclasses import dataclass

from RUFAS.routines.feed_storage.enums import CropCategory, CropType
from RUFAS.routines.feed_storage.feed_manager import StorageType
from RUFAS.routines.field.crop.crop_data import (
    CropData,
    PlantCategory
)


@dataclass(kw_only=True)
class WinterWheat(CropData):
    """
    Crop data class with default values for winter wheat.
    """
    species: str = "winter_wheat"
    name: str = "default winter_wheat"
    plant_code: str = "WWHT"
    scientific_name: str = "Triticum aestivum"
    plant_category: PlantCategory = PlantCategory("cool_annual")
    is_nitrogen_fixer: bool = False

    crop_category: CropCategory = CropCategory.SMALL_GRAIN
    crop_type: CropType = CropType.WHEAT

    minimum_temperature: float = 0.0
    optimal_temperature: float = 18.0

    max_leaf_area_index: float = 4.0
    first_heat_fraction_point: float = 0.05
    first_leaf_fraction_point: float = 0.05
    second_heat_fraction_point: float = 0.45
    second_leaf_fraction_point: float = 0.95
    senescent_heat_fraction: float = 0.90

    light_use_efficiency: float = 30.0

    emergence_nitrogen_fraction: float = 0.0663
    half_mature_nitrogen_fraction: float = 0.0255
    mature_nitrogen_fraction: float = 0.0148
    emergence_phosphorus_fraction: float = 0.0053
    half_mature_phosphorus_fraction: float = 0.0020
    mature_phosphorus_fraction: float = 0.0012

    max_root_depth: float = 1_300


@dataclass(kw_only=True)
class WinterWheatGrain(WinterWheat):
    """
    Crop data class with yield-related properties for Winter Wheat grain.

    Attributes
    ----------
    optimal_harvest_index: float, default=0.5
        Fraction of crop biomass that is harvested in optimal growing conditions (unitless).
    min_harvest_index: float, default=0.25
        Fraction of crop biomass that is harvested in water-stressed growing conditions (unitless).
    dry_matter_percentage: float, default=85.689
        Percentage of harvested crop biomass that is dry matter (unitless).
    lignin_dry_matter_percentage: float, default=1.518
        Percentage of dry matter yield that is lignin (unitless).
    yield_nitrogen_fraction: float, default=0.021576
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00359
        Fraction of wet crop yield that is phosphorus (unitless).

    """
    species: str = "winter_wheat_grain"
    name: str = "winter_wheat grain"

    storage_type: StorageType = StorageType.DRY

    optimal_harvest_index: float = 0.5
    min_harvest_index: float = 0.25
    dry_matter_percentage: float = 85.689
    lignin_dry_matter_percentage: float = 1.518
    yield_nitrogen_fraction: float = 0.021576
    yield_phosphorus_fraction: float = 0.00359


@dataclass(kw_only=True)
class WinterWheatSilage(WinterWheat):
    """
    Crop data class with yield-related properties for Winter Wheat silage.

    Attributes
    ----------
    optimal_harvest_index: float, default=0.9
        Fraction of crop biomass that is harvested in optimal growing conditions (unitless).
    min_harvest_index: float, default=0.6
        Fraction of crop biomass that is harvested in water-stressed growing conditions (unitless).
    dry_matter_percentage: float, default=34.801
        Percentage of harvested crop biomass that is dry matter (unitless).
    lignin_dry_matter_percentage: float, default=4.991
        Percentage of dry matter yield that is lignin (unitless).
    yield_nitrogen_fraction: float, default=0.0171648
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00293
        Fraction of wet crop yield that is phosphorus (unitless).

    """
    species: str = "winter_wheat_silage"
    name: str = "winter_wheat silage"

    storage_type: StorageType = StorageType.BUNKER

    optimal_harvest_index: float = 0.9
    min_harvest_index: float = 0.6
    dry_matter_percentage: float = 34.801
    lignin_dry_matter_percentage: float = 4.991
    yield_nitrogen_fraction: float = 0.0171648
    yield_phosphorus_fraction: float = 0.00293


@dataclass(kw_only=True)
class WinterWheatBaleage(WinterWheatSilage):
    """
    Crop data class with yield-related properties for Winter Wheat silage.

    Attributes
    ----------
    optimal_harvest_index: float, default=0.9
        Fraction of crop biomass that is harvested in optimal growing conditions (unitless).
    min_harvest_index: float, default=0.6
        Fraction of crop biomass that is harvested in water-stressed growing conditions (unitless).
    dry_matter_percentage: float, default=34.801
        Percentage of harvested crop biomass that is dry matter (unitless).
    lignin_dry_matter_percentage: float, default=4.991
        Percentage of dry matter yield that is lignin (unitless).
    yield_nitrogen_fraction: float, default=0.0171648
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00293
        Fraction of wet crop yield that is phosphorus (unitless).

    Notes
    -----
    Winter Wheat baleage currently has the same harvest and quality properties as Winter Wheat silage.

    """
    species: str = "winter_wheat_baleage"
    name: str = "winter_wheat baleage"

    storage_type: StorageType = StorageType.BALEAGE


@dataclass(kw_only=True)
class WinterWheatHay(WinterWheat):
    """
    Crop data class with yield-related properties for Winter Wheat hay.

    Attributes
    ----------
    optimal_harvest_index: float, default=0.85
        Fraction of crop biomass that is harvested in optimal growing conditions (unitless).
    min_harvest_index: float, default=0.55
        Fraction of crop biomass that is harvested in water-stressed growing conditions (unitless).
    dry_matter_percentage: float, default=90.592
        Percentage of harvested crop biomass that is dry matter (unitless).
    lignin_dry_matter_percentage: float, default=4.905
        Percentage of dry matter yield that is lignin (unitless).
    yield_nitrogen_fraction: float, default=0.0158032
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00233
        Fraction of wet crop yield that is phosphorus (unitless).

    """
    species: str = "winter_wheat_hay"
    name: str = "winter_wheat hay"

    storage_type: StorageType = StorageType.PROTECTED_TARPED

    optimal_harvest_index: float = 0.85
    min_harvest_index: float = 0.55
    dry_matter_percentage: float = 90.592
    lignin_dry_matter_percentage: float = 4.905
    yield_nitrogen_fraction: float = 0.0158032
    yield_phosphorus_fraction: float = 0.00233
