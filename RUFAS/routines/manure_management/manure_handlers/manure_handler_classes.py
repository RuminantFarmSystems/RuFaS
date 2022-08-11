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
from RUFAS.routines.manure_management.helpers.enum_helpers import ExtendedEnum
from RUFAS.routines.manure_management.manure_handlers.bedding_classes import BeddingEnum
from RUFAS.routines.manure_management.manure_handlers.bedding_manager import BeddingManager
from RUFAS.routines.manure_management.manure_handlers.manure_handler_output import ManureHandlerOutput
from RUFAS.routines.manure_management.manure_handlers.milking_center import MilkingCenter
from RUFAS.routines.manure_management.misc.constants import ManureManagementConstants as Constants
from RUFAS.routines.manure_management.misc.simple_pen import SimplePen


class ManureHandlerEnum(ExtendedEnum):
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
                 pen: SimplePen,
                 handler_init_data: ManureHandlerInitData):
        """
        Initializes a BaseManureHandler object.

        Args
        ----
        pen: A SimplePen object that specifies the types of manure handler and bedding used.
        handler_init_data: A ManureHandlerInitData object that specifies default data
            specific to the choice of manure handler.

        """

        self.handler_init_data = handler_init_data
        self.sand_lane = None  # TODO: Not yet implemented

        self.manure_handler_enum = ManureHandlerEnum.get_enum(
                pen.manure_handler)
        self.bedding_manager = BeddingManager.get_instance(pen.bedding_type)
        self.milking_center = MilkingCenter()

        self.all_output: List[ManureHandlerOutput] = []

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
        # bedding_mass = self.bedding_manager.total_bedding_mass(pen)
        # if self.bedding_manager.bedding_enum is BeddingEnum.SAND:
        #     bedding_mass *= (1 - efficiency)

        daily_output = ManureHandlerOutput(
                urea=pen.manure.U,
                TAN_s=pen.manure.TAN_s,
                manure_nitrogen=pen.manure.MN,
                TSd=pen.manure.TSd,
                VSd=pen.manure.VSd,
                VSnd=pen.manure.VSnd,
                p_excrt_manure=pen.manure.p_excrt_manure,
                K_manure=pen.manure.K_manure,
                CH4_floor=GasEmissions.calc_E_CH4_floor(pen),
                CO2_floor=GasEmissions.calc_E_C02_floor(pen),

                raw_manure=pen.manure_mass,
                cleaning_water=self.cleaning_water_volume_in_main_barn(pen),
                total_bedding_mass=self.bedding_manager.total_bedding_mass(pen),
                total_water_volume_in_milking_center=self.milking_center.total_water_volume_used_in_milking_center(
                        pen)
        )
        self.all_output.append(daily_output)
        return daily_output

    def cleaning_water_volume_in_main_barn(self, pen: SimplePen) -> float:
        return pen.num_animals * self.handler_init_data.water_use_rate  # liters

    def total_daily_volume(self, pen: SimplePen) -> float:
        return sum([
            pen.manure_volume,  # m^3
            self.cleaning_water_volume_in_main_barn(
                    pen) * Constants.LITERS_TO_CUBIC_METERS,  # m^3
            self.bedding_manager.total_bedding_volume(pen),  # m^3
            self.milking_center.total_water_volume_used_in_milking_center(
                    pen) * Constants.LITERS_TO_CUBIC_METERS,
            # m^3
            pen.manure.U,  # g/L
            pen.manure.TAN_s,  # g/L
            pen.manure.MN,  # kg
            pen.manure.TSd,  # kg
            pen.manure.VSd,  # kg
            pen.manure.VSnd,  # kg
            pen.manure.p_excrt_manure,  # kg
            pen.manure.K_manure  # kg
        ])

    # TODO: unused
    def init_sand_lane(self, sand_lane_data):
        # if self.bedding_manager.bedding_enum is BeddingEnum.SAND:
        #     self.sand_lane = SandSeparationLane(sand_lane_data)
        pass

    # TODO: move to sand lane class
    # def sand_lane(self):
    #     """
    #     Description:
    #         Sand separation lane. Method only called for sand bedding.
    #     """
    #     sand_lane = self.sand_lane
    #     sand_lane.sand_washed_with_water = self.bedding_mass_per_day  # kg/day
    #     sand_lane.sand_mass_separated = sand_lane.sand_separation_efficiency * \
    #                                     sand_lane.sand_washed_with_water  # kg/day
    #     sand_lane.sand_volume_separated = sand_lane.sand_mass_separated / self.bedding_density  # m3/day


class FlushSystem(BaseManureHandler):
    def __init__(self, pen: SimplePen, handler_init_data: ManureHandlerInitData):
        super().__init__(pen, handler_init_data)


class ManualScraping(BaseManureHandler):
    def __init__(self, pen: SimplePen, handler_init_data: ManureHandlerInitData):
        super().__init__(pen, handler_init_data)


class AlleyScraper(BaseManureHandler):
    def __init__(self, pen: SimplePen, handler_init_data: ManureHandlerInitData):
        super().__init__(pen, handler_init_data)


@dataclass
class ManureHandlerInitData:
    """
    A class that contains custom initialization configuration used in the
    creation of a BaseManureHandler object.

    """
    water_use_rate: int = 0  # liters/animal/day
    time_per_cleaning: int = 8
    cleanings_per_day: int = 2

    @classmethod
    def get_instance(cls, manure_handler_enum: ManureHandlerEnum):
        """
        Returns an instance of ManureHandlerInitData based on a given ManureHandlerEnum.

        Args:
            manure_handler_enum: a member of the ManureHandlerEnum.

        Returns:
            A new ManureHandlerInitData object.

        """
        init_data = ManureHandlerInitData()
        enum_to_water_use_rate: Dict[ManureHandlerEnum, int] = {
            ManureHandlerEnum.FLUSH_SYSTEM: 757,  # liters
            ManureHandlerEnum.MANUAL_SCRAPING: 10,  # liters
            ManureHandlerEnum.ALLEY_SCRAPER: 10  # liters
        }
        if manure_handler_enum in enum_to_water_use_rate:
            init_data.water_use_rate = enum_to_water_use_rate[manure_handler_enum]
        return init_data


class ManureHandlerFactory:
    """A class that contains the logic for creating different types of manure handlers."""

    @classmethod
    def get_instance(cls, pen: SimplePen) -> BaseManureHandler:
        """
        Returns an instance of a specific subtype of BaseManureHandler based on
        the subtype specified in the given pen.

        Args:
            pen: A SimplePen object that specifies which subtype of BaseManureHandler
                is needed.

        Returns:
            A new instance of a BaseManureHandler subtype.

        """
        manure_handler_enum = ManureHandlerEnum.get_enum(pen.manure_handler)

        params = {
            'pen': pen,
            'handler_init_data': ManureHandlerInitData.get_instance(manure_handler_enum)
        }

        enum_to_class: Dict[ManureHandlerEnum, Type[BaseManureHandler]] = {
            ManureHandlerEnum.FLUSH_SYSTEM: FlushSystem,
            ManureHandlerEnum.ALLEY_SCRAPER: AlleyScraper,
            ManureHandlerEnum.MANUAL_SCRAPING: ManualScraping,
        }

        return enum_to_class[manure_handler_enum](**params)
