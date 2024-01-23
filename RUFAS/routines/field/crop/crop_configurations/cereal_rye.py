from dataclasses import dataclass

from RUFAS.routines.feed_storage.enums import CropCategory, CropType
from RUFAS.routines.feed_storage.feed_manager import StorageType
from RUFAS.routines.field.crop.crop_data import (
    CropData,
    PlantCategory
)


@dataclass(kw_only=True)
class CerealRye(CropData):
    """
    Crop data class with default values for cereal rye.
    """
    species: str = "cereal_rye"
    name: str = "default cereal_rye"
    plant_code: str = "RYE"
    scientific_name: str = "Secale cereale"
    plant_category: PlantCategory = PlantCategory("cool_annual")
    is_nitrogen_fixer: bool = False

    crop_category: CropCategory = CropCategory.SMALL_GRAIN
    crop_type: CropType = CropType.RYE

    minimum_temperature: float = 0
    optimal_temperature: float = 12.5

    max_leaf_area_index: float = 4.0
    first_heat_fraction_point: float = 0.15
    first_leaf_fraction_point: float = 0.01
    second_heat_fraction_point: float = 0.50
    second_leaf_fraction_point: float = 0.95
    senescent_heat_fraction: float = 0.80

    light_use_efficiency: float = 35.0

    emergence_nitrogen_fraction: float = 0.0600
    half_mature_nitrogen_fraction: float = 0.0231
    mature_nitrogen_fraction: float = 0.0130
    emergence_phosphorus_fraction: float = 0.0084
    half_mature_phosphorus_fraction: float = 0.0032
    mature_phosphorus_fraction: float = 0.0019

    max_root_depth: float = 1_800


@dataclass(kw_only=True)
class CerealRyeGrain(CerealRye):
    """
    Crop data class with default values for cereal rye grain.

    Attributes
    ----------
    optimal_harvest_index: float, default=0.3
        Fraction of crop biomass that is harvested in optimal growing conditions (unitless).
    min_harvest_index: float, default=0.20
        Fraction of crop biomass that is harvested in water-stressed growing conditions (unitless).
    dry_matter_percentage: float, default=85.962
        Percentage of harvested crop biomass that is dry matter (unitless).
    lignin_dry_matter_percentage: float, default=1.547
        Percentage of dry matter yield that is lignin (unitless).
    crude_protein_percent: float, default=11.804
        Percentage of dry matter mass that is dietary crude protein (unitless).
    non_protein_nitrogen: float, default=3.894
        Percentage of dry matter mass that is non-protein nitrogen (unitless).
    starch: float, default=57.622
        Percentage of dry matter mass that is starch (unitless).
    adf: float, default=5.398
        Percentage of dry matter mass that is acid detergent fiber (unitless).
    ndf: float, default=16.033
        Percentage of dry matter mass that is neutral detergent fiber (unitless).
    sugar: float, default=8.0
        Percentage of dry matter mass that is labile carbohydrate (unitless).
    ash: float, default=2.576
        Percentage of dry matter mass that is ash (unitless).
    yield_nitrogen_fraction: float, default=0.0188864
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00381
        Fraction of dry matter crop yield that is phosphorus (unitless).

    """
    species: str = "cereal_rye_grain"
    name: str = "cereal_rye grain"

    storage_type: StorageType = StorageType.DRY

    optimal_harvest_index: float = 0.3
    min_harvest_index: float = 0.20
    dry_matter_percentage: float = 85.962
    lignin_dry_matter_percentage: float = 1.547
    crude_protein_percent: float = 11.804
    non_protein_nitrogen: float = 3.894
    starch: float = 57.622
    adf: float = 5.398
    ndf: float = 16.033
    sugar: float = 8.0
    ash: float = 2.576
    yield_nitrogen_fraction: float = 0.0188864
    yield_phosphorus_fraction: float = 0.00381


@dataclass(kw_only=True)
class CerealRyeSilage(CerealRye):
    """
    Crop data class with default values for cereal rye silage.

    Attributes
    ----------
    optimal_harvest_index: float, default=0.90
        Fraction of crop biomass that is harvested in optimal growing conditions (unitless).
    min_harvest_index: float, default=0.68
        Fraction of crop biomass that is harvested in water-stressed growing conditions (unitless).
    dry_matter_percentage: float, default=34.881
        Percentage of harvested crop biomass that is dry matter (unitless).
    lignin_dry_matter_percentage: float, default=4.932
        Percentage of dry matter yield that is lignin (unitless).
    crude_protein_percent: float, default=14.434
        Percentage of dry matter mass that is dietary crude protein (unitless).
    non_protein_nitrogen: float, default=8.904
        Percentage of dry matter mass that is non-protein nitrogen (unitless).
    starch: float, default=1.477
        Percentage of dry matter mass that is starch (unitless).
    adf: float, default=38.282
        Percentage of dry matter mass that is acid detergent fiber (unitless).
    ndf: float, default=58.026
        Percentage of dry matter mass that is neutral detergent fiber (unitless).
    sugar: float, default=8.761
        Percentage of dry matter mass that is labile carbohydrate (unitless).
    ash: float, default=10.275
        Percentage of dry matter mass that is ash (unitless).
    yield_nitrogen_fraction: float, default=0.0230944
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00371
        Fraction of dry matter crop yield that is phosphorus (unitless).

    """
    species: str = "cereal_rye_silage"
    name: str = "cereal_rye silage"

    storage_type: StorageType = StorageType.BUNKER

    optimal_harvest_index: float = 0.90
    min_harvest_index: float = 0.68
    dry_matter_percentage: float = 34.881
    lignin_dry_matter_percentage: float = 4.932
    crude_protein_percent: float = 14.434
    non_protein_nitrogen: float = 8.904
    starch: float = 1.477
    adf: float = 38.282
    ndf: float = 58.026
    sugar: float = 8.761
    ash: float = 10.275
    yield_nitrogen_fraction: float = 0.0230944
    yield_phosphorus_fraction: float = 0.00371


