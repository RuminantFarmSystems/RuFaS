from RUFAS.biophysical.manure.storage.storage import Storage
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.rufas_time import RufasTime


class DailySpread(Storage):
    def __init__(
        self,
        name: str,
        cover: str,
        surface_area: float,
        capacity: float,
        storage_time_period: int = 1,
    ):
        """Initialize DailySpread object."""
        super().__init__(
            name=name,
            is_housing_emissions_calculator=False,
            cover=cover,
            storage_time_period=storage_time_period,
            surface_area=surface_area,
            capacity=capacity,
        )

    def process_manure(self, current_day_conditions: CurrentDayConditions, time: RufasTime) -> dict[str, ManureStream]:
        self._report_manure_stream(self._received_manure, "received", time.simulation_day)
        return super().process_manure(current_day_conditions, time)