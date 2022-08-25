"""
RUFAS: Ruminant Farm Systems Model

File name: manure_separator_classes.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu 
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import auto
from typing import Dict, List, Optional, Tuple, Type

from RUFAS.routines.manure_management.helpers.enum_helpers import ExtendedEnum
from RUFAS.routines.manure_management.manure_handlers.bedding_classes import BeddingEnum
from RUFAS.routines.manure_management.manure_separators.manure_separator_output import ManureSeparatorOutput
from RUFAS.routines.manure_management.misc.simple_pen import SimplePen
from RUFAS.routines.manure_management.reception_pits.reception_pit_classes import BaseReceptionPit


class ManureSeparatorEnum(ExtendedEnum):
    ROTARY_SCREEN = auto()
    SCREW_PRESS = auto()

    BELT_PRESS = auto()
    DECANTING_CENTRIFUGE = auto()
    MOVING_DISC_PRESS = auto()
    SLOPE_SCREEN = auto()

    MECHANICAL_SAND_SEPARATOR = auto()
    SAND_LANE_MANURE_SEPARATION = auto()
    NULL_SEPARATOR = auto()

    DEFAULT_ORGANIC = ROTARY_SCREEN
    DEFAULT_SAND = SAND_LANE_MANURE_SEPARATION

    # Organic bedding => default = rotary screen
    # Sand bedding => default = sand lane

    @classmethod
    def get_default_enum(cls, bedding_type='ORGANIC') -> ExtendedEnum:
        if bedding_type == 'ORGANIC':
            return cls.DEFAULT_ORGANIC
        return cls.DEFAULT_SAND


class BaseSeparator:
    def __init__(self, pen: SimplePen, reception_pit: BaseReceptionPit):
        self.pen = pen
        self.manure_separator_enum = ManureSeparatorEnum.get_enum(pen.manure_separator)
        self.reception_pit = reception_pit
        self.all_output: List[ManureSeparatorOutput] = []

    def reset_daily_variables(self):
        pass

    @property
    def last_output(self) -> Optional[ManureSeparatorOutput]:
        return self.all_output[-1] if len(self.all_output) > 0 else None

    def update(self) -> ManureSeparatorOutput:
        """
        Description:
            Calls functions to calculate nutrient losses and transformations during
            manure separation.
            "pseudocode_manure_management" MS.4

        """
        rp = self.reception_pit.last_output

        daily_output = ManureSeparatorOutput(
                TAN_s=rp.TAN_s,
                manure_nitrogen=rp.manure_nitrogen,
                TSd=rp.TSd,
                VSd=rp.VSd,
                VSnd=rp.VSnd,
                p_excrt_manure=rp.p_excrt_manure,
                K_manure=rp.K_manure,
                total_daily_mass=self.total_daily_mass(),

                final_solids_dry_content=rp.TSd,
                wet_weight_of_final_solids=rp.TSd * self.init_data.TS_removal_efficiency /
                                           self.init_data.percent_dry_solids,
                TS_liquid=rp.TSd * (1 - self.init_data.TS_removal_efficiency),
                VS_liquid=(rp.VSd + rp.VSnd) * (1 - self.init_data.VS_removal_efficiency),
                N_liquid=rp.manure_nitrogen * (1 - self.init_data.N_removal_efficiency),
                TAN_liquid=rp.TAN_s * (1 - self.init_data.TAN_removal_efficiency),
                P_liquid=rp.p_excrt_manure * (1 - self.init_data.P_removal_efficiency),
                K_liquid=rp.K_manure * (1 - self.init_data.K_removal_efficiency),

                TS_solid=rp.TSd * self.init_data.TS_removal_efficiency,
                VS_solid=(rp.VSd + rp.VSnd) * self.init_data.VS_removal_efficiency,
                N_solid=rp.manure_nitrogen * self.init_data.N_removal_efficiency,
                TAN_solid=rp.TAN_s * self.init_data.TAN_removal_efficiency,
                P_solid=rp.p_excrt_manure * self.init_data.P_removal_efficiency,
                K_solid=rp.K_manure * self.init_data.K_removal_efficiency,

                TS_DM_effluent=rp.TSd * self.init_data.TS_DM_effluent_rate
        )
        self.all_output.append(daily_output)
        return daily_output

    def total_daily_mass(self):
        return self.reception_pit.last_output.total_daily_mass

    def effluent_liquid(self):
        pass

    def effluent_solid(self):
        pass

    def update_treatment_variables(self):
        pass


class BaseManureSeparator(BaseSeparator):

    def __init__(self, pen: SimplePen, reception_pit: BaseReceptionPit,
                 separator_init_data: ManureSeparatorInitData):
        super().__init__(pen, reception_pit)
        self.init_data = separator_init_data

    def update(self) -> ManureSeparatorOutput:
        """
        Description:
            Calls functions to calculate nutrient losses and transformations during
            manure separation.
            "pseudocode_manure_management" MS.4

        """
        rp = self.reception_pit.last_output

        daily_output = ManureSeparatorOutput(
                TAN_s=rp.TAN_s,
                manure_nitrogen=rp.manure_nitrogen,
                TSd=rp.TSd,
                VSd=rp.VSd,
                VSnd=rp.VSnd,
                p_excrt_manure=rp.p_excrt_manure,
                K_manure=rp.K_manure,
                total_daily_mass=self.total_daily_mass(),

                final_solids_dry_content=rp.TSd,
                wet_weight_of_final_solids=rp.TSd * self.init_data.TS_removal_efficiency /
                                           self.init_data.percent_dry_solids,
                TS_liquid=rp.TSd * (1 - self.init_data.TS_removal_efficiency),
                VS_liquid=(rp.VSd + rp.VSnd) * (1 - self.init_data.VS_removal_efficiency),
                N_liquid=rp.manure_nitrogen * (1 - self.init_data.N_removal_efficiency),
                TAN_liquid=rp.TAN_s * (1 - self.init_data.TAN_removal_efficiency),
                P_liquid=rp.p_excrt_manure * (1 - self.init_data.P_removal_efficiency),
                K_liquid=rp.K_manure * (1 - self.init_data.K_removal_efficiency),

                TS_solid=rp.TSd * self.init_data.TS_removal_efficiency,
                VS_solid=(rp.VSd + rp.VSnd) * self.init_data.VS_removal_efficiency,
                N_solid=rp.manure_nitrogen * self.init_data.N_removal_efficiency,
                TAN_solid=rp.TAN_s * self.init_data.TAN_removal_efficiency,
                P_solid=rp.p_excrt_manure * self.init_data.P_removal_efficiency,
                K_solid=rp.K_manure * self.init_data.K_removal_efficiency,

                TS_DM_effluent=rp.TSd * self.init_data.TS_DM_effluent_rate
        )
        self.all_output.append(daily_output)
        return daily_output


class BeltPress(BaseSeparator):
    pass


class DecantingCentrifuge(BaseSeparator):
    pass


class MechanicalSeparator(BaseSeparator):
    pass


class MovingDiscPress(BaseSeparator):
    pass


class RotaryScreen(BaseSeparator):
    pass


class ScrewPress(BaseSeparator):
    pass


class Sedimentation(BaseSeparator):
    pass


class SlopeScreen(BaseSeparator):
    pass


class CustomSeparator(BaseSeparator):
    pass


class NullSeparator(BaseSeparator):
    pass


class SandLaneSystem(BaseSeparator):
    def total_daily_mass(self):
        manure_handler = self.reception_pit.manure_handler
        total_bedding_mass = manure_handler.bedding.total_bedding_mass()
        return total_bedding_mass * (1 - self.efficiency)
        # manure_handler = self.reception_pit.manure_handler
        # bedding_manager = manure_handler.bedding_manager
        # total_bedding_mass = bedding_manager.total_bedding_mass()
        # total_bedding_volume = bedding_manager.total_bedding_volume()
        # if bedding_manager.bedding_enum is BeddingEnum.SAND:
        #     total_bedding_mass *= (1 - efficiency)

        # bedding_mass = self.bedding_manager.total_bedding_mass(pen)
        # if self.bedding_manager.bedding_enum is BeddingEnum.SAND:
        #     bedding_mass *= (1 - efficiency)
        pass


class MechanicalSandSeparator(BaseSeparator):
    pass


@dataclass
class BaseManureSeparatorInitData(ABC):
    @classmethod
    @abstractmethod
    def get_instance(cls, manure_separator_enum: ManureSeparatorEnum) -> BaseManureSeparatorInitData:
        pass


@dataclass
class SandSeparatorInitData(BaseManureSeparatorInitData):
    efficiency: float = 1.0

    @classmethod
    def get_instance(cls, manure_separator_enum: ManureSeparatorEnum) -> SandSeparatorInitData:
        enum_to_init_data: Dict[ManureSeparatorEnum, SandSeparatorInitData] = {
            ManureSeparatorEnum.SAND_LANE_MANURE_SEPARATION: SandSeparatorInitData(efficiency=1.0)
        }
        return enum_to_init_data.get(manure_separator_enum, SandSeparatorInitData())


@dataclass
class ManureSeparatorInitData(BaseManureSeparatorInitData):
    percent_dry_solids: float = 1.0
    TS_removal_efficiency: float = 0.0
    VS_removal_efficiency: float = 0.0
    N_removal_efficiency: float = 0.0
    TAN_removal_efficiency: float = 0.0
    P_removal_efficiency: float = 0.0
    K_removal_efficiency: float = 0.0
    TS_DM_effluent_rate: float = 0.0

    @classmethod
    def get_instance(cls, manure_separator_enum: ManureSeparatorEnum) -> ManureSeparatorInitData:
        enum_to_init_data: Dict[ManureSeparatorEnum, ManureSeparatorInitData] = {
            ManureSeparatorEnum.ROTARY_SCREEN: ManureSeparatorInitData(
                    percent_dry_solids=0.2,
                    TS_removal_efficiency=0.55,
                    VS_removal_efficiency=0.55,
                    N_removal_efficiency=0.3,
                    TAN_removal_efficiency=0.15,
                    P_removal_efficiency=0.4,
                    K_removal_efficiency=0.15,
                    TS_DM_effluent_rate=0.2
            ),
            ManureSeparatorEnum.SCREW_PRESS: ManureSeparatorInitData(
                    percent_dry_solids=0.35,
                    TS_removal_efficiency=0.30,
                    VS_removal_efficiency=0.5,
                    N_removal_efficiency=0.3,
                    TAN_removal_efficiency=0.10,
                    P_removal_efficiency=0.2,
                    K_removal_efficiency=0.23,
                    TS_DM_effluent_rate=0.35
            )
        }
        return enum_to_init_data.get(manure_separator_enum, ManureSeparatorInitData())


class ManureSeparatorFactory:
    @classmethod
    def get_instance(cls, pen: SimplePen, reception_pit: BaseReceptionPit) -> BaseSeparator:
        manure_separator_enum = ManureSeparatorEnum.get_enum(pen.manure_separator)

        enum_to_class: Dict[ManureSeparatorEnum, Tuple[Type[BaseSeparator], Type[BaseManureSeparatorInitData]]] = {
            # ManureSeparatorEnum.BELT_PRESS: BeltPress,
            # ManureSeparatorEnum.DECANTING_CENTRIFUGE: DecantingCentrifuge,
            # ManureSeparatorEnum.MOVING_DISC_PRESS: MovingDiscPress,
            ManureSeparatorEnum.NULL_SEPARATOR: (NullSeparator, ManureSeparatorInitData),
            ManureSeparatorEnum.ROTARY_SCREEN: (RotaryScreen, ManureSeparatorInitData),
            # ManureSeparatorEnum.SCREW_PRESS: ScrewPress,
            # ManureSeparatorEnum.SLOPE_SCREEN: SlopeScreen,
            ManureSeparatorEnum.SAND_LANE_MANURE_SEPARATION: (SandLaneSystem, SandSeparatorInitData)
        }

        params = {
            'pen': pen,
            'reception_pit': reception_pit,
            'separator_init_data': enum_to_class[manure_separator_enum][1].get_instance(manure_separator_enum)
        }

        return enum_to_class[manure_separator_enum][0](**params)
