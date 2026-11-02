from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, ClassVar

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.util import Aggregator
from RUFAS.EEE.economics.fallback_values import ECONOMIC_PRICE_FALLBACK
from RUFAS.EEE.economics.handler.base import ProcessorLineItemHandler
from RUFAS.EEE.economics.mapping import EconomicSection

if TYPE_CHECKING:
    from RUFAS.EEE.economics.preprocessing import EconomicItem

_DIGESTER_NAME_PATTERN = re.compile(r"energy\.(.+?)\.[^.]+$")


class DigesterRevenueHandler(ProcessorLineItemHandler):
    """Aggregate per-digester daily energy production into per-year revenue."""

    section: ClassVar[EconomicSection] = EconomicSection.MANURE
    _NAMES = (
        "Electricity production from anaerobic digester",
        "Renewable natural gas (RNG) production",
    )

    @property
    def economic_map_keys(self) -> tuple[tuple[str, str], ...]:
        """Own both digester energy-product line items under ``Manure``/``Revenue``."""
        return tuple((self.section, name) for name in self._NAMES)

    def build_processor_entries(self, item: EconomicItem) -> dict[str, dict[str, Any]]:
        """Compute revenue for a per-digester daily series priced by year, with one entry per digester."""
        im = InputManager()
        om = OutputManager()
        info_map = {"class": self.__class__.__name__, "function": self.build_processor_entries.__name__}

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
                        year = start_year if start_year is not None else 0
                    else:
                        year = (start_date + timedelta(days=int(simulation_day))).year
                    bio_values_by_digester_by_year[digester_name][year].append(numeric_value)

        if not bio_values_by_digester_by_year:
            om.add_warning(
                "MissingDigesterEnergyOutputs",
                f"No per-digester energy outputs matched patterns {item.biophysical_simulation} for '{item.name}'.",
                info_map,
            )

        entries: dict[str, dict[str, Any]] = {}
        for digester_name, year_quantities in bio_values_by_digester_by_year.items():
            revenue_by_year: dict[int, list[float]] = {}
            price_data_by_day: list[float] = []
            for year, quantity in year_quantities.items():
                price = price_by_year.get(year, fallback_price)
                revenue_by_year[year] = [daily_quantity * price for daily_quantity in quantity]
                price_data_by_day.extend([price] * len(quantity))
            bio_values = bio_values_by_digester[digester_name]
            bio_aggregate = sum(bio_values)
            entries[digester_name] = {
                "biophysical_values": bio_values,
                "biophysical_aggregate": bio_aggregate,
                "biophysical_values_by_scenario": {"baseline": bio_values},
                "biophysical_aggregate_by_scenario": {"baseline": bio_aggregate},
                "price_data": price_data,
                "price_values": price_by_year,
                "price_aggregate": Aggregator.average(price_data_by_day) if price_data_by_day else None,
                "line_item_values_by_scenario": {
                    "baseline": sum(sum(year_revenue) for year_revenue in revenue_by_year.values())
                },
                "revenue_by_year": revenue_by_year,
                "flow_type": "revenue",
            }

        with open(f"econ_{item.biophysical_simulation[0].split(".")[-1]}.json", "w") as f:
            json.dump(entries, f, indent=4)
        return entries


__all__ = ["DigesterRevenueHandler"]
