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
    def __init__(self,
                 pen: SimplePen,
                 reception_pit: BaseReceptionPit,
                 separator_init_data: ManureSeparatorInitData):
        self.pen = pen
        self.manure_separator_enum = ManureSeparatorEnum.get_enum(pen.manure_separator)
        self.init_data = separator_init_data
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
            wet_weight_of_final_solids=rp.TSd * self.init_data.TS_removal_efficiency / self.init_data.percent_dry_solids,
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


class BaseSandSeparator:
    """
    Description
    ------------
    An instance of SandSeparator has a method separateSand() which removes sand
    present in this SandSeparator. It also has two resetters- resetSeparator and
    resetSand. See their implementations below for description. Each instance
    has the following attributes and the corresponding invariants, getters, and
    setters.

    Attributes
    ----------
    Attribute _manure: The manure held in the SanSeparator
    invariant: _manure must be a Manure Object or None.

    Attribute _sand: The sand that has been removed from Manure.
    Invariant: _sand must be a SandBedding Object or None

    Attribute _sand_removal_efficiency: The fraction of sand removed from Manure
    in each separation cycle.
    Invariant: A flaot >=0.6 and <=0.9
    """

    def __init__(self, efficiency=1.0, manure=None, sand=None):
        """
        Initializes a SandSeparator

        Parameter efficiency: the sand separation efficiency
        Precondition: between 0.7 and 1.0

        Parameter manure: The manure held in this SandSeparator
        Precondition: Manure Object or None

        Parameter sand: The sand present in this SandSeparator
        Precondition: Must be a SandBedding Object
        """
        self._manure = manure
        self._sand_bedding = sand
        self._sand_removal_efficiency = efficiency

    def output(self):
        """
        Returns the Manure _manure in this Separator and resets _manure to None.

        Return type: Manure or None
        """
        manure = self._manure
        self._manure = None
        return manure

    def separateSand(self):
        """
        Does one cycle of sand separation on the manure present
        """
        if not self._manure:  # Max
            return

        sand = self._manure.getBedding()

        separated_sand_mass = self._sand_removal_efficiency * sand.getMass()
        remaining_sand_mass = sand.getMass() - separated_sand_mass

        self._sand_bedding.setMass(separated_sand_mass)
        sand.setMass(remaining_sand_mass)

    # getters
    def getEfficiency(self):
        """
        Returns the effiency of this SandSeparator
        """
        return self._sand_removal_efficiency

    def getManure(self):
        """
        Returns the manure in this SandSeparator
        """
        return self._manure

    def getSand(self):
        """
        Returns the Sand in this SandSeparator
        """
        return self._sand_bedding

    # resetters
    def resetSeparator(self):
        """
        Reset the _sand to None and _sand to 0 mass SandBedding
        """
        self._manure = None
        self.resetSand()

    def resetSand(self):
        """
        Reset Sand to 0 mass SandBedding
        """
        self._sand_bedding.setMass(0.0)

    # setters
    def setEfficiency(self, efficiency):
        """
        Sets _efficiency to efficiency

        Parameter efficiency: The new efficiency of the SandSeparator
        Precondition: float >=0.6 and <=0.9
        """
        self._sand_removal_efficiency = efficiency

    def setManure(self, manure=None):
        """
        Sets _manure to manure

        Parameter manure: The new manure held by this SandSeparator.
        Precondition: manure must be distinct from _manure.
        manure.getBedding() must return a SandBedding.
        """
        assert manure != self._manure, "The Manure is already in this SandSepearator. Use a different Manure object"
        if self._manure and manure:
            self._manure.aggregateManure(manure)
        else:
            self._manure = manure

    # def __init__(self, treatment_data, pen):
    #     super().__init__(treatment_data, pen)
    #     if self.default: self.set_defaults()

    # def set_defaults(self):
    #     self.TS_removal_efficiency = 0.3
    #     self.VS_removal_efficiency = 0.55
    #     self.N_removal_efficiency = 0.3
    #     self.P_removal_efficiency = 0.4
    #     self.K_removal_efficiency = 0.15
    #     self.TS_DM_effluent_rate = 0.2


class SandLaneSystem(BaseSandSeparator):
    def __init__(self, sand_lane_data):
        super.__init__()
        if sand_lane_data is None or sand_lane_data['default']:
            self.default_sand_lane()
        else:
            self.sand_separated = sand_lane_data['sand_separated']

    def default_sand_lane(self):
        self.sand_separated = 1.0  # range from .6-.9 USER INPUT

    def total_daily_mass(self):
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


class MechanicalSandSeparator(BaseSandSeparator):
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
        if manure_separator_enum in enum_to_init_data:
            return enum_to_init_data[manure_separator_enum]
        return ManureSeparatorInitData()


class ManureSeparatorFactory:
    @classmethod
    def get_instance(cls, pen: SimplePen, reception_pit: BaseReceptionPit) -> BaseSeparator:
        manure_separator_enum = ManureSeparatorEnum.get_enum(pen.manure_separator)
        params = {
            'pen': pen,
            'reception_pit': reception_pit,
            'separator_init_data': ManureSeparatorInitData.get_instance(manure_separator_enum)
        }

        enum_to_class: Dict[ManureSeparatorEnum, Type[BaseSeparator]] = {
            ManureSeparatorEnum.BELT_PRESS: BeltPress,
            ManureSeparatorEnum.DECANTING_CENTRIFUGE: DecantingCentrifuge,
            ManureSeparatorEnum.MOVING_DISC_PRESS: MovingDiscPress,
            ManureSeparatorEnum.NULL_SEPARATOR: NullSeparator,
            ManureSeparatorEnum.ROTARY_SCREEN: RotaryScreen,
            ManureSeparatorEnum.SCREW_PRESS: ScrewPress,
            ManureSeparatorEnum.SLOPE_SCREEN: SlopeScreen,
            ManureSeparatorEnum.SAND_LANE_MANURE_SEPARATION: SandLaneSystem
        }

        return enum_to_class[manure_separator_enum](**params)
