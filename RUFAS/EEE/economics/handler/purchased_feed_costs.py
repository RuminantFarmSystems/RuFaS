"""Special-case preprocessing for the ``Purchased feed costs`` line item.

The feed module reports ration interval purchases per feed as
``ration_interval_{rufas_id}_amount_purchased`` (kg) and
``ration_interval_{rufas_id}_cost`` ($, priced from the feed input file's
``purchased_feed_cost``). The generic pipeline cannot express this line item
because its dollar total comes from the simulation itself rather than from
commodity price files: the handler reports the purchased amounts as the
biophysical quantity, derives the per-feed prices actually paid, and uses the
purchase-amount-weighted average price so that
``biophysical_aggregate * price_aggregate == line_item_value`` holds.
"""

from __future__ import annotations

import re
from typing import Any, ClassVar

from RUFAS.util import Aggregator
from RUFAS.EEE.economics.fallback_values import ECONOMIC_QUANTITY_FALLBACK
from RUFAS.EEE.economics.handler.base import Handler


class PurchasedFeedCostHandler(Handler):
    """Owner of the preprocessing for the ``Purchased feed costs`` line item."""

    section: ClassVar[str] = "Feed_storage"
    name: ClassVar[str] = "Purchased feed costs"

    amount_patterns: ClassVar[list[str]] = ["FeedManager.purchase_feed.ration_interval_.*_amount_purchased"]
    cost_patterns: ClassVar[list[str]] = ["FeedManager.purchase_feed.ration_interval_.*_cost"]

    def process(self) -> dict[str, Any]:
        """Build the result entry from the simulation's ration interval purchase outputs."""

        values_by_scenario = self.context.fetch_values_by_scenario(self.amount_patterns, expand_interval_to_daily=True)
        if not values_by_scenario:
            values_by_scenario = {"baseline": [ECONOMIC_QUANTITY_FALLBACK]}

        biophysical_values: list[float] = []
        for scenario_values in values_by_scenario.values():
            biophysical_values.extend(scenario_values)
        aggregated_value = Aggregator.sum(biophysical_values) if biophysical_values else None
        aggregates_by_scenario = {
            scenario: Aggregator.sum(scenario_values) if scenario_values else None
            for scenario, scenario_values in values_by_scenario.items()
        }

        cost_values_by_scenario = self.context.fetch_values_by_scenario(self.cost_patterns)
        line_item_values_by_scenario = {
            scenario: Aggregator.sum(scenario_values)
            for scenario, scenario_values in cost_values_by_scenario.items()
            if scenario_values
        }

        price_values, price_aggregate = self._derive_prices()

        return {
            "biophysical_values": biophysical_values,
            "biophysical_aggregate": aggregated_value,
            "biophysical_values_by_scenario": values_by_scenario,
            "biophysical_aggregate_by_scenario": aggregates_by_scenario,
            "price_data": {},
            "price_values": price_values,
            "price_aggregate": price_aggregate,
            "line_item_values_by_scenario": line_item_values_by_scenario,
            "flow_type": "cost",
        }

    def _sum_matches_by_wildcard(self, patterns: list[str]) -> dict[str, float]:
        """Sum matched pool values per wildcard capture (the feed ID)."""

        sums: dict[str, float] = {}
        for pattern in patterns:
            capture_pattern = re.compile(f"^{pattern.replace('.*', '(.+)')}$")
            for variable_name, payload in self.context.om.filter_variables_pool({"filters": [pattern]}).items():
                capture_match = capture_pattern.fullmatch(variable_name)
                key = capture_match.group(1) if capture_match else variable_name
                values: list[float] = []
                self.context.append_from_payload(values, payload)
                sums[key] = sums.get(key, 0.0) + sum(values)
        return sums

    def _derive_prices(self) -> tuple[list[float], float | None]:
        """Derive per-feed prices and the purchase-amount-weighted average price.

        Each per-feed price is the reported cost divided by the reported amount,
        which recovers the feed input file's ``purchased_feed_cost``; the
        aggregate is total cost over total amount so scaling the purchased
        amounts by it reproduces the line item total.
        """

        amount_sums = self._sum_matches_by_wildcard(self.amount_patterns)
        cost_sums = self._sum_matches_by_wildcard(self.cost_patterns)
        price_values = [cost_sums[key] / amount_sums[key] for key in sorted(cost_sums) if amount_sums.get(key)]

        total_amount = sum(amount_sums.values())
        total_cost = sum(cost_sums.values())
        price_aggregate = total_cost / total_amount if total_amount else None
        return price_values, price_aggregate


__all__ = ["PurchasedFeedCostHandler"]
