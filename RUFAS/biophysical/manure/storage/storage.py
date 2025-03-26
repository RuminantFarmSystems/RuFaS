from dataclasses import replace
from math import inf
from numpy import exp

from RUFAS.biophysical.manure.processor import Processor
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.general_constants import GeneralConstants
from RUFAS.time import Time
from RUFAS.util import Utility

from .storage_cover import StorageCover

"""
Activation energy (joules per mole, J/mol). The activation energy is the minimum energy that must be available to
molecules for a reaction to occur.
"""
ACTIVATION_ENERGY: float = 81_000.0

"""Default pH for ammonia (unitless)."""
DEFAULT_PH_FOR_AMMONIA: float = 7.5

"""
Rate correcting factor for degradable volatile solids, used in calculation of slurry storage methane emission
(unitless).
"""
DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR: float = 1.0

"""
Rate correcting factor for non-degradable volatile solids, used in calculation of slurry storage methane emission
(unitless).
"""
NON_DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR: float = 0.01

"""The ideal gas constant (J/mol * K)."""
GAS_CONSTANT: float = 8.314

"""General temperature lower bound (degrees C)."""
GENERAL_LOWER_BOUND_TEMPERATURE: float = -40.0

"""General temperature upper bound (degrees C)."""
GENERAL_UPPER_BOUND_TEMPERATURE: float = 60.0

"""Housing specific constant for manure storage (siemens / meter)."""
HOUSING_SPECIFIC_CONSTANT = 4.1

"""Percentage of methane destroyed in storage systems using a cap and flare."""
METHANE_DESTRUCTION_EFFICIENCY = 81.0

"""Natural log of the Arrhenius constant (g methane / kg manure Volatile Solids / hour)."""
NATURAL_LOG_ARRHENIUS_CONSTANT: float = 31.2

"""
Mapping of storage cover types to the nitrous oxide emissions factor associated with that cover type (kg nitrous oxide N
/ kg manure N).
"""
STORAGE_COVER_NITROUS_OXIDE_EMISSIONS_FACTOR_MAPPING: dict[StorageCover, float] = {
    StorageCover.COVER: 0.005,
    StorageCover.CRUST: 0.005,
    StorageCover.NO_COVER: 0.0,
    StorageCover.COVER_AND_FLARE: 0.005,
}


class Storage(Processor):
    """
    Base manure Storage class.

    Parameters
    ----------
    cover : StorageCover
        What the storage will be covered with, if anything.
    storage_time_period : int | None
        How long manure is stored for before emptying the storage (days). None if the storage is never emptied.
    surface_area : float
        The surface area of the manure storage (m^2).
    nitrous_oxide_emissions_factor : float
        Factor governing the nitrous oxide emissions from storage (kg nitrous oxide N / kg manure N).
    capacity : float, default math.inf
        Volumetric capacity of the storage (m^3).

    Attributes
    ----------
    _received_manure : ManureStream
        The total amount of manure received by a storage in a single day.
    _stored_manure : ManureStream
        The current amount of manure currently held by the storage.
    _capacity : float
        The volumetric capacity of the storage (m^3).
    _cover : StorageCover
        The cover of the storage.
    _storage_time_period : int | None
        Interval between emptyings of the storage (days). If the storage is never emptied, this is None.
    _surface_area : float
        Surface area of the manure storage (m^2).
    _nitrous_oxide_emissions_factor : float
        Factor governing the nitrous oxide emissions from storage (kg nitrous oxide N / kg manure N).
    _manure_to_process : ManureStream
        The manure that to be processed during the `process_manure()` method call.

    """

    def __init__(
        self,
        name: str,
        is_housing_emissions_calculator: bool,
        cover: StorageCover,
        storage_time_period: int | None,
        surface_area: float,
        nitrous_oxide_emissions_factor: float,
        capacity: float = inf,
    ) -> None:
        """Initializes a manure Storage."""
        super().__init__(name, is_housing_emissions_calculator)
        self._received_manure = ManureStream.make_empty_manure_stream()
        self._stored_manure = ManureStream.make_empty_manure_stream()
        self._capacity = capacity
        self._cover = cover
        self._storage_time_period = storage_time_period
        self._surface_area = surface_area
        self._nitrous_oxide_emissions_factor = nitrous_oxide_emissions_factor
        self._manure_to_process = ManureStream.make_empty_manure_stream()

    @property
    def is_overflowing(self) -> bool:
        """True if the manure in storage exceeds the storage's volumetric capacity, else False."""
        return self._stored_manure.volume > self._capacity

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
            error_message = f"Processor '{self.name}' received an incompatible ManureStream."
            self._om.add_error("invalid_manure_stream", error_message, info_map)
            raise ValueError(error_message)

        self._received_manure += manure

    def process_manure(self, _: CurrentDayConditions, time: Time) -> dict[str, ManureStream]:
        """
        Adds the manure received on the current day to the manure already stored, and empties the storage if scheduled.
        """
        self._stored_manure += self._received_manure
        self._received_manure = ManureStream.make_empty_manure_stream()

        is_emptying_day = self._storage_time_period is not None and time.simulation_day % self._storage_time_period == 0
        if is_emptying_day:
            self._report_manure_stream(self._stored_manure, "emptied", time)
            manure_to_be_returned = {"manure": replace(self._stored_manure)}
            self._stored_manure = ManureStream.make_empty_manure_stream()
        else:
            manure_to_be_returned = {}

        if self.is_overflowing is True:
            self.handle_overflowing_manure(time)

        return manure_to_be_returned

    def handle_overflowing_manure(self, time: Time) -> None:
        """
        Deals with excess manure when amount in storage exceeds capacity.

        Parameters
        ----------
        time : Time
            Time instance tracking the current time of the simulation.

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
            rate_correcting_factor = DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR
        else:
            rate_correcting_factor = NON_DEGRADABLE_VOLATILE_SOLIDS_RATE_CORRECTING_FACTOR

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
        is_temp_invalid: bool = not (GENERAL_LOWER_BOUND_TEMPERATURE <= temperature <= GENERAL_UPPER_BOUND_TEMPERATURE)
        if is_temp_invalid:
            raise ValueError(
                f"Temperature must be between -40 and 60 degrees Celsius. Temperature provided: {temperature}"
            )

        temp_kelvin = Utility.convert_celsius_to_kelvin(temperature)
        return float(exp(NATURAL_LOG_ARRHENIUS_CONSTANT - (ACTIVATION_ENERGY / (GAS_CONSTANT * temp_kelvin))))

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
        storage_methane_burned = methane_loss * METHANE_DESTRUCTION_EFFICIENCY * GeneralConstants.PERCENTAGE_TO_FRACTION
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
