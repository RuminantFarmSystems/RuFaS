from dataclasses import dataclass

from RUFAS.routines.feed_storage.enums import CropCategory, CropType
from RUFAS.routines.feed_storage.feed_manager import StorageType
from RUFAS.routines.field.crop.crop_data import (
    CropData,
    PlantCategory
)


@dataclass(kw_only=True)
class Alfalfa(CropData):
    """
    Crop data class with default values for alfalfa.
    """
    species: str = "alfalfa"
    name: str = "default alfalfa"
    plant_code: str = "ALFA"
    scientific_name: str = "Medicago sativa"
    plant_category: PlantCategory = PlantCategory("perennial_legume")
    is_nitrogen_fixer: bool = True

    crop_category: CropCategory = CropCategory.ALFALFA
    crop_type: CropType = CropType.ALFALFA

    minimum_temperature: float = 4.0
    optimal_temperature: float = 25.0

    max_leaf_area_index: float = 4.0
    first_heat_fraction_point: float = 0.15
    first_leaf_fraction_point: float = 0.01
    second_heat_fraction_point: float = 0.50
    second_leaf_fraction_point: float = 0.95
    senescent_heat_fraction: float = 0.90

    light_use_efficiency: float = 20.0

    emergence_nitrogen_fraction: float = 0.0417
    half_mature_nitrogen_fraction: float = 0.0290
    mature_nitrogen_fraction: float = 0.0200
    emergence_phosphorus_fraction: float = 0.0035
    half_mature_phosphorus_fraction: float = 0.0028
    mature_phosphorus_fraction: float = 0.0020

    max_root_depth: float = 3_000


@dataclass(kw_only=True)
class AlfalfaSilage(Alfalfa):
    """
    Crop data class with yield-related properties for Alfalfa silage.

    Attributes
    ----------
    optimal_harvest_index: float, default=0.90
        Fraction of crop biomass that is harvested in optimal growing conditions (unitless).
    min_harvest_index: float, default=0.90
        Fraction of crop biomass that is harvested in water-stressed growing conditions (unitless).
    dry_matter_percentage: float, default=42.883
        Percentage of harvested crop biomass that is dry matter (unitless).
    lignin_dry_matter_percentage: float, default=7.419
        Percentage of dry matter yield that is lignin (unitless).
    crude_protein_percent: float, default=20.471
        Percentage of dry matter mass that is dietary crude protein (unitless).
    non_protein_nitrogen: float, default=10.098
        Percentage of dry matter mass that is non-protein nitrogen (unitless).
    starch: float, default=1.973
        Percentage of dry matter mass that is starch (unitless).
    adf: float, default=33.683
        Percentage of dry matter mass that is acid detergent fiber (unitless).
    ndf: float, default=43.195
        Percentage of dry matter mass that is neutral detergent fiber (unitless).
    sugar: float, default=6.274
        Percentage of dry matter mass that is labile carbohydrate (unitless).
    ash: float, default=10.597
        Percentage of dry matter mass that is ash (unitless).
    yield_nitrogen_fraction: float, default=0.0327536
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float, default=0.00351
        Fraction of wet crop yield that is phosphorus (unitless).

    """
    species: str = "alfalfa_silage"
    name: str = "alfalfa silage"

    storage_type: StorageType = StorageType.BUNKER

    optimal_harvest_index: float = 0.90
    min_harvest_index: float = 0.40
    dry_matter_percentage: float = 42.883
    lignin_dry_matter_percentage: float = 7.419
    crude_protein_percent: float = 20.471
    non_protein_nitrogen: float = 10.098
    starch: float = 1.973
    adf: float = 33.683
    ndf: float = 43.195
    sugar: float = 6.274
    ash: float = 10.597
    yield_nitrogen_fraction: float = 0.0327536
    yield_phosphorus_fraction: float = 0.00351


