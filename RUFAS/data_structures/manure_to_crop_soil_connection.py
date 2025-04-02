from typing import NamedTuple, Optional
from dataclasses import dataclass, fields
from RUFAS.data_structures.events import ManureEvent
from RUFAS.data_structures.manure_types import ManureType
import math


@dataclass(kw_only=True, frozen=True)
class NutrientRequest:
    """A class that represents a request for nutrients from the crop and soil module."""

    nitrogen: float = 0.0
    """Amount of manure nitrogen requested, kg."""

    phosphorus: float = 0.0
    """Amount of manure phosphorus requested, kg."""

    manure_type: ManureType
    """The type of manure."""

    use_supplemental_manure: bool
    """Whether to use supplemental manure if the request cannot be fulfilled by on-farm manure."""

    def __post_init__(self) -> None:
        """
        Validate the dataclass fields.

        Raises
        ------
        ValueError
            If any field is negative.
            If no fields are positive.
            If the manure type provided is not a valid ManureType.

        """
        for field in fields(self):
            value = getattr(self, field.name)
            if field.name != "manure_type" and value < 0:
                raise ValueError(f"Field {field.name} must be non-negative.")
            if field.name == "manure_type" and not isinstance(value, ManureType):
                raise ValueError(f"Field {field.name} must be an instance of ManureType.")

        if any(
            isinstance(getattr(self, field.name), (int, float)) and getattr(self, field.name) > 0.0
            for field in fields(self)
        ):
            return
        else:
            raise ValueError("At least one nutrient must be requested and positive.")


