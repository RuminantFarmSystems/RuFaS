from typing import Any

from numpy import clip

from RUFAS.biophysical.manure.processor import Processor
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.data_structures.processor_types import ProcessorTypes
from RUFAS.general_constants import GeneralConstants
from RUFAS.time import Time
from RUFAS.units import MeasurementUnits


class Handler(Processor):
    """
    Base class for all handlers.

    Parameters
    ----------
    name : str
        Unique identifier of the processor.
    handler_type: ProcessorTypes
        The class of sun type of manure handlers that this handler falls into.
    cleaning_water_use_amount : float
        Amount of cleaning water used per animal per day (L).
    minutes_per_cleaning : int
        Number of minutes needed per animal per cleaning, minutes.
    cleanings_per_day : int
        Number of cleanings per day.
    cleaning_water_recycle_fraction : float
        Fraction of cleaning water that is from recycled (not fresh) water sources.
    use_parlor_flush : bool
        Indication for if a parlor flush is used in addition to routine parlor water cleaning with fresh water.

    Attributes
    ----------
    manure_stream : ManureStream
        The ManureStream instance being checked for compatibility.
    fresh_water_volume_used_for_milking : float
        The amount of fresh water used for milking (L).
    ammonia_emission : float
        The amount of ammonia emission (kg).
    handler_type: ProcessorTypes
        The class of sun type of manure handlers that this handler falls into.
    cleaning_water_use_amount : float
        Amount of cleaning water used per animal per day (L).
    minutes_per_cleaning : int
        Number of minutes needed per animal per cleaning, minutes.
    cleanings_per_day : int
        Number of cleanings per day.
    cleaning_water_recycle_fraction : float
        Fraction of cleaning water that is from recycled (not fresh) water sources.
    use_parlor_flush : bool
        Indication for if a parlor flush is used in addition to routine parlor water cleaning with fresh water.

    """

    def __init__(self, name: str, handler_type: ProcessorTypes, cleaning_water_use_amount: float,
                 minutes_per_cleaning: int, cleanings_per_day: int, cleaning_water_recycle_fraction: float,
                 use_parlor_flush: bool):
        super().__init__(name, is_housing_emissions_calculator=True)
        self.manure_stream: ManureStream | None = None
        self.fresh_water_volume_used_for_milking: float = 0.0
        self.ammonia_emission: float = 0.0
        self.handler_type = handler_type
        self.cleaning_water_use_amount = cleaning_water_use_amount
        self.minutes_per_cleaning = minutes_per_cleaning
        self.cleanings_per_day = cleanings_per_day
        self.cleaning_water_recycle_fraction = cleaning_water_recycle_fraction
        self.use_parlor_flush = use_parlor_flush

    def receive_manure(self, manure_stream: ManureStream) -> None:
        """
        Implements the basic checks for receiving manure stream.

        Parameters
        ----------
        manure_stream : ManureStream
            The ManureStream instance being checked for compatibility.

        """
        info_map = {"class": self.__class__.__name__, "function": self.receive_manure.__name__}
        if not self.check_manure_stream_compatibility(manure_stream):
            self._om.add_error(
                "Invalid manure stream.",
                "Received manure stream is not compatible with a handler type processor.",
                info_map,
            )
            raise ValueError("ValueError: Invalid manure stream for handler processor.")

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
        info_map: dict[str, Any] = {
            "class": self.__class__.__name__,
            "function": self.process_manure.__name__,
            "prefix": self._prefix,
            "simulation_day": time.simulation_day,
            "handler_type": self.handler_type
        }
        if self.manure_stream is None or self.manure_stream.pen_manure_data is None:
            self._om.add_error(
                "None type ManureStream.",
                "The processed ManureStream or pen data of the manure stream is None type.",
                info_map,
            )
            raise TypeError("TypeError: Handler tries to process 'NoneType' object ManureStream.")

        info_map_c = {"units": MeasurementUnits.DEGREES_CELSIUS, **info_map}
        info_map_m3 = {"units": MeasurementUnits.CUBIC_METERS, **info_map}
        cleaning_water_volume = self.determine_cleaning_water_volume_in_main_barn(
            self.manure_stream.pen_manure_data.num_animals,
            self.cleaning_water_use_amount,
            self.cleaning_water_recycle_fraction,
        )
        barn_temperature = self.determine_barn_temperature(conditions.mean_air_temperature)

        total_cleaning_water_volume = (
            cleaning_water_volume + self.fresh_water_volume_used_for_milking
        ) * GeneralConstants.LITERS_TO_CUBIC_METERS

        self._om.add_variable("total_cleaning_water_volume", total_cleaning_water_volume, info_map_m3)
        self._om.add_variable("barn_temperature", barn_temperature, info_map_c)

        manure_water = self.manure_stream.water + (
            total_cleaning_water_volume * GeneralConstants.WATER_DENSITY_KG_PER_M3
        )

        manure_total_ammoniacal_nitrogen = max(0.0, self.manure_stream.ammoniacal_nitrogen - self.ammonia_emission)
        nitrogen = self.manure_stream.nitrogen
        phosphorus = self.manure_stream.phosphorus
        potassium = self.manure_stream.potassium
        ash = self.manure_stream.ash
        non_degradable_volatile_solids = self.manure_stream.non_degradable_volatile_solids
        degradable_volatile_solids = self.manure_stream.degradable_volatile_solids
        volume = self.manure_stream.volume + total_cleaning_water_volume
        total_solids = self.manure_stream.total_solids

        self.manure_stream = None
        return {
            "manure": ManureStream(
                water=manure_water,
                ammoniacal_nitrogen=manure_total_ammoniacal_nitrogen,
                nitrogen=nitrogen,
                phosphorus=phosphorus,
                potassium=potassium,
                ash=ash,
                non_degradable_volatile_solids=non_degradable_volatile_solids,
                degradable_volatile_solids=degradable_volatile_solids,
                volume=volume,
                total_solids=total_solids,
                pen_manure_data=None,
            )
        }

    def determine_cleaning_water_volume_in_main_barn(
        self, num_animals: int, cleaning_water_use_amount: float, cleaning_water_recycle_fraction: float
    ) -> float:
        """
        Calculates the volume of fresh (non-recycled) cleaning water used for, and ultimately added to, a single manure
         stream on a single simulation day by the manure handler. For parlor cleaning handlers, this water volume
          represents an optional parlor flush (separate from fresh water only cleaning water). For all other handler
           types, this water volume represents water use by handlers in the pen, such as a barn floor flush system.

        Parameters
        ----------
        num_animals : int
            Number of animals.
        cleaning_water_use_amount : float
             Amount of cleaning water used per animal per day (L).
        cleaning_water_recycle_fraction : float
            The fraction of cleaning water recycled (unitless).

        Returns
        -------
        float
            The volume of fresh (non-recycled) cleaning water (L).

        """
        return num_animals * (cleaning_water_use_amount * (1 - cleaning_water_recycle_fraction))

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

        References
        ----------
        Between 5 and 30 C, barn temperature is assumed to be equal to outdoor air temperature.
        This function assumes that barn temperature does not drop below 5 C or increase above 30 C.
        These bounds were suggested by manure SMEs and are supported by barn temperature ranges
        reported in Bucklin et al. (FL, upper limit; https://doi.org/10.13031/2013.28851).
        The lower bound (5 C) suggested by SMEs was based on general industry standards/conditions.

        """
        return float(clip(air_temp, 5, 30))

    def check_manure_stream_compatibility(self, manure_stream: ManureStream) -> bool:
        """
        Basic checks for receiving manure stream.

        Parameters
        ----------
        manure_stream : ManureStream
            The ManureStream instance being checked for compatibility.

        """
        info_map = {"class": self.__class__.__name__, "function": self.check_manure_stream_compatibility.__name__}
        if not super().check_manure_stream_compatibility(manure_stream):
            return False
        if (
            manure_stream.pen_manure_data is not None
            and manure_stream.pen_manure_data.pen_type is not None
            and manure_stream.pen_manure_data.pen_type not in ["freestall", "tiestall"]
        ):
            self._om.add_error(
                "Unsupported pen type.",
                f"Handler should only be used with freestall and tiestall pen types,"
                f" received {manure_stream.pen_manure_data.pen_type}.",
                info_map,
            )
            return False
        return True
