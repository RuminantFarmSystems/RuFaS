from __future__ import annotations

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.manure.constants_and_units.gas_emission_constants import (
    GasEmissionConstants,
)
from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants
from RUFAS.routines.manure.gas_emissions.calculator import (
    GasEmissionsCalculator,
)
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import (
    BaseManureTreatment,
)
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import (
    ManureTreatmentDailyOutput,
)
from RUFAS.routines.manure.manure_treatments.manure_treatment_types import (
    ManureTreatmentType,
)


class AnaerobicDigestion(BaseManureTreatment):
    """A class that calculates the output of an anaerobic digester.

    Attributes:
        Same as BaseManureTreatment.

    """

    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        """Updates the daily output from anaerobic digestion.

        Returns:
            The daily output from anaerobic digestion.

        """
        daily_input = self._current_manure_treatment_daily_input
        daily_output = self._initialize_daily_output_during_update(daily_input)
        daily_output = self._calc_anaerobic_digestion_daily_output(daily_output)
        self._adjust_accumulated_output(daily_output)

        daily_output.storage_nitrous_oxide = self._calc_empirical_nitrogen_loss_from_nitrous_oxide_emission(
            manure_treatment_type=ManureTreatmentType.ANAEROBIC_DIGESTION,
            manure_cover=self.config.manure_cover,
            manure_nitrogen_kg_N_per_day=daily_output.liquid_manure_nitrogen,
        )
        daily_output.liquid_manure_nitrogen -= daily_output.storage_nitrous_oxide
        self._accumulated_output.storage_nitrous_oxide += daily_output.storage_nitrous_oxide
        self._accumulated_output.liquid_manure_nitrogen -= daily_output.storage_nitrous_oxide

        return daily_output

    def _calc_anaerobic_digestion_daily_output(
        self, manure_treatment_daily_output: ManureTreatmentDailyOutput
    ) -> ManureTreatmentDailyOutput:
        """Returns the daily output from anaerobic digestion.

        Args:

        Returns:
            The daily output from anaerobic digestion.

        """
        daily_final_manure_volume = manure_treatment_daily_output.daily_final_manure_volume
        new_daily_output = manure_treatment_daily_output.clone()

        moisture_content = self._calc_moisture_content(
            total_daily_mass=daily_final_manure_volume,
            liquid_manure_total_solids=self._manure_handler_daily_output.liquid_manure_total_solids,
        )
        average_temperature_celsius = self._get_current_day_average_temperature_celsius()
        heating_input_energy = (
            self._calc_specific_input_energy(average_temperature_celsius, moisture_content)
            * daily_final_manure_volume
            * GeneralConstants.LITERS_TO_CUBIC_METERS
        )
        # MS.3.B.7R
        total_methane_generation_volume = GasEmissionsCalculator.calculate_CSTR_methane_volume(
            manure_total_volatile_solids=self._current_manure_treatment_daily_input.liquid_manure_total_volatile_solids
        )
        # MS.3.B.2
        minimum_digester_volume = daily_final_manure_volume * self.config.hydraulic_retention_time
        # MS.3.B.3
        top_cover_volume = minimum_digester_volume * self.config.top_cover_volume_fraction

        new_daily_output.liquid_manure_total_ammoniacal_nitrogen = min(
            self._current_manure_treatment_daily_input.liquid_manure_total_ammoniacal_nitrogen
            * ManureConstants.AD_TAN_INCREASE_FACTOR,
            self._current_manure_treatment_daily_input.liquid_manure_nitrogen,
        )
        total_methane_generation_mass = total_methane_generation_volume * GasEmissionConstants.AD_METHANE_DENSITY
        AD_carbon_dioxide = (
            total_methane_generation_volume * GasEmissionConstants.AD_CARBON_DIOXIDE_TO_METHANE_RATIO
        ) * GasEmissionConstants.AD_CARBON_DIOXIDE_DENSITY
        AD_VS_destruction = total_methane_generation_mass + AD_carbon_dioxide

        new_daily_output.liquid_manure_total_solids = (
            self._current_manure_treatment_daily_input.liquid_manure_total_solids - AD_VS_destruction
        )
        new_daily_output.liquid_manure_total_volatile_solids = (
            self._current_manure_treatment_daily_input.liquid_manure_total_volatile_solids - AD_VS_destruction
        )
        new_daily_output.liquid_manure_total_degradable_volatile_solids = (
            self._current_manure_treatment_daily_input.liquid_manure_total_degradable_volatile_solids
            - AD_VS_destruction
        )
        new_daily_output.liquid_manure_total_non_degradable_volatile_solids = (
            self._current_manure_treatment_daily_input.liquid_manure_total_non_degradable_volatile_solids
        )

        new_daily_output.daily_final_manure_volume = (
            self._current_manure_treatment_daily_input.liquid_manure_daily_volume
            - (AD_VS_destruction / ManureConstants.SLURRY_MANURE_DENSITY)
        )
        methane_leakage = GasEmissionsCalculator.calculate_digester_methane_leakage(
            total_methane_generation_volume, self.config.digester_methane_leakage_fraction
        )
        captured_methane_generation_volume = total_methane_generation_volume - methane_leakage
        captured_methane_generation_mass = captured_methane_generation_volume * GasEmissionConstants.AD_METHANE_DENSITY
        captured_methane_energy_content = GasEmissionsCalculator.calculate_methane_energy_content(
            methane_mass=captured_methane_generation_mass
        )
        new_daily_output.heating_input_energy = heating_input_energy
        new_daily_output.evaporated_water = self.config.evaporation_fraction * daily_final_manure_volume
        new_daily_output.methane_energy_content = captured_methane_energy_content
        new_daily_output.minimum_digester_volume = minimum_digester_volume
        new_daily_output.top_cover_volume = top_cover_volume
        new_daily_output.methane_leakage_volume = methane_leakage
        new_daily_output.methane_generation_volume = captured_methane_generation_volume
        new_daily_output.methane_generation_mass = captured_methane_generation_mass
        return new_daily_output

    @classmethod
    def _calc_moisture_content(cls, total_daily_mass: float, liquid_manure_total_solids: float) -> float:
        """Returns moisture_content of influent as decimal (0-1).

        Args:
            total_daily_mass: Total daily mass of influent, kg.
            liquid_manure_total_solids: Total solids of influent, kg.

        Returns:
            Moisture content of influent as decimal (0-1).

        """
        if total_daily_mass > 0:
            return 1 - (liquid_manure_total_solids / total_daily_mass)
        return 0.0

    def _calc_specific_input_energy(self, average_temperature_celsius, moisture_content) -> float:
        """Returns the energy required to maintain anaerobic digestion temperature at set point.

        Args:
            average_temperature_celsius: Average daily temperature, C.
            moisture_content: A 0-1 decimal representing water content of manure.

        Returns:
            Energy required to maintain anaerobic digestion temperature at set point, MJ/m^3.

        """
        effluent_temperature = self._bound_influent_temperature(average_temperature_celsius)
        influent_heat_capacity = self._calc_manure_heat_capacity(average_temperature_celsius, moisture_content)
        anaerobic_digestion_heat_capacity = self._calc_manure_heat_capacity(
            self.config.anaerobic_digestion_temperature_set_point, moisture_content
        )
        average_manure_heat_capacity = (influent_heat_capacity + anaerobic_digestion_heat_capacity) / 2
        heating_input_energy = average_manure_heat_capacity * (
            self.config.anaerobic_digestion_temperature_set_point - effluent_temperature
        )
        return heating_input_energy

    @classmethod
    def _bound_influent_temperature(cls, average_temperature_celsius: float) -> float:
        """Returns the max between the given average temperature and temperature bound.

        Args:
            average_temperature_celsius: Average daily temperature, C.

        """
        return max(average_temperature_celsius, 4.0)  # TODO: Use constants instead - Issue #1120

    @classmethod
    def _calc_manure_heat_capacity(cls, average_temperature_celsius: float, moisture_content: float) -> float:
        """Returns heat capacity of manure.

        Args:
            average_temperature_celsius: Average daily temperature, C.
            moisture_content: A 0-1 decimal representing water content of manure.

        Returns:
            Heat capacity of manure, kJ /kg /C.

        """
        # TODO: Name the constants if you can - Issue #1120
        return 0.68298 + 0.025662 * average_temperature_celsius + 0.01306 * moisture_content * 100

    def _adjust_accumulated_output(
        self, manure_treatment_daily_output: ManureTreatmentDailyOutput
    ) -> ManureTreatmentDailyOutput:
        """Override method of BaseManureTreatment class _adjust_accumulated_output() to accommodate for
        wanting to never empty the manure pit for AnaerobicDigestion"""
        self._accumulated_output += manure_treatment_daily_output
