from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.biophysical.manure.processor import Processor
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.time import Time


class Storage(Processor):
    """Base manure Storage class."""

    def __init__(self, name: str, is_housing_emissions_calculator: bool) -> None:
        super().__init__(name, is_housing_emissions_calculator)

    def receive_manure(self, manure: ManureStream) -> None:
        is_compatible_manure = self.check_manure_stream_compatibility(manure)
        if not is_compatible_manure:
            info_map = {
                "class": self.__class__.__name__,
                "function": self.receive_manure.__name__,
                "processor_name": self.name,
                "manure_stream": manure,
            }
            error_message = f"Processor {self.name} received an incompatible ManureStream."
            self._om.add_error("invalid_manure_stream", error_message, info_map)
            raise ValueError(error_message
        )
        pass
    
    def process_manure(self, conditions: CurrentDayConditions, time: Time) -> dict[str, ManureStream]:
        return super().process_manure(conditions, time)
