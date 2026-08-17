"""Base class for economics preprocessing special cases.

A *special case* is a line item whose preprocessing cannot be expressed by the
generic biophysical/input/price pipeline in
:class:`~RUFAS.EEE.economics.preprocessing.EconomicPreprocessor`. Each such
line item is implemented as a :class:`SpecialCaseHandler` subclass that owns
its bespoke logic and is registered in
:mod:`RUFAS.EEE.economics.special_cases`.

Adding a new special case is a three-step operation:

1. Subclass :class:`SpecialCaseHandler`, set ``section`` and ``name`` to the
   :data:`~RUFAS.EEE.economics.mapping.ECONOMIC_MAP` coordinates it owns, and
   implement :meth:`process`.
2. Add the subclass to ``SPECIAL_CASE_HANDLERS`` in the package ``__init__``.
3. Resolve shared InputManager/OutputManager needs through ``self.context``.
"""
from abc import ABC, abstractmethod
from typing import Any, ClassVar

from RUFAS.EEE.economics.preprocessing_context import PreprocessingContext


class SpecialCaseHandler(ABC):
    """Owner of the preprocessing for a single special-case line item.

    Parameters
    ----------
    context : PreprocessingContext
        Shared services granting access to the input/output managers and the
        common data-access, pricing, scenario, and aggregation helpers.

    Attributes
    ----------
    section : str
        ``ECONOMIC_MAP`` section owning this line item (e.g. ``"Soil_and_crop"``).
    name : str
        ``ECONOMIC_MAP`` line-item name owning this special case (e.g.
        ``"Seeds costs"``).
    """

    section: ClassVar[str]
    name: ClassVar[str]

    def __init__(self, context: PreprocessingContext) -> None:
        self.context = context

    @property
    def key(self) -> tuple[str, str]:
        """Return the ``(section, name)`` pair this handler is keyed on."""
        return (self.section, self.name)

    @abstractmethod
    def process(self) -> dict[str, Any]:
        """Build the preprocessing result entry for this line item.

        Returns
        -------
        dict
            The result entry stored under
            ``results[section][category][name]`` by the main preprocessor,
            using the same schema as the generic pipeline.
        """
        raise NotImplementedError


__all__ = ["SpecialCaseHandler"]
