from dataclasses import dataclass

from RUFAS.data_structures.feed_storage_to_animal_connection import (
    RUFAS_ID,
    Feed,
    FeedCategorization,
    FeedComponentType,
    NutrientStandard,
)
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionSupply
from RUFAS.general_constants import GeneralConstants


@dataclass
class FeedInRation:
    """
    Defines the amount of feed in a ration (kg) and all the nutritive info associated with it, in a Feed instance.
    """

    amount: float
    info: Feed


class NutritionSupplyCalculator:
    """Calculates the energy and nutrients supplied by a ration."""

    nutrient_standard: NutrientStandard
    nutrients_to_calculate = ["NDF", "EE", "CP", "ADF", "TDN", "lignin", "ash", "potassium", "starch"]

    @classmethod
    def calculate_nutrient_supply(
        cls, feeds_used: list[Feed], ration_formulation: dict[RUFAS_ID, float], body_weight: float
    ) -> NutritionSupply:
        """
        Calculates the energy and nutrients supplied in a ration.

        Parameters
        ----------
        feeds_used : list[Feed]
            List of feeds that were used to construct the ration formulation.
        ration_formulation : dict[RUFAS_ID, float]
            Maps the RuFaS ID of a feed to the amount fed in a ration (kg dry matter).

        Returns
        -------
        NutritionSupply
            NutritionSupply instance containing the energy and nutritive content of the given ration.

        """
        feeds = [
            FeedInRation(amount=amount, info=next((feed for feed in feeds_used if feed.rufas_id == rufas_id), None))
            for rufas_id, amount in ration_formulation.items()
        ]

        intake_nutrient_discount = cls._calculate_nutrient_intake_discount(feeds, body_weight)
        actual_tdn_percentages = {feed.info.rufas_id: feed.info.TDN * intake_nutrient_discount for feed in feeds}
        actual_digestible_energy = {feed.info.rufas_id: feed.info.DE * intake_nutrient_discount for feed in feeds}

        metabolizable_energy = cls._calculate_actual_metabolizable_energy(feeds, actual_digestible_energy)
        total_metabolizable_energy = sum([feed.amount * metabolizable_energy[feed.info.rufas_id] for feed in feeds])

        maintenance_energy = cls._calculate_actual_maintenance_net_energy(feeds, metabolizable_energy)
        lactation_energy = cls._calculate_actual_lactation_net_energy(
            feeds, metabolizable_energy, actual_digestible_energy
        )
        growth_energy = cls._calculate_actual_growth_net_energy(feeds, metabolizable_energy)
        calcium = cls._calculate_calcium_supply(feeds)
        phosphorus = cls._calculate_phosphorus_supply(feeds)
        dry_matter_intake = sum([feed.amount for feed in feeds])
        wet_matter = sum([feed.amount / (feed.info.DM * GeneralConstants.PERCENTAGE_TO_FRACTION) for feed in feeds])
        protein = cls._calculate_metabolizable_protein_supply(
            feeds, dry_matter_intake, actual_tdn_percentages, body_weight
        )
        nutrient_contents = {
            nutrient: cls._calculate_nutritive_content(feeds, nutrient) for nutrient in cls.nutrients_to_calculate
        }
        digestible_energy = cls._calculate_digestible_energy(feeds)
        total_byproducts = cls._calculate_byproducts_supply(feeds)
        forage_ndf_content = cls._calculate_forage_neutral_detergent_fiber_content(feeds)

        return NutritionSupply(
            metabolizable_energy=total_metabolizable_energy,
            maintenance_energy=maintenance_energy,
            lactation_energy=lactation_energy,
            growth_energy=growth_energy,
            metabolizable_protein=protein,
            calcium=calcium,
            phosphorus=phosphorus,
            dry_matter=dry_matter_intake,
            wet_matter=wet_matter,
            ndf_supply=nutrient_contents["NDF"],
            fat_supply=nutrient_contents["EE"],
            crude_protein=nutrient_contents["CP"],
            adf_supply=nutrient_contents["ADF"],
            digestible_energy_supply=digestible_energy,
            tdn_supply=nutrient_contents["TDN"],
            lignin_supply=nutrient_contents["lignin"],
            ash_supply=nutrient_contents["ash"],
            potassium_supply=nutrient_contents["potassium"],
            starch_supply=nutrient_contents["starch"],
            byproduct_supply=total_byproducts,
            forage_ndf_supply=forage_ndf_content,
        )

    @classmethod
    def _calculate_nutrient_intake_discount(cls, feeds: list[FeedInRation], body_weight: float) -> float:
        """
        Calculates discount applied to Total Digestible Nutrients (TDN) and Digestible Energy (DE).

        Parameters
        ----------
        feeds : list[FeedInRation]
            List of feeds in ration, including the amount and nutritive properties.
        body_weight : float
            Body weight of an animal (kg).

        Returns
        -------
        float
            Discount used to calculate the actual TDN and DE content of feeds in the ration.

        References
        ----------
        Animal Scientific Documentation [A.Cow.E.1-3]-[A.Heifer.E.1-3]

        """
        dry_matter_intake = sum([feed.amount for feed in feeds])

        total_tdn = sum([feed.amount * feed.info.TDN * GeneralConstants.PERCENTAGE_TO_FRACTION for feed in feeds])
        tdn_percentage = (
            total_tdn / dry_matter_intake * GeneralConstants.FRACTION_TO_PERCENTAGE if dry_matter_intake > 0.0 else 0.0
        )

        if tdn_percentage < 60.0:
            return 1.0

        if total_tdn < (0.035 * body_weight**0.75):
            return 1.0

        somatic_body_weight = body_weight * 0.96
        maintenance_dry_matter_intake = total_tdn / (0.035 * somatic_body_weight**0.75)

        discount: float = (
            tdn_percentage - ((0.18 * tdn_percentage - 10.3) * (maintenance_dry_matter_intake - 1))
        ) / tdn_percentage

        return max(discount, 0.6)

    @classmethod
    def _calculate_actual_metabolizable_energy(
        cls, feeds: list[FeedInRation], actual_digestible_energy: dict[RUFAS_ID, float]
    ) -> dict[RUFAS_ID, float]:
        """
        Calculates the actual metabolizable energy of feeds.

        Parameters
        ----------
        feeds : list[FeedInRation]
            List of feeds in ration, including the amount and nutritive properties.
        actual_digestible_energy : dict[RUFAS_ID, float]
            Mapping of RuFaS Feed IDs to the discounted digestible energy content (Mcal / kg) of the corresponding feed.

        Returns
        -------
        dict[RUFAS_ID, float]
            Mapping of RuFaS Feed IDs to the actual metabolizable energy content of the corresponding feed (Mcal / kg).

        References
        ----------
        Animal Scientific Documentation [A.Cow.E.6]-[A.Heifer.E.6]

        """
        actual_metabolizable_energy: dict[RUFAS_ID, float] = {}

        for feed in feeds:
            if feed.info.feed_type is FeedComponentType.MINERAL:
                energy = 0.0
            elif feed.info.is_fat is True:
                energy = feed.info.DE
            elif feed.info.EE >= 3.0:
                energy = 1.01 * actual_digestible_energy[feed.info.rufas_id] - 0.45 + 0.0046 * (feed.info.EE - 3.0)
            else:
                energy = 1.01 * actual_digestible_energy[feed.info.rufas_id] - 0.45
            actual_metabolizable_energy[feed.info.rufas_id] = energy

        return actual_metabolizable_energy

    @classmethod
    def _calculate_actual_maintenance_net_energy(
        cls, feeds: list[FeedInRation], actual_metabolizable_energy: dict[RUFAS_ID, float]
    ) -> float:
        """
        Calculates the actual net energy of the ration available to use for maintenance.

        Parameters
        ----------
        feeds : list[FeedInRation]
            List of feeds in ration, including the amount and nutritive properties.
        actual_metabolizable_energy : dict[RUFAS_ID, float]
            Mapping of RuFaS Feed IDs to the actual metabolizable energy content (Mcal / kg) of the feed.

        Returns
        -------
        float
            Total actual net energy available for maintenance in the ration (Mcal).

        References
        ----------
        Animal Scientific Documentation [A.Cow.E.8]-[A.Heifer.E.8]

        """
        actual_maintenance_net_energy: dict[RUFAS_ID, float] = {}

        for feed in feeds:
            actual_metabolizable = actual_metabolizable_energy[feed.info.rufas_id]
            if feed.info.feed_type is FeedComponentType.MINERAL:
                energy = 0.0
            elif feed.info.is_fat is True:
                energy = 0.8 * actual_metabolizable
            else:
                energy = (
                    1.37 * actual_metabolizable
                    - 0.138 * actual_metabolizable**2
                    + 0.0105 * actual_metabolizable**3
                    - 1.12
                )
            actual_maintenance_net_energy[feed.info.rufas_id] = energy
        total = sum([feed.amount * actual_maintenance_net_energy[feed.info.rufas_id] for feed in feeds])

        return total

    @classmethod
    def _calculate_actual_lactation_net_energy(
        cls,
        feeds: list[FeedInRation],
        actual_metabolizable_energy: dict[RUFAS_ID, float],
        actual_digestible_energy: dict[RUFAS_ID, float],
    ) -> float:
        """
        Calculates the actual net energy of the ration available to use for lactation.

        Parameters
        ----------
        feeds : list[FeedInRation]
            List of feeds in ration, including the amount and nutritive properties.
        actual_digestible_energy : dict[RUFAS_ID, float]
            Mapping of RuFaS Feed IDs to the discounted digestible energy content (Mcal / kg) of the feed.
        actual_metabolizable : dict[RUFAS_ID, float]
            Mapping of RuFaS Feed IDs to the actual metabolizable energy content (Mcal / kg) of the feed.

        Returns
        -------
        float
            Total actual net energy available for lactation in the ration (Mcal).

        References
        ----------
        Animal Scientific Documentation [A.Cow.E.7]-[A.Heifer.E.7]

        """
        actual_lactation_net_energy: dict[RUFAS_ID, float] = {}

        for feed in feeds:
            if feed.info.feed_type is FeedComponentType.MINERAL:
                energy = 0.0
            elif feed.info.is_fat is True:
                energy = 0.8 * actual_digestible_energy[feed.info.rufas_id]
            elif feed.info.EE >= 3.0:
                energy = (
                    (0.703 * actual_metabolizable_energy[feed.info.rufas_id])
                    - 0.19
                    + ((((0.097 * actual_metabolizable_energy[feed.info.rufas_id]) + 0.19) / 97) * (feed.info.EE - 3.0))
                )
            else:
                energy = 0.703 * actual_metabolizable_energy[feed.info.rufas_id] - 0.19
            actual_lactation_net_energy[feed.info.rufas_id] = energy
        total = sum([feed.amount * actual_lactation_net_energy[feed.info.rufas_id] for feed in feeds])

        return total

    @classmethod
    def _calculate_actual_growth_net_energy(
        cls, feeds: list[FeedInRation], actual_metabolizable_energy: dict[RUFAS_ID, float]
    ) -> float:
        """
        Calculates the actual net energy of the ration available to use for growth.

        Parameters
        ----------
        feeds : list[FeedInRation]
            List of feeds in ration, including the amount and nutritive properties.
        actual_metabolizable : dict[RUFAS_ID, float]
            Mapping of RuFaS Feed IDs to the actual metabolizable energy content (Mcal / kg) of the feed.

        Returns
        -------
        float
            Total actual net energy available for growth in the ration (Mcal).

        References
        ----------
        Animal Scientific Documentation [A.Cow.E.9]-[A.Heifer.E.9]

        """
        actual_growth_net_energy: dict[RUFAS_ID, float] = {}

        for feed in feeds:
            if feed.info.feed_type is FeedComponentType.MINERAL:
                energy = 0.0
            elif feed.info.is_fat is True:
                energy = 0.55 * actual_metabolizable_energy[feed.info.rufas_id]
            else:
                energy = (
                    1.42 * actual_metabolizable_energy[feed.info.rufas_id]
                    - 0.174 * actual_metabolizable_energy[feed.info.rufas_id] ** 2
                    + 0.0122 * actual_metabolizable_energy[feed.info.rufas_id] ** 3
                    - 1.65
                )
            actual_growth_net_energy[feed.info.rufas_id] = energy
        total = sum([feed.amount * actual_growth_net_energy[feed.info.rufas_id] for feed in feeds])

        return total

    @classmethod
    def _calculate_calcium_supply(cls, feeds: list[FeedInRation]) -> float:
        """
        Calculates the calcium supply in the ration.

        Parameters
        ----------
        feeds : list[FeedInRation]
            List of feeds in ration, including the amount and nutritive properties.

        Returns
        -------
        float
            Total digestible calcium supply in the ration (g).

        References
        ----------
        Animal Scientific Documentation [A.Cow.E.16]-[A.Heifer.E.16]

        """
        calcium_digestibility: dict[RUFAS_ID, float] = {}

        for feed in feeds:
            if feed.info.feed_type is FeedComponentType.FORAGE:
                digestibility = 0.3
            elif feed.info.feed_type is FeedComponentType.CONC:
                digestibility = 0.6
            elif feed.info.feed_type is FeedComponentType.MINERAL:
                digestibility = 0.95
            else:
                digestibility = 0.0
            calcium_digestibility[feed.info.rufas_id] = digestibility

        total = sum(
            [
                feed.amount
                * calcium_digestibility[feed.info.rufas_id]
                * feed.info.calcium
                * GeneralConstants.PERCENTAGE_TO_FRACTION
                for feed in feeds
            ]
        )

        return total * GeneralConstants.KG_TO_GRAMS

    @classmethod
    def _calculate_phosphorus_supply(cls, feeds: list[FeedInRation]) -> float:
        """
        Calculates the phosphorus supply in the ration.

        Parameters
        ----------
        feeds : list[FeedInRation]
            List of feeds in ration, including the amount and nutritive properties.

        Returns
        -------
        float
            Total digestible phosphorus supply in the ration (g).

        References
        ----------
        Animal Scientific Documentation [A.Cow.E.17]-[A.Heifer.E.17]

        """
        phosphorus_digestibility: dict[RUFAS_ID, float] = {}

        for feed in feeds:
            if feed.info.feed_type is FeedComponentType.FORAGE:
                digestibility = 0.64
            elif feed.info.feed_type is FeedComponentType.CONC:
                digestibility = 0.7
            elif feed.info.feed_type is FeedComponentType.MINERAL:
                digestibility = 0.8
            else:
                digestibility = 0.0
            phosphorus_digestibility[feed.info.rufas_id] = digestibility

        total = sum(
            [
                feed.amount
                * phosphorus_digestibility[feed.info.rufas_id]
                * feed.info.phosphorus
                * GeneralConstants.PERCENTAGE_TO_FRACTION
                for feed in feeds
            ]
        )

        return total * GeneralConstants.KG_TO_GRAMS

    @classmethod
    def _calculate_metabolizable_protein_supply(
        cls,
        feeds: list[FeedInRation],
        dry_matter_intake: float,
        actual_tdn_percentages: dict[RUFAS_ID, float],
        body_weight: float,
    ) -> float:
        """
        Calculates amount of metabolizable protein in ration.

        Parameters
        ----------
        feeds : list[FeedInRation]
            List of feeds in ration, including the amount and nutritive properties.
        dry_matter_intake : float
            Total dry matter contained in the ration (kg).
        actual_tdn_percentages : dict[RUFAS_ID, float]
            Mapping of RuFaS Feed IDs to the discounted Total Digestable Nutrition (TDN) percentage of the feed.
        body_weight : float
            The body weight of an animal (kg).

        Returns
        -------
        float
            Total metabolizable protein in the ration (g).

        References
        ----------
        Animal Scientific Documentation [A.Cow.E.13]-[A.Cow.E.13], [A.Cow.E.14]-[A.Heifer.E.14], [A.Cow.E.15]
        .. [1] National Research Council. 2001. Nutrient Requirements of Dairy Cattle: Seventh Revised Edition, 2001.
               Washington, DC: The National Academies Press. https://doi.org/10.17226/9825.

        Notes
        -----
        Endogenous metabolizable protein is calculated from the dry matter intake, but the units of the protein are
        grams while the dry matter intake is in kilograms, see page 319 of [1].

        """
        concentrate_percentage_of_ration = cls._calculate_percentage_of_concentrates(feeds, dry_matter_intake)
        protein_passage_rates = cls._calculate_protein_passage_rates(
            feeds, dry_matter_intake, body_weight, concentrate_percentage_of_ration
        )
        rdp_percentages = cls._calculate_rumen_degradable_protein_percentages(feeds, protein_passage_rates)
        rup_percentages = cls._calculate_rumen_undegradable_protein_percentages(feeds, rdp_percentages)

        ration_tdn_content = sum(
            [
                feed.amount * actual_tdn_percentages[feed.info.rufas_id] * GeneralConstants.PERCENTAGE_TO_FRACTION
                for feed in feeds
            ]
        )
        ration_rdp_content = sum(
            [
                feed.amount * rdp_percentages[feed.info.rufas_id] * GeneralConstants.PERCENTAGE_TO_FRACTION
                for feed in feeds
            ]
        )

        microbial_protein_tdn = ration_tdn_content * 0.13 * GeneralConstants.KG_TO_GRAMS
        microbial_protein_rdp = ration_rdp_content * 0.85 * GeneralConstants.KG_TO_GRAMS
        metabolizable_microbial_protein_production = float(0.64 * min(microbial_protein_tdn, microbial_protein_rdp))

        ration_rup_content = sum(
            [
                feed.amount
                * rup_percentages[feed.info.rufas_id]
                * GeneralConstants.PERCENTAGE_TO_FRACTION
                * feed.info.dRUP
                * GeneralConstants.PERCENTAGE_TO_FRACTION
                for feed in feeds
            ]
        )
        ration_rup_content *= GeneralConstants.KG_TO_GRAMS

        endogenous_metabolizable_protein = 0.4 * 11.8 * dry_matter_intake

        return metabolizable_microbial_protein_production + ration_rup_content + endogenous_metabolizable_protein

    @classmethod
    def _calculate_percentage_of_concentrates(cls, feeds: list[FeedInRation], dry_matter_intake: float) -> float:
        """
        Calculates percentage of dry matter in ration that is concentrate.

        Parameters
        ----------
        feeds : list[FeedInRation]
            List of feeds in ration, including the amount and nutritive properties.
        dry_matter_intake : float
            Total dry matter contained in the ration (kg).

        Returns
        -------
        float
            Percentage of the ration's dry matter which is made up of concentrates (percent).

        """
        dry_matter_from_concentrate = sum(
            [feed.amount for feed in feeds if feed.info.feed_type is FeedComponentType.CONC]
        )

        return dry_matter_from_concentrate / dry_matter_intake * GeneralConstants.FRACTION_TO_PERCENTAGE

    @classmethod
    def _calculate_protein_passage_rates(
        cls,
        feeds: list[FeedInRation],
        dry_matter_intake: float,
        body_weight: float,
        percentage_concentrates: float,
    ) -> dict[RUFAS_ID, float]:
        """
        Calculates the protein passage rate of feeds in ration.

        Parameters
        ----------
        feeds : list[FeedInRation]
            List of feeds in ration, including the amount and nutritive properties.
        dry_matter_intake : float
            Total dry matter contained in the ration (kg).
        body_weight : float
            The body weight of an animal (kg).
        percentage_concetrates : dict[RUFAS_ID, float]
            Percentage of the ration's dry matter which is made up of concentrates.

        Returns
        -------
        dict[RUFAS_ID, float]
            Mapping of RuFaS Feed IDs to protein passage rates (percentage / hour).

        References
        ----------
        Animal Scientific Documentation [A.Cow.E.10]-[A.Heifer.E.10]

        """
        protein_passage_rates: dict[RUFAS_ID, float] = {}

        percentage_feed_of_body_weight = (dry_matter_intake / body_weight) * GeneralConstants.FRACTION_TO_PERCENTAGE
        for feed in feeds:
            if feed.info.feed_type is FeedComponentType.CONC:
                rate = 2.904 + 1.375 * percentage_feed_of_body_weight - 0.02 * percentage_concentrates
            elif feed.info.feed_type is FeedComponentType.FORAGE and feed.info.is_wetforage is False:
                rate = (
                    3.362
                    + 0.479 * percentage_feed_of_body_weight
                    - 0.017 * feed.info.NDF
                    - 0.007 * percentage_concentrates
                )
            elif feed.info.is_wetforage is True:
                rate = 3.054 + 0.614 * percentage_feed_of_body_weight
            else:
                rate = 0.0
            protein_passage_rates[feed.info.rufas_id] = rate

        return protein_passage_rates

    @classmethod
    def _calculate_rumen_degradable_protein_percentages(
        cls, feeds: list[FeedInRation], protein_passage_rates: dict[RUFAS_ID, float]
    ) -> dict[RUFAS_ID, float]:
        """
        Calculates rumen degradable protein (RDP) percentages of feeds in ration.

        Parameters
        ----------
        feeds : list[FeedInRation]
            List of feeds in ration, including the amount and nutritive properties.
        protein_passage_rates : dict[RUFAS_ID, float]
            Mapping of RuFaS Feed IDs to protein passage rates (percentage / hour).

        Returns
        -------
        dict[RUFAS_ID, float]
            Mapping of RuFaS Feed IDs to RDP percentages (percent).

        References
        ----------
        Animal Scientific Documentation [A.Cow.E.11]-[A.Heifer.E.11]

        """
        rdp_percentages: dict[RUFAS_ID, float] = {}

        for feed in feeds:
            passage_rate = protein_passage_rates[feed.info.rufas_id]
            feed_degradation_rate_of_b_fraction = feed.info.Kd
            if passage_rate > -feed_degradation_rate_of_b_fraction:
                rdp = (feed_degradation_rate_of_b_fraction / (feed_degradation_rate_of_b_fraction + passage_rate)) * (
                    feed.info.N_B * GeneralConstants.PERCENTAGE_TO_FRACTION
                ) * feed.info.CP + (feed.info.N_A * GeneralConstants.PERCENTAGE_TO_FRACTION) * feed.info.CP
            else:
                rdp = 0.0
            rdp_percentages[feed.info.rufas_id] = rdp

        return rdp_percentages

    @classmethod
    def _calculate_rumen_undegradable_protein_percentages(
        cls, feeds: list[FeedInRation], rumen_degradable_protein_percentages: dict[RUFAS_ID, float]
    ) -> dict[RUFAS_ID, float]:
        """
        Calculates rumen undegradable protein (RUP) percentages of feeds in ration.

        Parameters
        ----------
        feeds : list[FeedInRation]
            List of feeds in ration, including the amount and nutritive properties.
        rumen_degradable_protein_percentages : dict[RUFAS_ID, float]
            Mapping of RuFaS Feed IDs to RDP percentages.

        Returns
        -------
        dict[RUFAS_ID, float]
            Mapping of RuFaS Feed IDs to RUP percentages (percent).

        References
        ----------
        Animal Scientific documentation [A.Cow.E.12]-[A.Cow.E.12]

        """
        rup_percentages: dict[RUFAS_ID, float] = {}

        for feed in feeds:
            rup_percentages[feed.info.rufas_id] = (
                feed.info.CP - rumen_degradable_protein_percentages[feed.info.rufas_id]
            )

        return rup_percentages

    @classmethod
    def _calculate_nutritive_content(cls, feeds: list[FeedInRation], nutrient: str) -> float:
        """
        Calculates the content of a specific nutrient in a ration.

        Parameters
        ----------
        feeds : list[FeedInRation]
            List of feeds in ration, including the amount and nutritive properties.
        nutrient : str
            Name of the nutrient.

        Returns
        -------
        float
            Total supply of nutrient in a ration (kg).

        """
        return sum(
            [feed.amount * getattr(feed.info, nutrient) * GeneralConstants.PERCENTAGE_TO_FRACTION for feed in feeds]
        )

    @classmethod
    def _calculate_digestible_energy(cls, feeds: list[FeedInRation]) -> float:
        """
        Calculates the amount of digestible energy in a ration.

        Parameters
        ----------
        feeds : list[FeedInRation]
            List of feeds in ration, including the amount and nutritive properties.

        Returns
        -------
        float
            Total supply of nutrient in a ration (Mcal).

        """
        de_attribute = "DE_Base" if cls.nutrient_standard is NutrientStandard.NASEM else "DE"
        return sum([feed.amount * getattr(feed.info, de_attribute) for feed in feeds])

    @classmethod
    def _calculate_byproducts_supply(cls, feeds: list[FeedInRation]) -> float:
        """
        Calculates the amount of byproducts in a ration.

        Parameters
        ----------
        feeds : list[FeedInRation]
            List of feeds in ration, including the amount and nutritive properties.

        Returns
        -------
        float
            Total supply of byproduct in a ration (kg dry matter).

        """
        return sum(
            [
                feed.amount * (1.0 if feed.info.Fd_Category is FeedCategorization.BY_PRODUCT_OTHER else 0.0)
                for feed in feeds
            ]
        )

    @classmethod
    def _calculate_forage_neutral_detergent_fiber_content(cls, feeds: list[FeedInRation]) -> float:
        """
        Calculates the neutral detergent fiber (NDF) content supplied by forages in a ration.

        Parameters
        ----------
        feeds : list[FeedInRation]
            List of feeds in ration, including the amount and nutritive properties.

        Returns
        -------
        float
            Total supply of NDF from forages in a ration (kg).

        """
        return sum(
            [
                feed.amount * feed.info.NDF * GeneralConstants.PERCENTAGE_TO_FRACTION
                for feed in feeds
                if feed.info.feed_type == FeedComponentType.FORAGE
            ]
        )
