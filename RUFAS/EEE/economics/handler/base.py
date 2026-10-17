from abc import ABC, abstractmethod
from typing import Any, ClassVar

from RUFAS.EEE.economics.data_processor import EconomicDataProcessor
from RUFAS.EEE.economics.mapping import EconomicLineItem, EconomicSection


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
    def economic_map_key(self) -> tuple[str, str]:
        """Return the ``(section, name)`` pair this handler is keyed on."""
        return (self.section, self.name)

    @abstractmethod
    def build_preprocessing_entry(self) -> dict[str, Any]:
        """Build the economic preprocessing result entry for this line item.

        Returns
        -------
        dict[str, Any]
            The result entry stored under
            ``results[section][category][name]`` by the main preprocessor,
            using the same schema as the generic pipeline.
        """
        raise NotImplementedError