@dataclass(kw_only=True)
class CerealRyeBaleage(CerealRyeSilage):
    """
    Crop data class with default values for cereal rye baleage.

    Attributes
    ----------
    optimal_harvest_index: float, default=0.90
        Fraction of crop biomass that is harvested in optimal growing conditions (unitless).
    min_harvest_index: float, default=0.68
        Fraction of crop biomass that is harvested in water-stressed growing conditions (unitless).
    dry_matter_percentage: float, default=34.881
        Percentage of harvested crop biomass that is dry matter (unitless).
    lignin_dry_matter_percentage: float, default=4.932
        Percentage of dry matter yield that is lignin (unitless).
    crude_protein_percent: float, default=14.434
        Percentage of dry matter mass that is dietary crude protein (unitless).
    non_protein_nitrogen: float, default=8.904
        Percentage of dry matter mass that is non-protein nitrogen (unitless).
    starch: float, default=1.477
        Percentage of dry matter mass that is starch (unitless).
    adf: float, default=38.282
        Percentage of dry matter mass that is acid detergent fiber (unitless).
    ndf: float, default=58.026
        Percentage of dry matter mass that is neutral detergent fiber (unitless).
    sugar: float, default=8.761
        Percentage of dry matter mass that is labile carbohydrate (unitless).
    ash: float, default=10.275
        Percentage of dry matter mass that is ash (unitless).
    yield_nitrogen_fraction: float, default=0.0230944
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00371
        Fraction of dry matter crop yield that is phosphorus (unitless).

    Notes
    -----
    Cereal rye baleage has the same harvest parameters as cereal rye silage.

    """
    species: str = "cereal_rye_baleage"
    name: str = "cereal_rye baleage"

    storage_type: StorageType = StorageType.BALEAGE


@dataclass(kw_only=True)
class CerealRyeHay(CropData):
    """
    Crop data class with default values for cereal rye grain.

    Attributes
    ----------
    optimal_harvest_index: float, default=0.50
        Fraction of crop biomass that is harvested in optimal growing conditions (unitless).
    min_harvest_index: float, default=0.30
        Fraction of crop biomass that is harvested in water-stressed growing conditions (unitless).
    dry_matter_percentage: float, default=86.0907
        Percentage of harvested crop biomass that is dry matter (unitless).
    lignin_dry_matter_percentage: float, default=6.205
        Percentage of dry matter yield that is lignin (unitless).
    crude_protein_percent: float, default=7.62
        Percentage of dry matter mass that is dietary crude protein (unitless).
    non_protein_nitrogen: float, default=2.746
        Percentage of dry matter mass that is non-protein nitrogen (unitless).
    starch: float, default=2.014
        Percentage of dry matter mass that is starch (unitless).
    adf: float, default=42.683
        Percentage of dry matter mass that is acid detergent fiber (unitless).
    ndf: float, default=66.825
        Percentage of dry matter mass that is neutral detergent fiber (unitless).
    sugar: float, default=12.73
        Percentage of dry matter mass that is labile carbohydrate (unitless).
    ash: float, default=6.293
        Percentage of dry matter mass that is ash (unitless).
    yield_nitrogen_fraction: float, default=0.0140
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00309
        Fraction of dry matter crop yield that is phosphorus (unitless).

    """
    species: str = "cereal_rye_hay"
    name: str = "cereal_rye hay"

    storage_type: StorageType = StorageType.PROTECTED_TARPED

    optimal_harvest_index: float = 0.85
    min_harvest_index: float = 0.64
    dry_matter_percentage: float = 92.705
    lignin_dry_matter_percentage: float = 6.205
    crude_protein_percent: float = 7.62
    non_protein_nitrogen: float = 2.746
    starch: float = 2.014
    adf: float = 42.683
    ndf: float = 66.825
    sugar: float = 12.73
    ash: float = 6.293
    yield_nitrogen_fraction: float = 0.012192
    yield_phosphorus_fraction: float = 0.00179
