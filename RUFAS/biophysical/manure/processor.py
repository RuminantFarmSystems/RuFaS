from abc import ABC, abstractmethod

from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.time import Time
from RUFAS.output_manager import OutputManager


class Processor(ABC):
    """
    Base class for all manure processors.

    Parameters
    ----------
    name : str
        Unique identifier of the processor.
    is_housing_emissions_calculator : bool
        Indicates if a Processor calculates housing emissions.

    Attributes
    ----------
    name : str
        Unique identifier of the processor used to label outputs.
    is_housing_emissions_calculator : bool
        If true, processor will only accept ManureStreams with non-None PenManureData, if false then vice versa.
    _om : OutputManager
        Instance of the OutputManager.

    Methods
    -------
    receive_manure(manure: ManureStream) -> None
        Entry point of manure into the processor.
    process_manure(conditions: CurrentDayConditions, time: Time) -> dict[str, ManureStream]
        Handles the daily operations for the processor.

    """

    def __init__(self, name: str, is_housing_emissions_calculator: bool) -> None:
        """Initializes a new Processor."""
        self.name = name
        self.is_housing_emissions_calculator = is_housing_emissions_calculator
        self._om = OutputManager()

    @abstractmethod
    def receive_manure(self, manure: ManureStream) -> None:
        """
        Takes in manure to be processed.

        Parameters
        ----------
        manure : ManureStream
            The manure to be processed.

        Raises
        ------
        ValueError
            If the ManureStream is incompatible with the processor receiving it.

        """
        pass

    @abstractmethod
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
        dict[str, ManureStream]
            Mapping between classification of manure coming out of this processor to the ManureStream containing the
            manure information. If the processor is a separator, the classifications are "solid" and "liquid". Otherwise
            the only classification is "manure".

        """
        pass

    def check_manure_stream_compatibility(self, manure_stream: ManureStream) -> bool:
        """
        Checks if a ManureStream is capable of being processed.

        Parameters
        ----------
        manure_stream : ManureStream
            The ManureStream instance being checked for compatibility.

        Returns
        -------
        bool
            True if the ManureStream can be processed by the Processor, otherwise false.

        """
        is_valid_housing_emissions_calculator = (
            True if (self.is_housing_emissions_calculator and manure_stream.pen_manure_data is not None) else False
        )
        is_valid_non_housing_emissions_calculator = (
            True if (not self.is_housing_emissions_calculator and manure_stream.pen_manure_data is None) else False
        )

        return is_valid_housing_emissions_calculator ^ is_valid_non_housing_emissions_calculator
