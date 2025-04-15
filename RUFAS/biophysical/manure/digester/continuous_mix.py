from dataclasses import replace

from RUFAS.biophysical.manure.digester.digester import Digester
from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits
from RUFAS.general_constants import GeneralConstants


"""Volumetric ratio of carbon dioxide to methane generated during anaerobic digestion
    (m^3 carbon dioxide / m^3 methane)."""
CARBON_DIOXIDE_TO_METHANE_RATIO: float = 4 / 6

"""Factor by which total ammoniacal nitrogen content is increased by the anaerobic digestion process (unitless)."""
TAN_INCREASE_FACTOR = 1.60

"""Value of R in the ideal gas law (L·atm/(mol·K)."""
IDEAL_GAS_LAW_R = 0.0821

"""Molar mass of methane (g)."""
METHANE_MOLAR_MASS = 16.04

"""Molar mass of carbon dioxide (g)."""
CARBON_DIOXIDE_MOLAR_MASS = 44.01


class ContinuousMix(Digester):
    """
    Defines the behaviors and attributes of an anaerobic digester type, specifically a continuous stirred tank reactor.

    Parameters
    ----------
    name : str
        Unique identifier of the anaerobic digester.
    temperature_set_point : float
        Temperature set point for the anaerobic digestion (°C).
    hydraulic_retention_time : int
        Number of days manure spends in the anaerobic digester (days).
    biogas_leakage_fraction : float
        Fraction of biogas generated in the anaerobic digester that escapes to the atmosphere through unintended
        leakage and is not collected by the gas capture system (unitless).

    Attributes
    ----------
    _manure_in_digester : ManureStream
        The total amount of manure received by an anaerobic digester in a single day.
    _temperature_set_point : float
        Temperature set point for the anaerobic digestion (°C).
    _hydraulic_retention_time : int
        Number of days manure spends in the anaerobic digester (days).
    _biogas_leakage_fraction : float
        Fraction of methane generated in the anaerobic digester that escapes to the atmosphere through unintended
        leakage and is not collected by the gas capture system (unitless).

    """

    def __init__(
        self,
        name: str,
        temperature_set_point: float,
        hydraulic_retention_time: int,
        biogas_leakage_fraction: float,
    ) -> None:
        super().__init__(name=name, is_housing_emissions_calculator=False)
        self._manure_in_digester: ManureStream = ManureStream.make_empty_manure_stream()
        self._temperature_set_point: float = temperature_set_point
        self._hydraulic_retention_time: int = hydraulic_retention_time
        self._biogas_leakage_fraction: float = biogas_leakage_fraction

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
                captured_biogas_volume=0.0,
                captured_methane_volume=0.0,
                methane_leakage_volume=0.0,
                simulation_day=time.simulation_day,
            )
            return {}

        self._manure_in_digester.ammoniacal_nitrogen = min(
            self._manure_in_digester.ammoniacal_nitrogen * TAN_INCREASE_FACTOR, self._manure_in_digester.nitrogen
        )

        generated_methane_mass, generated_methane_volume = self._calculate_generated_methane()
        generated_carbon_dioxide_mass, generated_carbon_dioxide_volume = self._calculate_generated_carbon_dioxide(
            generated_methane_volume
        )

        total_biogas_volume = generated_methane_volume + generated_carbon_dioxide_volume
        captured_biogas_volume = total_biogas_volume * (1 - self._biogas_leakage_fraction)

        total_volatile_solids_destruction = generated_methane_mass + generated_carbon_dioxide_mass
        self._manure_in_digester = self._destroy_volatile_solids(total_volatile_solids_destruction, time)
        self._manure_in_digester.volume -= total_volatile_solids_destruction / ManureConstants.SLURRY_MANURE_DENSITY

        methane_leakage_volume = self._calculate_methane_leakage(
            generated_methane_volume, self._biogas_leakage_fraction
        )
        captured_methane_volume = generated_methane_volume - methane_leakage_volume

        self._report_anaerobic_digester_outputs(
            captured_biogas_volume=captured_biogas_volume,
            captured_methane_volume=captured_methane_volume,
            methane_leakage_volume=methane_leakage_volume,
            simulation_day=time.simulation_day,
        )

        digested_manure = replace(self._manure_in_digester)
        self._manure_in_digester = ManureStream.make_empty_manure_stream()
        return {"manure": digested_manure}

    def _calculate_generated_carbon_dioxide(self, generated_methane_volume: float) -> tuple[float, float]:
        """
        Calculate the mass and volume of carbon dioxide generated based on the generated methane volume.

        Parameters
        ----------
        generated_methane_volume : float
            The volume of generated methane from which carbon dioxide generation is calculated.

        Returns
        -------
        tuple[float, float]
            A tuple containing:
            - generated_carbon_dioxide_mass : float
                The calculated mass of generated carbon dioxide.
            - generated_carbon_dioxide_volume : float
                The calculated volume of generated carbon dioxide.

        Notes
        -----
        The calculation uses the ideal gas law and the ratio of carbon dioxide to methane to determine
        the density, mass, and volume of the generated carbon dioxide.
        """
        carbon_dioxide_density = CARBON_DIOXIDE_MOLAR_MASS / (
            IDEAL_GAS_LAW_R * (self._temperature_set_point + GeneralConstants.CELSIUS_TO_KELVIN)
        )
        generated_carbon_dioxide_mass = (
            generated_methane_volume * CARBON_DIOXIDE_TO_METHANE_RATIO * carbon_dioxide_density
        )
        generated_carbon_dioxide_volume = generated_carbon_dioxide_mass / carbon_dioxide_density
        return generated_carbon_dioxide_mass, generated_carbon_dioxide_volume

    def _calculate_generated_methane(self) -> tuple[float, float]:
        """
        Calculates the generated methane mass and volume.

        Uses the supplied temperature set point and volatile solids in the digester
        to compute the density of methane and its corresponding volume and mass.

        Returns
        -------
        tuple[float, float]
            A tuple containing:
            - generated_methane_mass (float): The mass of generated methane.
            - generated_methane_volume (float): The volume of generated methane.
        """
        methane_density = METHANE_MOLAR_MASS / (
            IDEAL_GAS_LAW_R * (self._temperature_set_point + GeneralConstants.CELSIUS_TO_KELVIN)
        )
        generated_methane_volume = self._calculate_CSTR_methane_volume(self._manure_in_digester.total_volatile_solids)
        generated_methane_mass = generated_methane_volume * methane_density
        return generated_methane_mass, generated_methane_volume

    def _destroy_volatile_solids(self, total_volatile_solids_destruction: float, time: RufasTime) -> ManureStream:
        """
        Adjusts the quantities of solids in the manure after volatile solids are destroyed.

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
        captured_biogas_volume: float,
        captured_methane_volume: float,
        methane_leakage_volume: float,
        simulation_day: int,
    ) -> None:
        """
        Reports manure that was digested and the amounts of different things that were lost or generated in the
        anaerobic digestion process.

        Parameters
        ----------
        captured_biogas_volume : float
            Captured biogas (assumed to be composed of 40% CO2, 60% CH4) volume after accounting for leakage
             on the current day (m^3).
        captured_methane_volume : float
            Capture methane volume on the current day, after accounting for leakage (m^3).
        methane_leakage_volume : float
            Volume of methane lost to the atmosphere through unintended leakage on the current day (m^3).
        simulation_day : int
            The current simulation day.

        """
        data_origin_function = self._report_anaerobic_digester_outputs.__name__
        self._report_manure_stream(self._manure_in_digester, "", simulation_day)

        self._report_processor_output(
            "captured_biogas_volume",
            captured_biogas_volume,
            data_origin_function,
            MeasurementUnits.CUBIC_METERS,
            simulation_day,
        )
        self._report_processor_output(
            "captured_methane_volume",
            captured_methane_volume,
            data_origin_function,
            MeasurementUnits.CUBIC_METERS,
            simulation_day,
        )
        self._report_processor_output(
            "methane_leakage_volume",
            methane_leakage_volume,
            data_origin_function,
            MeasurementUnits.CUBIC_METERS,
            simulation_day,
        )

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
        return total_volatile_solids * ManureConstants.ACHIEVABLE_METHANE_EMISSION

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
