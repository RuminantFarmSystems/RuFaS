from RUFAS.biophysical.manure.handler import Handler, HandlerConfig
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.time import Time


class ParlorCleaningHandler(Handler):
    """
    A handler class for parlor cleaning handler.

    Parameters
    ----------
    name : str
        Unique identifier of the processor.
    is_housing_emissions_calculator : bool
        Indicates if a Processor calculates housing emissions.

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
        if self.manure_stream is None or self.manure_stream.pen_manure_data is None:
            info_map = {"class": self.__class__.__name__, "function": self.process_manure.__name__}
            self._om.add_error(
                "None type ManureStream.",
                "The processed ManureStream or pen data of the manure stream is None type.",
                info_map,
            )
            raise TypeError("TypeError: Handler tries to process 'NoneType' object ManureStream.")
        num_animals = self.manure_stream.pen_manure_data.num_animals
        self.fresh_water_volume_used_for_milking = self.determine_fresh_water_volume_used_for_milking(num_animals)
        return super().process_manure(conditions, time)

    def determine_cleaning_water_volume_in_main_barn(
        self, num_animals: int, cleaning_water_use_rate: float, cleaning_water_recycle_fraction: float
    ) -> float:
        """
        Calculates the volume of fresh (non-recycled) cleaning water used for, and ultimately added to, a single manure
         stream on a single simulation day by the manure handler.

        Parameters
        ----------
        num_animals : int
            Number of animals.
        cleaning_water_use_rate : float
            The use rate of cleaning water (unitless).
        cleaning_water_recycle_fraction : float
            The fraction of cleaning water recycled (unitless).

        Returns
        -------
        float
            The volume of fresh (non-recycled) cleaning water (m^3).

        """
        if self.config.use_parlor_flush:
            return super().determine_cleaning_water_volume_in_main_barn(num_animals, cleaning_water_use_rate,
                                                                        cleaning_water_recycle_fraction)
        else:
            return 0.0

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
        The volume of fresh water used for milking (L).

        """
        return num_animals * 30
