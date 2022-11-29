from __future__ import annotations

from typing import Tuple

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

    def calc_CH4_emission(self, accumulated_TS: float) -> Tuple[float, float]:
        tempC = self._get_current_day_avg_tempC()
        CH4_loss = GasEmissions.calc_E_CH4_slurry_storage(
                TS=accumulated_TS,
                enclosed=True,
                tempC=tempC
        )
        new_accumulated_TS = max(accumulated_TS - CH4_loss, 0.0)
        return CH4_loss, new_accumulated_TS

    def calc_NH3_emission(self, num_animals: int, barn_area: float,
                          accumulated_urine: float,
                          accumulated_urine_TAN: float) -> Tuple[float, float]:
        tempC = self._get_current_day_avg_tempC()
        NH3_loss = GasEmissions.calc_E_NH3_emission(
                num_animals=num_animals,
                barn_area=barn_area,
                urine=accumulated_urine,
                urine_TAN=accumulated_urine_TAN,
                tempC=tempC
        )
        new_accumulated_pen_urine_TAN = max(accumulated_urine_TAN - NH3_loss, 0.0)
        return NH3_loss, new_accumulated_pen_urine_TAN

    # TODO: review this
    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        daily_output = self._initialize_daily_output_during_update()
        self._accumulate_daily_output(daily_output)

        CH4_loss, new_accumulated_TS = self.calc_CH4_emission(self._accumulated_output.TS)
        daily_output.CH4 = CH4_loss
        self._accumulated_output.TS = new_accumulated_TS

        NH3_loss, new_accumulated_pen_urine_TAN = self.calc_NH3_emission(
                num_animals=self._current_pen.num_animals,
                barn_area=self._current_pen.barn_area_from_pen_type,
                accumulated_urine=0.0,
                accumulated_urine_TAN=self._accumulated_output.TAN,
        )
        daily_output.NH3 = NH3_loss
        self._accumulated_output.TAN = new_accumulated_pen_urine_TAN

        return daily_output
