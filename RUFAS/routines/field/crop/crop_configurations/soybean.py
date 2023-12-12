from dataclasses import dataclass

from RUFAS.routines.field.crop.crop_data import (
    CropData,
    PlantCategory
)


@dataclass(kw_only=True)
class Soybean(CropData):
    """crop data class with default values for soy bean"""
    species: str = "soybean"
    name: str = "default soybean"
    plant_code: str = "SOYB"
    scientific_name: str = "Glycine max"
    plant_category: PlantCategory = PlantCategory("warm_annual_legume")
    is_nitrogen_fixer: bool = True

    minimum_temperature: float = 10.0
    optimal_temperature: float = 25.0

    max_leaf_area_index: float = 3.0
    first_heat_fraction_point: float = 0.15
    first_leaf_fraction_point: float = 0.05
    second_heat_fraction_point: float = 0.50
    second_leaf_fraction_point: float = 0.95
    senescent_heat_fraction: float = 0.90

    light_use_efficiency: float = 25.0

    emergence_nitrogen_fraction: float = 0.0524
    half_mature_nitrogen_fraction: float = 0.0265
    mature_nitrogen_fraction: float = 0.0258
    emergence_phosphorus_fraction: float = 0.0074
    half_mature_phosphorus_fraction: float = 0.0037
    mature_phosphorus_fraction: float = 0.0035

    max_root_depth: float = 1_700


@dataclass(kw_only=True)
class SoybeanGrain(Soybean):
    """
    Crop data class with yield-related properties for Soybean grain.

    Attributes
    ----------
    optimal_harvest_index: float, default=0.35
        Fraction of crop biomass that is harvested in optimal growing conditions (unitless).
    min_harvest_index: float, default=0.26
        Fraction of crop biomass that is harvested in water-stressed growing conditions (unitless).
    dry_matter_percentage: float, default=89.105
        Percentage of harvested crop biomass that is dry matter (unitless).
    lignin_dry_matter_percentage: float, default=1.516
        Percentage of dry matter yield that is lignin (unitless).
    yield_nitrogen_fraction: float, default=0.063968
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00654
        Fraction of wet crop yield that is phosphorus (unitless).

    """
    optimal_harvest_index: float = 0.35
    min_harvest_index: float = 0.26
    dry_matter_percentage: float = 89.105
    lignin_dry_matter_percentage: float = 1.516
    yield_nitrogen_fraction: float = 0.063968
    yield_phosphorus_fraction: float = 0.00654


@dataclass(kw_only=True)
class SoybeanHay(Soybean):
    """
    Crop data class with yield-related properties for Soybean hay.

    Attributes
    ----------
    optimal_harvest_index: float, default=0.90
        Fraction of crop biomass that is harvested in optimal growing conditions (unitless).
    min_harvest_index: float, default=0.54
        Fraction of crop biomass that is harvested in water-stressed growing conditions (unitless).
    dry_matter_percentage: float, default=91.578
        Percentage of harvested crop biomass that is dry matter (unitless).
    lignin_dry_matter_percentage: float, default=7.227
        Percentage of dry matter yield that is lignin (unitless).
    yield_nitrogen_fraction: float, default=0.0321328
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.0028
        Fraction of wet crop yield that is phosphorus (unitless).

    """
    optimal_harvest_index: float = 0.90
    min_harvest_index: float = 0.54
    dry_matter_percentage: float = 91.578
    lignin_dry_matter_percentage: float = 7.227
    yield_nitrogen_fraction: float = 0.0321328
    yield_phosphorus_fraction: float = 0.0028