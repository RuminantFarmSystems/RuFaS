from __future__ import annotations

from RUFAS.routines.manure.manure_treatments.anaerobic_digestion import AnaerobicDigestion
from RUFAS.routines.manure.manure_treatments.anaerobic_lagoon import AnaerobicLagoon
from RUFAS.routines.manure.manure_treatments.base_manure_treatment import BaseManureTreatment
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import ManureTreatmentConfig
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput


class AnaerobicDigestionAndLagoon(BaseManureTreatment):
    """A class that models the coupling of the anaerobic digestion and lagoon manure treatments.

    There are two distinct scenarios that this class models: (1) This combination of manure treatments
    is preceded by a manure separator, and (2) this combination of manure treatments sandwiches
    a manure separator.

    Attributes:
        Same as BaseManureTreatment.

    """

    def __init__(self, weather, time, manure_treatment_config: ManureTreatmentConfig) -> None:
        super().__init__(weather, time, manure_treatment_config)
        self._anaerobic_digestion = AnaerobicDigestion(weather, time, manure_treatment_config)
        self._anaerobic_lagoon = AnaerobicLagoon(weather, time, manure_treatment_config)

    def _create_anaerobic_digestion_daily_output(self) -> ManureTreatmentDailyOutput:
        """Creates the daily output for the anaerobic digestion model.

        Returns:
            A ManureTreatmentDailyOutput object containing the daily output for the anaerobic digestion model.

        """
        return self._anaerobic_digestion.daily_update(
                manure_handler_daily_output=self._manure_handler_daily_output,
                manure_treatment_daily_input=self._current_manure_treatment_daily_input,
                pen=self._current_pen,
                sim_day=self._sim_day
        )

    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        """Returns the manure treatment daily output.

        Returns:
            A ManureTreatmentDailyOutput object containing the daily output for
            the anaerobic digestion and lagoon model.

        """
        anaerobic_digestion_daily_output = self._create_anaerobic_digestion_daily_output()

        manure_separator_daily_output = self._manure_separator.daily_update(
                manure_separator_daily_input=anaerobic_digestion_daily_output,
        ) if self._manure_separator else None

        self._manure_separator_daily_output = manure_separator_daily_output

        anaerobic_lagoon_daily_output = self._anaerobic_lagoon.daily_update(
                manure_handler_daily_output=self._manure_handler_daily_output,
                manure_treatment_daily_input=manure_separator_daily_output or anaerobic_digestion_daily_output,
                pen=self._current_pen,
                sim_day=self._sim_day
        )

        return anaerobic_lagoon_daily_output
