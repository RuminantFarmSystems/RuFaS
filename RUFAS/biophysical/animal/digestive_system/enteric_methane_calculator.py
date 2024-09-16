from RUFAS.general_constants import GeneralConstants


class EntericMethaneCalculator:
    @staticmethod
    def calf_methane(methane_model: str, body_weight: float) -> float:
        """

        Parameters
        ----------
        methane_model
        body_weight

        Returns
        -------

        """
        methane_emission = 0.0
        if methane_model:
            methane_emission = (0.013 * (body_weight ** 0.75) * 4.184) / 0.05565

        return methane_emission

    @staticmethod
    def heifer_methane(methane_model: str,
                       dry_matter_intake: float,
                       nutrient_concentrations: dict[str, float]) -> float:
        """

        Parameters
        ----------
        methane_model
        dry_matter_intake
        nutrient_concentrations

        Returns
        -------

        """
        methane_emission = 0.0
        if methane_model:
            # Default: IPCC Tier 2
            CP_concentration = nutrient_concentrations["CP"]
            EE_concentration = nutrient_concentrations["EE"]
            NDF_concentration = nutrient_concentrations["NDF"]
            ASH_concentration = nutrient_concentrations["ash"]
            soluble_residue = (
                (GeneralConstants.FRACTION_TO_PERCENTAGE - ASH_concentration)
                - NDF_concentration
                - CP_concentration
                - EE_concentration
            )
            gross_energy_concentration = (
                0.263 * CP_concentration + 0.522 * EE_concentration + 0.198 * NDF_concentration + 0.160 * soluble_residue
            )  # [A.3B.C.2]
            methane_emission = (0.065 * gross_energy_concentration * dry_matter_intake) / 0.05565  # [A.3B.C.3]

        return methane_emission
