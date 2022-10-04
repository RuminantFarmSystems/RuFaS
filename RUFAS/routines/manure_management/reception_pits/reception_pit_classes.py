from __future__ import annotations

from enum import auto
from typing import List, Optional

from RUFAS.routines.manure_management.helpers.enum_helpers import DefaultEnum
from RUFAS.routines.manure_management.manure_handlers.manure_handler_classes import \
    BaseManureHandler
from RUFAS.routines.manure_management.misc.simple_pen import SimplePen
from RUFAS.routines.manure_management.reception_pits.reception_pit_output import ReceptionPitOutput


class ReceptionPitType(DefaultEnum):
    BASE = auto()
    NULL = auto()

    DEFAULT = BASE


class BaseReceptionPit:
    def __init__(self, manure_handler: BaseManureHandler):
        self.manure_handler = manure_handler
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
    pass


class ReceptionPitFactory:
    @classmethod
    def get_instance(cls,
                     reception_pit_type_name: str,
                     manure_handler: BaseManureHandler) \
            -> BaseReceptionPit:
        reception_pit_class_by_type = {
            ReceptionPitType.BASE: BaseReceptionPit,
            ReceptionPitType.NULL: NullReceptionPit,
        }

        reception_pit_type = ReceptionPitType.get_type(reception_pit_type_name)
        reception_pit_class = reception_pit_class_by_type[reception_pit_type]
        return reception_pit_class(manure_handler)
