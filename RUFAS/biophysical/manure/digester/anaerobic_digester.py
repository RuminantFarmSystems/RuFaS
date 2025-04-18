from dataclasses import replace

from RUFAS.biophysical.manure.digester.digester import Digester
from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.general_constants import GeneralConstants
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits


class AnaerobicDigester(Digester):
    """
    Defines the behaviors and attributes of an anaerobic digester.

    Parameters
    ----------
    name : str
        Unique identifier of the anaerobic digester.
    temperature_set_point : float
        Temperature set point for the anaerobic digestion (degrees C).
    hydraulic_retention_time : int
        Number of days manure spends in the anaerobic digester (days).
    top_cover_volume_fraction : float
        Fraction of the total volume of the anaerobic digester that is assumed to be the top cover volume (unitless).
    methane_leakage_fraction : float
        Fraction of methane generated in the anaerobic digester that escapes to the atmosphere through unintended
        leakage and is not collected by the gas capture system (unitless).
    evaporation_fraction : float
        Fraction of the liquid portion evaporated from the anaerobic digester (unitless).

    Attributes
    ----------
    _manure_in_digester : ManureStream
        The total amount of manure received by an anaerobic digester in a single day.
    _temperature_set_point : float
        Temperature set point for the anaerobic digestion (degrees C).
    _hydraulic_retention_time : int
        Number of days manure spends in the anaerobic digester (days).
    _top_cover_volume_fraction : float
        Fraction of the total volume of the anaerobic digester that is assumed to be the top cover volume (unitless).
    _methane_leakage_fraction : float
        Fraction of methane generated in the anaerobic digester that escapes to the atmosphere through unintended
        leakage and is not collected by the gas capture system (unitless).
    _evaporation_fraction : float
        Fraction of the liquid portion evaporated from the anaerobic digester (unitless).

    """

    def __init__(
        self,
        name: str,
        temperature_set_point: float,
        hydraulic_retention_time: int,
        top_cover_volume_fraction: float,
        methane_leakage_fraction: float,
        evaporation_fraction: float,
    ) -> None:
        super().__init__(name=name, is_housing_emissions_calculator=False)
        self._manure_in_digester: ManureStream = ManureStream.make_empty_manure_stream()
        self._temperature_set_point: float = temperature_set_point
        self._hydraulic_retention_time: int = hydraulic_retention_time
        self._top_cover_volume_fraction: float = top_cover_volume_fraction
        self._methane_leakage_fraction: float = methane_leakage_fraction
        self._evaporation_fraction: float = evaporation_fraction

    def receive_manure(self, manure: ManureStream) -> None:
        """Receives and stores manure to be digested."""
        is_received_manure_valid = self.check_manure_stream_compatibility(manure)
        if is_received_manure_valid is False:
            raise ValueError(f"Anaerobic digester {self.name} received an invalid manure stream.")
        self._manure_in_digester += manure

    def process_manure(self, conditions: CurrentDayConditions, time: RufasTime) -> dict[str, ManureStream]:
        """Digests manure received on the current day."""
        if self._manure_in_digester.is_empty is True:
            self._report_anaerobic_digester_outputs(
                biogas=0.0,
                biogas_energy_content=0.0,
                evaporated_water=0.0,
                heating_input_energy=0.0,
                methane_generation_volume=0.0,
                methane_leakage_mass=0.0,
                minimum_digester_volume=0.0,
                top_cover_volume=0.0,
                simulation_day=time.simulation_day,
            )
            return {}

        moisture_fraction = self._manure_in_digester.water / self._manure_in_digester.mass
        specific_input_energy = self._calculate_specific_input_energy(
            conditions.mean_air_temperature, moisture_fraction, self._temperature_set_point
        )
        heating_input_energy = (
            specific_input_energy * self._manure_in_digester.volume * GeneralConstants.LITERS_TO_CUBIC_METERS
        )

        minimum_digester_volume = self._manure_in_digester.volume * self._hydraulic_retention_time
        top_cover_volume = minimum_digester_volume * self._top_cover_volume_fraction

        self._manure_in_digester.ammoniacal_nitrogen = min(
            self._manure_in_digester.ammoniacal_nitrogen * ManureConstants.TAN_INCREASE_FACTOR,
            self._manure_in_digester.nitrogen
        )

        generated_methane_volume = self._calculate_CSTR_methane_volume(self._manure_in_digester.total_volatile_solids)
        generated_methane_mass = generated_methane_volume * ManureConstants.METHANE_DENSITY
        generated_carbon_dioxide_mass = (
            generated_methane_volume * ManureConstants.CARBON_DIOXIDE_TO_METHANE_RATIO *
            ManureConstants.CARBON_DIOXIDE_DENSITY
        )
        total_volatile_solids_destruction = generated_methane_mass + generated_carbon_dioxide_mass
        self._manure_in_digester = self._destroy_volatile_solids(total_volatile_solids_destruction, time)

        self._manure_in_digester.volume -= total_volatile_solids_destruction / ManureConstants.SLURRY_MANURE_DENSITY

        methane_leakage = self._calculate_methane_leakage(generated_methane_mass, self._methane_leakage_fraction)
        captured_methane_mass = generated_methane_mass - methane_leakage
        captured_methane_energy_content = self._calculate_methane_energy_content(captured_methane_mass)

        evaporated_water = self._manure_in_digester.volume * self._evaporation_fraction

        self._report_anaerobic_digester_outputs(
            biogas=captured_methane_mass,
            biogas_energy_content=captured_methane_energy_content,
            evaporated_water=evaporated_water,
            heating_input_energy=heating_input_energy,
            methane_generation_volume=generated_methane_volume,
            methane_leakage_mass=methane_leakage,
            minimum_digester_volume=minimum_digester_volume,
            top_cover_volume=top_cover_volume,
            simulation_day=time.simulation_day,
        )

        digested_manure = replace(self._manure_in_digester)
        self._manure_in_digester = ManureStream.make_empty_manure_stream()
        return {"manure": digested_manure}

    def _destroy_volatile_solids(self, total_volatile_solids_destruction: float, time: RufasTime) -> ManureStream:
        """
        Adjusts the pools of solids in the manure after volatile solids are destroyed.

        Parameters
        ----------
        total_volatile_solids_destruction : float
            Amount of volatile solids removed from the manure (kg).
        time : RufasTime
            RufasTime instance tracking time of the simulation.

        Returns
        -------
        ManureStream
            Manure being processed by the anaerobic digester after volatile solids are removed.

        """
        if self._manure_in_digester.total_volatile_solids < total_volatile_solids_destruction:
            info_map = {
                "class": self.__class__.__name__,
                "function": self._destroy_volatile_solids.__name__,
                "name": self.name,
                "date": time.current_date.date(),
                "simulation_day": time.simulation_day,
                "degradable_volatile_solids": self._manure_in_digester.degradable_volatile_solids,
                "non_degradable_volatile_solids": self._manure_in_digester.non_degradable_volatile_solids,
                "total_volatile_solids": self._manure_in_digester.total_volatile_solids,
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
                self._manure_in_digester.degradable_volatile_solids / self._manure_in_digester.total_volatile_solids
            )

            degradable_volatile_solids = self._manure_in_digester.degradable_volatile_solids - (
                total_volatile_solids_destruction * degradable_volatile_solids_frac
            )
            non_degradable_volatile_solids = self._manure_in_digester.non_degradable_volatile_solids - (
                total_volatile_solids_destruction * (1.0 - degradable_volatile_solids_frac)
            )
        return replace(
            self._manure_in_digester,
            degradable_volatile_solids=degradable_volatile_solids,
            non_degradable_volatile_solids=non_degradable_volatile_solids,
        )

    def _report_anaerobic_digester_outputs(
        self,
        biogas: float,
        biogas_energy_content: float,
        evaporated_water: float,
        heating_input_energy: float,
        methane_generation_volume: float,
        methane_leakage_mass: float,
        minimum_digester_volume: float,
        top_cover_volume: float,
        simulation_day: int,
    ) -> None:
        """
        Reports manure that was digested and the amounts of different things that were lost in the anaerobic digestion
        process.

        Parameters
        ----------
        biogas : float
            Captured biogas (kg).
        biogas_energy_content : float
            Energy from captured biogas (MJ).
        evaporated_water : float
            Water that evaporated during anaerobic digestion (m^3)
        heating_input_energy : float
            Energy required to maintain the anaerobic digester's temperature (MJ).
        methane_generation_volume : float
            Volume of all methane generated during anaerobic digestion (m^3).
        methane_leakage_mass : float
            Mass of all methane generated during anaerobic digestion (m^3).
        minimum_digester_volume : float
            Minimum volume of manure allowed to be left in the anaerobic digester (m^3).
        top_cover_volume : float
            Headspace volume above manure inside digester where biogas collects (m^3).
        simulation_day : int
            The current simulation day.

        """
        data_origin_function = self._report_anaerobic_digester_outputs.__name__
        self._report_manure_stream(self._manure_in_digester, "", simulation_day)

        self._report_processor_output(
            "biogas", biogas, data_origin_function, MeasurementUnits.KILOGRAMS, simulation_day
        )
        self._report_processor_output(
            "methane_leakage_mass",
            methane_leakage_mass,
            data_origin_function,
            MeasurementUnits.KILOGRAMS,
            simulation_day,
        )
        self._report_processor_output(
            "methane_generation_volume",
            methane_generation_volume,
            data_origin_function,
            MeasurementUnits.CUBIC_METERS,
            simulation_day,
        )
        self._report_processor_output(
            "evaporated_water",
            evaporated_water,
            data_origin_function,
            MeasurementUnits.CUBIC_METERS,
            simulation_day,
        )
        self._report_processor_output(
            "minimum_digester_volume",
            minimum_digester_volume,
            data_origin_function,
            MeasurementUnits.CUBIC_METERS,
            simulation_day,
        )
        self._report_processor_output(
            "top_cover_volume",
            top_cover_volume,
            data_origin_function,
            MeasurementUnits.CUBIC_METERS,
            simulation_day,
        )
        self._report_processor_output(
            "heating_input_energy",
            heating_input_energy,
            data_origin_function,
            MeasurementUnits.MEGAJOULES,
            simulation_day,
        )
        self._report_processor_output(
            "biogas_energy_content",
            biogas_energy_content,
            data_origin_function,
            MeasurementUnits.MEGAJOULES,
            simulation_day,
        )

    @staticmethod
    def _calculate_specific_input_energy(
        average_temperature: float, moisture_fraction: float, temperature_set_point: float
    ) -> float:
        """
        Calculates the energy required to maintain anaerobic digestion temperature at set point.

        Parameters
        ----------
        average_temperature : float
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
        effluent_temperature = AnaerobicDigester._bind_influent_temperature(average_temperature)
        influent_heat_capacity = AnaerobicDigester._calculate_manure_heat_capacity(
            average_temperature, moisture_fraction
        )
        anaerobic_digester_heat_capacity = AnaerobicDigester._calculate_manure_heat_capacity(
            temperature_set_point, moisture_fraction
        )

        average_heat_capacity = (influent_heat_capacity + anaerobic_digester_heat_capacity) / 2.0
        heating_input_energy = average_heat_capacity * (temperature_set_point - effluent_temperature)
        return heating_input_energy

    @staticmethod
    def _bind_influent_temperature(average_temperature: float) -> float:
        """
        Lower-bounds the influent temperature of manure based on the average ambient temperature.

        Parameters
        ----------
        average_temperature : float
            Average ambient temperature (degrees C).

        Returns
        -------
        float
            The bound temperature of influent manure (degrees C).

        """
        return max(average_temperature, ManureConstants.MINIMUM_INFLUENT_TEMPERATURE)

    @staticmethod
    def _calculate_manure_heat_capacity(temperature: float, moisture_fraction: float) -> float:
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

    @staticmethod
    def _calculate_CSTR_methane_volume(total_volatile_solids: float) -> float:
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

    @staticmethod
    def _calculate_methane_leakage(generated_methane_mass: float, leakage_fraction: float) -> float:
        """
        Calculates the mass of methane lost from an anaerobic digester as leakage.

        Parameters
        ----------
        generated_methane_mass : float
            Amount of methane generated within the digester (kg).
        leakage_fraction : float
            Fraction of generated methane that escapes as leakage (unitless).

        Returns
        -------
        float
            Mass of methane lost as leakage (kg).

        """
        return generated_methane_mass * leakage_fraction

    @staticmethod
    def _calculate_methane_energy_content(methane_mass: float) -> float:
        """
        Calculates energy content of methane generated in an anaerobic digester.

        Parameters
        ----------
        methane_mass : float
            Methane generation mass (kg).

        Returns
        -------
        float
            Methane energy content (MJ).

        """
        return methane_mass * ManureConstants.METHANE_ENERGY_DENSITY
