from dataclasses import dataclass
from RUFAS.biophysical.manure.processor import Processor
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.time import Time


@dataclass
class SeparatorConfig:
    """
    Base configuration for a manure separator.

    Attributes
    ----------
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
    non_degradable_volatile_solids_efficiency : float
        The efficiency of the separator in removing non-degradable volatile solids from the manure.
    degradable_volatile_solids_efficiency : float
        The efficiency of the separator in removing degradable volatile solids from the manure.
    total_solids_efficiency : float
        The efficiency of the separator in removing total solids from the manure.
    """

    water_efficiency: float
    ammoniacal_nitrogen_efficiency: float
    nitrogen_efficiency: float
    phosphorus_efficiency: float
    potassium_efficiency: float
    ash_efficiency: float
    non_degradable_volatile_solids_efficiency: float
    degradable_volatile_solids_efficiency: float
    total_solids_efficiency: float


class Separator(Processor):
    """
    A manure processor that separates solids from liquids.

    Parameters
    ----------
    config : SeparatorConfig
        Configuration for the separator.
    is_housing_emissions_calculator : bool
        Indicates if a Processor calculates housing emissions.

    Attributes
    ----------
    config : SeparatorConfig
        Configuration for the separator.
    is_housing_emissions_calculator : bool
        If true, processor will only accept ManureStreams with non-None PenManureData, if false then vice versa.

    """

    def __init__(self, config: SeparatorConfig, is_housing_emissions_calculator: bool = False) -> None:
        """Initializes a new Separator."""
        super().__init__(is_housing_emissions_calculator)
        self.config: SeparatorConfig = config
        self.held_manure: ManureStream | None = None

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

        Parameters
        ----------
        conditions : CurrentDayConditions
            Current weather and environmental conditions that manure is being processed in.
        time : Time
            Time instance containing the simulations temporal information.

        Returns
        -------
        dict
            A dictionary containing:
            - "solid" : ManureStream
                The solid portion of the separated manure.
            - "liquid" : ManureStream
                The liquid portion of the separated manure.

        """
        if not self.held_manure:
            return {"solid": ManureStream(), "liquid": ManureStream()}
        return self._separate_manure()

    def _separate_manure(self) -> dict[str, ManureStream]:
        """
        Separates the held manure and returns the separated manure streams.

        This method should be implemented by subclasses to define the specific separation process.
        It is called only when `held_manure` is not None or zero.

        Returns
        -------
        dict
            A dictionary containing:
            - "solid" : ManureStream
                The solid portion of the separated manure.
            - "liquid" : ManureStream
                The liquid portion of the separated manure.

        Raises
        ------
        NotImplementedError
            If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement this method.")
