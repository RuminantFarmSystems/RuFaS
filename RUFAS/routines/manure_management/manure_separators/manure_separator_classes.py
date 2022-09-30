"""
RUFAS: Ruminant Farm Systems Model

File name: manure_separator_classes.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu 
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import auto
from typing import Dict, List, Optional, Type

from RUFAS.routines.manure_management.helpers.enum_helpers import ExtendedEnum
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


class BaseManureSeparator:
    def __init__(self, pen: SimplePen,
                 reception_pit: BaseReceptionPit,
                 separator_init_data: ManureSeparatorInitData):
        self.pen = pen
        self.manure_separator_enum = ManureSeparatorEnum.get_type(pen.manure_separator)
        self.reception_pit = reception_pit
        self.init_data = separator_init_data
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


class BeltPress(BaseManureSeparator):
    pass


class DecantingCentrifuge(BaseManureSeparator):
    pass


class MechanicalSeparator(BaseManureSeparator):
    pass


class MovingDiscPress(BaseManureSeparator):
    pass


class RotaryScreen(BaseManureSeparator):
    pass


class ScrewPress(BaseManureSeparator):
    pass


class Sedimentation(BaseManureSeparator):
    pass


class SlopeScreen(BaseManureSeparator):
    pass


class CustomSeparator(BaseManureSeparator):
    pass


class NullSeparator(BaseManureSeparator):
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


class SandLaneSystem(BaseManureSeparator):
    pass


class MechanicalSandSeparator(BaseManureSeparator):
    pass


@dataclass
class ManureSeparatorInitData:
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
    def get_instance(cls, pen: SimplePen, reception_pit: BaseReceptionPit) -> BaseManureSeparator:
        manure_separator_enum = ManureSeparatorEnum.get_type(pen.manure_separator)

        enum_to_class: Dict[ManureSeparatorEnum, Type[BaseManureSeparator]] = {
            ManureSeparatorEnum.BELT_PRESS: BeltPress,
            ManureSeparatorEnum.DECANTING_CENTRIFUGE: DecantingCentrifuge,
            ManureSeparatorEnum.MOVING_DISC_PRESS: MovingDiscPress,
            ManureSeparatorEnum.NULL_SEPARATOR: NullSeparator,
            ManureSeparatorEnum.ROTARY_SCREEN: RotaryScreen,
            ManureSeparatorEnum.SCREW_PRESS: ScrewPress,
            ManureSeparatorEnum.SLOPE_SCREEN: SlopeScreen,
            ManureSeparatorEnum.SAND_LANE_MANURE_SEPARATION: SandLaneSystem
        }

        params = {
            'pen': pen,
            'reception_pit': reception_pit,
            'separator_init_data': ManureSeparatorInitData.get_instance(manure_separator_enum)
        }

        return enum_to_class[manure_separator_enum](**params)
