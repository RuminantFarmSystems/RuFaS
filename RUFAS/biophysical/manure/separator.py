from RUFAS.biophysical.manure.processor import Processor
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.time import Time


class BaseSeparator(Processor):
    """
    A manure processor that separates solids from liquids.

    Parameters
    ----------
    is_housing_emissions_calculator : bool
        Indicates if a Processor calculates housing emissions.

    Attributes
    ----------
    is_housing_emissions_calculator : bool
        If true, processor will only accept ManureStreams with non-None PenManureData, if false then vice versa.

    Methods
    -------
    receive_manure(manure: ManureStream) -> None
        Entry point of manure into the processor.
    process_manure(conditions: CurrentDayConditions, time: Time) -> dict[str, ManureStream]
        Handles the daily operations for the processor.

    """

    def __init__(self, is_housing_emissions_calculator: bool = False) -> None:
        """Initializes a new Separator."""
        super().__init__(is_housing_emissions_calculator)

    def receive_manure(self, manure: ManureStream) -> None:
        """
        Takes in manure to be processed.

        Parameters
        ----------
        manure : ManureStream
            The manure to be processed.
        """
        pass

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
