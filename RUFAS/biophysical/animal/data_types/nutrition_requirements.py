from dataclasses import dataclass

from RUFAS.biophysical.animal.ration.amino_acid import EssentialAminoAcidRequirements


@dataclass
class EnergyNutritionRequirements:
    """
    Energy and nutritional requirements.

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
        Phosphorus requirement (g).
    dry_matter : float
        Dry matter intake (kg).
    activity : float
        Net energy requirement for activity (Mcal).
    essential_amino_acids : EssentialAminoAcidRequirements
        Essential amino acid requirements.

    """
    maintenance : float
    growth : float
    pregnancy : float
    lactation : float
    protein : float
    calcium : float
    phosphorus : float
    dry_matter : float
    activity : float
    essential_amino_acids: EssentialAminoAcidRequirements

    @property
    def total_energy_requirements(self) -> float:
        """Total energy requirements for an animal (Mcal)."""
        return self.maintenance + self.growth + self.pregnancy + self.lactation + self.activity


class EnergyNutritionSupply:
    """
    Energy and nutrition supply for a ration.
    """
    pass
