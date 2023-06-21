from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Optional
from typing import Tuple
from typing import Union

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

    def __init__(self, weather, time,
                 manure_treatment_config: Union[ManureTreatmentConfig,
                                                Tuple[ManureTreatmentConfig, ManureTreatmentConfig]]
                 ) -> None:
        """Initializes the BaseManureTreatment class.

        Args:
            weather: A Weather object.
            time: A Time object.
            manure_treatment_config: A ManureTreatmentConfig object containing the
                configuration for the manure treatment.

        Private attributes:
            _sim_day: The current simulation day.
            _current_pen: The current pen object.
            _manure_handler_daily_output: The daily output of the manure handler.
            _current_manure_treatment_daily_input: The current input data assigned based on the
                input data passed into the daily_update() method.
            _manure_separator: Only present in the digester - separator - lagoon scenario.
            _manure_separator_daily_output: Only present in the digester - separator - lagoon scenario.
            _accumulated_output: Summation of all daily outputs.

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
        """Returns the daily output of the intervening separator in the digester - separator - lagoon scenario.

        Returns:
            A ManureSeparatorDailyOutput object containing the daily output of
            the intervening separator in the digester - separator - lagoon scenario.

        """
        return self._manure_separator_daily_output

    def _initialize_private_attributes_during_update(self, sim_day: int,
                                                     current_pen: ManureManagementPen,
                                                     manure_handler_daily_output: ManureHandlerDailyOutput,
                                                     manure_treatment_daily_input: LiquidManurePortionProtocol,
                                                     manure_separator: BaseManureSeparator) -> None:
        """Initializes the private attributes of the class.

        Args:
            sim_day: The current simulation day.
            current_pen: The current pen.
            manure_handler_daily_output: The daily output of the manure handler.
            manure_treatment_daily_input: The daily input of the manure treatment.
            manure_separator: The manure separator.

        """
        self._sim_day = sim_day
        self._current_pen = current_pen
        self._manure_handler_daily_output = manure_handler_daily_output
        self._current_manure_treatment_daily_input = manure_treatment_daily_input
        self._manure_separator = manure_separator

    def _initialize_daily_output_during_update(self, manure_treatment_daily_input: LiquidManurePortionProtocol) \
            -> ManureTreatmentDailyOutput:
        """Initializes the daily output of the manure treatment, which will be subsequently modified.

        Typically, this method should be called at the beginning of the _daily_update_helper() method.
        The generated ManureTreatmentDailyOutput object can then be modified depending on the nature
        of the manure treatment subclass.

        Args:
            manure_treatment_daily_input: A LiquidManurePortionProtocol object containing
                the daily input of the manure treatment.

        Returns:
            A ManureTreatmentDailyOutput object containing the daily output of the manure treatment.

        """
        final_manure_volume = (manure_treatment_daily_input.liquid_manure_daily_volume -
                               (manure_treatment_daily_input.liquid_manure_total_solids *
                                self.config.total_solids_removal_efficiency_for_treatment) /
                               1000.0)  # TODO: Make 1000.0 a constant

        return ManureTreatmentDailyOutput(
                simulation_day=manure_treatment_daily_input.simulation_day,
                pen_id=manure_treatment_daily_input.pen_id,
                liquid_manure_total_ammoniacal_nitrogen=(
                        manure_treatment_daily_input.liquid_manure_total_ammoniacal_nitrogen *
                        (1 - self.config.total_ammoniacal_nitrogen_removal_efficiency_for_treatment)),
                liquid_manure_nitrogen=(
                        manure_treatment_daily_input.liquid_manure_nitrogen *
                        (1 - self.config.nitrogen_removal_efficiency_for_treatment)),
                liquid_manure_total_solids=(
                        manure_treatment_daily_input.liquid_manure_total_solids *
                        (1 - self.config.total_solids_removal_efficiency_for_treatment)),
                liquid_manure_total_volatile_solids=(
                        manure_treatment_daily_input.liquid_manure_total_volatile_solids *
                        (1 - self.config.volatile_solids_removal_efficiency_for_treatment)),
                liquid_manure_phosphorus=(
                        manure_treatment_daily_input.liquid_manure_phosphorus *
                        (1 - self.config.phosphorus_removal_efficiency_for_treatment)),
                liquid_manure_potassium=(
                        manure_treatment_daily_input.liquid_manure_potassium *
                        (1 - self.config.potassium_removal_efficiency_for_treatment)),
                daily_final_manure_volume=final_manure_volume,
        )

    def daily_update(self,
                     manure_handler_daily_output: ManureHandlerDailyOutput,
                     manure_treatment_daily_input: LiquidManurePortionProtocol,
                     pen: ManureManagementPen,
                     sim_day: int,
                     manure_separator: Optional[BaseManureSeparator] = None
                     ) -> ManureTreatmentDailyOutput:
        """Calculates the daily output of the manure treatment.

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
        daily_output = self._daily_update_helper()
        self._accumulated_output.simulation_day = sim_day
        self._accumulated_output.pen_id = pen.id
        return daily_output

    @abstractmethod
    def _daily_update_helper(self) -> ManureTreatmentDailyOutput:
        """Helper method for the daily_update() method.

        This method is called immediately after the private attributes of the class are initialized,
        and it is up to the subclass to decide what to put in here.

        Returns:
            A ManureTreatmentDailyOutput object containing the output of the manure
                treatment for the current simulation day.

        """
        pass

    def calc_methane_emission(self, *args, **kwargs) -> float:
        """Calculates the methane emission of the manure treatment.

        For those treatments that do not produce methane emission, this method will return 0.0.
        Otherwise, the method will be overridden by the subclass.

        """
        return 0.0

    def calc_ammonia_emission(self, *args, **kwargs) -> float:
        """Calculates the ammonia emission of the manure treatment.

        For those treatments that do not produce ammonia emission, this method will return 0.0.
        Otherwise, the method will be overridden by the subclass.

        """
        return 0.0

    def _get_current_day_average_temperature_celsius(self) -> float:
        """Returns the average temperature of the current day in Celsius.

        Returns:
            The average temperature of the current day in Celsius.

        """
        return self.weather.T_avg[self.time.year - 1][self.time.day - 1]

    def _get_current_day_rainfall(self) -> float:
        """Returns the rainfall of the current day in mm.  # TODO: Check the unit.

        Returns:
            The rainfall of the current day in mm.

        """
        return self.weather.rainfall[self.time.year - 1][self.time.day - 1]

    def _accumulate_daily_output(self, manure_treatment_daily_output: ManureTreatmentDailyOutput) -> None:
        """Accumulates the daily output of the manure treatment.

        Args:
            manure_treatment_daily_output: A ManureTreatmentDailyOutput object containing
                the daily output of the manure treatment.

        """
        self._accumulated_output += manure_treatment_daily_output
