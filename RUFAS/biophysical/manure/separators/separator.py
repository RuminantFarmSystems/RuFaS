from RUFAS.biophysical.manure.processor import Processor
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.output_manager import OutputManager
from RUFAS.time import Time
from RUFAS.units import MeasurementUnits


class Separator(Processor):
    """
    A manure processor that separates a portion of solids from manure.

    Parameters
    ----------
    name : str = ""
        The name of the separator.
    percent_dry_solids : float = 0.0
        The dry matter content (percent DM) of separated manure solids.
    ammoniacal_nitrogen_efficiency : float = 0.0
        The efficiency of the separator in removing ammoniacal nitrogen from the manure.
    nitrogen_efficiency : float = 0.0
        The efficiency of the separator in removing nitrogen from the manure.
    phosphorus_efficiency : float = 0.0
        The efficiency of the separator in removing phosphorus from the manure.
    potassium_efficiency : float = 0.0
        The efficiency of the separator in removing potassium from the manure.
    ash_efficiency : float = 0.0
        The efficiency of the separator in removing ash from the manure.
    volatile_solids_efficiency : float = 0.0
        The efficiency of the separator in removing volatile solids from the manure.
    total_solids_efficiency : float = 0.0
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
        name: str = "",
        percent_dry_solids: float = 0.0,
        ammoniacal_nitrogen_efficiency: float = 0.0,
        nitrogen_efficiency: float = 0.0,
        phosphorus_efficiency: float = 0.0,
        potassium_efficiency: float = 0.0,
        ash_efficiency: float = 0.0,
        volatile_solids_efficiency: float = 0.0,
        total_solids_efficiency: float = 0.0,
    ) -> None:
        """Initializes a new Separator."""
        super().__init__(name=name, is_housing_emissions_calculator=False)
        self._name: str = name
        self._prefix: str = f"{self.__class__.__name__}"
        self.held_manure: ManureStream | None = None
        self.percent_dry_solids: float = percent_dry_solids
        self.ammoniacal_nitrogen_efficiency: float = ammoniacal_nitrogen_efficiency
        self.nitrogen_efficiency: float = nitrogen_efficiency
        self.phosphorus_efficiency: float = phosphorus_efficiency
        self.potassium_efficiency: float = potassium_efficiency
        self.ash_efficiency: float = ash_efficiency
        self.volatile_solids_efficiency: float = volatile_solids_efficiency
        self.total_solids_efficiency: float = total_solids_efficiency
        self.om = OutputManager()

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
        Executes the daily manure processing operations.
        For this class, it separates a portion of solids from the manure and returns the solid and liquid portions.

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
        }
        if not self.held_manure:
            self.om.add_variable("empty_separator_output", {}, {**info_map, "units": MeasurementUnits.UNITLESS})
            return {}
        solid_manure_total_solids = self.held_manure.total_solids * self.total_solids_efficiency
        solid_manure_total_mass = solid_manure_total_solids / self.percent_dry_solids
        solid_manure_water = solid_manure_total_mass - solid_manure_total_solids
        solid_manure_volume = (solid_manure_water + solid_manure_total_solids) / ManureConstants.SOLID_MANURE_DENSITY
        solid_manure = ManureStream(
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
        solid_stream_name = f"{self._prefix}.SeparatedSolids.{self._name}"
        self.om.add_variable(
            f"{solid_stream_name}.water", solid_manure.water, {**info_map, "units": MeasurementUnits.KILOGRAMS}
        )
        self.om.add_variable(
            f"{solid_stream_name}.ammoniacal_nitrogen",
            solid_manure.ammoniacal_nitrogen,
            {**info_map, "units": MeasurementUnits.KILOGRAMS},
        )
        self.om.add_variable(
            f"{solid_stream_name}.nitrogen", solid_manure.nitrogen, {**info_map, "units": MeasurementUnits.KILOGRAMS}
        )
        self.om.add_variable(
            f"{solid_stream_name}.phosphorus",
            solid_manure.phosphorus,
            {**info_map, "units": MeasurementUnits.KILOGRAMS},
        )
        self.om.add_variable(
            f"{solid_stream_name}.potassium", solid_manure.potassium, {**info_map, "units": MeasurementUnits.KILOGRAMS}
        )
        self.om.add_variable(
            f"{solid_stream_name}.ash", solid_manure.ash, {**info_map, "units": MeasurementUnits.KILOGRAMS}
        )
        self.om.add_variable(
            f"{solid_stream_name}.non_degradable_volatile_solids",
            solid_manure.non_degradable_volatile_solids,
            {**info_map, "units": MeasurementUnits.KILOGRAMS},
        )
        self.om.add_variable(
            f"{solid_stream_name}.degradable_volatile_solids",
            solid_manure.degradable_volatile_solids,
            {**info_map, "units": MeasurementUnits.KILOGRAMS},
        )
        self.om.add_variable(
            f"{solid_stream_name}.total_solids",
            solid_manure.total_solids,
            {**info_map, "units": MeasurementUnits.KILOGRAMS},
        )
        self.om.add_variable(
            f"{solid_stream_name}.volume", solid_manure.volume, {**info_map, "units": MeasurementUnits.CUBIC_METERS}
        )
        self.om.add_variable(
            f"{solid_stream_name}.mass", solid_manure.mass, {**info_map, "units": MeasurementUnits.KILOGRAMS}
        )

        liquid_manure_name = f"{self._prefix}.SeparatedLiquid.{self._name}"
        liquid_manure_water = self.held_manure.water - solid_manure_water
        liquid_manure_total_solids = self.held_manure.total_solids * (1 - self.total_solids_efficiency)
        liquid_manure_volume = (
            liquid_manure_water + liquid_manure_total_solids
        ) / ManureConstants.LIQUID_MANURE_DENSITY
        liquid_manure = ManureStream(
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
        self.om.add_variable(
            f"{liquid_manure_name}.water", liquid_manure.water, {**info_map, "units": MeasurementUnits.KILOGRAMS}
        )
        self.om.add_variable(
            f"{liquid_manure_name}.ammoniacal_nitrogen",
            liquid_manure.ammoniacal_nitrogen,
            {**info_map, "units": MeasurementUnits.KILOGRAMS},
        )
        self.om.add_variable(
            f"{liquid_manure_name}.nitrogen", liquid_manure.nitrogen, {**info_map, "units": MeasurementUnits.KILOGRAMS}
        )
        self.om.add_variable(
            f"{liquid_manure_name}.phosphorus",
            liquid_manure.phosphorus,
            {**info_map, "units": MeasurementUnits.KILOGRAMS},
        )
        self.om.add_variable(
            f"{liquid_manure_name}.potassium",
            liquid_manure.potassium,
            {**info_map, "units": MeasurementUnits.KILOGRAMS},
        )
        self.om.add_variable(
            f"{liquid_manure_name}.ash", liquid_manure.ash, {**info_map, "units": MeasurementUnits.KILOGRAMS}
        )
        self.om.add_variable(
            f"{liquid_manure_name}.non_degradable_volatile_solids",
            liquid_manure.non_degradable_volatile_solids,
            {**info_map, "units": MeasurementUnits.KILOGRAMS},
        )
        self.om.add_variable(
            f"{liquid_manure_name}.degradable_volatile_solids",
            liquid_manure.degradable_volatile_solids,
            {**info_map, "units": MeasurementUnits.KILOGRAMS},
        )
        self.om.add_variable(
            f"{liquid_manure_name}.total_solids",
            liquid_manure.total_solids,
            {**info_map, "units": MeasurementUnits.KILOGRAMS},
        )
        self.om.add_variable(
            f"{liquid_manure_name}.volume", liquid_manure.volume, {**info_map, "units": MeasurementUnits.CUBIC_METERS}
        )
        self.om.add_variable(
            f"{liquid_manure_name}.mass", liquid_manure.mass, {**info_map, "units": MeasurementUnits.KILOGRAMS}
        )

        self.om.add_variable(
            f"{self._prefix}.{self._name}.simulation_day",
            time.simulation_day,
            {**info_map, "units": MeasurementUnits.SIMULATION_DAY},
        )

        self.clear_held_manure()

        return {"solid": solid_manure, "liquid": liquid_manure}

    def clear_held_manure(self) -> None:
        """Clears the held manure stream."""
        self.held_manure = None
