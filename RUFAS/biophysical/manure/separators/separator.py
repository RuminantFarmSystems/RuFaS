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

    Attributes
    ----------
    is_housing_emissions_calculator : bool = False
        A flag to indicate if the processor is a housing emissions calculator. Will always be false for a separator.
    name : str
        The name of the separator.
    prefix : str
        The prefix to be used for naming output variables.
    water_efficiency : float
        The efficiency of the separator in removing water from the manure.
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
    total_volatile_solids_efficiency : float
        The efficiency of the separator in removing volatile solids from the manure.
    total_solids_efficiency : float
        The efficiency of the separator in removing total solids from the manure.

    """

    def __init__(self) -> None:
        """Initializes a new Separator."""
        super().__init__(is_housing_emissions_calculator=False)
        self._name: str
        self._prefix: str = f"{self.__class__.__name__}."
        self.held_manure: ManureStream | None = None
        self.water_efficiency: float = 0.0
        self.ammoniacal_nitrogen_efficiency: float = 0.0
        self.nitrogen_efficiency: float = 0.0
        self.phosphorus_efficiency: float = 0.0
        self.potassium_efficiency: float = 0.0
        self.ash_efficiency: float = 0.0
        self.total_volatile_solids_efficiency: float = 0.0
        self.total_solids_efficiency: float = 0.0

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
        om = OutputManager()
        if not self.held_manure:
            info_map = info_map | {"units": MeasurementUnits.UNITLESS}
            om.add_variable("empty_separator_output", {}, info_map)
            return {}
        solid_manure = ManureStream(
            water=self.held_manure.water * self.water_efficiency,
            ammoniacal_nitrogen=self.held_manure.ammoniacal_nitrogen * self.ammoniacal_nitrogen_efficiency,
            nitrogen=self.held_manure.nitrogen * self.nitrogen_efficiency,
            phosphorus=self.held_manure.phosphorus * self.phosphorus_efficiency,
            potassium=self.held_manure.potassium * self.potassium_efficiency,
            ash=self.held_manure.ash * self.ash_efficiency,
            non_degradable_volatile_solids=self.held_manure.non_degradable_volatile_solids
            * self.total_volatile_solids_efficiency,
            degradable_volatile_solids=self.held_manure.degradable_volatile_solids
            * self.total_volatile_solids_efficiency,
            total_solids=self.held_manure.total_solids * self.config.total_solids_efficiency,
            volume=self.held_manure.volume * ManureConstants.SOLID_MANURE_DENSITY,  # TODO: Check if this is correct
        )
        solid_manure_units = {
            "solid_manure_water": MeasurementUnits.KILOGRAMS,
            "solid_manure_ammoniacal_nitrogen": MeasurementUnits.KILOGRAMS,
            "solid_manure_nitrogen": MeasurementUnits.KILOGRAMS,
            "solid_manure_phosphorus": MeasurementUnits.KILOGRAMS,
            "solid_manure_potassium": MeasurementUnits.KILOGRAMS,
            "solid_manure_ash": MeasurementUnits.KILOGRAMS,
            "solid_manure_non_degradable_volatile_solids": MeasurementUnits.KILOGRAMS,
            "solid_manure_degradable_volatile_solids": MeasurementUnits.KILOGRAMS,
            "solid_manure_total_solids": MeasurementUnits.KILOGRAMS,
            "solid_manure_volume": MeasurementUnits.CUBIC_METERS,
            "solid_manure_mass": MeasurementUnits.KILOGRAMS,
            "simulation_day": MeasurementUnits.SIMULATION_DAY,
        }
        info_map = info_map | solid_manure_units
        solid_stream_name = f"{self._prefix}.Solids.{self._name}"
        om.add_variable(f"{solid_stream_name}.water", solid_manure.water, info_map)
        om.add_variable(f"{solid_stream_name}.ammoniacal_nitrogen", solid_manure.ammoniacal_nitrogen, info_map)
        om.add_variable(f"{solid_stream_name}.nitrogen", solid_manure.nitrogen, info_map)
        om.add_variable(f"{solid_stream_name}.phosphorus", solid_manure.phosphorus, info_map)
        om.add_variable(f"{solid_stream_name}.potassium", solid_manure.potassium, info_map)
        om.add_variable(f"{solid_stream_name}.ash", solid_manure.ash, info_map)
        om.add_variable(f"{solid_stream_name}.non_degradable_volatile_solids",
                        solid_manure.non_degradable_volatile_solids, info_map)
        om.add_variable(f"{solid_stream_name}.degradable_volatile_solids", solid_manure.degradable_volatile_solids,
                        info_map)
        om.add_variable(f"{solid_stream_name}.total_solids", solid_manure.total_solids, info_map)
        om.add_variable(f"{solid_stream_name}.volume", solid_manure.volume, info_map)
        om.add_variable(f"{solid_stream_name}.mass", solid_manure.mass, info_map)

        liquid_manure_units = {
            "liquid_manure_water": MeasurementUnits.KILOGRAMS,
            "liquid_manure_ammoniacal_nitrogen": MeasurementUnits.KILOGRAMS,
            "liquid_manure_nitrogen": MeasurementUnits.KILOGRAMS,
            "liquid_manure_phosphorus": MeasurementUnits.KILOGRAMS,
            "liquid_manure_potassium": MeasurementUnits.KILOGRAMS,
            "liquid_manure_ash": MeasurementUnits.KILOGRAMS,
            "liquid_manure_non_degradable_volatile_solids": MeasurementUnits.KILOGRAMS,
            "liquid_manure_degradable_volatile_solids": MeasurementUnits.KILOGRAMS,
            "liquid_manure_total_solids": MeasurementUnits.KILOGRAMS,
            "liquid_manure_volume": MeasurementUnits.CUBIC_METERS,
            "liquid_manure_mass": MeasurementUnits.KILOGRAMS,
            "simulation_day": MeasurementUnits.SIMULATION_DAY,
        }
        info_map = info_map | liquid_manure_units
        liquid_manure_name = f"{self._prefix}.Liquid.{self._name}"
        liquid_manure = ManureStream(
            water=self.held_manure.water * (1 - self.water_efficiency),
            ammoniacal_nitrogen=self.held_manure.ammoniacal_nitrogen * (1 - self.ammoniacal_nitrogen_efficiency),
            nitrogen=self.held_manure.nitrogen * (1 - self.nitrogen_efficiency),
            phosphorus=self.held_manure.phosphorus * (1 - self.phosphorus_efficiency),
            potassium=self.held_manure.potassium * (1 - self.potassium_efficiency),
            ash=self.held_manure.ash * (1 - self.ash_efficiency),
            non_degradable_volatile_solids=self.held_manure.non_degradable_volatile_solids
            * (1 - self.volatile_solids_efficiency),
            degradable_volatile_solids=self.held_manure.degradable_volatile_solids
            * (1 - self.volatile_solids_efficiency),
            total_solids=self.held_manure.total_solids * (1 - self.total_solids_efficiency),
            volume=self.held_manure.volume * ManureConstants.LIQUID_MANURE_DENSITY,  # TODO: Check if this is correct
        )
        om.add_variable(f"{liquid_manure_name}.water", liquid_manure.water, info_map)
        om.add_variable(f"{liquid_manure_name}.ammoniacal_nitrogen", liquid_manure.ammoniacal_nitrogen, info_map)
        om.add_variable(f"{liquid_manure_name}.nitrogen", liquid_manure.nitrogen, info_map)
        om.add_variable(f"{liquid_manure_name}.phosphorus", liquid_manure.phosphorus, info_map)
        om.add_variable(f"{liquid_manure_name}.potassium", liquid_manure.potassium, info_map)
        om.add_variable(f"{liquid_manure_name}.ash", liquid_manure.ash, info_map)
        om.add_variable(f"{liquid_manure_name}.non_degradable_volatile_solids",
                        liquid_manure.non_degradable_volatile_solids, info_map)
        om.add_variable(f"{liquid_manure_name}.degradable_volatile_solids", liquid_manure.degradable_volatile_solids,
                        info_map)
        om.add_variable(f"{liquid_manure_name}.total_solids", liquid_manure.total_solids, info_map)
        om.add_variable(f"{liquid_manure_name}.volume", liquid_manure.volume, info_map)
        om.add_variable(f"{liquid_manure_name}.mass", liquid_manure.mass, info_map)

        om.add_variable(f"{self._prefix}.{self._name}.simulation_day", time.simulation_day, info_map)

        return {"solid": solid_manure, "liquid": liquid_manure}
