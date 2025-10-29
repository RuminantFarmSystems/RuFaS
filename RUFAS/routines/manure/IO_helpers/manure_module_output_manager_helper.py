from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, Dict

from RUFAS.output_manager import OutputManager


class ManureModuleOutputManagerHelper:
    """
    A helper class that builds on the more general OutputManger for managing the output of the Manure Module.

    Attributes
    ----------
    _om : OutputManager
        An instance of the OutputManager to manage output-related operations.

    """

    _om = OutputManager()

    @classmethod
    def add_dataclass_object(
        cls,
        dataclass_object: dataclass,
        info_maps: Dict[str, Any],
        exclude_fields: list[str] | None = None,
    ) -> None:
        """
        Add the fields of a dataclass object to the output manager.

        Parameters
        ----------
        dataclass_object : dataclass
            The dataclass object whose fields are to be added.
        info_maps : dict
            Mapping information for the variables.
        exclude_fields : list[str] | None, optional
            List of field names to be excluded, by default None.

        """
        units_vars_list = list(key for (key, value) in dataclass_object.__dict__.items() if key.endswith("_unit"))

        for field in fields(dataclass_object):
            if field.name not in units_vars_list and (exclude_fields is None or field.name not in exclude_fields):
                attribute = getattr(dataclass_object, field.name)
                unit = getattr(dataclass_object, field.name + "_unit")

                cls._om.add_variable(field.name, attribute, dict(info_maps, **{"units": unit}))
