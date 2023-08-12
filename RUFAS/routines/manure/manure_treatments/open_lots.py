from __future__ import annotations

from typing import Tuple

from RUFAS.routines.manure.constants.gas_emission_constants import GasEmissionConstants
from RUFAS.routines.manure.constants.manure_constants import ManureConstants
from RUFAS.routines.manure.gas_emissions.gas_emissions import GasEmissions
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import BaseManureTreatment
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import ManureTreatmentConfig
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput


class OpenLots(BaseManureTreatment):
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
            moisture_effect: float = ManureConstants.DEFAULT_MOISTURE_EFFECT_MICROBIAL_DECOMP,
            days_since_last_tillage: int = ManureConstants.DEFAULT_DAYS_SINCE_LAST_TILLAGE,
            lag: int = ManureConstants.DEFAULT_LAG_TIME,
            carbon_available_in_manure: float = ManureConstants.DEFAULT_CARBON_FRACTION_AVAILABLE_IN_MANURE,
            carbon_available_in_bedding: float = GasEmissionConstants.DEFAULT_CARBON_FRACTION_AVAILABLE_IN_BEDDING
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
            The total solids in the manure-bedding mixture after emissions (kg).
        float
            The dry matter lost from carbon and methane emissions (kg).

        """
        total_solids = bedding_total_solids + manure_total_solids
        temperature_celsius = self._get_current_day_average_temperature_celsius()
        methane_emissions = GasEmissions.calc_open_lots_ifsm_methane_emission(
            manure_volatile_solids=manure_volatile_solids,
            ambient_barn_temp=temperature_celsius
        )
        carbon_decomposition = GasEmissions.calc_total_carbon_decomposition(
            manure_total_solids, bedding_total_solids, days_since_last_tillage,
            lag, moisture_effect, carbon_available_in_manure, carbon_available_in_bedding
        )

        remaining_volatile_solids = manure_volatile_solids - methane_emissions
        dry_matter_loss = 2 * carbon_decomposition + methane_emissions
        remaining_total_solids = total_solids - methane_emissions - 2 * carbon_decomposition

        return remaining_volatile_solids, remaining_total_solids, dry_matter_loss

    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        """
        Calculate the daily output of the compost bedded pack barn manure treatment system.

        Returns:
            A ManureTreatmentDailyOutput object containing the daily output of the
            compost bedded pack barn manure treatment system.

        """
        daily_input = self._current_manure_treatment_daily_input
        simulation_day = daily_input.simulation_day
        pen_id = daily_input.pen_id

        nitrogen_losses = GasEmissions.calc_open_lots_nitrogen_losses(
            daily_nitrogen_input=daily_input.liquid_manure_nitrogen)
        manure_nitrogen = daily_input.liquid_manure_nitrogen - nitrogen_losses
        manure_organic_nitrogen = ManureConstants.COMPOST_BEDDING_ORGANIC_NITROGEN_FRACTION * manure_nitrogen
        manure_inorganic_nitrogen = manure_nitrogen - manure_organic_nitrogen
        manure_inorganic_nitrogen_ammonium = ManureConstants.COMPOST_BEDDING_INORGANIC_NITROGEN_AMMONIUM_FRACTION * manure_inorganic_nitrogen

        remaining_volatile_solids, remaining_total_solids, dry_matter_loss = self._calc_dry_matter_changes(
            manure_total_solids=daily_input.liquid_manure_total_solids,
            bedding_total_solids=self._manure_handler_daily_output.total_bedding_mass,
            manure_volatile_solids=daily_input.liquid_manure_total_volatile_solids,
        )
        initial_total_solids_fraction = (daily_input.liquid_manure_total_solids /
                                         (
                                                 daily_input.liquid_manure_daily_volume * ManureConstants.SOLID_MANURE_DENSITY))
        solid_manure_mass = remaining_total_solids / initial_total_solids_fraction

        manure_potassium = (daily_input.liquid_manure_potassium *
                            (1 - self.config.potassium_removal_efficiency_for_treatment))

        manure_phosphorus = (daily_input.liquid_manure_phosphorus *
                             (1 - self.config.phosphorus_removal_efficiency_for_treatment))
        water_extractable_inorganic_phosphorus = self._current_pen.manure.inorganic_phosphorus_fraction * manure_phosphorus
        water_extractable_organic_phosphorus = self._current_pen.manure.organic_phosphorus_fraction * manure_phosphorus
        non_water_extractable_inorganic_phosphorus = self._current_pen.manure.non_water_inorganic_phosphorus_fraction * manure_phosphorus
        non_water_extractable_organic_phosphorus = self._current_pen.manure.non_water_organic_phosphorus_fraction * manure_phosphorus

        storage_methane = GasEmissions.calc_open_lots_ifsm_methane_emission(
            manure_volatile_solids=daily_input.liquid_manure_total_volatile_solids,
            ambient_barn_temp=self._get_current_day_average_temperature_celsius()
        )
        storage_ammonia = GasEmissions.calc_open_lots_nitrogen_loss_ammonia_emission(
            daily_nitrogen_input=daily_input.liquid_manure_nitrogen,
        )
        storage_nitrous_oxide = GasEmissions.calc_open_lots_nitrogen_loss_nitrous_oxide_emission(
            daily_nitrogen_input=daily_input.liquid_manure_nitrogen,
        )

        daily_output = ManureTreatmentDailyOutput(
            simulation_day=simulation_day,
            pen_id=pen_id,
            solid_manure_total_solids=remaining_total_solids,
            solid_manure_total_volatile_solids=remaining_volatile_solids,
            solid_manure_nitrogen=manure_nitrogen,
            solid_manure_organic_nitrogen=manure_organic_nitrogen,
            solid_manure_inorganic_nitrogen=manure_inorganic_nitrogen,
            solid_manure_inorganic_nitrogen_ammonium=manure_inorganic_nitrogen_ammonium,
            solid_manure_potassium=manure_potassium,
            solid_manure_phosphorus=manure_phosphorus,
            solid_manure_water_extractable_inorganic_phosphorus=water_extractable_inorganic_phosphorus,
            solid_manure_water_extractable_organic_phosphorus=water_extractable_organic_phosphorus,
            solid_manure_non_water_extractable_inorganic_phosphorus=non_water_extractable_inorganic_phosphorus,
            solid_manure_non_water_extractable_organic_phosphorus=non_water_extractable_organic_phosphorus,
            storage_methane=storage_methane,
            storage_ammonia=storage_ammonia,
            storage_nitrous_oxide=storage_nitrous_oxide,
            solid_manure_daily_mass=solid_manure_mass,
        )
        self._accumulate_daily_output(daily_output)

        return daily_output
