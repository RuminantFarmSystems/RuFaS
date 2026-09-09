from __future__ import annotations
from typing import TYPE_CHECKING, Any

from RUFAS.EEE.economics.fallback_values import ECONOMIC_PRICE_FALLBACK
from RUFAS.EEE.economics.special_cases.base import SpecialCaseHandler
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager

if TYPE_CHECKING:
    from RUFAS.EEE.economics.preprocessing import EconomicItem


class SlurryStorageCostHandler(SpecialCaseHandler):
    """Compute per-slurry-store operational costs from a ``list[dict]`` input."""

    section = "Manure"
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
    def keys(self) -> tuple[tuple[str, str], ...]:
        """Own every slurry-storage operational-cost line item under ``Manure``/``Costs``."""
        return tuple((self.section, name) for name in self._NAMES)

    def process(self, item: EconomicItem) -> dict[str, Any]:
        """Compute cost for one slurry-processor field across every processor.

        The processor-specific quantity for this line item (the single
        ``slurry_storage`` field named by ``item.input_manager``) is multiplied
        by the item's commodity price, averaged across the simulation window.
        Costs are summed across processors into ``line_item_values_by_scenario`` and
        also reported per processor, keyed by each processor's ``name``, under
        ``cost_by_processor``.
        """
        im = InputManager()
        om = OutputManager()
        info_map = {"class": self.__class__.__name__, "function": "process"}

        field = item.input_manager[0].rsplit(".", 1)[-1] if item.input_manager else ""

        slurry_storage_data: Any = im.get_data(self._SLURRY_STORAGE_PATH)
        if slurry_storage_data is None:
            slurry_storage_data = []
        elif not isinstance(slurry_storage_data, list):
            slurry_storage_data = [slurry_storage_data]

        price_data = self.context.fetch_prices(item.economics_files)
        price_values = self.context.extract_price_values(price_data)
        price_aggregate = self.context.aggregate(price_values, "average")
        if price_aggregate is None:
            price_aggregate = ECONOMIC_PRICE_FALLBACK.get("cost", 1.0)

        quantity_by_processor: dict[str, list[float]] = {}
        quantity_aggregate_by_processor: dict[str, float] = {}
        cost_by_processor: dict[str, float] = {}
        total_cost = 0.0

        if not slurry_storage_data:
            om.add_warning(
                "MissingEconomicInput",
                f"No slurry storage entries found at '{self._SLURRY_STORAGE_PATH}' for '{item.name}'",
                info_map,
            )

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
            cost = quantity * price_aggregate
            quantity_by_processor[name] = [quantity]
            quantity_aggregate_by_processor[name] = quantity
            cost_by_processor[name] = cost
            total_cost += cost

        return {
            "biophysical_values": quantity_by_processor,
            "biophysical_aggregate": quantity_aggregate_by_processor,
            "biophysical_values_by_scenario": {"baseline": quantity_by_processor},
            "biophysical_aggregate_by_scenario": {"baseline": quantity_aggregate_by_processor},
            "price_data": price_data,
            "price_values": price_values,
            "price_aggregate": price_aggregate,
            "line_item_values_by_scenario": {"baseline": total_cost},
            "cost_by_processor": cost_by_processor,
            "flow_type": "cost",
        }


__all__ = ["SlurryStorageCostHandler"]
