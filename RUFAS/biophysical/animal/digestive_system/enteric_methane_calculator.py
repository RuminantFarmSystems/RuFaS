from numpy import exp

from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionSupply
from RUFAS.biophysical.animal.digestive_system.methane_mitigation_calculator import MethaneMitigationCalculator
from RUFAS.general_constants import GeneralConstants


class EntericMethaneCalculator:
    @staticmethod
    def calculate_calf_methane(methane_model: str | None, body_weight: float) -> float:
        """
        Calculates the amount of methane emission for calf.

        Parameters
        ----------
        methane_model: str | None
            Methane model used for methane emission calculations, including Mutian, Mills, IPCC.
        body_weight: float
            Body weight of the current animal, kg.

        Returns
        -------
        float
            The amount of methane emission for calf (g/day).

        """
        methane_emission = 0.0
        if methane_model:
            methane_emission = (0.013 * (body_weight**0.75) * 4.184) / 0.05565

        return methane_emission

    @staticmethod
    def calculate_heifer_methane(
        methane_model: str | None,
        nutrition_supply: NutritionSupply,
    ) -> float:
        """
        Calculates the amount of methane emission for heifer.

        Parameters
        ----------
        methane_model: str
            Methane model used for methane emission calculations, including IPCC.
        nutrition_supply: NutritionSupply
            Amounts of nutrients in pen ration, calculated per animal, see Notes section for units.

        Returns
        -------
        float
            Amount of methane emission for heifer (g/day).

        References
        ----------
        IPCC tier 2 calculation: [A.3B.C.2]

        """
        methane_emission = 0.0
        if methane_model:
            crude_protein_concentration = nutrition_supply.ndf_percentage
            ethyl_ester_concentration = nutrition_supply.fat_percentage
            neutral_detergent_fiber_concentration = nutrition_supply.ndf_percentage
            ash_concentration = nutrition_supply.ash_percentage
            soluble_residue = (
                (100 - ash_concentration)
                - neutral_detergent_fiber_concentration
                - crude_protein_concentration
                - ethyl_ester_concentration
            )
            gross_energy_concentration = (
                0.263 * crude_protein_concentration
                + 0.522 * ethyl_ester_concentration
                + 0.198 * neutral_detergent_fiber_concentration
                + 0.160 * soluble_residue
            )
            methane_emission = (
                0.065 * gross_energy_concentration * nutrition_supply.dry_matter
            ) / 0.05565  # [A.3B.C.3]

        return methane_emission

    @staticmethod
    def calculate_cow_methane(
        is_lactating: bool,
        body_weight: float,
        milk_fat: float,
        metabolizable_energy_intake: float,
        nutrient_amounts: NutritionSupply,
        methane_mitigation_method: str,
        methane_mitigation_additive_amount: float,
        methane_model: str,
    ) -> float:
        """
        Calculates the daily enteric emissions for cows.

        Parameters
        ----------
        body_weight: float
            Body weight of the current cow (kg).
        methane_model: str
            Methane model used for methane emission calculations, including "Mutian", "Mills", "IPCC".
        is_lactating: bool
            Indicator of cow's lactating status.
        milk_fat: float
            Milk fat, % of milk.
        metabolizable_energy_intake: float
            Metabolizable energy intake, Mcal/kg dry matter.
        nutrient_amounts: NutritionSupply
            Amounts of nutrients in pen ration, calculated per animal, see Notes section for units.
        methane_mitigation_method: str
            The name of the methane mitigation feed additives. The accepted names are
                '3-NOP', 'Monensin', 'Essential Oils', and 'Seaweed'.
        methane_mitigation_additive_amount: float
            The dosage of the feed additive, mg/kg DMI.

        Returns
        -------
        float
            The daily enteric emissions for cows (g/day).

        Notes
        -----
        The dry matter ("dm") unit is kg per animal. Crude protein ("CP"), ADF, NDF, lignin, ash, phosphorus, potassium,
        and nitrogen ("N") are all percentages of dry matter.

        """
        dry_matter_intake = nutrient_amounts.dry_matter
        neutral_detergent_fiber_concentration = nutrient_amounts.ndf_percentage
        ethyl_ester_concentration = nutrient_amounts.fat_percentage
        starch_concentration = nutrient_amounts.starch_percentage

        if is_lactating:
            methane_emission = EntericMethaneCalculator._calculate_lactating_cow_enteric_methane(
                body_weight,
                milk_fat,
                metabolizable_energy_intake,
                nutrient_amounts,
                methane_model,
            )
            if methane_mitigation_method:
                methane_yield = 0.0
                methane_yield_reduction = 0.0
                if dry_matter_intake != 0:
                    methane_yield = methane_emission / dry_matter_intake
                    methane_yield_reduction = MethaneMitigationCalculator.mitigate_methane(
                        neutral_detergent_fiber_concentration,
                        ethyl_ester_concentration,
                        starch_concentration,
                        methane_mitigation_method,
                        methane_mitigation_additive_amount,
                    )

                methane_emission = (
                    methane_yield
                    * (1 + methane_yield_reduction * GeneralConstants.PERCENTAGE_TO_FRACTION)
                    * dry_matter_intake
                )
        else:
            methane_emission = EntericMethaneCalculator._calculate_dry_cow_enteric_methane(
                methane_model, metabolizable_energy_intake, nutrient_amounts
            )

        return methane_emission

    @staticmethod
    def _calculate_lactating_cow_enteric_methane(
        body_weight: float,
        milk_fat: float,
        metabolizable_energy_intake: float,
        nutrient_amounts: NutritionSupply,
        methane_model: str,
    ) -> float:
        """
        Calculates the daily enteric emissions for lactating cows.

        Parameters
        ----------
        body_weight: float
            Body weight of the current cow (kg).
        milk_fat: float
            Milk fat (from animal input), % of milk.
        metabolizable_energy_intake: float
            Metabolizable energy intake, Mcal/kg dry matter.
        nutrient_amounts: Dict[str, float]
            Amounts of nutrients in pen ration, calculated per animal, see Notes section for units.

        Returns
        -------
        float
            The daily enteric emissions for lactating cows (g/day).

        Notes
        -----
        The dry matter ("dm") unit is kg per animal. Crude protein ("CP"), ADF, NDF, lignin, ash, phosphorus, potassium,
        and nitrogen ("N") are all percentages of dry matter.

        References
        ----------
        Mutian calculation: [A.3E.C.1]
        Mills calculation: [A.3E.C.2]
        IPCC calculation: [A.3B.C.2]
        gross energy concentration calculation: Moraes et al. 2014
        Methane emission calculation: [A.3B.C.3]

        """
        dry_matter_intake = nutrient_amounts.dry_matter
        ash_concentration = nutrient_amounts.ash_percentage
        acid_detergent_fiber_concentration = nutrient_amounts.adf_percentage
        crude_protein_concentration = nutrient_amounts.crude_protein_percentage
        neutral_detergent_fiber_concentration = nutrient_amounts.ndf_percentage
        ethyl_ester_concentration = nutrient_amounts.fat_percentage
        starch_concentration = nutrient_amounts.starch_percentage
        methane_emission = 0.0
        if methane_model == "Mutian":
            methane_emission = (
                -126
                + 11.3 * dry_matter_intake
                + 2.30 * neutral_detergent_fiber_concentration
                + 28.8 * milk_fat
                + 0.148 * body_weight
            )

        elif methane_model == "Mills":
            starch_to_acid_detergent_fiber_concentration_ratio = (
                -0.0011 * starch_concentration / acid_detergent_fiber_concentration
            )
            temp = -(starch_to_acid_detergent_fiber_concentration_ratio + 0.0045) * metabolizable_energy_intake * 4.184
            methane_emission = 45.98 * (1 - exp(temp)) / 0.05565

        elif methane_model == "IPCC":
            soluble_residue = (
                GeneralConstants.FRACTION_TO_PERCENTAGE
                - ash_concentration
                - neutral_detergent_fiber_concentration
                - crude_protein_concentration
                - ethyl_ester_concentration
            )
            gross_energy_concentration = (
                0.263 * crude_protein_concentration
                + 0.522 * ethyl_ester_concentration
                + 0.198 * neutral_detergent_fiber_concentration
                + 0.160 * soluble_residue
            )
            methane_emission = 0.065 * gross_energy_concentration * dry_matter_intake / 0.05565

        return methane_emission

    @staticmethod
    def _calculate_dry_cow_enteric_methane(
        methane_model: str,
        metabolizable_energy_intake: float,
        nutrient_amounts: NutritionSupply,
    ) -> float:
        """
        Calculates the daily enteric methane emissions for dry cows.

        Parameters
        ----------
        methane_model: str
            Methane model used for methane emission calculations, including Mills, IPCC.
        metabolizable_energy_intake: float
            Metabolizable energy intake, Mcal/kg dry matter.
        nutrient_amounts: Dict[str, float]
            Amounts of nutrients in pen ration, calculated per animal, see Notes section for units.

        Returns
        -------
        float
            The daily enteric emissions for dry cows (g/day).

        Notes
        -----
        The dry matter ("dm") unit is kg per animal. Crude protein ("CP"), ADF, NDF, lignin, ash, phosphorus, potassium,
        and nitrogen ("N") are all percentages of dry matter.

        References
        ----------
        Mills calculation: [A.3E.C.2]
        IPCC tier2 calculation: [A.3B.C.2]

        """
        dry_matter_intake = nutrient_amounts.dry_matter
        ash_concentration = nutrient_amounts.ash_percentage
        acid_detergent_fiber_concentrations = nutrient_amounts.adf_percentage
        crude_protein_concentration = nutrient_amounts.crude_protein_percentage
        neutral_detergent_fiber_concentration = nutrient_amounts.ndf_percentage
        ethyl_ester_concentration = nutrient_amounts.fat_percentage
        starch_concentration = nutrient_amounts.starch_percentage
        soluble_residue = (
            (100 - ash_concentration)
            - neutral_detergent_fiber_concentration
            - crude_protein_concentration
            - ethyl_ester_concentration
        )
        if methane_model == "Mills":
            methane_emission = (
                45.98
                - 45.98
                * exp(
                    -((-0.0011 * starch_concentration / acid_detergent_fiber_concentrations) + 0.0045)
                    * metabolizable_energy_intake
                    * 4.184
                )
            ) / 0.05565
        else:
            gross_energy_concentration = (
                0.263 * crude_protein_concentration
                + 0.522 * ethyl_ester_concentration
                + 0.198 * neutral_detergent_fiber_concentration
                + 0.160 * soluble_residue
            )
            methane_emission = (0.065 * gross_energy_concentration * dry_matter_intake) / 0.05565  # [A.3B.C.3]

        return methane_emission
