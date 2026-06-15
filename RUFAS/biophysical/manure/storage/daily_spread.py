import math

from RUFAS.biophysical.manure.storage.storage import Storage
from RUFAS.biophysical.manure.storage.storage_cover import StorageCover
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.rufas_time import RufasTime


class DailySpread(Storage):
    """
    The daily spread manure storage class.

    Parameters
    ----------
    name : str
        The name of the storage.
    storage_time_period : int, default=1
        The length of time (days) manure is stored for between emptying events.
    surface_area : float, default=math.inf
        The surface area of the manure storage (m^2).
    cover : StorageCover, default=StorageCover.NO_COVER
        The type of cover used with the specified storage.

    """

    def __init__(
        self,
        name: str,
        storage_time_period: int = 1,
        surface_area: float = math.inf,
        cover: StorageCover = StorageCover.NO_COVER,
    ):
        super().__init__(
            name=name,
            is_housing_emissions_calculator=False,
            cover=cover,
            storage_time_period=storage_time_period,
            surface_area=surface_area,
        )
        self.available_for_field_application = ManureStream.make_empty_manure_stream()

    def receive_manure(self, manure: ManureStream) -> None:
        """
        Receives the manure.

        Parameters
        ----------
        manure : ManureStream

        """
        self._received_manure += manure

    def process_manure(self, current_day_conditions: CurrentDayConditions, time: RufasTime) -> dict[str, ManureStream]:
        """
        Processes manure in daily spread.

        Parameters
        ----------
        current_day_conditions : CurrentDayConditions
            The current day conditions.
        time : RufasTime
            The time of the simulation.

        Returns
        -------
        dict[str, ManureStream]
            The processed manure stream.

        """
        self._report_manure_stream(self._received_manure, "received", time.simulation_day)
        output_streams = super().process_manure(current_day_conditions, time)
        self.available_for_field_application = output_streams.get("manure", ManureStream.make_empty_manure_stream())
        return {}

    def set_available_for_field_application(self, stream: ManureStream) -> None:
        """Set remaining manure available for daily spread field application."""
        self.available_for_field_application = stream

    def export_and_clear_remaining_available(self, time: RufasTime) -> None:
        """Report and clear leftover daily spread manure at end of day."""
        self._report_manure_stream(self.available_for_field_application, "exported_excess", time.simulation_day)
        self.available_for_field_application = ManureStream.make_empty_manure_stream()
