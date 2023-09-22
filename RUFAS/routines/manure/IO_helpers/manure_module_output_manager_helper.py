from __future__ import annotations

from dataclasses import fields, dataclass
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
        info_maps: dict,
        exclude_fields: list[str] | None = None,
    ):
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

        for field in fields(dataclass_object):
            if exclude_fields is None or field.name not in exclude_fields:
                cls._om.add_variable(
                    field.name, getattr(dataclass_object, field.name), info_maps
                )
