"""Special-case preprocessing for per-digester, per-year revenue line items.

Anaerobic-digester energy products (electricity, renewable natural gas) are
emitted by the biophysical model as one daily series per digester. Revenue is
not a simple quantity times average price: each day's production must be bucketed
into its calendar year and priced at that year's commodity rate. This handler
owns the two ``Manure``/``Revenue`` line items that carry those daily series.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from RUFAS.util import Aggregator
from RUFAS.EEE.economics.fallback_values import ECONOMIC_PRICE_FALLBACK
from RUFAS.EEE.economics.special_cases.base import SpecialCaseHandler

if TYPE_CHECKING:
    from RUFAS.EEE.economics.preprocessing import EconomicItem

# Captures the digester name from a variable like
# ``Manure.Digester.energy.<digester_name>.electricity_produced_kwh``.
_DIGESTER_NAME_PATTERN = re.compile(r"energy\.(.+?)\.[^.]+$")


class DigesterRevenueHandler(SpecialCaseHandler):
    """Aggregate per-digester daily energy production into per-year revenue."""

    section = "Manure"
    # The two Manure/Revenue line items whose daily per-digester series this
    # handler prices by year.
    _NAMES = (
        "Electricity production from anaerobic digester",
        "Renewable natural gas (RNG) production",
    )

    @property
    def keys(self) -> tuple[tuple[str, str], ...]:
        """Own both digester energy-product line items under ``Manure``/``Revenue``."""
        return tuple((self.section, name) for name in self._NAMES)

    def process(self, item: EconomicItem) -> dict[str, Any]:
        """Compute revenue for a per-digester daily series priced by year.

        For each biophysical pattern (matching one variable per digester), the
        daily values are summed into calendar-year buckets using each value's
        ``simulation_day``. Every year's quantity is multiplied by that year's
        commodity price (falling back to the average price for years without an
        explicit entry), and the results are summed into the total revenue line
        item.
        """
        im = self.context.im
        om = self.context.om
        info_map = {"class": self.__class__.__name__, "function": "process"}

        start_date_str = im.get_data("config.start_date")
        end_date_str = im.get_data("config.end_date")
        start_year: int | None = None
        end_year: int | None = None
        start_date: datetime | None = None
        if start_date_str and end_date_str:
            try:
                start_year = int(str(start_date_str).split(":")[0])
                end_year = int(str(end_date_str).split(":")[0])
                start_date = datetime.strptime(str(start_date_str), "%Y:%j")
            except (ValueError, AttributeError):
                start_year = end_year = None
                start_date = None

        price_data = self.context.fetch_prices(item.economics_files)
        price_values = self.context.extract_price_values(price_data)
        price_by_year: dict[int, float] = {}
        if start_year is not None and end_year is not None:
            for offset, year in enumerate(range(start_year, end_year + 1)):
                if offset < len(price_values):
                    price_by_year[year] = price_values[offset]
        fallback_price = Aggregator.average(price_values) if price_values else None
        if fallback_price is None:
            fallback_price = ECONOMIC_PRICE_FALLBACK.get("revenue", 1.0)

        bio_values_by_digester_by_year: dict[str, dict[int, list[float]]] = {}
        bio_values_by_digester: dict[str, list[float]] = {}

        for path in item.biophysical_simulation:
            filtered_pool = om.filter_variables_pool({"filters": [path]})
            for variable_name, payload in filtered_pool.items():
                if not isinstance(payload, dict):
                    continue
                values = payload.get("values", [])
                info_maps = payload.get("info_maps", [])
                name_match = _DIGESTER_NAME_PATTERN.search(variable_name)
                digester_name = name_match.group(1) if name_match else variable_name
                if digester_name not in bio_values_by_digester:
                    bio_values_by_digester[digester_name] = []
                    bio_values_by_digester_by_year[digester_name] = {
                        year: [] for year in range(start_year, end_year + 1)
                    }
                for index, value in enumerate(values):
                    entry_info = (
                        info_maps[index] if index < len(info_maps) and isinstance(info_maps[index], dict) else {}
                    )
                    simulation_day = entry_info.get("simulation_day")
                    try:
                        numeric_value = float(value)
                    except (TypeError, ValueError):
                        continue
                    bio_values_by_digester[digester_name].append(numeric_value)
                    if simulation_day is None or start_date is None:
                        # Without a day we cannot place the value in a year; fold it into the start year.
                        year = start_year if start_year is not None else 0
                    else:
                        year = (start_date + timedelta(days=int(simulation_day))).year
                    bio_values_by_digester_by_year[digester_name][year].append(numeric_value)

        revenue_by_year: dict[str, dict[int, list[float]]] = {}
        price_data_by_day: list[float] = []
        total_revenue = 0.0
        for digester_name, year_quantities in bio_values_by_digester_by_year.items():
            if digester_name not in revenue_by_year:
                revenue_by_year[digester_name] = {}
            for year, quantity in year_quantities.items():
                if year not in revenue_by_year[digester_name]:
                    revenue_by_year[digester_name][year] = []
                price = price_by_year.get(year, fallback_price)
                year_revenue: list[float] = [daily_quantity * price for daily_quantity in quantity]
                revenue_by_year[digester_name][year] = year_revenue
                price_data_by_day.extend([price] * len(year_revenue))
                total_revenue += sum(year_revenue)

        if not bio_values_by_digester_by_year:
            om.add_warning(
                "MissingDigesterEnergyOutputs",
                f"No per-digester energy outputs matched patterns {item.biophysical_simulation} for '{item.name}'.",
                info_map,
            )

        bio_aggregate = {
            digester_name: sum(bio_values) for digester_name, bio_values in bio_values_by_digester.items()
        }
        with open(f"econ_{item.biophysical_simulation[0].split(".")[-1]}.json", "w") as f:
            output = {
                "biophysical_values": bio_values_by_digester,
                "biophysical_aggregate": bio_aggregate,
                "biophysical_values_by_scenario": {"baseline": bio_values_by_digester},
                "biophysical_aggregate_by_scenario": {"baseline": bio_aggregate},
                "price_data": price_data,
                "price_values": price_by_year,
                "price_aggregate": Aggregator.average(price_data_by_day) if price_data_by_day else None,
                "line_item_values_by_scenario": {"baseline": total_revenue},
                "revenue_by_year": revenue_by_year,
                "flow_type": "revenue",
            }
            json.dump(output, f, indent=4)
        return {
            "biophysical_values": bio_values_by_digester,
            "biophysical_aggregate": bio_aggregate,
            "biophysical_values_by_scenario": {"baseline": bio_values_by_digester},
            "biophysical_aggregate_by_scenario": {"baseline": bio_aggregate},
            "price_data": price_data,
            "price_values": price_by_year,
            "price_aggregate": Aggregator.average(price_data_by_day) if price_data_by_day else None,
            "line_item_values_by_scenario": {"baseline": total_revenue},
            "revenue_by_year": revenue_by_year,
            "flow_type": "revenue",
        }


__all__ = ["DigesterRevenueHandler"]
