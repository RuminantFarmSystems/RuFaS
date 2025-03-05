from dataclasses import replace

from RUFAS.biophysical.manure.digester.digester import Digester
from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.general_constants import GeneralConstants
from RUFAS.time import Time


"""
Unit conversion factor for carbon dioxide generated from anaerobic digestion at 1 atm of pressure and 37.5C (kg / m^3).
"""
CARBON_DIOXIDE_DENSITY: float = 1.716

"""
Volumetric ratio of carbon dioxide to methane generated during anaerobic digestion (m^3 carbon dioxide / m^3 methane).
"""
CARBON_DIOXIDE_TO_METHANE_RATIO: float = 4 / 6

"""
Unit conversion factor for methane generated from an anaerobic digester at 1 atm of pressure and 37.5 C (kg / m^3).
"""
METHANE_DENSITY: float = 0.629

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
    _hydraulic_retention_time : int
        Number of days manure spends in the anaerobic digester (days).
    _top_cover_volume_fraction : float
        Fraction of the total volume of the anaerobic digester that is assumed to be the top cover volume (unitless).

    """

    def __init__(self, name: str) -> None:
        super().__init__(name=name, is_housing_emissions_calculator=False)
        self._received_manure: ManureStream = ManureStream.make_empty_manure_stream()
        self._temperature_set_point: float = 20.0
        self._hydraulic_retention_time: int = 25
        self._top_cover_volume_fraction: float = 0.1

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
        specific_input_energy = self._calculate_specific_input_energy(
            conditions.mean_air_temperature, moisture_fraction, self._temperature_set_point
        )
        heating_input_energy = (  # TODO: wrong unit conversion factor?
            specific_input_energy * self._received_manure.volume * GeneralConstants.LITERS_TO_CUBIC_METERS
        )

        minimum_volume = self._received_manure.volume * self._hydraulic_retention_time
        top_cover_volume = self._received_manure * self._top_cover_volume_fraction

        generated_methane_volume = self._calculate_CSTR_methane_volume(self._received_manure.total_volatile_solids)
        generated_methane_mass = generated_methane_volume * METHANE_DENSITY
        generated_carbon_dioxide_mass = (
            generated_methane_volume * CARBON_DIOXIDE_TO_METHANE_RATIO * CARBON_DIOXIDE_DENSITY
        )
        total_volatile_solids_destruction = generated_methane_mass + generated_carbon_dioxide_mass
        self._received_manure = self._destroy_volatile_solids(total_volatile_solids_destruction)

    def _destroy_volatile_solids(self, total_volatile_solids_destruction: float, time: Time) -> ManureStream:
        """
        Adjusts the pools of solids in the manure after volatile solids are destroyed.

        Parameters
        ----------
        total_volatile_solids_destruction : float
            Amount of volatile solids removed from the manure (kg).

        Returns
        -------
        ManureStream
            Manure being processed by the anaerobic digester after volatile solids are removed.

        """
        if self._received_manure.total_volatile_solids < total_volatile_solids_destruction:
            info_map = {
                "class": self.__class__.__name__,
                "function": self._destroy_volatile_solids.__name__,
                "name": self.name,
                "date": time.current_date.date(),
                "simulation_day": time.simulation_day,
                "total_volatile_solids": self._received_manure.total_volatile_solids,
                "total_volatile_solids_destruction": total_volatile_solids_destruction,
            }
            err_name = f"Anerobic digester '{self.name}' attempted to destroy more volatile solids than available"
            err_msg = "Setting degradable volatile solids, non-degradable volatile solids, and total volatile solids "
            "pools to be 0.0."
            self._om.add_error(err_name, err_msg, info_map)
            degradable_volatile_solids = 0.0
            non_degradable_volatile_solids = 0.0
        else:
            degradable_volatile_solids_frac = (
                self._received_manure.degradable_volatile_solids / self._received_manure.total_volatile_solids
            )

            degradable_volatile_solids = self._received_manure.degradable_volatile_solids - (
                total_volatile_solids_destruction * degradable_volatile_solids_frac
            )
            non_degradable_volatile_solids = self._received_manure.non_degradable_volatile_solids - (
                total_volatile_solids_destruction * (1.0 - degradable_volatile_solids_frac)
            )
        return replace(
            self._received_manure,
            degradable_volatile_solids=degradable_volatile_solids,
            non_degradable_volatile_solids=non_degradable_volatile_solids,
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

    @classmethod
    def _calculate_CSTR_methane_volume(cls, total_volatile_solids: float) -> float:
        """
        Calculates volume of methane generated from a continuously-stirred tank reactor.

        Parameters
        ----------
        total_volatile_solids : float
            Total volatile solids contained in manure (kg).

        Returns
        -------
        float
            Methane generation volume (m^3).

        Notes
        -----
        This function originates from personal communications with subject matter experts Wei Liao (liaow@msu.edu) and
        April Leytem (april.leytem@usda.gov). The equation is a simplification of the IPCC Tier II estimate of CH4
        emissions from anaerobic digesters, where CH4 generated in the digester is assumed to be equivalent to the
        amount of manure volatile solids loaded per day, multiplied by the generally-accepted methane potential value
        for dairy manure (240 L CH4 per kg of manure volatile solids).

        """
        return ManureConstants.ACHIEVABLE_METHANE_EMISSION * total_volatile_solids
