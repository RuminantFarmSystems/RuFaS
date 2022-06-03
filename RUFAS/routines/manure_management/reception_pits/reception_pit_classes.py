from __future__ import annotations

from enum import auto
from typing import List, Optional

from RUFAS.routines.manure_management.helpers.enum_helpers import ExtendedEnum
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes import \
    BaseManureHandler
from RUFAS.routines.manure_management.reception_pits.reception_pit_output import ReceptionPitOutput


class ReceptionPitEnum(ExtendedEnum):
    BASE = auto()
    NULL = auto()

    DEFAULT = BASE


class BaseReceptionPit:
    def __init__(self, manure_handler: BaseManureHandler):
        self.manure_handler = manure_handler
        self.daily_vars = ReceptionPitOutput()
        self.all_output: List[ReceptionPitOutput] = []

    @property
    def last_output(self) -> Optional[ReceptionPitOutput]:
        return self.all_output[-1] if len(self.all_output) > 0 else None

    def reset_daily_variables(self):
        pass

    def update(self) -> ReceptionPitOutput:
        daily_output = ReceptionPitOutput.get_instance(self.manure_handler.last_output)
        self.all_output.append(daily_output)
        return daily_output


class NullReceptionPit(BaseReceptionPit):
    def __init__(self, manure_handler: BaseManureHandler):
        super().__init__(manure_handler)


class ReceptionPitFactory:
    @classmethod
    def get_instance(cls, manure_handler: BaseManureHandler) -> BaseReceptionPit:
        params = {
            'manure_handler': manure_handler
        }
        return BaseReceptionPit(**params)
