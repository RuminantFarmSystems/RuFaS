from __future__ import annotations

from typing import List

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.manure.gas_emissions.gas_emissions import GasEmissions
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import BaseManureTreatment
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import ManureTreatmentConfig
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import AnaerobicDigestionOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import SludgeOutput
from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import LiquidManurePortionProtocol


class AnaerobicDigestion(BaseManureTreatment):
    """A class that calculates the output of an anaerobic digester.

    Attributes:
        Same as BaseManureTreatment.

    """

    def __init__(self, weather, time, manure_treatment_config: ManureTreatmentConfig) -> None:
        super().__init__(weather, time, manure_treatment_config)
        self._accumulated_sludge_output = SludgeOutput()
        self.all_ad_output: List[AnaerobicDigestionOutput] = []

    def _create_daily_sludge_output(self, manure_treatment_daily_input: LiquidManurePortionProtocol) -> SludgeOutput:
        """Returns the daily sludge output from anaerobic digestion.

        Args:
            manure_treatment_daily_input: The daily output from the manure treatment.

        Returns:
            The daily sludge output from anaerobic digestion.

        """
        return SludgeOutput(
                sludge_manure_total_solids=(manure_treatment_daily_input.liquid_manure_total_solids *
                                            self.config.total_solids_removal_efficiency_for_treatment),
                sludge_manure_total_volatile_solids=(manure_treatment_daily_input.liquid_manure_total_volatile_solids
                                                     * self.config.volatile_solids_removal_efficiency_for_treatment),
                sludge_manure_nitrogen=(manure_treatment_daily_input.liquid_manure_nitrogen *
                                        self.config.nitrogen_removal_efficiency_for_treatment),
                sludge_manure_phosphorus=(manure_treatment_daily_input.liquid_manure_phosphorus *
                                          self.config.phosphorus_removal_efficiency_for_treatment),
                sludge_manure_potassium=(manure_treatment_daily_input.liquid_manure_potassium *
                                         self.config.potassium_removal_efficiency_for_treatment),
                sludge_manure_daily_volume=(manure_treatment_daily_input.liquid_manure_total_volatile_solids * 0.03 /
                                            1000.0)
        )

    def _accumulate_daily_sludge_output(self, daily_sludge_output: SludgeOutput) -> None:
        """Accumulates the daily sludge output from anaerobic digestion.

        Args:
            daily_sludge_output: The daily sludge output from anaerobic digestion.

        """
        self._accumulated_sludge_output += daily_sludge_output

    def _assign_extra_output_variables(self, daily_output: ManureTreatmentDailyOutput,
                                       daily_sludge_output: SludgeOutput) -> None:
        """Assigns extra output variables for debugging purposes.

        Args:
            daily_output: The daily output from the manure treatment.
            daily_sludge_output: The daily sludge output from anaerobic digestion.

        """
        daily_output.sludge_manure_total_solids = daily_sludge_output.sludge_manure_total_solids
        daily_output.sludge_manure_total_volatile_solids = daily_sludge_output.sludge_manure_total_volatile_solids
        daily_output.sludge_manure_nitrogen = daily_sludge_output.sludge_manure_nitrogen
        daily_output.sludge_manure_phosphorus = daily_sludge_output.sludge_manure_phosphorus
        daily_output.sludge_manure_potassium = daily_sludge_output.sludge_manure_potassium
        daily_output.sludge_volume = daily_sludge_output.sludge_manure_daily_volume
        daily_output.accumulated_sludge_volume = self._accumulated_sludge_output.sludge_manure_daily_volume
        daily_output.accumulated_final_manure_volume = self._accumulated_output.daily_final_manure_volume

    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        """Updates the anaerobic digestion model for a single day."""

        daily_output = self._initialize_daily_output_during_update(self._current_manure_treatment_daily_input)
        self._accumulate_daily_output(daily_output)

        daily_sludge_output = self._create_daily_sludge_output(self._current_manure_treatment_daily_input)
        self._accumulate_daily_sludge_output(daily_sludge_output)

        anaerobic_digestion_daily_output = self._create_anaerobic_digestion_daily_output(
                daily_output.daily_final_manure_volume)
        self.all_ad_output.append(anaerobic_digestion_daily_output)

        self._assign_extra_output_variables(daily_output, daily_sludge_output)
        return daily_output

    def _create_anaerobic_digestion_daily_output(self, final_manure_volume: float) -> AnaerobicDigestionOutput:
        """Returns the daily output from anaerobic digestion.

        Args:
            final_manure_volume: The final manure volume of manure treatment daily output.

        Returns:
            The daily output from anaerobic digestion.

        """
        moisture_content = self._get_moisture_content(
                total_daily_mass=final_manure_volume,
                TS=self._manure_handler_daily_output.liquid_manure_total_solids
        )
        avg_tempC = self._get_current_day_average_temperature_celsius()
        input_energy_heating = (self._calc_specific_input_energy(avg_tempC, moisture_content) *
                                final_manure_volume *
                                GeneralConstants.LITERS_TO_CUBIC_METERS)
        # MS.3.B.7R
        methane_generation_volume = GasEmissions.calc_methane_volume_via_Chen_equation(
                manure_total_volatile_solids=self._manure_handler_daily_output.liquid_manure_total_volatile_solids,
                hydraulic_retention_time=self.config.hydraulic_retention_time
        )
        biogas_energy_content = GasEmissions.calc_biogas_energy_content(methane_volume=methane_generation_volume)
        # MS.3.B.2
        minimum_digester_volume = final_manure_volume * self.config.hydraulic_retention_time
        # MS.3.B.3
        top_cover_volume = minimum_digester_volume * self.config.top_cover_volume_fraction

        anaerobic_digestion_daily_output = AnaerobicDigestionOutput(
                biogas=self.config.biogas_generation_ratio *
                       self._manure_handler_daily_output.liquid_manure_total_volatile_solids,
                input_energy_heating=input_energy_heating,
                evaporated_water=self.config.evaporation_fraction * final_manure_volume,
                methane_generation_volume=methane_generation_volume,
                biogas_energy_content=biogas_energy_content,
                minimum_digester_volume=minimum_digester_volume,
                top_cover_volume=top_cover_volume
        )
        return anaerobic_digestion_daily_output

    @property
    def sludge_volume(self):
        """Returns total accumulated sludge volume.

        Returns:
            Total accumulated sludge volume, m^3.

        """
        return self._accumulated_sludge_output.sludge_manure_total_volatile_solids * GeneralConstants.KG_TO_CUBIC_METERS

    @classmethod
    def _get_moisture_content(cls, total_daily_mass: float, TS: float) -> float:
        """Returns moisture_content of influent as decimal (0-1).

        Args:
            total_daily_mass: Total daily mass of influent, kg.
            TS: Total solids of influent, kg.

        Returns:
            Moisture content of influent as decimal (0-1).

        """
        if total_daily_mass > 0.0:
            return 1 - TS / total_daily_mass
        return 0.0

    def _calc_specific_input_energy(self, avg_tempC, moisture_content) -> float:
        """Returns the energy required to maintain AD temperature at set point.

        Args:
            avg_tempC: Average daily temperature, C.
            moisture_content: A 0-1 decimal representing water content of manure.

        """
        effluent_temperature = self._bound_influent_temperature(avg_tempC)
        heat_capacity_influent = self._calc_heat_capacity_manure(avg_tempC, moisture_content)
        heat_capacity_AD = self._calc_heat_capacity_manure(self.config.anaerobic_digestion_temperature_set_point,
                                                           moisture_content)
        avg_heat_capacity = (heat_capacity_influent + heat_capacity_AD) / 2
        input_energy_heating = avg_heat_capacity * (
                    self.config.anaerobic_digestion_temperature_set_point - effluent_temperature)
        return input_energy_heating

    @classmethod
    def _bound_influent_temperature(cls, avg_tempC: float) -> float:
        """Returns the max between avg_tempC and temperature bound.

        Args:
            avg_tempC: Average daily temperature, C.

        """
        return max(avg_tempC, 4)

    @classmethod
    def _calc_heat_capacity_manure(cls, avg_tempC: float, moisture_content: float) -> float:
        """Returns heat capacity of manure.

        Args:
            avg_tempC: Average daily temperature, C.
            moisture_content: A 0-1 decimal representing water content of manure.

        Returns:
            Heat capacity of manure, kJ /kg /C.

        """
        return 0.68298 + 0.025662 * avg_tempC + 0.01306 * moisture_content * 100
