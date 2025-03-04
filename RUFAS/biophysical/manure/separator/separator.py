from dataclasses import asdict
from RUFAS.biophysical.manure.processor import Processor
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.time import Time
from RUFAS.units import MeasurementUnits


class Separator(Processor):
    """
    A manure processor that separates a portion of solids from manure.

    Parameters
    ----------
    name : str
        The name of the separator.
    percent_dry_solids : float
        The dry matter content (percent DM) of separated manure solids.
    ammoniacal_nitrogen_efficiency : float
        The efficiency of the separator in removing ammoniacal nitrogen from the manure.
    nitrogen_efficiency : float
        The efficiency of the separator in removing nitrogen from the manure.
    phosphorus_efficiency : float
        The efficiency of the separator in removing phosphorus from the manure.
    potassium_efficiency : float
        The efficiency of the separator in removing potassium from the manure.
    ash_efficiency : float
        The efficiency of the separator in removing ash from the manure.
    volatile_solids_efficiency : float
        The efficiency of the separator in removing volatile solids from the manure.
    total_solids_efficiency : float
        The efficiency of the separator in removing total solids from the manure.

    Attributes
    ----------
    is_housing_emissions_calculator : bool = False
        A flag to indicate if the processor is a housing emissions calculator. Will always be false for a separator.
    name : str
        The name of the separator.
    prefix : str
        The prefix to be used for naming output variables.
    percent_dry_solids : float
        The dry matter content (percent DM) of separated manure solids.
    ammoniacal_nitrogen_efficiency : float
        The efficiency of the separator in removing ammoniacal nitrogen from the manure.
    nitrogen_efficiency : float
        The efficiency of the separator in removing nitrogen from the manure.
    phosphorus_efficiency : float
        The efficiency of the separator in removing phosphorus from the manure.
    potassium_efficiency : float
        The efficiency of the separator in removing potassium from the manure.
    ash_efficiency : float
        The efficiency of the separator in removing ash from the manure.
    volatile_solids_efficiency : float
        The efficiency of the separator in removing volatile solids from the manure.
    total_solids_efficiency : float
        The efficiency of the separator in removing total solids from the manure.
    om : OutputManager
        The output manager instance used to store and manage output data.

    """

    def __init__(
        self,
        name: str,
        percent_dry_solids: float,
        ammoniacal_nitrogen_efficiency: float,
        nitrogen_efficiency: float,
        phosphorus_efficiency: float,
        potassium_efficiency: float,
        ash_efficiency: float,
        volatile_solids_efficiency: float,
        total_solids_efficiency: float,
    ) -> None:
        """Initializes a new Separator."""
        super().__init__(name=name, is_housing_emissions_calculator=False)
        self.held_manure: ManureStream | None = None
        self.percent_dry_solids: float = percent_dry_solids
        self.ammoniacal_nitrogen_efficiency: float = ammoniacal_nitrogen_efficiency
        self.nitrogen_efficiency: float = nitrogen_efficiency
        self.phosphorus_efficiency: float = phosphorus_efficiency
        self.potassium_efficiency: float = potassium_efficiency
        self.ash_efficiency: float = ash_efficiency
        self.volatile_solids_efficiency: float = volatile_solids_efficiency
        self.total_solids_efficiency: float = total_solids_efficiency

    def receive_manure(self, manure: ManureStream) -> None:
        """
        Takes in manure to be processed.

        Parameters
        ----------
        manure : ManureStream
            The manure to be processed.

        """
        if self.held_manure is None:
            self.held_manure = manure
        else:
            self.held_manure += manure

    def process_manure(self, conditions: CurrentDayConditions, time: Time) -> dict[str, ManureStream]:
        """
        Executes the daily separation of solids from the manure and returns the solid and liquid portions.

        Parameters
        ----------
        conditions : CurrentDayConditions
            Current weather and environmental conditions that manure is being processed in.
        time : Time
            Time instance containing the simulations temporal information.

        Returns
        -------
        dict[str, ManureStream]
            A dictionary containing:
            - "solid" : ManureStream
                The solid portion of the separated manure.
            - "liquid" : ManureStream
                The liquid portion of the separated manure.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self.process_manure.__name__,
            "prefix": self._prefix,
            "simulation_day": time.simulation_day,
        }
        if not self.held_manure:
            self._om.add_variable("empty_separator_output", {}, {**info_map, "units": MeasurementUnits.UNITLESS})
            return {}
        solid_manure_total_solids = self.held_manure.total_solids * self.total_solids_efficiency
        solid_manure_total_mass = solid_manure_total_solids / self.percent_dry_solids
        solid_manure_water = solid_manure_total_mass - solid_manure_total_solids
        solid_manure_volume = (solid_manure_water + solid_manure_total_solids) / ManureConstants.SOLID_MANURE_DENSITY
        solid_manure_stream = ManureStream(
            water=solid_manure_water,
            ammoniacal_nitrogen=self.held_manure.ammoniacal_nitrogen * self.ammoniacal_nitrogen_efficiency,
            nitrogen=self.held_manure.nitrogen * self.nitrogen_efficiency,
            phosphorus=self.held_manure.phosphorus * self.phosphorus_efficiency,
            potassium=self.held_manure.potassium * self.potassium_efficiency,
            ash=self.held_manure.ash * self.ash_efficiency,
            non_degradable_volatile_solids=self.held_manure.non_degradable_volatile_solids
            * self.volatile_solids_efficiency,
            degradable_volatile_solids=self.held_manure.degradable_volatile_solids * self.volatile_solids_efficiency,
            total_solids=solid_manure_total_solids,
            volume=solid_manure_volume,
            pen_manure_data=None,
        )
        solid_stream_name = "SeparatedSolids"
        self._log_manure_stream(solid_manure_stream, solid_stream_name, time)

        liquid_manure_water = self.held_manure.water - solid_manure_water
        liquid_manure_total_solids = self.held_manure.total_solids * (1 - self.total_solids_efficiency)
        liquid_manure_volume = (
            liquid_manure_water + liquid_manure_total_solids
        ) / ManureConstants.LIQUID_MANURE_DENSITY
        liquid_manure_stream = ManureStream(
            water=liquid_manure_water,
            ammoniacal_nitrogen=self.held_manure.ammoniacal_nitrogen * (1 - self.ammoniacal_nitrogen_efficiency),
            nitrogen=self.held_manure.nitrogen * (1 - self.nitrogen_efficiency),
            phosphorus=self.held_manure.phosphorus * (1 - self.phosphorus_efficiency),
            potassium=self.held_manure.potassium * (1 - self.potassium_efficiency),
            ash=self.held_manure.ash * (1 - self.ash_efficiency),
            non_degradable_volatile_solids=self.held_manure.non_degradable_volatile_solids
            * (1 - self.volatile_solids_efficiency),
            degradable_volatile_solids=self.held_manure.degradable_volatile_solids
            * (1 - self.volatile_solids_efficiency),
            total_solids=liquid_manure_total_solids,
            volume=liquid_manure_volume,
            pen_manure_data=None,
        )
        liquid_stream_name = "SeparatedLiquid"
        self._log_manure_stream(liquid_manure_stream, liquid_stream_name, time)

        self.clear_held_manure()

        return {"solid": solid_manure_stream, "liquid": liquid_manure_stream}

    def clear_held_manure(self) -> None:
        """Clears the held manure stream."""
        self.held_manure = None

    def _log_manure_stream(self, manure_stream: ManureStream, stream_name: str, time: Time) -> None:
        """
        Logs the manure stream data to Output Manager.

        Parameters
        ----------
        manure_stream : ManureStream
            The manure stream to log.
        stream_name : str
            The name of the manure stream being logged.

        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._log_manure_stream.__name__,
            "prefix": self._prefix,
            "simulation_day": time.simulation_day,
        }
        manure_stream_units = {
            "water": MeasurementUnits.KILOGRAMS,
            "ammoniacal_nitrogen": MeasurementUnits.KILOGRAMS,
            "nitrogen": MeasurementUnits.KILOGRAMS,
            "phosphorus": MeasurementUnits.KILOGRAMS,
            "potassium": MeasurementUnits.KILOGRAMS,
            "ash": MeasurementUnits.KILOGRAMS,
            "non_degradable_volatile_solids": MeasurementUnits.KILOGRAMS,
            "degradable_volatile_solids": MeasurementUnits.KILOGRAMS,
            "total_solids": MeasurementUnits.KILOGRAMS,
            "volume": MeasurementUnits.CUBIC_METERS,
            "mass": MeasurementUnits.KILOGRAMS,
        }
        manure_stream_dict = asdict(manure_stream)
        for key, value in manure_stream_dict.items():
            if key != "pen_manure_data":
                self._om.add_variable(
                    f"{stream_name}.manure_{key}", value, {**info_map, "units": manure_stream_units[key]}
                )
