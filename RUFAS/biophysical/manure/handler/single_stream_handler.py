from typing import Any

from RUFAS.biophysical.manure.handler.handler import Handler
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.time import Time
from RUFAS.units import MeasurementUnits


class SingleStreamHandler(Handler):
    """
    Base class for all handlers that only accept a single manure stream at a time.

    Parameters
    ----------
    name : str
        Unique identifier of the processor.
    handler_type: str
        The manure handler sub-type class into which this handler is categorized.
    cleaning_water_use_amount : float
        Amount of cleaning water used per animal per day (L).
    cleaning_water_recycle_fraction : float
        Fraction of cleaning water that is from recycled (not fresh) water sources (unitless).
    use_parlor_flush : bool
        Indication for if a parlor flush is used in addition to routine parlor water cleaning with fresh water.

    """

    def __init__(
        self,
        name: str,
        handler_type: str,
        cleaning_water_use_amount: float,
        cleaning_water_recycle_fraction: float,
        use_parlor_flush: bool,
    ):
        super().__init__(name, handler_type, cleaning_water_use_amount, cleaning_water_recycle_fraction, use_parlor_flush)
        self._prefix = f"{self.__class__.__name__}.{self.handler_type}.{self.name}"

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
            raise ValueError("Non-parlor handler cannot receive multiple streams.")
        self.manure_stream = manure_stream

    def process_manure(self, conditions: CurrentDayConditions, time: Time) -> dict[str, ManureStream]:
        """
        Executes the daily manure processing operations. This method will calculate the gas emissions then call the
        base handler's process manure.

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
            raise TypeError("Handler tries to process 'NoneType' object ManureStream or PenManureData.")
        barn_temperature = self.determine_barn_temperature(conditions.mean_air_temperature)
        surface_area = self.manure_stream.pen_manure_data.manure_deposition_surface_area
        emission_info_map: dict[str, Any] = {
            "class": self.__class__.__name__,
            "function": self.process_manure.__name__,
            "prefix": self._prefix,
            "simulation_day": time.simulation_day,
            "units": MeasurementUnits.KILOGRAMS,
            "handler type": self.handler_type,
        }
        housing_CO2_emissions = self.determine_housing_carbon_dioxide_emissions(surface_area, barn_temperature)
        housing_methane_emissions = self.determine_housing_methane_emissions(surface_area, barn_temperature)
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
        return max(0.0, 0.0065 + 0.0192 * barn_temperature) * manure_deposition_surface_area
