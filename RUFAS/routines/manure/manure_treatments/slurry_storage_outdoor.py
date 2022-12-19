from __future__ import annotations

from typing import Tuple

import math

from RUFAS.routines.manure.constants.manure_constants import ManureConstants
from RUFAS.routines.manure.gas_emissions.gas_emissions import GasEmissions
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import BaseManureTreatment
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import ManureTreatmentConfig
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput


class SlurryStorageOutdoor(BaseManureTreatment):
    """Class for the outdoor slurry storage.

    Attributes:
        All attributes inherited from BaseManureTreatment.
        In addition, the following attributes are defined:
        storage_time_period: Time in days that the manure is stored in the manure
            treatment system, days.
        freeboard_input: Empty storage space above the manure in the treatment system.
            onto the treatment system.

    """

    def __init__(self, weather, time, manure_treatment_config: ManureTreatmentConfig) -> None:
        """Initializes the outdoor slurry storage manure treatment.

        Args:
            weather: A Weather object.
            time: A Time object.
            manure_treatment_config: A ManureTreatmentConfig object containing
                the configuration data for the manure treatment system.
        """

        super().__init__(weather, time, manure_treatment_config)
        self.storage_time_period = self.config.storage_time_period
        self.freeboard_input = self.config.freeboard_input

    @property
    def wastewater_volume(self) -> float:
        """Calculates the volume of wastewater in the treatment system.

        Returns:
            The volume of wastewater in the treatment system, m^3.

        """
        if self._current_manure_treatment_daily_input:
            return self._current_manure_treatment_daily_input.liquid_manure_daily_volume
        return 0.0

    @property
    def treatment_volume(self) -> float:
        """Calculates the minimum treatment volume.

        Returns:
            The minimum treatment volume, m^3.

        """
        return self.wastewater_volume * self.storage_time_period

    @property
    def total_pit_volume(self) -> float:
        """Calculates the total pit volume.

        Returns:
            The total lagoon pit, m^3.

        """
        if self._current_manure_treatment_daily_input:
            return self.treatment_volume + self.freeboard + self.precip
        return 0.0

    @property
    def pit_depth(self):
        """Returns the depth of the pit.

        Returns:
            The depth of the pit, m.

        """
        return 3.657

    @property
    def pit_slope(self):
        """Returns the slope of the pit.

        Returns:
            The slope of the pit, dimensionless.

        """
        return 2.0

    def _calc_abc(self) -> Tuple[float, float, float]:
        """Calculates the coefficients a, b, and c for volume calculations.

        Returns:
            A tuple containing the coefficients a, b, and c for volume calculations.

        """
        a = 3 * self.pit_depth
        b = -4 * self.pit_slope * self.pit_depth ** 2
        c = 4 * (self.pit_slope ** 2) * (self.pit_depth ** 3) / 3 - self.treatment_volume
        return a, b, c

    @property
    def pit_width(self) -> float:
        """Calculates the width of the pit.

        Returns:
            The width of the pit, m.

        """
        if self._current_manure_treatment_daily_input:
            a, b, c = self._calc_abc()
            return (-b + math.sqrt(b ** 2 - 4 * a * c)) / (2 * a)
        return 0.0

    @property
    def pit_length(self) -> float:
        """Calculate the length of the pit.

        Returns:
            The length of the pit, m.

        """
        return self.pit_width * 3

    @property
    def pit_surface_area(self) -> float:
        """Calculate the surface area of the pit.

        Returns:
            The surface area of the pit, m^2.

        """
        return self.pit_width * self.pit_length

    @property
    def pit_volume(self) -> float:
        """Calculates the volume of the pit.

        Returns:
            The volume of the pit, m^3.

        """
        return (self.pit_length * self.pit_width * self.pit_depth
                - (self.pit_slope * (self.pit_depth ** 2)) * (self.pit_length + self.pit_width)
                + (4 * self.pit_slope * (self.pit_depth ** 3) / 3))

    @property
    def precip(self) -> float:
        """Calculates the additional pit volume needed for precipitation.

        Returns:
            The additional pit volume needed for precipitation, m^3.

        """
        return self._get_current_day_rainfall() * self.pit_surface_area

    @property
    def freeboard(self):
        """Calculates the additional pit volume needed for freeboard.

        Returns:
            The additional pit volume needed for freeboard, m^3.

        """
        return self.freeboard_input * self.pit_surface_area

    def calc_CH4_emission(self, accumulated_manure_total_solids: float) -> Tuple[float, float]:
        """Calculates the CH4 emission from the outdoor slurry storage treatment system.

        Args:
            accumulated_manure_total_solids: The accumulated TS in the treatment system, kg TS.

        Returns:
            A tuple containing the CH4 emission (kg) and the new accumulated TS (kg).

        """

        avg_tempC = self._get_current_day_avg_tempC()
        CH4_loss = GasEmissions.calc_methane_emission_for_slurry_storage(
                manure_total_solids=accumulated_manure_total_solids,
                is_enclosed=False,  # This is what differs from the slurry storage underfloor
                temperature_celsius=avg_tempC
        )
        new_accumulated_TS = max(accumulated_manure_total_solids - CH4_loss, 0.0)
        return CH4_loss, new_accumulated_TS

    def calc_NH3_emission(self, num_animals: int, barn_area: float,
                          accumulated_manure_volume: float,
                          accumulated_manure_total_ammoniacal_nitrogen: float) -> Tuple[float, float]:
        """Calculates the ammonia emission from the outdoor slurry storage treatment system.

        Args:
            num_animals: The number of animals in the barn.
            barn_area: The area of the barn per animal, m^2/animal.
            accumulated_manure_volume: The accumulated manure volume in the treatment system, m^3.
            accumulated_manure_total_ammoniacal_nitrogen: The accumulated TAN in the treatment system, kg.

        Returns:
            NH3_loss: NH3 emission from the outdoor slurry storage, kg.
            new_accumulated_TAN: Accumulated TAN in the treatment system after the
                NH3 emission is calculated, kg.

        """
        avg_tempC = self._get_current_day_avg_tempC()
        NH3_loss = GasEmissions.calc_ammonia_housing_emission(
                num_animals=num_animals,
                barn_area=barn_area,
                manure_urine=accumulated_manure_volume * ManureConstants.MANURE_DENSITY / num_animals,
                manure_urine_total_ammoniacal_nitrogen=accumulated_manure_total_ammoniacal_nitrogen / num_animals,
                temperature_celsius=avg_tempC
        )
        new_accumulated_TAN = max(accumulated_manure_total_ammoniacal_nitrogen - NH3_loss, 0.0)
        return NH3_loss, new_accumulated_TAN

    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        """Returns the daily output of the outdoor slurry storage treatment system.

        Returns:
            A ManureTreatmentDailyOutput object containing the daily output of the
            slurry storage outdoor treatment system.

        """

        daily_output = self._initialize_daily_output_during_update(self._current_manure_treatment_daily_input)
        self._accumulate_daily_output(daily_output)

        CH4_loss, new_accumulated_TS = self.calc_CH4_emission(self._accumulated_output.liquid_manure_total_solids)
        daily_output.storage_methane = CH4_loss
        self._accumulated_output.liquid_manure_total_solids = new_accumulated_TS

        NH3_loss, new_accumulated_TAN = self.calc_NH3_emission(
                num_animals=self._current_pen.num_animals,
                barn_area=self._current_pen.barn_area_from_pen_type,
                accumulated_manure_volume=self._accumulated_output.final_manure_volume,
                accumulated_manure_total_ammoniacal_nitrogen=self._accumulated_output.liquid_manure_total_ammoniacal_nitrogen,
        )
        daily_output.storage_ammonia = NH3_loss
        self._accumulated_output.liquid_manure_total_ammoniacal_nitrogen = new_accumulated_TAN
        return daily_output
