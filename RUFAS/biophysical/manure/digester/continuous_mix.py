from dataclasses import replace

from RUFAS.biophysical.manure.digester.digester import Digester
from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits
from RUFAS.general_constants import GeneralConstants


class ContinuousMix(Digester):
    """
    Defines the behaviors and attributes of an anaerobic digester type, specifically a continuous stirred tank reactor.

    Parameters
    ----------
    name : str
        Unique identifier of the anaerobic digester.
    anaerobic_digestion_temperature_set_point : float
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
        anaerobic_digestion_temperature_set_point: float,
        hydraulic_retention_time: int,
        biogas_leakage_fraction: float,
    ) -> None:
        super().__init__(name=name, is_housing_emissions_calculator=False)
        self._manure_in_digester: ManureStream = ManureStream.make_empty_manure_stream()
        self._temperature_set_point: float = anaerobic_digestion_temperature_set_point
        self._hydraulic_retention_time: int = hydraulic_retention_time
        self._biogas_leakage_fraction: float = biogas_leakage_fraction

    def receive_manure(self, manure: ManureStream) -> None:
        """Receives and stores manure to be digested."""
        is_received_manure_valid = self.check_manure_stream_compatibility(manure)
        if is_received_manure_valid is False:
            raise ValueError(f"Continuous mix digester {self.name} received an invalid manure stream.")
        self._manure_in_digester += manure

    def process_manure(self, conditions: CurrentDayConditions, time: RufasTime) -> dict[str, ManureStream]:
        """Digests manure received on the current day."""
        if self._manure_in_digester.is_empty is True:
            self._report_continuous_mix_outputs(
                captured_biogas_volume=0.0,
                captured_methane_volume=0.0,
                methane_leakage_mass=0.0,
                simulation_day=time.simulation_day,
            )
            return {}

        self._manure_in_digester.ammoniacal_nitrogen = min(
            self._manure_in_digester.ammoniacal_nitrogen * ManureConstants.TAN_INCREASE_FACTOR,
            self._manure_in_digester.nitrogen,
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

        methane_leakage_mass, methane_leakage_volume = self._calculate_methane_leakage(
            generated_methane_mass, generated_methane_volume, self._biogas_leakage_fraction
        )
        captured_methane_volume = generated_methane_volume - methane_leakage_volume

        self._report_continuous_mix_outputs(
            captured_biogas_volume=captured_biogas_volume,
            captured_methane_volume=captured_methane_volume,
            methane_leakage_mass=methane_leakage_mass,
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
        carbon_dioxide_density = ManureConstants.CARBON_DIOXIDE_MOLAR_MASS / (
            GeneralConstants.IDEAL_GAS_LAW_R * (self._temperature_set_point + GeneralConstants.CELSIUS_TO_KELVIN)
        )
        generated_carbon_dioxide_mass = (
            generated_methane_volume * ManureConstants.CARBON_DIOXIDE_TO_METHANE_RATIO * carbon_dioxide_density
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
        methane_density = ManureConstants.METHANE_MOLAR_MASS / (
            GeneralConstants.IDEAL_GAS_LAW_R * (self._temperature_set_point + GeneralConstants.CELSIUS_TO_KELVIN)
        )
        generated_methane_volume = self._calculate_CSTR_methane_volume(
            self._manure_in_digester.total_volatile_solids, self._manure_in_digester.methane_production_potential
        )
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
                "total_non_degradable_volatile_solids": self._manure_in_digester.non_degradable_volatile_solids
                + self._manure_in_digester.bedding_non_degradable_volatile_solids,
                "total_volatile_solids": self._manure_in_digester.total_volatile_solids,
                "total_volatile_solids_destruction": total_volatile_solids_destruction,
            }
            err_name = f"Anerobic digester '{self.name}' attempted to destroy more volatile solids than available"
            err_msg = "Setting degradable volatile solids, non-degradable volatile solids, and total volatile solids "
            "pools to be 0.0."
            self._om.add_error(err_name, err_msg, info_map)
            degradable_volatile_solids = 0.0
            non_degradable_volatile_solids = 0.0
            bedding_non_degradable_volatile_solids = 0.0
        else:
            if self._manure_in_digester.total_volatile_solids <= 0.0:
                info_map = {
                    "class": self.__class__.__name__,
                    "function": self._destroy_volatile_solids.__name__,
                    "name": self.name,
                    "date": time.current_date.date(),
                    "simulation_day": time.simulation_day,
                    "total_volatile_solids": self._manure_in_digester.total_volatile_solids,
                    "total_manure_mass": self._manure_in_digester.mass,
                }
                self._om.add_warning(
                    f"Anaerobic digester '{self.name}' receieved manure containing 0 total volatile solids."
                    "Moving manure to next processor unchanged.",
                    f"Digester has {self._manure_in_digester.mass} kg manure"
                    f"and {self._manure_in_digester.total_volatile_solids} kg volatile solids.",
                    info_map,
                )
            manure_degradable_volatile_solids_frac = (
                (self._manure_in_digester.degradable_volatile_solids / self._manure_in_digester.total_volatile_solids)
                if self._manure_in_digester.total_volatile_solids > 0.0
                else 0.0
            )

            manure_non_degradable_volatile_solids_fraction = (
                (
                    self._manure_in_digester.non_degradable_volatile_solids
                    / self._manure_in_digester.total_volatile_solids
                )
                if self._manure_in_digester.total_volatile_solids > 0.0
                else 0.0
            )

            degradable_volatile_solids = self._manure_in_digester.degradable_volatile_solids - (
                total_volatile_solids_destruction * manure_degradable_volatile_solids_frac
            )
            non_degradable_volatile_solids = self._manure_in_digester.non_degradable_volatile_solids - (
                total_volatile_solids_destruction * manure_non_degradable_volatile_solids_fraction
            )
            bedding_non_degradable_volatile_solids = self._manure_in_digester.bedding_non_degradable_volatile_solids - (
                total_volatile_solids_destruction
                * (1 - manure_degradable_volatile_solids_frac - manure_non_degradable_volatile_solids_fraction)
            )

        return replace(
            self._manure_in_digester,
            degradable_volatile_solids=degradable_volatile_solids,
            non_degradable_volatile_solids=non_degradable_volatile_solids,
            bedding_non_degradable_volatile_solids=bedding_non_degradable_volatile_solids,
        )

    def _report_continuous_mix_outputs(
        self,
        captured_biogas_volume: float,
        captured_methane_volume: float,
        methane_leakage_mass: float,
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
        methane_leakage_mass : float
            The mass of methane lost to the atmosphere through unintended leakage on the current day (kg).
        simulation_day : int
            The current simulation day.

        """
        data_origin_function = self._report_continuous_mix_outputs.__name__
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
            "methane_leakage_mass",
            methane_leakage_mass,
            data_origin_function,
            MeasurementUnits.KILOGRAMS,
            simulation_day,
        )

    @staticmethod
    def _calculate_CSTR_methane_volume(total_volatile_solids: float, methane_production_potential: float) -> float:
        """
        Calculates volume of methane generated from a continuously-stirred tank reactor.

        Parameters
        ----------
        total_volatile_solids : float
            Total volatile solids contained in manure (kg).
        methane_production_potential : float
            Achievable emission of methane from dairy manure (m^3 methane / kg volatile solids).

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
        return total_volatile_solids * methane_production_potential

    @staticmethod
    def _calculate_methane_leakage(
        generated_methane_mass: float, generated_methane_volume: float, leakage_fraction: float
    ) -> tuple[float, float]:
        """
        Calculates the mass of methane lost from an anaerobic digester as leakage.

        Parameters
        ----------
        generated_methane_mass : float
            The mass of methane generated within the digester (kg).
        generated_methane_mass : float
            The volume of methane generated within the digester (m^3).
        leakage_fraction : float
            Fraction of generated methane that escapes as leakage (unitless).

        Returns
        -------
        tuple[float, float]
            - Mass of methane lost as leakage (kg).
            - Volume of methane lost as leakage (m^3).

        """
        return generated_methane_mass * leakage_fraction, generated_methane_volume * leakage_fraction
