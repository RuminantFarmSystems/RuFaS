from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Optional

from RUFAS.routines.manure.manure_handlers.manure_handler_daily_output import ManureHandlerDailyOutput
from RUFAS.routines.manure.manure_separators.manure_separator_classes import BaseManureSeparator
from RUFAS.routines.manure.manure_separators.manure_separator_daily_output import ManureSeparatorDailyOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import ManureTreatmentConfig
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput
from RUFAS.routines.manure.pen.manure_management_pen import ManureManagementPen
from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import LiquidManurePortionProtocol


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
            _current_manure_treatment_daily_input: The current input data assigned based on the
                input data passed into the daily_update() method.

        """
        self.weather = weather
        self.time = time
        self.config = manure_treatment_config

        self._sim_day = -1
        self._current_pen: Optional[ManureManagementPen] = None
        self._manure_handler_daily_output = None
        self._current_manure_treatment_daily_input: Optional[LiquidManurePortionProtocol] = None
        self._manure_separator: Optional[BaseManureSeparator] = None
        self._manure_separator_daily_output: Optional[ManureSeparatorDailyOutput] = None
        self._accumulated_output = ManureTreatmentDailyOutput()

    @property
    def manure_separator_daily_output(self) -> Optional[ManureSeparatorDailyOutput]:
        return self._manure_separator_daily_output

    def _initialize_private_attributes_during_update(self, sim_day: int,
                                                     current_pen: ManureManagementPen,
                                                     manure_handler_daily_output: ManureHandlerDailyOutput,
                                                     manure_treatment_daily_input: LiquidManurePortionProtocol,
                                                     manure_separator: BaseManureSeparator) -> \
            None:
        self._sim_day = sim_day
        self._current_pen = current_pen
        self._manure_handler_daily_output = manure_handler_daily_output
        self._current_manure_treatment_daily_input = manure_treatment_daily_input
        self._manure_separator = manure_separator

    def _initialize_daily_output_during_update(self, manure_treatment_daily_input: LiquidManurePortionProtocol) -> \
            ManureTreatmentDailyOutput:
        final_manure_volume = (manure_treatment_daily_input.liquid_manure_daily_volume -
                               (
                                       manure_treatment_daily_input.liquid_manure_total_solids *
                                       self.config.TS_removal_efficiency_for_treatment) /
                               1000.0)

        return ManureTreatmentDailyOutput(
                simulation_day=manure_treatment_daily_input.simulation_day,
                pen_id=manure_treatment_daily_input.pen_id,
                liquid_manure_total_ammoniacal_nitrogen=(
                        manure_treatment_daily_input.liquid_manure_total_ammoniacal_nitrogen *
                        (1 - self.config.TAN_removal_efficiency_for_treatment)),
                liquid_manure_nitrogen=(
                        manure_treatment_daily_input.liquid_manure_nitrogen *
                        (1 - self.config.N_removal_efficiency_for_treatment)),
                liquid_manure_total_solids=(
                        manure_treatment_daily_input.liquid_manure_total_solids *
                        (1 - self.config.TS_removal_efficiency_for_treatment)),
                liquid_manure_total_volatile_solids=(
                        manure_treatment_daily_input.liquid_manure_total_volatile_solids *
                        (1 - self.config.VS_removal_efficiency_for_treatment)),
                liquid_manure_phosphorus=(
                        manure_treatment_daily_input.liquid_manure_phosphorus *
                        (1 - self.config.P_removal_efficiency_for_treatment)),
                liquid_manure_potassium=(
                        manure_treatment_daily_input.liquid_manure_potassium *
                        (1 - self.config.K_removal_efficiency_for_treatment)),
                final_manure_volume=final_manure_volume,
        )

    def daily_update(self,
                     manure_handler_daily_output: ManureHandlerDailyOutput,
                     manure_treatment_daily_input: LiquidManurePortionProtocol,
                     pen: ManureManagementPen,
                     sim_day: int,
                     manure_separator: Optional[BaseManureSeparator] = None
                     ) -> ManureTreatmentDailyOutput:
        """Calculates and stores the daily output of the manure treatment.

        Args:
            manure_handler_daily_output: A ManureHandlerDailyOutput object containing the
                daily output of the manure handler.
            manure_treatment_daily_input: A LiquidManurePortionProtocol object containing
                the daily input of the manure treatment.
            pen: A ManureManagementPen object.
            sim_day: The current simulation day.
            manure_separator: A optional BaseManureSeparator object meant to be used in the special
                case of digester-separator-lagoon configuration triple.

        Returns:
            A ManureTreatmentDailyOutput object containing the output of the manure
                treatment for the current simulation day.

        """
        self._initialize_private_attributes_during_update(sim_day, pen, manure_handler_daily_output,
                                                          manure_treatment_daily_input, manure_separator)
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
