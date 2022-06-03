"""
RUFAS: Ruminant Farm Systems Model

File name: storage_pond.py

Description:

Author(s):  William Donovan, wmdonovan@wisc.edu 
            Yunus Mohammed, ymm26@cornell.edu
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import auto
from typing import Dict, List, Optional, Type

from RUFAS.routines.manure_management.helpers.enum_helpers import ExtendedEnum
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes import \
    BaseManureHandler
from RUFAS.routines.manure_management.manure_separators.manure_separator_classes import BaseSeparator
from RUFAS.routines.manure_management.misc.simple_pen import SimplePen
from RUFAS.routines.manure_management.reception_pits.reception_pit_output import ReceptionPitOutput
from RUFAS.routines.manure_management.treatments.treatment_output import TreatmentOutput


class TreatmentEnum(ExtendedEnum):
    STORAGE_POND = auto()
    ANAEROBIC_LAGOON = auto()
    ANAEROBIC_DIGESTION = auto()
    CUSTOM_STORAGE = auto()

    DEFAULT = STORAGE_POND


class BaseTreatment:
    def __init__(self,
                 pen: SimplePen,
                 manure_handler: BaseManureHandler,
                 manure_separator: BaseSeparator,
                 treatment_init_data: TreatmentInitData):
        """
        Description:
            An instance of this class represents an storage receptacle.
            It is primarily used by the emissions sub-module

        Args:
            pen
            treatment_init_data
        """
        self.pen = pen
        self.treatment_enum = TreatmentEnum.get_enum(pen.manure_storage)
        self.treatment_init_data = treatment_init_data
        self.manure_handler = manure_handler
        self.manure_separator = manure_separator

        self.all_output: List[TreatmentOutput] = []

    def reset_daily_variables(self):
        pass

    @property
    def last_output(self) -> Optional[ReceptionPitOutput]:
        return self.all_output[-1] if len(self.all_output) > 0 else None

    def update(self, pen: SimplePen) -> TreatmentOutput:
        # self.methane(pen.manure)
        # self.WIP_WOP_frac()
        daily_output = TreatmentOutput(

        )
        self.all_output.append(daily_output)
        return daily_output

    def methane(self, manure):
        # manure.CH4_emissions = self.VS * manure.Bo * manure.MCF * manure.MS * manure.m3
        # self.daily_vars.CH4 = self.daily_vars.VS * Constants.Bo * Constants.MCF * Constants.MS * Constants.m3
        pass

    def WIP_WOP_frac(self):
        # daily = self.daily_vars
        # if daily.TS + daily.VS == 0:
        #     daily.WIP_frac = 0.0
        #     daily.WOP_frac = 0.0
        # else:
        #     daily.WIP_frac = daily.WIP / (daily.TS + daily.VS)
        #     daily.WOP_frac = daily.WOP / (daily.TS + daily.VS)
        pass


class AnaerobicDigestion(BaseTreatment):
    def __init__(self,
                 pen: SimplePen,
                 manure_handler: BaseManureHandler,
                 manure_separator: BaseSeparator,
                 treatment_init_data: TreatmentInitData):
        super().__init__(pen, manure_handler, manure_separator, treatment_init_data)


class AnaerobicLagoon(BaseTreatment):
    def __init__(self,
                 pen: SimplePen,
                 manure_handler: BaseManureHandler,
                 manure_separator: BaseSeparator,
                 treatment_init_data: TreatmentInitData):
        super().__init__(pen, manure_handler, manure_separator, treatment_init_data)


class CustomTreatment(BaseTreatment):
    def __init__(self,
                 pen: SimplePen,
                 manure_handler: BaseManureHandler,
                 manure_separator: BaseSeparator,
                 treatment_init_data: TreatmentInitData):
        super().__init__(pen, manure_handler, manure_separator, treatment_init_data)


class StoragePond(BaseTreatment):
    def __init__(self,
                 pen: SimplePen,
                 manure_handler: BaseManureHandler,
                 manure_separator: BaseSeparator,
                 treatment_init_data: TreatmentInitData):
        super().__init__(pen, manure_handler, manure_separator, treatment_init_data)


@dataclass
class TreatmentInitData:
    """
    A data class that contains information used in the
    creation of a ManureHandler object.

    """

    sludge_accumulation_volume: float = 0.00251
    hydraulic_retention_time: int = 180
    sludge_accumulation_period: float = 5.0

    @classmethod
    def get_instance(cls, treatment_enum: TreatmentEnum) -> TreatmentInitData:
        init_data = TreatmentInitData()

        # Customize init data here based on enum if necessary
        # ...

        return init_data


class TreatmentFactory:
    @classmethod
    def get_instance(cls,
                     pen: SimplePen,
                     manure_handler: BaseManureHandler,
                     manure_separator: BaseSeparator) -> BaseTreatment:
        treatment_enum = TreatmentEnum.get_enum(pen.manure_storage)
        params = {
            'pen': pen,
            'manure_handler': manure_handler,
            'manure_separator': manure_separator,
            'treatment_init_data': TreatmentInitData.get_instance(treatment_enum)
        }
        enum_to_class: Dict[TreatmentEnum, Type[BaseTreatment]] = {
            treatment_enum.STORAGE_POND: StoragePond,
            treatment_enum.ANAEROBIC_LAGOON: AnaerobicLagoon,
            treatment_enum.ANAEROBIC_DIGESTION: AnaerobicDigestion,
            treatment_enum.CUSTOM_STORAGE: CustomTreatment
        }
        return enum_to_class[treatment_enum](**params)
