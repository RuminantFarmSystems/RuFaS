from numba import njit

from ..animal_constants import DRY
from ..animal_module_constants import AnimalModuleConstants
from ..animal_properties.general_properties import GeneralProperties
from ..animal_properties.milk_production_properties import MilkProductionProperties
from ..data_types.milk_production_record import MilkProductionRecord
from RUFAS.general_constants import GeneralConstants
from RUFAS.time import Time
from RUFAS.util import Utility

import numpy as np


class MilkProduction:
    """
    Handles updating the milk-production related animal attributes.
    """

    @staticmethod
    def perform_daily_milking_update(
        milking_properties: MilkProductionProperties, general_properties: GeneralProperties, time: Time
    ) -> tuple[MilkProductionProperties, GeneralProperties]:
        """
        Handles an animal's daily milking update.

        Parameters
        ----------
        milking_properties : MilkProductionProperties
            Animal properties only used to determine milk production.
        general_properties : GeneralProperties
            Animal properties that are general or are used to determine many animal outcomes.
        time : Time
            Time instance containing the current time of the simulation.

        Returns
        -------
        tuple[MilkingProperties, GeneralProperties]
            Milking and general properties of the animal after milk production-related updates for the current day.

        """
        if not general_properties.milking:
            milking_properties = MilkProduction._update_milking_history(milking_properties, general_properties, time)
            return milking_properties, general_properties

        is_dry_off_day = general_properties.days_in_preg == general_properties.dry_off_day_of_pregnancy
        if is_dry_off_day:
            milking_properties = MilkProduction._update_milking_history(milking_properties, general_properties, time)
            general_properties.events.add_event(general_properties.days_born, time.simulation_day, DRY)
            general_properties.days_in_milk = 0
            general_properties.estimated_daily_milk_produced = 0.0
            milking_properties.true_protein_content = 0.0
            milking_properties.fat_content = 0.0
            milking_properties.latest_305_day_milk_production = 0.0
            milking_properties.crude_protein_percent = 0.0
            milking_properties.true_protein_percent = 0.0
            milking_properties.fat_percent = 0.0
            milking_properties.lactose_percent = 0.0
            return milking_properties, general_properties

        general_properties.days_in_milk += 1
        general_properties.estimated_daily_milk_produced = MilkProduction.calculate_daily_milk_production(
            general_properties.days_in_milk,
            milking_properties.wood_l,
            milking_properties.wood_m,
            milking_properties.wood_n,
        )
        general_properties.estimated_daily_milk_produced = MilkProduction._adjust_milk_production(
            general_properties.estimated_daily_milk_produced, milking_properties.milk_production_reduction
        )

        milking_properties.true_protein_content = (
            general_properties.estimated_daily_milk_produced
            * milking_properties.true_protein_percent
            * GeneralConstants.PERCENTAGE_TO_FRACTION
        )
        milking_properties.fat_content = (
            general_properties.estimated_daily_milk_produced
            * milking_properties.fat_percent
            * GeneralConstants.PERCENTAGE_TO_FRACTION
        )

        milking_properties = MilkProduction._update_milking_history(milking_properties, general_properties, time)

        if general_properties.days_in_milk == 305:
            milk_history = [record["milk_production"] for record in milking_properties.milk_production_history[-305:]]
            milking_properties.latest_305_day_milk_production = np.sum(milk_history)

        return milking_properties, general_properties

    @staticmethod
    @njit
    def calculate_daily_milk_production(
        day_of_milk: int, l_param: float, m_param: float, n_param: float
    ) -> float:
        """
        Calculates the milk yield on the given day using Wood's lactation curve.

        Parameters
        ----------
        day_of_milk : int
            Days into milk of the cow.
        l_param: float
            Wood's lactation curve parameter l.
        m_param: float
            Wood's lactation curve parameter m.
        n_param: float
            Wood's lactation curve parameter n.

        Returns
        -------
        numpy.float64
            Milk yield on the provided day (kg).

        References
        ----------
        Li, M., et al. "Investigating the effect of temporal, geographic, and management factors on US Holstein
        lactation curve parameters." Journal of Dairy Science 105.9 (2022): 7525-7538.

        """
        return l_param * np.power(day_of_milk, m_param) * np.exp(-1 * n_param * day_of_milk)

    @staticmethod
    @njit
    def _adjust_milk_production(milk_production: float, milk_production_reduction: float) -> float:
        """
        Randomly adjusts the milk production on a specific day.

        Parameters
        ----------
        milk_production : float
            Unvaried milk production (kg).

        Returns
        -------
        float
            Milk production that has been varied by a random amount (kg).

        """
        milk_production_variance = Utility.generate_random_number(
            AnimalModuleConstants.DAILY_MILK_VARIATION_MEAN, AnimalModuleConstants.DAILY_MILK_VARIATION_STD_DEV
        )
        milk_production += milk_production_variance - milk_production_reduction
        return milk_production

    @staticmethod
    def _update_milking_history(
        milking_properties: MilkProductionProperties, general_properties: GeneralProperties, time: Time
    ) -> MilkProductionProperties:
        """Updates the milking history kept in a MilkProductionProperties instance."""
        milking_properties.milk_production_history.append(
            MilkProductionRecord(
                simulation_day=time.simulation_day,
                days_in_milk=general_properties.days_in_milk,
                milk_production=general_properties.estimated_daily_milk_produced,
                days_born=general_properties.days_born,
            )
        )
        return milking_properties
