from typing import Tuple

from RUFAS.data_structures.animal_manure_excretions import AnimalManureExcretions
from RUFAS.general_constants import GeneralConstants


class ManureExcretionCalculator:
    @staticmethod
    def calf_manure(
        body_weight: float,
        fecal_phosphorus: float,
        urine_phosphorus_required: float,
        nutrient_amount: dict[str, float],
        nutrient_conc: dict[str, float],
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
        nutrient_amount : Dict[str, float]
            Amounts of nutrients in pen ration, calculated per animal, see Notes section for units.
        nutrient_conc : Dict[str, float]
            Concentration of nutrients in pen ration, calculated per animal, percentages.

        Returns
        -------
        float
            Total amount of phosphorus excreted by the given animal, g.
        AnimalManureExcretions
            A dictionary that contains the manure excretion values as specified
                in the AnimalManureExcretions class definition.
        """

        nutrient_amounts = nutrient_amount
        nutrient_concentrations = nutrient_conc
        dry_matter_intake = nutrient_amounts["dm"]
        CP_concentration = nutrient_concentrations["CP"]

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
        manure_nitrogen = (112.55 * dry_matter_intake * (CP_concentration / 100)) * GeneralConstants.GRAMS_TO_KG

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
    def heifer_manure(
        body_weight: float,
        fecal_phosphorus: float,
        urine_phosphorus_required: float,
        nutrient_amount: dict[str, float],
        nutrient_conc: dict[str, float],
    ) -> Tuple[float, AnimalManureExcretions]:
        """Calculates the manure excretion values for a growing heifer with information from the ration formulation.

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
        nutrient_amount_units = {
            "dm": "kg/animal",
            "CP": "percent of DM",
            "ADF": "percent of DM",
            "NDF": "percent of DM",
            "lignin": "percent of DM",
            "ash": "percent of DM",
            "phosphorus": "percent of DM",
            "potassium": "percent of DM",
            "N": "percent of DM",
        }

        """
        # TODO: Same TODOs as in dry_cow_manure_excretion.py - GitHub Issue #1219
        nutrient_amounts = nutrient_amount
        nutrient_concentrations = nutrient_conc
        dry_matter_intake = nutrient_amounts["dm"]
        CP_concentration = nutrient_concentrations["CP"]
        potassium_concentration = nutrient_concentrations["potassium"]
        ASH_concentration = nutrient_concentrations["ash"]
        NDF_concentration = nutrient_concentrations["NDF"]
        EE_concentration = nutrient_concentrations["EE"]
        # Soluble residue
        # Dietary percentage of soluble residues, % DM, in the note of [A.3B.C.2]
        soluble_residue = (
            (GeneralConstants.FRACTION_TO_PERCENTAGE - ASH_concentration)
            - NDF_concentration
            - CP_concentration
            - EE_concentration
        )

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
            * (CP_concentration * GeneralConstants.PROTEIN_TO_NITROGEN)
            / GeneralConstants.FRACTION_TO_PERCENTAGE
        ) * GeneralConstants.GRAMS_TO_KG

        # Nitrogen excretion in feces, kg [A.3B.B.2]
        fecal_nitrogen = (
            0.345
            + 0.317
            * (dry_matter_intake * GeneralConstants.KG_TO_GRAMS)
            * (CP_concentration * GeneralConstants.PROTEIN_TO_NITROGEN)
            / GeneralConstants.FRACTION_TO_PERCENTAGE
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
            * (potassium_concentration / GeneralConstants.FRACTION_TO_PERCENTAGE)
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
