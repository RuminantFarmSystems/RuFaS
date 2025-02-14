from numpy import exp

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

"""The ideal gas constant (J/mol :math:`\\cdot` K)."""
GAS_CONSTANT: float = 8.314

"""General temperature lower bound (:math:`^{\\circ}C`). Default is set to -40.0."""
GENERAL_LOWER_BOUND_TEMPERATURE: float = -40.0

"""General temperature upper bound (:math:`^{\\circ}C`). Default is set to 60.0."""
GENERAL_UPPER_BOUND_TEMPERATURE: float = 60.0

"""Natural log of the Arrhenius constant (g :math:`CH_4`/kg manure VS/h)."""
NATURAL_LOG_ARRHENIUS_CONSTANT: float = 31.2


class Storage(Processor):
    """
    Base manure Storage class.

    Parameters
    ----------
    cover : StorageCover
        What the storage will be covered with, if anything.
    storage_time_period : int
        How long manure is stored for before emptying the storage (days).

    Attributes
    ----------
    _stored_manure : ManureStream
        The current amount of manure currently held by the storage.
    _cover : StorageCover
        The cover of the storage.
    _storage_time_period : int
        Interval between emptyings of the storage (days).

    """

    def __init__(
        self, name: str, is_housing_emissions_calculator: bool, cover: StorageCover, storage_time_period: int
    ) -> None:
        """Initializes a manure Storage."""
        super().__init__(name, is_housing_emissions_calculator)
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

        self._stored_manure += manure

    @classmethod
    def _calculate_methane_emissions(
        cls, volatile_solids: float, manure_temperature: float, is_degradable: bool
    ) -> float:
        """
        Calculate the methane emission.

        Parameters
        ----------
        volatile_solids : float
            Mass of volatile solids that are emitting methane. Can be degrdable or non-degradable.
        manure_temperature : float
            Temperature of the manure in storage :math:`^\\circ C`).
        is_degradable : bool
            True if the volatile solids are degrdable, otherwise false.

        Returns
        -------
        float
            Methane emission from volatile solids (kg :math:`CH_4`).

        Notes
        -----
        The equation used to calculate the methane emission from manure storage is as follows:

        .. math::

            E_{CH_4} = 24 \\cdot e^{lnA - \\frac{E}{RT}} \\cdot VS_{d} \\cdot b_{1} \\cdot \frac{1}{1000}
            + 24 \\cdot e^{lnA - \\frac{E}{RT}} \\cdot VS_{nd} \\cdot b_{2} \\cdot \frac{1}{1000}

        where:

            :math:`E_{CH_4}` is the methane emission from manure storage (kg :math:`CH_4`/day),

            :math:`VS_{d}` is the degradable volatile solids in manure (kg),

            :math:`b_{1}` is the degradable volatile solids rate correcting factor (1.0, unitless),

            :math:`VS_{nd}` is the non-degradable volatile solids in manure (kg),

            :math:`b_{2}` is the non-degradable volatile solids rate correcting factor (0.01, unitless),

            :math:`lnA` is the natural log of the Arrhenius constant (31.2, $\frac{\text{kg VS}}{\text{h}}^{-1}$),

            :math:`E` is the activation energy (81,000.0 J/mol),

            :math:`R` is the ideal gas constant (8.314 J/mol :math:`\\cdot` K),

            :math:`T` is the temperature in Kelvin (:math:`K`).

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
            Temperature in Celsius (:math:`^\\circ C`).

        Returns
        -------
        float
            Arrhenius exponent (unitless).

        Raises
        ------
        ValueError
            If the temperature is not between -40 and 50 degrees Celsius.

        Notes
        -----
        The Arrhenius exponent is calculated as follows:

        .. math::

            e^{lnA - \\frac{E}{RT}}

        where:

            :math:`lnA` is the natural log of the Arrhenius constant (unitless),

            :math:`E` is the activation energy (joules per mol, J/mol),

            :math:`R` is the universal gas constant (joules per mol Kelvin, J/mol :math:`\\cdot` K),

            :math:`T` is the temperature in Kelvin (K).

        """
        is_temp_invalid: bool = not (GENERAL_LOWER_BOUND_TEMPERATURE <= temp <= GENERAL_UPPER_BOUND_TEMPERATURE)
        if is_temp_invalid:
            raise ValueError(f"Temperature must be between -40 and 60 degrees Celsius. Temperature provided: {temp}")

        temp_kelvin = temp * Utility.convert_celsius_to_kelvin(temp)
        return exp(NATURAL_LOG_ARRHENIUS_CONSTANT - (ACTIVATION_ENERGY / (GAS_CONSTANT * temp_kelvin)))
