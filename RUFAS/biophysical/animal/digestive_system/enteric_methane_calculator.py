from typing import Any

from freezegun.api import real_uuid_generate_time
from numpy import exp

from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionSupply
from RUFAS.biophysical.animal.digestive_system.methane_mitigation_calculator import MethaneMitigationCalculator
from RUFAS.general_constants import GeneralConstants
from RUFAS.biophysical.animal import animal_constants


class EntericMethaneCalculator:
    @staticmethod
    def calculate_calf_methane(methane_models: dict[str, bool], body_weight: float) -> dict[str, float]:
        """
        Calculates the amount of methane emission for calf.

        Notes
        -----
        [AN.MET.4]

        Parameters
        ----------
        methane_models: dict[str, bool]
            Methane model used for methane emission calculations, including Mutian, Mills, IPCC.
        body_weight: float
            Body weight of the current animal, kg.

        Returns
        -------
        dict[str, float]
            The amount of methane emission for calf (g/day) corresponding to each method.

        References
        ----------
        (Pattanaik et al., 2003)

        """
        methane_results = {}
        for model, usage in methane_models.items():
            if usage:
                methane_emission = (
                    0.013 * (body_weight**0.75) * GeneralConstants.KCAL_TO_MJ
                ) / GeneralConstants.MJ_CH4_TO_G_CH4
                methane_results[model] = methane_emission
            else:
                methane_results[model] = 0

        return methane_results

    @staticmethod
    def calculate_heifer_methane(
        methane_models: dict[str, bool],
        nutrition_supply: NutritionSupply,
    ) -> dict[str, float]:
        """
        Calculates the amount of methane emission for heifer.

        Notes
        -----
        Soluble residue: [AN.MET.1]
        Gross energy concentration: [AN.MET.2]
        Starch to acid detergent fiber concentration ratio: [AN.MET.3]
        Enteric methane emission:  [AN.MET.5]

        Parameters
        ----------
        methane_models: str
            Methane model used for methane emission calculations, including IPCC.
        nutrition_supply: NutritionSupply
            Amounts of nutrients in pen ration, calculated per animal, see Notes section for units.

        Returns
        -------
        dict[str, float]
            Amount of methane emission for heifer (g/day).

        References
        ----------
        (IPCC tier 2, 2006)

        """
        methane_results = {}
        for model, usage in methane_models.items():
            if usage:
                crude_protein_concentration = nutrition_supply.crude_protein_percentage
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
                ) / GeneralConstants.MJ_CH4_TO_G_CH4
                methane_results[model] = methane_emission
            else:
                methane_results[model] = 0

        return methane_results

    @staticmethod
    def calculate_cow_methane(
        is_lactating: bool,
        body_weight: float,
        milk_fat: float,
        metabolizable_energy_intake: float,
        nutrient_amounts: NutritionSupply,
        methane_mitigation_method: str,
        methane_mitigation_additive_amount: float,
        methane_models: dict[str, Any],
    ) -> dict[str, float]:
        """
        Calculates the daily enteric emissions for cows.

        Notes
        -----
        The dry matter ("dm") unit is kg per animal. Crude protein ("CP"), ADF, NDF, lignin, ash, phosphorus, potassium,
        and nitrogen ("N") are all percentages of dry matter.

        Parameters
        ----------
        body_weight: float
            Body weight of the current cow (kg).
        methane_models: str
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
        dict[str, float]
            The daily enteric emissions for cows (g/day).

        """
        dry_matter_intake = nutrient_amounts.dry_matter
        neutral_detergent_fiber_concentration = nutrient_amounts.ndf_percentage
        ethyl_ester_concentration = nutrient_amounts.fat_percentage
        starch_concentration = nutrient_amounts.starch_percentage
        methane_models = methane_models["cows"]

        if is_lactating:
            methane_models = methane_models["lactating cows"]
            methane_emissions = EntericMethaneCalculator._calculate_lactating_cow_enteric_methane(
                body_weight,
                milk_fat,
                metabolizable_energy_intake,
                nutrient_amounts,
                methane_models,
            )
            if methane_mitigation_method:
                for method, result in methane_emissions.items():
                    methane_yield = 0.0
                    methane_yield_reduction = 0.0
                    if dry_matter_intake != 0:
                        methane_yield = result / dry_matter_intake
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

                    methane_emissions[method] = methane_emission
        else:
            methane_models = methane_models["dry cows"]
            methane_emissions = EntericMethaneCalculator._calculate_dry_cow_enteric_methane(
                methane_models, metabolizable_energy_intake, nutrient_amounts
            )

        return methane_emissions

    @staticmethod
    def _calculate_lactating_cow_enteric_methane(
        body_weight: float,
        milk_fat: float,
        metabolizable_energy_intake: float,
        nutrient_amounts: NutritionSupply,
        methane_models: dict[str, bool],
    ) -> dict[str, float]:
        """
        Calculates the daily enteric emissions for lactating cows.

        Notes
        -----
        Soluble residue: [AN.MET.1]
        Gross energy concentration: [AN.MET.2]
        Starch to acid detergent fiber concentration ratio: [AN.MET.3]
        Enteric methane emission, Mutian Model:  [AN.MET.6]
        Enteric methane emission, Mills Model:  [AN.MET.7]
        Enteric methane emission, IPCC Model:  [AN.MET.5]

        The dry matter ("dm") unit is kg per animal. Crude protein ("CP"), ADF, NDF, lignin, ash, phosphorus, potassium,
        and nitrogen ("N") are all percentages of dry matter.

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
        dict[str, float]
            The daily enteric emissions for lactating cows (g/day).

        References
        ----------
        (Niu et al., 2018; Mills et al., 2003; IPCC, 2006)

        """
        dry_matter_intake = nutrient_amounts.dry_matter
        ash_concentration = nutrient_amounts.ash_percentage
        acid_detergent_fiber_concentration = nutrient_amounts.adf_percentage
        crude_protein_concentration = nutrient_amounts.crude_protein_percentage
        neutral_detergent_fiber_concentration = nutrient_amounts.ndf_percentage
        ethyl_ester_concentration = nutrient_amounts.fat_percentage
        starch_concentration = nutrient_amounts.starch_percentage
        methane_results = {}
        for model, usage in methane_models.items():
            if usage:
                if model == "Mutian":
                    methane_emission = (
                        -126
                        + 11.3 * dry_matter_intake
                        + 2.30 * neutral_detergent_fiber_concentration
                        + 28.8 * milk_fat
                        + 0.148 * body_weight
                    )
                elif model == "Mills":
                    mitscherlich_parameter_a = animal_constants.MITS_PARAMETER_A
                    mitscherlich_parameter_b = animal_constants.MITS_PARAMETER_B
                    mitscherlich_parameter_c = (
                        -0.0011 * starch_concentration / acid_detergent_fiber_concentration + 0.0045
                    )
                    methane_emission_MJ = mitscherlich_parameter_a - (
                        mitscherlich_parameter_a + mitscherlich_parameter_b
                    ) * exp(-mitscherlich_parameter_c * metabolizable_energy_intake * GeneralConstants.KCAL_TO_MJ)
                    methane_emission = methane_emission_MJ / GeneralConstants.MJ_CH4_TO_G_CH4
                else:
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
                    methane_emission = (
                        0.065 * gross_energy_concentration * dry_matter_intake / GeneralConstants.MJ_CH4_TO_G_CH4
                    )
                methane_results[model] = methane_emission
            else:
                methane_results[model] = 0.0

        return methane_results

    @staticmethod
    def _calculate_dry_cow_enteric_methane(
        methane_models: dict[str, bool],
        metabolizable_energy_intake: float,
        nutrient_amounts: NutritionSupply,
    ) -> dict[str, float]:
        """
        Calculates the daily enteric methane emissions for dry cows.

        Notes
        -----
        Soluble residue: [AN.MET.1]
        Gross energy concentration: [AN.MET.2]
        Starch to acid detergent fiber concentration ratio: [AN.MET.3]
        Enteric methane emission, Mills Model:  [AN.MET.7]
        Enteric methane emission, IPCC Model:  [AN.MET.5]

        The dry matter ("dm") unit is kg per animal. Crude protein ("CP"), ADF, NDF, lignin, ash, phosphorus, potassium,
        and nitrogen ("N") are all percentages of dry matter.

        Parameters
        ----------
        methane_models: str
            Methane model used for methane emission calculations, including Mills, IPCC.
        metabolizable_energy_intake: float
            Metabolizable energy intake, Mcal/kg dry matter.
        nutrient_amounts: Dict[str, float]
            Amounts of nutrients in pen ration, calculated per animal, see Notes section for units.

        Returns
        -------
        float
            The daily enteric emissions for dry cows (g/day).


        References
        ----------
        (Mills et al., 2003; IPCC, 2006)

        """
        dry_matter_intake = nutrient_amounts.dry_matter
        ash_concentration = nutrient_amounts.ash_percentage
        acid_detergent_fiber_concentration = nutrient_amounts.adf_percentage
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
        methane_results = {}
        for model, usage in methane_models.items():
            if usage:
                if model == "Mills":
                    mitscherlich_parameter_a = animal_constants.MITS_PARAMETER_A
                    mitscherlich_parameter_b = animal_constants.MITS_PARAMETER_B
                    mitscherlich_parameter_c = (
                        -0.0011 * starch_concentration / acid_detergent_fiber_concentration + 0.0045
                    )
                    methane_emission_MJ = mitscherlich_parameter_a - (
                        mitscherlich_parameter_a + mitscherlich_parameter_b
                    ) * exp(-mitscherlich_parameter_c * metabolizable_energy_intake * GeneralConstants.KCAL_TO_MJ)
                    methane_emission = methane_emission_MJ / GeneralConstants.MJ_CH4_TO_G_CH4
                else:
                    gross_energy_concentration = (
                        0.263 * crude_protein_concentration
                        + 0.522 * ethyl_ester_concentration
                        + 0.198 * neutral_detergent_fiber_concentration
                        + 0.160 * soluble_residue
                    )
                    methane_emission = (
                        0.065 * gross_energy_concentration * dry_matter_intake
                    ) / GeneralConstants.MJ_CH4_TO_G_CH4
                methane_results[model] = methane_emission
            else:
                methane_results[model] = 0.0

        return methane_results
