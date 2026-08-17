"""Special-case preprocessing for homegrown-feed revenue and cost line items.

Homegrown feed fed to animals (a cost) and homegrown crops received into storage
(a revenue) are emitted by the biophysical model as one wildcard series per RuFaS
feed ID. Each feed ID must be priced with the commodity series for its crop,
resolved from ``feed_storage_configurations`` (with a curated alias fallback for
crops lacking a dedicated price series). This handler owns both ``Feed_storage``
line items and prices each feed ID individually.

The two line items carry no ``economics_files``; the biophysical wildcard is the
only input, so when no feed outputs match the handler declines (returns ``None``)
and the generic pipeline produces the usual fallback entry.
"""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, Any

from RUFAS.EEE.economics.mapping import HOMEGROWN_FEED_PRICE_ALIASES
from RUFAS.EEE.economics.special_cases.base import SpecialCaseHandler

if TYPE_CHECKING:
    from RUFAS.EEE.economics.preprocessing import EconomicItem


class HomegrownFeedHandler(SpecialCaseHandler):
    """Price per-feed-ID homegrown feed series using the feed-storage price map."""

    section = "Feed_storage"
    # The two Feed_storage line items whose per-feed-ID wildcard series this
    # handler prices from feed_storage_configurations.
    _NAMES = (
        "Homegrown feed fed",
        "Homegrown feed received",
    )

    def __init__(self, context) -> None:
        super().__init__(context)
        # Built once from feed_storage_configurations and shared across the two
        # line items this handler owns.
        self._feed_id_to_price_file: dict[str, str] | None = None

    @property
    def keys(self) -> tuple[tuple[str, str], ...]:
        """Own both homegrown-feed line items under ``Feed_storage``."""
        return tuple((self.section, name) for name in self._NAMES)

    @property
    def feed_id_to_price_file(self) -> dict[str, str]:
        """Lazily build and cache the feed-ID → commodity-price-file-key map."""
        if self._feed_id_to_price_file is None:
            self._feed_id_to_price_file = self._build_feed_id_to_price_file_map()
        return self._feed_id_to_price_file

    def _resolve_price_file_key(self, crop_name: str) -> str | None:
        """Resolve a feed ``crop_name`` to an available commodity price file key.

        Prefers an exact ``commodity_prices_{crop_name}_dollar_per_kilogram``
        match. When a feed crop has no dedicated commodity price series, falls
        back to a curated alias (see
        :data:`~RUFAS.EEE.economics.mapping.HOMEGROWN_FEED_PRICE_ALIASES`) that
        points to the closest available proxy commodity, as agreed with the
        economics SMEs. Returns ``None`` when neither a direct match nor a valid
        alias resolves to an available InputManager key.
        """
        direct_key = f"commodity_prices_{crop_name}_dollar_per_kilogram"

        # Without metadata we cannot validate keys; preserve the direct key so
        # downstream lookups behave as before.
        if not self.context.available_input_keys:
            return direct_key

        if direct_key in self.context.available_input_keys:
            return direct_key

        alias = HOMEGROWN_FEED_PRICE_ALIASES.get(crop_name)
        if alias is not None:
            alias_key = f"commodity_prices_{alias}_dollar_per_kilogram"
            if alias_key in self.context.available_input_keys:
                return alias_key

        return None

    def _build_feed_id_to_price_file_map(self) -> dict[str, str]:
        """Build a mapping of RuFaS feed ID to commodity price file key from feed storage configs.

        Reads ``feed_storage_configurations`` from the InputManager. Each storage entry
        carries a ``rufas_id`` integer and a ``crop_name`` string. The commodity price
        file key is resolved via :meth:`_resolve_price_file_key`, which prefers an exact
        ``commodity_prices_{crop_name}_dollar_per_kilogram`` match and otherwise falls
        back to a curated alias for feeds without a dedicated price series.
        """
        info_map = {"class": self.__class__.__name__, "function": self._build_feed_id_to_price_file_map.__name__}
        feed_id_map: dict[str, str] = {}
        try:
            configs = self.context.im.get_data("feed_storage_configurations")
        except Exception:
            return feed_id_map

        if not isinstance(configs, dict):
            return feed_id_map

        for storage_type_entries in configs.values():
            if not isinstance(storage_type_entries, list):
                continue
            for entry in storage_type_entries:
                if not isinstance(entry, dict):
                    continue
                rufas_id = entry.get("rufas_id")
                crop_name = entry.get("crop_name")
                if rufas_id is None or not isinstance(crop_name, str):
                    continue
                price_file_key = self._resolve_price_file_key(crop_name)
                if price_file_key is None:
                    self.context.om.add_warning(
                        "MissingHomegrownFeedPriceMapping",
                        f"No commodity price file or alias found for feed crop '{crop_name}' "
                        f"(feed ID '{rufas_id}')",
                        info_map,
                    )
                    continue
                feed_id_map[str(rufas_id)] = price_file_key

        return feed_id_map

    def _compute_line_items_by_wildcard(
            self,
            item: EconomicItem,
            wildcard_values: list[tuple],
    ) -> dict[str, float]:
        """Compute per-wildcard-match line items using the feed config price map.

        For each captured wildcard group (i.e. a RuFaS feed ID), the method:
        1. Fetches the biophysical quantity for that specific feed ID.
        2. Resolves the commodity price CSV key from :attr:`feed_id_to_price_file`.
        3. Returns a mapping of feed ID string to ``quantity * price`` line item.
        """
        info_map = {
            "class": self.__class__.__name__,
            "function": self._compute_line_items_by_wildcard.__name__,
        }
        line_items: dict[str, float] = {}

        for groups in wildcard_values:
            if not groups:
                continue
            wildcard_value = str(groups[0])

            specific_patterns = [re.sub(r"\.\*", wildcard_value, p) for p in item.biophysical_simulation]
            quantity_values = self.context.fetch_values(specific_patterns)
            quantity = self.context.aggregate(quantity_values, item.preprocessing or "") or 0.0

            price_file_key = self.feed_id_to_price_file.get(wildcard_value)
            if not price_file_key:
                self.context.om.add_warning(
                    "MissingHomegrownFeedPriceMapping",
                    f"No commodity price file found for feed ID '{wildcard_value}' in feed storage configurations",
                    info_map,
                )
                continue

            price_data = self.context.fetch_prices([price_file_key])
            price_values = self.context.extract_price_values(price_data)
            price = self.context.aggregate(price_values, "average") or 0.0

            line_items[wildcard_value] = quantity * price

        return line_items

    def process(self, item: EconomicItem) -> dict[str, Any] | None:
        """Build the per-feed-ID line item entry, or defer to the generic pipeline.

        Returns ``None`` when no feed-ID wildcards match or none of them resolve
        to a priced quantity, so the generic pipeline can produce the usual
        fallback entry for the line item.
        """
        wildcard_values = self.context.collect_biophysical_wildcards(item.biophysical_simulation)
        if not wildcard_values:
            return None

        per_wildcard_items = self._compute_line_items_by_wildcard(item, wildcard_values)
        if not per_wildcard_items:
            return None

        total = sum(per_wildcard_items.values())
        flow_type = "revenue" if "revenue" in item.category.lower() else "cost"
        with open(f"{self.keys}.json", "w") as f:
            output = {
                "biophysical_values": list(per_wildcard_items.values()),
                "biophysical_aggregate": total,
                "biophysical_values_by_scenario": {"baseline": list(per_wildcard_items.values())},
                "biophysical_aggregate_by_scenario": {"baseline": total},
                "price_data": {},
                "price_values": [],
                "price_aggregate": None,
                "line_item_values_by_scenario": {"baseline": total},
                "per_wildcard_line_items": per_wildcard_items,
                "flow_type": flow_type,
            }
            json.dump(output, f, indent=4)
        return {
            "biophysical_values": list(per_wildcard_items.values()),
            "biophysical_aggregate": total,
            "biophysical_values_by_scenario": {"baseline": list(per_wildcard_items.values())},
            "biophysical_aggregate_by_scenario": {"baseline": total},
            "price_data": {},
            "price_values": [],
            "price_aggregate": None,
            "line_item_values_by_scenario": {"baseline": total},
            "per_wildcard_line_items": per_wildcard_items,
            "flow_type": flow_type,
        }


__all__ = ["HomegrownFeedHandler"]
