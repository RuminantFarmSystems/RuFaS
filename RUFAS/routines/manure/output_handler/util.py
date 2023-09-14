from __future__ import annotations

from dataclasses import fields

from RUFAS.output_manager import OutputManager


class ManureModuleOutputHandler:
    _om = OutputManager()

    @classmethod
    def add_dataclass_object(cls, dataclass_object, info_maps, exclude_fields: list[str] | None = None):
        for field in fields(dataclass_object):
            if exclude_fields is None or field.name not in exclude_fields:
                cls._om.add_variable(field.name, getattr(dataclass_object, field.name), info_maps)
