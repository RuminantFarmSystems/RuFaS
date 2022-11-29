from __future__ import annotations

from typing import Tuple

from RUFAS.routines.manure.gas_emissions.gas_emissions import GasEmissions
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import BaseManureTreatment
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import ManureTreatmentConfig
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import SludgeOutput


class AnaerobicLagoon(BaseManureTreatment):
    def __init__(self, weather, time, manure_treatment_config: ManureTreatmentConfig):
        super().__init__(weather, time, manure_treatment_config)
        self.storage_time_period = self.config.storage_time_period
        self.freeboard_input = self.config.freeboard_input
        self._accumulated_sludge_output = SludgeOutput()
        self._accumulated_minimum_treatment_volume = 0.0
        self._accumulated_precip = 0.0

    def _create_daily_sludge_output(self, manure_treatment_daily_output: ManureTreatmentDailyOutput) -> SludgeOutput:
        """Creates the daily sludge output for the current day.

        Args:
            manure_treatment_daily_output: The daily output for the current day.

        Returns:
            The daily sludge output for the current day.

        """
        return SludgeOutput(
                TS=manure_treatment_daily_output.TS * self.config.TS_removal_efficiency_for_treatment,
                VS=manure_treatment_daily_output.VS_total * self.config.VS_removal_efficiency_for_treatment,
                N=manure_treatment_daily_output.N * self.config.N_removal_efficiency_for_treatment,
                P=manure_treatment_daily_output.P * self.config.P_removal_efficiency_for_treatment,
                K=manure_treatment_daily_output.K * self.config.K_removal_efficiency_for_treatment
        )

    def _accumulate_daily_sludge_output(self, daily_sludge_output: SludgeOutput) -> None:
        """Accumulates the daily sludge output.

        Args:
            daily_sludge_output: The daily sludge output for the current day.

        """
        self._accumulated_sludge_output += daily_sludge_output

    def _assign_extra_output_variables(self, daily_output: ManureTreatmentDailyOutput,
                                       daily_sludge_output: SludgeOutput) -> None:
        """Assigns extra output variables for the anaerobic lagoon.

        Args:
            daily_output: The daily output for the current day.
            daily_sludge_output: The daily sludge output for the current day.

        """
        daily_output.sludge_TS = daily_sludge_output.TS
        daily_output.sludge_VS = daily_sludge_output.VS
        daily_output.sludge_N = daily_sludge_output.N
        daily_output.sludge_P = daily_sludge_output.P
        daily_output.sludge_K = daily_sludge_output.K
        daily_output.accumulated_sludge_TS = self._accumulated_sludge_output.TS
        daily_output.accumulated_minimum_treatment_volume = self._accumulated_minimum_treatment_volume

    def calc_CH4_emission(self, accumulated_VS_total: float, accumulated_TS: float) -> Tuple[float, float]:
        """Calculates CH4 emission from the anaerobic lagoon.

        Args:
            accumulated_VS_total: The accumulated VS total in the lagoon.
            accumulated_TS: The accumulated TS in the lagoon.

        Returns:
            The CH4 emission from the anaerobic lagoon and the new accumulated TS in the lagoon.

        """
        CH4_loss = GasEmissions.calc_E_CH4_anaerobic_lagoon(VS=accumulated_VS_total)
        new_accumulated_TS = max(accumulated_TS - CH4_loss, 0.0)
        return CH4_loss, new_accumulated_TS

    def calc_NH3_emission(self, num_animals: int, barn_area: float,
                          accumulated_pen_urine: float,
                          accumulated_pen_urine_TAN: float) -> Tuple[float, float]:
        """Calculates NH3 emission from the anaerobic lagoon.

        Args:
            num_animals: The number of animals in the pen.
            barn_area: The barn area of the pen.
            accumulated_pen_urine: The accumulated urine in the pen.
            accumulated_pen_urine_TAN: The accumulated TAN in the pen.

        Returns:
            The NH3 emission from the anaerobic lagoon and the new accumulated pen urine TAN in the pen.

        """
        tempC = self._get_current_day_avg_tempC()
        NH3_loss = GasEmissions.calc_E_NH3_emission(
                num_animals=num_animals,
                barn_area=barn_area,
                urine=accumulated_pen_urine,
                urine_TAN=accumulated_pen_urine_TAN,
                tempC=tempC
        )
        new_accumulated_pen_urine_TAN = max(accumulated_pen_urine_TAN - NH3_loss, 0.0)
        return NH3_loss, new_accumulated_pen_urine_TAN

    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        """Updates the daily output variables for the anaerobic lagoon.

        Returns:
            The daily output variables for the anaerobic lagoon.

        """
        daily_output = self._initialize_daily_output_during_update()
        daily_output.final_manure_volume = self._adjust_final_manure_volume(daily_output.final_manure_volume)
        self._accumulate_daily_output(daily_output)
        self._accumulate_minimum_treatment_volume()
        self._accumulate_precip()

        daily_sludge_output = self._create_daily_sludge_output(daily_output)
        self._accumulate_daily_sludge_output(daily_sludge_output)

        CH4_loss, new_accumulated_TS = self.calc_CH4_emission(self._accumulated_output.VS_total,
                                                              self._accumulated_output.TS)
        daily_output.CH4 = CH4_loss
        self._accumulated_output.TS = new_accumulated_TS

        NH3_loss, new_accumulated_pen_urine_TAN = self.calc_NH3_emission(
                num_animals=self._current_pen.num_animals,
                barn_area=self._current_pen.barn_area_from_pen_type,
                accumulated_pen_urine=0.0,
                accumulated_pen_urine_TAN=self._accumulated_output.TAN,
        )
        daily_output.NH3 = NH3_loss
        self._accumulated_output.TAN = new_accumulated_pen_urine_TAN

        # TODO: Remove after development
        self._assign_extra_output_variables(daily_output, daily_sludge_output)
        return daily_output

    def _adjust_final_manure_volume(self, current_day_final_manure_volume: float):
        """Adjust the final manure volume to account for the precipitation and the storage time period.

        Args:
            current_day_final_manure_volume: The final manure volume for the current day.

        Returns:
            The adjusted final manure volume.

        """
        current_day_final_manure_volume += self.precip
        if self._sim_day % self.storage_time_period > 1:
            current_day_final_manure_volume -= self.flushing_volume
        return current_day_final_manure_volume

    @property
    def sludge_accumulation_volume(self) -> float:
        """Returns sludge accumulation volume.

        Returns:
            Sludge accumulation volume, m^3.
        """
        return self._accumulated_sludge_output.TS / 1000.0

    @property
    def flushing_volume(self) -> float:
        """Returns flushing water recycled.

        Returns:
            Flushing water volume, m^3

        """
        return self._manure_handler_daily_output.cleaning_water_volume

    @property
    def wastewater_volume(self) -> float:
        """Calculates the volume of wastewater in the treatment system.

        Returns:
            The volume of wastewater in the treatment system, m^3.

        """
        if self._current_input_data:
            return self._get_input_manure_volume(self._current_input_data)
        return 0.0

    @property
    def reduced_volume(self) -> float:
        """Returns reduced volume.

        Returns:
            The reduced volume, m^3.

        """
        return self.wastewater_volume - self.flushing_volume  # m^3

    def _accumulate_minimum_treatment_volume(self) -> None:
        """Returns minimum treatment volume.

        Returns:
            Minimum treatment volume, m^3.

        """
        if self._sim_day % self.storage_time_period == 1:
            self._accumulated_minimum_treatment_volume = self._get_input_manure_volume(self._current_input_data)
        else:
            self._accumulated_minimum_treatment_volume += self.reduced_volume

    @property
    def total_lagoon_volume(self) -> float:
        """Returns total lagoon volume.

        Returns:
            Total lagoon volume, m^3.

        """
        return self.volume_needed + self.freeboard + self._accumulated_precip

    @property
    def volume_needed(self):
        """Returns volume needed.

        Returns:
            Volume needed, m^3.

        """
        return self._accumulated_minimum_treatment_volume + self.sludge_accumulation_volume

    @property
    def lagoon_depth(self):
        """Returns lagoon depth.

        Returns:
            Lagoon depth, m.

        """
        return 3.657

    @property
    def lagoon_slope(self):
        """Returns lagoon slope.

        Returns:
            Lagoon slope.

        """
        return 2.0

    def calc_abc(self):
        """Calculates the a, b, and c parameters for the lagoon sizing equation.

        Returns:
            a, b, and c parameters for the lagoon sizing equation.

        """
        a = 3 * self.lagoon_depth
        b = -4 * self.lagoon_slope * self.lagoon_depth ** 2
        c = 4 * (self.lagoon_slope ** 2) * (self.lagoon_depth ** 3) / 3 - self.volume_needed
        return a, b, c

    @property
    def lagoon_width(self):
        """returns lagoon width in meters"""
        abc = self.calc_abc()
        a, b, c = abc[0], abc[1], abc[2]
        return (-1 * b + (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)

    @property
    def lagoon_length(self):
        """Returns lagoon width.

        Returns:
            Lagoon length, m.

        """
        return self.lagoon_width * 3

    @property
    def lagoon_surface_area(self):
        """Returns lagoon surface area.

         Returns:
                Lagoon surface area, m^2.

        """
        return self.lagoon_width * self.lagoon_length

    @property
    def _calc_modeled_lagoon_volume(self) -> float:
        """Returns modeled lagoon volume.

        This modeled volume is used to verify that equations for surface area,
        with slope assumptions, match the volume needed for treatment

        Returns:
            Modeled lagoon volume, m^3.

        """
        return (self.lagoon_length * self.lagoon_width * self.lagoon_depth
                - (self.lagoon_slope * self.lagoon_depth ** 2) * (self.lagoon_length + self.lagoon_width)
                + 4 * self.lagoon_slope * self.lagoon_depth ** 3 / 3)

    @property
    def precip(self):
        """Returns additional lagoon volume needed for precipitation.

        Returns:
            Additional lagoon volume needed for precipitation, m^3.

        """
        return self._get_current_day_rainfall() * self.lagoon_surface_area

    def _accumulate_precip(self) -> None:
        """Accumulates daily precipitation."""
        self._accumulated_precip += self.precip

    @property
    def freeboard(self) -> float:
        """Returns additional lagoon volume needed for freeboard.

        Returns:
            Additional lagoon volume needed for freeboard, m^3.

        """
        return self.freeboard_input * self.lagoon_surface_area

    def _bound_sludge_accumulation_volume(self, calculated_SAV_value: float, lower_bound: float,
                                          upper_bound: float) -> float:
        """Returns a value bounded by the lower and upper bounds.

        Args:
            calculated_SAV_value: The value to be bounded.
            lower_bound: The lower bound.
            upper_bound: The upper bound.

        Returns:
            The bounded value of sludge accumulation volume.

        """
        return min(max(self.sludge_accumulation_volume * lower_bound, calculated_SAV_value),
                   self.sludge_accumulation_volume * upper_bound)

