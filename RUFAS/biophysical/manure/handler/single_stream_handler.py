from typing import Any

from RUFAS.biophysical.manure.handler.handler import Handler, HandlerConfig
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.routines.manure.constants_and_units.gas_emission_constants import GasEmissionConstants
from RUFAS.routines.manure.constants_and_units.manure_constants import ManureConstants
from RUFAS.time import Time
from RUFAS.units import MeasurementUnits


class SingleStreamHandler(Handler):
    """
    Base class for all handlers that only accepts single manure stream at a time.

    Parameters
    ----------
    name : str
        Unique identifier of the processor.

    """

    def __init__(self, name: str, config: HandlerConfig):
        super().__init__(name, config)

    def receive_manure(self, manure_stream: ManureStream) -> None:
        """
        Takes in manure to be processed.

        Parameters
        ----------
        manure_stream : ManureStream
            The manure to be processed.

        Raises
        ------
        ValueError
            If the ManureStream is incompatible with the processor receiving it.

        """
        info_map = {"class": self.__class__.__name__, "function": self.receive_manure.__name__}
        super().receive_manure(manure_stream)
        if self.manure_stream is not None:
            self._om.add_error(
                "Multiple stream received.",
                f"Non parlor handler should only receive one manure stream at a time,"
                f" handler {self.name} already received a manure stream.",
                info_map,
            )
            raise ValueError("Handler cannot receive multiple streams.")
        self.manure_stream = manure_stream

    def process_manure(self, conditions: CurrentDayConditions, time: Time) -> dict[str, ManureStream]:
        """
        Executes the daily manure processing operations.

        Parameters
        ----------
        conditions : CurrentDayConditions
            Current weather and environmental conditions that manure is being processed in.
        time : Time
            Time instance containing the simulations temporal information.

        Returns
        -------
        dict[str, ManureStream]
            Mapping between classification of manure coming out of this processor to the ManureStream containing the
            manure information. If the processor is a separator, the classifications are "solid" and "liquid". Otherwise
            the only classification is "manure".

        """
        if self.manure_stream is None or self.manure_stream.pen_manure_data is None:
            info_map = {"class": self.__class__.__name__, "function": self.process_manure.__name__}
            self._om.add_error(
                "None type ManureStream.",
                "The processed ManureStream or pen data of the manure stream is None type.",
                info_map,
            )
            raise TypeError("TypeError: Handler tries to process 'NoneType' object ManureStream.")
        barn_temperature = self.determine_barn_temperature(conditions.mean_air_temperature)
        surface_area = self.manure_stream.pen_manure_data.manure_deposition_surface_area
        self.ammonia_emission = self._calculate_ammonia_emissions(
            self.manure_stream.ammoniacal_nitrogen,
            self.manure_stream.volume,
            ManureConstants.SLURRY_MANURE_DENSITY,
            barn_temperature,
            self.determine_ammonia_resistance(barn_temperature),
            surface_area,
            GasEmissionConstants.DEFAULT_PH_FOR_HOUSING_AMMONIA,
        )
        emission_info_map: dict[str, Any] = {
            "class": self.__class__.__name__,
            "function": self.process_manure.__name__,
            "prefix": self._prefix,
            "simulation_day": time.simulation_day,
            "units": MeasurementUnits.KILOGRAMS,
        }
        housing_CO2_emissions = self.determine_housing_carbon_dioxide_emissions(surface_area, barn_temperature)
        housing_methane_emissions = self.determine_housing_methane_emissions(surface_area, barn_temperature)
        self._om.add_variable("housing_ammonia_emissions", self.ammonia_emission, emission_info_map)
        self._om.add_variable("housing_CO2_emissions", housing_CO2_emissions, emission_info_map)
        self._om.add_variable("housing_methane_emissions", housing_methane_emissions, emission_info_map)
        return super().process_manure(conditions, time)

    @staticmethod
    def determine_housing_methane_emissions(manure_deposition_surface_area: float, barn_temperature: float) -> float:
        """
        Calculates the methane housing emission.

        Parameters
        ----------
        manure_deposition_surface_area : float
            The surface area of the manure deposition area in the pen (m^2).
        barn_temperature : float
            Temperature of the barn (Celsius).

        Returns
        -------
        float
            Methane emission from manure (kg).

        """
        return max(0.0, 0.13 * barn_temperature) * manure_deposition_surface_area / 1000

    @staticmethod
    def determine_housing_carbon_dioxide_emissions(
        manure_deposition_surface_area: float, barn_temperature: float
    ) -> float:
        """
        Calculates the housing carbon dioxide housing emission.

        Parameters
        ----------
        manure_deposition_surface_area : float
            The surface area of the manure deposition area in the pen (m^2).
        barn_temperature : float
            Temperature of the barn (Celsius).

        Returns
        -------
        float
            Carbon dioxide emission from manure (kg).

        """
        return max(0.0, 0.0065 + 0.0192 * barn_temperature) * manure_deposition_surface_area / 1000

    @staticmethod
    def determine_ammonia_resistance(temp: float) -> float:
        """
        Calculate resistance of ammonia transport to the atmosphere in a barn.

        Parameters
        ----------
        temp : float
            Temperature in Celsius (C).

        Returns
        -------
        float
            Resistance of ammonia transport to the atmosphere in a barn (s/m).

        """
        return GasEmissionConstants.HOUSING_HSC * (1 - 0.027 * (20.0 - max(temp, -15.0)))
