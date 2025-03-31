from copy import copy
from enum import Enum
import math
from RUFAS.biophysical.manure.storage.storage import Storage
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.time import Time
from RUFAS.units import MeasurementUnits


class CompostingType(Enum):
    """
    This is an Enum class that represents different types of composting.

    Attribute
    ----------
    INTENSIVE_WINDROW : str
        Intensive windrow.
    PASSIVE_WINDROW : str
        Passive windrow.
    STATIC_PILE: str
        Static pile.

    """

    INTENSIVE_WINDROW = "intensive windrow"
    PASSIVE_WINDROW = "passive windrow"
    STATIC_PILE = "static pile"


ACHIEVABLE_METHANE_EMISSION: float = 0.24
"""Achievable emission of methane from dairy manure (m^3 methane / kg volatile solids)."""

MCF_COMPOSTING_STATIC_PILE: float = 0.005
"""The MCF for static pile composting."""

MCF_LOWER_BOUND_TEMPERATURE: float = 15.0
"""The lower bound temperature for determining MCF for windrow composting."""

MCF_UPPER_BOUND_TEMPERATURE: float = 25.0
"""The lower bound temperature for determining MCF for windrow composting."""

MCF_COMPOSTING_WINDROW_LOW: float = 0.005
"""The MCF for windrow composting when the air temperature is below the lower bound temperature."""

MCF_COMPOSTING_WINDROW_MEDIUM: float = 0.01
"""The MCF for windrow composting when the air temperature is between the lower and upper bound temperature."""

MCF_COMPOSTING_WINDROW_HIGH: float = 0.015
"""The MCF for windrow composting when the air temperature is above the upper bound temperature."""

DEFAULT_CARBON_FRACTION_AVAILABLE_IN_MANURE: float = 0.5
"""Default proportion of carbon available in manure, (unitless, [0, 1]). Default is set to 0.5."""

DEFAULT_CARBON_FRACTION_AVAILABLE_IN_BEDDING: float = 0.35
"""Default proportion of carbon available in bedding, (unitless, [0, 1]). Default is set to 0.35."""

DEFAULT_EFFECT_OF_MOISTURE_ON_MICROBIAL_DECOMPOSITION: float = 0.65
"""The default effect of moisture on microbial decomposition."""

DEFAULT_FIRST_ORDER_DECAYING_COEFFICIENT: float = 0.1
"""The default first order decaying coefficient."""

DEFAULT_LAG_TIME: int = 2
"""Default lag time used in the calculation of the carbon decomposition rate (days). Default is set to 2."""

DEFAULT_MOLE_FRACTION_OF_OXYGEN: float = 0.15
"""The default mole fraction of Oxygen."""

OXYGEN_HALF_SATURATION_CONSTANT: float = 0.02
"""The half saturation constant of Oxygen gas (O2)"""

DEFAULT_AMBIENT_AIR_MOLE_FRACTION_OF_OXYGEN: float = 0.21
"""The default ambient air mole fraction of Oxygen."""

FRACTION_NITROGEN_LOST_TO_AMMONIA_EMISSION: dict[CompostingType, float] = {
    CompostingType.STATIC_PILE: 0.5,
    CompostingType.PASSIVE_WINDROW: 0.45,
    CompostingType.INTENSIVE_WINDROW: 0.5,
}

FRACTION_NITROGEN_LOST_TO_DIRECT_N2O_EMISSION: dict[CompostingType, float] = {
    CompostingType.STATIC_PILE: 0.06,
    CompostingType.PASSIVE_WINDROW: 0.04,
    CompostingType.INTENSIVE_WINDROW: 0.06,
}

FRACTION_NITROGEN_LOST_TO_LEACHING: dict[CompostingType, float] = {
    CompostingType.STATIC_PILE: 0.06,
    CompostingType.PASSIVE_WINDROW: 0.04,
    CompostingType.INTENSIVE_WINDROW: 0.06,
}

DEFAULT_EFFECTIVENESS_OF_MICROBIAL_DECOMPOSITION_RATE: float = 2.73e-3
"""
The default effectiveness of microbial decomposition rate.
"""