@dataclass(kw_only=True)
class AlfalfaBaleage(AlfalfaSilage):
    """
    Crop data class with yield-related properties for Alfalfa baleage.

    Attributes
    ----------
    optimal_harvest_index: float, default=0.90
        Fraction of crop biomass that is harvested in optimal growing conditions (unitless).
    min_harvest_index: float, default=0.90
        Fraction of crop biomass that is harvested in water-stressed growing conditions (unitless).
    dry_matter_percentage: float, default=42.883
        Percentage of harvested crop biomass that is dry matter (unitless).
    lignin_dry_matter_percentage: float, default=7.419
        Percentage of dry matter yield that is lignin (unitless).
    crude_protein_percent: float, default=20.471
        Percentage of dry matter mass that is dietary crude protein (unitless).
    non_protein_nitrogen: float, default=10.098
        Percentage of dry matter mass that is non-protein nitrogen (unitless).
    starch: float, default=1.973
        Percentage of dry matter mass that is starch (unitless).
    adf: float, default=33.683
        Percentage of dry matter mass that is acid detergent fiber (unitless).
    ndf: float, default=43.195
        Percentage of dry matter mass that is neutral detergent fiber (unitless).
    sugar: float, default=6.274
        Percentage of dry matter mass that is labile carbohydrate (unitless).
    ash: float, default=10.597
        Percentage of dry matter mass that is ash (unitless).
    yield_nitrogen_fraction: float, default=0.0327536
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float, default=0.00351
        Fraction of wet crop yield that is phosphorus (unitless).

    Notes
    -----
    Alfalfa baleage currently has the same harvest and quality properties as Alfalfa silage.

    """
    species: str = "alfalfa_baleage"
    name: str = "alfalfa baleage"

    storage_type: StorageType = StorageType.BALEAGE


@dataclass(kw_only=True)
class AlfalfaHay(Alfalfa):
    """
    Crop data class with yield-related properties for Alfalfa hay.

    Attributes
    ----------
    optimal_harvest_index: float, default=0.85
        Fraction of crop biomass that is harvested in optimal growing conditions (unitless).
    min_harvest_index: float, default=0.35
        Fraction of crop biomass that is harvested in water-stressed growing conditions (unitless).
    dry_matter_percentage: float, default=42.883
        Percentage of harvested crop biomass that is dry matter (unitless).
    lignin_dry_matter_percentage: float, default=6.643
        Percentage of dry matter yield that is lignin (unitless).
    crude_protein_percent: float, default=20.745
        Percentage of dry matter mass that is dietary crude protein (unitless).
    non_protein_nitrogen: float, default=7.18
        Percentage of dry matter mass that is non-protein nitrogen (unitless).
    starch: float, default=1.513
        Percentage of dry matter mass that is starch (unitless).
    adf: float, default=32.073
        Percentage of dry matter mass that is acid detergent fiber (unitless).
    ndf: float, default=41.109
        Percentage of dry matter mass that is neutral detergent fiber (unitless).
    sugar: float, default=8.97
        Percentage of dry matter mass that is labile carbohydrate (unitless).
    ash: float, default=10.762
        Percentage of dry matter mass that is ash (unitless).
    yield_nitrogen_fraction: float, default=0.0250
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float, default=0.00282
        Fraction of wet crop yield that is phosphorus (unitless).

    Notes
    -----
    Alfalfa baleage currently has the same harvest and quality properties as Alfalfa silage.

    """
    species: str = "alfalfa_hay"
    name: str = "alfalfa hay"

    storage_type: StorageType = StorageType.PROTECTED_TARPED

    optimal_harvest_index: float = 0.85
    min_harvest_index: float = 0.35
    dry_matter_percentage: float = 88.136
    lignin_dry_matter_percentage: float = 6.643
    crude_protein_percent: float = 20.745
    non_protein_nitrogen: float = 7.18
    starch: float = 1.513
    adf: float = 32.073
    ndf: float = 41.109
    sugar: float = 8.97
    ash: float = 10.762
    yield_nitrogen_fraction: float = 0.033192
    yield_phosphorus_fraction: float = 0.00282
