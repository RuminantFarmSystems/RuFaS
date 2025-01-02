from dataclasses import dataclass

from RUFAS.biophysical.animal.ration.amino_acid import EssentialAminoAcidRequirements


@dataclass
class NutritionRequirements:
    """
    Energy and nutrition requirements.

    Attributes
    ----------
    maintenance_energy : float
        Net energy requirement for maintenance (Mcal).
    growth_energy : float
        Net energy requirement for growth (Mcal).
    pregnancy_energy : float
        Net energy requirement for pregnancy (Mcal).
    lactation_energy : float
        Net energy requirement for lactation (Mcal).
    metabolizable_protein : float
        Metabolizable protein requirement (g).
    calcium : float
        Calcium requirement (g).
    phosphorus : float
        Phosphorus requirement (g).
    dry_matter : float
        Dry matter intake requirement (kg).
    activity_energy : float
        Net energy requirement for activity (Mcal).
    essential_amino_acids : EssentialAminoAcidRequirements
        Essential amino acid requirements.

    """

    maintenance_energy: float
    growth_energy: float
    pregnancy_energy: float
    lactation_energy: float
    metabolizable_protein: float
    calcium: float
    phosphorus: float
    dry_matter: float
    activity_energy: float
    essential_amino_acids: EssentialAminoAcidRequirements

    @property
    def total_energy_requirement(self) -> float:
        """Total energy requirement for an animal (Mcal)."""
        return (
            self.maintenance_energy
            + self.growth_energy
            + self.pregnancy_energy
            + self.lactation_energy
            + self.activity_energy
        )


@dataclass
class NutritionSupply:
    """
    Energy and nutrition supply for a ration.

    Attributes
    ----------
    metabolizable_energy : float
        Total metabolizable energy in a ration (Mcal).
    maintenance_energy : float
        Energy available for maintenance in a ration (Mcal).
    lactation_energy : float
        Energy available for lactation in a ration (Mcal).
    growth_energy : float
        Energy available for growth in a ration (Mcal).
    metabolizable_protein : float
        Metabolizable protein supplied in a ration (g).
    calcium : float
        Calcium supplied in a ration (g).
    phosphorus : float
        Phosphorus supplied in a ration (g).
    dry_matter : float
        Total dry matter supply of a ration (kg).
    ndf_supply : float
        Total neutral detergent fiber (NDF) supplied by the ration (kg).
    fat_supply : float
        Total fat supplied by the ration (kg).

    """

    metabolizable_energy: float
    maintenance_energy: float
    lactation_energy: float
    growth_energy: float
    metabolizable_protein: float
    calcium: float
    phosphorus: float
    dry_matter: float
    ndf_supply: float
    fat_supply: float


@dataclass
class NutritionEvaluationResults:
    """
    Results of evaluating whether a ration supplied the required energy and nutrients.

    Attributes
    ----------
    total_energy : float | None
        Surplus or deficit of total energy in a ration (Mcal). Necessary to know for cows, not heifers because it
        accounts for some energy demands that are not relevant to all heifers (for example, lactation for growing
        heifers).
    maintenance_energy : float
        Surplus or deficit of energy in a ration for maintenance (Mcal).
    lactation_energy : float | None
        Surplus or deficit of lactation in a ration (Mcal). This value is None when evaluating nutrition requirements of
        heifers, because they are never lactating.
    growth_energy : float
        Surplus or deficit of energy in a ration for growth (Mcal).
    metabolizable_protein : float
        Amount of metabolizable protein by which a ration was outside the acceptable bounds (g). If protein is within
        acceptable bounds, this value will be 0.0.
    calcium : float
        Surplus or deficit of calcium in a ration (g).
    phosphorus : float
        Surplus or deficit of phosphorus in a ration (g).
    dry_matter : float
        Amount of dry matter by which a ration was outside the acceptable bounds (kg). If dry matter is within
        acceptable bounds, this value will be 0.0.
    ndf_percentage : float
        Surplus or deficit of neutral detergent fiber (NDF) percentage in a ration. If NDF percentage is within
        acceptable bounds, this value will be 0.0.
    fat_percent : float
        Surplus or deficit of fat percentage in a ration. If fat percentage is within acceptable bounds, this value will
        be 0.0.
    is_valid_heifer_ration : bool
        True if evaluated nutrient supply meets requirements for heifers, else false.
    is_valid_cow_ration : bool
        True if evaluated nutrient supply meets requirements for cows, else false.

    """

    total_energy: float | None
    maintenance_energy: float
    lactation_energy: float | None
    growth_energy: float
    metabolizable_protein: float
    calcium: float
    phosphorus: float
    dry_matter: float
    ndf_percent: float
    fat_percent: float

    @property
    def _are_clamped_values_acceptable(self) -> bool:
        """Checks that values which must be in a certain range are in that range."""
        clamped_values = [self.metabolizable_protein, self.ndf_percent, self.fat_percent, self.dry_matter]
        return all([value == 0.0 for value in clamped_values])

    @property
    def is_valid_heifer_ration(self) -> bool:
        """True if evaluated supply meets requirements for heifers, else false."""
        non_negative_fields = {self.maintenance_energy, self.growth_energy, self.calcium, self.phosphorus}
        valid_non_negative_fields = all([field >= 0.0 for field in non_negative_fields])

        return valid_non_negative_fields and self._are_clamped_values_acceptable

    @property
    def is_valid_cow_ration(self) -> bool:
        """True if evaluated supply meets requirements for cows, else false."""
        if self.total_energy is None or self.lactation_energy is None:
            return False

        valid_non_negative_fields = all([field >= 0.0 for field in {self.total_energy, self.lactation_energy}])

        return valid_non_negative_fields and self._are_clamped_values_acceptable and self.is_valid_heifer_ration
