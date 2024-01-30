from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
from typing import Optional
from typing import Type

from RUFAS.time import Time
from RUFAS.weather import Weather
from RUFAS.routines.manure.beddings.bedding_classes import BaseBedding
from RUFAS.routines.manure.default_enum.default_enum import DefaultEnum
from RUFAS.routines.manure.gas_emissions.calculator import (
    GasEmissionsCalculator,
)
from RUFAS.routines.manure.manure_handlers.manure_handler_daily_output import (
    ManureHandlerDailyOutput,
)
from RUFAS.routines.manure.manure_handlers.milking_parlor import MilkingParlor
from RUFAS.routines.manure.pen_manure.manure_manager_pen import ManureManagerPen


class ManureHandlerType(DefaultEnum):
    """Enumerates the different types of manure handlers."""

    FLUSH_SYSTEM = "flush system"
    MANUAL_SCRAPING = "manual scraping"
    ALLEY_SCRAPER = "alley scraper"
    TILLAGE = "tillage"
    HARROWING = "harrowing"
    DEFAULT = FLUSH_SYSTEM


class BaseManureHandler:
    """Base class for all manure handlers.

    Attributes
    ----------
    weather : Weather
        A Weather object.
    time : Time
        A Time object.
    config : ManureHandlerConfig
        A ManureHandlerConfig object that specifies default data specific to the choice of
        manure handler.
    milking_parlor : MilkingParlor
        A MilkingParlor object that handles relevant calculations
        related to the time lactating cows spent there.

    """

    def __init__(self, weather: Weather, time: Time, manure_handler_config: ManureHandlerConfig):
        """Initialize a BaseManureHandler object.

        Parameters
        ----------
        weather : Weather
            A Weather object.
        time : Time
            A Time object.
        manure_handler_config : ManureHandlerConfig
            A ManureHandlerInitData object that specifies default data
            specific to the choice of manure handler.
        """

        self.weather = weather
        self.time = time
        self.config = manure_handler_config
        self.milking_parlor = MilkingParlor()

    def _get_current_day_average_temperature_in_celsius(self) -> float:
        """Gets the average temperature of the day, in Celsius.

        Returns
        -------
        The average temperature of the day, in Celsius.
        """
        current_conditions = self.weather.get_current_day_conditions(self.time)
        avg_temp = current_conditions.mean_air_temperature

        return avg_temp

    def daily_update(self,
                     pen: ManureManagerPen,
                     bedding: BaseBedding | None,
                     sim_day: int) -> ManureHandlerDailyOutput:
        """
        Calculate the daily manure handler output based on input passed from the animal module.

        Parameters
        ----------
        pen : ManureManagerPen
            A ManureManagerPen object that stores relevant information about the pen that
            can helpful in the manure module.
        bedding : BaseBedding | None
            A BaseBedding object that specifies the type of bedding use or None if no bedding is used.
        sim_day : int
            The current simulation day.

        Returns
        -------
        ManureHandlerDailyOutput
            A ManureHandlerDailyOutput object that stores the daily manure handler output.
            See details in the class definition (:class:`ManureHandlerDailyOutput`).
        """

        if pen.num_animals == 0:
            return ManureHandlerDailyOutput()

        housing_methane_emission = GasEmissionsCalculator.housing_methane_emission(
            num_animals=pen.num_animals,
            barn_area=pen.barn_area_from_pen_type,
            barn_temp=self._get_current_day_average_temperature_in_celsius(),
        )

        housing_carbon_dioxide_emission = (
            GasEmissionsCalculator.housing_carbon_dioxide_emission(
                num_animals=pen.num_animals,
                barn_area=pen.barn_area_from_pen_type,
                barn_temp=self._get_current_day_average_temperature_in_celsius(),
            )
        )

        if pen.pen_type in ["freestall", "tiestall"]:
            housing_ammonia_emission = GasEmissionsCalculator.housing_ammonia_emission(
                num_animals=pen.num_animals,
                barn_area_per_animal=pen.barn_area_from_pen_type,  # m^2/animal
                urine_total_ammoniacal_nitrogen=pen.manure.manure_total_ammoniacal_nitrogen,  # kg
                urine=pen.manure.urine,  # kg
                temp=self._get_current_day_average_temperature_in_celsius(),
            )
        else:
            housing_ammonia_emission = 0.0

        daily_output = ManureHandlerDailyOutput(
            simulation_day=sim_day,
            pen_id=pen.id,
            manure_urea=pen.manure.urea,
            liquid_manure_total_ammoniacal_nitrogen=(
                max(
                    0.0,
                    pen.manure.manure_total_ammoniacal_nitrogen
                    - housing_ammonia_emission,
                )
            ),
            liquid_manure_nitrogen=pen.manure.nitrogen,
            liquid_manure_total_solids=pen.manure.total_solids,
            manure_degradable_volatile_solids=pen.manure.degradable_volatile_solids,
            manure_non_degradable_volatile_solids=pen.manure.non_degradable_volatile_solids,
            liquid_manure_phosphorus=pen.manure.phosphorus,
            liquid_manure_potassium=pen.manure.potassium,
            housing_methane=housing_methane_emission,
            housing_carbon_dioxide=housing_carbon_dioxide_emission,
            housing_ammonia=housing_ammonia_emission,
            manure_volume=pen.manure.manure_volume,
            cleaning_water_volume=self.calc_cleaning_water_volume_in_main_barn(
                pen.num_animals),
            total_bedding_volume=bedding.calc_total_bedding_volume(
                pen.num_animals) if bedding is not None else 0.0,
            total_bedding_mass=bedding.calc_total_bedding_mass(
                pen.num_animals) if bedding is not None else 0.0,
            total_water_volume_in_milking_parlor=(
                self.milking_parlor.calc_total_water_volume_used_in_milking_parlor(
                    pen.num_lactating_cows
                )
            ),
            tempC=self._get_current_day_average_temperature_in_celsius(),
        )

        return daily_output

    def calc_cleaning_water_volume_in_main_barn(self, num_animals: int) -> float:
        """Calculate the volume of cleaning water needed for all the animals in pen.

        Attributes
        ----------
        num_animals : int
            The number of animals in the pen.

        Returns
        -------
        Volume of cleaning water needed for the given pen, L.

        """
        cleaning_water_volume = (num_animals * self.config.cleaning_water_use_rate *
                                 (1-self.config.cleaning_water_recycle_fraction))

        return cleaning_water_volume


