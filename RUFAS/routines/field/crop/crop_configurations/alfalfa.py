from dataclasses import dataclass

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
    yield_nitrogen_fraction: float, default=0.0327536
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00351
        Fraction of wet crop yield that is phosphorus (unitless).

    """
    optimal_harvest_index: float = 0.90
    min_harvest_index: float = 0.40
    dry_matter_percentage: float = 42.883
    lignin_dry_matter_percentage: float = 7.419
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
    yield_nitrogen_fraction: float, default=0.0327536
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00351
        Fraction of wet crop yield that is phosphorus (unitless).

    Notes
    -----
    Alfalfa baleage currently has the same harvest and quality properties as Alfalfa silage.

    """


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
    yield_nitrogen_fraction: float, default=0.0250
        Fraction of dry matter crop yield that is nitrogen (unitless).
    yield_phosphorus_fraction: float default=0.00282
        Fraction of wet crop yield that is phosphorus (unitless).

    Notes
    -----
    Alfalfa baleage currently has the same harvest and quality properties as Alfalfa silage.

    """
    optimal_harvest_index: float = 0.85
    min_harvest_index: float = 0.35
    dry_matter_percentage: float = 88.136
    lignin_dry_matter_percentage: float = 6.643
    yield_nitrogen_fraction: float = 0.033192
    yield_phosphorus_fraction: float = 0.00282
