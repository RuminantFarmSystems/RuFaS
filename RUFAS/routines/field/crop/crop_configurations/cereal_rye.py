from dataclasses import dataclass

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
    yield_nitrogen_fraction: float, default=0.0188864
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00381
        Fraction of dry matter crop yield that is phosphorus (unitless).

    """
    optimal_harvest_index: float = 0.3
    min_harvest_index: float = 0.20
    dry_matter_percentage: float = 85.962
    lignin_dry_matter_percentage: float = 1.547
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
    yield_nitrogen_fraction: float, default=0.0230944
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00371
        Fraction of dry matter crop yield that is phosphorus (unitless).

    """
    optimal_harvest_index: float = 0.90
    min_harvest_index: float = 0.68
    dry_matter_percentage: float = 34.881
    lignin_dry_matter_percentage: float = 4.932
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
    yield_nitrogen_fraction: float, default=0.0230944
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00371
        Fraction of dry matter crop yield that is phosphorus (unitless).

    Notes
    -----
    Cereal rye baleage has the same harvest parameters as cereal rye silage.

    """


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
    yield_nitrogen_fraction: float, default=0.0140
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00309
        Fraction of dry matter crop yield that is phosphorus (unitless).

    """
    optimal_harvest_index: float = 0.85
    min_harvest_index: float = 0.64
    dry_matter_percentage: float = 92.705
    lignin_dry_matter_percentage: float = 6.205
    yield_nitrogen_fraction: float = 0.012192
    yield_phosphorus_fraction: float = 0.00179
