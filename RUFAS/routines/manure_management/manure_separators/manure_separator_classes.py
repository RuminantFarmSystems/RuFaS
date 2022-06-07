"""
RUFAS: Ruminant Farm Systems Model

File name: manure_separator_classes.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu
            Yunus Mohammed, ymm26@cornell.edu 
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import auto
from typing import Dict, List, Optional, Type

from RUFAS.routines.manure_management.helpers.enum_helpers import ExtendedEnum
from RUFAS.routines.manure_management.manure_separators.manure_separator_output import ManureSeparatorOutput
from RUFAS.routines.manure_management.misc.simple_pen import SimplePen
from RUFAS.routines.manure_management.reception_pits.reception_pit_classes import BaseReceptionPit


class ManureSeparatorEnum(ExtendedEnum):
    ROTARY_SCREEN = auto()
    SCREW_PRESS = auto()

    BASE_SEPARATOR = auto()
    BELT_PRESS = auto()
    CUSTOM_SEPARATOR = auto()
    DECANTING_CENTRIFUGE = auto()
    MECHANICAL_SEPARATOR = auto()
    MOVING_DISC_PRESS = auto()
    NULL_SEPARATOR = auto()
    SEDIMENTATION = auto()
    SLOPE_SCREEN = auto()

    DEFAULT = ROTARY_SCREEN


class BaseSeparator:
    def __init__(self,
                 pen: SimplePen,
                 reception_pit: BaseReceptionPit,
                 separator_init_data: ManureSeparatorInitData):
        """
        Description:
            An instance of this class represents a manure separator method.
            It is primarily used by the manure separator sub-module

        Args:
        """
        self.pen = pen
        self.manure_separator_enum = ManureSeparatorEnum.get_enum(pen.manure_separator)
        self.separator_init_data = separator_init_data
        self.reception_pit = reception_pit
        self.all_output: List[ManureSeparatorOutput] = []

    def reset_daily_variables(self):
        pass

    @property
    def last_output(self) -> Optional[ManureSeparatorOutput]:
        return self.all_output[-1] if len(self.all_output) > 0 else None

    def update(self, pen: SimplePen) -> ManureSeparatorOutput:
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
            total_daily_mass=rp.total_daily_mass,

            final_solids_dry_content=rp.TSd,
            wet_weight_of_final_solids=rp.TSd * self.separator_init_data.TS_removal_efficiency / self.separator_init_data.percent_dry_solids,
            TS_liquid=rp.TSd * (1 - self.separator_init_data.TS_removal_efficiency),
            VS_liquid=(rp.VSd + rp.VSnd) * (1 - self.separator_init_data.VS_removal_efficiency),
            N_liquid=rp.manure_nitrogen * (1 - self.separator_init_data.N_removal_efficiency),
            TAN_liquid=rp.TAN_s * (1 - self.separator_init_data.TAN_removal_efficiency),
            P_liquid=rp.p_excrt_manure * (1 - self.separator_init_data.P_removal_efficiency),
            K_liquid=rp.K_manure * (1 - self.separator_init_data.K_removal_efficiency),

            TS_solid=rp.TSd * self.separator_init_data.TS_removal_efficiency,
            VS_solid=(rp.VSd + rp.VSnd) * self.separator_init_data.VS_removal_efficiency,
            N_solid=rp.manure_nitrogen * self.separator_init_data.N_removal_efficiency,
            TAN_solid=rp.TAN_s * self.separator_init_data.TAN_removal_efficiency,
            P_solid=rp.p_excrt_manure * self.separator_init_data.P_removal_efficiency,
            K_solid=rp.K_manure * self.separator_init_data.K_removal_efficiency,

            TS_DM_effluent=rp.TSd * self.separator_init_data.TS_DM_effluent_rate
        )
        self.all_output.append(daily_output)
        return daily_output

    def effluent_liquid(self):
        """
        Description:
            Calculate liquid nutrient content of the separator
            "pseudocode_manure_management" MS.4.A
        """

        # d.TS_liquid = d.TS - (d.TS * self.separator_init_data.TS_removal_efficiency)
        # d.VS_liquid = d.VS - (d.VS * self.separator_init_data.VS_removal_efficiency)
        # d.N_liquid = d.N - (d.N * self.separator_init_data.N_removal_efficiency)
        # d.P_liquid = d.P - (d.P * self.separator_init_data.P_removal_efficiency)
        # d.K_liquid = d.K - (d.K * self.separator_init_data.K_removal_efficiency)
        pass

    def effluent_solid(self):
        """
        Description:
            Update solid nutrient content of the separator
            "pseudocode_manure_management" MS.4.B
        """
        # d.TS -= d.TS_liquid
        # d.TS_DM_effluent = d.TS * self.separator_init_data.TS_DM_effluent_rate
        # d.TS -= d.TS_DM_effluent
        #
        # d.VS -= d.VS_liquid
        # d.N -= d.N_liquid
        # d.P -= d.P_liquid
        # d.K -= d.K_liquid
        pass

    def update_treatment_variables(self):
        """
        Description:
            Update solid and liquid nutrient contents of the treatment receptacle
            "pseudocode_manure_management" MS.4.C
        """
        pass


class BeltPress(BaseSeparator):
    def __init__(self,
                 pen: SimplePen,
                 reception_pit: BaseReceptionPit,
                 separator_init_data: ManureSeparatorInitData):
        super().__init__(pen, reception_pit, separator_init_data)


class DecantingCentrifuge(BaseSeparator):
    def __init__(self,
                 pen: SimplePen,
                 reception_pit: BaseReceptionPit,
                 separator_init_data: ManureSeparatorInitData):
        super().__init__(pen, reception_pit, separator_init_data)


class MechanicalSeparator(BaseSeparator):
    def __init__(self,
                 pen: SimplePen,
                 reception_pit: BaseReceptionPit,
                 separator_init_data: ManureSeparatorInitData):
        super().__init__(pen, reception_pit, separator_init_data)


class MovingDiscPress(BaseSeparator):
    def __init__(self,
                 pen: SimplePen,
                 reception_pit: BaseReceptionPit,
                 separator_init_data: ManureSeparatorInitData):
        super().__init__(pen, reception_pit, separator_init_data)


class RotaryScreen(BaseSeparator):
    def __init__(self,
                 pen: SimplePen,
                 reception_pit: BaseReceptionPit,
                 separator_init_data: ManureSeparatorInitData):
        super().__init__(pen, reception_pit, separator_init_data)


class ScrewPress(BaseSeparator):
    def __init__(self,
                 pen: SimplePen,
                 reception_pit: BaseReceptionPit,
                 separator_init_data: ManureSeparatorInitData):
        super().__init__(pen, reception_pit, separator_init_data)


class Sedimentation(BaseSeparator):
    def __init__(self,
                 pen: SimplePen,
                 reception_pit: BaseReceptionPit,
                 separator_init_data: ManureSeparatorInitData):
        super().__init__(pen, reception_pit, separator_init_data)


class SlopeScreen(BaseSeparator):
    def __init__(self,
                 pen: SimplePen,
                 reception_pit: BaseReceptionPit,
                 separator_init_data: ManureSeparatorInitData):
        super().__init__(pen, reception_pit, separator_init_data)


class CustomSeparator(BaseSeparator):
    def __init__(self,
                 pen: SimplePen,
                 reception_pit: BaseReceptionPit,
                 separator_init_data: ManureSeparatorInitData):
        super().__init__(pen, reception_pit, separator_init_data)


class NullSeparator(BaseSeparator):
    def __init__(self,
                 pen: SimplePen,
                 reception_pit: BaseReceptionPit,
                 separator_init_data: ManureSeparatorInitData):
        super().__init__(pen, reception_pit, separator_init_data)


@dataclass
class ManureSeparatorInitData:
    percent_dry_solids: float = 0.0
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
        if manure_separator_enum in enum_to_init_data:
            return enum_to_init_data[manure_separator_enum]
        return ManureSeparatorInitData()


class ManureSeparatorFactory:
    @classmethod
    def get_instance(cls, pen: SimplePen, reception_pit: BaseReceptionPit) -> BaseSeparator:
        manure_separator_enum = ManureSeparatorEnum.get_enum(pen.manure_handler)
        params = {
            'pen': pen,
            'reception_pit': reception_pit,
            'separator_init_data': ManureSeparatorInitData.get_instance(manure_separator_enum)
        }

        enum_to_class: Dict[ManureSeparatorEnum, Type[BaseSeparator]] = {
            ManureSeparatorEnum.BASE_SEPARATOR: BaseSeparator,
            ManureSeparatorEnum.BELT_PRESS: BeltPress,
            ManureSeparatorEnum.CUSTOM_SEPARATOR: CustomSeparator,
            ManureSeparatorEnum.DECANTING_CENTRIFUGE: DecantingCentrifuge,
            ManureSeparatorEnum.MECHANICAL_SEPARATOR: MechanicalSeparator,
            ManureSeparatorEnum.MOVING_DISC_PRESS: MovingDiscPress,
            ManureSeparatorEnum.NULL_SEPARATOR: NullSeparator,
            ManureSeparatorEnum.ROTARY_SCREEN: RotaryScreen,
            ManureSeparatorEnum.SCREW_PRESS: ScrewPress,
            ManureSeparatorEnum.SEDIMENTATION: Sedimentation,
            ManureSeparatorEnum.SLOPE_SCREEN: SlopeScreen
        }

        return enum_to_class[manure_separator_enum](**params)
