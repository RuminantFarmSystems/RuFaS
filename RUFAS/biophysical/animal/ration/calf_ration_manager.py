from enum import Enum

from numpy import exp, log

from RUFAS.data_structures.feed_storage_to_animal_connection import RUFAS_ID, NutrientStandard, NASEMFeed, NRCFeed
from RUFAS.general_constants import GeneralConstants


"""RuFaS IDs for supported calf feeds."""
WHOLE_MILK_ID: RUFAS_ID = 202
MILK_REPLACER_ID: RUFAS_ID = 203
STARTER_ID: RUFAS_ID = 216


class CalfMilkType(Enum):
    """Calf milk types."""

    WHOLE = "whole"
    REPLACER = "replacer"


class CalfRationManager:
    """
    Calf ration formulation is distinct from other animal types, and managed separately. Calf nutrition requirements are
    calculated based on the calf's nutritional intake.
    """

    milk_type: CalfMilkType

    @classmethod
    def set_milk_type(cls, milk_type: CalfMilkType) -> None:
        """
        Set the milk type for the calf.

        Parameters
        ----------
        milk_type : CalfMilkType
            The type of milk being fed to the calf.

        """
        cls.milk_type = milk_type

    @classmethod
    def calc_requirements(
        cls,
        days_born: int,
        body_weight: float,
        temp: float,
        animal_intake: dict[str, int | float],
    ) -> dict[str, float]:
        """
        Calculate dietary intake and nutrient requirements for the calf.

        Parameters
        ----------
        days_born : int
            Number of days since the calf was born.
        body_weight : float
            Body weight of the calf (kg).
        temp : float
            Average temperature of the simulation day (C).
        animal_intake : dict
            Whole milk, replacer, and starter intake amounts and nutritional content.

        Returns
        -------
        dict[str, float]
            Dictionary of requirement values and methods.

        References
        ----------
        RuFaS' NRC Requirements Scientific Documentation [A.1B.F] through [A.1B.H]

        """

        whole_milk_intake = animal_intake["whole_milk_intake"]
        milk_replacer_intake = animal_intake["milk_replacer_intake"]
        starter_intake = animal_intake["starter_intake"]
        me_intake = animal_intake["me_intake"]
        milk_crude_protein_intake = animal_intake["milk_cp_intake"]
        starter_crude_protein_intake = animal_intake["starter_cp_intake"]
        cp_intake = animal_intake["cp_intake"]
        apparent_digestible_protein_intake = animal_intake["adp_intake"]
        milk_me_proportion = animal_intake["milk_me_proportion"]
        starter_me_proportion = animal_intake["starter_me_proportion"]
        milk_proportion = animal_intake["milk_proportion"]
        starter_proportion = animal_intake["starter_proportion"]

        t_factor = 0
        if days_born <= 60:
            if temp < -30:
                t_factor = 1.34
            elif temp < 15:
                t_factor = -0.0272 * temp + 0.4751
        else:
            if temp < -30:
                t_factor = 1.07
            elif temp <= 5:
                t_factor = -0.0271 * temp + 0.2002

        maintenance_net_energy = 0.086 * body_weight**0.75 * (1 + t_factor)
        maintenance_metabolizable_energy = maintenance_net_energy / (0.86 * milk_proportion + 0.75 * starter_proportion)

        biological_value = 0.8 * milk_crude_protein_intake / cp_intake + 0.7 * starter_crude_protein_intake / cp_intake

        endogenous_urine_n_loss = 0.0002 * body_weight**0.75 * GeneralConstants.KG_TO_GRAMS
        metabolic_fecal_n = (
            0.0019 * (whole_milk_intake + milk_replacer_intake) + 0.0033 * starter_intake
        ) * GeneralConstants.KG_TO_GRAMS

        maintentenance_apparent_digestible_protein = 6.25 * (
            1 / biological_value * (endogenous_urine_n_loss + metabolic_fecal_n) - metabolic_fecal_n
        )

        growth_metabolizable_energy = me_intake - maintenance_metabolizable_energy
        growth_net_energy = growth_metabolizable_energy * (0.69 * milk_me_proportion + 0.57 * starter_me_proportion)

        energy_allowable_gain = 0
        if growth_net_energy >= 0:
            energy_allowable_gain = exp(0.833 * log((1.19 * growth_net_energy) / (0.69 * body_weight**0.355)))

        apparent_digestible_protein_allowable_gain = (
            (apparent_digestible_protein_intake - maintentenance_apparent_digestible_protein)
            * biological_value
            / 0.188
            * GeneralConstants.GRAMS_TO_KG
        )
        live_weight_change = min(energy_allowable_gain, apparent_digestible_protein_allowable_gain)

        nutrient_requirements = {
            "ne_maint": maintenance_net_energy,
            "me_maint": maintenance_metabolizable_energy,
            "biological_value": biological_value,
            "endo_urine_N": endogenous_urine_n_loss,
            "meta_fecal_N": metabolic_fecal_n,
            "adp_maint": maintentenance_apparent_digestible_protein,
            "me_gain": growth_metabolizable_energy,
            "ne_gain": growth_net_energy,
            "energy_allow_gain": energy_allowable_gain,
            "adp_allow_gain": apparent_digestible_protein_allowable_gain,
            "live_weight_change": live_weight_change,
        }

        return nutrient_requirements

    @classmethod
    def calc_intake(
        cls,
        birth_weight: float,
        body_weight: float,
        wean_day: int,
        wean_length: int,
        available_feeds: list[NASEMFeed | NRCFeed],
        nutrient_standard: NutrientStandard,
    ) -> dict[str, float]:
        """
        Calculates the amounts of whole milk, milk replacer, and starter that a calf consumes.

        Parameters
        ----------
        birth_weight : float
            Birth weight of the calf (kg).
        body_weight : float
            Body weight of the calf (kg).
        wean_day : int
            Number of days after birth that calf is fully weaned from milk (or replacer).
        wean_length : int
            Wean length of the calf (days).
        available_feeds : list[NASEMFeed | NRCFeed]
            List of feeds available to the calf.
        nutrient_standard : NutrientStandard
            Enum member indicating whether the NASEM or NRC nutrition standard is being used.

        Returns
        -------
        dict[str, float]
            Amounts of feed taken in by calf and nutritive content of the intake.

        References
        ----------
        RuFaS' NRC Requirements Scientific Documentation [A.1B.A] through [A.1B.E]

        """

        whole_milk = next((feed for feed in available_feeds if feed.rufas_id == WHOLE_MILK_ID), None)
        milk_replacer = next((feed for feed in available_feeds if feed.rufas_id == MILK_REPLACER_ID), None)
        starter = next(feed for feed in available_feeds if feed.rufas_id == STARTER_ID)

        wean_start = wean_day - wean_length - 1
        milk_reduct = round(0.5 * wean_length)
        wean_fraction = 1 - milk_reduct / (wean_length + 1)

        if is_standard_nasem := (nutrient_standard == NutrientStandard.NASEM):
            starter_digestible_energy = starter.DE_Base
        else:
            starter_digestible_energy = starter.DE

        if cls.milk_type == CalfMilkType.WHOLE:
            whole_milk_digestible_energy = whole_milk.DE_Base if is_standard_nasem is True else whole_milk.DE
            whole_milk_intake = 0.1 * birth_weight * whole_milk.DM * GeneralConstants.PERCENTAGE_TO_FRACTION
            whole_milk_metabolizable_energy = 0.96 * whole_milk_digestible_energy
            whole_milk_crude_protein = whole_milk.CP
            milk_replacer_intake, milk_replacer_metabolizable_energy, milk_replacer_crude_protein = 0.0, 0.0, 0.0
            milk_intake_wean = whole_milk_intake * wean_fraction
        else:
            whole_milk_intake, whole_milk_metabolizable_energy, whole_milk_crude_protein = 0.0, 0.0, 0.0
            milk_replacer_digestible_energy = milk_replacer.DE_Base if is_standard_nasem is True else milk_replacer.DE
            milk_replacer_intake = 0.1 * birth_weight * milk_replacer.DM * GeneralConstants.PERCENTAGE_TO_FRACTION
            milk_replacer_metabolizable_energy = 0.96 * milk_replacer_digestible_energy
            milk_replacer_crude_protein = milk_replacer.CP
            milk_intake_wean = milk_replacer_intake * wean_fraction

        if body_weight <= 50.0:
            starter_intake = 0.01
        elif 50.0 < body_weight <= 69.365:
            starter_intake = -0.24783 + 0.0049567 * body_weight
        else:
            starter_intake = -6.2263 + 0.091145 * body_weight

        dry_matter_intake = whole_milk_intake + milk_replacer_intake + starter_intake

        starter_metabolizable_energy = (1.01 * starter_digestible_energy - 0.45) + 0.0046 * (
            starter_digestible_energy - 3
        )

        milk_me_intake = (
            whole_milk_metabolizable_energy * whole_milk_intake
            + milk_replacer_metabolizable_energy * milk_replacer_intake
        )
        starter_me_intake = starter_metabolizable_energy * starter_intake
        me_intake = milk_me_intake + starter_me_intake

        milk_me_proportion = milk_me_intake / me_intake
        starter_me_proportion = starter_me_intake / me_intake

        milk_cp_intake = GeneralConstants.PERCENTAGE_TO_FRACTION * (
            whole_milk_crude_protein * whole_milk_intake + milk_replacer_crude_protein * milk_replacer_intake
        )
        starter_cp_intake = GeneralConstants.PERCENTAGE_TO_FRACTION * starter.CP * starter_intake
        total_cp_intake = milk_cp_intake + starter_cp_intake

        adp_intake = (
            0.93 * milk_cp_intake / total_cp_intake + 0.75 * starter_cp_intake / total_cp_intake
        ) * GeneralConstants.KG_TO_GRAMS

        milk_proportion = (whole_milk_intake + milk_replacer_intake) / dry_matter_intake
        starter_proportion = starter_intake / dry_matter_intake

        animal_intake = {
            "whole_milk_intake": whole_milk_intake,
            "milk_replacer_intake": milk_replacer_intake,
            "starter_intake": starter_intake,
            "wean_start": wean_start,
            "milk_reduction": milk_reduct,
            "milk_intake_wean": milk_intake_wean,
            "dry_matter_intake": dry_matter_intake,
            "me_intake": me_intake,
            "milk_cp_intake": milk_cp_intake,
            "starter_cp_intake": starter_cp_intake,
            "cp_intake": total_cp_intake,
            "adp_intake": adp_intake,
            "milk_me_proportion": milk_me_proportion,
            "starter_me_proportion": starter_me_proportion,
            "milk_proportion": milk_proportion,
            "starter_proportion": starter_proportion,
        }

        return animal_intake
