from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Tuple, Union

import numpy as np

from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.manure.constants_and_units.gas_emission_constants import GasEmissionConstants
from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants
from RUFAS.routines.manure.IO_helpers.manure_module_output_manager_helper import ManureModuleOutputManagerHelper
from RUFAS.routines.manure.manure_handlers.manure_handler_daily_output import ManureHandlerDailyOutput
from RUFAS.routines.manure.manure_separators.manure_separator_classes import BaseManureSeparator
from RUFAS.routines.manure.manure_separators.manure_separator_daily_output import ManureSeparatorDailyOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_configs import ManureTreatmentConfig
from RUFAS.routines.manure.manure_treatments.manure_treatment_daily_output import ManureTreatmentDailyOutput
from RUFAS.routines.manure.manure_treatments.manure_treatment_types import ManureTreatmentType
from RUFAS.routines.manure.pen_manure.manure_manager_pen import ManureManagerPen
from RUFAS.routines.manure.protocols.liquid_manure_portion_protocol import LiquidManurePortionProtocol
from RUFAS.time import Time
from RUFAS.weather import Weather


class BaseManureTreatment(ABC):
    """Base class for all manure treatment classes.

    Attributes:
        weather: A Weather object.
        time: A Time object.
        config: A ManureTreatmentConfig object containing the configuration for the manure treatment.

    """

    def __init__(
        self,
        weather: Weather,
        time: Time,
        manure_treatment_config: Union[ManureTreatmentConfig, Tuple[ManureTreatmentConfig, ManureTreatmentConfig]],
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
            _manure_separator: Present in the separator - digester - separator - lagoon scenario.
            _manure_separator_daily_output: Only present in the digester - separator - lagoon scenario.
            _accumulated_output: Summation of all daily outputs.

        """
        self.weather = weather
        self.time = time
        self.config = manure_treatment_config

        self._sim_day = -1
        self._current_pen: Optional[ManureManagerPen] = None
        self._manure_handler_daily_output = None
        self._current_manure_treatment_daily_input: Optional[LiquidManurePortionProtocol] = None
        self._manure_separator: Optional[BaseManureSeparator] = None
        self._manure_separator_daily_output: Optional[ManureSeparatorDailyOutput] = None
        self._manure_separator_after_digestion: Optional[BaseManureSeparator] = None
        self._manure_separator_after_digestion_daily_output: Optional[ManureSeparatorDailyOutput] = None
        try:
            self.storage_time_period = self.config.storage_time_period
        except AttributeError:
            self.storage_time_period = None
        self._accumulated_output = ManureTreatmentDailyOutput()

    @property
    def accumulated_output(self) -> ManureTreatmentDailyOutput:
        """Returns the accumulated output of the manure treatment.
        Returns
        -------
        ManureTreatmentDailyOutput
            A ManureTreatmentDailyOutput object containing the accumulated output of the manure treatment.
        """
        return self._accumulated_output

    @property
    def manure_separator_after_digestion_daily_output(
        self,
    ) -> Optional[ManureSeparatorDailyOutput]:
        """Returns the daily output of the intervening separator in the digester - separator - lagoon scenario.

        Returns:
            A ManureSeparatorDailyOutput object containing the daily output of
            the intervening separator in the digester - separator - lagoon scenario.

        """
        return self._manure_separator_after_digestion_daily_output

    def _initialize_private_attributes_during_update(
        self,
        sim_day: int,
        current_pen: ManureManagerPen,
        manure_handler_daily_output: ManureHandlerDailyOutput,
        manure_treatment_daily_input: LiquidManurePortionProtocol,
        manure_separator: BaseManureSeparator,
        manure_separator_after_digestion: BaseManureSeparator,
    ) -> None:
        """Initializes the private attributes of the class.

        Args:
            sim_day: The current simulation day.
            current_pen: The current pen.
            manure_handler_daily_output: The daily output of the manure handler.
            manure_treatment_daily_input: The daily input of the manure treatment.
            manure_separator: The manure separator.
            manure_separator_after_digestion: The manure separator between the digestor and lagoon.

        """
        self._sim_day = sim_day
        self._current_pen = current_pen
        self._manure_handler_daily_output = manure_handler_daily_output
        self._current_manure_treatment_daily_input = manure_treatment_daily_input
        self._manure_separator = manure_separator
        self._manure_separator_after_digestion = manure_separator_after_digestion

    def _initialize_daily_output_during_update(
        self, manure_treatment_daily_input: LiquidManurePortionProtocol
    ) -> ManureTreatmentDailyOutput:
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
        simulation_day = manure_treatment_daily_input.simulation_day
        pen_id = manure_treatment_daily_input.pen_id

        liquid_manure_total_ammoniacal_nitrogen = (
            manure_treatment_daily_input.liquid_manure_total_ammoniacal_nitrogen
            * (1 - self.config.total_ammoniacal_nitrogen_removal_efficiency_for_treatment)
        )

        liquid_manure_nitrogen = manure_treatment_daily_input.liquid_manure_nitrogen * (
            1 - self.config.nitrogen_removal_efficiency_for_treatment
        )

        liquid_manure_total_solids = manure_treatment_daily_input.liquid_manure_total_solids * (
            1 - self.config.total_solids_removal_efficiency_for_treatment
        )

        liquid_manure_total_volatile_solids = manure_treatment_daily_input.liquid_manure_total_volatile_solids * (
            1 - self.config.volatile_solids_removal_efficiency_for_treatment
        )

        liquid_manure_total_degradable_volatile_solids = (
            manure_treatment_daily_input.liquid_manure_total_degradable_volatile_solids
            * (1 - self.config.volatile_solids_removal_efficiency_for_treatment)
        )

        liquid_manure_total_non_degradable_volatile_solids = (
            manure_treatment_daily_input.liquid_manure_total_non_degradable_volatile_solids
            * (1 - self.config.volatile_solids_removal_efficiency_for_treatment)
        )

        liquid_manure_phosphorus = manure_treatment_daily_input.liquid_manure_phosphorus * (
            1 - self.config.phosphorus_removal_efficiency_for_treatment
        )

        liquid_manure_potassium = manure_treatment_daily_input.liquid_manure_potassium * (
            1 - self.config.potassium_removal_efficiency_for_treatment
        )

        final_manure_volume = manure_treatment_daily_input.liquid_manure_daily_volume

        return ManureTreatmentDailyOutput(
            simulation_day=simulation_day,
            pen_id=pen_id,
            liquid_manure_total_ammoniacal_nitrogen=liquid_manure_total_ammoniacal_nitrogen,
            liquid_manure_nitrogen=liquid_manure_nitrogen,
            liquid_manure_total_solids=liquid_manure_total_solids,
            liquid_manure_total_volatile_solids=liquid_manure_total_volatile_solids,
            liquid_manure_total_degradable_volatile_solids=liquid_manure_total_degradable_volatile_solids,
            liquid_manure_total_non_degradable_volatile_solids=liquid_manure_total_non_degradable_volatile_solids,
            liquid_manure_phosphorus=liquid_manure_phosphorus,
            liquid_manure_potassium=liquid_manure_potassium,
            daily_final_manure_volume=final_manure_volume,
        )

    def daily_update(
        self,
        manure_handler_daily_output: ManureHandlerDailyOutput,
        manure_treatment_daily_input: LiquidManurePortionProtocol,
        pen: ManureManagerPen,
        sim_day: int,
        manure_separator: Optional[BaseManureSeparator] = None,
        manure_separator_after_digestion: Optional[BaseManureSeparator] = None,
    ) -> ManureTreatmentDailyOutput:
        """Calculates the daily output of the manure treatment.

        Args:
            manure_handler_daily_output: A ManureHandlerDailyOutput object containing the
                daily output of the manure handler.
            manure_treatment_daily_input: A LiquidManurePortionProtocol object containing
                the daily input of the manure treatment.
            pen: A ManureManagerPen object.
            sim_day: The current simulation day.
            manure_separator: A optional BaseManureSeparator object meant to be used in the special
                case of digester-separator-lagoon configuration triple.
            manure_separator_after_digestion: An optional BaseManureSeparator object meant to be used in the special
                case of digester-separator-lagoon configuration triple.

        Returns:
            A ManureTreatmentDailyOutput object containing the output of the manure
                treatment for the current simulation day.

        """
        self._initialize_private_attributes_during_update(
            sim_day,
            pen,
            manure_handler_daily_output,
            manure_treatment_daily_input,
            manure_separator,
            manure_separator_after_digestion,
        )
        if pen.num_animals == 0:
            daily_output = ManureTreatmentDailyOutput()
        else:
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

    @staticmethod
    def _determine_outdoor_storage_temperature(air_temperature: float) -> float:
        """Determines the temperature of the manure in outdoor liquid and slurry storages.

        Parameters
        ----------
        air_temperature : float
            The current day's ambient air temperature (°C).

        Returns
        -------
        float
            The estimated temperature of the manure storage (°C).

        References
        ----------

        This function clamps stored manure temperature to between 0 and 35 °C. Between 0 and 35 °C, outdoor stored
        liquid manure temperature is assumed to be equal to ambient air temperature. These bounds were based on
        personal communication and recommendations from A. Leytem (april.leytem@usda.gov) and A. VanderZaag
        (andrew.vanderzaag@AGR.GC.CA). These bounds are also support by work from Genedy and Ogejo, 2021
        (https://doi.org/10.1016/j.compag.2021.106234) who observed similar minimum and maximum liquid manure
        temperatures in outdoor clay pit and concrete tank manure storages.
        """
        return float(np.clip(air_temperature, 0.0, 35.0))

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

    def _get_nitrous_oxide_emissions_factor(
        self, manure_treatment_type: ManureTreatmentType, manure_cover: str
    ) -> float:
        """
        Get the correct nitrous oxide emissions factor based on manure treatment type and cover.

        Parameters
        ----------
        manure_treatment_type : ManureTreatmentType
            The type of manure treatment.
        manure_cover : str
            The type of cover for the manure. Options are: cover, crust, no cover, and N/A.

        Returns
        -------
        float
            Nitrous oxide emission factor for different manure treatment and storage
            systems (kg N2O/kg manure N).
        """

        return GasEmissionConstants.NITROUS_OXIDE_EMISSION_FACTOR_KG_NITROUS_OXIDE_N_PER_KG_MANURE_N[
            manure_treatment_type
        ][manure_cover]

    def _get_current_day_average_temperature_celsius(self) -> float:
        """Returns the average temperature of the current day in Celsius.

        Returns:
            The average temperature of the current day in Celsius.

        """
        current_conditions = self.weather.get_current_day_conditions(self.time)
        return current_conditions.mean_air_temperature

    def _get_current_day_rainfall(self) -> float:
        """
        Return the rainfall of the current day in meters (m).

        Returns
        -------
        float
            The rainfall of the current day in meters (m).

        """
        current_conditions = self.weather.get_current_day_conditions(self.time)
        precipitation = current_conditions.precipitation
        return precipitation * GeneralConstants.MM_TO_M

    def _adjust_accumulated_output(self, manure_treatment_daily_output: ManureTreatmentDailyOutput) -> None:
        """Adjust the accumulated output by either resetting it or adding the daily output to it.

        Notes
        -----

        The accumulated output will be reset on the first day of every storage time period.

        Parameters
        ----------
        manure_treatment_daily_output : ManureTreatmentDailyOutput
            The daily output from the manure treatment system.

        """
        if self._sim_day % self.storage_time_period == 0:
            if self._accumulated_output.pen_id >= 0:
                ManureModuleOutputManagerHelper.add_dataclass_object(
                    self._accumulated_output,
                    info_maps={
                        "class": self.__class__.__name__,
                        "function": self._adjust_accumulated_output.__name__,
                        "prefix": f"{self.__class__.__name__}_emptying_amount_pen_"
                        f"{self._accumulated_output.pen_id}",
                        "simulation_day": self._sim_day,
                    },
                )
            self._accumulated_output = manure_treatment_daily_output.clone()
        else:
            self._accumulated_output += manure_treatment_daily_output

    @staticmethod
    def calculate_cover_and_flare_methane(methane_loss: float) -> tuple[float, float]:
        """
        Adjust the methane burned and lost when using cover and flare cover type.

        Parameters
        ----------
        methane_loss: float
            The amount of methane lost (kg).

        Returns
        -------
        tuple[float, float]
            The amount of storage methane burned and the adjusted methane loss (kg).

        """
        storage_methane_burned = (
            methane_loss * ManureConstants.METHANE_DESTRUCTION_EFFICIENCY * GeneralConstants.PERCENTAGE_TO_FRACTION
        )
        adjusted_methane_loss = methane_loss * (
            1 - ManureConstants.METHANE_DESTRUCTION_EFFICIENCY * GeneralConstants.PERCENTAGE_TO_FRACTION
        )
        return storage_methane_burned, adjusted_methane_loss
