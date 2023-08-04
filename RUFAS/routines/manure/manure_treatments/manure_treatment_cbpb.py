from __future__ import annotations
from typing import Tuple

from RUFAS.routines.manure.manure_treatments.base_manure_treatment import BaseManureTreatment
from RUFAS.routines.manure.gas_emissions.gas_emissions import GasEmissions
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import ManureTreatmentConfig
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput


class CompostBeddedPackBarn(BaseManureTreatment):
    """Class for the compost bedded pack barn.

    Attributes:
        All attributes inherited from BaseManureTreatment.

    """

    def __init__(self, weather, time, manure_treatment_config: ManureTreatmentConfig) -> None:
        """Initializes the compost bedded pack barn manure treatment.

        Args:
            weather: A Weather object.
            time: A Time object.
            manure_treatment_config: A ManureTreatmentConfig object containing
                the configuration data for the manure treatment system.
        """

        super().__init__(weather, time, manure_treatment_config)

    def _calc_bedding_potassium_content(
        self,
        current_manure_bedding_mix_potassium: float,
        additional_potassium_in_manure: float,
        additional_potassium_in_bedding: float = 0,
        potassium_loss: float = 0
    ) -> float:
        """Calculates the potassium content of the manure-bedding mixture.

        Parameters
        ----------
        current_manure_bedding_mix_potassium : float
          The current potassium content of the manure-bedding mixture.

        additional_potassium_in_manure : float
          The amount of potassium in the current day's manure production amount.

        additional_potassium_in_bedding : float
          The amount of potassium in the current day's additional bedding amount.

        potassium_loss : float
          Loss of potassium within the compost bedded pack barn.

        Returns
        -------
        float
            The total potassium within the compost bedded pack barn's manure-bedding mixture (in kg).

        """
        return (
            current_manure_bedding_mix_potassium
            + additional_potassium_in_manure
            + additional_potassium_in_bedding
            - potassium_loss
        )

    def _calc_dry_matter_changes(
            self,
            manure_total_solids: float,
            bedding_total_solids: float,
            manure_volatile_solids: float,
            days_since_last_tillage: int,
            lag: int,
            moisture_effect: float,
            carbon_available_in_manure: float,
            carbon_available_in_bedding: float
    ) -> Tuple[float, float, float]:
        """Calculates the changes in dry-matter for the manure-bedding mixture.

        Parameters
        ----------
        manure_total_solids : float
            The total mass of the manure (kg).
        bedding_total_solids : float
            The mass of the bedding material (kg).
        manure_volatile_solids : float
            The mass of manure volatile solids (kg).
        days_since_last_tillage : float
            The number of days since the manure-bedding mixture was last tilled.
        lag : int
            The lag time
        moisture_effect : float
            The effect of moisture on microbial decomposition (unitless)
        carbon_available_in_manure : float
            The proportion of carbon available in manure (unitless)
        carbon_available_in_bedding : float
            The proportion of carbon available in the bedding material (unitless)

        Returns
        -------
        float
            The total volatile solids in the manure-bedding mixture after emissions (kg).
        float
            The total solids in the manure-bedding mixtrue after emissions (kg).
        float
            The dry matter lost from carbon and methane emissions (kg).

        """
        total_solids = bedding_total_solids + manure_total_solids
        temperature_celsius = self._get_current_day_average_temperature_celsius()
        methane_emissions = GasEmissions.calc_ifsm_methane_emission(
            manure_volatile_solids, temperature_celsius)
        carbon_decomposition = GasEmissions.calc_total_carbon_decomposition(
            manure_total_solids, bedding_total_solids, days_since_last_tillage,
            lag, moisture_effect, carbon_available_in_manure, carbon_available_in_bedding
        )

        remaining_volatile_solids = manure_volatile_solids - methane_emissions
        dry_matter_loss = 2 * carbon_decomposition + methane_emissions
        remaining_total_solids = total_solids - methane_emissions - 2 * carbon_decomposition

        return (remaining_volatile_solids, remaining_total_solids, dry_matter_loss)

    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        """Returns the daily output of the outdoor slurry storage treatment system.

        Returns:
            A ManureTreatmentDailyOutput object containing the daily output of the
            slurry storage outdoor treatment system.

        """
        daily_output = self._initialize_daily_output_during_update(self._current_manure_treatment_daily_input)
        self._accumulate_daily_output(daily_output)

        return daily_output
