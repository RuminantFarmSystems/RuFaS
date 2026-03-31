from typing import Any

from numpy import exp

from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionSupply
from RUFAS.biophysical.animal.digestive_system.methane_mitigation_calculator import MethaneMitigationCalculator
from RUFAS.general_constants import GeneralConstants
from RUFAS.biophysical.animal import animal_constants


class EntericMethaneCalculator:
    @staticmethod
    def calculate_calf_methane(methane_model: str, body_weight: float) -> float:
        """
        Calculates the amount of methane emission for calf.

        Parameters
        ----------
        methane_model: str
            Methane model used for methane emission calculations.
        body_weight: float
            Body weight of the current animal, kg.

        Returns
        -------
        float
            The amount of methane emission for calf (g/day).

        References
        ----------
        (Pattanaik et al., 2003)
        [AN.MET.4]

        """
        if methane_model == "Pattanaik":
            methane_emission = (
                0.013 * (body_weight**0.75) * GeneralConstants.KCAL_TO_MJ
            ) / GeneralConstants.MJ_CH4_TO_G_CH4
            return methane_emission
        else:
            return 0.0

    @staticmethod
    def calculate_heifer_methane(
        methane_model: str,
        nutrition_supply: NutritionSupply,
    ) -> float:
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
        methane_model: str
            Model for methane prediction.
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
        if methane_model == "IPCC":
            return EntericMethaneCalculator._calculate_IPCC_methane(nutrition_supply)
        else:
            return 0.0

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
    ) -> float:
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
        methane_models: dict[str, Any]
            Methane model used for methane emission calculations.
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

        """
        dry_matter_intake = nutrient_amounts.dry_matter
        neutral_detergent_fiber_concentration = nutrient_amounts.ndf_percentage
        ethyl_ester_concentration = nutrient_amounts.fat_percentage
        starch_concentration = nutrient_amounts.starch_percentage
        methane_models = methane_models["cows"]

        if is_lactating:
            methane_models = methane_models["lactating cows"]
            methane_emission = EntericMethaneCalculator._calculate_lactating_cow_enteric_methane(
                body_weight,
                milk_fat,
                metabolizable_energy_intake,
                nutrient_amounts,
                methane_models,
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
            methane_models = methane_models["dry cows"]
            methane_emission = EntericMethaneCalculator._calculate_dry_cow_enteric_methane(
                methane_models, metabolizable_energy_intake, nutrient_amounts
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
        Soluble residue: [AN.MET.1]
        Gross energy concentration: [AN.MET.2]
        Starch to acid detergent fiber concentration ratio: [AN.MET.3]
        Enteric methane emission, Mutian Model:  [AN.MET.6]
        Enteric methane emission, Mills Model:  [AN.MET.7]
        Enteric methane emission, IPCC Model:  [AN.MET.5]

        The dry matter ("dm") unit is kg per animal. Crude protein ("CP"), ADF, NDF, lignin, ash, phosphorus, potassium,
        and nitrogen ("N") are all percentages of dry matter.

        References
        ----------
        (Niu et al., 2018; Mills et al., 2003; IPCC, 2006)

        """
        dry_matter_intake = nutrient_amounts.dry_matter
        neutral_detergent_fiber_concentration = nutrient_amounts.ndf_percentage
        if methane_model == "Mutian":
            methane_emission = (
                -126
                + 11.3 * dry_matter_intake
                + 2.30 * neutral_detergent_fiber_concentration
                + 28.8 * milk_fat
                + 0.148 * body_weight
            )
            return methane_emission
        elif methane_model == "Mills":
            return EntericMethaneCalculator._calculate_cow_mills_methane(nutrient_amounts, metabolizable_energy_intake)
        else:
            return EntericMethaneCalculator._calculate_IPCC_methane(nutrient_amounts)

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
            Methane model used for methane emission calculations.
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
        Soluble residue: [AN.MET.1]
        Gross energy concentration: [AN.MET.2]
        Starch to acid detergent fiber concentration ratio: [AN.MET.3]
        Enteric methane emission, Mills Model:  [AN.MET.7]
        Enteric methane emission, IPCC Model:  [AN.MET.5]

        The dry matter ("dm") unit is kg per animal. Crude protein ("CP"), ADF, NDF, lignin, ash, phosphorus, potassium,
        and nitrogen ("N") are all percentages of dry matter.

        """
        if methane_model == "Mills":
            return EntericMethaneCalculator._calculate_cow_mills_methane(nutrient_amounts, metabolizable_energy_intake)
        else:
            return EntericMethaneCalculator._calculate_IPCC_methane(nutrient_amounts)

    @staticmethod
    def _calculate_cow_mills_methane(nutrient_amounts: NutritionSupply, metabolizable_energy_intake: float) -> float:
        """
        Return the amount of cow methane predicted my Mills method.

        Parameters
        ----------
        nutrient_amounts: Dict[str, float]
            Amounts of nutrients in pen ration, calculated per animal, see Notes section for units.
        metabolizable_energy_intake : float
            Metabolizable energy intake, Mcal/kg dry matter.

        Returns
        -------
        float
            The daily enteric emissions for cows (g/day).

        References
        ----------
        Mills et al., 2003

        """
        starch_concentration = nutrient_amounts.starch_percentage
        acid_detergent_fiber_concentration = nutrient_amounts.adf_percentage
        mitscherlich_parameter_a = animal_constants.MITS_PARAMETER_A
        mitscherlich_parameter_b = animal_constants.MITS_PARAMETER_B
        mitscherlich_parameter_c = -0.0011 * starch_concentration / acid_detergent_fiber_concentration + 0.0045
        methane_emission_MJ = mitscherlich_parameter_a - (mitscherlich_parameter_a + mitscherlich_parameter_b) * exp(
            -mitscherlich_parameter_c * metabolizable_energy_intake * GeneralConstants.KCAL_TO_MJ
        )
        methane_emission = methane_emission_MJ / GeneralConstants.MJ_CH4_TO_G_CH4
        return methane_emission

    @staticmethod
    def _calculate_IPCC_methane(
        nutrient_amounts: NutritionSupply,
    ) -> float:
        """
        Return the amount of methane predicted my IPCC method.

        Parameters
        ----------
        nutrient_amounts: Dict[str, float]
            Amounts of nutrients in pen ration, calculated per animal, see Notes section for units.

        Returns
        -------
        float
            The daily enteric emissions (g/day).

        References
        ----------
        IPCC, 2006

        """
        dry_matter_intake = nutrient_amounts.dry_matter
        ash_concentration = nutrient_amounts.ash_percentage
        crude_protein_concentration = nutrient_amounts.crude_protein_percentage
        neutral_detergent_fiber_concentration = nutrient_amounts.ndf_percentage
        ethyl_ester_concentration = nutrient_amounts.fat_percentage
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
        methane_emission = (0.065 * gross_energy_concentration * dry_matter_intake) / GeneralConstants.MJ_CH4_TO_G_CH4
        return methane_emission
