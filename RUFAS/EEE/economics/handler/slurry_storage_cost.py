from __future__ import annotations
from typing import TYPE_CHECKING, Any, ClassVar

from RUFAS.EEE.economics.fallback_values import ECONOMIC_PRICE_FALLBACK
from RUFAS.EEE.economics.handler.base import ProcessorLineItemHandler
from RUFAS.EEE.economics.mapping import EconomicSection
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.util import Aggregator

if TYPE_CHECKING:
    from RUFAS.EEE.economics.preprocessing import EconomicItem


class SlurryStorageCostHandler(ProcessorLineItemHandler):
    """Compute per-slurry-store operational costs from a ``list[dict]`` input."""

    section: ClassVar[EconomicSection] = EconomicSection.MANURE
    _SLURRY_STORAGE_PATH = "economic_inputs.Manure.slurry_storage"
    _NAMES = (
        "Slurry storage operational costs - Diesel consumption",
        "Slurry storage operational costs - Electricity consumption",
        "Slurry storage operational costs - Gasoline consumption",
        "Slurry storage operational costs - Labor hours",
        "Slurry storage operational costs - Natural gas consumption",
        "Slurry storage operational costs - Propane consumption",
        "Slurry storage operational costs - Water consumption",
    )

    @property
    def economic_map_keys(self) -> tuple[tuple[str, str], ...]:
        """Own every slurry-storage operational-cost line item under ``Manure``/``Costs``."""
        return tuple((self.section, name) for name in self._NAMES)

    def build_processor_entries(self, item: EconomicItem) -> dict[str, dict[str, Any]]:
        """Compute cost for one slurry-storage field, with one entry per slurry storage."""
        im = InputManager()
        om = OutputManager()
        info_map = {"class": self.__class__.__name__, "function": self.build_processor_entries.__name__}

        field = item.input_manager[0].rsplit(".", 1)[-1] if item.input_manager else ""

        slurry_storage_data: Any = im.get_data(self._SLURRY_STORAGE_PATH)
        if slurry_storage_data is None:
            slurry_storage_data = []
        elif not isinstance(slurry_storage_data, list):
            slurry_storage_data = [slurry_storage_data]

        price_data = self.context.fetch_prices(item.economics_files)
        price_values = self.context.extract_price_values(price_data)
        price_aggregate = Aggregator.aggregate_by_description(price_values, "average")
        if price_aggregate is None:
            price_aggregate = ECONOMIC_PRICE_FALLBACK.get("cost", 1.0)

        if not slurry_storage_data:
            om.add_warning(
                "MissingEconomicInput",
                f"No slurry storage entries found at '{self._SLURRY_STORAGE_PATH}' for '{item.name}'",
                info_map,
            )

        entries: dict[str, dict[str, Any]] = {}
        for index, processor in enumerate(slurry_storage_data):
            if not isinstance(processor, dict):
                continue
            name = processor.get("name") or f"slurry_storage_{index + 1}"
            try:
                quantity = float(processor.get(field))
            except (TypeError, ValueError):
                om.add_warning(
                    "MissingEconomicInput",
                    f"Slurry storage '{name}' has no numeric '{field}' for '{item.name}'",
                    info_map,
                )
                continue
            entries[name] = {
                "biophysical_values": [quantity],
                "biophysical_aggregate": quantity,
                "biophysical_values_by_scenario": {"baseline": [quantity]},
                "biophysical_aggregate_by_scenario": {"baseline": quantity},
                "price_data": price_data,
                "price_values": price_values,
                "price_aggregate": price_aggregate,
                "line_item_values_by_scenario": {"baseline": quantity * price_aggregate},
                "flow_type": "cost",
            }
        return entries


__all__ = ["SlurryStorageCostHandler"]
