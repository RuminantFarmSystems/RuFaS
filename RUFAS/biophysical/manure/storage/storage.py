import math
from dataclasses import replace
from math import inf
from numpy import exp

from RUFAS.biophysical.manure.processor import Processor
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.general_constants import GeneralConstants
from RUFAS.input_manager import InputManager
from RUFAS.rufas_time import RufasTime
from RUFAS.user_constants import UserConstants
from RUFAS.util import Utility

from .storage_cover import StorageCover
from ..manure_constants import ManureConstants

MANURE_CONVERSION_CONSTANT = 0.1175
"""Factor to estimate m^3 of herd-wide manure produced per day per mature cow housed on the farm (m^3/day)."""

FREEBOARD_CONSTANT = 1.20
"""Represents 20% volume allowance above the maximum volume of a slurry or liquid manure storage (unitless)."""

DEPTH_CONSTANT = 4.572
"""Value for slurry or liquid manure storage depth (m)."""

PRECIPITATION_CONSTANT = 0.25
"""The annual precipitation constant value (m)."""


class Storage(Processor):
    """
    Base manure Storage class.

    Parameters
    ----------
    cover : str
        What the storage will be covered with, if anything.
    storage_time_period : int | None
        How long manure is stored for before emptying the storage (days). None if the storage is never emptied.
    surface_area : float
        The surface area of the manure storage (m^2).
    capacity : float, default math.inf
        Volumetric capacity of the storage (m^3).

    Attributes
    ----------
    _received_manure : ManureStream
        The total amount of manure received by a storage in a single day.
    stored_manure : ManureStream
        The current amount of manure currently held by the storage.
    _capacity : float
        The volumetric capacity of the storage (m^3).
    _cover : StorageCover
        The cover of the storage.
    _storage_time_period : int | None
        Interval between emptyings of the storage (days). If the storage is never emptied, this is None.
    _surface_area : float
        Surface area of the manure storage (m^2).
    _manure_to_process : ManureStream
        The manure that is processed during the `process_manure()` method call.
    intercept_mean_temp : float
        The intercept mean temperature calculate from linest function.
    phase_shift : float
        Temperature phase shift of the weather data.
    amplitude : float
        The temperature amplitude of the weather data.

    """

    def __init__(
        self,
        name: str,
        is_housing_emissions_calculator: bool,
        cover: str | StorageCover,
        storage_time_period: int | None,
        surface_area: float,
        capacity: float = inf,
    ) -> None:
        """Initializes a manure Storage."""
        super().__init__(name, is_housing_emissions_calculator)
        self._received_manure = ManureStream.make_empty_manure_stream()
        self.stored_manure = ManureStream.make_empty_manure_stream()
        self._capacity = capacity
        self._cover = StorageCover(cover)
        self._storage_time_period = storage_time_period
        self._surface_area = surface_area
        self._manure_to_process = ManureStream.make_empty_manure_stream()
        self.__post_init__()

        self.intercept_mean_temp: float | None = None
        self.phase_shift: float | None = None
        self.amplitude: float | None = None

    def __post_init__(self) -> None:
        """
        Post-initialization method to calculate the surface area of the storage.
        """
        if self._surface_area is None:
            self._calculate_surface_area()

    @property
    def is_overflowing(self) -> bool:
        """True if the manure in storage exceeds the storage's volumetric capacity, else False."""
        return self.stored_manure.volume > self._capacity

    @property
    def _emptying_fraction(self) -> float:
        """
        The fraction of the accumulated stored manure that is removed from storage when the emptying time is reached.
        Defaults to 1.0.
        """
        return 1.0

    def _determine_outdoor_storage_temperature(
        self,
        simulation_day: int,
        minimum_manure_temperature: float,
    ) -> float:
        """
        Determines the temperature of the manure in outdoor liquid and slurry storages.

        Parameters
        ----------
        simulation_day : int
            Current julian day of the year.
        minimum_manure_temperature : float
            The minimum temperature of the manure in storage (°C).

        Returns
        -------
        float
            The estimated temperature of the manure storage (°C).

        Notes
        -----
        This function determines daily temperature of manure in liquid storage by fitting a sin/cos function. Several
        parameters of this function are derived and utilized here. The amplitude of simulation-wide average air
        temperature data, which is derived by least squares fitting cos and sin waves to temperature data, is adjusted
        by a fixed damping factor to reflect the smaller degree of annual variation in temperature compared to air
        temperature. The phase shift (time of peak of annual temperature) is also determined from simulation weather
        data and is adjusted to reflect the time of manure temperature change based on a fixed lag constant.

        """
        if self.amplitude and self.intercept_mean_temp and self.phase_shift:
            manure_amplitude = self.amplitude * ManureConstants.MANURE_DAMPING_FACTOR
            estimated_temperature = self.intercept_mean_temp + manure_amplitude * math.cos(
                2 * math.pi / 365 * (simulation_day - self.phase_shift - ManureConstants.MANURE_TEMPERATURE_LAG)
            )
            return max(minimum_manure_temperature, estimated_temperature)
        else:
            raise ValueError("No data for outdoor storage temperature calculations.")

    def _calculate_surface_area(self) -> None:
        """
        Calculates the surface area of the storage.
        """
        cow_num = InputManager().get_data("animal.herd_information.cow_num")
        self._surface_area = (cow_num * MANURE_CONVERSION_CONSTANT * self._storage_time_period * FREEBOARD_CONSTANT) / (
            DEPTH_CONSTANT - PRECIPITATION_CONSTANT
        )

    def receive_manure(self, manure: ManureStream) -> None:
        """Receives manure and puts it in storage to be processed."""
        is_compatible_manure = self.check_manure_stream_compatibility(manure)
        if not is_compatible_manure:
            info_map = {
                "class": self.__class__.__name__,
                "function": self.receive_manure.__name__,
                "processor_name": self.name,
                "manure_stream": manure,
            }
            if self.is_housing_emissions_calculator and not manure.pen_manure_data:
                error_message = (
                    f"Processor '{self.name}' received a ManureStream without pen manure data, "
                    "which is required for housing emissions calculations. Cannot place a handler "
                    "before Open Lot/Bedded Pack in the manure processor connection chain."
                )
            else:
                error_message = f"Processor '{self.name}' received an incompatible ManureStream."
            self._om.add_error("invalid_manure_stream", error_message, info_map)
            raise ValueError(error_message)

        self._received_manure += manure

    def process_manure(self, _: CurrentDayConditions, time: RufasTime) -> dict[str, ManureStream]:
        """
        Adds the manure received on the current day to the manure already stored, and empties the storage if scheduled.
        """
        self.stored_manure += self._received_manure
        self._received_manure = ManureStream.make_empty_manure_stream()

        is_emptying_day = (
            self._storage_time_period is not None and (time.simulation_day + 1) % self._storage_time_period == 0
        )
        if not is_emptying_day:
            empty_stream = ManureStream.make_empty_manure_stream()
            self._report_manure_stream(empty_stream, "emptied", time.simulation_day)
            manure_to_be_returned = {}
        else:
            self._validate_emptying_fraction()
            if 0.0 < self._emptying_fraction < 1.0:
                emptied_stream = self.stored_manure.split_stream(self._emptying_fraction)
                retained_stream = self.stored_manure.split_stream(1.0 - self._emptying_fraction)
                self._report_manure_stream(emptied_stream, "emptied", time.simulation_day)
                self.stored_manure = retained_stream
                manure_to_be_returned = {"manure": replace(self.stored_manure)}
            elif self._emptying_fraction == 0.0:
                empty_stream = ManureStream.make_empty_manure_stream()
                self._report_manure_stream(empty_stream, "emptied", time.simulation_day)
                manure_to_be_returned = {}
            else:
                self._report_manure_stream(self.stored_manure, "emptied", time.simulation_day)
                manure_to_be_returned = {"manure": replace(self.stored_manure)}
                self.stored_manure = ManureStream.make_empty_manure_stream()

        if self.is_overflowing is True:
            self.handle_overflowing_manure(time)

        return manure_to_be_returned

    def _validate_emptying_fraction(self) -> None:
        """Validates that the emptying fraction is between 0.0 and 1.0."""
        if not 0.0 <= self._emptying_fraction <= 1.0:
            info_map = {
                "class": self.__class__.__name__,
                "function": self.process_manure.__name__,
                "processor_name": self.name,
            }
            error_message = (
                f"Processor '{self.name}' has an invalid emptying fraction of {self._emptying_fraction}. "
                "The emptying fraction must be between 0.0 and 1.0. Check retention constants if applicable."
            )
            self._om.add_error("Invalid Emptying Fraction", error_message, info_map)
            raise ValueError(error_message)

    def handle_overflowing_manure(self, time: RufasTime) -> None:
        """
        Deals with excess manure when amount in storage exceeds capacity.

        Parameters
        ----------
        time : RufasTime
            RufasTime instance tracking the current time of the simulation.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.handle_overflowing_manure.__name__,
            "prefix": self._prefix,
            "simulation_day": time.simulation_day,
        }
        self._om.add_warning(f"Manure storage '{self.name}' is overflowing!", "Handling excess manure", info_map)

    @staticmethod
    def _calculate_methane_emissions(volatile_solids: float, manure_temperature: float, is_degradable: bool) -> float:
        """
        Calculates methane that is emitted from liquid manure storages by calculating emissions from the degradable and
        non-degradable volatile solids fractions.

        Parameters
        ----------
        volatile_solids : float
            Mass of volatile solids that are emitting methane (kg). Can be degradable or non-degradable.
        manure_temperature : float
            Temperature of the manure in storage (degrees C).
        is_degradable : bool
            True if the volatile solids are degrdable, otherwise false.

        Returns
        -------
        float
            Methane emission from volatile solids (kg).

        """

        arrhenius_exponent = Storage._calculate_arrhenius_exponent(manure_temperature)

        if is_degradable:
            rate_correcting_factor = ManureConstants.DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR
        else:
            rate_correcting_factor = ManureConstants.NON_DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR

        methane_emissions = (
            GeneralConstants.HOURS_PER_DAY
            * arrhenius_exponent
            * volatile_solids
            * rate_correcting_factor
            * GeneralConstants.GRAMS_TO_KG
        )

        return methane_emissions

    @staticmethod
    def _calculate_arrhenius_exponent(temperature: float) -> float:
        """
        Calculate the Arrhenius exponent.

        Parameters
        ----------
        temperature : float
            Temperature in Celsius (degrees C).

        Returns
        -------
        float
            Arrhenius exponent (unitless).

        Raises
        ------
        ValueError
            If the temperature is not between -40 and 60 degrees Celsius.

        """
        is_temp_invalid: bool = not (
            UserConstants.GENERAL_LOWER_BOUND_TEMPERATURE
            <= temperature
            <= UserConstants.GENERAL_UPPER_BOUND_TEMPERATURE
        )
        if is_temp_invalid:
            raise ValueError(
                f"Temperature must be between -40 and 60 degrees Celsius. Temperature provided: {temperature}"
            )

        temp_kelvin = Utility.convert_celsius_to_kelvin(temperature)
        return float(
            exp(
                ManureConstants.NATURAL_LOG_ARRHENIUS_CONSTANT
                - (ManureConstants.ACTIVATION_ENERGY / (GeneralConstants.GAS_CONSTANT * temp_kelvin))
            )
        )

    @staticmethod
    def _calculate_cover_and_flare_methane(methane_loss: float) -> tuple[float, float]:
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
        adjusted_methane_loss = methane_loss - storage_methane_burned
        return storage_methane_burned, adjusted_methane_loss

    @staticmethod
    def _calculate_nitrous_oxide_emissions(nitrous_oxide_emissions_factor: float, nitrogen_added: float) -> float:
        """
        Calculates amount of nitrous oxide nitrogen emitted from a storage on a single day.

        Parameters
        ----------
        nitrous_oxide_emissions_factor : float
            The emission factor for nitrous oxide (kg nitrous oxide nitrogen / kg nitrogen).
        nitrogen_added: float
            Amount of nitrogen that was added to the storage on the current day (kg).

        Returns
        -------
        float
            Nitrous oxide nitrogen emissions (kg).

        """

        return nitrous_oxide_emissions_factor * nitrogen_added
