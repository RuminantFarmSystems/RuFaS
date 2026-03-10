from dataclasses import asdict
from RUFAS.biophysical.manure.processor import Processor
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits


class Separator(Processor):
    """
    A manure processor that separates a portion of solids from manure.

    Parameters
    ----------
    name : str
        The name of the separator.
    separated_solids_dry_matter : float
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
    separated_solids_dry_matter : float
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
        separated_solids_dry_matter: float,
        ammoniacal_nitrogen_efficiency: float,
        nitrogen_efficiency: float,
        phosphorus_efficiency: float,
        potassium_efficiency: float,
        ash_efficiency: float,
        volatile_solids_efficiency: float,
        total_solids_efficiency: float,
        processor_type: str,
    ) -> None:
        """Initializes a new Separator."""
        super().__init__(name=name, is_housing_emissions_calculator=False)
        self.held_manure: ManureStream | None = None
        self.separated_solids_dry_matter: float = separated_solids_dry_matter
        self.ammoniacal_nitrogen_efficiency: float = ammoniacal_nitrogen_efficiency
        self.nitrogen_efficiency: float = nitrogen_efficiency
        self.phosphorus_efficiency: float = phosphorus_efficiency
        self.potassium_efficiency: float = potassium_efficiency
        self.ash_efficiency: float = ash_efficiency
        self.volatile_solids_efficiency: float = volatile_solids_efficiency
        self.total_solids_efficiency: float = total_solids_efficiency
        self.separator_type = processor_type
        self._prefix = f"Manure.{self.__class__.__name__}.{self.separator_type}.{self.name}"

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

    def process_manure(self, conditions: CurrentDayConditions, time: RufasTime) -> dict[str, ManureStream]:
        """
        Executes the daily separation of solids from the manure and returns the solid and liquid portions.

        Parameters
        ----------
        conditions : CurrentDayConditions
            Current weather and environmental conditions that manure is being processed in.
        time : RufasTime
            RufasTime instance containing the simulations temporal information.

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
        solid_manure_total_mass = solid_manure_total_solids / self.separated_solids_dry_matter
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
            methane_production_potential=self.held_manure.methane_production_potential,
            pen_manure_data=None,
            bedding_non_degradable_volatile_solids=self.held_manure.bedding_non_degradable_volatile_solids
            * self.volatile_solids_efficiency,
        )
        solid_stream_name = "SeparatedSolids"
        solid_manure_stream_dict = asdict(solid_manure_stream)
        solid_manure_stream_dict["mass"] = solid_manure_total_mass
        solid_manure_stream_dict["total_volatile_solids"] = solid_manure_stream.total_volatile_solids
        self._report_manure_stream(solid_manure_stream, solid_stream_name, time.simulation_day)

        liquid_manure_water = self.held_manure.water - solid_manure_water
        if liquid_manure_water <= 0.0:
            self._om.add_error(
                f"Liquid manure volume is {liquid_manure_water}",
                f"Separator '{self.name}' attempted to separate more water into manure solids fraction than was "
                "present in manure entering separator. The separated_solids_dry_matter "
                f"value for separator '{self.name}' may need to be increased.",
                {**info_map},
            )
            raise ValueError(
                f"Separator '{self.name}' attempted to separate more water into manure solids fraction than was "
                "present in manure entering separator. The separated_solids_dry_matter "
                f"value for separator '{self.name}' may need to be increased."
            )
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
            methane_production_potential=self.held_manure.methane_production_potential,
            pen_manure_data=None,
            bedding_non_degradable_volatile_solids=self.held_manure.bedding_non_degradable_volatile_solids
            * (1 - self.volatile_solids_efficiency),
        )
        liquid_stream_name = "SeparatedLiquid"
        self._report_manure_stream(liquid_manure_stream, liquid_stream_name, time.simulation_day)

        self.clear_held_manure()

        return {"solid": solid_manure_stream, "liquid": liquid_manure_stream}

    def clear_held_manure(self) -> None:
        """Clears the held manure stream."""
        self.held_manure = None
