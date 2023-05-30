from __future__ import annotations

import math
from typing import Tuple

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.manure.constants.gas_emission_constants import GasEmissionConstants
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
            return self.treatment_volume + self.freeboard_volume + self.precipitation_volume
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
    def precipitation_volume(self) -> float:
        """Calculates the additional pit volume needed for precipitation.

        Returns:
            The additional pit volume needed for precipitation, m^3.

        """
        rainfall = self._get_current_day_rainfall() * GeneralConstants.MM_TO_M
        return rainfall * self.pit_surface_area

    @property
    def freeboard_volume(self):
        """Calculates the additional pit volume needed for freeboard.

        Returns:
            The additional pit volume needed for freeboard, m^3.

        """
        return self.freeboard_input * self.pit_surface_area

    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        """Returns the daily output of the outdoor slurry storage treatment system.

        Returns:
            A ManureTreatmentDailyOutput object containing the daily output of the
            slurry storage outdoor treatment system.

        """
        daily_output = self._initialize_daily_output_during_update(self._current_manure_treatment_daily_input)
        self._accumulate_daily_output(daily_output)

        methane_emission = GasEmissions.calc_methane_emission_for_slurry_storage(
            total_volatile_solids=daily_output.liquid_manure_total_volatile_solids,
            temp=self._get_current_day_average_temperature_celsius()
        )
        methane_emission = max(methane_emission, 0.0)
        daily_output.storage_methane = methane_emission
        self._accumulated_output.storage_methane += methane_emission
        self._accumulated_output.liquid_manure_total_volatile_solids += \
            daily_output.liquid_manure_total_volatile_solids - methane_emission * 3

        storage_ammonia_emission = GasEmissions.calc_storage_ammonia_emission(
            num_animals=self._current_pen.num_animals,
            manure_total_ammoniacal_nitrogen=(daily_output.liquid_manure_total_ammoniacal_nitrogen
                                              + self._current_pen.manure.urine_total_ammoniacal_nitrogen
                                              - self._manure_handler_daily_output.housing_ammonia),
            manure_volume=daily_output.daily_final_manure_volume,
            total_solids=daily_output.liquid_manure_total_solids,
            storage_area=GasEmissionConstants.DEFAULT_STORAGE_AREA,
            temp=self._get_current_day_average_temperature_celsius(),
            pH=GasEmissionConstants.DEFAULT_PH_FOR_STORAGE_AMMONIA
        )
        daily_output.storage_ammonia = storage_ammonia_emission
        self._accumulated_output.storage_ammonia += storage_ammonia_emission

        return daily_output
