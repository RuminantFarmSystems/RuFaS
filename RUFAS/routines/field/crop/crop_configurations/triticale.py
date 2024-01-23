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
    crude_protein_percent: float, default=12.053
        Percentage of dry matter mass that is dietary crude protein (unitless).
    non_protein_nitrogen: float, default=3.774
        Percentage of dry matter mass that is non-protein nitrogen (unitless).
    starch: float, default=61.218
        Percentage of dry matter mass that is starch (unitless).
    adf: float, default=4.422
        Percentage of dry matter mass that is acid detergent fiber (unitless).
    ndf: float, default=14.121
        Percentage of dry matter mass that is neutral detergent fiber (unitless).
    sugar: float, default=8.014
        Percentage of dry matter mass that is labile carbohydrate (unitless).
    ash: float, default=2.084
        Percentage of dry matter mass that is ash (unitless).
    yield_nitrogen_fraction: float, default=0.0192848
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float, default=0.00348
        Fraction of wet crop yield that is phosphorus (unitless).

    """
    species: str = "triticale_grain"
    name: str = "triticale grain"

    storage_type: StorageType = StorageType.DRY

    optimal_harvest_index: float = 0.3
    min_harvest_index: float = 0.2
    dry_matter_percentage: float = 88.374
    lignin_dry_matter_percentage: float = 1.786
    crude_protein_percent: float = 12.053
    non_protein_nitrogen: float = 3.774
    starch: float = 61.218
    adf: float = 4.422
    ndf: float = 14.121
    sugar: float = 8.014
    ash: float = 2.084
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
    crude_protein_percent: float, default=17.784
        Percentage of dry matter mass that is dietary crude protein (unitless).
    non_protein_nitrogen: float, default=11.876
        Percentage of dry matter mass that is non-protein nitrogen (unitless).
    starch: float, default=1.486
        Percentage of dry matter mass that is starch (unitless).
    adf: float, default=34.78
        Percentage of dry matter mass that is acid detergent fiber (unitless).
    ndf: float, default=52.202
        Percentage of dry matter mass that is neutral detergent fiber (unitless).
    sugar: float, default=7.548
        Percentage of dry matter mass that is labile carbohydrate (unitless).
    ash: float, default=12.449
        Percentage of dry matter mass that is ash (unitless).
    yield_nitrogen_fraction: float, default=0.0284544
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float, default=0.00409
        Fraction of wet crop yield that is phosphorus (unitless).

    """
    species: str = "triticale_silage"
    name: str = "triticale silage"

    storage_type: StorageType = StorageType.BUNKER

    optimal_harvest_index: float = 0.9
    min_harvest_index: float = 0.7
    dry_matter_percentage: float = 33.281
    lignin_dry_matter_percentage: float = 4.313
    crude_protein_percent: float = 17.784
    non_protein_nitrogen: float = 11.876
    starch: float = 1.486
    adf: float = 34.78
    ndf: float = 52.202
    sugar: float = 7.548
    ash: float = 12.449
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
    crude_protein_percent: float, default=17.784
        Percentage of dry matter mass that is dietary crude protein (unitless).
    non_protein_nitrogen: float, default=11.876
        Percentage of dry matter mass that is non-protein nitrogen (unitless).
    starch: float, default=1.486
        Percentage of dry matter mass that is starch (unitless).
    adf: float, default=34.78
        Percentage of dry matter mass that is acid detergent fiber (unitless).
    ndf: float, default=52.202
        Percentage of dry matter mass that is neutral detergent fiber (unitless).
    sugar: float, default=7.548
        Percentage of dry matter mass that is labile carbohydrate (unitless).
    ash: float, default=12.449
        Percentage of dry matter mass that is ash (unitless).
    yield_nitrogen_fraction: float, default=0.0284544
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float, default=0.00409
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
    crude_protein_percent: float, default=10.329
        Percentage of dry matter mass that is dietary crude protein (unitless).
    non_protein_nitrogen: float, default=4.831
        Percentage of dry matter mass that is non-protein nitrogen (unitless).
    starch: float, default=3.061
        Percentage of dry matter mass that is starch (unitless).
    adf: float, default=38.257
        Percentage of dry matter mass that is acid detergent fiber (unitless).
    ndf: float, default=59.959
        Percentage of dry matter mass that is neutral detergent fiber (unitless).
    sugar: float, default=14.015
        Percentage of dry matter mass that is labile carbohydrate (unitless).
    ash: float, default=8.485
        Percentage of dry matter mass that is ash (unitless).
    yield_nitrogen_fraction: float, default=0.0165264
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float, default=0.00236
        Fraction of wet crop yield that is phosphorus (unitless).

    """
    species: str = "triticale_hay"
    name: str = "triticale hay"

    storage_type: StorageType = StorageType.PROTECTED_TARPED

    optimal_harvest_index: float = 0.85
    min_harvest_index: float = 0.65
    dry_matter_percentage: float = 91.019
    lignin_dry_matter_percentage: float = 4.844
    crude_protein_percent: float = 10.329
    non_protein_nitrogen: float = 4.831
    starch: float = 3.061
    adf: float = 38.257
    ndf: float = 59.959
    sugar: float = 14.015
    ash: float = 8.485
    yield_nitrogen_fraction: float = 0.0165264
    yield_phosphorus_fraction: float = 0.00236
