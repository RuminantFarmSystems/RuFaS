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
    maintenance: float
    growth: float
    pregnancy: float
    lactation: float
    protein: float
    calcium: float
    phosphorus: float
    dry_matter: float
    activity: float
    essential_amino_acids: EssentialAminoAcidRequirements

    @property
    def total_energy_requirements(self) -> float:
        """Total energy requirements for an animal (Mcal)."""
        return self.maintenance + self.growth + self.pregnancy + self.lactation + self.activity


@dataclass
class EnergyNutritionSupply:
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
        Total dry matter content of a diet (kg).

    """
    metabolizable: float
    maintenance: float
    lactation: float
    growth: float
    protein: float
    calcium: float
    phosphorus: float
    dry_matter: float
