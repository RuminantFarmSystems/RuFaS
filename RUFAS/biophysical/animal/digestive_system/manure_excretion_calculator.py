from typing import Tuple, Dict

from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_manure_excretions import AnimalManureExcretions

from RUFAS.general_constants import GeneralConstants


class ManureExcretionCalculator:
    @staticmethod
    def calculate_calf_manure(
        body_weight: float,
        fecal_phosphorus: float,
        urine_phosphorus_required: float,
        nutrient_amounts: Dict[str, float],
        nutrient_concentrations: Dict[str, float],
    ) -> Tuple[float, AnimalManureExcretions]:
        """
        Calculates the manure excretion values for a calf with information from the ration formulation.

        Parameters
        ----------
        body_weight : float
            Body weight of the current animal, kg.
        fecal_phosphorus : float
            Amount of fecal phosphorus excreted by the current animal, g.
        urine_phosphorus_required : float
            Amount of phosphorus required for urine production, g.
        nutrient_amounts : Dict[str, float]
            Amounts of nutrients in pen ration, calculated per animal, see Notes section for units.
        nutrient_concentrations : Dict[str, float]
            Concentration of nutrients in pen ration, calculated per animal, percentages.

        Returns
        -------
        float
            Total amount of phosphorus excreted by the given animal, g.
        AnimalManureExcretions
            A dictionary that contains the manure excretion values as specified
                in the AnimalManureExcretions class definition.

        """
        dry_matter_intake = nutrient_amounts["dm"]
        crude_protein_concentration = nutrient_concentrations["CP"]

        # Manure excretion
        # Amount of feces and urine excreted daily by the calf, kg [A.3A.A.1]
        total_manure_excreted = 3.45 * dry_matter_intake

        # Total urine, kg [A.3A.A.2]
        urine = 2.0

        # Total solids excretion
        # Amount of dry material excreted by the calf, kg [A.3A.A.3]
        total_solids = 0.393 * dry_matter_intake

        # Total volatile solids, kg/day [A.3A.A.4]
        total_volatile_solids = 0.0023 * body_weight

        # Degradable volatile solids, kg/day [A.3A.A.5]
        degradable_volatile_solids = 0.9 * total_volatile_solids

        # Non-degradable volatile solids, kg/day [A.3A.A.6]
        non_degradable_volatile_solids = total_volatile_solids - degradable_volatile_solids

        # Nitrogen excretion
        # Amount of nitrogen excreted by the calf, kg [A.3A.B.1]
        manure_nitrogen = (
            112.55 * dry_matter_intake * (crude_protein_concentration * GeneralConstants.PERCENTAGE_TO_FRACTION)
        ) * GeneralConstants.GRAMS_TO_KG

        # Amount of urine nitrogen excreted by a calf, kg [A.3A.B.2]
        urine_nitrogen = 0.45 * manure_nitrogen

        # Total ammoniacal N in manure, kg
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
        nutrient_amount: dict[str, float],
        nutrient_conc: dict[str, float],
    ) -> Tuple[float, AnimalManureExcretions]:
        """
        Calculates the manure excretion values for a growing heifer with information from the ration formulation.

        Parameters
        ----------
        body_weight : float
            Body weight of the current animal, kg.
        fecal_phosphorus : float
            Amount of fecal phosphorus excreted by the current animal, g.
        urine_phosphorus_required : float
            Amount of phosphorus required for urine production, g.
        nutrient_amount : Dict[str, float]
            Amounts of nutrients in pen ration, calculated per animal, see Notes section for units.
        nutrient_conc : Dict[str, float]
            Concentrations of nutrients in pen ration, calculated per animal, percentages.

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

        """
        # TODO: Same TODOs as in dry_cow_manure_excretion.py - GitHub Issue #1219
        nutrient_amounts = nutrient_amount
        nutrient_concentrations = nutrient_conc
        dry_matter_intake = nutrient_amounts["dm"]
        crude_protein_concentration = nutrient_concentrations["CP"]
        potassium_concentration = nutrient_concentrations["potassium"]

        # Soluble residue
        # Dietary percentage of soluble residues, % DM, in the note of [A.3B.C.2]

        # Total urine, kg [A.3B.A.1]
        urine = 9.0

        # Manure excretion
        # Amount of feces and urine excreted daily by the growing heifer, kg [A.3B.A.2]
        total_manure_excreted = 4.158 * dry_matter_intake - 0.0246 * body_weight

        # Total solids excretion
        # Amount of dry material excreted by the growing heifer, kg [A.3F.A.3]
        total_solids = 0.178 * dry_matter_intake + 2.733

        # Total volatile solids, kg [A.3B.A.3]
        total_volatile_solids = 0.0073 * body_weight

        # Degradable volatile solids, kg [A.3A.A.5]
        degradable_volatile_solids = 0.9 * total_volatile_solids

        # Non-degradable volatile solids, kg [A.3A.A.6]
        non_degradable_volatile_solids = total_volatile_solids - degradable_volatile_solids

        # Nitrogen in liquid and solid manure, kg [A.3B.B.1]
        manure_nitrogen = (
            15.1
            + 0.83
            * (dry_matter_intake * GeneralConstants.KG_TO_GRAMS)
            * (crude_protein_concentration * GeneralConstants.PROTEIN_TO_NITROGEN)
            * GeneralConstants.PERCENTAGE_TO_FRACTION
        ) * GeneralConstants.GRAMS_TO_KG

        # Nitrogen excretion in feces, kg [A.3B.B.2]
        fecal_nitrogen = (
            0.345
            + 0.317
            * (dry_matter_intake * GeneralConstants.KG_TO_GRAMS)
            * (crude_protein_concentration * GeneralConstants.PROTEIN_TO_NITROGEN)
            * GeneralConstants.PERCENTAGE_TO_FRACTION
        ) * GeneralConstants.GRAMS_TO_KG

        # Nitrogen excretion in urine, kg [A.3B.B.3]
        urine_nitrogen = manure_nitrogen - fecal_nitrogen

        # Urinary N concentration, g N/kg [A.3G.B.1]
        urinary_nitrogen_concentration = (urine_nitrogen * GeneralConstants.KG_TO_GRAMS) / urine
        # Nitrogen concentration in urinary urea, g urea-N/L [A.3G.B.2]
        urine_urea_nitrogen_concentration = -1.16 + 0.86 * urinary_nitrogen_concentration

        # Total ammoniacal nitrogen in the manure slurry, kg
        manure_total_ammoniacal_nitrogen = urine_nitrogen

        # Amount of potassium excreted, g [A.3B.B.4]
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
        nutrient_amounts: dict[str, float],
        nutrient_concentrations: dict[str, float],
    ) -> Tuple[float, AnimalManureExcretions]:
        """
        Calculates the manure excretion values for a cow with information from the ration formulation.

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
        nutrient_amounts: Dict[str, float]
            Amounts of nutrients in pen ration, calculated per animal, see Notes section for units.
        nutrient_concentrations: Dict[str, float]
            Concentrations of nutrients in pen ration, calculated per animal, percentages.

        Returns
        -------
        float
            Total amount of phosphorus excreted by the given animal (g).

        AnimalManureExcretions
            A dictionary that contains the manure excretion values as specified
                in the AnimalManureExcretions class definition.

        Notes
        -----
        The dry matter ("dm") unit is kg per animal. Crude protein ("CP"), ADF, NDF, lignin, ash, phosphorus, potassium,
        and nitrogen ("N") are all percentages of dry matter.

        """
        if is_lactating:
            return ManureExcretionCalculator._calculate_lactating_cow_manure(
                days_in_milk,
                milk_protein,
                daily_milk_production,
                fecal_phosphorus,
                urine_phosphorus_required,
                nutrient_amounts,
                nutrient_concentrations,
            )
        else:
            return ManureExcretionCalculator._calculate_dry_cow_manure(
                body_weight,
                daily_milk_production,
                fecal_phosphorus,
                urine_phosphorus_required,
                nutrient_amounts,
                nutrient_concentrations,
            )

    @staticmethod
    def _calculate_lactating_cow_manure(
        days_in_milk: int,
        milk_protein: float,
        daily_milk_production: float,
        fecal_phosphorus: float,
        urine_phosphorus_required: float,
        nutrient_amounts: dict[str, float],
        nutrient_concentrations: dict[str, float],
    ) -> Tuple[float, AnimalManureExcretions]:
        """
        Calculates the manure excretion values for a lactating cow with information from the ration formulation.

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

        Notes
        -----
        The dry matter ("dm") unit is kg per animal. Crude protein ("CP"), ADF, NDF, lignin, ash, phosphorus, potassium,
        and nitrogen ("N") are all percentages of dry matter.

        """
        dry_matter_intake = nutrient_amounts["dm"]
        ash_diet_content = nutrient_amounts["ash"]
        dry_matter_concentration = nutrient_concentrations["dm"]
        acid_detergent_fiber_concentrations = nutrient_concentrations["ADF"]
        crude_protein_concentration = nutrient_concentrations["CP"]
        neutral_detergent_fiber_concentration = nutrient_concentrations["NDF"]
        potassium_concentration = nutrient_concentrations["potassium"]

        # Fecal water, kg [A.3E.A.1]
        fecal_water = (
            1.987 * dry_matter_intake
            + 0.348 * acid_detergent_fiber_concentrations
            - 0.412 * crude_protein_concentration
            - 0.074 * dry_matter_concentration
            - 0.0057 * days_in_milk
        )

        # Total Solids, kg [A.3E.A.2]
        # The amount of fecal solids is assumed to be equivalent to the amount of total solids
        fecal_solids = (
            -0.576
            + 0.370 * dry_matter_intake
            - 0.075 * crude_protein_concentration
            + 0.059 * acid_detergent_fiber_concentrations
        )

        # Total urine, kg [A.3E.A.3]
        urine = -7.742 + 0.388 * dry_matter_intake + 0.726 * crude_protein_concentration + 2.066 * milk_protein

        # Manure excretion
        # Amount of feces and urine excreted daily by the growing heifer, kg [A.3E.A.4]
        total_manure_excreted = fecal_water + fecal_solids + urine

        # Total manure nitrogen, kg [A.3E.B.1]
        manure_nitrogen = (
            20.3
            + 0.654
            * (dry_matter_intake * GeneralConstants.KG_TO_GRAMS)
            * (crude_protein_concentration * GeneralConstants.PROTEIN_TO_NITROGEN)
            / GeneralConstants.FRACTION_TO_PERCENTAGE
        ) * GeneralConstants.GRAMS_TO_KG

        # Fecal nitrogen, kg [A.3B.B.2]
        dry_matter_intake = max(dry_matter_intake, AnimalModuleConstants.MINIMUM_DMI_LACT)
        fecal_nitrogen = (-18.5 + 10.1 * dry_matter_intake) * GeneralConstants.GRAMS_TO_KG

        # Urine nitrogen, kg [A.3E.B.3]
        urine_nitrogen = manure_nitrogen - fecal_nitrogen

        # Organic matter intake, kg [A.2.A.3]
        organic_matter_intake = dry_matter_intake - ash_diet_content

        # Degradable volatile solids, kg [A.3E.A.5]
        degradable_volatile_solids = (
            -1.017
            + 0.364 * organic_matter_intake
            + 0.029 * neutral_detergent_fiber_concentration
            - 0.023 * crude_protein_concentration
        )

        # Total volatile solids, kg [A.3E.A.6]
        total_volatile_solids = (
            -1.201
            + 0.402 * organic_matter_intake
            + 0.036 * neutral_detergent_fiber_concentration
            - 0.024 * crude_protein_concentration
        )

        # Non-degradable volatile solids, kg [A.3A.A.6]
        non_degradable_volatile_solids = total_volatile_solids - degradable_volatile_solids

        # Urinary N concentration, g N/kg [A.3G.B.1]
        urinary_nitrogen_concentration = (urine_nitrogen * GeneralConstants.KG_TO_GRAMS) / urine
        # Nitrogen concentration in urinary urea, g urea-N/L [A.3G.B.2]
        urine_urea_nitrogen_concentration = -1.16 + 0.86 * urinary_nitrogen_concentration

        # Total ammoniacal nitrogen in the manure slurry, kg
        manure_total_ammoniacal_nitrogen = urine_nitrogen

        # Amount of potassium excreted, g [A.3E.B.3]
        potassium = (
            7.21 * dry_matter_intake + 15944 * potassium_concentration / GeneralConstants.FRACTION_TO_PERCENTAGE - 164.5
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
        nutrient_amounts: dict[str, float],
        nutrient_concentrations: dict[str, float],
    ) -> Tuple[float, AnimalManureExcretions]:
        """Calculates the manure excretion values for a non-lactating cow with information from the ration formulation.

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

        Notes
        -----
        The dry matter ("dm") unit is kg per animal. Crude protein ("CP"), ADF, NDF, lignin, ash, phosphorus, potassium,
        and nitrogen ("N") are all percentages of dry matter.

        """
        # TODO: Add TypedDicts for ration_formulation and available feeds - GitHub Issue #1218
        # TODO: Pass in available feeds directly instead of a Feed object - GitHub Issue #1218
        # TODO: Rename abbreviated key names to full names - GitHub Issue #1218
        dry_matter_intake = nutrient_amounts["dm"]
        crude_protein_concentration = nutrient_concentrations["CP"]
        potassium_concentration = nutrient_concentrations["potassium"]
        ash_concentration = nutrient_concentrations["ash"]
        neutral_detergent_fiber_concentration = nutrient_concentrations["NDF"]
        # Soluble residue
        # Dietary percentage of soluble residues, % DM, in the note of [A.3B.C.2]
        # TODO: Further calculations to account for entire diet:- GitHub Issue #1218
        # DMI: dry matter intake, kg
        # DM: dietary dry matter, % of diet
        # CP: dietary crude protein, % of DM

        # Total urine, kg [A.3F.A.1]
        urine = 15.4

        # Manure excretion
        # Amount of feces and urine excreted daily by the dry cow, kg [A.3F.A.2]
        total_manure_excreted = (
            0.00711 * body_weight
            + 0.324 * crude_protein_concentration
            + 0.259 * neutral_detergent_fiber_concentration
            + 8.05
        )

        # Total solids excretion
        # Amount of dry material excreted by the dry cow, kg [A.3F.A.3]
        total_solids = 0.178 * dry_matter_intake + 2.733

        # Organic matter intake, kg [A.2.A.3]
        dry_matter_intake = max(dry_matter_intake, AnimalModuleConstants.MINIMUM_DMI_DRY)
        organic_matter_intake = (
            dry_matter_intake
            * (GeneralConstants.FRACTION_TO_PERCENTAGE - ash_concentration)
            * GeneralConstants.PERCENTAGE_TO_FRACTION
        )

        # Total volatile solids, kg [A.3E.A.6]
        total_volatile_solids = (
            -1.201
            + 0.402 * organic_matter_intake
            + 0.036 * neutral_detergent_fiber_concentration
            - 0.024 * crude_protein_concentration
        )

        # Degradable volatile solids, kg [A.3E.A.5]
        degradable_volatile_solids = (
            -1.017
            + 0.364 * organic_matter_intake
            + 0.029 * neutral_detergent_fiber_concentration
            - 0.023 * crude_protein_concentration
        )

        # Non-degradable volatile solids, kg [A.3A.A.6]
        non_degradable_volatile_solids = total_volatile_solids - degradable_volatile_solids

        # Nitrogen in liquid and solid manure, kg [A.3B.B.1]
        manure_nitrogen = (
            15.1
            + 0.83
            * (dry_matter_intake * GeneralConstants.KG_TO_GRAMS)
            * (crude_protein_concentration * GeneralConstants.PROTEIN_TO_NITROGEN)
            / GeneralConstants.FRACTION_TO_PERCENTAGE
        ) * GeneralConstants.GRAMS_TO_KG

        # Nitrogen excretion in feces, kg [A.3B.B.2]
        fecal_nitrogen = (
            0.345
            + 0.317
            * (dry_matter_intake * GeneralConstants.KG_TO_GRAMS)
            * (crude_protein_concentration * GeneralConstants.PROTEIN_TO_NITROGEN)
            * GeneralConstants.PERCENTAGE_TO_FRACTION
        ) * GeneralConstants.GRAMS_TO_KG

        # Nitrogen excretion in urine, kg [A.3B.B.3]
        urine_nitrogen = manure_nitrogen - fecal_nitrogen

        # Urinary N concentration, g N/kg [A.3G.B.1]
        urinary_nitrogen_concentration = (urine_nitrogen * GeneralConstants.KG_TO_GRAMS) / urine
        # Nitrogen concentration in urinary urea, g urea-N/L [A.3G.B.2]
        urine_urea_nitrogen_concentration = -1.16 + 0.86 * urinary_nitrogen_concentration

        # Total ammoniacal nitrogen in the manure slurry, kg
        manure_total_ammoniacal_nitrogen = urine_nitrogen

        # Amount of potassium excreted, g [A.3B.B.4]
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

        """
        # P fraction of manure (A.3.A.1)
        if total_manure_excreted > 0:
            manure_phosphorus_fraction = (fecal_phosphorus + urine_phosphorus_required) / (
                total_manure_excreted * GeneralConstants.KG_TO_GRAMS
            )
        else:
            manure_phosphorus_fraction = 0.0

        # Water extractable Inorganic P (WIP) fraction - fraction of manure
        # compromised of inorganic water extractable P [A.3.A.2]
        inorganic_phosphorus_fraction = 0.50 * manure_phosphorus_fraction

        # Water extractable Organic P (WOP) fraction - fraction of maure
        # comprised of organic water extractable P [A.3.A.3]
        organic_phosphorus_fraction = 0.05 * manure_phosphorus_fraction

        # amount of P in milk per animal (g) [A.3E.B.1]
        phosphorus_in_milk = 0.0009 * daily_milk_production * GeneralConstants.KG_TO_GRAMS

        # manure P excretion for manure module input (g) [A.3.B.2]
        manure_phosphorus_excreted = fecal_phosphorus + urine_phosphorus_required

        # amount of P excreted by an animal (g) [A.3.B.3]
        total_phosphorus_excreted = phosphorus_in_milk + fecal_phosphorus + urine_phosphorus_required

        return (
            total_phosphorus_excreted,
            inorganic_phosphorus_fraction,
            organic_phosphorus_fraction,
            manure_phosphorus_excreted,
            manure_phosphorus_fraction,
        )
