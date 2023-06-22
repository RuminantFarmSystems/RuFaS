from __future__ import annotations

import math
from dataclasses import dataclass, fields


@dataclass(frozen=True)
class NutrientRequestResults:
    nitrogen: float = 0.0
    """Amount of manure nitrogen requested that can be fulfilled (kg). Default to 0."""

    phosphorus: float = 0.0
    """Amount of manure phosphorus requested that can be fulfilled (kg). Default to 0."""

    total_manure_mass: float = 0.0
    """Total amount of manure that can be fulfilled (kg). Default to 0."""

    organic_nitrogen_fraction: float = 0.4
    """Fraction of nitrogen that is present in organic form, between 0 and 1 (unitless). Default to 0.4."""

    inorganic_nitrogen_fraction: float = 0.6
    """Fraction of nitrogen that is present in inorganic form, between 0 and 1 (unitless). Default to 0.6."""

    ammonium_nitrogen_fraction: float = 0.3
    """Fraction of inorganic nitrogen that is present in ammonium form, between 0 and 1 (unitless). Default to 0.3."""

    organic_phosphorus_fraction: float = 0.7
    """Fraction of phosphorus that is present in organic form, between 0 and 1 (unitless). Default to 0.7."""

    inorganic_phosphorus_fraction: float = 0.3
    """Fraction of phosphorus that is present in inorganic form, between 0 and 1 (unitless). Default to 0.3."""

    dry_matter: float = 0.0
    """Amount of dry matter that can be fulfilled (kg). Default to 0."""

    dry_matter_fraction: float = 0.0
    """Fraction of manure that is dry matter, between 0 and 1 (unitless). Default to 0."""

    def __post_init__(self) -> None:
        """
        Validate the dataclass fields.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            For fractional fields, if the value is not between 0 and 1.
            For non-fractional fields, if the value is negative.
            For nitrogen and phosphorus, if the sum of organic and inorganic fractions doesn't equal 1.

        """
        fractional_fields = [f for f in fields(self) if 'fraction' in f.name]
        non_fractional_fields = list(set(fields(self)) - set(fractional_fields))

        for field in fractional_fields:
            if not 0.0 <= getattr(self, field.name) <= 1.0:
                raise ValueError(f'{field.name} must be between 0 and 1.')

        for field in non_fractional_fields:
            if getattr(self, field.name) < 0.0:
                raise ValueError(f'{field.name} must be non-negative.')

        if not math.isclose(self.organic_nitrogen_fraction + self.inorganic_nitrogen_fraction, 1.0, abs_tol=1e-6):
            raise ValueError('Sum of organic and inorganic nitrogen fractions must be 1.')

        if not math.isclose(self.organic_phosphorus_fraction + self.inorganic_phosphorus_fraction, 1.0, abs_tol=1e-6):
            raise ValueError('Sum of organic and inorganic phosphorus fractions must be 1.')
