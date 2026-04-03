from typing import Tuple

from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionSupply
from RUFAS.biophysical.animal.data_types.animal_manure_excretions import AnimalManureExcretions

from RUFAS.general_constants import GeneralConstants
from RUFAS.user_constants import UserConstants


class ManureExcretionCalculator:
    @staticmethod
    def calculate_calf_manure(
        body_weight: float,
        fecal_phosphorus: float,
        urine_phosphorus_required: float,
        nutrient_amounts: NutritionSupply,
    ) -> Tuple[float, AnimalManureExcretions]:
        """
        Calculates the manure excretion values for a calf with information from the ration formulation.

        Notes
        -----
        Manure excretion: [AN.EXC.1]
        Urine excretion: [AN.EXC.2]
        Manure total solids excretion: [AN.EXC.3]
        Total volatile solids: [AN.EXC.4]
        Degradable volatile solids excretion: [AN.EXC.5]
        Non-degradable volatile solids excretion: [AN.EXC.6]
        Manure nitrogen excretion: [AN.EXC.7]
        Urine N excretion: [AN.EXC.8]
        Manure total ammoniacal nitrogen: [AN.EXC.9]

        Parameters
        ----------
        body_weight : float
            Body weight of the current animal, kg.
        fecal_phosphorus : float
            Amount of fecal phosphorus excreted by the current animal, g.
        urine_phosphorus_required : float
            Amount of phosphorus required for urine production, g.
        nutrient_amounts : NutritionSupply
            Amounts of nutrients in pen ration, calculated per animal, see Notes section for units.

        Returns
        -------
        float
            Total amount of phosphorus excreted by the given animal, g.
        AnimalManureExcretions
            A dictionary that contains the manure excretion values as specified
                in the AnimalManureExcretions class definition.

        References
        ----------
        (ASABE, 2003; Nennich et al., 2005)

        """
        dry_matter_intake = nutrient_amounts.dry_matter
        crude_protein_concentration = nutrient_amounts.crude_protein_percentage

        total_manure_excreted = 3.45 * dry_matter_intake

        urine = 2.0

        total_solids = 0.393 * dry_matter_intake

        total_volatile_solids = 0.0023 * body_weight

        degradable_volatile_solids = 0.9 * total_volatile_solids

        non_degradable_volatile_solids = total_volatile_solids - degradable_volatile_solids

        manure_nitrogen = (
            112.55 * dry_matter_intake * (crude_protein_concentration * GeneralConstants.PERCENTAGE_TO_FRACTION)
        ) * GeneralConstants.GRAMS_TO_KG

        urine_nitrogen = 0.45 * manure_nitrogen

        manure_total_ammoniacal_nitrogen = urine_nitrogen

        phosphorus_excretion_values = ManureExcretionCalculator._calculate_phosphorus_excretion_values(
            daily_milk_production=0,
            total_manure_excreted=total_manure_excreted,
            fecal_phosphorus=fecal_phosphorus,
            urine_phosphorus_required=urine_phosphorus_required,
        )

        (
            total_phosphorus_excreted,
            inorganic_phosphorus_fraction,
            organic_phosphorus_fraction,
            manure_phosphorus_excreted,
            manure_phosphorus_fraction,
        ) = phosphorus_excretion_values

        manure_excretion_values = AnimalManureExcretions(
            urea=9.52,  # 0.340 mol/L TODO: Implement with correct equation GitHub Issue # 1216
            urine=urine,
            # TODO: Implement with correct equation GitHub Issue # 1216
            manure_total_ammoniacal_nitrogen=manure_total_ammoniacal_nitrogen,
            urine_nitrogen=urine_nitrogen,
            manure_nitrogen=manure_nitrogen,
            manure_mass=total_manure_excreted,
            total_solids=total_solids,
            degradable_volatile_solids=degradable_volatile_solids,
            non_degradable_volatile_solids=non_degradable_volatile_solids,
            inorganic_phosphorus_fraction=inorganic_phosphorus_fraction,
            organic_phosphorus_fraction=organic_phosphorus_fraction,
            non_water_inorganic_phosphorus_fraction=0.0,
            non_water_organic_phosphorus_fraction=0.0,
            phosphorus=manure_phosphorus_excreted,
            phosphorus_fraction=manure_phosphorus_fraction,
            potassium=0,
        )

        return total_phosphorus_excreted, manure_excretion_values

    @staticmethod
    def calculate_heifer_manure(
        body_weight: float,
        fecal_phosphorus: float,
        urine_phosphorus_required: float,
        nutrient_amount: NutritionSupply,
    ) -> Tuple[float, AnimalManureExcretions]:
        """
        Calculates the manure excretion values for a growing and close-up heifer with information from the ration
        formulation.

        Notes
        -----
        Urine excretion: [AN.EXC.10]
        Total manure excretion: [AN.EXC.11]
        Total solids excretion: [AN.EXC.12]
        Total volatile solids excretion: [AN.EXC.13]
        Degradable volatile solids excretion: [AN.EXC.5]
        Non-degradable volatile solids excretion: [AN.EXC.6]
        Manure N excretion: [AN.EXC.14]
        Fecal N excretion: [AN.EXC.15]
        Urine N excretion: [AN.EXC.16]
        Manure total ammoniacal nitrogen: [AN.EXC.9]
        Manure K excretion: [AN.EXC.17]

        Parameters
        ----------
        body_weight : float
            Body weight of the current animal, kg.
        fecal_phosphorus : float
            Amount of fecal phosphorus excreted by the current animal, g.
        urine_phosphorus_required : float
            Amount of phosphorus required for urine production, g.
        nutrient_amount : NutritionSupply
            Amounts of nutrients in pen ration, calculated per animal, see Notes section for units.

        Returns
        -------
        float
            Total amount of phosphorus excreted by the given animal, g.
        AnimalManureExcretions
            A dictionary that contains the manure excretion values as specified
                in the AnimalManureExcretions class definition.

        Notes
        -----
        The dry matter ("dm") unit is kg per animal. Crude protein ("CP"), ADF, NDF, lignin, ash, phosphorus, potassium,
        and nitrogen ("N") are all percentages of dry matter.

        References
        ----------
        (ASABE, 2005; Nennich et al., 2005; Reed et al., 2015; Johnson et al., 2016; NASEM, 2021)

        """
        # TODO: Same TODOs as in dry_cow_manure_excretion.py - GitHub Issue #1219
        dry_matter_intake = nutrient_amount.dry_matter
        crude_protein_concentration = nutrient_amount.crude_protein_percentage
        potassium_concentration = nutrient_amount.potassium_percentage

        urine = 9.0

        total_manure_excreted = 4.158 * dry_matter_intake - 0.0246 * body_weight

        total_solids = 0.178 * dry_matter_intake + 2.733

        total_manure_excreted = max(
            total_manure_excreted, (total_solids / AnimalModuleConstants.MAXMIMUM_MANURE_DRY_MATTER_CONTENT)
        )

        total_volatile_solids = 0.0073 * body_weight

        degradable_volatile_solids = 0.9 * total_volatile_solids

        non_degradable_volatile_solids = total_volatile_solids - degradable_volatile_solids

        manure_nitrogen = (
            15.1
            + 0.83
            * (dry_matter_intake * GeneralConstants.KG_TO_GRAMS)
            * (crude_protein_concentration * UserConstants.PROTEIN_TO_NITROGEN)
            * GeneralConstants.PERCENTAGE_TO_FRACTION
        ) * GeneralConstants.GRAMS_TO_KG

        fecal_nitrogen = (
            0.345
            + 0.317
            * (dry_matter_intake * GeneralConstants.KG_TO_GRAMS)
            * (crude_protein_concentration * UserConstants.PROTEIN_TO_NITROGEN)
            * GeneralConstants.PERCENTAGE_TO_FRACTION
        ) * GeneralConstants.GRAMS_TO_KG

        urine_nitrogen = manure_nitrogen - fecal_nitrogen

        urinary_nitrogen_concentration = (urine_nitrogen * GeneralConstants.KG_TO_GRAMS) / urine

        urine_urea_nitrogen_concentration = -1.16 + 0.86 * urinary_nitrogen_concentration

        manure_total_ammoniacal_nitrogen = urine_nitrogen

        potassium = (
            dry_matter_intake
            * (potassium_concentration * GeneralConstants.PERCENTAGE_TO_FRACTION)
            * GeneralConstants.KG_TO_GRAMS
        )

        phosphorus_excretion_values = ManureExcretionCalculator._calculate_phosphorus_excretion_values(
            daily_milk_production=0,
            total_manure_excreted=total_manure_excreted,
            fecal_phosphorus=fecal_phosphorus,
            urine_phosphorus_required=urine_phosphorus_required,
        )

        (
            total_phosphorus_excreted,
            inorganic_phosphorus_fraction,
            organic_phosphorus_fraction,
            manure_phosphorus_excreted,
            manure_phosphorus_fraction,
        ) = phosphorus_excretion_values

        manure_excretion_values = AnimalManureExcretions(
            urea=urine_urea_nitrogen_concentration,
            urine=urine,
            manure_total_ammoniacal_nitrogen=manure_total_ammoniacal_nitrogen,
            urine_nitrogen=urine_nitrogen,
            manure_nitrogen=manure_nitrogen,
            manure_mass=total_manure_excreted,
            total_solids=total_solids,
            degradable_volatile_solids=degradable_volatile_solids,
            non_degradable_volatile_solids=non_degradable_volatile_solids,
            inorganic_phosphorus_fraction=inorganic_phosphorus_fraction,
            organic_phosphorus_fraction=organic_phosphorus_fraction,
            non_water_inorganic_phosphorus_fraction=0.0,
            non_water_organic_phosphorus_fraction=0.0,
            phosphorus=manure_phosphorus_excreted,
            phosphorus_fraction=manure_phosphorus_fraction,
            potassium=potassium,
        )

        return total_phosphorus_excreted, manure_excretion_values

    @staticmethod
    def calculate_cow_manure(
        is_lactating: bool,
        body_weight: float,
        days_in_milk: int,
        milk_protein: float,
        daily_milk_production: float,
        fecal_phosphorus: float,
        urine_phosphorus_required: float,
        nutrient_amounts: NutritionSupply,
    ) -> Tuple[float, AnimalManureExcretions]:
        """
        Calculates the manure excretion values for a cow with information from the ration formulation.

        Notes
        -----
        The dry matter ("dm") unit is kg per animal. Crude protein ("CP"), ADF, NDF, lignin, ash, phosphorus, potassium,
        and nitrogen ("N") are all percentages of dry matter.

        Parameters
        ----------
        is_lactating: bool
            Indicates cow's lactating status.
        body_weight: float
            Body weight of the current animal (kg).
        days_in_milk: int
            Days in milk.
        milk_protein: float
            Milk protein (from animal input), % of milk.
        daily_milk_production: float
            Daily milk production of the current cow (kg).
        fecal_phosphorus: float
            Amount of fecal phosphorus excreted by the current cow (g).
        urine_phosphorus_required: float
            Amount of phosphorus required for urine production (g).
        nutrient_amounts: NutritionSupply
            Amounts of nutrients in pen ration, calculated per animal, see Notes section for units.

        Returns
        -------
        float
            Total amount of phosphorus excreted by the given animal (g).

        AnimalManureExcretions
            A dictionary that contains the manure excretion values as specified
                in the AnimalManureExcretions class definition.

        """
        if is_lactating:
            return ManureExcretionCalculator._calculate_lactating_cow_manure(
                days_in_milk,
                milk_protein,
                daily_milk_production,
                fecal_phosphorus,
                urine_phosphorus_required,
                nutrient_amounts,
            )
        else:
            return ManureExcretionCalculator._calculate_dry_cow_manure(
                body_weight,
                daily_milk_production,
                fecal_phosphorus,
                urine_phosphorus_required,
                nutrient_amounts,
            )

    @staticmethod
    def _calculate_lactating_cow_manure(
        days_in_milk: int,
        milk_protein: float,
        daily_milk_production: float,
        fecal_phosphorus: float,
        urine_phosphorus_required: float,
        nutrient_amounts: NutritionSupply,
    ) -> Tuple[float, AnimalManureExcretions]:
        """
        Calculates the manure excretion values for a lactating cow with information from the ration formulation.

        Notes
        -----
        Fecal water excretion: [AN.EXC.18]
        Total solids/Fecal dry matter: [AN.EXC.19]
        Urine excretion: [AN.EXC.20]
        Total manure excretion: [AN.EXC.21]
        Organic matter intake: [AN.EXC.22]
        Degradable volatile solids: [AN.EXC.23]
        Total volatile solids excretion: [AN.EXC.24]
        Non-degradable volatile solids excretion: [AN.EXC.6]
        Manure N excretion: [AN.EXC.25]
        Fecal nitrogen: [AN.EXC.26]
        Urinary nitrogen: [AN.EXC.16]
        Manure total ammoniacal nitrogen: [AN.EXC.9]
        Manure K excretion: [AN.EXC.27]

        The dry matter ("dm") unit is kg per animal. Crude protein ("CP"), ADF, NDF, lignin, ash, phosphorus, potassium,
        and nitrogen ("N") are all percentages of dry matter.

        Parameters
        ----------
        days_in_milk : int
            Days in milk, days.
        milk_protein : float
            Milk protein (from animal input), % of milk.
        daily_milk_production : float
            Daily milk production of the current cow, kg.
        fecal_phosphorus : float
            Amount of fecal phosphorus excreted by the current cow, g.
        urine_phosphorus_required : float
            Amount of phosphorus required for urine production, g.
        nutrient_amounts : Dict[str, float]
            Amounts of nutrients in pen ration, calculated per animal, see Notes section for units.
        nutrient_concentrations : Dict[str, float]
            Concentrations of nutrients in pen ration, calculated per animal, percentages.

        Returns
        -------
        float
            Total amount of phosphorus excreted by the given animal, g.
        AnimalManureExcretions
            A dictionary that contains the manure excretion values as specified
                in the AnimalManureExcretions class definition.

        References
        ----------
        (Nennich et al., 2005; Appuhamy et al., 2014; Reed et al., 2015; Appuhamy et al., 2018)

        """
        dry_matter_intake = nutrient_amounts.dry_matter
        ash_diet_content = nutrient_amounts.ash_supply
        dry_matter_concentration = nutrient_amounts.dry_matter_percentage
        acid_detergent_fiber_concentrations = nutrient_amounts.adf_percentage
        crude_protein_concentration = nutrient_amounts.crude_protein_percentage
        neutral_detergent_fiber_concentration = nutrient_amounts.ndf_percentage
        potassium_concentration = nutrient_amounts.potassium_percentage

        fecal_water = (
            1.987 * dry_matter_intake
            + 0.348 * acid_detergent_fiber_concentrations
            - 0.412 * crude_protein_concentration
            - 0.074 * dry_matter_concentration
            - 0.0057 * days_in_milk
        )

        fecal_solids = (
            -0.576
            + 0.370 * dry_matter_intake
            - 0.075 * crude_protein_concentration
            + 0.059 * acid_detergent_fiber_concentrations
        )

        urine = -7.742 + 0.388 * dry_matter_intake + 0.726 * crude_protein_concentration + 2.066 * milk_protein

        total_manure_excreted = fecal_water + fecal_solids + urine

        manure_nitrogen = (
            20.3
            + 0.654
            * (dry_matter_intake * GeneralConstants.KG_TO_GRAMS)
            * (crude_protein_concentration * UserConstants.PROTEIN_TO_NITROGEN)
            * GeneralConstants.PERCENTAGE_TO_FRACTION
        ) * GeneralConstants.GRAMS_TO_KG

        dry_matter_intake = max(dry_matter_intake, AnimalModuleConstants.MINIMUM_DMI_LACT)
        fecal_nitrogen = (-18.5 + 10.1 * dry_matter_intake) * GeneralConstants.GRAMS_TO_KG

        urine_nitrogen = manure_nitrogen - fecal_nitrogen

        organic_matter_intake = dry_matter_intake - ash_diet_content

        degradable_volatile_solids = (
            -1.017
            + 0.364 * organic_matter_intake
            + 0.029 * neutral_detergent_fiber_concentration
            - 0.023 * crude_protein_concentration
        )

        total_volatile_solids = (
            -1.201
            + 0.402 * organic_matter_intake
            + 0.036 * neutral_detergent_fiber_concentration
            - 0.024 * crude_protein_concentration
        )

        non_degradable_volatile_solids = total_volatile_solids - degradable_volatile_solids

        urinary_nitrogen_concentration = (urine_nitrogen * GeneralConstants.KG_TO_GRAMS) / urine

        urine_urea_nitrogen_concentration = -1.16 + 0.86 * urinary_nitrogen_concentration

        manure_total_ammoniacal_nitrogen = urine_nitrogen

        potassium = (
            7.21 * dry_matter_intake + 15944 * potassium_concentration * GeneralConstants.PERCENTAGE_TO_FRACTION - 164.5
        )

        phosphorus_excretion_values = ManureExcretionCalculator._calculate_phosphorus_excretion_values(
            daily_milk_production=daily_milk_production,
            total_manure_excreted=total_manure_excreted,
            fecal_phosphorus=fecal_phosphorus,
            urine_phosphorus_required=urine_phosphorus_required,
        )

        (
            total_phosphorus_excreted,
            inorganic_phosphorus_fraction,
            organic_phosphorus_fraction,
            manure_phosphorus_excreted,
            manure_phosphorus_fraction,
        ) = phosphorus_excretion_values

        manure_excretion_values = AnimalManureExcretions(
            urea=urine_urea_nitrogen_concentration,
            urine=urine,
            manure_total_ammoniacal_nitrogen=manure_total_ammoniacal_nitrogen,
            urine_nitrogen=urine_nitrogen,
            manure_nitrogen=manure_nitrogen,
            manure_mass=total_manure_excreted,
            total_solids=fecal_solids,
            degradable_volatile_solids=degradable_volatile_solids,
            non_degradable_volatile_solids=non_degradable_volatile_solids,
            inorganic_phosphorus_fraction=inorganic_phosphorus_fraction,
            organic_phosphorus_fraction=organic_phosphorus_fraction,
            non_water_inorganic_phosphorus_fraction=0.0,
            non_water_organic_phosphorus_fraction=0.0,
            phosphorus=manure_phosphorus_excreted,
            phosphorus_fraction=manure_phosphorus_fraction,
            potassium=potassium,
        )

        return total_phosphorus_excreted, manure_excretion_values

    @staticmethod
    def _calculate_dry_cow_manure(
        body_weight: float,
        daily_milk_production: float,
        fecal_phosphorus: float,
        urine_phosphorus_required: float,
        nutrient_amounts: NutritionSupply,
    ) -> Tuple[float, AnimalManureExcretions]:
        """Calculates the manure excretion values for a non-lactating cow with information from the ration formulation.

        Notes
        -----
        Urine excretion: [AN.EXC.28]
        Total manure excretion: [AN.EXC.29]
        Total solids excretion: [AN.EXC.12]
        Organic matter intake: [AN.EXC.22]
        Degradable volatile solids: [AN.EXC.23]
        Total volatile solids excretion: [AN.EXC.24]
        Non-degradable volatile solids excretion: [AN.EXC.6]
        Manure N excretion: [AN.EXC.14]
        Fecal nitrogen: [AN.EXC.15]
        Urinary nitrogen: [AN.EXC.16]
        Manure total ammoniacal nitrogen: [AN.EXC.9]
        Manure K excretion: [AN.EXC.17]

        The dry matter ("dm") unit is kg per animal. Crude protein ("CP"), ADF, NDF, lignin, ash, phosphorus, potassium,
        and nitrogen ("N") are all percentages of dry matter.

        Parameters
        ----------
        body_weight : float
            Body weight of the current animal, kg.
        daily_milk_production : float
            Daily milk production of the current animal, kg.
        fecal_phosphorus : float
            Amount of fecal phosphorus excreted by the current animal, g.
        urine_phosphorus_required : float
            Amount of phosphorus required for urine production, g.
        nutrient_amounts: Dict[str, float]
            Amounts of nutrients in pen ration, calculated per animal, see Notes section for units.
        nutrient_concentrations: Dict[str, float]
            Concentrations of nutrients in pen ration, calculated per animal, percentages.

        Returns
        -------
        float
            Total amount of phosphorus excreted by the given animal, g.
        AnimalManureExcretions
            A dictionary that contains the manure excretion values as specified
                in the AnimalManureExcretions class definition.

        References
        ----------
        (Wilkerson et al., 1997; Nennich et al., 2005; Appuhamy et al., 2014; Reed et al., 2015;
        Johnson et al., 2016; Appuhamy et al., 2018; NASEM, 2021)

        """
        # TODO: Add TypedDicts for ration_formulation and available feeds - GitHub Issue #1218
        # TODO: Pass in available feeds directly instead of a Feed object - GitHub Issue #1218
        # TODO: Rename abbreviated key names to full names - GitHub Issue #1218
        dry_matter_intake = nutrient_amounts.dry_matter
        crude_protein_concentration = nutrient_amounts.crude_protein_percentage
        potassium_concentration = nutrient_amounts.potassium_percentage
        ash_concentration = nutrient_amounts.ash_percentage
        neutral_detergent_fiber_concentration = nutrient_amounts.ndf_percentage

        # TODO: Further calculations to account for entire diet:- GitHub Issue #1218
        urine = 15.4

        total_manure_excreted = (
            0.00711 * body_weight
            + 0.324 * crude_protein_concentration
            + 0.259 * neutral_detergent_fiber_concentration
            + 8.05
        )

        total_solids = 0.178 * dry_matter_intake + 2.733

        total_manure_excreted = max(
            total_manure_excreted, (total_solids / AnimalModuleConstants.MAXMIMUM_MANURE_DRY_MATTER_CONTENT)
        )

        dry_matter_intake = max(dry_matter_intake, AnimalModuleConstants.MINIMUM_DMI_DRY)
        organic_matter_intake = (
            dry_matter_intake
            * (GeneralConstants.FRACTION_TO_PERCENTAGE - ash_concentration)
            * GeneralConstants.PERCENTAGE_TO_FRACTION
        )

        total_volatile_solids = (
            -1.201
            + 0.402 * organic_matter_intake
            + 0.036 * neutral_detergent_fiber_concentration
            - 0.024 * crude_protein_concentration
        )

        degradable_volatile_solids = (
            -1.017
            + 0.364 * organic_matter_intake
            + 0.029 * neutral_detergent_fiber_concentration
            - 0.023 * crude_protein_concentration
        )

        non_degradable_volatile_solids = total_volatile_solids - degradable_volatile_solids

        manure_nitrogen = (
            15.1
            + 0.83
            * (dry_matter_intake * GeneralConstants.KG_TO_GRAMS)
            * (crude_protein_concentration * UserConstants.PROTEIN_TO_NITROGEN)
            / GeneralConstants.FRACTION_TO_PERCENTAGE
        ) * GeneralConstants.GRAMS_TO_KG

        fecal_nitrogen = (
            0.345
            + 0.317
            * (dry_matter_intake * GeneralConstants.KG_TO_GRAMS)
            * (crude_protein_concentration * UserConstants.PROTEIN_TO_NITROGEN)
            * GeneralConstants.PERCENTAGE_TO_FRACTION
        ) * GeneralConstants.GRAMS_TO_KG

        urine_nitrogen = manure_nitrogen - fecal_nitrogen

        urinary_nitrogen_concentration = (urine_nitrogen * GeneralConstants.KG_TO_GRAMS) / urine

        urine_urea_nitrogen_concentration = -1.16 + 0.86 * urinary_nitrogen_concentration

        manure_total_ammoniacal_nitrogen = urine_nitrogen

        potassium = (
            dry_matter_intake
            * (potassium_concentration * GeneralConstants.PERCENTAGE_TO_FRACTION)
            * GeneralConstants.KG_TO_GRAMS
        )

        phosphorus_excretion_values = ManureExcretionCalculator._calculate_phosphorus_excretion_values(
            daily_milk_production=daily_milk_production,
            total_manure_excreted=total_manure_excreted,
            fecal_phosphorus=fecal_phosphorus,
            urine_phosphorus_required=urine_phosphorus_required,
        )

        (
            total_phosphorus_excreted,
            inorganic_phosphorus_fraction,
            organic_phosphorus_fraction,
            manure_phosphorus_excreted,
            manure_phosphorus_fraction,
        ) = phosphorus_excretion_values

        manure_excretion_values = AnimalManureExcretions(
            urea=urine_urea_nitrogen_concentration,
            urine=urine,
            manure_total_ammoniacal_nitrogen=manure_total_ammoniacal_nitrogen,
            urine_nitrogen=urine_nitrogen,
            manure_nitrogen=manure_nitrogen,
            manure_mass=total_manure_excreted,
            total_solids=total_solids,
            degradable_volatile_solids=degradable_volatile_solids,
            non_degradable_volatile_solids=non_degradable_volatile_solids,
            inorganic_phosphorus_fraction=inorganic_phosphorus_fraction,
            organic_phosphorus_fraction=organic_phosphorus_fraction,
            non_water_inorganic_phosphorus_fraction=0.0,
            non_water_organic_phosphorus_fraction=0.0,
            phosphorus=manure_phosphorus_excreted,
            phosphorus_fraction=manure_phosphorus_fraction,
            potassium=potassium,
        )

        return total_phosphorus_excreted, manure_excretion_values

    @staticmethod
    def _calculate_phosphorus_excretion_values(
        daily_milk_production: float,
        total_manure_excreted: float,
        fecal_phosphorus: float,
        urine_phosphorus_required: float,
    ) -> Tuple[float, float, float, float, float]:
        """
        Calculates a set of phosphorus excretion values produced by a given animal.

        Notes
        -----
        Total phosphorus fraction of feces: [AN.EXC.30]
        Inorganic phosphorus fraction: [AN.EXC.31]
        Organic phosphorus fraction: [AN.EXC.32]
        Milk phosphorus: [AN.EXC.33]
        Manure P excreted by a cow: [AN.EXC.34]
        Total P excreted by a cow: [AN.EXC.35]

        Parameters
        ----------
        daily_milk_production : float
            Amount of daily milk produced by the animal, kg.
            This parameter should be set to 0 if this function is called for a non-cow animal.
        total_manure_excreted : float
            Amount of manure excreted by the animal, kg.
        fecal_phosphorus : float
            Amount of fecal phosphorus excreted by the animal, g.
        urine_phosphorus_required : float
            Amount of phosphorus required for urine production, g.

        Returns
        -------
        float
            Total amount of phosphorus excreted by the animal, g.
        float
            Fraction of extractable inorganic phosphorus, unitless.
        float
            Fraction of water extractable organic phosphorus, unitless.
        float
            Amount of manure phosphorus excreted, g.
        float
            Fraction of phosphorus in the manure, unitless.

        References
        ----------
        (NRC, 2001; Vadas et al., 2007)


        """
        if total_manure_excreted > 0:
            manure_phosphorus_fraction = (fecal_phosphorus + urine_phosphorus_required) / (
                total_manure_excreted * GeneralConstants.KG_TO_GRAMS
            )
        else:
            manure_phosphorus_fraction = 0.0

        inorganic_phosphorus_fraction = 0.50 * manure_phosphorus_fraction

        organic_phosphorus_fraction = 0.05 * manure_phosphorus_fraction

        phosphorus_in_milk = 0.0009 * daily_milk_production * GeneralConstants.KG_TO_GRAMS

        manure_phosphorus_excreted = fecal_phosphorus + urine_phosphorus_required

        total_phosphorus_excreted = phosphorus_in_milk + fecal_phosphorus + urine_phosphorus_required

        return (
            total_phosphorus_excreted,
            inorganic_phosphorus_fraction,
            organic_phosphorus_fraction,
            manure_phosphorus_excreted,
            manure_phosphorus_fraction,
        )
