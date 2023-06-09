from __future__ import annotations

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.manure.constants.gas_emission_constants import GasEmissionConstants
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

    def _update_methane_emission(self, daily_output: ManureTreatmentDailyOutput) -> None:
        """
        Calculate the methane emission from the anaerobic lagoon.

        Parameters
        ----------
        daily_output : ManureTreatmentDailyOutput
            A ManureTreatmentDailyOutput object containing the daily output of the anaerobic lagoon.

        Returns
        -------
        None
            Update the `storage_methane` attribute of the daily output object.

            Update the `storage_methane` and `liquid_manure_total_volatile_solids` attributes of the accumulated
            output object.

        """
        volatile_solids_factor = 3
        methane_emission = GasEmissions.calc_methane_emission_for_slurry_storage(
            total_volatile_solids=daily_output.liquid_manure_total_volatile_solids,
            temp=self._get_current_day_average_temperature_celsius()
        )
        methane_emission = max(methane_emission, 0.0)
        daily_output.storage_methane = methane_emission
        self._accumulated_output.storage_methane += methane_emission

        new_liquid_manure_total_volatile_solids = (daily_output.liquid_manure_total_volatile_solids -
                                                   methane_emission * volatile_solids_factor)
        self._accumulated_output.liquid_manure_total_volatile_solids += new_liquid_manure_total_volatile_solids

    def _update_ammonia_emission(self, daily_output: ManureTreatmentDailyOutput) -> None:
        """
        Calculate the ammonia emission from the anaerobic lagoon.

        Parameters
        ----------
        daily_output : ManureTreatmentDailyOutput
            A ManureTreatmentDailyOutput object containing the daily output of the anaerobic lagoon.

        Returns
        -------
        None
            Update the `storage_ammonia` attribute of the daily output object.

            Update the `storage_ammonia` attribute of the accumulated output object.

        """
        manure_total_ammoniacal_nitrogen = (
                daily_output.liquid_manure_total_ammoniacal_nitrogen +
                self._current_pen.manure.urine_total_ammoniacal_nitrogen -
                self._manure_handler_daily_output.housing_ammonia
        )
        storage_ammonia_emission = GasEmissions.calc_storage_ammonia_emission(
            num_animals=self._current_pen.num_animals,
            manure_total_ammoniacal_nitrogen=manure_total_ammoniacal_nitrogen,
            manure_volume=daily_output.daily_final_manure_volume,
            total_solids=daily_output.liquid_manure_total_solids,
            storage_area=GasEmissionConstants.DEFAULT_STORAGE_AREA,
            temp=self._get_current_day_average_temperature_celsius(),
            pH=GasEmissionConstants.DEFAULT_PH_FOR_STORAGE_AMMONIA
        )
        daily_output.storage_ammonia = storage_ammonia_emission
        self._accumulated_output.storage_ammonia += storage_ammonia_emission

    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        """
        Update the daily output variables for the anaerobic lagoon.

        Returns
        -------
        ManureTreatmentDailyOutput
            The daily output variables for the anaerobic lagoon.

        """
        daily_output = self._initialize_daily_output_during_update(self._current_manure_treatment_daily_input)
        daily_output.set_daily_final_manure_volume(
            self._adjust_final_manure_volume(daily_output.daily_final_manure_volume)
        )
        daily_output.daily_precipitation_volume = self.precipitation_volume
        daily_output.daily_rainfall = self._get_current_day_rainfall()

        daily_output = self._calc_daily_sludge_output(daily_output, self._current_manure_treatment_daily_input)
        self._accumulated_output = self._adjust_accumulated_output(daily_output)
        self._accumulated_precipitation_volume += self.precipitation_volume

        self._update_methane_emission(daily_output)
        self._update_ammonia_emission(daily_output)

        return daily_output

    def _adjust_final_manure_volume(self, current_day_final_manure_volume: float) -> float:
        """Adjusts the final manure volume to account for the precipitation and the storage time period.

        Args:
            current_day_final_manure_volume: The final manure volume for the current day.

        Returns:
            The adjusted final manure volume.

        """
        return current_day_final_manure_volume + self.precipitation_volume

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
        """
        Adjust the accumulated output by either resetting it or adding the daily output to it.

        The accumulated output will be reset on the first day of every storage time period.

        Parameters
        ----------
        manure_treatment_daily_output : ManureTreatmentDailyOutput
            The daily output from the manure treatment system.

        Returns
        -------
        ManureTreatmentDailyOutput
            The adjusted accumulated output.

        """
        if self._sim_day % self.storage_time_period == 1:
            return manure_treatment_daily_output.clone()
        else:
            new_accumulated_output = self._accumulated_output + manure_treatment_daily_output
            new_accumulated_output.daily_final_manure_volume -= self.flushing_volume
            return new_accumulated_output

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
        discriminant = b ** 2 - 4 * a * c

        if discriminant < 0:
            # raise ValueError("No real solution exists for these parameters.")
            return 0.0
        else:
            return max((-b + discriminant ** 0.5) / (2 * a), (-b - discriminant ** 0.5) / (2 * a))

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
        rainfall = self._get_current_day_rainfall() * GeneralConstants.MM_TO_M
        return rainfall * self.lagoon_surface_area

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
