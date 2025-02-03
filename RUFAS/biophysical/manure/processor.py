from abc import ABC, abstractmethod

from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.manure_stream import ManureStream
from RUFAS.time import Time


class Processor(ABC):
    """
    Base class for all manure processors.

    Methods
    -------
    receive_manure(manure: ManureStream) -> None
        Entry point of manure into the processor.
    process_manure(conditions: CurrentDayConditions, time: Time) -> dict[str, ManureStream]
        Handles the daily operations for the processor.

    """

    @abstractmethod
    def receive_manure(manure: ManureStream) -> None:
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
    def process_manure(conditions: CurrentDayConditions, time: Time) -> dict[str, ManureStream]:
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
