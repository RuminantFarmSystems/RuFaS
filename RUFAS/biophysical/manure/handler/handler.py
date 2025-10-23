from typing import Any

from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.biophysical.manure.processor import Processor
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.general_constants import GeneralConstants
from RUFAS.rufas_time import RufasTime
from RUFAS.units import MeasurementUnits
from RUFAS.user_constants import UserConstants


class Handler(Processor):
    """
    Base class for all handlers.

    Parameters
    ----------
    name : str
        Unique identifier of the processor.
    cleaning_water_use_amount : float
        Amount of cleaning water used per animal per day (L).
    cleaning_water_recycle_fraction : float
        Fraction of cleaning water that is from recycled (not fresh) water sources.
    use_parlor_flush : bool
        Indication for if a parlor flush is used in addition to routine parlor water cleaning with fresh water.

    Attributes
    ----------
    manure_stream : ManureStream
        The ManureStream instance being checked for compatibility.
    handler_type: str
        The type of manure handler.
    cleaning_water_use_amount : float
        Amount of cleaning water used per animal per day (L).
    cleaning_water_recycle_fraction : float
        Fraction of cleaning water that is from recycled (not fresh) water sources.
    use_parlor_flush : bool
        Indication for if a parlor flush is used in addition to routine parlor water cleaning with fresh water.

    """

    def __init__(
        self,
        name: str,
        processor_type: str,
        cleaning_water_use_amount: float,
        cleaning_water_recycle_fraction: float,
        use_parlor_flush: bool,
    ):
        super().__init__(name, is_housing_emissions_calculator=True)
        self.manure_stream: ManureStream | None = None
        self.handler_type = processor_type
        self.cleaning_water_use_amount = cleaning_water_use_amount
        self.cleaning_water_recycle_fraction = cleaning_water_recycle_fraction
        self.use_parlor_flush = use_parlor_flush
        self._prefix = f"Manure.{self.__class__.__name__}.{self.handler_type}.{self.name}"

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
            Mapping between classification of manure coming out of this handler to the ManureStream containing the
            manure information.

        """
        info_map: dict[str, Any] = {
            "class": self.__class__.__name__,
            "function": self.process_manure.__name__,
            "prefix": self._prefix,
            "simulation_day": time.simulation_day,
            "handler_type": self.handler_type,
        }
        if self.manure_stream is None or self.manure_stream.pen_manure_data is None:
            self._om.add_error(
                "None type ManureStream.",
                "The processed ManureStream or pen data of the manure stream is None type.",
                info_map,
            )
            raise TypeError("Handler tries to process 'NoneType' object ManureStream.")

        cleaning_water_volume = self.determine_handler_cleaning_water_volume(
            self.manure_stream.pen_manure_data.num_animals,
            self.cleaning_water_use_amount,
            self.cleaning_water_recycle_fraction,
        )
        barn_temperature = self._determine_barn_temperature(conditions.mean_air_temperature)
        surface_area = self.manure_stream.pen_manure_data.manure_deposition_surface_area

        ammonia_emission = 0.0
        fresh_water_volume_used_for_milking = 0.0

        if self.handler_type in ["ManualScraper", "AlleyScraper", "FlushSystem"]:
            ammonia_emission = self._calculate_ammonia_emissions(
                self.manure_stream.ammoniacal_nitrogen,
                self.manure_stream.pen_manure_data.manure_urine_mass,
                ManureConstants.SLURRY_MANURE_DENSITY,
                barn_temperature,
                self.determine_ammonia_resistance(barn_temperature),
                surface_area,
                ManureConstants.DEFAULT_PH_FOR_HOUSING_AMMONIA,
            )

        if self.__class__.__name__ == "ParlorCleaningHandler":
            num_animals = self.manure_stream.pen_manure_data.num_animals
            fresh_water_volume_used_for_milking = self.determine_fresh_water_volume_used_for_milking(num_animals)

        total_cleaning_water_volume = self.determine_total_cleaning_water_volume(
            cleaning_water_volume, fresh_water_volume_used_for_milking
        )

        self._report_processor_output(
            "total_cleaning_water_volume",
            total_cleaning_water_volume,
            self.process_manure.__name__,
            MeasurementUnits.CUBIC_METERS,
            time.simulation_day,
        )
        self._report_processor_output(
            "barn_temperature",
            barn_temperature,
            self.process_manure.__name__,
            MeasurementUnits.DEGREES_CELSIUS,
            time.simulation_day,
        )

        manure_water = self.determine_manure_water(self.manure_stream.water, total_cleaning_water_volume)

        manure_total_ammoniacal_nitrogen = max(0.0, self.manure_stream.ammoniacal_nitrogen - ammonia_emission)
        manure_total_nitrogen = max(0.0, self.manure_stream.nitrogen - ammonia_emission)
        phosphorus = self.manure_stream.phosphorus
        potassium = self.manure_stream.potassium
        ash = self.manure_stream.ash
        non_degradable_volatile_solids = self.manure_stream.non_degradable_volatile_solids
        degradable_volatile_solids = self.manure_stream.degradable_volatile_solids
        volume = self.manure_stream.volume + total_cleaning_water_volume
        total_solids = self.manure_stream.total_solids
        methane_production_potential = self.manure_stream.methane_production_potential
        bedding_non_degradable_volatile_solids = self.manure_stream.bedding_non_degradable_volatile_solids

        self.manure_stream = None
        self._report_processor_output(
            "housing_ammonia_N_emissions",
            ammonia_emission,
            self.process_manure.__name__,
            MeasurementUnits.KILOGRAMS,
            time.simulation_day,
        )
        output_stream = ManureStream(
            water=manure_water,
            ammoniacal_nitrogen=manure_total_ammoniacal_nitrogen,
            nitrogen=manure_total_nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            ash=ash,
            non_degradable_volatile_solids=non_degradable_volatile_solids,
            degradable_volatile_solids=degradable_volatile_solids,
            volume=volume,
            total_solids=total_solids,
            methane_production_potential=methane_production_potential,
            pen_manure_data=None,
            bedding_non_degradable_volatile_solids=bedding_non_degradable_volatile_solids
        )
        self._report_manure_stream(output_stream, "", time.simulation_day)

        return {"manure": output_stream}

    def determine_handler_cleaning_water_volume(
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
             Rate of cleaning water used per animal per day (unitless).
        cleaning_water_recycle_fraction : float
            The fraction of cleaning water recycled (unitless).

        Returns
        -------
        float
            The volume of fresh (non-recycled) cleaning water (L).

        Notes
        -----
        For parlor cleaning handlers, this water volume
          represents an optional parlor flush (separate from fresh water only cleaning water). For all other handler
           types, this water volume represents water use by handlers in the pen, such as a barn floor flush system.

        """
        if self.handler_type in ["ManualScraper", "AlleyScraper", "FlushSystem"]:
            return num_animals * (cleaning_water_use_rate * (1 - cleaning_water_recycle_fraction))
        else:
            if self.use_parlor_flush:
                return num_animals * (cleaning_water_use_rate * (1 - cleaning_water_recycle_fraction))
            else:
                return 0.0

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
        if manure_stream is None or manure_stream.pen_manure_data is None:
            self._om.add_error(
                "None type ManureStream or PenManureData.",
                "The received ManureStream or PenManureData of the manure stream is None type.",
                info_map,
            )
            return False
        return True

    @staticmethod
    def determine_ammonia_resistance(temp: float) -> float:
        """
        Calculate resistance of ammonia transport to the atmosphere in a barn.

        Parameters
        ----------
        temp : float
            Temperature in Celsius (C).

        Returns
        -------
        float
            Resistance of ammonia transport to the atmosphere in a barn (s/m).

        """
        return ManureConstants.HOUSING_SPECIFIC_CONSTANT * (1 - 0.027 * (20.0 - max(temp, -15.0)))

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

    @staticmethod
    def determine_total_cleaning_water_volume(
        cleaning_water_volume: float, fresh_water_volume_used_for_milking: float
    ) -> float:
        """
        Calculates the total volume of cleaning water.

        Parameters
        ----------
        cleaning_water_volume : float
            Volume of cleaning water (L).
        fresh_water_volume_used_for_milking : float
            Volume of fresh water used for milking (L).

        Returns
        -------
        float
            The total volume of cleaning water (m^3).

        """
        return (cleaning_water_volume + fresh_water_volume_used_for_milking) * GeneralConstants.LITERS_TO_CUBIC_METERS

    @staticmethod
    def determine_manure_water(manure_stream_water: float, total_cleaning_water_volume: float) -> float:
        """
        Calculates the amount of manure water.

        Parameters
        ----------
        manure_stream_water : float
            The amount of water in manure stream (KG).
        total_cleaning_water_volume : float
            The amount of total_cleaning_water_volume (L).

        Returns
        -------
        The amount of manure water (KG).

        """
        return manure_stream_water + (total_cleaning_water_volume * UserConstants.WATER_DENSITY_KG_PER_M3)
