from dataclasses import dataclass

from RUFAS.routines.feed_storage.enums import CropCategory, CropType
from RUFAS.routines.feed_storage.feed_manager import StorageType
from RUFAS.routines.field.crop.crop_data import (
    CropData,
    PlantCategory
)


@dataclass(kw_only=True)
class Triticale(CropData):
    """
    Crop data class with default values for triticale.

    Notes
    -------
    We use the closest analog data available which is the Durum Wheat data.

    """
    species: str = "triticale"
    name: str = "default triticale"
    plant_code: str = "DWHT"
    scientific_name: str = "Triticum durum"
    plant_category: PlantCategory = PlantCategory("cool_annual")
    is_nitrogen_fixer: bool = False

    crop_category: CropCategory = CropCategory.SMALL_GRAIN
    crop_type: CropType = CropType.WHEAT

    minimum_temperature: float = 0.0
    optimal_temperature: float = 15.0

    max_leaf_area_index: float = 4.0
    first_heat_fraction_point: float = 0.15
    first_leaf_fraction_point: float = 0.01
    second_heat_fraction_point: float = 0.50
    second_leaf_fraction_point: float = 0.95
    senescent_heat_fraction: float = 0.90

    light_use_efficiency: float = 30.0

    emergence_nitrogen_fraction: float = 0.0600
    half_mature_nitrogen_fraction: float = 0.0231
    mature_nitrogen_fraction: float = 0.0130
    emergence_phosphorus_fraction: float = 0.0084
    half_mature_phosphorus_fraction: float = 0.0032
    mature_phosphorus_fraction: float = 0.0019

    max_root_depth: float = 2_000


@dataclass(kw_only=True)
class TriticaleGrain(Triticale):
    """
    Crop data class with yield-related properties for Triticale grain.

    Attributes
    ----------
    optimal_harvest_index: float, default=0.3
        Fraction of crop biomass that is harvested in optimal growing conditions (unitless).
    min_harvest_index: float, default=0.2
        Fraction of crop biomass that is harvested in water-stressed growing conditions (unitless).
    dry_matter_percentage: float, default=88.374
        Percentage of harvested crop biomass that is dry matter (unitless).
    lignin_dry_matter_percentage: float, default=1.786
        Percentage of dry matter yield that is lignin (unitless).
    yield_nitrogen_fraction: float, default=0.0192848
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00348
        Fraction of wet crop yield that is phosphorus (unitless).

    """
    species: str = "triticale_grain"
    name: str = "triticale grain"

    storage_type: StorageType = StorageType.DRY

    optimal_harvest_index: float = 0.3
    min_harvest_index: float = 0.2
    dry_matter_percentage: float = 88.374
    lignin_dry_matter_percentage: float = 1.786
    yield_nitrogen_fraction: float = 0.0192848
    yield_phosphorus_fraction: float = 0.00348


@dataclass(kw_only=True)
class TriticaleSilage(Triticale):
    """
    Crop data class with yield-related properties for Triticale silage.

    Attributes
    ----------
    optimal_harvest_index: float, default=0.9
        Fraction of crop biomass that is harvested in optimal growing conditions (unitless).
    min_harvest_index: float, default=0.7
        Fraction of crop biomass that is harvested in water-stressed growing conditions (unitless).
    dry_matter_percentage: float, default=33.281
        Percentage of harvested crop biomass that is dry matter (unitless).
    lignin_dry_matter_percentage: float, default=4.313
        Percentage of dry matter yield that is lignin (unitless).
    yield_nitrogen_fraction: float, default=0.0284544
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00409
        Fraction of wet crop yield that is phosphorus (unitless).

    """
    species: str = "triticale_silage"
    name: str = "triticale silage"

    storage_type: StorageType = StorageType.BUNKER

    optimal_harvest_index: float = 0.9
    min_harvest_index: float = 0.7
    dry_matter_percentage: float = 33.281
    lignin_dry_matter_percentage: float = 4.313
    yield_nitrogen_fraction: float = 0.0284544
    yield_phosphorus_fraction: float = 0.00409


@dataclass(kw_only=True)
class TriticaleBaleage(TriticaleSilage):
    """
    Crop data class with yield-related properties for Triticale baleage.

    Attributes
    ----------
    optimal_harvest_index: float, default=0.9
        Fraction of crop biomass that is harvested in optimal growing conditions (unitless).
    min_harvest_index: float, default=0.7
        Fraction of crop biomass that is harvested in water-stressed growing conditions (unitless).
    dry_matter_percentage: float, default=33.281
        Percentage of harvested crop biomass that is dry matter (unitless).
    lignin_dry_matter_percentage: float, default=4.313
        Percentage of dry matter yield that is lignin (unitless).
    yield_nitrogen_fraction: float, default=0.0284544
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00409
        Fraction of wet crop yield that is phosphorus (unitless).

    Notes
    -----
    Triticale baleage currently has the same harvest and quality properties as Triticale silage.

    """
    species: str = "triticale_baleage"
    name: str = "triticale baleage"

    storage_type: StorageType = StorageType.BALEAGE


@dataclass(kw_only=True)
class TriticaleHay(Triticale):
    """
    Crop data class with yield-related properties for Triticale hay.

    Attributes
    ----------
    optimal_harvest_index: float, default=0.85
        Fraction of crop biomass that is harvested in optimal growing conditions (unitless).
    min_harvest_index: float, default=0.65
        Fraction of crop biomass that is harvested in water-stressed growing conditions (unitless).
    dry_matter_percentage: float, default=91.019
        Percentage of harvested crop biomass that is dry matter (unitless).
    lignin_dry_matter_percentage: float, default=4.844
        Percentage of dry matter yield that is lignin (unitless).
    yield_nitrogen_fraction: float, default=0.0165264
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00236
        Fraction of wet crop yield that is phosphorus (unitless).

    """
    species: str = "triticale_hay"
    name: str = "triticale hay"

    storage_type: StorageType = StorageType.PROTECTED_TARPED

    optimal_harvest_index: float = 0.85
    min_harvest_index: float = 0.65
    dry_matter_percentage: float = 91.019
    lignin_dry_matter_percentage: float = 4.844
    yield_nitrogen_fraction: float = 0.0165264
    yield_phosphorus_fraction: float = 0.00236
