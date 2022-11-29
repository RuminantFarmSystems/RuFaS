from __future__ import annotations

from typing import Tuple

from RUFAS.routines.manure.manure_handlers.manure_handler_daily_output import ManureHandlerDailyOutput
from RUFAS.routines.manure.manure_separators.manure_separator_classes import BaseManureSeparator
from RUFAS.routines.manure.manure_separators.manure_separator_daily_output import ManureSeparatorDailyOutput
from RUFAS.routines.manure.manure_treatments.anaerobic_digestion import AnaerobicDigestion
from RUFAS.routines.manure.manure_treatments.anaerobic_lagoon import AnaerobicLagoon
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import BaseManureTreatment
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import ManureTreatmentConfig
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput
from RUFAS.routines.manure.pen.manure_management_pen import ManureManagementPen
from RUFAS.routines.manure.reception_pits.reception_pit_daily_output import ReceptionPitDailyOutput


class AnaerobicDigestionAndLagoon(BaseManureTreatment):
    def __init__(self, weather, time, manure_treatment_config: ManureTreatmentConfig) -> None:
        super().__init__(weather, time, manure_treatment_config)
        self._anaerobic_digestion = AnaerobicDigestion(weather, time, manure_treatment_config)
        self._anaerobic_lagoon = AnaerobicLagoon(weather, time, manure_treatment_config)
        self.with_split = False

    def daily_update_with_separator_as_middle_step(self,
                                                   manure_handler_daily_output: ManureHandlerDailyOutput,
                                                   reception_pit_daily_output: ReceptionPitDailyOutput,
                                                   manure_separator: BaseManureSeparator,
                                                   pen: ManureManagementPen,
                                                   sim_day: int
                                                   ) -> Tuple[ManureSeparatorDailyOutput, ManureTreatmentDailyOutput]:
        self._initialize_private_attributes_during_update(
                sim_day=sim_day,
                current_pen=pen,
                manure_handler_daily_output=manure_handler_daily_output,
                reception_pit_daily_output=reception_pit_daily_output,
                manure_separator_daily_output=None,
        )
        anaerobic_digestion_daily_output = self._anaerobic_digestion.daily_update(
                manure_handler_daily_output=self._manure_handler_daily_output,
                reception_pit_daily_output=self._reception_pit_daily_output,
                manure_separator_daily_output=self._manure_separator_daily_output,
                pen=self._current_pen,
                sim_day=self._sim_day
        )
        # TODO: Pass the anaerobic digestion output to the separator
        # TODO: Pass the separator output to the anaerobic lagoon
        return ManureSeparatorDailyOutput(), ManureTreatmentDailyOutput()

    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        """Updates the anaerobic digestion model for a single day."""
        anaerobic_digestion_daily_output = self._anaerobic_digestion.daily_update(
                manure_handler_daily_output=self._manure_handler_daily_output,
                reception_pit_daily_output=self._reception_pit_daily_output,
                manure_separator_daily_output=self._manure_separator_daily_output,
                pen=self._current_pen,
                sim_day=self._sim_day
        )
        # TODO: Process the anaerobic digestion output to the anaerobic lagoon
        # temp_manure_handler_daily_output = ManureHandlerDailyOutput(
        #
        # )
        anaerobic_lagoon_daily_output = self._anaerobic_lagoon.daily_update(
                manure_handler_daily_output=self._manure_handler_daily_output,
                reception_pit_daily_output=self._reception_pit_daily_output,
                manure_separator_daily_output=self._manure_separator_daily_output,
                pen=self._current_pen,
                sim_day=self._sim_day
        )
        combined_daily_output = anaerobic_digestion_daily_output + anaerobic_lagoon_daily_output
        return self._adjust_pen_id_and_sim_day(combined_daily_output)

    # TODO: Remove afterward
    def _adjust_pen_id_and_sim_day(self, manure_treatment_daily_output: ManureTreatmentDailyOutput) \
            -> ManureTreatmentDailyOutput:
        """Adjusts the pen ID and sim day for the daily output."""
        manure_treatment_daily_output_copy = manure_treatment_daily_output.clone()
        manure_treatment_daily_output_copy.pen_id = self._current_pen.id
        manure_treatment_daily_output_copy.sim_day = self._sim_day
        return manure_treatment_daily_output_copy
