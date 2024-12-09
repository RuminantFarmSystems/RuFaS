from collections import namedtuple
from dataclasses import dataclass

from RUFAS.data_structures.feed_storage_to_animal_module_connection import Feed, Type
from RUFAS.biophysical.animal.data_types.nutrition_requirements import EnergyNutritionSupply
from RUFAS.general_constants import GeneralConstants


@dataclass
class FeedInRation:
    amount: float
    info: Feed


class EnergySupplyCalculator:
    """Calculates the energy and nutrients supplied by a ration."""

    @classmethod
    def calculate_energy_nutrient_supply(
        cls, feeds_used: list[Feed], ration_formulation: dict[int, float], average_body_weight: float
    ) -> EnergyNutritionSupply:
        """
        Calculates the energy and nutrients supplied in a ration.

        Parameters
        ----------
        feeds_used : list[Feed]
            List of feeds that were used to construct the ration formulation.
        ration_formulation : dict[int, float]
            Maps the RuFaS ID of a feed to the amount fed in a ration (kg dry matter).

        """
        feeds = [
            FeedInRation(amount=amount, info=next((feed for feed in feeds_used if feed.rufas_id == rufas_id), None))
            for rufas_id, amount in ration_formulation.items()
        ]

        discount = cls.calculate_discount(feeds, average_body_weight)
        actual_tdn_percentages = {feed.info.rufas_id: feed.info.TDN * discount for feed in feeds}
        actual_digestible_energy = {feed.info.rufas_id: feed.info.DE * discount for feed in feeds}

        metabolizable_energy = cls.calculate_actual_metabolizable_energy(feeds, actual_digestible_energy)
        maintenance_energy = cls.calculate_actual_maintenance_net_energy(feeds, metabolizable_energy)
        lactation_energy = cls.calculate_actual_lactation_net_energy(
            feeds, metabolizable_energy, actual_digestible_energy
        )
        growth_energy = cls.calculate_actual_growth_net_energy(feeds, metabolizable_energy)
        calcium = cls.calculate_calcium_supply(feeds)
        phosphorus = cls.calculate_phosphorus_supply(feeds)
        dry_matter_intake = sum([feed.amount for feed in feeds])
        protein = cls.calculate_metabolizable_protein_supply(feeds, dry_matter_intake, actual_tdn_percentages, average_body_weight)

        return EnergyNutritionSupply(
            metabolizable=metabolizable_energy,
            maintenance=maintenance_energy,
            lactation=lactation_energy,
            growth=growth_energy,
            protein=protein,
            calcium=calcium,
            phosphorus=phosphorus,
            dry_matter=dry_matter_intake
        )

    @classmethod
    def calculate_discount(cls, feeds: list[FeedInRation], average_body_weight: float) -> float:
        """Calculates discount applied to Total Digestible Nutrients (TDN) and Digestible Energy (DE)."""
        dry_matter_intake = sum([feed.amount for feed in feeds])

        total_tdn = sum([feed.amount * feed.info.TDN * GeneralConstants.PERCENTAGE_TO_FRACTION for feed in feeds])
        tdn_percentage = (
            total_tdn / dry_matter_intake * GeneralConstants.FRACTION_TO_PERCENTAGE if dry_matter_intake > 0.0 else 0.0
        )

        somatic_body_weight = average_body_weight * 0.96

        if total_tdn < (0.035 * average_body_weight**0.75):
            maintenance_dry_matter_intake = 1.0
        else:
            maintenance_dry_matter_intake = total_tdn / (0.035 * somatic_body_weight**0.75)

        if tdn_percentage < 60.0:
            discount = 1.0
        else:
            discount = (
                tdn_percentage - ((0.18 * tdn_percentage - 10.3) * (maintenance_dry_matter_intake - 1))
            ) / tdn_percentage

        return discount

    @classmethod
    def calculate_actual_metabolizable_energy(
        cls, feeds: list[FeedInRation], actual_digestable_energy: dict[int, float]
    ) -> dict[int, float]:
        """Calculates the actual metabolizable energy of feeds (Mcal)."""
        actual_metabolizable_energy: dict[int, float] = {}

        for feed in feeds:
            if feed.info.feed_type is Type.MINERAL:
                energy = 0.0
            elif feed.info.is_fat is True:
                energy = feed.info.DE
            elif feed.info.EE >= 3.0:
                energy = 1.01 * actual_digestable_energy[feed.info.rufas_id] - 0.45 * 0.0046 * (feed.info.EE - 3.0)
            else:
                energy = 1.01 * actual_digestable_energy[feed.info.rufas_id] - 0.45
            actual_metabolizable_energy[feed.info.rufas_id] = energy
        total = sum([feed.amount * actual_metabolizable_energy[feed.info.rufas_id] for feed in feeds])

        return total

    @classmethod
    def calculate_actual_maintenance_net_energy(
        cls, feeds: list[FeedInRation], actual_metabolizable_energy: dict[int, float]
    ) -> dict[int, float]:
        """Calculates the actual net energy for maintenance of feeds (Mcal)."""
        actual_maintenance_net_energy: dict[int, float] = {}

        for feed in feeds:
            actual_metabolizable = actual_metabolizable_energy[feed.info.rufas_id]
            if feed.info.is_fat is True:
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
    def calculate_actual_lactation_net_energy(
        cls,
        feeds: list[FeedInRation],
        actual_metabolizable_energy: dict[int, float],
        actual_digestible_energy: dict[int, float],
    ) -> float:
        """Calculates the actual net energy for lactation of feeds (Mcal)."""
        actual_lactation_net_energy: dict[int, float] = {}

        for feed in feeds:
            if feed.info.feed_type is Type.MINERAL:
                energy = 0.0
            elif feed.info.is_fat is True:
                energy = 0.8 * actual_digestible_energy[feed.info.rufas_id]
            elif feed.info.EE >= 3.0:
                energy = (
                    0.703 * actual_metabolizable_energy[feed.info.rufas_id]
                    - 0.19
                    + ((0.097 * actual_metabolizable_energy[feed.info.rufas_id] + 0.19) / 97) * (feed.info.EE - 3.0)
                )
            else:
                energy = 0.703 * actual_metabolizable_energy[feed.info.rufas_id] - 0.19
            actual_lactation_net_energy[feed.info.rufas_id] = energy
        total = sum([feed.amount * actual_lactation_net_energy[feed.info.rufas_id] for feed in feeds])

        return total

    @classmethod
    def calculate_actual_growth_net_energy(
        cls, feeds: list[FeedInRation], actual_metabolizable_energy: dict[int, float]
    ) -> float:
        """Calculates actual net energy for growth of feeds (Mcal)."""
        actual_growth_net_energy: dict[int, float] = {}

        for feed in feeds:
            if feed.info.feed_type is Type.MINERAL:
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
    def calculate_calcium_supply(cls, feeds: list[FeedInRation]) -> float:
        """Calculates the calcium supply in the ration (kg)."""  # TODO: check units
        calcium_digestibility: dict[int, float] = {}

        for feed in feeds:
            if feed.info.feed_type is Type.FORAGE:
                ca_digestibility = 0.3
            elif feed.info.feed_type is Type.CONC:
                ca_digestibility = 0.6
            elif feed.info.feed_type is Type.MINERAL:
                ca_digestibility = 0.95
            else:
                ca_digestibility = 0.0
            calcium_digestibility[feed.info.rufas_id] = ca_digestibility

        total = sum(
            [
                feed.amount
                * calcium_digestibility[feed.info.rufas_id]
                * feed.info.calcium
                * GeneralConstants.PERCENTAGE_TO_FRACTION
                for feed in feeds
            ]
        )

        return total * GeneralConstants.GRAMS_TO_KG

    @classmethod
    def calculate_phosphorus_supply(cls, feeds: list[FeedInRation]) -> float:
        """Calculates the phosphorus supply in the ration (kg)."""  # TODO: check units
        phosphorus_digestibility: dict[int, float] = {}

        for feed in feeds:
            if feed.info.feed_type is Type.FORAGE:
                p_digestibility = 0.64
            elif feed.info.feed_type is Type.CONC:
                p_digestibility = 0.7
            elif feed.info.feed_type is Type.MINERAL:
                p_digestibility = 0.8
            else:
                p_digestibility = 0.0
            phosphorus_digestibility[feed.info.rufas_id] = p_digestibility

        total = sum(
            [
                feed.amount
                * phosphorus_digestibility[feed.info.rufas_id]
                * feed.info.phosphorus
                * GeneralConstants.PERCENTAGE_TO_FRACTION
                for feed in feeds
            ]
        )

        return total * GeneralConstants.GRAMS_TO_KG

    @classmethod
    def calculate_metabolizable_protein_supply(
        cls, feeds: list[FeedInRation], dry_matter_intake: float, actual_tdn_percentages: dict[int, float], average_body_weight: float
    ) -> dict[int, float]:
        """Calculates amount of metabolizable protein in ration (kg)."""  # TODO: check units
        concentrate_percentage_of_ration = cls._calculate_percentage_of_concentrates(feeds, dry_matter_intake)
        protein_passage_rates = cls._calculate_protein_passage_rates(
            feeds, dry_matter_intake, average_body_weight, concentrate_percentage_of_ration
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

        metabolizable_protein_tdn = ration_tdn_content * 0.13 * GeneralConstants.KG_TO_GRAMS
        metabolizable_protein_rdp = ration_rdp_content * 0.85 * GeneralConstants.KG_TO_GRAMS
        metabolizable_bacterial_protein_production = float(
            0.64 * min(metabolizable_protein_tdn, metabolizable_protein_rdp)
        )

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
        # TODO: check units
        return metabolizable_bacterial_protein_production + ration_rup_content + 0.4 * 11.8 * dry_matter_intake

    @classmethod
    def _calculate_percentage_of_concentrates(cls, feeds: list[FeedInRation], dry_matter_intake: float) -> float:
        """Calculates percentage of dry matter in ration that is concentrate."""
        dry_matter_from_concentrate = sum([feed.amount for feed in feeds if feed.info.feed_type is Type.CONC])

        return dry_matter_from_concentrate / dry_matter_intake * GeneralConstants.FRACTION_TO_PERCENTAGE

    @classmethod
    def _calculate_protein_passage_rates(
        cls,
        feeds: list[FeedInRation],
        dry_matter_intake: float,
        average_body_weight: float,
        percentage_concentrates: float,
    ) -> dict[int, float]:
        """Calculates the protein passage rate of feeds in ration (percentage / hour)."""
        protein_passage_rates: dict[int, float] = {}

        for feed in feeds:
            if feed.info.feed_type is Type.CONC:
                rate = (
                    2.904
                    + 1.375 * (dry_matter_intake / average_body_weight) * GeneralConstants.FRACTION_TO_PERCENTAGE
                    - 0.02 * percentage_concentrates
                )
            elif feed.info.feed_type is Type.FORAGE and feed.info.is_wetforage is False:
                rate = (
                    3.362
                    + 0.479 * (dry_matter_intake / average_body_weight) * GeneralConstants.FRACTION_TO_PERCENTAGE
                    - 0.017 * feed.info.NDF
                    - 0.007 * percentage_concentrates
                )
            elif feed.info.is_wetforage is True:
                rate = (
                    3.054 + 0.614 * (dry_matter_intake / average_body_weight) * GeneralConstants.FRACTION_TO_PERCENTAGE
                )
            else:
                rate = 0.0
            protein_passage_rates[feed.info.rufas_id] = rate

        return protein_passage_rates

    @classmethod
    def _calculate_rumen_degradable_protein_percentages(
        cls, feeds: list[FeedInRation], protein_passage_rates: dict[int, float]
    ) -> dict[int, float]:
        """Calculates rumen degradable protein (RDP) percentages of feeds in ration."""
        rdp_percentages: dict[int, float] = {}

        for feed in feeds:
            passage_rate = protein_passage_rates[feed.info.rufas_id]
            kd = feed.info.Kd  # TODO: unabbreviate kd
            if passage_rate > -kd:
                rdp = (kd / (kd + passage_rate)) * (
                    feed.info.N_B * GeneralConstants.PERCENTAGE_TO_FRACTION
                ) * feed.info.CP + (feed.info.N_A * GeneralConstants.PERCENTAGE_TO_FRACTION) * feed.info.CP
            else:
                rdp = 0.0
            rdp_percentages[feed.info.rufas_id] = rdp

        return rdp_percentages

    @classmethod
    def _calculate_rumen_undegradable_protein_percentages(
        cls, feeds: list[FeedInRation], rumen_degradable_protein_percentages: dict[int, float]
    ) -> dict[int, float]:
        """Calculates rumen undegradable protein (RUP) percentages of feeds in ration."""
        rup_percentages: dict[int, float] = {}

        for feed in feeds:
            rup_percentages[feed.info.rufas_id] = (
                feed.info.CP - rumen_degradable_protein_percentages[feed.info.rufas_id]
            )

        return rup_percentages