class FlushSystem(BaseManureHandler):
    """A class that handles calculations related to a flush system.

    Attributes
    ----------
    All inherited from BaseManureHandler.
    """

    pass


class ManualScraping(BaseManureHandler):
    """A class that handles calculations related to manual scraping.

    Attributes
    ----------
    All inherited from BaseManureHandler.
    """

    pass


class AlleyScraper(BaseManureHandler):
    """A class that handles calculations related to an alley scraper.

    Attributes
    ----------
    All inherited from BaseManureHandler.
    """

    pass


class Tillage(BaseManureHandler):
    """A class that handles calculations related to tillage.

    Attributes
    ----------
    All inherited from BaseManureHandler.
    """

    pass


class Harrowing(BaseManureHandler):
    """A class that handles calculations related to harrowing.

    Attributes
    ----------
    All inherited from BaseManureHandler.

    """

    pass


@dataclass
class ManureHandlerConfig:
    """Class for storing the configuration of a manure handler.

    Attributes
    ----------
    cleaning_water_use_rate : float
        Amount of cleaning water used per animal per day, L.
    minutes_per_cleaning : int
        Number of minutes needed per animal per cleaning, minutes.
    cleanings_per_day : int
        Number of cleanings per day.
    daily_tillage_frequency : int
        Number of times per day that compost bedding is tilled.
    cleaning_water_recycle_fraction : float
        Fraction of cleaning water that is from recycled (not fresh) water sources.
    """

    cleaning_water_use_rate: float = 0.0
    minutes_per_cleaning: int = 8
    cleanings_per_day: int = 2
    daily_tillage_frequency: int = 0
    cleaning_water_recycle_fraction: float = 0.0


