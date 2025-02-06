from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.biophysical.manure.processor import Processor
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.time import Time

from .storage_cover import StorageCover


class Storage(Processor):
    """
    Base manure Storage class.

    Parameters
    ----------
    cover : StorageCover
        What the storage will be covered with, if anything.

    Attributes
    ----------
    _stored_manure : ManureStream
        The current amount of manure currently held by the storage.
    _cover : StorageCover
        The cover of the storage.

    """

    def __init__(self, name: str, is_housing_emissions_calculator: bool, cover: StorageCover) -> None:
        """Initializes a manure Storage."""
        super().__init__(name, is_housing_emissions_calculator)
        self._stored_manure = ManureStream(
            water=0.0,
            ammoniacal_nitrogen=0.0,
            nitrogen=0.0,
            phosphorus=0.0,
            potassium=0.0,
            ash=0.0,
            non_degradable_volatile_solids=0.0,
            degradable_volatile_solids=0.0,
            total_solids=0.0,
            volume=0.0,
            pen_manure_data=None,
        )
        self._cover = cover

    def receive_manure(self, manure: ManureStream) -> None:
        """Receives manure and puts it in storage to be processed."""
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
            raise ValueError(error_message)
        self._stored_manure += manure

    def process_manure(self, conditions: CurrentDayConditions, time: Time) -> dict[str, ManureStream]:
        return super().process_manure(conditions, time)
