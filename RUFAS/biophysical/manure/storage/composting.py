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
"""The upper bound temperature for determining MCF for windrow composting."""

MCF_COMPOSTING_WINDROW_LOW: float = 0.005
"""The MCF for windrow composting when the air temperature is below the lower bound temperature."""

MCF_COMPOSTING_WINDROW_MEDIUM: float = 0.01
"""The MCF for windrow composting when the air temperature is between the lower and upper bound temperature."""

MCF_COMPOSTING_WINDROW_HIGH: float = 0.015
"""The MCF for windrow composting when the air temperature is above the upper bound temperature."""

DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSD: float = 0.5
"""Default carbon content (percent by mass) of manure degradable volatile solids (unitless, [0, 1])."""

DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSND: float = 0.35
"""Default carbon content (percent by mass) of manure non-degradable volatile solids (unitless, [0, 1])."""

DEFAULT_EFFECT_OF_MOISTURE_ON_MICROBIAL_DECOMPOSITION: float = 0.65
"""The default effect of moisture on microbial decomposition."""

FIRST_ORDER_DECAYING_COEFFICIENT: float = 0.1
"""The first order decaying coefficient."""

DEFAULT_LAG_TIME: int = 2
"""Default lag time used in the calculation of the carbon decomposition rate (days). Default is set to 2."""

DEFAULT_DAYS_SINCE_LAST_TURNING: int = 1
"""Default days since the previous compost turning event (days). Default is set to 1."""

DEFAULT_MOLE_FRACTION_OF_OXYGEN: float = 0.15
"""The default mole fraction of oxygen in the air wihtin the compost layer."""

OXYGEN_HALF_SATURATION_CONSTANT: float = 0.02
"""The half saturation constant of Oxygen gas (O2)"""

AMBIENT_AIR_MOLE_FRACTION_OF_OXYGEN: float = 0.21
"""The mole fraction of oxygen in ambient air."""

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

EFFECTIVENESS_OF_MICROBIAL_DECOMPOSITION_RATE: float = 2.73e-3
"""
The rate of effectiveness of microbial decomposition.
"""

