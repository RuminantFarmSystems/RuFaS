from abc import ABC, abstractmethod
from dataclasses import dataclass

from RUFAS.biophysical.manure.processor import Processor
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.output_manager import OutputManager
from RUFAS.time import Time


@dataclass(kw_only=True)
class HandlerConfig:
    """
    Class for storing the configuration of a manure handler.

    Attribute
    ----------
    name : str
        The name of the manure handler.
    manure_handler_type: str
        The class of manure handlers that this configuration falls into.
    cleaning_water_use_rate : float
        Amount of cleaning water used per animal per day, L.
    minutes_per_cleaning : int
        Number of minutes needed per animal per cleaning, minutes.
    cleanings_per_day : int
        Number of cleanings per day.
    cleaning_water_recycle_fraction : float
        Fraction of cleaning water that is from recycled (not fresh) water sources.
    use_parlor_flush : bool
        Indication for if a parlor flush is used in addition to routine parlor water cleaning with fresh water.

    """
    name: str
    manure_handler_type: str
    cleaning_water_use_rate: float
    minutes_per_cleaning: int
    cleanings_per_day: int
    cleaning_water_recycle_fraction: float
    use_parlor_flush: bool


class Handler(Processor, ABC):
    def __init__(self, is_housing_emissions_calculator: bool, config: HandlerConfig):
        super().__init__(is_housing_emissions_calculator)
        self.manure_stream: ManureStream | None = None
        self.config = config

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
        if manure.pen_manure_data is None:
            om = OutputManager()
            info_map = {"class": Handler.__class__.__name__, "function": Handler.receive_manure.__name__}
            om.add_error(
                "None type PenManureData", "The received ManureStream has a None type PenManureData.", info_map
            )
            raise TypeError("TypeError: Handler received 'NoneType' object for PenManureData in ManureStream")

        self.manure_stream = manure

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

        return {"manure": self.manure_stream}

    def calc_cleaning_water_volume_in_main_barn(self) -> float:
        """
        Calculates the volume of fresh (non-recycled) cleaning water used for, and ultimately added to, a single manure
         stream on a single simulation day by the manure handler.

        Returns
        -------
        float
            The volume of fresh (non-recycled) cleaning water (m^3).

        """
        return (self.manure_stream.pen_manure_data.num_animals *
                (self.config.cleaning_water_use_rate * (1 - self.config.cleaning_water_recycle_fraction)))

    @staticmethod
    def determine_barn_temperature(air_temp: float) -> float:
        """
        Calculates the barn temperature.

        Parameters
        ----------
        air_temp : float
            Air temperature (c).

        Returns
        -------
        float
            Adjusted barn temperature (c).

        """
        adjusted_temp = air_temp
        if air_temp < 5:
            adjusted_temp = 5
        elif air_temp > 30:
            adjusted_temp = 30

        return adjusted_temp

