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

from RUFAS.routines.manure.default_enum.default_enum import DefaultEnum
from RUFAS.routines.manure.manure_separators.manure_separator_daily_output import ManureSeparatorDailyOutput
from RUFAS.routines.manure.reception_pits.reception_pit_daily_output import ReceptionPitDailyOutput


class ManureSeparatorType(DefaultEnum):
    ROTARY_SCREEN = auto()
    SCREW_PRESS = auto()
    BELT_PRESS = auto()
    DECANTING_CENTRIFUGE = auto()
    MOVING_DISC_PRESS = auto()
    SLOPE_SCREEN = auto()

    MECHANICAL_SAND_SEPARATOR = auto()
    SAND_LANE_MANURE_SEPARATION = auto()

    DEFAULT_ORGANIC = ROTARY_SCREEN
    DEFAULT_SAND = SAND_LANE_MANURE_SEPARATION

    @classmethod
    def get_default_type(cls, bedding_type='ORGANIC') -> DefaultEnum:
        if bedding_type == 'ORGANIC':
            return cls.DEFAULT_ORGANIC
        return cls.DEFAULT_SAND


class BaseManureSeparator:
    def __init__(self, manure_separator_config: ManureSeparatorConfig):
        self.config = manure_separator_config
        self.all_output: List[ManureSeparatorDailyOutput] = []

    def reset_daily_variables(self):
        pass

    @property
    def last_output(self) -> Optional[ManureSeparatorDailyOutput]:
        return self.all_output[-1] if len(self.all_output) > 0 else None

    def daily_update(self, reception_pit_daily_output: ReceptionPitDailyOutput) -> ManureSeparatorDailyOutput:
        """
        Description:
            Calls functions to calculate nutrient losses and transformations during
            manure separation.
            "pseudocode_manure_management" MS.4

        """
        rp = reception_pit_daily_output
        daily_output = ManureSeparatorDailyOutput(
                simulation_day=rp.simulation_day,
                pen_id=rp.pen_id,
                TAN=rp.TAN,
                N=rp.N,
                TS=rp.TS,
                VS_total=rp.VS_total,
                P=rp.P,
                K=rp.K,
                total_daily_manure_volume=rp.total_daily_manure_volume,

                final_solids_wet_mass=(
                        rp.TS * self.config.TS_removal_efficiency / self.config.percent_dry_solids
                ),

                final_solids_dry_mass=rp.TS,  # TODO: Review this

                TS_liquid=rp.TS * (1 - self.config.TS_removal_efficiency),
                VS_liquid=rp.VS_total * (1 - self.config.VS_removal_efficiency),
                N_liquid=rp.N * (1 - self.config.N_removal_efficiency),
                TAN_liquid=rp.TAN * (1 - self.config.TAN_removal_efficiency),
                P_liquid=rp.P * (1 - self.config.P_removal_efficiency),
                K_liquid=rp.K * (1 - self.config.K_removal_efficiency),

                TS_solid=rp.TS * self.config.TS_removal_efficiency,
                VS_solid=rp.VS_total * self.config.VS_removal_efficiency,
                N_solid=rp.N * self.config.N_removal_efficiency,
                P_solid=rp.P * self.config.P_removal_efficiency,
                K_solid=rp.K * self.config.K_removal_efficiency,

                TS_DM_effluent=rp.TS * self.config.TS_DM_effluent_rate  # TODO: Review this
        )
        self.all_output.append(daily_output)
        return daily_output


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


class SandLaneSystem(BaseManureSeparator):
    pass


class MechanicalSandSeparator(BaseManureSeparator):
    pass


@dataclass
class ManureSeparatorConfig:
    percent_dry_solids: float = 1.0
    TS_removal_efficiency: float = 0.0
    VS_removal_efficiency: float = 0.0
    N_removal_efficiency: float = 0.0
    TAN_removal_efficiency: float = 0.0
    P_removal_efficiency: float = 0.0
    K_removal_efficiency: float = 0.0
    TS_DM_effluent_rate: float = 0.0


class DefaultManureSeparatorConfigFactory:
    ROTARY_SCREEN_CONFIG = ManureSeparatorConfig(
            percent_dry_solids=0.2,
            TS_removal_efficiency=0.55,
            VS_removal_efficiency=0.55,
            N_removal_efficiency=0.3,
            TAN_removal_efficiency=0.15,
            P_removal_efficiency=0.4,
            K_removal_efficiency=0.15,
            TS_DM_effluent_rate=0.2
    )
    SCREW_PRESS_CONFIG = ManureSeparatorConfig(
            percent_dry_solids=0.35,
            TS_removal_efficiency=0.30,
            VS_removal_efficiency=0.5,
            N_removal_efficiency=0.3,
            TAN_removal_efficiency=0.10,
            P_removal_efficiency=0.2,
            K_removal_efficiency=0.23,
            TS_DM_effluent_rate=0.35
    )

    @classmethod
    def get_instance(cls, manure_separator_type: ManureSeparatorType) -> ManureSeparatorConfig:
        manure_separator_config_by_type: Dict[ManureSeparatorType, ManureSeparatorConfig] = {
            ManureSeparatorType.ROTARY_SCREEN: cls.ROTARY_SCREEN_CONFIG,
            ManureSeparatorType.SCREW_PRESS: cls.SCREW_PRESS_CONFIG
        }
        return manure_separator_config_by_type.get(manure_separator_type, ManureSeparatorConfig())


class ManureSeparatorFactory:
    @classmethod
    def get_instance(cls,
                     manure_separator_type_name: str,
                     manure_separator_config: Optional[ManureSeparatorConfig] = None) \
            -> BaseManureSeparator:

        manure_separator_class_by_type: Dict[ManureSeparatorType, Type[BaseManureSeparator]] = {
            ManureSeparatorType.BELT_PRESS: BeltPress,
            ManureSeparatorType.DECANTING_CENTRIFUGE: DecantingCentrifuge,
            ManureSeparatorType.MOVING_DISC_PRESS: MovingDiscPress,
            ManureSeparatorType.ROTARY_SCREEN: RotaryScreen,
            ManureSeparatorType.SCREW_PRESS: ScrewPress,
            ManureSeparatorType.SLOPE_SCREEN: SlopeScreen,
            ManureSeparatorType.SAND_LANE_MANURE_SEPARATION: SandLaneSystem
        }

        manure_separator_type = ManureSeparatorType.get_type(manure_separator_type_name)
        manure_separator_class = manure_separator_class_by_type.get(manure_separator_type, NullSeparator)

        if manure_separator_config:
            return manure_separator_class(manure_separator_config)
        else:
            default_manure_separator_config = DefaultManureSeparatorConfigFactory.get_instance(manure_separator_type)
            return manure_separator_class(default_manure_separator_config)
