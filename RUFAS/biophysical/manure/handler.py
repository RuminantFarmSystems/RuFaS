from dataclasses import dataclass

from numpy import clip

from RUFAS.biophysical.manure.processor import Processor
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.enums import AnimalCombination
from RUFAS.general_constants import GeneralConstants
from RUFAS.output_manager import OutputManager
from RUFAS.time import Time
from RUFAS.units import MeasurementUnits


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


class Handler(Processor):
    def __init__(self, name: str, is_housing_emissions_calculator: bool, config: HandlerConfig):
        super().__init__(name, is_housing_emissions_calculator)
        self.manure_stream: ManureStream | None = None
        self.fresh_water_volume_used_for_milking: float = 0.0
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
        om = OutputManager()
        info_map = {"class": Handler.__class__.__name__, "function": Handler.receive_manure.__name__}
        if self.manure_stream is not None:
            om.add_error(
                "Multiple stream received.",
                f"Handler should only receive one manure stream at a time,"
                f" handler {self.name} already received a manure stream.",
                info_map,
            )
            raise ValueError("Handler cannot receive multi streams.")

        if manure.pen_manure_data is None:
            om.add_error(
                "None type PenManureData.", "The received ManureStream has a None type PenManureData.", info_map
            )
            raise TypeError("TypeError: Handler received 'NoneType' object for PenManureData in ManureStream")

        if manure.pen_manure_data.pen_type in ["open lot", "compost bedded pack barn"]:
            om.add_error(
                "Unsupported pen type.",
                f"Handler only supports flush_system,manual_scraping,"
                f" alley_scraper and parlor_cleaning,"
                f" received {manure.pen_manure_data.pen_type}.",
                info_map,
            )
            raise ValueError("ValueError: Handler received unsupported pen type in ManureStream")
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
        info_map_c = {"units": MeasurementUnits.DEGREES_CELSIUS}
        info_map_m3 = {"units": MeasurementUnits.CUBIC_METERS}
        om = OutputManager()
        cleaning_water_volume = self.determine_cleaning_water_volume_in_main_barn(
            self.manure_stream.pen_manure_data.num_animals,
            self.config.cleaning_water_use_rate,
            self.config.cleaning_water_recycle_fraction,
        )
        barn_temperature = self.determine_barn_temperature(conditions.mean_air_temperature)

        total_cleaning_water_volume = (
            cleaning_water_volume + self.fresh_water_volume_used_for_milking
        ) * GeneralConstants.LITERS_TO_CUBIC_METERS
        om.add_variable("total_cleaning_water_volume", total_cleaning_water_volume, info_map_m3)
        om.add_variable("barn_temperature", barn_temperature, info_map_c)

        manure_water = self.manure_stream.water + cleaning_water_volume

        surface_area = self.determine_barn_area(
            self.manure_stream.pen_manure_data.animal_combination,
            self.manure_stream.pen_manure_data.pen_type,
            self.manure_stream.pen_manure_data.num_stalls,
        )
        ammonia_emission = self._calculate_ammonia_emissions(
            self.manure_stream.ammoniacal_nitrogen,
            self.manure_stream.volume,
            990.0,
            barn_temperature,
            self.determine_ammonia_resistance(barn_temperature),
            surface_area,
            7.7,
        )
        manure_total_ammoniacal_nitrogen = max(0.0, self.manure_stream.ammoniacal_nitrogen - ammonia_emission)
        nitrogen = self.manure_stream.nitrogen
        phosphorus = self.manure_stream.phosphorus
        potassium = self.manure_stream.potassium
        ash = self.manure_stream.ash
        non_degradable_volatile_solids = self.manure_stream.non_degradable_volatile_solids
        degradable_volatile_solids = self.manure_stream.degradable_volatile_solids
        volume = self.manure_stream.volume
        total_solids = self.manure_stream.total_solids

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
                total_solids=total_solids,  # temp value waiting for Elle's confirmation
                pen_manure_data=None,
            )
        }

    @staticmethod
    def determine_cleaning_water_volume_in_main_barn(
        num_animals: int, cleaning_water_use_rate: float, cleaning_water_recycle_fraction: float
    ) -> float:
        """
        Calculates the volume of fresh (non-recycled) cleaning water used for, and ultimately added to, a single manure
         stream on a single simulation day by the manure handler.

        Returns
        -------
        float
            The volume of fresh (non-recycled) cleaning water (m^3).

        """
        return num_animals * (cleaning_water_use_rate * (1 - cleaning_water_recycle_fraction))

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
        return float(clip(air_temp, 5, 30))

    @classmethod
    def determine_methane_emissions(
        cls, animal_combination: AnimalCombination, pen_type: str, num_stalls: int, barn_temperature: float
    ) -> float:
        """
        Calculates the methane housing emission.

        Parameters
        ----------
        animal_combination : AnimalCombination
        pen_type : str
        num_stalls : int
        barn_temperature : float

        Returns
        -------
        float
            Methane emission from manure (kg).

        """
        barn_area = cls.determine_barn_area(animal_combination, pen_type, num_stalls)

        return max(0.0, 0.13 * barn_temperature) * barn_area / 1000

    @classmethod
    def determine_carbon_dioxide_emissions(
        cls, animal_combination: AnimalCombination, pen_type: str, num_stalls: int, barn_temperature: float
    ) -> float:
        """
        Calculates the carbon dioxide housing emission.

        Parameters
        ----------
        animal_combination : AnimalCombination
        pen_type : str
        num_stalls : int
        barn_temperature : float

        Returns
        -------
        float
            Carbon dioxide emission from manure (kg).

        """
        barn_area = cls.determine_barn_area(animal_combination, pen_type, num_stalls)
        return max(0.0, 0.0065 + 0.0192 * barn_temperature) * barn_area / 1000

    @classmethod
    def determine_barn_area(cls, animal_combination: AnimalCombination, pen_type: str, num_stalls: int) -> float:
        """
        Calculates the barn area based on animal and pen type.

        Parameters
        ----------
        animal_combination : AnimalCombination
            An AnimalCombination enum that describes the current animal makeup in this pen.
        pen_type : str
            The type of pen used for this pen.
        num_stalls : int
            The number of stalls in this pen.

        Returns
        -------
        float
            The barn exposed area base on the given animal combination and pen types (m^2).

        Raises
        ------
        ValueError
            If the pen type is not one of the following: "freestall", "tiestall".

        """
        om = OutputManager()
        surface_area_table = {
            ("freestall", True): 1.2,
            ("freestall", False): 1.0,
            ("tiestall", True): 3.5,
            ("tiestall", False): 2.5,
        }
        if pen_type not in ["freestall", "tiestall"]:
            info_map = {"class": cls.__name__, "function": cls.determine_barn_area.__name__}
            om.add_error("Invalid pen type.", f"Valid pen types are tiestall and freestall, got {pen_type}", info_map)
            raise ValueError(f"Invalid pen type: {pen_type}")

        is_lac_cow = animal_combination == AnimalCombination.LAC_COW
        surface_area_per_stall = surface_area_table.get((pen_type, is_lac_cow))

        return num_stalls * surface_area_per_stall

    @staticmethod
    def determine_ammonia_resistance(temp: float, hsc: float = 260) -> float:
        """
        Calculate resistance of ammonia transport to the atmosphere in a barn.

        Parameters
        ----------
        temp : float
            Temperature in Celsius (C).
        hsc : float, optional, default = 260
            Housing specific constant (s/m).

        Returns
        -------
        float
            Resistance of ammonia transport to the atmosphere in a barn (s/m).

        """
        return hsc * (1 - 0.027 * (20.0 - max(temp, -15.0)))
