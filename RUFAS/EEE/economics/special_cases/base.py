"""Base class for economics preprocessing special cases.

A *special case* is a line item whose preprocessing cannot be expressed by the
generic biophysical/input/price pipeline in
:class:`~RUFAS.EEE.economics.preprocessing.EconomicPreprocessor`. Each such
line item is implemented as a :class:`SpecialCaseHandler` subclass that owns
its bespoke logic and is registered in
:mod:`RUFAS.EEE.economics.special_cases`.

Adding a new special case is a three-step operation:

1. Subclass :class:`SpecialCaseHandler`, tell it which line items it owns, and
   implement :meth:`process`. Ownership is declared by setting the
   ``section``/``name`` class attributes; a handler that owns several line
   items instead overrides :attr:`keys` to return one ``(section, name)`` pair
   per item.
2. Add the subclass to ``SPECIAL_CASE_HANDLERS`` in
   :mod:`RUFAS.EEE.economics.preprocessing`.
3. Resolve shared InputManager/OutputManager needs through ``self.context``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar

from RUFAS.EEE.economics.preprocessing_context import PreprocessingContext

if TYPE_CHECKING:
    from RUFAS.EEE.economics.preprocessing import EconomicItem


class SpecialCaseHandler(ABC):
    """Owner of the preprocessing for one or more special-case line items.

    Parameters
    ----------
    context : PreprocessingContext
        Shared services granting access to the input/output managers and the
        common data-access, pricing, scenario, and aggregation helpers.

    Attributes
    ----------
    section : str or None
        ``ECONOMIC_MAP`` section owning this line item (e.g. ``"Soil_and_crop"``).
        Used by the default :attr:`keys`.
    name : str or None
        ``ECONOMIC_MAP`` line-item name owning this special case (e.g.
        ``"Seeds costs"``). Used by the default :attr:`keys`.
    """

    section: ClassVar[str | None] = None
    name: ClassVar[str | None] = None

    def __init__(self, context: PreprocessingContext) -> None:
        self.context = context

    @property
    def keys(self) -> tuple[tuple[str, str], ...]:
        """Line items this handler owns, as ``(section, name)`` pairs.

        Defaults to the single pair built from the ``section``/``name`` class
        attributes. Handlers that own several line items override this to
        return one pair per item.
        """
        if self.section is not None and self.name is not None:
            return ((self.section, self.name),)
        return ()

    @abstractmethod
    def process(self, item: EconomicItem) -> dict[str, Any]:
        """Build the preprocessing result entry for ``item``.

        Parameters
        ----------
        item : EconomicItem
            The line item this handler matched.

        Returns
        -------
        dict
            The result entry stored under
            ``results[section][category][name]`` by the main preprocessor,
            using the same schema as the generic pipeline.
        """
        raise NotImplementedError


__all__ = ["SpecialCaseHandler"]
