from __future__ import annotations

from typing import Tuple

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

    def calc_CH4_emission(self, accumulated_manure_total_solids: float) -> Tuple[float, float]:
        """Calculates the CH4 emission from the underfloor slurry storage.

        Args:
            accumulated_manure_total_solids: Accumulated TS in the treatment system, kg.

        Returns:
            CH4_loss: CH4 emission from the underfloor slurry storage, kg.

        """
        tempC = self._get_current_day_avg_tempC()
        CH4_loss = GasEmissions.calc_methane_emission_for_slurry_storage(
                manure_total_solids=accumulated_manure_total_solids,
                is_enclosed=True,
                temperature_celsius=tempC
        )
        new_accumulated_TS = max(accumulated_manure_total_solids - CH4_loss, 0.0)
        return CH4_loss, new_accumulated_TS

    def calc_NH3_emission(self, num_animals: int, barn_area: float,
                          accumulated_manure_volume: float,
                          accumulated_manure_total_ammoniacal_nitrogen: float) -> Tuple[float, float]:
        """Calculates the NH3 emission from the underfloor slurry storage.

        Args:
            num_animals: Number of animals in the pen, animals.
            barn_area: Area of the barn per animal, m^2/animal.
            accumulated_manure_volume: Accumulated manure volume in the treatment system, m^3.
            accumulated_manure_total_ammoniacal_nitrogen: Accumulated TAN in the treatment system, kg.

        Returns:
            NH3_loss: NH3 emission from the underfloor slurry storage, kg.
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
        """Returns the daily output of the slurry storage underfloor system.

        Returns:
            A ManureTreatmentDailyOutput object containing the daily output of the
            slurry storage underfloor system.

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
                accumulated_manure_total_ammoniacal_nitrogen=self._accumulated_output.liquid_manure_total_ammoniacal_nitrogen
        )
        daily_output.storage_ammonia = NH3_loss
        self._accumulated_output.liquid_manure_total_ammoniacal_nitrogen = new_accumulated_TAN

        return daily_output
