import numpy as np
from numba import njit
from scipy.integrate import quad

from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_constants import DRY
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.milk_production import MilkProductionInputs, MilkProductionOutputs
from RUFAS.biophysical.animal.data_types.milk_production_record import MilkProductionRecord
from RUFAS.general_constants import GeneralConstants
from RUFAS.rufas_time import RufasTime
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
    The class constants for fat and true protein percentages in milk are intended to be stores. The actual fat and true
    protein percentages of an individual animal will be stored in the MilkProductionProperties instance associated with
    that animal.

    """

    crude_protein_content: float
    true_protein_content: float
    fat_content: float
    lactose_content: float
    milk_production_reduction: float
    milk_305_day_yield: float
    crude_protein_percent: float
    true_protein_percent: float
    fat_percent: float
    lactose_percent: float
    wood_l: float
    wood_m: float
    wood_n: float
    milk_production_history: list[MilkProductionRecord]

    def __init__(self) -> None:
        self._daily_milk_produced = 0.0
        self._milk_production_variance = Utility.generate_random_number(
            AnimalModuleConstants.DAILY_MILK_VARIATION_MEAN, AnimalModuleConstants.DAILY_MILK_VARIATION_STD_DEV
        )
        self.crude_protein_content = 0.0
        self.true_protein_content = 0.0
        self.fat_content = 0.0
        self.lactose_content = 0.0
        self.milk_production_reduction = 0.0
        self.milk_production_history = []
        self.milk_305_day_yield = 0.0

    @property
    def daily_milk_produced(self) -> float:
        adjusted_milk_production = max(
            self._daily_milk_produced + (self._milk_production_variance - self.milk_production_reduction), 0.0
        )
        return adjusted_milk_production if self._daily_milk_produced > 0.0 else 0.0

    @daily_milk_produced.setter
    def daily_milk_produced(self, value: float) -> None:
        self._daily_milk_produced = value

    @classmethod
    def set_milk_quality(cls, fat_percent: float, true_protein_percent: float, lactose_percent: float) -> None:
        """Sets user-defined milk qualities."""
        cls.fat_percent = fat_percent
        cls.true_protein_percent = true_protein_percent
        cls.lactose_percent = lactose_percent

    def set_wood_parameters(self, wood_l: float, wood_m: float, wood_n: float) -> None:
        self.wood_l = wood_l
        self.wood_m = wood_m
        self.wood_n = wood_n

    def _get_current_lactation_history(self) -> list[MilkProductionRecord]:
        """Returns only the current lactation records from the full milk history."""
        current_lactation_history: list[MilkProductionRecord] = []
        for record in reversed(self.milk_production_history):
            if record["days_in_milk"] == 0:
                break
            current_lactation_history.append(record)

        current_lactation_history.reverse()
        return current_lactation_history

    def perform_daily_milking_update(
        self, milk_production_inputs: MilkProductionInputs, time: RufasTime
    ) -> MilkProductionOutputs:
        """
        Handles an animal's daily milking update.

        Parameters
        ----------
        milking_properties : MilkProductionProperties
            Animal properties only used to determine milk production.
        general_properties : GeneralProperties
            Animal properties that are general or are used to determine many animal outcomes.
        time : RufasTime
            RufasTime instance containing the current time of the simulation.

        Returns
        -------
        tuple[MilkingProperties, GeneralProperties]
            Milking and general properties of the animal after milk production-related updates for the current day.

        """
        milk_production_outputs = MilkProductionOutputs(
            events=AnimalEvents(), days_in_milk=milk_production_inputs.days_in_milk
        )

        if not milk_production_inputs.is_milking:
            self.daily_milk_produced = 0.0
            self._update_milking_history(
                days_in_milk=milk_production_inputs.days_in_milk,
                days_born=milk_production_inputs.days_born,
                daily_milk_produced=self.daily_milk_produced,
                time=time,
            )
            return milk_production_outputs

        is_dry_off_day = milk_production_inputs.days_in_pregnancy == AnimalConfig.dry_off_day_of_pregnancy
        if is_dry_off_day:
            milk_production_outputs.events.add_event(milk_production_inputs.days_born, time.simulation_day, DRY)
            milk_production_outputs.days_in_milk = 0
            self.daily_milk_produced = 0.0
            self.crude_protein_content = 0.0
            self.true_protein_content = 0.0
            self.fat_content = 0.0
            self.lactose_content = 0.0
            self._update_milking_history(
                days_in_milk=milk_production_outputs.days_in_milk,
                days_born=milk_production_inputs.days_born,
                daily_milk_produced=self.daily_milk_produced,
                time=time,
            )
            return milk_production_outputs

        milk_production_outputs.days_in_milk += 1
        self._daily_milk_produced = self.calculate_daily_milk_production(
            milk_production_inputs.days_in_milk,
            self.wood_l,
            self.wood_m,
            self.wood_n,
        )
        self._milk_production_variance = Utility.generate_random_number(
            AnimalModuleConstants.DAILY_MILK_VARIATION_MEAN, AnimalModuleConstants.DAILY_MILK_VARIATION_STD_DEV
        )
        self.crude_protein_content = self._calculate_nutrient_content(
            self.daily_milk_produced, self.crude_protein_content
        )
        self.true_protein_content = self._calculate_nutrient_content(
            self.daily_milk_produced, self.true_protein_percent
        )
        self.fat_content = self._calculate_nutrient_content(self.daily_milk_produced, self.fat_percent)
        self.lactose_content = self._calculate_nutrient_content(self.daily_milk_produced, self.lactose_percent)

        self._update_milking_history(
            days_in_milk=milk_production_outputs.days_in_milk,
            days_born=milk_production_inputs.days_born,
            daily_milk_produced=self.daily_milk_produced,
            time=time,
        )

        return milk_production_outputs

    def perform_daily_milking_update_without_history(
        self, milk_production_inputs: MilkProductionInputs
    ) -> MilkProductionOutputs:
        """
        Handles an animal's daily milking update, without updating the milk history attributes.
        This method is intended to be utilized only prior to the first ration formulation.

        Parameters
        ----------
        milk_production_inputs : MilkProductionProperties
            Animal properties only used to determine milk production.

        Returns
        -------
        MilkProductionOutputs
            Milking properties of the animal after milk production-related updates for the current day.

        """
        milk_production_outputs = MilkProductionOutputs(
            events=AnimalEvents(), days_in_milk=milk_production_inputs.days_in_milk
        )

        if not milk_production_inputs.is_milking:
            self.daily_milk_produced = 0.0
            return milk_production_outputs

        is_dry_off_day = milk_production_inputs.days_in_pregnancy == AnimalConfig.dry_off_day_of_pregnancy
        if is_dry_off_day:
            self.daily_milk_produced = 0.0
            self.crude_protein_content = 0.0
            self.true_protein_content = 0.0
            self.fat_content = 0.0
            self.lactose_content = 0.0
            return milk_production_outputs

        milk_production_outputs.days_in_milk += 1
        self._daily_milk_produced = self.calculate_daily_milk_production(
            milk_production_inputs.days_in_milk,
            self.wood_l,
            self.wood_m,
            self.wood_n,
        )
        self._milk_production_variance = Utility.generate_random_number(
            AnimalModuleConstants.DAILY_MILK_VARIATION_MEAN, AnimalModuleConstants.DAILY_MILK_VARIATION_STD_DEV
        )
        self.crude_protein_content = self._calculate_nutrient_content(
            self.daily_milk_produced, self.crude_protein_content
        )
        self.true_protein_content = self._calculate_nutrient_content(
            self.daily_milk_produced, self.true_protein_percent
        )
        self.fat_content = self._calculate_nutrient_content(self.daily_milk_produced, self.fat_percent)
        self.lactose_content = self._calculate_nutrient_content(self.daily_milk_produced, self.lactose_percent)

        return milk_production_outputs

    @staticmethod
    @njit
    def calculate_daily_milk_production(days_in_milk: int, l_param: float, m_param: float, n_param: float) -> float:
        """
        Calculates the milk yield on the given day using Wood's lactation curve.

        Notes
        -----
        [AN.MLK.9]

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
    def calculate_predicted_305_day_milk_yield(l_param: float, m_param: float, n_param: float) -> float:
        """
        Predicted 305-day milk yield from Wood's lactation curve alone — the integral of
        the daily-production curve from day 1 to 305, with no per-cow history involved.

        This is the metric used when fitting Wood's l parameter to a target annual yield
        at the start of the simulation, and is also the fallback when a cow has no
        current-lactation history yet (e.g. dry cows at sim start).

        Notes
        -----
        [AN.MLK.10]

        Parameters
        ----------
        l_param, m_param, n_param : float
            Wood's lactation curve parameters l, m, and n.

        Returns
        -------
        float
            305-day milk yield from Wood's curve (kg).
        """
        result, _ = quad(MilkProduction.calculate_daily_milk_production, 1, 305, args=(l_param, m_param, n_param))
        return result

    def calculate_305_day_milk_yield(self) -> float:
        """
        Per-cow estimate of the cow's current-lactation 305-day milk yield, combining
        observed daily production with Wood's-curve predictions for any unobserved DIMs
        in 1..305. This keeps the metric meaningful early in the simulation (or for cows
        that were mid-lactation at sim start) when actual history doesn't yet span all
        305 days. Cows with no current-lactation history fall back to the pure predicted
        yield from ``calculate_predicted_305_day_milk_yield``.

        Use ``calculate_predicted_305_day_milk_yield`` instead when fitting Wood's
        parameters — that's the optimization hot path and doesn't need any of the
        per-cow logic here.

        Returns
        -------
        float
            305-day milk yield estimate for the current lactation (kg).
        """
        current_lactation_history = self._get_current_lactation_history()
        observed_records = [record for record in current_lactation_history if 1 <= record["days_in_milk"] <= 305]

        if not observed_records:
            return MilkProduction.calculate_predicted_305_day_milk_yield(self.wood_l, self.wood_m, self.wood_n)

        actual_production = sum(record["milk_production"] for record in observed_records)
        observed_dims = sorted(record["days_in_milk"] for record in observed_records)
        earliest_observed = observed_dims[0]
        latest_observed = observed_dims[-1]

        early_predicted = 0.0
        if earliest_observed > 1:
            early_predicted, _ = quad(
                MilkProduction.calculate_daily_milk_production,
                1,
                earliest_observed,
                args=(self.wood_l, self.wood_m, self.wood_n),
            )

        late_predicted = 0.0
        if latest_observed < 305:
            late_predicted, _ = quad(
                MilkProduction.calculate_daily_milk_production,
                latest_observed + 1,
                305,
                args=(self.wood_l, self.wood_m, self.wood_n),
            )

        return actual_production + early_predicted + late_predicted

    def _get_milk_production_adjustment(self) -> float:
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

        return milk_production_variance - self.milk_production_reduction

    def _calculate_nutrient_content(self, milk: float, nutrient_percentage: float) -> float:
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

    def _update_milking_history(
        self, days_in_milk: int, daily_milk_produced: float, days_born: int, time: RufasTime
    ) -> None:
        """Updates the milking history kept in a MilkProductionProperties instance."""
        self.milk_production_history.append(
            MilkProductionRecord(
                simulation_day=time.simulation_day,
                days_in_milk=days_in_milk,
                milk_production=daily_milk_produced,
                days_born=days_born,
            )
        )
