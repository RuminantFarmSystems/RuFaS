from typing import Dict, List, TypedDict

from RUFAS.general_constants import GeneralConstants


class AminoAcidComposition(TypedDict):
    duodenal_endogenous: float
    microbial: float
    scurf: float
    whole_empty_body: float
    metabolic_fecal: float
    milk: float


AMINO_ACID_COMPOSITION: Dict[str, AminoAcidComposition] = {
    "arginine": {
        "duodenal_endogenous": 4.61,
        "microbial": 5.47,
        "scurf": 9.60,
        "whole_empty_body": 8.20,
        "metabolic_fecal": 5.90,
        "milk": 3.74,
    },
    "histidine": {
        "duodenal_endogenous": 2.90,
        "microbial": 2.21,
        "scurf": 1.75,
        "whole_empty_body": 3.04,
        "metabolic_fecal": 3.54,
        "milk": 2.92,
    },
    "isoleucine": {
        "duodenal_endogenous": 4.09,
        "microbial": 6.99,
        "scurf": 2.96,
        "whole_empty_body": 3.69,
        "metabolic_fecal": 5.39,
        "milk": 6.18,
    },
    "leucine": {
        "duodenal_endogenous": 7.67,
        "microbial": 9.23,
        "scurf": 6.93,
        "whole_empty_body": 8.27,
        "metabolic_fecal": 9.19,
        "milk": 10.56,
    },
    "lysine": {
        "duodenal_endogenous": 6.23,
        "microbial": 9.44,
        "scurf": 5.64,
        "whole_empty_body": 7.90,
        "metabolic_fecal": 7.61,
        "milk": 8.82,
    },
    "methionine": {
        "duodenal_endogenous": 1.26,
        "microbial": 2.63,
        "scurf": 1.40,
        "whole_empty_body": 2.37,
        "metabolic_fecal": 1.73,
        "milk": 3.03,
    },
    "phenylalanine": {
        "duodenal_endogenous": 3.98,
        "microbial": 6.30,
        "scurf": 3.61,
        "whole_empty_body": 4.41,
        "metabolic_fecal": 5.28,
        "milk": 5.26,
    },
    "threonine": {
        "duodenal_endogenous": 5.18,
        "microbial": 6.23,
        "scurf": 4.01,
        "whole_empty_body": 4.84,
        "metabolic_fecal": 7.36,
        "milk": 4.62,
    },
    "thryptophan": {
        "duodenal_endogenous": 1.29,
        "microbial": 1.37,
        "scurf": 0.73,
        "whole_empty_body": 1.05,
        "metabolic_fecal": 1.79,
        "milk": 1.65,
    },
    "valine": {
        "duodenal_endogenous": 5.29,
        "microbial": 6.88,
        "scurf": 4.66,
        "whole_empty_body": 5.15,
        "metabolic_fecal": 7.01,
        "milk": 6.90,
    },
}
ESSENTIAL_AMINO_ACIDS: List[str] = [
    "histidine",
    "isoleucine",
    "leucine",
    "lysine",
    "methionine",
    "phenylalanine",
    "threonine",
    "thryptophan",
    "valine",
]

ESSENTIAL_AMINO_ACID_TARGET_EFFICIENCIES: Dict[str, float] = {
    "histidine": 0.75,
    "isoleucine": 0.71,
    "leucine": 0.73,
    "lysine": 0.72,
    "methionine": 0.73,
    "phenylalanine": 0.60,
    "threonine": 0.64,
    "thryptophan": 0.86,
    "valine": 0.74,
}