@dataclass(frozen=True)
class NutrientRequestResults:
    """A dataclass to store the results of the nutrient request calculations."""

    nitrogen: float = 0.0
    """Amount of manure nitrogen requested that can be fulfilled (kg). Default to 0."""

    phosphorus: float = 0.0
    """Amount of manure phosphorus requested that can be fulfilled (kg). Default to 0."""

    total_manure_mass: float = 0.0
    """Total amount of manure that can be fulfilled (kg). Default to 0."""

    organic_nitrogen_fraction: float = 0.7
    """Fraction of nitrogen that is present in organic form, between 0 and 1 (unitless). Default to 0.7."""

    inorganic_nitrogen_fraction: float = 0.3
    """Fraction of nitrogen that is present in inorganic form, between 0 and 1 (unitless). Default to 0.3."""

    ammonium_nitrogen_fraction: float = 1.0
    """Fraction of `inorganic` nitrogen that is present in ammonium form, between 0 and 1 (unitless). Default to 1.0."""

    organic_phosphorus_fraction: float = 0.5
    """Fraction of phosphorus that is present in organic form, between 0 and 1 (unitless). Default to 0.5."""

    inorganic_phosphorus_fraction: float = 0.5
    """Fraction of phosphorus that is present in inorganic form, between 0 and 1 (unitless). Default to 0.5."""

    dry_matter: float = 0.0
    """Amount of dry matter that can be fulfilled (kg). Default to 0."""

    dry_matter_fraction: float = 0.0
    """Fraction of manure that is dry matter, between 0 and 1 (unitless). Default to 0."""

    def __post_init__(self) -> None:
        """
        Validate the dataclass fields.

        Raises
        ------
        ValueError
            For fractional fields, if the value is not between 0 and 1.
            For non-fractional fields, if the value is negative.
            For nitrogen and phosphorus, if the sum of organic and inorganic fractions doesn't equal 1.

        """
        fractional_fields = [f for f in fields(self) if "fraction" in f.name]
        non_fractional_fields = list(set(fields(self)) - set(fractional_fields))

        for field in fractional_fields:
            if not 0.0 <= getattr(self, field.name) <= 1.0:
                raise ValueError(f"{field.name} must be between 0 and 1.")

        for field in non_fractional_fields:
            if getattr(self, field.name) < 0.0:
                raise ValueError(f"{field.name} must be non-negative.")

        if not math.isclose(
            self.organic_nitrogen_fraction + self.inorganic_nitrogen_fraction,
            1.0,
            abs_tol=1e-6,
        ):
            raise ValueError("Sum of organic and inorganic nitrogen fractions must be 1.")

        if not math.isclose(
            self.organic_phosphorus_fraction + self.inorganic_phosphorus_fraction,
            1.0,
            abs_tol=1e-6,
        ):
            raise ValueError("Sum of organic and inorganic phosphorus fractions must be 1.")

    def __add__(self, other: "NutrientRequestResults") -> "NutrientRequestResults":
        """
        Add two NutrientRequestResults objects together.

        Parameters
        ----------
        other : NutrientRequestResults
            The other NutrientRequestResults object to add.

        Returns
        -------
        NutrientRequestResults
            A new NutrientRequestResults object with the sums of the fields.

        """
        combined_total_nitrogen = self.nitrogen + other.nitrogen
        combined_total_phosphorus = self.phosphorus + other.phosphorus
        combined_total_manure_mass = self.total_manure_mass + other.total_manure_mass
        combined_total_dry_matter = self.dry_matter + other.dry_matter

        if combined_total_nitrogen > 0:
            self_nitrogen_contribution = self.nitrogen / combined_total_nitrogen
            other_nitrogen_contribution = other.nitrogen / combined_total_nitrogen

            combined_organic_nitrogen_fraction = (
                self.organic_nitrogen_fraction * self_nitrogen_contribution
                + other.organic_nitrogen_fraction * other_nitrogen_contribution
            )
            combined_inorganic_nitrogen_fraction = (
                self.inorganic_nitrogen_fraction * self_nitrogen_contribution
                + other.inorganic_nitrogen_fraction * other_nitrogen_contribution
            )

            combined_total_inorganic_nitrogen = (
                self.inorganic_nitrogen_fraction * self.nitrogen + other.inorganic_nitrogen_fraction * other.nitrogen
            )

            if combined_total_inorganic_nitrogen > 0:
                self_inorganic_contribution = (
                    self.inorganic_nitrogen_fraction * self.nitrogen / combined_total_inorganic_nitrogen
                )
                other_inorganic_contribution = (
                    other.inorganic_nitrogen_fraction * other.nitrogen / combined_total_inorganic_nitrogen
                )

                combined_ammonium_nitrogen_fraction = (
                    self.ammonium_nitrogen_fraction * self_inorganic_contribution
                    + other.ammonium_nitrogen_fraction * other_inorganic_contribution
                )
            else:
                combined_ammonium_nitrogen_fraction = self.ammonium_nitrogen_fraction
        else:
            combined_organic_nitrogen_fraction = self.organic_nitrogen_fraction
            combined_inorganic_nitrogen_fraction = self.inorganic_nitrogen_fraction
            combined_ammonium_nitrogen_fraction = self.ammonium_nitrogen_fraction

        if combined_total_phosphorus > 0:
            combined_organic_phosphorus_fraction = (
                self.organic_phosphorus_fraction * self.phosphorus
                + other.organic_phosphorus_fraction * other.phosphorus
            ) / combined_total_phosphorus
            combined_inorganic_phosphorus_fraction = (
                self.inorganic_phosphorus_fraction * self.phosphorus
                + other.inorganic_phosphorus_fraction * other.phosphorus
            ) / combined_total_phosphorus
        else:
            combined_organic_phosphorus_fraction = self.organic_phosphorus_fraction
            combined_inorganic_phosphorus_fraction = self.inorganic_phosphorus_fraction

        if combined_total_manure_mass > 0:
            combined_dry_matter_fraction = combined_total_dry_matter / combined_total_manure_mass
        else:
            combined_dry_matter_fraction = self.dry_matter_fraction

        return NutrientRequestResults(
            nitrogen=combined_total_nitrogen,
            phosphorus=combined_total_phosphorus,
            total_manure_mass=combined_total_manure_mass,
            organic_nitrogen_fraction=combined_organic_nitrogen_fraction,
            inorganic_nitrogen_fraction=combined_inorganic_nitrogen_fraction,
            ammonium_nitrogen_fraction=combined_ammonium_nitrogen_fraction,
            organic_phosphorus_fraction=combined_organic_phosphorus_fraction,
            inorganic_phosphorus_fraction=combined_inorganic_phosphorus_fraction,
            dry_matter=combined_total_dry_matter,
            dry_matter_fraction=combined_dry_matter_fraction,
        )


class ManureEventNutrientRequest(NamedTuple):
    """Used to couple a manure event with a nutrient request."""

    field_name: str
    event: ManureEvent
    nutrient_request: Optional[NutrientRequest]


class ManureEventNutrientRequestResults(NamedTuple):
    """Used to couple a manure event with the results of a nutrient request."""

    field_name: str
    event: ManureEvent
    nutrient_request_results: Optional[NutrientRequestResults]
