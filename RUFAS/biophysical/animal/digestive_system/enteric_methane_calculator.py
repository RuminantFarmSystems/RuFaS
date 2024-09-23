import math

from RUFAS.biophysical.animal.digestive_system.methane_mitigation_calculator import MethaneMitigationCalculator
from RUFAS.general_constants import GeneralConstants


class EntericMethaneCalculator:
    @staticmethod
    def calf_methane(methane_model: str | None, body_weight: float) -> float:
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
    def heifer_methane(
        methane_model: str | None, dry_matter_intake: float, nutrient_concentrations: dict[str, float]
    ) -> float:
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
                0.263 * CP_concentration
                + 0.522 * EE_concentration
                + 0.198 * NDF_concentration
                + 0.160 * soluble_residue
            )  # [A.3B.C.2]
            methane_emission = (0.065 * gross_energy_concentration * dry_matter_intake) / 0.05565  # [A.3B.C.3]

        return methane_emission

    @staticmethod
    def cow_methane(
        is_lactating: bool,
        body_weight: float,
        milk_fat: float,
        metabolizable_energy_intake: float,
        nutrient_amounts: dict[str, float],
        nutrient_concentrations: dict[str, float],
        methane_mitigation_method: str,
        methane_mitigation_additive_amount: float,
        methane_model: str,
    ) -> float:
        """
        Calculates the daily enteric emissions for cows.

        Parameters
        ----------
        body_weight
        methane_model
        is_lactating
        milk_fat
        metabolizable_energy_intake
        nutrient_amounts
        nutrient_concentrations
        methane_mitigation_method
        methane_mitigation_additive_amount

        Returns
        -------
        float
            The daily enteric emissions for cows (g/day).

        """
        dry_matter_intake = nutrient_amounts["dm"]
        NDF_concentration = nutrient_concentrations["NDF"]
        EE_concentration = nutrient_concentrations["EE"]
        starch_concentration = nutrient_concentrations["starch"]

        if is_lactating:
            methane_emission = EntericMethaneCalculator._lactating_cow_manure(
                body_weight,
                milk_fat,
                metabolizable_energy_intake,
                nutrient_amounts,
                nutrient_concentrations,
                methane_model,
            )
        else:
            methane_emission = EntericMethaneCalculator._dry_cow_manure(
                methane_model, metabolizable_energy_intake, nutrient_amounts, nutrient_concentrations
            )

        if methane_mitigation_method:
            methane_yield = 0.0
            methane_yield_reduction = 0.0
            if dry_matter_intake != 0:
                methane_yield = methane_emission / dry_matter_intake
                methane_yield_reduction = MethaneMitigationCalculator.methane_mitigation(
                    NDF_concentration,
                    EE_concentration,
                    starch_concentration,
                    methane_mitigation_method,
                    methane_mitigation_additive_amount
                )

            methane_emission = (
                methane_yield
                * (1 + methane_yield_reduction / GeneralConstants.FRACTION_TO_PERCENTAGE)
                * dry_matter_intake
            )

        return methane_emission

    @staticmethod
    def _lactating_cow_manure(
        body_weight: float,
        milk_fat: float,
        metabolizable_energy_intake: float,
        nutrient_amounts: dict[str, float],
        nutrient_concentrations: dict[str, float],
        methane_model: str,
    ) -> float:
        """
        Calculates the daily enteric emissions for lactating cows.

        Parameters
        ----------
        body_weight
        milk_fat
        metabolizable_energy_intake
        nutrient_amounts
        nutrient_concentrations

        Returns
        -------
        float
            The daily enteric emissions for lactating cows (g/day).

        """
        dry_matter_intake = nutrient_amounts["dm"]
        ASH_concentration = nutrient_concentrations["ash"]
        ADF_concentration = nutrient_concentrations["ADF"]
        CP_concentration = nutrient_concentrations["CP"]
        NDF_concentration = nutrient_concentrations["NDF"]
        EE_concentration = nutrient_concentrations["EE"]
        starch_concentration = nutrient_concentrations["starch"]
        methane_emission = 0.0
        if methane_model == "Mutian":  # [A.3E.C.1]
            methane_emission = (
                -126 + 11.3 * dry_matter_intake + 2.30 * NDF_concentration + 28.8 * milk_fat + 0.148 * body_weight
            )

        elif methane_model == "Mills":  # [A.3E.C.2]
            starch_to_ADF_concentration_ratio = -0.0011 * starch_concentration / ADF_concentration
            temp = -(starch_to_ADF_concentration_ratio + 0.0045) * metabolizable_energy_intake * 4.184
            methane_emission = 45.98 * (1 - math.exp(temp)) / 0.05565

        elif methane_model == "IPCC":  # IPCC
            # Calculating gross energy concentration (Moraes et al. 2014)
            soluble_residue = (
                GeneralConstants.FRACTION_TO_PERCENTAGE
                - ASH_concentration
                - NDF_concentration
                - CP_concentration
                - EE_concentration
            )
            gross_energy_concentration = (
                0.263 * CP_concentration
                + 0.522 * EE_concentration
                + 0.198 * NDF_concentration
                + 0.160 * soluble_residue
            )  # [A.3B.C.2]
            methane_emission = 0.065 * gross_energy_concentration * dry_matter_intake / 0.05565  # [A.3B.C.3]

        return methane_emission

    @staticmethod
    def _dry_cow_manure(
        methane_model: str,
        metabolizable_energy_intake: float,
        nutrient_amounts: dict[str, float],
        nutrient_concentrations: dict[str, float],
    ) -> float:
        """
        Calculates the daily enteric methane emissions for dry cows.

        Parameters
        ----------
        methane_model
        metabolizable_energy_intake
        nutrient_amounts
        nutrient_concentration

        Returns
        -------
        float
            The daily enteric emissions for dry cows (g/day).

        """
        dry_matter_intake = nutrient_amounts["dm"]
        ASH_concentration = nutrient_concentrations["ash"]
        ADF_concentration = nutrient_concentrations["ADF"]
        CP_concentration = nutrient_concentrations["CP"]
        NDF_concentration = nutrient_concentrations["NDF"]
        EE_concentration = nutrient_concentrations["EE"]
        starch_concentration = nutrient_concentrations["starch"]
        soluble_residue = (
            (GeneralConstants.FRACTION_TO_PERCENTAGE - ASH_concentration)
            - NDF_concentration
            - CP_concentration
            - EE_concentration
        )
        if methane_model == "Mills":
            # Methane model = 'Mills' [A.3E.C.2]
            methane_emission = (
                                   45.98
                                   - 45.98
                                   * math.exp(
                                   -((-0.0011 * starch_concentration / ADF_concentration) + 0.0045)
                                   * metabolizable_energy_intake
                                   * 4.184
                               )
                               ) / 0.05565
        else:
            # Default: IPCC Tier 2
            gross_energy_concentration = (
                0.263 * CP_concentration
                + 0.522 * EE_concentration
                + 0.198 * NDF_concentration
                + 0.160 * soluble_residue
            )  # [A.3B.C.2]
            methane_emission = (0.065 * gross_energy_concentration * dry_matter_intake) / 0.05565  # [A.3B.C.3]

        return methane_emission
