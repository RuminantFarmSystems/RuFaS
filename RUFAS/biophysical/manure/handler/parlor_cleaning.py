from RUFAS.biophysical.manure.handler.handler import Handler
from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits


class ParlorCleaningHandler(Handler):
    """
    Handles the reception and processing of manure from parlor cleaning operations.

        Parameters
        ----------
        name : str
            Unique identifier of the processor.

    """

    def __init__(
        self,
        name: str,
        processor_type: str,
        cleaning_water_use_amount: float,
        cleaning_water_recycle_fraction: float,
        use_parlor_flush: bool,
    ):
        super().__init__(
            name, processor_type, cleaning_water_use_amount, cleaning_water_recycle_fraction, use_parlor_flush
        )

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

    def process_manure(self, conditions: CurrentDayConditions, time: RufasTime) -> dict[str, ManureStream]:
        """
        Executes the daily manure processing operations.

        Parameters
        ----------
        conditions : CurrentDayConditions
            Current weather and environmental conditions that manure is being processed in.
        time : RufasTime
            RufasTime instance containing the simulations temporal information.

        Returns
        -------
        dict[str, ManureStream]
            Mapping between classification of manure coming out of this processor to the ManureStream containing the
            manure information.

        """
        if self.manure_stream is None or self.manure_stream.pen_manure_data is None:
            info_map = {"class": self.__class__.__name__, "function": self.process_manure.__name__}
            self._om.add_error(
                "None type ManureStream.",
                "The processed ManureStream or pen data of the manure stream is None type.",
                info_map,
            )
            raise TypeError("TypeError: Handler tries to process 'NoneType' object ManureStream.")
        data_origin_function = self.process_manure.__name__
        self._report_processor_output(
            "housing_CO2_emissions", 0.0, data_origin_function, MeasurementUnits.KILOGRAMS, time.simulation_day
        )
        self._report_processor_output(
            "housing_methane_emissions", 0.0, data_origin_function, MeasurementUnits.KILOGRAMS, time.simulation_day
        )
        return super().process_manure(conditions, time)

    @staticmethod
    def determine_fresh_water_volume_used_for_milking(num_animals: int) -> float:
        """
        Calculates the volume of fresh water used for milking.

        Parameters
        ----------
        num_animals : int
            Number of animals.

        Returns
        -------
        float
                The volume of fresh water used for milking (L).

        """
        return num_animals * ManureConstants.MILKING_FRESH_WATER_USE_RATE
