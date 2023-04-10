from __future__ import annotations

from typing import Tuple

from RUFAS.routines.manure.constants.gas_emission_constants import GasEmissionConstants
from RUFAS.routines.manure.constants.manure_constants import ManureConstants
from RUFAS.routines.manure.gas_emissions.gas_emissions import GasEmissions
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import BaseManureTreatment
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import ManureTreatmentConfig
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput


class SlurryStorageUnderfloor(BaseManureTreatment):
    """Class for the underfloor slurry storage.

    Attributes:
        All attributes inherited from BaseManureTreatment.
        In addition, the following attributes are defined:
        storage_time_period: Time in days that the manure is stored in the manure
            treatment system, days.

    """

    def __init__(self, weather, time, manure_treatment_config: ManureTreatmentConfig) -> None:
        """Initialize the underfloor slurry storage manure treatment.

        Args:
            weather: A Weather object.
            time: A Time object.
            manure_treatment_config: A ManureTreatmentConfig object containing
                the configuration data for the manure treatment system.

        """
        super().__init__(weather, time, manure_treatment_config)
        self.storage_time_period = self.config.storage_time_period

    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        """Returns the daily output of the slurry storage underfloor system.

        Returns:
            A ManureTreatmentDailyOutput object containing the daily output of the
            slurry storage underfloor system.

        """
        daily_output = self._initialize_daily_output_during_update(self._current_manure_treatment_daily_input)
        self._accumulate_daily_output(daily_output)

        methane_emission = GasEmissions.calc_methane_emission_for_slurry_storage(
            total_volatile_solids=daily_output.liquid_manure_total_volatile_solids,
            temperature_celsius=self._get_current_day_average_temperature_celsius()
        )
        methane_emission = max(methane_emission, 0.0)
        daily_output.storage_methane = methane_emission
        self._accumulated_output.storage_methane += methane_emission
        self._accumulated_output.liquid_manure_total_volatile_solids += \
            daily_output.liquid_manure_total_volatile_solids - methane_emission * 3

        storage_ammonia_emission = GasEmissions.calc_storage_ammonia_emission(
            manure_total_ammoniacal_nitrogen=(daily_output.liquid_manure_total_ammoniacal_nitrogen
                                              + self._current_pen.manure.urine_total_ammoniacal_nitrogen
                                              - self._manure_handler_daily_output.housing_ammonia),
            manure_volume=daily_output.daily_final_manure_volume,
            total_solids=daily_output.liquid_manure_total_solids,
            storage_area=GasEmissionConstants.DEFAULT_STORAGE_AREA,
            temperature_celsius=self._get_current_day_average_temperature_celsius(),
            pH=GasEmissionConstants.DEFAULT_PH_FOR_STORAGE_AMMONIA
        )
        daily_output.storage_ammonia = storage_ammonia_emission
        self._accumulated_output.storage_ammonia += storage_ammonia_emission

        return daily_output
