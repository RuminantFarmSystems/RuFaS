from __future__ import annotations

from typing import Tuple

from RUFAS.routines.manure.constants.manure_constants import ManureConstants
from RUFAS.routines.manure.gas_emissions.gas_emissions import GasEmissions
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import BaseManureTreatment
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import ManureTreatmentConfig
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput
from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import LiquidManurePortionProtocol


class AnaerobicLagoon(BaseManureTreatment):
    def __init__(self, weather, time, manure_treatment_config: ManureTreatmentConfig):
        super().__init__(weather, time, manure_treatment_config)
        self.storage_time_period = self.config.storage_time_period
        self.freeboard_input = self.config.freeboard_input
        self._accumulated_precipitation_volume = 0.0

    def _calc_daily_sludge_output(self, daily_output: ManureTreatmentDailyOutput,
                                  manure_treatment_daily_input: LiquidManurePortionProtocol) \
            -> ManureTreatmentDailyOutput:
        """Calculates the daily sludge output for the current day.

        """
        new_daily_output = daily_output.clone()
        new_daily_output.sludge_manure_total_solids = (manure_treatment_daily_input.liquid_manure_total_solids *
                                                       self.config.total_solids_removal_efficiency_for_treatment)
        new_daily_output.sludge_manure_total_volatile_solids = (
                manure_treatment_daily_input.liquid_manure_total_volatile_solids *
                self.config.volatile_solids_removal_efficiency_for_treatment)
        new_daily_output.sludge_manure_nitrogen = (manure_treatment_daily_input.liquid_manure_nitrogen *
                                                   self.config.nitrogen_removal_efficiency_for_treatment)
        new_daily_output.sludge_manure_phosphorus = (manure_treatment_daily_input.liquid_manure_phosphorus *
                                                     self.config.phosphorus_removal_efficiency_for_treatment)
        new_daily_output.sludge_manure_potassium = (manure_treatment_daily_input.liquid_manure_potassium *
                                                    self.config.potassium_removal_efficiency_for_treatment)
        new_daily_output.sludge_manure_daily_volume = (
                manure_treatment_daily_input.liquid_manure_total_volatile_solids *
                0.03 / ManureConstants.MANURE_DENSITY)  # TODO: Use constants instead
        return new_daily_output

    def calc_methane_emission(self,
                              accumulated_liquid_manure_total_volatile_solids: float,
                              accumulated_liquid_manure_total_solids: float) \
            -> Tuple[float, float]:
        """Calculates methane emission from the anaerobic lagoon.

        Args:
            accumulated_liquid_manure_total_volatile_solids: The accumulated total volatile solids in the lagoon, kg.
            accumulated_liquid_manure_total_solids: The accumulated total solids in the lagoon, kg.

        Returns:
            methane loss: The methane loss from the lagoon, kg.
            new_accumulated_liquid_manure_total_solids: The new accumulated total solids in the lagoon, kg.

        """
        methane_loss = GasEmissions.calc_methane_emission_for_anaerobic_lagoon(
                manure_volatile_solids=accumulated_liquid_manure_total_volatile_solids)
        new_accumulated_liquid_manure_total_solids = max(accumulated_liquid_manure_total_solids - methane_loss, 0.0)
        return methane_loss, new_accumulated_liquid_manure_total_solids

    def calc_ammonia_emission(self, num_animals: int, barn_area: float,
                              accumulated_manure_volume: float,
                              accumulated_manure_total_ammoniacal_nitrogen: float) -> Tuple[float, float]:
        """Calculates NH3 emission from the anaerobic lagoon.

        Args:
            num_animals: The number of animals in the barn.
            barn_area: The barn area per animal, m^2/animal.
            accumulated_manure_volume: The accumulated manure volume in the lagoon, m^3.
            accumulated_manure_total_ammoniacal_nitrogen: The accumulated total ammoniacal nitrogen
             in the lagoon, kg.

        Returns:
            ammonia loss: The ammonia loss from the lagoon, kg.
            new_accumulated_liquid_manure_total_ammoniacal_nitrogen: Accumulated total ammoniacal nitrogen
            in the treatment system after the ammonia emission is calculated, kg.


        """
        ammonia_loss = GasEmissions.calc_ammonia_emission(
                num_animals=num_animals,
                barn_area=barn_area,
                mass=accumulated_manure_volume * ManureConstants.MANURE_DENSITY / num_animals,
                total_ammoniacal_nitrogen=accumulated_manure_total_ammoniacal_nitrogen / num_animals,
                temperature_celsius=self._get_current_day_average_temperature_celsius()
        )
        new_accumulated_liquid_manure_total_ammoniacal_nitrogen = \
            max(accumulated_manure_total_ammoniacal_nitrogen - ammonia_loss, 0.0)
        return ammonia_loss, new_accumulated_liquid_manure_total_ammoniacal_nitrogen

    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        """Updates the daily output variables for the anaerobic lagoon.

        Returns:
            The daily output variables for the anaerobic lagoon.

        """
        daily_output = self._initialize_daily_output_during_update(self._current_manure_treatment_daily_input)
        adjusted_daily_final_manure_volume = self._adjust_final_manure_volume(daily_output.daily_final_manure_volume)
        daily_output.set_daily_final_manure_volume(adjusted_daily_final_manure_volume)

        daily_output = self._calc_daily_sludge_output(daily_output, self._current_manure_treatment_daily_input)
        self._accumulated_output = self._adjust_accumulated_output(daily_output)
        self._accumulated_precipitation_volume += self.precipitation_volume

        methane_loss, new_accumulated_liquid_manure_total_solids = self.calc_methane_emission(
                self._accumulated_output.liquid_manure_total_volatile_solids,
                self._accumulated_output.liquid_manure_total_solids)
        daily_output.storage_methane = methane_loss
        self._accumulated_output.liquid_manure_total_solids = new_accumulated_liquid_manure_total_solids

        ammonia_loss, new_accumulated_liquid_manure_total_ammoniacal_nitrogen = \
            self.calc_ammonia_emission(
                    num_animals=self._current_pen.num_animals,
                    barn_area=self._current_pen.barn_area_from_pen_type,
                    accumulated_manure_volume=self._accumulated_output.daily_final_manure_volume,
                    accumulated_manure_total_ammoniacal_nitrogen=(
                        self._accumulated_output.liquid_manure_total_ammoniacal_nitrogen)
            )
        daily_output.storage_ammonia = ammonia_loss
        self._accumulated_output.liquid_manure_total_ammoniacal_nitrogen = \
            new_accumulated_liquid_manure_total_ammoniacal_nitrogen

        return daily_output

    def _adjust_final_manure_volume(self, current_day_final_manure_volume: float) -> float:
        """Adjusts the final manure volume to account for the precipitation and the storage time period.

        Args:
            current_day_final_manure_volume: The final manure volume for the current day.

        Returns:
            The adjusted final manure volume.

        """
        adjusted_final_manure_volume = current_day_final_manure_volume + self.precipitation_volume
        if self._sim_day % self.storage_time_period > 1:
            adjusted_final_manure_volume -= self.flushing_volume
        return adjusted_final_manure_volume

    @property
    def sludge_accumulation_volume(self) -> float:
        """Returns sludge accumulation volume.

        Returns:
            Sludge accumulation volume, m^3.
        """
        return self._accumulated_output.sludge_manure_daily_volume

    @property
    def flushing_volume(self) -> float:
        """Returns flushing water recycled.

        Returns:
            Flushing water volume, m^3

        """
        return self._manure_handler_daily_output.cleaning_water_volume

    def _adjust_accumulated_output(self, manure_treatment_daily_output: ManureTreatmentDailyOutput) \
            -> ManureTreatmentDailyOutput:
        """Adjusts the accumulated output by either resetting it or adding the daily output to it.

        The accumulated output will be reset on the first day of every storage time period.

        Args:
            manure_treatment_daily_output: The daily output from the manure treatment system.

        Returns:
            The adjusted accumulated output.

        """
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
        return self._accumulated_output.daily_final_manure_volume + self.sludge_accumulation_volume

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

    def _calc_abc(self):
        """Calculates the a, b, and c parameters for the lagoon sizing equation.

        Returns:
            a, b, and c parameters for the lagoon sizing equation.

        """
        a = 3 * self.lagoon_depth
        b = -4 * self.lagoon_slope * self.lagoon_depth ** 2
        c = 4 * (self.lagoon_slope ** 2) * (self.lagoon_depth ** 3) / 3 - self.volume_needed
        return a, b, c

    @property
    def lagoon_width(self) -> float:
        """Returns lagoon width.

        Returns:
            Lagoon width, m.

        """
        abc = self._calc_abc()
        a, b, c = abc[0], abc[1], abc[2]
        return (-1 * b + (b ** 2 - 4 * a * c) ** 0.5) / (2 * a)

    @property
    def lagoon_length(self):
        """Returns lagoon length.

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
        with slope assumptions, match the volume needed for treatment.

        Returns:
            Modeled lagoon volume, m^3.

        """
        return (self.lagoon_length * self.lagoon_width * self.lagoon_depth
                - (self.lagoon_slope * self.lagoon_depth ** 2) * (self.lagoon_length + self.lagoon_width)
                + 4 * self.lagoon_slope * self.lagoon_depth ** 3 / 3)

    @property
    def precipitation_volume(self):
        """Returns additional lagoon volume needed for precipitation.

        Returns:
            Additional lagoon volume needed for precipitation, m^3.

        """
        return self._get_current_day_rainfall() * self.lagoon_surface_area

    @property
    def freeboard_volume(self) -> float:
        """Returns additional lagoon volume needed for freeboard.

        Returns:
            Additional lagoon volume needed for freeboard, m^3.

        """
        return self.freeboard_input * self.lagoon_surface_area

    def _bound_sludge_accumulation_volume(self,
                                          calculated_sludge_accumulation_volume: float,
                                          lower_bound: float,
                                          upper_bound: float) -> float:
        """Returns a value bounded by the lower and upper bounds.

        Args:
            calculated_sludge_accumulation_volume: The value to be bounded.
            lower_bound: The lower bound.
            upper_bound: The upper bound.

        Returns:
            The bounded value of sludge accumulation volume.

        """
        return min(max(self.sludge_accumulation_volume * lower_bound, calculated_sludge_accumulation_volume),
                   self.sludge_accumulation_volume * upper_bound)
