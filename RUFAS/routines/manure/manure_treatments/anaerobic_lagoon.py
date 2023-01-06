from __future__ import annotations

from typing import Tuple

from RUFAS.routines.manure.constants.manure_constants import ManureConstants
from RUFAS.routines.manure.gas_emissions.gas_emissions import GasEmissions
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import BaseManureTreatment
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import ManureTreatmentConfig
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import SludgeOutput
from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import LiquidManurePortionProtocol


class AnaerobicLagoon(BaseManureTreatment):
    def __init__(self, weather, time, manure_treatment_config: ManureTreatmentConfig):
        super().__init__(weather, time, manure_treatment_config)
        self.storage_time_period = self.config.storage_time_period
        self.freeboard_input = self.config.freeboard_input
        self._accumulated_sludge_output = SludgeOutput()
        self._accumulated_precip = 0.0

    def _create_daily_sludge_output(self, manure_treatment_daily_input: LiquidManurePortionProtocol) -> SludgeOutput:
        """Creates the daily sludge output for the current day.

        Args:
            manure_treatment_daily_input: The daily output for the current day.

        Returns:
            The daily sludge output for the current day.

        """
        return SludgeOutput(
                sludge_manure_total_solids=manure_treatment_daily_input.liquid_manure_total_solids *
                                           self.config.total_solids_removal_efficiency_for_treatment,
                sludge_manure_total_volatile_solids=manure_treatment_daily_input.liquid_manure_total_volatile_solids
                                                    * self.config.volatile_solids_removal_efficiency_for_treatment,
                sludge_manure_nitrogen=manure_treatment_daily_input.liquid_manure_nitrogen *
                                       self.config.nitrogen_removal_efficiency_for_treatment,
                sludge_manure_phosphorus=manure_treatment_daily_input.liquid_manure_phosphorus *
                                         self.config.phosphorus_removal_efficiency_for_treatment,
                sludge_manure_potassium=manure_treatment_daily_input.liquid_manure_potassium *
                                        self.config.potassium_removal_efficiency_for_treatment,
                sludge_manure_daily_volume=manure_treatment_daily_input.liquid_manure_total_volatile_solids * 0.03 /
                                           1000.0
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
        daily_output.sludge_manure_total_solids = daily_sludge_output.sludge_manure_total_solids
        daily_output.sludge_manure_total_volatile_solids = daily_sludge_output.sludge_manure_total_volatile_solids
        daily_output.sludge_manure_nitrogen = daily_sludge_output.sludge_manure_nitrogen
        daily_output.sludge_manure_phosphorus = daily_sludge_output.sludge_manure_phosphorus
        daily_output.sludge_manure_potassium = daily_sludge_output.sludge_manure_potassium
        daily_output.sludge_manure_daily_volume = daily_sludge_output.sludge_manure_daily_volume
        daily_output.accumulated_sludge_volume = self._accumulated_sludge_output.sludge_manure_daily_volume
        daily_output.accumulated_final_manure_volume = self._accumulated_output.final_manure_volume

    def calc_methane_emission(self, accumulated_VS_total: float, accumulated_TS: float) -> Tuple[float, float]:
        """Calculates CH4 emission from the anaerobic lagoon.

        Args:
            accumulated_VS_total: The accumulated VS total in the lagoon.
            accumulated_TS: The accumulated TS in the lagoon.

        Returns:
            CH4 loss: The CH4 loss from the lagoon, kg.
            new_accumulated_TS: The new accumulated TS in the lagoon, kg.

        """
        CH4_loss = GasEmissions.calc_methane_emission_for_anaerobic_lagoon(manure_volatile_solids=accumulated_VS_total)
        new_accumulated_TS = max(accumulated_TS - CH4_loss, 0.0)
        return CH4_loss, new_accumulated_TS

    def calc_ammonia_emission(self, num_animals: int, barn_area: float,
                              accumulated_manure_volume: float,
                              accumulated_TAN: float) -> Tuple[float, float]:
        """Calculates NH3 emission from the anaerobic lagoon.

        Args:
            num_animals: The number of animals in the barn.
            barn_area: The barn area per animal, m^2/animal.
            accumulated_manure_volume: The accumulated manure volume in the lagoon, m^3.
            accumulated_TAN: The accumulated TAN in the lagoon, kg.

        Returns:
            NH3 loss: The NH3 loss from the lagoon, kg.
            new_accumulated_TAN: The new accumulated TAN in the lagoon, kg.

        """
        avg_tempC = self._get_current_day_average_temperature_celsius()
        NH3_loss = GasEmissions.calc_ammonia_emission(
                num_animals=num_animals,
                barn_area=barn_area,
                manure_urine=accumulated_manure_volume * ManureConstants.MANURE_DENSITY / num_animals,
                manure_urine_total_ammoniacal_nitrogen=accumulated_TAN / num_animals,
                temperature_celsius=avg_tempC
        )
        new_accumulated_TAN = max(accumulated_TAN - NH3_loss, 0.0)
        return NH3_loss, new_accumulated_TAN

    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        """Updates the daily output variables for the anaerobic lagoon.

        Returns:
            The daily output variables for the anaerobic lagoon.

        """
        daily_output = self._initialize_daily_output_during_update(self._current_manure_treatment_daily_input)
        daily_output.final_manure_volume = self._adjust_final_manure_volume(daily_output.final_manure_volume)
        daily_output.daily_volume = daily_output.final_manure_volume

        self._accumulated_output = self._adjust_accumulated_output(daily_output)
        daily_output.accumulated_final_manure_volume = self._accumulated_output.final_manure_volume
        self._accumulate_precip()

        daily_sludge_output = self._create_daily_sludge_output(self._current_manure_treatment_daily_input)
        self._accumulate_daily_sludge_output(daily_sludge_output)

        CH4_loss, new_accumulated_TS = self.calc_methane_emission(
                self._accumulated_output.liquid_manure_total_volatile_solids,
                self._accumulated_output.liquid_manure_total_solids)
        daily_output.storage_methane = CH4_loss
        self._accumulated_output.TS = new_accumulated_TS

        NH3_loss, new_accumulated_TAN = self.calc_ammonia_emission(
                num_animals=self._current_pen.num_animals,
                barn_area=self._current_pen.barn_area_from_pen_type,
                accumulated_manure_volume=self._accumulated_output.final_manure_volume,
                accumulated_TAN=self._accumulated_output.liquid_manure_total_ammoniacal_nitrogen
        )
        daily_output.storage_ammonia = NH3_loss
        self._accumulated_output.TAN = new_accumulated_TAN

        self._assign_extra_output_variables(daily_output, daily_sludge_output)
        return daily_output

    def _adjust_final_manure_volume(self, current_day_final_manure_volume: float):
        """Adjusts the final manure volume to account for the precipitation and the storage time period.

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
        return self._accumulated_sludge_output.sludge_manure_daily_volume

    @property
    def flushing_volume(self) -> float:
        """Returns flushing water recycled.

        Returns:
            Flushing water volume, m^3

        """
        return self._manure_handler_daily_output.cleaning_water_volume

    def _adjust_accumulated_output(self,
                                   manure_treatment_daily_output: ManureTreatmentDailyOutput) -> \
            ManureTreatmentDailyOutput:
        if self._sim_day % self.storage_time_period == 1:
            return manure_treatment_daily_output
        else:
            return self._accumulated_output + manure_treatment_daily_output

    @property
    def volume_needed(self):
        """Returns volume needed.

        Returns:
            Volume needed, m^3.

        """
        return self._accumulated_output.final_manure_volume + self.sludge_accumulation_volume

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
