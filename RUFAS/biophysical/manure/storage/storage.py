from numpy import clip, exp

from RUFAS.biophysical.manure.processor import Processor
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.general_constants import GeneralConstants
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
    storage_time_period : int
        How long manure is stored for before emptying the storage (days).
    surface_area : float
        The surface area of the manure storage (m^2).
    nitrous_oxide_emission_factor : float
        Factor governing the nitrous oxide emissions from storage (kg nitrous oxide N / kg manure N).

    Attributes
    ----------
    _received_manure : ManureStream
        The total amount of manure received by a storage in a single day.
    _stored_manure : ManureStream
        The current amount of manure currently held by the storage.
    _cover : StorageCover
        The cover of the storage.
    _storage_time_period : int
        Interval between emptyings of the storage (days).
    _surface_area : float
        Surface area of the manure storage (m^2).
    _nitrous_oxide_emission_factor : float
        Factor governing the nitrous oxide emissions from storage (kg nitrous oxide N / kg manure N).

    """

    def __init__(
        self,
        name: str,
        is_housing_emissions_calculator: bool,
        cover: StorageCover,
        storage_time_period: int,
        surface_area: float,
        nitrous_oxide_emissions_factor: float,
    ) -> None:
        """Initializes a manure Storage."""
        super().__init__(name, is_housing_emissions_calculator)
        self._received_manure = ManureStream(
            water=0.0,
            ammoniacal_nitrogen=0.0,
            nitrogen=0.0,
            phosphorus=0.0,
            potassium=0.0,
            ash=0.0,
            non_degradable_volatile_solids=0.0,
            degradable_volatile_solids=0.0,
            total_solids=0.0,
            volume=0.0,
            pen_manure_data=None,
        )
        self._stored_manure = ManureStream(
            water=0.0,
            ammoniacal_nitrogen=0.0,
            nitrogen=0.0,
            phosphorus=0.0,
            potassium=0.0,
            ash=0.0,
            non_degradable_volatile_solids=0.0,
            degradable_volatile_solids=0.0,
            total_solids=0.0,
            volume=0.0,
            pen_manure_data=None,
        )
        self._cover = cover
        self._storage_time_period = storage_time_period
        self._surface_area = surface_area
        self._nitrous_oxide_emissions_factor = nitrous_oxide_emissions_factor

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
            error_message = f"Processor {self.name} received an incompatible ManureStream."
            self._om.add_error("invalid_manure_stream", error_message, info_map)
            raise ValueError(error_message)

        self._received_manure += manure

    @classmethod
    def _calculate_methane_emissions(
        cls, volatile_solids: float, manure_temperature: float, is_degradable: bool
    ) -> float:
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

        arrhenius_exponent = cls._calculate_arrhenius_exponent(manure_temperature)

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

    @classmethod
    def _calculate_arrhenius_exponent(cls, temp: float) -> float:
        """
        Calculate the Arrhenius exponent.

        Parameters
        ----------
        temp : float
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
        is_temp_invalid: bool = not (GENERAL_LOWER_BOUND_TEMPERATURE <= temp <= GENERAL_UPPER_BOUND_TEMPERATURE)
        if is_temp_invalid:
            raise ValueError(f"Temperature must be between -40 and 60 degrees Celsius. Temperature provided: {temp}")

        temp_kelvin = Utility.convert_celsius_to_kelvin(temp)
        return float(exp(NATURAL_LOG_ARRHENIUS_CONSTANT - (ACTIVATION_ENERGY / (GAS_CONSTANT * temp_kelvin))))

    @classmethod
    def _determine_outdoor_storage_temperature(air_temperature: float) -> float:
        """
        Determines the temperature of the manure in outdoor liquid and slurry storages.

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
        The temperature bounds of this method were based on personal communication and recommendations from A. Leytem
        (april.leytem@usda.gov) and A. VanderZaag (andrew.vanderzaag@AGR.GC.CA). These bounds are also support by work
        from Genedy and Ogejo, 2021 (https://doi.org/10.1016/j.compag.2021.106234) who observed similar minimum and
        maximum liquid manure temperatures in outdoor clay pit and concrete tank manure storages.

        Notes
        -----
        This function clamps stored manure temperature to between 0 and 35 °C. Between 0 and 35 °C, outdoor stored
        liquid manure temperature is assumed to be equal to ambient air temperature.

        """
        return float(clip(air_temperature, 0.0, 35.0))
