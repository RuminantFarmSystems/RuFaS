"""
RUFAS: Ruminant Farm Systems Model

File name: manure_handler_classes.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
from typing import Optional
from typing import Type

from RUFAS.output_manager import OutputManager
from RUFAS.routines.manure.beddings.bedding_classes import BaseBedding
from RUFAS.routines.manure.constants.gas_emission_constants import GasEmissionConstants
from RUFAS.routines.manure.constants.manure_constants import ManureConstants
from RUFAS.routines.manure.default_enum.default_enum import DefaultEnum
from RUFAS.routines.manure.gas_emissions.gas_emissions import GasEmissions
from RUFAS.routines.manure.manure_handlers.manure_handler_daily_output import ManureHandlerDailyOutput
from RUFAS.routines.manure.manure_handlers.milking_parlor import MilkingParlor
from RUFAS.routines.manure.pen.manure_management_pen import ManureManagementPen

om = OutputManager()


class ManureHandlerType(DefaultEnum):
    """Enumerates the different types of manure handlers."""
    FLUSH_SYSTEM = 'flush system'
    MANUAL_SCRAPING = 'manual scraping'
    ALLEY_SCRAPER = 'alley scraper'
    TILLAGE = 'tillage'
    DEFAULT = FLUSH_SYSTEM


class BaseManureHandler:
    """Base class for all manure handlers.

    Attributes:
        weather: A Weather object.
        time: A Time object.
        config: A ManureHandlerConfig object that specifies default data specific to the choice of
            manure handler.
        milking_parlor: A MilkingParlor object that handles relevant calculations
            related to the time lactating cows spent there.

    """

    def __init__(self, weather, time, manure_handler_config: ManureHandlerConfig):
        """Initialize a BaseManureHandler object.

        Args:
            weather: A Weather object.
            time: A Time object.
            manure_handler_config: A ManureHandlerInitData object that specifies default data
                specific to the choice of manure handler.

        """
        info_map = {"class": self.__class__.__name__,
                    "function": self.__init__.__name__,
                    "weather": vars(weather),
                    "time": vars(time),
                    "config": vars(manure_handler_config),
                    }

        self.weather = weather
        self.time = time
        self.config = manure_handler_config
        self.milking_parlor = MilkingParlor()

        om.add_variable("milking_parlor", vars(self.milking_parlor), info_map)

    def _get_current_day_average_temperature_in_celsius(self) -> float:
        """Gets the average temperature of the day, in Celsius.

        Returns:
            The average temperature of the day, in Celsius.
        """

        info_map = {"class": self.__class__.__name__,
                    "function": self._get_current_day_average_temperature_in_celsius.__name__,
                    }

        avg_temp = self.weather.T_avg[self.time.year - 1][self.time.day - 1]

        om.add_variable(
            "current_day_average_temperature_in_celsius", avg_temp, info_map)

        return avg_temp

    def daily_update(self,
                     pen: ManureManagementPen,
                     bedding: BaseBedding,
                     sim_day: int) -> ManureHandlerDailyOutput:
        """Calculates and stores the daily output of the manure handler.

        Notes:
            "pseudocode_manure_management" MS.3

        Args:
            pen: A ManureManagementPen object.
            bedding: A BaseBedding object that specifies the type of bedding used.
            sim_day: The current simulation day.

        Returns:
            A ManureHandlerDailyOutput object.
        """
        info_map = {"class": self.__class__.__name__,
                    "function": self.daily_update.__name__,
                    "bedding": vars(bedding),
                    "sim_day": sim_day, }

        housing_methane_emission = GasEmissions.calc_housing_methane_emission(
            num_animals=pen.num_animals,
            barn_area=pen.barn_area_from_pen_type,
            current_barn_temp=self._get_current_day_average_temperature_in_celsius(),
        )

        housing_carbon_dioxide_emission = GasEmissions.calc_housing_carbon_dioxide_emission(
            num_animals=pen.num_animals,
            barn_area=pen.barn_area_from_pen_type,
            current_barn_temp=self._get_current_day_average_temperature_in_celsius(),
        )

        housing_ammonia_emission = GasEmissions.calc_housing_ammonia_emission(
            num_animals=pen.num_animals,
            barn_area=pen.barn_area_from_pen_type,  # m^2/animal
            urine_total_ammoniacal_nitrogen=pen.manure.urine_total_ammoniacal_nitrogen,  # kg
            urine=pen.manure.urine,  # kg
            temperature_celsius=self._get_current_day_average_temperature_in_celsius(),
        )

        daily_output = ManureHandlerDailyOutput(
            simulation_day=sim_day,
            pen_id=pen.id,
            manure_urea=pen.manure.urea,
            liquid_manure_total_ammoniacal_nitrogen=(
                max(0.0, pen.manure.manure_total_ammoniacal_nitrogen - housing_ammonia_emission)),  # kg - kg
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
                pen.num_animals),
            total_water_volume_in_milking_parlor=(
                self.milking_parlor.calc_total_water_volume_used_in_milking_parlor(pen.num_lactating_cows)),
            tempC=self._get_current_day_average_temperature_in_celsius()
        )

        om.add_variable("daily_output", vars(daily_output), info_map)

        return daily_output

    def calc_cleaning_water_volume_in_main_barn(self, num_animals: int) -> float:
        """Calculate the volume of cleaning water needed for all the animals in pen.

        Args:
            num_animals: The number of animals in the pen.

        Returns:
            Volume of cleaning water needed for the given pen, L.

        """

        info_map = {"class": self.__class__.__name__,
                    "function": self.calc_cleaning_water_volume_in_main_barn.__name__,
                    }

        clean_water_volume = num_animals * self.config.cleaning_water_use_rate

        om.add_variable(
            "cleaning_water_volume_in_main_barn", clean_water_volume, info_map)

        return clean_water_volume


class FlushSystem(BaseManureHandler):
    """A class that handles calculations related to a flush system.

    Attributes:
        All inherited from BaseManureHandler.

    """
    pass


class ManualScraping(BaseManureHandler):
    """A class that handles calculations related to manual scraping.

    Attributes:
        All inherited from BaseManureHandler.

    """
    pass


class AlleyScraper(BaseManureHandler):
    """A class that handles calculations related to an alley scraper.

    Attributes:
        All inherited from BaseManureHandler.

    """
    pass


class Tillage(BaseManureHandler):
    """A class that handles calculations related to tillage.

    Attributes:
        All inherited from BaseManureHandler.

    """
    pass


@dataclass
class ManureHandlerConfig:
    """Class for storing the configuration of a manure handler.

    Attributes:
        cleaning_water_use_rate: Amount of cleaning water used per animal per day, L.
        minutes_per_cleaning: Number of minutes needed per animal per cleaning, minutes.
        cleanings_per_day: Number of cleanings per day.
        daily_tillage_frequency: Number of times per day that tillage occurs.

    """
    cleaning_water_use_rate: float = 0.0
    minutes_per_cleaning: int = 0
    cleanings_per_day: int = 0
    daily_tillage_frequency: int = 0


class DefaultManureHandlerConfigFactory:
    """Class for creating default manure handler configurations."""

    FLUSH_SYSTEM_CONFIG = ManureHandlerConfig(
        cleaning_water_use_rate=757.0,
        minutes_per_cleaning=8,
        cleanings_per_day=2,
    )
    MANUAL_SCRAPING_CONFIG = ManureHandlerConfig(
        cleaning_water_use_rate=10.0,
        minutes_per_cleaning=8,
        cleanings_per_day=2,
    )
    ALLEY_SCRAPER_CONFIG = ManureHandlerConfig(
        cleaning_water_use_rate=10.0,
        minutes_per_cleaning=8,
        cleanings_per_day=2,
    )
    TILLAGE_CONFIG = ManureHandlerConfig(
        daily_tillage_frequency=1,
    )

    @classmethod
    def get_instance(cls, manure_handler_type: ManureHandlerType) -> ManureHandlerConfig:
        """Return a default manure handler configuration for the given manure handler type.

        Args:
            manure_handler_type: The type of manure handler.

        Returns:
            A default ManureHandlerConfig object for the given manure handler type.

        """
        info_map = {"class": cls.__name__,
                    "function": cls.get_instance.__name__,
                    }

        manure_handler_config_by_type = {
            ManureHandlerType.FLUSH_SYSTEM: cls.FLUSH_SYSTEM_CONFIG,
            ManureHandlerType.MANUAL_SCRAPING: cls.MANUAL_SCRAPING_CONFIG,
            ManureHandlerType.ALLEY_SCRAPER: cls.ALLEY_SCRAPER_CONFIG,
            ManureHandlerType.TILLAGE: cls.TILLAGE_CONFIG,
        }

        manure_handler_config = manure_handler_config_by_type[manure_handler_type]
        om.add_variable("manure_handler_config",
                        vars(manure_handler_config), info_map)

        return manure_handler_config


class ManureHandlerFactory:
    """A class that contains the logic for creating different types of manure handlers."""

    @classmethod
    def get_instance(cls,
                     manure_handler_type_name: str,
                     weather,
                     time,
                     custom_manure_handler_config: Optional[ManureHandlerConfig] = None) \
            -> BaseManureHandler:
        """Returns an instance of a specific subtype of BaseManureHandler.

        Args:
            manure_handler_type_name: A string that specifies the type of manure handler.
            weather: A Weather object.
            time: A Time object.
            custom_manure_handler_config: A ManureHandlerConfig object that contains
                custom initialization data.

        Returns:
            A new instance of a BaseManureHandler subtype.

        """
        manure_handler_class_by_type: Dict[ManureHandlerType, Type[BaseManureHandler]] = {
            ManureHandlerType.FLUSH_SYSTEM: FlushSystem,
            ManureHandlerType.ALLEY_SCRAPER: AlleyScraper,
            ManureHandlerType.MANUAL_SCRAPING: ManualScraping,
            ManureHandlerType.TILLAGE: Tillage,
        }

        manure_handler_type = ManureHandlerType.get_type(
            manure_handler_type_name)
        manure_handler_class = manure_handler_class_by_type[manure_handler_type]

        if custom_manure_handler_config:
            manure_handler_subtype = manure_handler_class(
                weather, time, custom_manure_handler_config)

            return manure_handler_subtype
        else:
            default_manure_handler_config = DefaultManureHandlerConfigFactory.get_instance(
                manure_handler_type)
            manure_handler_subtype = manure_handler_class(
                weather, time, default_manure_handler_config)

            return manure_handler_subtype
