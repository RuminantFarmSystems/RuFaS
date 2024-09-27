import numpy as np
from numba import njit

from RUFAS.biophysical.animal.animal_constants import DRY
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.animal_properties.general_properties import GeneralProperties
from RUFAS.biophysical.animal.animal_properties.milk_production_properties import MilkProductionProperties
from RUFAS.biophysical.animal.data_types.milk_production_record import MilkProductionRecord
from RUFAS.general_constants import GeneralConstants
from RUFAS.time import Time
from RUFAS.util import Utility


class MilkProduction:
    """
    Handles updating the milk-production related animal attributes.

    Attributes
    ----------
    FAT_PERCENT : float
        Class constant which stores the user-defined fat percentage of milk (by weight).
    TRUE_PROTEIN_PERCENT : float
        Class constant which stores the user-defined true protein percentage of milk (by weight).

    Notes
    -----
    The class constants for fat and true protein percentages in milk are intented to be stores. The actual fat and true
    protein percentages of an individual animal will be stored in the MilkProductionProperties instance associated with
    that animal.

    """

    FAT_PERCENT = None
    TRUE_PROTEIN_PERCENT = None

    @classmethod
    def set_milk_quality(cls, fat_percent: float, true_protein_percent: float) -> None:
        """Sets user-defined milk qualities."""
        cls.FAT_PERCENT = fat_percent
        cls.TRUE_PROTEIN_PERCENT = true_protein_percent

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
        if not general_properties.is_milking:
            milking_properties = MilkProduction._update_milking_history(milking_properties, general_properties, time)
            return milking_properties, general_properties

        is_dry_off_day = general_properties.days_in_preg == general_properties.dry_off_day_of_pregnancy
        if is_dry_off_day:
            general_properties.events.add_event(general_properties.days_born, time.simulation_day, DRY)
            general_properties.days_in_milk = 0
            general_properties.daily_milk_produced = 0.0
            milking_properties.crude_protein_content = 0.0
            milking_properties.true_protein_content = 0.0
            milking_properties.fat_content = 0.0
            milking_properties.lactose_content = 0.0
            milking_properties.current_lactation_305_day_milk_produced = 0.0
            milking_properties.crude_protein_percent = 0.0
            milking_properties.true_protein_percent = 0.0
            milking_properties.fat_percent = 0.0
            milking_properties.lactose_percent = 0.0
            milking_properties = MilkProduction._update_milking_history(milking_properties, general_properties, time)
            return milking_properties, general_properties

        general_properties.days_in_milk += 1
        general_properties.daily_milk_produced = MilkProduction.calculate_daily_milk_production(
            general_properties.days_in_milk,
            milking_properties.wood_l,
            milking_properties.wood_m,
            milking_properties.wood_n,
        )
        general_properties = MilkProduction._adjust_milk_production(milking_properties, general_properties)
        milking_properties.crude_protein_content = MilkProduction._calculate_nutrient_content(
            general_properties.daily_milk_produced, milking_properties.crude_protein_content
        )
        milking_properties.true_protein_content = MilkProduction._calculate_nutrient_content(
            general_properties.daily_milk_produced, milking_properties.true_protein_percent
        )
        milking_properties.fat_content = MilkProduction._calculate_nutrient_content(
            general_properties.daily_milk_produced, milking_properties.fat_percent
        )
        milking_properties.lactose_content = MilkProduction._calculate_nutrient_content(
            general_properties.daily_milk_produced, milking_properties.lactose_percent
        )

        milking_properties = MilkProduction._update_milking_history(milking_properties, general_properties, time)

        if general_properties.days_in_milk == 305:
            milk_history = [record["milk_production"] for record in milking_properties.milk_production_history[-305:]]
            milking_properties.current_lactation_305_day_milk_produced = np.sum(milk_history)

        return milking_properties, general_properties

    @staticmethod
    @njit
    def calculate_daily_milk_production(days_in_milk: int, l_param: float, m_param: float, n_param: float) -> float:
        """
        Calculates the milk yield on the given day using Wood's lactation curve.

        Parameters
        ----------
        days_in_milk : int
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
        return l_param * np.power(days_in_milk, m_param) * np.exp(-1 * n_param * days_in_milk)

    @staticmethod
    def _adjust_milk_production(
        milking_properties: MilkProductionProperties, general_properties: GeneralProperties
    ) -> GeneralProperties:
        """
        Randomly adjusts the milk production on a specific day.

        Parameters
        ----------
        milking_properties : MilkProductionProperties
            Animal properties only used to determine milk production.
        general_properties : GeneralProperties
            Animal properties that are general or are used to determine many animal outcomes.

        Returns
        -------
        general_properties : GeneralProperties
            Animal properties with the daily_milk_produced attribute updated.

        """
        milk_production_variance = Utility.generate_random_number(
            AnimalModuleConstants.DAILY_MILK_VARIATION_MEAN, AnimalModuleConstants.DAILY_MILK_VARIATION_STD_DEV
        )
        general_properties.daily_milk_produced += (
            milk_production_variance + milking_properties.milk_production_reduction
        )
        return general_properties

    @staticmethod
    def _calculate_nutrient_content(milk: float, nutrient_percentage: float) -> float:
        """
        Calculates the amount of a given nutrient in milk.

        Parameters
        ----------
        milk : float
            Amount of milk produced (kg).
        nutrient_percentage : float
            Percentage of nutrient in the milk.

        Returns
        -------
        float
            Amount of nutrient contained in the milk (kg).

        """
        return milk * nutrient_percentage * GeneralConstants.PERCENTAGE_TO_FRACTION

    @staticmethod
    def _update_milking_history(
        milking_properties: MilkProductionProperties, general_properties: GeneralProperties, time: Time
    ) -> MilkProductionProperties:
        """Updates the milking history kept in a MilkProductionProperties instance."""
        milking_properties.milk_production_history.append(
            MilkProductionRecord(
                simulation_day=time.simulation_day,
                days_in_milk=general_properties.days_in_milk,
                milk_production=general_properties.daily_milk_produced,
                days_born=general_properties.days_born,
            )
        )
        return milking_properties
