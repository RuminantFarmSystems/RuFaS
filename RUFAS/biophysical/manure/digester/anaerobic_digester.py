from RUFAS.biophysical.manure.digester.digester import Digester
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.general_constants import GeneralConstants
from RUFAS.time import Time


"""The lower temperature bound for manure flowing into an anaerobic digester (degrees C)."""
MINIMUM_INFLUENT_TEMPERATURE = 4.0


class AnaerobicDigester(Digester):
    """
    Defines the behaviors and attributes of an anaerobic digester.

    Parameters
    ----------
    name : str
        Unique identifier of the processor.

    Attributes
    ----------
    _received_manure : ManureStream
        The total amount of manure received by an anaerobic digester in a single day.
    _temperature_set_point : float
        Temperature set point for the anaerobic digestion (degrees C).

    """

    def __init__(self, name: str) -> None:
        super().__init__(name=name, is_housing_emissions_calculator=False)
        self._received_manure: ManureStream = ManureStream.make_empty_manure_stream()
        self._temperature_set_point: float = 20.0

    def receive_manure(self, manure: ManureStream) -> None:
        """Receives and stores manure to digested."""
        is_received_manure_valid = self.check_manure_stream_compatibility(manure)
        if is_received_manure_valid is False:
            raise ValueError(f"Anaerobic digester {self.name} received an invalid manure stream.")
        self._received_manure += manure

    def process_manure(self, conditions: CurrentDayConditions, time: Time) -> dict[str, ManureStream]:
        """Digests manure received on the current day."""
        if self._received_manure.is_empty is True:
            pass  # TODO: implement me

        moisture_fraction = self._received_manure.water / self._received_manure.mass
        _heating_input_energy = self._calculate_specific_input_energy(
            conditions.mean_air_temperature, moisture_fraction, self._temperature_set_point
        )

    @classmethod
    def _calculate_specific_input_energy(
        cls, average_temp: float, moisture_fraction: float, temperature_set_point: float
    ) -> float:
        """
        Calculates the energy required to maintain anaerobic digestion temperature at set point.

        Parameters
        ----------
        average_temp : float
            Average ambient temperature (degrees C).
        moisture_fraction : float
            Fraction of total manure mass that is water (unitless).
        temperature_set_point : float
            Temperature set point for anaerobic digestion.

        Returns
        -------
        float
            Energy required to maintain anaerobic digestion temperature at set point (MJ / m^3).

        """
        effluent_temperature = cls._bind_influent_temperature(average_temp)
        influent_heat_capacity = cls._calculate_manure_heat_capacity(average_temp, moisture_fraction)
        anaerobic_digester_heat_capacity = cls._calculate_manure_heat_capacity(temperature_set_point, moisture_fraction)

        average_heat_capacity = (influent_heat_capacity + anaerobic_digester_heat_capacity) / 2.0
        heating_input_energy = average_heat_capacity * (temperature_set_point - effluent_temperature)
        return heating_input_energy

    @classmethod
    def _bind_influent_temperature(cls, average_temp: float) -> float:
        """
        Lower-bounds the influent temperature of manure based on the average ambient temperature.

        Parameters
        ----------
        average_temp : float
            Average ambient temperature (degrees C).

        Returns
        -------
        float
            The bound temperature of influent manure (degrees C).

        """
        return max(average_temp, MINIMUM_INFLUENT_TEMPERATURE)

    @classmethod
    def _calculate_manure_heat_capacity(cls, temperature: float, moisture_fraction: float) -> float:
        """
        Calculates the heat capacity of manure.

        Parameters
        ----------
        temperature : float
            Temperature at which manure heat capacity is being calculated for (degrees C).
        moisture_fraction : float
            Fraction of manure mass that is water (unitless).

        Returns
        -------
        float
            Heat capacity of manure in an anaerobic digester (kJ / kg / degrees C).

        """
        return 0.68298 + 0.025662 * temperature + 0.01306 * moisture_fraction * GeneralConstants.FRACTION_TO_PERCENTAGE
