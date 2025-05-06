from dataclasses import dataclass
from typing import Optional

from RUFAS.biophysical.animal.data_types.bedding_types import BeddingType


@dataclass
class BeddingConfig:
    bedding_mass_per_day: float
    """Quantity of bedding required per animal per day (:math:`kg/animal/day`)."""

    bedding_density: float
    """Density of the bedding (:math:`kg/m^3`)."""

    bedding_dry_matter_content: float
    """
    Dry matter content in the bedding (unitless).
    Value should be in the range :math:`[0.7 - 1.0]`.
    """

    bedding_cleaned_fraction: float
    """
    Fraction of bedding that is removed from the barn (unitless).
    Value should be in the range :math:`[0.7 - 1.0]`.
    """

    bedding_carbon_fraction: float
    """
    Fraction of bedding that is composed of carbon (unitless).
    Value should be in the range :math:`[0.0 - 1.0]`.
    """

    bedding_phosphorus_content: float
    """Quantity of phosphorus in the bedding (kg)."""

    bedding_type: BeddingType
    """Type of bedding."""

    sand_removal_efficiency: Optional[float]
    """
    Efficiency of removing sand from the bedding (unitless).
    Value should be in the range :math:`[0.7 - 1.0]`.
    """
