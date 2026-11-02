from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar, TYPE_CHECKING

from RUFAS.EEE.economics.data_processor import EconomicDataProcessor
from RUFAS.EEE.economics.mapping import EconomicLineItem, EconomicSection

if TYPE_CHECKING:
    from RUFAS.EEE.economics.preprocessing import EconomicItem


class LineItemHandler(ABC):
    """Owner of the preprocessing for a single economic line item.

    Parameters
    ----------
    context : EconomicDataProcessor
        Shared services granting access to the input/output managers and the
        common data-access, pricing, scenario, and aggregation helpers.

    Attributes
    ----------
    section : EconomicSection
        ``ECONOMIC_MAP`` section owning this line item (e.g.
        ``EconomicSection.SOIL_AND_CROP``).
    name : EconomicLineItem
        ``ECONOMIC_MAP`` line-item name owned by this handler (e.g.
        ``EconomicLineItem.SEEDS_COSTS``).
    """

    section: ClassVar[EconomicSection]
    name: ClassVar[EconomicLineItem]

    def __init__(self, context: EconomicDataProcessor) -> None:
        self.context = context

    @property
    def economic_map_keys(self) -> tuple[tuple[str, str], ...]:
        """Return the ``(section, name)`` pair this handler is keyed on."""
        if self.section is not None and self.name is not None:
            return ((self.section, self.name),)
        return ()

    @abstractmethod
    def build_preprocessing_entry(self, item: EconomicItem | None = None) -> dict[str, Any]:
        """Build the economic preprocessing result entry for this line item.

        Parameters
        ----------
        item : EconomicItem, optional
            The mapping line item being processed, for handlers that own more
            than one ``(section, name)`` key.

        Returns
        -------
        dict[str, Any]
            The result entry stored under
            ``results[section][category][name]`` by the main preprocessor,
            using the same schema as the generic pipeline.
        """
        raise NotImplementedError

    def build_preprocessing_entries(self, item: EconomicItem) -> dict[str, dict[str, Any]]:
        """Build every economic preprocessing result entry produced for a line item.

        Parameters
        ----------
        item : EconomicItem
            The mapping line item being processed.

        Returns
        -------
        dict[str, dict[str, Any]]
            Result entries keyed by the name they are stored under in
            ``results[section][category]``. By default this is the single
            entry from :meth:`build_preprocessing_entry` under ``item.name``.
        """
        return {item.name: self.build_preprocessing_entry(item)}


class ProcessorLineItemHandler(LineItemHandler):
    """Owner of a line item that is preprocessed separately for each manure processor.

    Each processor gets its own result entry, stored under
    ``"{line item name}.{processor name}"`` with the same schema as the
    generic pipeline, instead of a single entry nesting every processor.
    """

    def build_preprocessing_entry(self, item: EconomicItem | None = None) -> dict[str, Any]:
        """Not supported; per-processor line items produce one entry per processor.

        Raises
        ------
        NotImplementedError
            Always; use :meth:`build_preprocessing_entries` instead.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} builds one entry per processor; use build_preprocessing_entries"
        )

    def build_preprocessing_entries(self, item: EconomicItem) -> dict[str, dict[str, Any]]:
        """Build one economic preprocessing result entry per processor.

        Parameters
        ----------
        item : EconomicItem
            The mapping line item being processed.

        Returns
        -------
        dict[str, dict[str, Any]]
            Result entries keyed by ``"{item.name}.{processor name}"``.
        """
        return {
            f"{item.name}.{processor_name}": entry
            for processor_name, entry in self.build_processor_entries(item).items()
        }

    @abstractmethod
    def build_processor_entries(self, item: EconomicItem) -> dict[str, dict[str, Any]]:
        """Build the economic preprocessing result entry for each processor.

        Parameters
        ----------
        item : EconomicItem
            The mapping line item being processed.

        Returns
        -------
        dict[str, dict[str, Any]]
            Result entries keyed by processor name, each using the same schema
            as the generic pipeline.
        """
        raise NotImplementedError
