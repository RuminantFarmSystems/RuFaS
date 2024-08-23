from dataclasses import dataclass

from RUFAS.routines.feed_storage.enums import CropCategory, CropType
from RUFAS.routines.feed_storage.feed_manager import StorageType
from RUFAS.routines.field.crop.crop_data import CropData, PlantCategory
from RUFAS.routines.field.crop.crop_enum import CropSpecies


@dataclass(kw_only=True)
class TallFescue(CropData):
    """crop data class with default values for tall fescue"""

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

    root_distribution_param_da: float = 137.0
    root_distribution_param_c: float = -1.144


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
    crude_protein_percent: float, default=13.422
        Percentage of dry matter mass that is dietary crude protein (unitless).
    non_protein_nitrogen: float, default=6.440
        Percentage of dry matter mass that is non-protein nitrogen (unitless).
    starch: float, default=1.936
        Percentage of dry matter mass that is starch (unitless).
    adf: float, default=38.971
        Percentage of dry matter mass that is acid detergent fiber (unitless).
    ndf: float, default=62.067
        Percentage of dry matter mass that is neutral detergent fiber (unitless).
    sugar: float, default=7.29
        Percentage of dry matter mass that is labile carbohydrate (unitless).
    ash: float, default=8.078
        Percentage of dry matter mass that is ash (unitless).
    yield_nitrogen_fraction: float, default=0.0229376
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float, default=0.00302
        Fraction of wet crop yield that is phosphorus (unitless).

    """

    species: CropSpecies = CropSpecies.TALL_FESCUE_SILAGE
    name: str = "tall_fescue silage"

    storage_type: StorageType = StorageType.BUNKER

    optimal_harvest_index: float = 0.90
    min_harvest_index: float = 0.4
    dry_matter_percentage: float = 39.612
    lignin_dry_matter_percentage: float = 5.616
    crude_protein_percent: float = 13.422
    non_protein_nitrogen: float = 6.440
    starch: float = 1.936
    adf: float = 38.971
    ndf: float = 62.067
    sugar: float = 7.29
    ash: float = 8.078
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
    crude_protein_percent: float, default=13.422
        Percentage of dry matter mass that is dietary crude protein (unitless).
    non_protein_nitrogen: float, default=6.440
        Percentage of dry matter mass that is non-protein nitrogen (unitless).
    starch: float, default=1.936
        Percentage of dry matter mass that is starch (unitless).
    adf: float, default=38.971
        Percentage of dry matter mass that is acid detergent fiber (unitless).
    ndf: float, default=62.067
        Percentage of dry matter mass that is neutral detergent fiber (unitless).
    sugar: float, default=7.29
        Percentage of dry matter mass that is labile carbohydrate (unitless).
    ash: float, default=8.078
        Percentage of dry matter mass that is ash (unitless).
    yield_nitrogen_fraction: float, default=0.0229376
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float, default=0.00302
        Fraction of wet crop yield that is phosphorus (unitless).

    Notes
    -----
    Tall fescue baleage currently has the same harvest and quality properties as Tall Fescue silage.

    """

    species: CropSpecies = CropSpecies.TALL_FESCUE_BALEAGE
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
    crude_protein_percent: float, default=13.28
        Percentage of dry matter mass that is dietary crude protein (unitless).
    non_protein_nitrogen: float, default=4.056
        Percentage of dry matter mass that is non-protein nitrogen (unitless).
    starch: float, default=2.217
        Percentage of dry matter mass that is starch (unitless).
    adf: float, default=35.524
        Percentage of dry matter mass that is acid detergent fiber (unitless).
    ndf: float, default=58.007
        Percentage of dry matter mass that is neutral detergent fiber (unitless).
    sugar: float, default=15.235
        Percentage of dry matter mass that is labile carbohydrate (unitless).
    ash: float, default=8.567
        Percentage of dry matter mass that is ash (unitless).
    yield_nitrogen_fraction: float, default=0.021248
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float, default=0.00281
        Fraction of wet crop yield that is phosphorus (unitless).

    """

    species: CropSpecies = CropSpecies.TALL_FESCUE_HAY
    name: str = "tall_fescue hay"

    storage_type: StorageType = StorageType.PROTECTED_TARPED

    optimal_harvest_index: float = 0.85
    min_harvest_index: float = 0.37
    dry_matter_percentage: float = 88.331
    lignin_dry_matter_percentage: float = 4.167
    crude_protein_percent: float = 13.28
    non_protein_nitrogen: float = 4.056
    starch: float = 2.217
    adf: float = 35.524
    ndf: float = 58.007
    sugar: float = 15.235
    ash: float = 8.567
    yield_nitrogen_fraction: float = 0.021248
    yield_phosphorus_fraction: float = 0.00281