class DefaultManureHandlerConfigFactory:
    """Class for creating default manure handler configurations."""

    FLUSH_SYSTEM_CONFIG = ManureHandlerConfig(
        cleaning_water_use_rate=757.0,
        cleaning_water_recycle_fraction=0.80,
    )
    MANUAL_SCRAPING_CONFIG = ManureHandlerConfig(
        cleaning_water_use_rate=10.0,
        cleaning_water_recycle_fraction=0.10,
    )
    ALLEY_SCRAPER_CONFIG = ManureHandlerConfig(
        cleaning_water_use_rate=10.0,
        cleaning_water_recycle_fraction=0.10,
    )
    TILLAGE_CONFIG = ManureHandlerConfig(
        daily_tillage_frequency=1,
    )
    HARROWING_CONFIG = ManureHandlerConfig(
        daily_tillage_frequency=0,
    )

    @classmethod
    def get_instance(
            cls, manure_handler_type: ManureHandlerType
    ) -> ManureHandlerConfig:
        """Return a default manure handler configuration for the given manure handler type.

        Parameters
        ----------
        manure_handler_type : ManureHandlerType
            The type of manure handler.

        Returns
        -------
        A default ManureHandlerConfig object for the given manure handler type.
        """

        manure_handler_config_by_type = {
            ManureHandlerType.FLUSH_SYSTEM: cls.FLUSH_SYSTEM_CONFIG,
            ManureHandlerType.MANUAL_SCRAPING: cls.MANUAL_SCRAPING_CONFIG,
            ManureHandlerType.ALLEY_SCRAPER: cls.ALLEY_SCRAPER_CONFIG,
            ManureHandlerType.TILLAGE: cls.TILLAGE_CONFIG,
            ManureHandlerType.HARROWING: cls.HARROWING_CONFIG,
        }

        manure_handler_config = manure_handler_config_by_type[manure_handler_type]

        return manure_handler_config


class ManureHandlerFactory:
    """A class that contains the logic for creating different types of manure handlers."""

    @classmethod
    def get_instance(
            cls,
            manure_handler_type_name: str,
            weather: Weather,
            time: Time,
            custom_manure_handler_config: Optional[ManureHandlerConfig] = None,
    ) -> BaseManureHandler:
        """Returns an instance of a specific subtype of BaseManureHandler.

        Parameters
        ----------
        manure_handler_type_name : str
            A string that specifies the type of manure handler.
        weather : Weather
            A Weather object.
        time : Time
            A Time object.
        custom_manure_handler_config : ManureHandlerConfig
            A ManureHandlerConfig object that contains custom initialization data.

        Returns
        -------
        A new instance of a BaseManureHandler subtype.

        """
        manure_handler_class_by_type: Dict[
            ManureHandlerType, Type[BaseManureHandler]
        ] = {
            ManureHandlerType.FLUSH_SYSTEM: FlushSystem,
            ManureHandlerType.ALLEY_SCRAPER: AlleyScraper,
            ManureHandlerType.MANUAL_SCRAPING: ManualScraping,
            ManureHandlerType.TILLAGE: Tillage,
            ManureHandlerType.HARROWING: Harrowing,
        }

        manure_handler_type = ManureHandlerType.get_type(manure_handler_type_name)
        manure_handler_class = manure_handler_class_by_type[manure_handler_type]

        if custom_manure_handler_config:
            manure_handler_subtype = manure_handler_class(
                weather, time, custom_manure_handler_config
            )

            return manure_handler_subtype
        else:
            default_manure_handler_config = (
                DefaultManureHandlerConfigFactory.get_instance(manure_handler_type)
            )
            manure_handler_subtype = manure_handler_class(
                weather, time, default_manure_handler_config
            )

            return manure_handler_subtype
