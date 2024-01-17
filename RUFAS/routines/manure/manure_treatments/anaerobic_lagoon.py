from __future__ import annotations

import math

from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants
from RUFAS.routines.manure.gas_emissions.calculator import (
    GasEmissionsCalculator,
)
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import (
    BaseManureTreatment,
)
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import (
    ManureTreatmentConfig,
)
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import (
    ManureTreatmentDailyOutput,
)


class AnaerobicLagoon(BaseManureTreatment):
    LAGOON_DEPTH = 3.657
    """The depth of the lagoon (m). Default is set to 3.657 m (12 ft)."""
    LAGOON_SLOPE = 2.0
    """The slope of the lagoon (unitless). Default is set to 2.0."""

    def __init__(self, weather, time, manure_treatment_config: ManureTreatmentConfig):
        super().__init__(weather, time, manure_treatment_config)
        self.storage_time_period = self.config.storage_time_period
        self.freeboard_input = self.config.freeboard_input
        self._accumulated_precipitation_volume = 0.0

    def _update_methane_emission(
        self, daily_output: ManureTreatmentDailyOutput
    ) -> None:
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
        methane_emission = GasEmissionsCalculator.methane_emission_from_slurry_storage(
            total_volatile_solids=daily_output.liquid_manure_total_volatile_solids,
            temp=self._get_current_day_average_temperature_celsius(),
        )
        methane_emission = max(methane_emission, 0.0)
        daily_output.storage_methane = methane_emission
        self._accumulated_output.storage_methane += methane_emission

        new_liquid_manure_total_volatile_solids = (
            daily_output.liquid_manure_total_volatile_solids
            - methane_emission * volatile_solids_factor
        )
        new_liquid_manure_total_volatile_solids = max(
            new_liquid_manure_total_volatile_solids, 0.0
        )
        self._accumulated_output.liquid_manure_total_volatile_solids += (
            new_liquid_manure_total_volatile_solids
        )

    def _update_ammonia_emission(
        self, daily_output: ManureTreatmentDailyOutput
    ) -> None:
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
        manure_total_ammoniacal_nitrogen = max(
            daily_output.liquid_manure_total_ammoniacal_nitrogen
            + self._current_pen.manure.urine_total_ammoniacal_nitrogen
            - self._manure_handler_daily_output.housing_ammonia,
            0.0,
        )
        storage_ammonia_emission = GasEmissionsCalculator.storage_ammonia_emission(
            num_animals=self._current_pen.num_animals,
            manure_total_ammoniacal_nitrogen=manure_total_ammoniacal_nitrogen,
            manure_volume=daily_output.daily_final_manure_volume,
            manure_density=ManureConstants.LIQUID_MANURE_DENSITY,
            total_solids=daily_output.liquid_manure_total_solids,
            temp=self._get_current_day_average_temperature_celsius(),
        )
        daily_output.storage_ammonia = storage_ammonia_emission
        self._accumulated_output.storage_ammonia += storage_ammonia_emission

    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        """
        Update the daily output variables for the anaerobic lagoon.

        Returns
        -------
            The daily output variables for the anaerobic lagoon.

        """
        daily_input = self._current_manure_treatment_daily_input
        daily_output = self._initialize_daily_output_during_update(daily_input)

        adjusted_daily_final_manure_volume = self._adjust_final_manure_volume(
            daily_output.daily_final_manure_volume
        )
        daily_output.set_daily_final_manure_volume(adjusted_daily_final_manure_volume)

        self._accumulated_output = self._adjust_accumulated_output(daily_output)
        self._accumulated_precipitation_volume += self.precipitation_volume

        self._update_methane_emission(daily_output)
        self._update_ammonia_emission(daily_output)

        return daily_output

    def _adjust_final_manure_volume(
        self, current_day_final_manure_volume: float
    ) -> float:
        """
        Adjust the final manure volume to account for the precipitation and the storage time period.

        Parameters
        ----------
        current_day_final_manure_volume : float
            The final manure volume for the current simulation day (:math:`m^3`).

        Returns
        -------
        float
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

    def _adjust_accumulated_output(
        self, manure_treatment_daily_output: ManureTreatmentDailyOutput
    ) -> ManureTreatmentDailyOutput:
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
            new_accumulated_output = (
                self._accumulated_output + manure_treatment_daily_output
            )
            new_accumulated_output.daily_final_manure_volume -= self.flushing_volume
            return new_accumulated_output

    @property
    def volume_needed(self):
        """Returns volume needed.

        Returns:
            Volume needed, m^3.

        """
        return (
            self._accumulated_output.daily_final_manure_volume
            + self.sludge_accumulation_volume
        )

    @property
    def lagoon_depth(self) -> float:
        """
        Get the lagoon depth.

        This property provides access to the depth of the lagoon.

        Returns
        -------
        float
            Lagoon depth in meters (m).

        """
        return self.LAGOON_DEPTH

    @property
    def lagoon_slope(self) -> float:
        """
        Get the lagoon slope.

        This property provides access to the slope of the lagoon.

        Returns
        -------
        float
            Lagoon slope (unitless).

        """
        return self.LAGOON_SLOPE

    def _calc_lagoon_width_coefficients(self) -> tuple[float, float, float]:
        """
        Calculate the coefficients a, b, and c for the quadratic equation used to calculate lagoon width.

        This method computes the coefficients based on the lagoon's depth and slope, which are then used
        to solve a quadratic equation for determining the width of the lagoon.

        Returns
        -------
        tuple[float, float, float]
            The coefficients a, b, and c for the quadratic equation:
            - a: Coefficient for the squared term, computed as 3 times the lagoon depth.
            - b: Coefficient for the linear term, computed as -4 times the lagoon slope times the square
                 of the lagoon depth.
            - c: Constant term, computed based on the lagoon slope, lagoon depth, and volume needed.

        Raises
        ------
        ValueError
            If the coefficient for the squared term (a) is 0, as this would lead to a division by zero
            in subsequent calculations.

        """
        a = 3 * self.lagoon_depth
        if math.isclose(a, 0.0, abs_tol=1e-9):
            raise ValueError("Coefficient for the squared term (a) cannot be 0.")
        b = -4 * self.lagoon_slope * self.lagoon_depth**2
        c = (
            4 * (self.lagoon_slope**2) * (self.lagoon_depth**3) / 3
            - self.volume_needed
        )
        return a, b, c

    @property
    def lagoon_width(self) -> float:
        """
        Calculate and return the lagoon width in meters.

        The width of the lagoon is computed by solving a quadratic equation derived from the lagoon's depth
        and slope. The coefficients for this equation are computed in the _calc_lagoon_width_coefficients method.

        If the quadratic equation does not have real roots (discriminant < 0), the width is considered to be 0.0.
        If both roots of the quadratic equation are negative, the width is also considered to be 0.0 as negative
        width is not physically meaningful.

        Returns
        -------
        float
            Lagoon width in meters (m). If the quadratic equation has no real solutions or both roots are negative,
            returns 0.0.

        """
        a, b, c = self._calc_lagoon_width_coefficients()
        discriminant = b**2 - 4 * a * c

        if discriminant < 0:
            return 0.0

        root1 = (-b + discriminant**0.5) / (2 * a)
        root2 = (-b - discriminant**0.5) / (2 * a)

        if root1 < 0 and root2 < 0:
            return 0.0

        return max(root1, root2)

    @property
    def lagoon_length(self) -> float:
        """
        Calculate and return the length of the lagoon in meters (m).

        The length of the lagoon is calculated as three times the width of the lagoon.

        Returns
        -------
        float
            Lagoon length in meters (m).

        """
        return self.lagoon_width * 3

    @property
    def lagoon_surface_area(self) -> float:
        """
        Calculate and return the surface area of the lagoon in square meters (m^2).

        The surface area is calculated as the product of the lagoon's width and length.

        Returns
        -------
        float
            Lagoon surface area in square meters (:math:`m^2`).

        """
        return self.lagoon_width * self.lagoon_length

    def _calc_modeled_lagoon_volume(self) -> float:
        """
        Return modeled lagoon volume in cubic meters (:math:`m^3`).

        The modeled volume is used to verify that equations for surface area,
        with slope assumptions, match the volume needed for treatment.

        The formula is composed of three parts:
        - Base volume (length * width * depth)
        - Slope correction for the sides ((slope * (depth ** 2)) * (length + width))
        - Slope correction for the corners (4 * slope * (depth ** 3) / 3)

        Returns
        -------
        float
            Modeled lagoon volume in cubic meters (:math:`m^3`).

        """
        base_volume = self.lagoon_length * self.lagoon_width * self.lagoon_depth
        slope_correction_sides = (self.lagoon_slope * (self.lagoon_depth**2)) * (
            self.lagoon_length + self.lagoon_width
        )
        slope_correction_corners = 4 * self.lagoon_slope * (self.lagoon_depth**3) / 3

        return base_volume - slope_correction_sides + slope_correction_corners

    @property
    def precipitation_volume(self) -> float:
        """
        Return additional lagoon volume needed for precipitation.

        The additional volume needed for precipitation is calculated as the product of
        the current day's rainfall and the lagoon's surface area.

        Returns
        -------
        float
            Additional lagoon volume needed for precipitation (:math:`m^3`).

        """
        return self._get_current_day_rainfall() * self.lagoon_surface_area

    @property
    def freeboard_volume(self) -> float:
        """
        Calculate additional lagoon volume needed for freeboard.

        Returns
        -------
        float
            Additional lagoon volume needed for freeboard (:math:`m^3`).

        """
        return self.freeboard_input * self.lagoon_surface_area

    def _bound_sludge_accumulation_volume(
        self,
        calculated_sludge_accumulation_volume: float,
        lower_bound: float,
        upper_bound: float,
    ) -> float:
        """
        Calculate a value for sludge accumulation volume bounded by the specified lower and upper bounds.

        This method constrains the calculated sludge accumulation volume such that it does not exceed the specified
        limits, given as a proportion of the current sludge accumulation volume.

        Parameters
        ----------
        calculated_sludge_accumulation_volume : float
            The value to be bounded, derived from a prior calculation.
        lower_bound : float
            The lower bound, given as a proportion of the current sludge accumulation volume.
            Must be nonnegative, and less than or equal to the upper bound.
        upper_bound : float
            The upper bound, given as a proportion of the current sludge accumulation volume.
            Must be nonnegative, and greater than or equal to the lower bound.

        Returns
        -------
        float
            The bounded value of sludge accumulation volume, ranging between the specified
            lower and upper bounds.

        Raises
        ------
        ValueError
            If the calculated_sludge_accumulation_volume is negative, or if the lower_bound is negative,
            or if the upper_bound is less than the lower_bound.

        """
        if calculated_sludge_accumulation_volume < 0:
            raise ValueError(
                "The calculated sludge accumulation volume must be nonnegative."
            )
        if lower_bound < 0:
            raise ValueError("The lower bound must be nonnegative.")
        if upper_bound < lower_bound:
            raise ValueError(
                "The upper bound must be greater than or equal to the lower bound."
            )

        return min(
            max(
                self.sludge_accumulation_volume * lower_bound,
                calculated_sludge_accumulation_volume,
            ),
            self.sludge_accumulation_volume * upper_bound,
        )