DEFAULT_COMPOSTING_DECOMPOSITION_TEMPERATURE: float = 60.0
"""
The default decomposition temperature for composting.
"""


class Composting(Storage):
    """
    Class for managing and simulating the composting process of manure treatment.

    This class simulates the composting process by considering various factors like weather,
    manure characteristics, and composting configurations. It provides methods for daily
    update of compost characteristics such as methane emissions, nitrogen content, and
    carbon decomposition. The calculations are based on standard composting models and
    environmental factors.

    Parameters
    ----------
    name : str
        The name of the storage.
    type : str
        The type of the composting process being used.
    storage_time_period : int
        The storage time period.
    """

    def __init__(
        self,
        name: str,
        type: str,
        storage_time_period: int,
    ):
        super().__init__(
            name=name,
            type=type,
            is_housing_emissions_calculator=False,
            cover=StorageCover.NO_COVER,
            storage_time_period=storage_time_period,
        )
        self._composting_type: CompostingType = CompostingType(type)

    def process_manure(self, current_day_conditions: CurrentDayConditions, time: Time) -> dict[str, ManureStream]:
        """Processes manure in Composting.

        Parameters
        ----------
        current_day_conditions : CurrentDayConditions
            The current day conditions.
        time : Time
            The time.

        Returns
        -------
        dict[str, ManureStream]
            _The processed manure stream.
        """
        self._manure_to_process = copy(self._received_manure)

        manure_temperature = self._determine_outdoor_storage_temperature(
            air_temperature=current_day_conditions.mean_air_temperature
        )
        storage_methane = self._calculate_methane_emissions(manure_temperature)
        storage_ammonia_N = self._apply_ammonia_emissions()
        storage_nitrous_oxide_N = self._apply_nitrous_oxide_emissions()
        storage_N_loss_from_leaching = self._calculate_nitrogen_loss_to_leaching()

        self._received_manure = copy(self._manure_to_process)
        manure_to_return = super().process_manure(current_day_conditions, time)

        carbon_decomposition = self._calculate_carbon_decomposition(manure_temperature)
        self._apply_dry_matter_loss(storage_methane, carbon_decomposition)

        data_origin_function = self.process_manure.__name__
        self._report_processor_output("storage_methane", storage_methane, data_origin_function,
                                      MeasurementUnits.KILOGRAMS, time.simulation_day)
        self._report_processor_output("storage_ammonia_N", storage_ammonia_N, data_origin_function,
                                      MeasurementUnits.KILOGRAMS, time.simulation_day)
        self._report_processor_output(
            "storage_nitrous_oxide_N", storage_nitrous_oxide_N, data_origin_function, MeasurementUnits.KILOGRAMS,
            time.simulation_day
        )
        self._report_processor_output(
            "storage_N_loss_from_leaching", storage_N_loss_from_leaching, data_origin_function,
            MeasurementUnits.KILOGRAMS, time.simulation_day
        )
        self._report_processor_output(
            "carbon_decomposition", carbon_decomposition, data_origin_function, MeasurementUnits.KILOGRAMS,
            time.simulation_day
        )
        self._report_manure_stream(self._stored_manure, "accumulated", time)
        self._report_manure_stream(self._received_manure, "received", time)

        return manure_to_return

    def _apply_dry_matter_loss(self, methane_emission: float, carbon_decomposition: float) -> None:
        """
        This function applies the dry matter loss to the stored manure in place.

        Parameters
        ----------
        methane_emission : float
            The methane emission of the current day, kg/day.
        carbon_decomposition : float
            The carbon decomposition of the current day, kg/day.
        """
        dry_matter_loss = self._calculate_dry_matter_loss(methane_emission, carbon_decomposition)
        degradable_volatile_solids_fraction = self._calculate_degradable_volatile_solids_fraction()
        self._stored_manure.non_degradable_volatile_solids -= dry_matter_loss * degradable_volatile_solids_fraction
        self._stored_manure.total_degradable_volatile_solids -= dry_matter_loss * (
            1 - degradable_volatile_solids_fraction
        )
        self._stored_manure.total_solids -= dry_matter_loss

    def _calculate_degradable_volatile_solids_fraction(self) -> float:
        """
        This function calculates the degradable volatile solids fraction of the current day.

        Returns
        -------
        float
            The degradable volatile solids fraction of the current day, unitless.
        """
        degradable_volatile_solids_fraction = (
            self._manure_to_process.degradable_volatile_solids / self._manure_to_process.total_volatile_solids
        )
        return degradable_volatile_solids_fraction

    def _calculate_nitrogen_loss_to_leaching(self) -> float:
        """
        This function calculates the amount of nitrogen leached out of the manure-bedding
        pile of the current day.

        Returns
        -------
        float
            The total nitrogen loss to Leaching of the current day, kg.
        """
        fraction_nitrogen_lost_as_ammonia = FRACTION_NITROGEN_LOST_TO_LEACHING[self._composting_type]

        return fraction_nitrogen_lost_as_ammonia * self._manure_to_process.nitrogen

    def _apply_nitrous_oxide_emissions(self) -> float:
        """
        This function calculates the amount of nitrogen loss through direct nitrous oxide emissions
        of the current day.

        Returns
        -------
        float
            The total nitrogen loss through direct nitrous oxide emissions of the current day, kg.
        """
        fraction_nitrogen_lost_as_ammonia = FRACTION_NITROGEN_LOST_TO_DIRECT_N2O_EMISSION[self._composting_type]

        storage_nitrous_oxide_N = fraction_nitrogen_lost_as_ammonia * self._manure_to_process.nitrogen * 44 / 28
        self._manure_to_process.nitrogen -= storage_nitrous_oxide_N
        return storage_nitrous_oxide_N

    def _apply_ammonia_emissions(self) -> float:
        """
        This function calculates the total nitrogen loss to ammonia emission of the current day.

        Returns
        -------
        float
            The total nitrogen loss to methane emission of the current day, kg.
        """
        fraction_nitrogen_lost_as_ammonia = FRACTION_NITROGEN_LOST_TO_AMMONIA_EMISSION[self._composting_type]
        storage_ammonia_N = fraction_nitrogen_lost_as_ammonia * self._manure_to_process.nitrogen
        self._manure_to_process.ammoniacal_nitrogen -= storage_ammonia_N
        return storage_ammonia_N

    def _calculate_methane_emissions(self, manure_temperature: float) -> float:
        """
        This function calculates the solid manure methane emission of the current day.

        Parameters
        ----------
        manure_temperature : float
            The manure temperature of the current day, Celsius.

        Returns
        -------
        float
            The solid manure methane emission of the current day, kg/day.
        """
        manure_volatile_solids = self._manure_to_process.total_volatile_solids
        methane_conversion_factor = self._calculate_methane_conversion_factor(manure_temperature)
        return (manure_volatile_solids) * (ACHIEVABLE_METHANE_EMISSION * 0.67 * methane_conversion_factor)

    def _calculate_methane_conversion_factor(self, manure_temperature: float) -> float:
        """
        This function returns the methane conversion factor depending on the composting type and the temperature.

        Parameters
        ----------
        manure_temperature : float
            The manure temperature of the current day, Celsius.

        Returns
        -------
        float
            The methane conversion factor, unitless.
        """
        if self._composting_type == CompostingType.STATIC_PILE:
            return MCF_COMPOSTING_STATIC_PILE
        else:
            current_day_mean_air_temperature = \
                self._determine_outdoor_storage_temperature(air_temperature=manure_temperature)
            if current_day_mean_air_temperature < MCF_LOWER_BOUND_TEMPERATURE:
                return MCF_COMPOSTING_WINDROW_LOW
            elif 15 <= current_day_mean_air_temperature <= MCF_UPPER_BOUND_TEMPERATURE:
                return MCF_COMPOSTING_WINDROW_MEDIUM
            else:
                return MCF_COMPOSTING_WINDROW_HIGH

    @staticmethod
    def _calculate_dry_matter_loss(methane_emission: float, carbon_decomposition: float) -> float:
        """
        This function calculates the total dry matter loss of the current day.

        Returns
        -------
        float
            The total dry matter loss of the current day, kg/day.
        """
        return 2 * carbon_decomposition + methane_emission

    def _calculate_carbon_decomposition(self, manure_temperature: float) -> float:
        """
        This function calculates the total carbon decomposition of the current day.

        Parameters
        ----------
        manure_temperature : float
            The manure temperature of the current day, Celsius.

        Returns
        -------
        float
            The total carbon decomposition of the current day, kg/day.
        """
        c_manure = DEFAULT_CARBON_FRACTION_AVAILABLE_IN_MANURE
        c_bedding = DEFAULT_CARBON_FRACTION_AVAILABLE_IN_BEDDING
        effect_moist = DEFAULT_EFFECT_OF_MOISTURE_ON_MICROBIAL_DECOMPOSITION

        q_bedding = self._manure_handler_daily_output.total_bedding_mass

        carbon_decomposition_rate = self._calculate_carbon_decomposition_rate(manure_temperature)
        anaerobic_coefficient = self._calculate_anaerobic_coefficient()

        return (
            (self._manure_to_process.total_solids * c_manure + q_bedding * c_bedding)
            * carbon_decomposition_rate
            * effect_moist
            * anaerobic_coefficient
        )

    def _calculate_carbon_decomposition_rate(self, manure_temperature: float) -> float:
        """
        This function calculates the carbon decomposition rate of the current day.

        Parameters
        ----------
        manure_temperature : float
            The manure temperature of the current day, Celsius.

        Returns
        -------
        float
            The carbon decomposition rate of the current day, per day.
        """
        max_microbial_decomposition_rate = self._calculate_max_microbial_decomposition_rate()
        slow_microbial_decomposition_rate = self._calculate_slow_microbial_decomposition_rate(manure_temperature)

        decay = DEFAULT_FIRST_ORDER_DECAYING_COEFFICIENT
        last_turning_or_addition = self.config.last_compost_turning_or_addition
        lag = DEFAULT_LAG_TIME

        return (
            (max_microbial_decomposition_rate - slow_microbial_decomposition_rate)
            * (math.e ** (decay * (last_turning_or_addition - lag)))
            * slow_microbial_decomposition_rate
        )

    @staticmethod
    def _calculate_max_microbial_decomposition_rate() -> float:
        """
        This function calculates the max microbial decomposition rate of the current day.

        Returns
        -------
        float
            The max microbial decomposition rate of the current day, per day.
        """
        effectiveness_of_microbial_decomposition_rate = (
            DEFAULT_EFFECTIVENESS_OF_MICROBIAL_DECOMPOSITION_RATE
        )
        decomposition_temperature = DEFAULT_COMPOSTING_DECOMPOSITION_TEMPERATURE

        return effectiveness_of_microbial_decomposition_rate * (
            1.066 ** (decomposition_temperature - 10) - 1.21 ** (decomposition_temperature - 50)
        )

    def _calculate_slow_microbial_decomposition_rate(self, manure_temperature: float) -> float:
        """
        This function calculates the slow microbial decomposition rate of the current day.

        Parameters
        ----------
        manure_temperature : float
            The manure temperature of the current day, Celsius.

        Returns
        -------
        float
            The slow microbial decomposition rate of the current day, per day.
        """
        effectiveness_of_microbial_decomposition_rate = (
            DEFAULT_EFFECTIVENESS_OF_MICROBIAL_DECOMPOSITION_RATE
        )

        return effectiveness_of_microbial_decomposition_rate * (
            1.066 ** (manure_temperature - 10) - 1.21 ** (manure_temperature - 50)
        )

    @staticmethod
    def _calculate_anaerobic_coefficient() -> float:
        """
        This function calculates the anaerobic coefficient.

        Returns
        -------
        float
            The anaerobic coefficient, unitless.
        """
        mole_fraction_of_oxygen = DEFAULT_MOLE_FRACTION_OF_OXYGEN
        oxygen_half_saturation = OXYGEN_HALF_SATURATION_CONSTANT
        ambient_air_mole_fraction_of_oxygen = DEFAULT_AMBIENT_AIR_MOLE_FRACTION_OF_OXYGEN

        return (mole_fraction_of_oxygen / (oxygen_half_saturation + mole_fraction_of_oxygen)) * (
            (oxygen_half_saturation + ambient_air_mole_fraction_of_oxygen) / ambient_air_mole_fraction_of_oxygen
        )