class AminoAcidCalculator:
    def calculate_essential_amino_acid_requirements(
        self,
        lactating: bool,
        body_weight: float,
        frame_weight_gain: float,
        gravid_uterine_weight_gain: float,
        dry_matter_intake_estimate: float,
        milk_true_protein: float,
        milk_production: float,
        NDF_conc: float,
    ) -> Dict[str, float]:
        """
        This function calculates the total Essential Amino Acid for an animal according to equations on page 8 of the
        AA requirements design doc.

        Parameters
        ----------
        lactating : bool
            Physiological condition
        body_weight : float
            Body weight (kilograms)
        frame_weight_gain : float
            Frame weight gain refers to the accretion of both fat and protein in carcass (grams per day)
        gravid_uterine_weight_gain : float
            Daiy energy Requirement associated to increased gain of reproductive tissues as pregnancy advances (Mcal/d)
        dry_matter_intake_estimate : float
            Estimated dry matter intake according to empirical prediction equation within NASEM (2021) (kg/d)
        milk_true_protein : float
            True protein contents in milk (%)
        milk_production: float
            Milk yield (kg/d)
        NDF_conc:
            Concentration (percent value) of Neutral Detergent Fiber in previously fed ration.

        Returns
        -------
        total_amino_acid_requirements : Dict[str, float]
            Total amino acid requirement for each of the essential amino acid (grams per day)

        Notes
        -----
        NPscurf: float
            Net protein requirement for scurf, g
        NPEndUrin: float
            Net protein requirement for endogenous urinary excretion, g
        CPMFP: float
            Crude protein in metabolic fecal protein, g
        NPMFP: float
            Net protein requirement for metabolic fecal protein, g
        NPGrowth: float
            Net protein requirement for body frame weight gain, g
        NPGest: float
            Net protein requirement for pregnancy, g
        NPMilk: float
            Net protein in milk, or milk true protein yield, g
        """
        total_amino_acid_requirements: Dict[str, float] = {}

        NPscurf: float = 0.20 * body_weight ** (0.60) * 0.85
        CPMFP: float = (11.62 + 0.134 * NDF_conc) * dry_matter_intake_estimate
        NPMFP: float = CPMFP * 0.73
        NPGrowth: float = frame_weight_gain * 0.11 * 0.86
        NPGest: float = gravid_uterine_weight_gain * 125
        NPMilk: float = (milk_true_protein / 100) * milk_production * GeneralConstants.KG_TO_GRAMS

        target_efficiency_gest: float = 0.33
        target_efficiency_growth: float = 0.40

        for amino_acid in ESSENTIAL_AMINO_ACIDS:
            net_AA_scurf: float = self._calculate_scurf(amino_acid, NPscurf)
            net_AA_End_Urine: float = self._calculate_endogenous_urinary_excretion(amino_acid, body_weight)
            net_AA_MFP: float = self._calculate_metabolic_fecal_protein(amino_acid, NPMFP)
            net_AA_Growth: float = self._calculate_growth(amino_acid, NPGrowth)
            net_AA_Gest: float = self._calculate_pregnancy(amino_acid, NPGest)

            if lactating:
                net_AA_Milk: float = self._calculate_lactation(amino_acid, NPMilk)

                total_amino_acid_requirements[amino_acid] = (
                    (
                        (net_AA_scurf + net_AA_MFP + net_AA_Growth + net_AA_Milk)
                        / ESSENTIAL_AMINO_ACID_TARGET_EFFICIENCIES[amino_acid]
                    )
                    + (net_AA_Gest / target_efficiency_gest)
                    + net_AA_End_Urine
                )
            else:
                total_amino_acid_requirements[amino_acid] = (
                    ((net_AA_scurf + net_AA_MFP) / ESSENTIAL_AMINO_ACID_TARGET_EFFICIENCIES[amino_acid])
                    + (net_AA_Growth / target_efficiency_growth)
                    + (net_AA_Gest / target_efficiency_gest)
                    + net_AA_End_Urine
                )

        return total_amino_acid_requirements

    def _calculate_scurf(self, amino_acid: str, NPscurf: float) -> float:
        """
        Calculates the net demand for the specific amino acid in scurf excretion (g/d).

        Parameters
        ----------
        amino_acid : str
            The type of amino acid to calculate.
        NPscurf: float
            Net protein requirement for scurf, g

        Returns
        -------
        float
            The net demand for the specific amino acid in scurf excretion (grams per day).
        """
        return NPscurf * AMINO_ACID_COMPOSITION[amino_acid]["scurf"] / 100

    def _calculate_endogenous_urinary_excretion(self, amino_acid: str, body_weight: float) -> float:
        """
        Calculates the net demand for the specific amino acid for endogenous urinary excretion (g/d).

        Parameters
        ----------
        amino_acid : str
            The type of amino acid to calculate.
        body_weight: float
            Body weight, kg

        Returns
        -------
        float
            The net demand for the specific amino acid for endogenous urinary excretion (grams per day).
        """
        return 0.010 * 6.25 * body_weight * AMINO_ACID_COMPOSITION[amino_acid]["whole_empty_body"] / 100

    def _calculate_metabolic_fecal_protein(self, amino_acid: str, NPMFP: float) -> float:
        """
        Calculates the net demand for the specific amino acid for metabolic fecal protein (g/d).

        Parameters
        ----------
        amino_acid : str
            The type of amino acid to calculate.
        NPMFP: float
            Net protein requirement for metabolic fecal protein, g

        Returns
        -------
        float
            The net demand for the specific amino acid for metabolic fecal protein (grams per day).
        """
        return NPMFP * AMINO_ACID_COMPOSITION[amino_acid]["metabolic_fecal"] / 100

    def _calculate_growth(self, amino_acid: str, NPGrowth: float) -> float:
        """
        Calculates the net demand for the specific amino acid for body frame weight gain (g/d).

        Parameters
        ----------
        amino_acid : str
            The type of amino acid to calculate.
        NPGrowth: float
            Net protein requirement for body frame weight gain, g

        Returns
        -------
        float
            The net demand for the specific amino acid for body frame weight gain (grams per day).
        """
        return NPGrowth * AMINO_ACID_COMPOSITION[amino_acid]["whole_empty_body"] / 100

    def _calculate_pregnancy(self, amino_acid: str, NPGest: float) -> float:
        """
        Calculates the net amino acid composition of protein accretion associated with pregnancy (g/d).

        Parameters
        ----------
        amino_acid : str
            The type of amino acid to calculate.
        NPGest: float
            Net protein requirement for pregnancy, g

        Returns
        -------
        float
            The net amino acid composition of protein accretion associated with pregnancy (grams per day).
        """
        return NPGest * AMINO_ACID_COMPOSITION[amino_acid]["whole_empty_body"] / 100

    def _calculate_lactation(self, amino_acid: str, NPMilk: float) -> float:
        """
        Calculates the net amino acids yield in milk (g/d).

        Parameters
        ----------
        amino_acid : str
            The type of amino acid to calculate.
        NPMilk: float
            Net protein in milk, or milk true protein yield, g

        Returns
        -------
        float
            The net amino acids yield in milk (grams per day).
        """
        return NPMilk * AMINO_ACID_COMPOSITION[amino_acid]["milk"] / 100
