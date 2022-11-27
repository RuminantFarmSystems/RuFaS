from __future__ import annotations

from typing import List

from RUFAS.routines.manure.constants.general_constants import GeneralConstants
from RUFAS.routines.manure.gas_emissions.gas_emissions import GasEmissions
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import BaseManureTreatment
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import ManureTreatmentConfig
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import AnaerobicDigestionOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import SludgeOutput


class AnaerobicDigestion(BaseManureTreatment):
    def __init__(self, weather, time, manure_treatment_config: ManureTreatmentConfig) -> None:
        super().__init__(weather, time, manure_treatment_config)
        self._accumulated_sludge_output = SludgeOutput()
        self.all_ad_output: List[AnaerobicDigestionOutput] = []

    def _create_daily_sludge_output(self, manure_treatment_daily_output: ManureTreatmentDailyOutput) -> SludgeOutput:
        """Returns the daily sludge output from anaerobic digestion.

        Args:
            manure_treatment_daily_output: The daily output from the manure treatment.

        Returns:
            The daily sludge output from anaerobic digestion.

        """
        return SludgeOutput(
                TS=manure_treatment_daily_output.TS * self.config.TS_removal_efficiency_for_treatment,
                VS=manure_treatment_daily_output.VS_total * self.config.VS_removal_efficiency_for_treatment,
                N=manure_treatment_daily_output.N * self.config.N_removal_efficiency_for_treatment,
                P=manure_treatment_daily_output.P * self.config.P_removal_efficiency_for_treatment,
                K=manure_treatment_daily_output.K * self.config.K_removal_efficiency_for_treatment
        )

    def _accumulate_daily_sludge_output(self, daily_sludge_output: SludgeOutput) -> None:
        """Accumulates the daily sludge output from anaerobic digestion."""
        self._accumulated_sludge_output += daily_sludge_output

    def _assign_extra_output_variables(self, daily_output: ManureTreatmentDailyOutput,
                                       daily_sludge_output: SludgeOutput) -> None:
        """Assigns extra output variables for debugging purposes.

        Args:
            daily_output: The daily output from the manure treatment.
            daily_sludge_output: The daily sludge output from anaerobic digestion.

        """
        daily_output.sludge_TS = daily_sludge_output.TS
        daily_output.sludge_VS = daily_sludge_output.VS
        daily_output.sludge_N = daily_sludge_output.N
        daily_output.sludge_P = daily_sludge_output.P
        daily_output.sludge_K = daily_sludge_output.K
        daily_output.accumulated_sludge_TS = self._accumulated_sludge_output.TS

    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        """Updates the anaerobic digestion model for a single day."""

        daily_output = self._initialize_daily_output_during_update()
        self._accumulate_daily_output(daily_output)

        daily_sludge_output = self._create_daily_sludge_output(daily_output)
        self._accumulate_daily_sludge_output(daily_sludge_output)

        anaerobic_digestion_daily_output = self._create_anaerobic_digestion_daily_output(
                daily_output.final_manure_volume)
        self.all_ad_output.append(anaerobic_digestion_daily_output)

        # TODO: Remove after development
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
                TS=self._manure_handler_daily_output.TS
        )
        avg_tempC = self._get_current_day_avg_tempC()
        input_energy_heating = (self._calc_specific_input_energy(avg_tempC, moisture_content) *
                                final_manure_volume *
                                GeneralConstants.LITERS_TO_CUBIC_METERS)
        # MS.3.B.7
        methane_generation_volume = GasEmissions.calc_CH4_volume_using_Chen_equation(
                VS_total=self._manure_handler_daily_output.VS_total,
                hydraulic_retention_time=self.config.hydraulic_retention_time
        )
        biogas_energy_content = GasEmissions.calc_biogas_energy_content(CH4_volume=methane_generation_volume)
        # MS.3.B.2
        minimum_digester_volume = final_manure_volume * self.config.hydraulic_retention_time
        # MS.3.B.3
        top_cover_volume = minimum_digester_volume * self.config.top_cover_volume_fraction

        anaerobic_digestion_daily_output = AnaerobicDigestionOutput(
                biogas=self.config.biogas_gen_ratio * self._manure_handler_daily_output.VS_total,
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
        return self._accumulated_sludge_output.VS * GeneralConstants.KG_TO_CUBIC_METERS

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
        heat_capacity_AD = self._calc_heat_capacity_manure(self.config.AD_temp_set_point, moisture_content)
        avg_heat_capacity = (heat_capacity_influent + heat_capacity_AD) / 2
        input_energy_heating = avg_heat_capacity * (self.config.AD_temp_set_point - effluent_temperature)
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
