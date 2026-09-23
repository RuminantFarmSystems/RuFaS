from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar, TYPE_CHECKING

from RUFAS.EEE.economics.data_processor import EconomicDataProcessor
if TYPE_CHECKING:
    from RUFAS.EEE.economics.preprocessing import EconomicItem


class Handler(ABC):
    """Owner of the preprocessing for a single special-case line item.

    Parameters
    ----------
    context : EconomicDataProcessor
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

    def __init__(self, context: EconomicDataProcessor) -> None:
        self.context = context

    @property
    def economic_map_keys(self) -> tuple[tuple[str, str], ...]:
        """Return the ``(section, name)`` pair this handler is keyed on."""
        if self.section is not None and self.name is not None:
            return ((self.section, self.name),)
        return ()

    @abstractmethod
    def process(self, item: EconomicItem | None = None) -> dict[str, Any]:
        """Build the preprocessing result entry for this line item.

        Returns
        -------
        dict
            The result entry stored under
            ``results[section][category][name]`` by the main preprocessor,
            using the same schema as the generic pipeline.
        """
        raise NotImplementedError


__all__ = ["Handler"]