COMPOSTING_DECOMPOSITION_TEMPERATURE: float = 60.0
"""
The temperature of the inner compost layer at which microbial growth and decomposition is maximized (C).
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
    composting_type : str
        The type of the composting process being used.
    storage_time_period : int
        The storage time period.
    """

    def __init__(self, name: str, composting_type: str, storage_time_period: int):
        super().__init__(
            name=name,
            is_housing_emissions_calculator=False,
            cover=StorageCover.NO_COVER,
            storage_time_period=storage_time_period,
            surface_area=math.inf,
        )
        self._composting_type: CompostingType = CompostingType(composting_type)

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
        original_received_manure = copy(self._received_manure)
        self._manure_to_process = copy(self._received_manure)

        manure_temperature = current_day_conditions.mean_air_temperature
        storage_methane = self._calculate_composting_methane_emissions(
            manure_temperature, self._manure_to_process.non_degradable_volatile_solids, self._composting_type
        )
        carbon_decomposition = self._calculate_carbon_decomposition(
            manure_temperature,
            self._manure_to_process.non_degradable_volatile_solids,
            self._manure_to_process.degradable_volatile_solids,
        )
        self._apply_dry_matter_loss(storage_methane, carbon_decomposition)

        storage_nitrous_oxide_N = self._calculate_nitrous_oxide_emissions(
            FRACTION_NITROGEN_LOST_TO_DIRECT_N2O_EMISSION[self._composting_type],
            self._manure_to_process.nitrogen,
        )
        storage_N_loss_from_leaching = self._calculate_nitrogen_loss_to_leaching(
            FRACTION_NITROGEN_LOST_TO_LEACHING[self._composting_type], self._manure_to_process.nitrogen
        )
        storage_ammonia_N = self._calculate_composting_ammonia_emissions(
            self._composting_type, self._manure_to_process.nitrogen
        )
        self._apply_nitrogen_losses(storage_nitrous_oxide_N, storage_ammonia_N, storage_N_loss_from_leaching)

        self._received_manure = copy(self._manure_to_process)
        manure_to_return = super().process_manure(current_day_conditions, time)

        data_origin_function = self.process_manure.__name__
        simulation_day = time.simulation_day
        self._report_processor_output(
            "storage_methane", storage_methane, data_origin_function, MeasurementUnits.KILOGRAMS, simulation_day
        )
        self._report_processor_output(
            "storage_ammonia_N",
            storage_ammonia_N,
            data_origin_function,
            MeasurementUnits.KILOGRAMS,
            simulation_day,
        )
        self._report_processor_output(
            "storage_nitrous_oxide_N",
            storage_nitrous_oxide_N,
            data_origin_function,
            MeasurementUnits.KILOGRAMS,
            simulation_day,
        )
        self._report_processor_output(
            "storage_N_loss_from_leaching",
            storage_N_loss_from_leaching,
            data_origin_function,
            MeasurementUnits.KILOGRAMS,
            simulation_day,
        )
        self._report_processor_output(
            "carbon_decomposition",
            carbon_decomposition,
            data_origin_function,
            MeasurementUnits.KILOGRAMS,
            simulation_day,
        )
        self._report_manure_stream(self._stored_manure, "accumulated", simulation_day)
        self._report_manure_stream(original_received_manure, "received", simulation_day)

        return manure_to_return

    def _apply_dry_matter_loss(self, methane_emission: float, carbon_decomposition: float) -> None:
        """
        This function calculates and then applies the dry matter loss to the received manure in place.

        Parameters
        ----------
        methane_emission : float
            The methane emission of the current day, kg/day.
        carbon_decomposition : float
            The carbon decomposition of the current day, kg/day.

        Raises
        ------
        ValueError
            If any of the dry matter loss calculations results in negative values for received-manure
            non-degradable volatile solids, degradable volatile solids, or total solids.
        """
        dry_matter_loss = self._calculate_dry_matter_loss(methane_emission, carbon_decomposition)
        degradable_volatile_solids_fraction = self._calculate_degradable_volatile_solids_fraction()

        non_degradable_volatile_solids_after_losses = (
            self._manure_to_process.non_degradable_volatile_solids
            - dry_matter_loss * (1 - degradable_volatile_solids_fraction)
        )
        degradable_volatile_solids_after_losses = (
            self._manure_to_process.degradable_volatile_solids
            - dry_matter_loss * degradable_volatile_solids_fraction
        )
        total_solids_after_losses = self._manure_to_process.total_solids - dry_matter_loss

        errors = []
        if non_degradable_volatile_solids_after_losses < 0:
            errors.append("non_degradable_volatile_solids")
        if degradable_volatile_solids_after_losses < 0:
            errors.append("degradable_volatile_solids")
        if total_solids_after_losses < 0:
            errors.append("total_solids")

        if errors:
            error_message = (
                f"Dry-matter loss calculations resulted in negative received-manure values for: {', '.join(errors)}."
            )
            self._om.add_error(
                "Dry-matter loss application error",
                error_message,
                info_map={
                    "class": self.__class__.__name__,
                    "function": self._apply_dry_matter_loss.__name__,
                },
            )
            raise ValueError(error_message)

        self._manure_to_process.non_degradable_volatile_solids = non_degradable_volatile_solids_after_losses
        self._manure_to_process.degradable_volatile_solids = degradable_volatile_solids_after_losses
        self._manure_to_process.total_solids = total_solids_after_losses

    def _calculate_degradable_volatile_solids_fraction(self) -> float:
        """
        This function calculates the degradable volatile solids fraction of the current day's received manure.

        Returns
        -------
        float
            The degradable volatile solids fraction of the current day, unitless.
        """
        degradable_volatile_solids_fraction = (
            self._manure_to_process.degradable_volatile_solids / self._manure_to_process.total_volatile_solids
        )
        return degradable_volatile_solids_fraction

    def _apply_nitrogen_losses(
        self, storage_nitrous_oxide_N: float, storage_ammonia_N: float, storage_N_loss_from_leaching: float
    ) -> None:
        """
        This function applies the nitrogen losses to the received manure in place.

        Parameters
        ----------
        storage_nitrous_oxide_N : float
            The nitrogen loss through nitrous oxide emissions of the current day, kg.
        storage_ammonia_N : float
            The nitrogen loss through ammonia emissions of the current day, kg.
        storage_N_loss_from_leaching : float
            The nitrogen loss through leaching of the current day, kg.

        Raises
        ------
        ValueError
            If the total nitrogen losses are greater than the total received manure nitrogen.
        """
        received_manure_nitrogen_after_losses = (
            self._manure_to_process.nitrogen
            - storage_nitrous_oxide_N
            - storage_ammonia_N
            - storage_N_loss_from_leaching
        )
        if received_manure_nitrogen_after_losses < 0:
            self._om.add_error(
                "Nitrogen loss application error",
                "Cannot have total nitrogen losses greater than total received manure nitrogen.",
                info_map={"class": self.__class__.__name__, "function": self._apply_nitrogen_losses.__name__},
            )
            raise ValueError(
                "Nitrogen loss application error: cannot have total nitrogen losses greater than "
                "total received manure nitrogen."
            )

        self._manure_to_process.nitrogen = received_manure_nitrogen_after_losses

    @staticmethod
    def _calculate_composting_ammonia_emissions(composting_type: CompostingType, received_manure_nitrogen: float
                                                ) -> float:
        """
        This function calculates the total nitrogen loss to ammonia emission of the current day.

        Parameters
        ----------
        composting_type : CompostingType
            The type of composting being used.
        received_manure_nitrogen : float
            The nitrogen content of the received manure, kg.

        Returns
        -------
        float
            The total nitrogen loss to ammonia emission of the current day, kg.
        """
        return FRACTION_NITROGEN_LOST_TO_AMMONIA_EMISSION[composting_type] * received_manure_nitrogen

    @staticmethod
    def _calculate_nitrogen_loss_to_leaching(leaching_fraction: float, received_manure_nitrogen: float) -> float:
        """
        This function calculates the amount of nitrogen leached out of the manure-bedding
        pile of the current day.

        Parameters
        ----------
        leaching_fraction : float
            The fraction of nitrogen lost to leaching, unitless.
        received_manure_nitrogen : float
            The nitrogen content of the received manure, kg.

        Returns
        -------
        float
            The total nitrogen loss to leaching of the current day, kg.
        """

        return leaching_fraction * received_manure_nitrogen

    @staticmethod
    def _calculate_composting_methane_emissions(
        manure_temperature: float, manure_volatile_solids: float, composting_type: CompostingType
    ) -> float:
        """
        This function calculates the composting solid manure methane emission of the current day.

        Parameters
        ----------
        manure_temperature : float
            The manure temperature of the current day, Celsius.
        manure_volatile_solids : float
            The manure volatile solids of the received manure, kg.
        composting_type : CompostingType
            The type of composting being used.

        Returns
        -------
        float
            The solid manure methane emission of the current day, kg/day.
        """
        methane_conversion_factor = Composting._calculate_methane_conversion_factor(manure_temperature, composting_type)
        return (manure_volatile_solids) * (ACHIEVABLE_METHANE_EMISSION * 0.67 * methane_conversion_factor)

    @staticmethod
    def _calculate_methane_conversion_factor(manure_temperature: float, composting_type: CompostingType) -> float:
        """
        This function returns the methane conversion factor depending on the composting type and the temperature.
        TODO issue #2307, update MCF determination method post-refresh.

        Parameters
        ----------
        manure_temperature : float
            The manure temperature of the current day, Celsius.
        composting_type : CompostingType
            The type of composting being used.

        Returns
        -------
        float
            The methane conversion factor, unitless.
        """
        if composting_type == CompostingType.STATIC_PILE:
            return MCF_COMPOSTING_STATIC_PILE
        else:
            if manure_temperature < MCF_LOWER_BOUND_TEMPERATURE:
                return MCF_COMPOSTING_WINDROW_LOW
            elif 15 <= manure_temperature <= MCF_UPPER_BOUND_TEMPERATURE:
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

    @staticmethod
    def _calculate_carbon_decomposition(
        manure_temperature: float, non_degradable_volatile_solids: float, degradable_volatile_solids: float
    ) -> float:
        """
        This function calculates the total carbon decomposition of the current day.

        Parameters
        ----------
        manure_temperature : float
            The manure temperature of the current day, Celsius.
        non_degradable_volatile_solids : float
            The non-degradable volatile solids of the current day, kg.
        degradable_volatile_solids : float
            The degradable volatile solids of the current day, kg.

        Returns
        -------
        float
            The total carbon decomposition of the current day, kg/day.
        """
        carbon_decomposition_rate = Composting._calculate_carbon_decomposition_rate(manure_temperature)
        anaerobic_coefficient = Composting._calculate_anaerobic_coefficient()

        return (
            (
                degradable_volatile_solids * DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSD
                + non_degradable_volatile_solids * DEFAULT_CARBON_FRACTION_AVAILABLE_IN_VSND
            )
            * carbon_decomposition_rate
            * DEFAULT_EFFECT_OF_MOISTURE_ON_MICROBIAL_DECOMPOSITION
            * anaerobic_coefficient
        )

    @staticmethod
    def _calculate_carbon_decomposition_rate(manure_temperature: float) -> float:
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
        max_microbial_decomposition_rate = Composting._calculate_max_microbial_decomposition_rate()
        slow_microbial_decomposition_rate = Composting._calculate_slow_fraction_decomposition_rate(manure_temperature)

        return float(
            (
                (max_microbial_decomposition_rate - slow_microbial_decomposition_rate)
                * (
                    math.e
                    ** (FIRST_ORDER_DECAYING_COEFFICIENT * (DEFAULT_DAYS_SINCE_LAST_TURNING - DEFAULT_LAG_TIME))
                )
                * slow_microbial_decomposition_rate
            )
        )

    @staticmethod
    def _calculate_max_microbial_decomposition_rate() -> float:
        """
        This function calculates the max microbial decomposition rate.
        This parameter is set to 0.04195 but the equation and set values are shown below for reference.

        Returns
        -------
        float
            The max microbial decomposition rate of the current day, per day.
        """

        return float(
            EFFECTIVENESS_OF_MICROBIAL_DECOMPOSITION_RATE
            * (
                1.066 ** (COMPOSTING_DECOMPOSITION_TEMPERATURE - 10)
                - 1.21 ** (COMPOSTING_DECOMPOSITION_TEMPERATURE - 50)
            )
        )

    @staticmethod
    def _calculate_slow_fraction_decomposition_rate(manure_temperature: float) -> float:
        """
        This function calculates the microbial decomposition rate of the slowly-degrading fraction
        in compost of the current day.

        Parameters
        ----------
        manure_temperature : float
            The manure temperature of the current day, Celsius.

        Returns
        -------
        float
            The slow microbial decomposition rate of the current day, per day.
        """

        return float(
            EFFECTIVENESS_OF_MICROBIAL_DECOMPOSITION_RATE
            * (1.066 ** (manure_temperature - 10) - 1.21 ** (manure_temperature - 50))
        )

    @staticmethod
    def _calculate_anaerobic_coefficient() -> float:
        """
        This function calculates the anaerobic coefficient. The value of this parameter is equal to 0.91270,
        but the equation and set values are included below for reference.

        Returns
        -------
        float
            The anaerobic coefficient, unitless.
        """
        return (
            DEFAULT_MOLE_FRACTION_OF_OXYGEN / (OXYGEN_HALF_SATURATION_CONSTANT + DEFAULT_MOLE_FRACTION_OF_OXYGEN)
        ) * (
            (OXYGEN_HALF_SATURATION_CONSTANT + AMBIENT_AIR_MOLE_FRACTION_OF_OXYGEN)
            / AMBIENT_AIR_MOLE_FRACTION_OF_OXYGEN
        )
