from dataclasses import dataclass

from RUFAS.biophysical.animal.ration.amino_acid import EssentialAminoAcidRequirements


@dataclass
class NutritionRequirements:
    """
    Energy and nutrition requirements.

    Attributes
    ----------
    maintenance : float
        Net energy requirement for maintenance (Mcal).
    growth : float
        Net energy requirement for growth (Mcal).
    pregnancy : float
        Net energy requirement for pregnancy (Mcal).
    lactation : float
        Net energy requirement for lactation (Mcal).
    protein : float
        Metabolizable protein requirement (g).
    calcium : float
        Calcium requirement (g).
    phosphorus : float
        Phosphorus requirement calculated with either the NASEM or NRC methodologies (g).
    secondary_phosphorus : float
        Phosphorus requirement calculated with the dedicated animal phosphorus submodule (g).
    dry_matter : float
        Dry matter intake (kg).
    activity : float
        Net energy requirement for activity (Mcal).
    essential_amino_acids : EssentialAminoAcidRequirements
        Essential amino acid requirements.

    """

    maintenance: float
    growth: float
    pregnancy: float
    lactation: float
    protein: float
    calcium: float
    phosphorus: float
    secondary_phosphorus: float
    dry_matter: float
    activity: float
    essential_amino_acids: EssentialAminoAcidRequirements

    @property
    def total_energy_requirement(self) -> float:
        """Total energy requirement for an animal (Mcal)."""
        return self.maintenance + self.growth + self.pregnancy + self.lactation + self.activity

    def __add__(self, other: "NutritionRequirements") -> "NutritionRequirements":
        """Add two NutritionRequirements objects together."""
        return NutritionRequirements(
            maintenance=self.maintenance + other.maintenance,
            growth=self.growth + other.growth,
            pregnancy=self.pregnancy + other.pregnancy,
            lactation=self.lactation + other.lactation,
            protein=self.protein + other.protein,
            calcium=self.calcium + other.calcium,
            phosphorus=self.phosphorus + other.phosphorus,
            secondary_phosphorus=self.secondary_phosphorus + other.secondary_phosphorus,
            dry_matter=self.dry_matter + other.dry_matter,
            activity=self.activity + other.activity,
            essential_amino_acids=self.essential_amino_acids + other.essential_amino_acids,
        )

    def __truediv__(self, divisor: float) -> "NutritionRequirements":
        """Divide all NutritionRequirements values by a scalar."""
        if divisor == 0.0:
            raise ZeroDivisionError("Cannot divide NutritionRequirements by zero.")
        return NutritionRequirements(
            maintenance=self.maintenance / divisor,
            growth=self.growth / divisor,
            pregnancy=self.pregnancy / divisor,
            lactation=self.lactation / divisor,
            protein=self.protein / divisor,
            calcium=self.calcium / divisor,
            phosphorus=self.phosphorus / divisor,
            secondary_phosphorus=self.secondary_phosphorus / divisor,
            dry_matter=self.dry_matter / divisor,
            activity=self.activity / divisor,
            essential_amino_acids=self.essential_amino_acids / divisor,
        )


@dataclass
class NutritionSupply:
    """
    Energy and nutrition supply for a ration.

    Attributes
    ----------
    metabolizable : float
        Total metabolizable energy in a ration (Mcal).
    maintenance : float
        Energy available for maintenance in a ration (Mcal).
    lactation : float
        Energy available for lactation in a ration (Mcal).
    growth : float
        Energy available for growth in a ration (Mcal).
    protein : float
        Metabolizable protein supplied in a ration (g).
    calcium : float
        Calcium supplied in a ration (g).
    phosphorus : float
        Phosphorus supplied in a ration (g).
    dry_matter : float
        Total dry matter content of a ration (kg).
    ndf_content : float
        Total neutral detergent fiber (NDF) in the ration (kg).
    fat_content : float
        Total fat content in the ration (kg).

    """

    metabolizable: float
    maintenance: float
    lactation: float
    growth: float
    protein: float
    calcium: float
    phosphorus: float
    dry_matter: float
    ndf_content: float
    fat_content: float


@dataclass
class NutritionEvaluationResults:
    """
    Results of evaluating whether a ration supplied the required energy and nutrients.

    Attributes
    ----------
    total_energy : float | None
        Surplus or deficit of total energy in a ration (Mcal). Necessary to know for cows, not heifers.
    maintenance : float
        Surplus or deficit of energy in a ration for maintenance (Mcal).
    lactation : float | None
        Surplus or deficit of lactation in a ration (Mcal). Necessary to know for cows, not heifers.
    growth : float
        Surplus or deficit of energy in a ration for growth (Mcal).
    protein : float
        Amount of metabolizable protein by which a ration was outside the acceptable bounds (g). If protein was
        acceptable, this value is 0.0.
    calcium : float
        Surplus or deficit of calcium in a ration (g).
    phosphorus : float
        Surplus or deficit of phosphorus in a ration (g).
    dry_matter : float
        Amount of dry matter by which a ration was outside the acceptable bounds (kg). If dry matter was acceptable,
        this value is 0.0.
    ndf : float
        Surplus or deficit of neutral detergent fiber (NDF) in a ration. If NDF was acceptable, this valus is 0.0.
    fat : float
        Surplus or deficit of fat percentage in a ration. If fat percentage was acceptable, this value is 0.0.
    is_valid_heifer_ration
    is_valid_cow_ration

    """
    total_energy: float | None
    maintenance: float
    lactation: float | None
    growth: float
    protein: float
    calcium: float
    phosphorus: float
    dry_matter: float
    ndf: float
    fat: float

    @property
    def _clamped_values_are_valid(self) -> bool:
        """Checks that values which must be in a certain range are in that range."""
        clamped_values = [self.protein, self.ndf, self.fat, self.dry_matter]
        return all([value == 0.0 for value in clamped_values])

    @property
    def is_valid_heifer_ration(self) -> bool:
        """True if evaluated supply meets requirements for heifers, else false."""
        non_negative_fields = {self.maintenance, self.growth, self.calcium, self.phosphorus}
        valid_non_negative_fields = all([field >= 0.0 for field in non_negative_fields])

        return valid_non_negative_fields and self._clamped_values_are_valid

    @property
    def is_valid_cow_ration(self) -> bool:
        """True if evaluated supply meets requirements for cows, else false."""
        if self.total_energy is None or self.lactation is None:
            return False

        non_negative_fields = {
            self.total_energy, self.maintenance, self.lactation, self.growth, self.calcium, self.phosphorus
        }
        valid_non_negative_fields = all([field >= 0.0 for field in non_negative_fields])

        return valid_non_negative_fields and self._clamped_values_are_valid
