from abc import ABC, abstractmethod
from dataclasses import asdict
from numpy import clip

from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.general_constants import GeneralConstants
from RUFAS.rufas_time import RufasTime
from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits
from RUFAS.util import Utility


class Processor(ABC):
    """
    Base class for all manure processors.

    Parameters
    ----------
    name : str
        Unique identifier of the processor.
    is_housing_emissions_calculator : bool
        Indicates if a Processor calculates housing emissions.

    Attributes
    ----------
    name : str
        Unique identifier of the processor used to label outputs.
    is_housing_emissions_calculator : bool
        If true, processor will only accept ManureStreams with non-None PenManureData, if false then vice versa.
    _om : OutputManager
        Instance of the OutputManager.
    _prefix : str
        Prefix in a standardized format for reporting daily outputs from the Processor.

    Methods
    -------
    receive_manure(manure: ManureStream) -> None
        Entry point of manure into the processor.
    process_manure(conditions: CurrentDayConditions, time: RufasTime) -> dict[str, ManureStream]
        Handles the daily operations for the processor.

    """

    def __init__(self, name: str, is_housing_emissions_calculator: bool) -> None:
        """Initializes a new Processor."""
        self.name = name
        self.is_housing_emissions_calculator = is_housing_emissions_calculator
        self._om = OutputManager()
        base_class_name = self.__class__.__bases__[0].__name__
        self._prefix = f"Manure.{base_class_name}.{self.__class__.__name__}.{self.name}"

    @abstractmethod
    def receive_manure(self, manure: ManureStream) -> None:
        """
        Takes in manure to be processed.

        Parameters
        ----------
        manure : ManureStream
            The manure to be processed.

        Raises
        ------
        ValueError
            If the ManureStream is incompatible with the processor receiving it.

        """
        pass

    @abstractmethod
    def process_manure(self, conditions: CurrentDayConditions, time: RufasTime) -> dict[str, ManureStream]:
        """
        Executes the daily manure processing operations.

        Parameters
        ----------
        conditions : CurrentDayConditions
            Current weather and environmental conditions that manure is being processed in.
        time : RufasTime
            RufasTime instance containing the simulations temporal information.

        Returns
        -------
        dict[str, ManureStream]
            Mapping between classification of manure coming out of this processor to the ManureStream containing the
            manure information. If the processor is a separator, the classifications are "solid" and "liquid". Otherwise
            the only classification is "manure".

        """
        pass

    def _report_manure_stream(
        self, manure_stream: ManureStream | dict[str, float | None], stream_name: str, simulation_day: int
    ) -> None:
        """
        Reports the manure stream data to Output Manager.

        Parameters
        ----------
        manure_stream : ManureStream | dict[str, float]
            The manure stream to report. If a `ManureStream` instance is passed, it will be converted to a dictionary.
        stream_name : str
            The name of the manure stream being reported.
        simulation_day : int
            The current simulation day.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._report_manure_stream.__name__,
            "prefix": self._prefix,
            "simulation_day": simulation_day,
        }
        if isinstance(manure_stream, ManureStream):
            manure_stream_dict = asdict(manure_stream)
            manure_stream_dict["total_volatile_solids"] = manure_stream.total_volatile_solids
            manure_stream_dict["mass"] = manure_stream.mass
        elif isinstance(manure_stream, dict):
            manure_stream_dict = manure_stream.copy()
        else:
            self._om.add_error(
                "Manure Stream Type Error",
                "This function requires either a ManureStream instance or a dictionary.",
                info_map,
            )
            raise ValueError("Manure stream must be a dictionary or a ManureStream instance to properly report it.")

        if manure_stream_dict.keys() != ManureStream.MANURE_STREAM_UNITS.keys():
            self._om.add_error(
                "Manure Stream Keys Error",
                f"Expected keys: {set(ManureStream.MANURE_STREAM_UNITS.keys())}, "
                f"received: {set(manure_stream_dict.keys())}.",
                info_map,
            )
            raise ValueError("Manure Stream must contain the same keys as manure_stream_units to properly report it.")

        for key, value in manure_stream_dict.items():
            if key not in ["pen_manure_data", "manure_production_potential"]:
                self._om.add_variable(
                    f"{stream_name}_manure_{key}" if stream_name != "" else f"manure_{key}",
                    value,
                    {**info_map, "units": ManureStream.MANURE_STREAM_UNITS[key]},
                )

    def check_manure_stream_compatibility(self, manure_stream: ManureStream) -> bool:
        """
        Checks if a ManureStream is capable of being processed.

        Parameters
        ----------
        manure_stream : ManureStream
            The ManureStream instance being checked for compatibility.

        Returns
        -------
        bool
            True if the ManureStream can be processed by the Processor, otherwise false.

        """
        is_valid_housing_emissions_calculator = (
            True if (self.is_housing_emissions_calculator and manure_stream.pen_manure_data is not None) else False
        )
        is_valid_non_housing_emissions_calculator = (
            True if (not self.is_housing_emissions_calculator and manure_stream.pen_manure_data is None) else False
        )

        return is_valid_housing_emissions_calculator ^ is_valid_non_housing_emissions_calculator

    @staticmethod
    def _calculate_ammonia_emissions(
        total_ammoniacal_nitrogen: float,
        mass: float,
        density: float,
        temperature: float,
        ammonia_resistance: float,
        surface_area: float,
        pH: float,
    ) -> float:
        """
        Calculate housing and liquid storage ammonia nitrogen emissions.

        Parameters
        ----------
        total_ammoniacal_nitrogen : float
            Total ammoniacal nitrogen in manure (kg).
        mass : float
            Total mass of the manure produced by the animals in the storage area (m^3).
        density : float
            Density of the manure (kg / m^3).
        temperature : float
            Temperature of the manure (degrees C).
        ammonia_resistance : float
            Resistance of ammonia transport to the atmosphere (siemens / meter).
        surface_area : float
            Total surface area of the manure storage (m^2).
        pH : float
            pH value of the manure (unitless).

        Returns
        -------
        float
            Ammonia nitrogen emission from manure (kg).

        Raises
        ------
        ValueError
            If total_ammoniacal_nitrogen < 0.0.
            If volume < 0.0.
            If density < 0.0.
            If surface area of storage < 0.0.0

        """
        if total_ammoniacal_nitrogen < 0.0:
            raise ValueError("Manure total ammoniacal nitrogen must be greater than or equal to 0.0.")
        if mass < 0.0:
            raise ValueError("Manure mass must be greater than or equal to 0.0.")
        if density < 0.0:
            raise ValueError("Manure density must be greater than or equal to 0.0.")
        if surface_area < 0.0:
            raise ValueError("Storage surface area must be greater than or equal to 0.0.")

        is_a_param_zero = any(param == 0 for param in [total_ammoniacal_nitrogen, mass, density, surface_area])
        if is_a_param_zero:
            return 0.0

        temp_kelvin = Utility.convert_celsius_to_kelvin(temperature)
        manure_kilograms_per_square_meter = mass / surface_area
        total_ammoniacal_nitrogen_per_meter = total_ammoniacal_nitrogen / surface_area
        equilibrium_coefficient = Processor._calculate_ammonia_equilibrium_coefficient(temp_kelvin, pH)
        ammonia_loss_per_meter = (total_ammoniacal_nitrogen_per_meter * GeneralConstants.SECONDS_PER_DAY * density) / (
            ammonia_resistance * manure_kilograms_per_square_meter * equilibrium_coefficient
        )
        total_ammonia_loss = min(ammonia_loss_per_meter * surface_area, total_ammoniacal_nitrogen)
        return total_ammonia_loss

    @staticmethod
    def _calculate_ammonia_equilibrium_coefficient(temperature: float, pH: float) -> float:
        """
        Calculates the equilibrium coefficient for the ammonia gas in the air for a given concentration of total
        ammoniacal nitrogen in the solution.

        Parameters
        ----------
        temperature : float
            Manure solution temperature in Kelvin (K).
        pH : float
            Manure solution pH (unitless).

        Returns
        -------
        float
            Equilibrium coefficient for the ammonia gas in the air (unitless).

        """
        henrys_ammonia_coefficient = Processor._calculate_henry_law_coefficient_of_ammonia(temperature)
        ammonium_dissociation_coefficient = Processor._calculate_dissociation_coefficient_of_ammonium(temperature, pH)
        return henrys_ammonia_coefficient * ammonium_dissociation_coefficient

    @staticmethod
    def _calculate_henry_law_coefficient_of_ammonia(temperature: float) -> float:
        """
        Calculate Henry's Law coefficient of ammonia.

        Parameters
        ----------
        temperature : float
            Temperature in Kelvin (K).

        Returns
        -------
        float
            Henry's law coefficient of ammonia (unitless).

        """
        return 10 ** (1478 / temperature - 1.69)

    @staticmethod
    def _calculate_dissociation_coefficient_of_ammonium(temperature: float, pH: float) -> float:
        """
        Calculate dissociation coefficient of ammonium.

        Parameters
        ----------
        temperature : float
            Temperature in Kelvin (K).
        pH : float
            Manure solution acidity (unitless).

        Returns
        -------
        float
            Dissociation coefficient of ammonium (unitless).

        """
        return 1 + 10 ** (0.09018 + 2729.9 / temperature - pH)

    @staticmethod
    def _determine_barn_temperature(air_temperature: float) -> float:
        """
        Calculates the barn temperature.

        Parameters
        ----------
        air_temperature : float
            Air temperature (c).

        Returns
        -------
        float
            Adjusted barn temperature (c).

        References
        ----------
        Between 5 and 30 C, barn temperature is assumed to be equal to outdoor air temperature.
        This function assumes that barn temperature does not drop below 5 C or increase above 30 C.
        These bounds were suggested by manure SMEs and are supported by barn temperature ranges
        reported in Bucklin et al. (FL, upper limit; https://doi.org/10.13031/2013.28851).
        The lower bound (5 C) suggested by SMEs was based on general industry standards/conditions.

        """
        return float(clip(air_temperature, 5.0, 30.0))

    def _report_processor_output(
        self,
        variable_name: str,
        variable_value: float,
        data_origin_function: str,
        units: MeasurementUnits,
        simulation_day: int,
    ) -> None:
        """
        Reports an output variable to the OutputManager.

        Parameters
        ----------
        variable_name : str
            The name of the reported variable.
        variable_value : str
            The value of the reported variable value.
        data_origin_function : str
            The name of the function that reported the variable value.
        units : MeasurementUnits
            The units for the reported variable value.
        simulation_day : int
            The current simulation day.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": data_origin_function,
            "prefix": self._prefix,
            "simulation_day": simulation_day,
            "units": units,
        }

        self._om.add_variable(variable_name, variable_value, info_map)
