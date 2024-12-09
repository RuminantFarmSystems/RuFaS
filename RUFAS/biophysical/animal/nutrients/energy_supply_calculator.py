from collections import namedtuple
from dataclasses import dataclass

from RUFAS.data_structures.feed_storage_to_animal_module_connection import (
    Feed,
    Type,
    NASEMFeed,
    NRCFeed,
    NutrientStandard,
)
from RUFAS.biophysical.animal.data_types.nutrition_requirements import EnergyNutritionSupply
from RUFAS.general_constants import GeneralConstants


# FeedInRation = namedtuple("FeedInRation", ["amount", "info"])
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
        total_energy = cls.calculate_total_energy(feeds)

    @classmethod
    def calculate_total_energy(cls, feeds: list[FeedInRation], average_body_weight: float) -> float:
        dry_matter_intake = sum([feed.amount for feed in feeds])

        total_tdn = sum([feed.amount * feed.info.TDN * 0.01 for feed in feeds])
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

        actual_tdn_percentage = {feed.info.rufas_id: feed.info.TDN * discount for feed in feeds}

        actual_digestible_energy = {feed.info.rufas_id: feed.info.DE * discount for feed in feeds}

    @classmethod
    def calculate_actual_metabolizable_energy(
        cls, feeds: list[FeedInRation], actual_digestable_energy: dict[int, float]
    ) -> dict[int, float]:
        """Calculates the actual metabolizable energy of feeds (Mcal / kg)."""
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

        return actual_metabolizable_energy

    @classmethod
    def calculate_actual_maintenance_net_energy(
        cls, feeds: list[FeedInRation], actual_metabolizable_energy: dict[int, float]
    ) -> dict[int, float]:
        """Calculates the actual net energy for maintenance of feeds (Mcal / kg)."""
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

        return actual_maintenance_net_energy

    @classmethod
    def calculate_actual_lactation_net_energy(
        cls,
        feeds: list[FeedInRation],
        actual_metabolizable_energy: dict[int, float],
        actual_digestible_energy: dict[int, float],
    ) -> dict[int, float]:
        """Calculates the actual net energy for lactation of feeds (Mcal / kg)."""
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

        return actual_lactation_net_energy

    @classmethod
    def calculate_actual_growth_net_energy(
        cls, feeds: list[FeedInRation], actual_metabolizable_energy: dict[int, float]
    ) -> dict[int, float]:
        """Calculates actual net energy for growth of feeds (Mcal / kg)."""
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

        return actual_growth_net_energy
