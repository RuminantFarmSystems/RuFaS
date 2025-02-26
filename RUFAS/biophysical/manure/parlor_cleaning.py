from RUFAS.biophysical.manure.handler import Handler, HandlerConfig
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.time import Time


class ParlorCleaning(Handler):
    """
    A handler class for parlor cleaning handler.
    """
    def __init__(self, name: str, is_housing_emissions_calculator: bool, config: HandlerConfig):
        super().__init__(name, is_housing_emissions_calculator, config)

    def receive_manure(self, manure_stream: ManureStream) -> None:
        """
        Receiving manure stream.

        Parameters
        ----------
        manure_stream : ManureStream
            The ManureStream instance being received.

        """
        super().receive_manure(manure_stream)
        if self.manure_stream is None:
            self.manure_stream = manure_stream
        else:
            self.manure_stream += manure_stream

    def process_manure(self, conditions: CurrentDayConditions, time: Time) -> dict[str, ManureStream]: