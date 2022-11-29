from __future__ import annotations
from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Optional
from typing import Union

from RUFAS.routines.manure.manure_handlers.manure_handler_daily_output import ManureHandlerDailyOutput
from RUFAS.routines.manure.manure_separators.manure_separator_daily_output import ManureSeparatorDailyOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import ManureTreatmentConfig
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput
from RUFAS.routines.manure.pen.manure_management_pen import ManureManagementPen
from RUFAS.routines.manure.reception_pits.reception_pit_daily_output import ReceptionPitDailyOutput

# Tne input for a manure treatment can come from a reception pit or a manure separator.
ManureTreatmentInputDataType = Union[ReceptionPitDailyOutput, ManureSeparatorDailyOutput]


class BaseManureTreatment(ABC):
    """Base class for all manure treatment classes.

    Attributes:
        weather: A Weather object.
        time: A Time object.
        config: A ManureTreatmentConfig object containing the configuration for the manure treatment.

    """

    def __init__(self, weather, time, manure_treatment_config: ManureTreatmentConfig) -> None:
        """Initializes the BaseManureTreatment class.

        Args:
            weather: A Weather object.
            time: A Time object.
            manure_treatment_config: A ManureTreatmentConfig object containing the
                configuration for the manure treatment.

        Private attributes:
            _current_input_data: The current input data assigned based on the
                input data passed into the daily_update() method.

        """
        self.weather = weather
        self.time = time
        self.config = manure_treatment_config

        self._sim_day = -1
        self._current_pen: Optional[ManureManagementPen] = None
        self._manure_handler_daily_output = None
        self._reception_pit_daily_output = None
        self._manure_separator_daily_output = None
        self._current_input_data: Optional[ManureTreatmentInputDataType] = None

        self._accumulated_output = ManureTreatmentDailyOutput()

    def _initialize_private_attributes_during_update(self, sim_day: int,
                                                     current_pen: ManureManagementPen,
                                                     manure_handler_daily_output: ManureHandlerDailyOutput,
                                                     reception_pit_daily_output: ReceptionPitDailyOutput,
                                                     manure_separator_daily_output: Optional[
                                                         ManureSeparatorDailyOutput]) \
            -> None:
        self._sim_day = sim_day
        self._current_pen = current_pen
        self._manure_handler_daily_output = manure_handler_daily_output
        self._reception_pit_daily_output = reception_pit_daily_output
        self._manure_separator_daily_output = manure_separator_daily_output
        self._current_input_data = manure_separator_daily_output or reception_pit_daily_output

    def _initialize_daily_output_during_update(self) -> ManureTreatmentDailyOutput:
        if not self._current_input_data:
            raise ValueError('No input data was passed into the daily_update() method.')

        final_manure_volume = (self._get_input_manure_volume(self._current_input_data) -
                               (self._current_input_data.TS * self.config.TS_removal_efficiency_for_treatment) / 1000.0)

        daily_output = ManureTreatmentDailyOutput(
                simulation_day=self._current_input_data.simulation_day,
                pen_id=self._current_input_data.pen_id,
                TAN=self._current_input_data.TAN * (1 - self.config.TAN_removal_efficiency_for_treatment),
                N=self._current_input_data.N * (1 - self.config.N_removal_efficiency_for_treatment),
                TS=self._current_input_data.TS * (1 - self.config.TS_removal_efficiency_for_treatment),
                VS_total=self._current_input_data.VS_total * (1 - self.config.VS_removal_efficiency_for_treatment),
                P=self._current_input_data.P * (1 - self.config.P_removal_efficiency_for_treatment),
                K=self._current_input_data.K * (1 - self.config.K_removal_efficiency_for_treatment),
                final_manure_volume=final_manure_volume,
        )
        return daily_output

    @classmethod
    def _get_input_manure_volume(cls, current_input_data: ManureTreatmentInputDataType) -> float:
        if not current_input_data:
            raise ValueError('No input data was passed into the daily_update() method.')
        elif isinstance(current_input_data, ManureSeparatorDailyOutput):
            return current_input_data.final_daily_volume
        elif isinstance(current_input_data, ReceptionPitDailyOutput):
            return current_input_data.total_daily_manure_volume
        else:
            raise ValueError('Invalid input data type.')

    def daily_update(self,
                     manure_handler_daily_output: ManureHandlerDailyOutput,
                     reception_pit_daily_output: ReceptionPitDailyOutput,
                     manure_separator_daily_output: Optional[ManureSeparatorDailyOutput],
                     pen: ManureManagementPen,
                     sim_day: int
                     ) -> ManureTreatmentDailyOutput:
        """Calculates and stores the daily output of the manure treatment.

        Args:
            manure_handler_daily_output: A ManureHandlerDailyOutput object containing the
                daily output of the manure handler.
            reception_pit_daily_output: ReceptionPitDailyOutput object containing
                the daily output of the reception pit.
            manure_separator_daily_output: ManureSeparatorDailyOutput object containing
                the daily output of the manure separator.
            pen: A ManureManagementPen object.
            sim_day: The current simulation day.

        Returns:
            A ManureTreatmentDailyOutput object containing the output of the manure
                treatment for the current simulation day.

        """
        self._initialize_private_attributes_during_update(sim_day, pen, manure_handler_daily_output,
                                                          reception_pit_daily_output, manure_separator_daily_output)
        return self._daily_update_helper()

    @abstractmethod
    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        pass

    def calc_CH4_emission(self, *args, **kwargs) -> float:
        return 0.0

    def calc_NH3_emission(self, *args, **kwargs) -> float:
        return 0.0

    def _get_current_day_avg_tempC(self) -> float:
        return self.weather.T_avg[self.time.year - 1][self.time.day - 1]

    def _get_current_day_rainfall(self) -> float:
        return self.weather.rainfall[self.time.year - 1][self.time.day - 1]

    def _accumulate_daily_output(self, daily_output: ManureTreatmentDailyOutput) -> None:
        self._accumulated_output += daily_output
