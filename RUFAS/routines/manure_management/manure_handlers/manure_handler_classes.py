"""
RUFAS: Ruminant Farm Systems Model

File name: base_handler.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu 
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import auto
from typing import Dict, List, Optional, Type

from RUFAS.routines.manure_management.gas_emissions.gas_emissions import GasEmissions
from RUFAS.routines.manure_management.helpers.enum_helpers import DefaultEnum
from RUFAS.routines.manure_management.manure_handlers.bedding_classes import BeddingFactory
from RUFAS.routines.manure_management.manure_handlers.manure_handler_output import ManureHandlerOutput
from RUFAS.routines.manure_management.manure_handlers.milking_center import MilkingCenter
from RUFAS.routines.manure_management.misc.constants import ManureManagementConstants as Constants
from RUFAS.routines.manure_management.misc.simple_pen import SimplePen


class ManureHandlerType(DefaultEnum):
    """
    An Enum class that lists all the different types of manure handlers.
    """

    FLUSH_SYSTEM = auto()
    MANUAL_SCRAPING = auto()
    ALLEY_SCRAPER = auto()
    DEFAULT = FLUSH_SYSTEM


class BaseManureHandler:
    """
    A class that contains common attributes and methods for all the different
    subtypes of manure handlers.
    """

    def __init__(self,
                 bedding_type_name: str,
                 manure_handler_config: ManureHandlerConfig,
                 weather,
                 time):
        """Initializes a BaseManureHandler object.

        Args
            bedding_type_name: The name of the bedding type.
            manure_handler_config: A ManureHandlerInitData object that specifies default data
                specific to the choice of manure handler.

        """

        self.config = manure_handler_config
        self.bedding = BeddingFactory.get_instance(bedding_type_name)
        self.milking_center = MilkingCenter()
        self.all_output: List[ManureHandlerOutput] = []
        self.weather_data=weather
        self.time=time

    @property
    def last_output(self) -> Optional[ManureHandlerOutput]:
        return self.all_output[-1] if len(self.all_output) > 0 else None

    def reset_daily_variables(self):
        pass

    def update(self, pen: SimplePen) -> ManureHandlerOutput:
        """
        Description:
            Calls functions to calculate nutrient losses and transformations during
            manure handling.
            "pseudocode_manure_management" MS.3
        """


                
        pen_urine = 21*pen.num_animals ##  (kg) Get this from animal module manure output 
        urine_TAN = pen.manure.MN*0.45  ## Can also get from animal module
        tempC = self.weather_data.T_avg[self.time.year - 1][self.time.day - 1]
        NH3_loss_in_housing = pen.num_animals*GasEmissions.calc_E_NH3_storage_v2(barn_area=pen.barn_area_from_pen_type,TAN =urine_TAN, U=pen_urine, tempC=tempC)
        
        daily_output = ManureHandlerOutput(
                urea=pen.manure.U,
                TAN_s=pen.manure.TAN_s-NH3_loss_in_housing,
                manure_nitrogen=pen.manure.MN,
                TSd=pen.manure.TSd,
                VSd=pen.manure.VSd,
                VSnd=pen.manure.VSnd,
                WIP_frac=pen.manure.WIP_frac,
                WOP_frac=pen.manure.WOP_frac,
                p_excrt_manure=pen.manure.p_excrt_manure,
                K_manure=pen.manure.K_manure,
                CH4_floor=GasEmissions.calc_E_CH4_floor(pen),
                CO2_floor=GasEmissions.calc_E_C02_floor(pen),
                NH3_floor=NH3_loss_in_housing,

                raw_manure=pen.manure_mass,
                cleaning_water=self.cleaning_water_volume_in_main_barn(pen),
                total_bedding_mass=self.bedding.total_bedding_mass(pen),
                total_water_volume_in_milking_center=self.milking_center.total_water_volume_used_in_milking_center(
                        pen)
        )
        self.all_output.append(daily_output)
        return daily_output

    def cleaning_water_volume_in_main_barn(self, pen: SimplePen) -> float:
        return pen.num_animals * self.config.water_use_rate  # liters

    def total_daily_volume(self, pen: SimplePen) -> float:
        return sum([
            pen.manure_volume,  # m^3
            self.cleaning_water_volume_in_main_barn(pen) * Constants.LITERS_TO_CUBIC_METERS,  # m^3
            self.bedding.total_bedding_volume(pen),  # m^3
            self.milking_center.total_water_volume_used_in_milking_center(pen) * \
            Constants.LITERS_TO_CUBIC_METERS,  # m^3
            pen.manure.U,  # g/L
            pen.manure.TAN_s,  # g/L
            pen.manure.MN,  # kg
            pen.manure.TSd,  # kg
            pen.manure.VSd,  # kg
            pen.manure.VSnd,  # kg
            pen.manure.p_excrt_manure,  # kg
            pen.manure.K_manure  # kg
        ])


class FlushSystem(BaseManureHandler):
    pass


class ManualScraping(BaseManureHandler):
    pass


class AlleyScraper(BaseManureHandler):
    pass


@dataclass
class ManureHandlerConfig:
    """
    A class that contains custom initialization configuration used in the
    creation of a BaseManureHandler object.

    """
    water_use_rate: int = 0  # liters/animal/day
    time_per_cleaning: int = 8
    cleanings_per_day: int = 2


class DefaultManureHandlerConfigFactory:
    FLUSH_SYSTEM_CONFIG = ManureHandlerConfig(
            water_use_rate=757,  # liters
    )
    MANUAL_SCRAPING_CONFIG = ManureHandlerConfig(
            water_use_rate=10,  # liters
    )
    ALLEY_SCRAPER_CONFIG = ManureHandlerConfig(
            water_use_rate=10,  # liters
    )

    @classmethod
    def get_instance(cls, manure_handler_type: ManureHandlerType):
        manure_handler_config_by_type = {
            ManureHandlerType.FLUSH_SYSTEM: cls.FLUSH_SYSTEM_CONFIG,
            ManureHandlerType.MANUAL_SCRAPING: cls.MANUAL_SCRAPING_CONFIG,
            ManureHandlerType.ALLEY_SCRAPER: cls.ALLEY_SCRAPER_CONFIG
        }
        return manure_handler_config_by_type[manure_handler_type]


class ManureHandlerFactory:
    """A class that contains the logic for creating different types of manure handlers."""

    @classmethod
    def get_instance(cls,
                     manure_handler_type_name: str,
                     bedding_type_name: str,
                     manure_handler_config: Optional[ManureHandlerConfig] = None,
                     weather=None,
                     time=None) \
            -> BaseManureHandler:
        """
        Returns an instance of a specific subtype of BaseManureHandler based on
        the subtype specified in the given pen.

        Args:
            manure_handler_type_name: A string that specifies the type of manure handler.
            bedding_type_name: A string that specifies the type of bedding.
            manure_handler_config: A ManureHandlerConfig object that contains
                custom initialization data.

        Returns:
            A new instance of a BaseManureHandler subtype.

        """

        manure_handler_class_by_type: Dict[ManureHandlerType, Type[BaseManureHandler]] = {
            ManureHandlerType.FLUSH_SYSTEM: FlushSystem,
            ManureHandlerType.ALLEY_SCRAPER: AlleyScraper,
            ManureHandlerType.MANUAL_SCRAPING: ManualScraping,
        }

        manure_handler_type = ManureHandlerType.get_type(manure_handler_type_name)
        manure_handler_class = manure_handler_class_by_type[manure_handler_type]

        if manure_handler_config:
            return manure_handler_class(bedding_type_name, manure_handler_config,weather,time)
        else:
            default_manure_handler_config = DefaultManureHandlerConfigFactory.get_instance(
                    manure_handler_type)
            return manure_handler_class(bedding_type_name, default_manure_handler_config,weather,time)
