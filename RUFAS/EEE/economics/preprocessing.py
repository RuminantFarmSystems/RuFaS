"""Preprocessing utilities for the economics module.

This module translates biophysical simulation outputs into
inputs required by the economic analysis using a hardcoded mapping
derived from ``economic_map.json`` and associated documentation.
The :class:`EconomicPreprocessor` now pulls biophysical values
from the :class:`~RUFAS.output_manager.OutputManager`, commodity
pricing from the :class:`~RUFAS.input_manager.InputManager`, and
stores the aggregated results back into the
:class:`~RUFAS.input_manager.InputManager` under the key
``economic_preprocessed``. The structure of the stored data is
validated using the ``economic_preprocessing_properties`` metadata.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Set

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.util import Aggregator
from RUFAS.EEE.economics.mapping import ECONOMIC_MAP
from RUFAS.EEE.economics.fallback_values import (
    BIOPHYSICAL_FALLBACKS,
    ECONOMIC_PRICE_FALLBACK,
    ECONOMIC_QUANTITY_FALLBACK,
    INPUT_MANAGER_FALLBACKS,
)


@dataclass(frozen=True)
class EconomicItem:
    """Definition of a single economic preprocessing item."""

    section: str
    category: str
    name: str
    biophysical_simulation: List[str]
    input_manager: List[str]
    economics_files: Any
    preprocessing: str | None


class EconomicPreprocessor:
    """Aggregate biophysical results for the economics module."""

    def __init__(
        self,
    ) -> None:
        self.im = InputManager()
        self.om = OutputManager()
        self.available_input_keys: Set[str] = self._load_available_input_keys()
        self.mapping = self._build_mapping()

    def _load_available_input_keys(self) -> Set[str]:
        """Cache the available input keys from the InputManager metadata."""

        try:
            metadata = self.im.get_metadata("files")
        except Exception:
            return set()

        if isinstance(metadata, dict):
            return set(metadata.keys())
        return set()

    def _normalize_economics_key(self, path: str) -> str:
        """Map mapping file paths to InputManager data keys."""

        candidate = path.removesuffix(".csv")

        if not self.available_input_keys:
            return candidate

        if candidate in self.available_input_keys:
            return candidate

        prefix_matches = sorted(key for key in self.available_input_keys if key.startswith(f"{candidate}."))
        if prefix_matches:
            return prefix_matches[0]

        return candidate

    def _get_data_with_handling(self, path: str, info_map: Dict[str, str]) -> Any:
        """Fetch data from the InputManager while handling invalid paths."""

        if not isinstance(path, str) or not path:
            self.om.add_warning(
                "InvalidEconomicsFilePath",
                f"Economics pricing path '{path}' is invalid",
                info_map,
            )
            return None

        candidate_paths = [path]
        normalized_path = self._normalize_economics_key(path)
        if normalized_path != path:
            candidate_paths.append(normalized_path)

        for candidate in candidate_paths:
            if candidate in INPUT_MANAGER_FALLBACKS:
                return INPUT_MANAGER_FALLBACKS[candidate]

        last_error: ValueError | None = None
        for candidate in candidate_paths:
            # Skip InputManager access entirely for wildcard paths (e.g., "*").
            # These selectors cannot be resolved to a concrete file and only
            # generate validation spam inside the InputManager. Emit a single
            # warning and continue.
            if "*" in str(candidate):
                if candidate in INPUT_MANAGER_FALLBACKS:
                    return INPUT_MANAGER_FALLBACKS[candidate]
                self.om.add_warning(
                    "MissingEconomicsFile",
                    f"Commodity pricing '{candidate}' uses wildcard and was skipped",
                    info_map,
                )
                continue

            if hasattr(self.im, "check_property_exists_in_pool"):
                # Wildcard paths are handled above. For concrete paths, perform the
                # inexpensive existence check when available to avoid repeated
                # validation warnings from deeper get_data calls.
                try:
                    if not self.im.check_property_exists_in_pool(candidate):
                        continue
                except ValueError as exc:
                    last_error = exc
                    continue
            try:
                data = self.im.get_data(candidate)
            except ValueError as exc:
                last_error = exc
                continue

            if data is not None:
                return data

        for candidate in candidate_paths:
            if candidate in INPUT_MANAGER_FALLBACKS:
                return INPUT_MANAGER_FALLBACKS[candidate]

        if last_error is not None:
            detail = (
                f"Failed to retrieve '{path}'"
                + (f" (normalized to '{normalized_path}')" if normalized_path != path else "")
                + f": {last_error}"
            )
            self.om.add_warning("InvalidEconomicsFilePath", detail, info_map)

        return None

    def _build_mapping(self) -> List[EconomicItem]:
        """Convert the hardcoded mapping into structured entries."""

        items: List[EconomicItem] = []
        for section, categories in ECONOMIC_MAP.items():
            if not isinstance(categories, dict):
                continue
            for category, entries in categories.items():
                if not isinstance(entries, dict):
                    continue
                for name, details in entries.items():
                    if not isinstance(details, dict):
                        continue
                    biophysical_simulation = details.get("biophysical_simulation") or []
                    input_manager = details.get("input_manager") or []
                    preprocessing = details.get("preprocessing")
                    economics_files = details.get("economics_files")
                    if not biophysical_simulation and not input_manager and not economics_files:
                        continue
                    if isinstance(biophysical_simulation, str):
                        biophysical_simulation = [biophysical_simulation]
                    if isinstance(input_manager, str):
                        input_manager = [input_manager]
                    items.append(
                        EconomicItem(
                            section=section,
                            category=category,
                            name=name,
                            biophysical_simulation=list(biophysical_simulation),
                            input_manager=list(input_manager),
                            economics_files=economics_files,
                            preprocessing=preprocessing,
                        )
                    )
        return items

    def _append_numeric(self, container: List[float], value: Any) -> None:
        """Append numeric value to container if possible."""
        try:
            container.append(float(value))
        except (TypeError, ValueError):
            pass

    def _append_from_payload(self, container: List[float], payload: Any) -> None:
        """Append numeric values from an OutputManager payload."""

        if isinstance(payload, dict) and "values" in payload:
            for value in payload.get("values", []):
                self._append_from_payload(container, value)
            return
        if isinstance(payload, dict):
            for value in payload.values():
                self._append_from_payload(container, value)
            return
        if isinstance(payload, (list, tuple)):
            for value in payload:
                self._append_from_payload(container, value)
            return
        self._append_numeric(container, payload)

    def _fetch_values(self, sim_paths: Iterable[str]) -> List[float]:
        """Collect values from the OutputManager for the provided patterns."""

        values: List[float] = []
        info_map = {"class": self.__class__.__name__, "function": self._fetch_values.__name__}
        flat_pool = self.om._get_flat_variables_pool()
        for path in sim_paths:
            pattern = re.compile(path)
            matched = False
            for variable_name, payload in flat_pool.items():
                if pattern.search(variable_name):
                    matched = True
                    self._append_from_payload(values, payload)
            if not matched:
                fallback_values = BIOPHYSICAL_FALLBACKS.get(path)
                if fallback_values:
                    values.extend(fallback_values)
                else:
                    self.om.add_warning(
                        "MissingBiophysicalData",
                        f"No biophysical outputs matched pattern '{path}'",
                        info_map,
                    )
        return values

    def _fetch_values_by_scenario(self, sim_paths: Iterable[str]) -> Dict[str, List[float]]:
        """Collect values per scenario from the OutputManager."""

        flat_pool = self.om._get_flat_variables_pool()
        if not flat_pool:
            fallback_values = self._fallback_values_by_scenario(sim_paths)
            return fallback_values

        scenario_names: List[str] = []
        pool = getattr(self.om, "variables_pool", {})
        if isinstance(pool, dict) and pool:
            if all(isinstance(value, dict) and "values" in value for value in pool.values()):
                scenario_names = ["baseline"]
            else:
                scenario_names = [name for name, data in pool.items() if isinstance(data, dict) and data]
        if not scenario_names:
            scenario_names = ["baseline"]

        values_by_scenario: Dict[str, List[float]] = {scenario: [] for scenario in scenario_names}
        info_map = {"class": self.__class__.__name__, "function": self._fetch_values_by_scenario.__name__}

        for path in sim_paths:
            pattern = re.compile(path)
            matched = False
            for variable_name, payload in flat_pool.items():
                if not pattern.search(variable_name):
                    continue
                matched = True
                if scenario_names == ["baseline"]:
                    scenario_key = "baseline"
                else:
                    scenario_key = variable_name.split(".", 1)[0]
                    if scenario_key not in values_by_scenario:
                        scenario_key = "baseline"
                        values_by_scenario.setdefault(scenario_key, [])
                self._append_from_payload(values_by_scenario[scenario_key], payload)
            if not matched:
                fallback_values = BIOPHYSICAL_FALLBACKS.get(path)
                if fallback_values:
                    scenario_key = scenario_names[0] if scenario_names else "baseline"
                    values_by_scenario.setdefault(scenario_key, [])
                    values_by_scenario[scenario_key].extend(fallback_values)
                else:
                    self.om.add_warning(
                        "MissingBiophysicalData",
                        f"No biophysical outputs matched pattern '{path}'",
                        info_map,
                    )
        return values_by_scenario

    def _fallback_values_by_scenario(self, sim_paths: Iterable[str]) -> Dict[str, List[float]]:
        """Build fallback values when no OutputManager data is available."""

        values_by_scenario: Dict[str, List[float]] = {"baseline": []}
        for path in sim_paths:
            fallback_values = BIOPHYSICAL_FALLBACKS.get(path)
            if fallback_values:
                values_by_scenario["baseline"].extend(fallback_values)

        if values_by_scenario["baseline"]:
            return values_by_scenario
        return {}

    def _fetch_input_values(self, input_paths: Iterable[str]) -> List[float]:
        """Collect values from the InputManager for the provided paths."""

        values: List[float] = []
        info_map = {"class": self.__class__.__name__, "function": self._fetch_input_values.__name__}
        for path in input_paths:
            data = self.im.get_data(path)
            if data is None:
                self.om.add_warning(
                    "MissingEconomicInput",
                    f"No economic input found at '{path}'",
                    info_map,
                )
                continue
            self._append_from_payload(values, data)
        return values

    def _extract_price_values(self, price_data: Any) -> List[float]:
        """Extract numeric price values from pricing payloads."""

        start_year: int = int(self.im.get_data("config.start_date").split(":")[0])
        end_year: int = int(self.im.get_data("config.end_date").split(":")[0])
        fips_code: int = self.im.get_data("config.FIPS_county_code")
        values: List[float] = []
        for key, value in price_data.items():
            if not isinstance(value, dict) or "fips" not in value or not isinstance(value["fips"], list):
                print(f"Warning: Price data for '{key}' is not in expected format; skipping price extraction.")
                continue
                # TODO: We are hitting this condition because some of the commodity prices for certain years are not available in the csv files.
            fips_idx = value["fips"].index(fips_code)
            for year in range(start_year, end_year + 1):
                try:
                    price = value[f"{year}"][fips_idx]
                    values.append(price)
                except (KeyError, IndexError):
                    self.om.add_warning(
                        "MissingPriceData",
                        f"Price data missing for year '{year}' and FIPS '{fips_code}' in '{key}'",
                        {"class": self.__class__.__name__, "function": self._extract_price_values.__name__},
                    )
                    continue
        return values

    def _infer_flow_type(self, item: EconomicItem) -> str | None:
        """Infer if an item is a revenue or cost based on naming conventions."""

        category = item.category.lower()
        if "revenue" in category:
            return "revenue"
        if "cost" in category:
            return "cost"

        haystack = " ".join([item.name, *item.biophysical_simulation, *item.input_manager]).lower()
        if "_products" in haystack:
            return "revenue"
        if "_inputs" in haystack:
            return "cost"
        return None

    def _fetch_prices(self, economics_files: Any) -> Dict[str, Any]:
        """Collect commodity pricing using the InputManager."""

        prices: Dict[str, Any] = {}
        info_map = {"class": self.__class__.__name__, "function": self._fetch_prices.__name__}
        fallback_map = {
            "commodity_prices.bedding_manure_solids.dollar_per_head": "economic_inputs.Manure.manure_disposal_price_per_kg",
        }

        if economics_files is None:
            return prices

        if isinstance(economics_files, list):
            for file_key in economics_files:
                price_data = self._get_data_with_handling(file_key, info_map)
                if price_data is None:
                    fallback_key = fallback_map.get(file_key)
                    if fallback_key:
                        price_data = self._get_data_with_handling(fallback_key, info_map)
                        if price_data is not None:
                            prices[file_key] = price_data
                            self.om.add_warning(
                                "MissingEconomicsFileFallback",
                                f"Commodity pricing '{file_key}' not found; used '{fallback_key}' instead.",
                                info_map,
                            )
                            continue
                    self.om.add_warning(
                        "MissingEconomicsFile",
                        f"Commodity pricing '{file_key}' not found in InputManager",
                        info_map,
                    )
                    continue
                prices[file_key] = price_data
            return prices

        if not isinstance(economics_files, dict):
            return prices

        selector_path = economics_files.get("input_manager_location")
        if selector_path:
            selection = self._get_data_with_handling(selector_path, info_map)
            if selection is None:
                self.om.add_warning(
                    "MissingSelection",
                    f"Selector value not found at '{selector_path}'",
                    info_map,
                )
                for option, file_key in economics_files.items():
                    if option == "input_manager_location":
                        continue
                    if not isinstance(file_key, str):
                        continue
                    price_data = self._get_data_with_handling(file_key, info_map)
                    if price_data is not None:
                        prices[file_key] = price_data
                if prices:
                    self.om.add_warning(
                        "MissingSelectionFallback",
                        f"No selector match; using all available pricing options for '{selector_path}'.",
                        info_map,
                    )
                return prices
            selection_key = str(selection).lower()
            selected_file = None
            for option, file_key in economics_files.items():
                if option == "input_manager_location":
                    continue
                if option.lower() == selection_key:
                    selected_file = file_key
                    break
            if selected_file is None:
                self.om.add_warning(
                    "UnknownSelection",
                    f"No price file matched selection '{selection}' at '{selector_path}'",
                    info_map,
                )
                for option, file_key in economics_files.items():
                    if option == "input_manager_location":
                        continue
                    if not isinstance(file_key, str):
                        continue
                    price_data = self._get_data_with_handling(file_key, info_map)
                    if price_data is not None:
                        prices[file_key] = price_data
                if prices:
                    self.om.add_warning(
                        "UnknownSelectionFallback",
                        f"No matching selection; using all available pricing options for '{selector_path}'.",
                        info_map,
                    )
                return prices
            price_data = self._get_data_with_handling(selected_file, info_map)
            if price_data is None:
                self.om.add_warning(
                    "MissingEconomicsFile",
                    f"Commodity pricing '{selected_file}' not found in InputManager",
                    info_map,
                )
                return prices
            prices[selected_file] = price_data
            return prices

        for label, file_key in economics_files.items():
            if not isinstance(file_key, str):
                continue
            price_data = self._get_data_with_handling(file_key, info_map)
            if price_data is None:
                self.om.add_warning(
                    "MissingEconomicsFile",
                    f"Commodity pricing '{file_key}' not found in InputManager",
                    info_map,
                )
                continue
            prices[label] = price_data
        return prices

    def _aggregate(self, values: List[float], desc: str) -> float | None:
        """Aggregate values according to a textual description."""
        if not values:
            return None
        d = desc.lower() if isinstance(desc, str) else ""
        if "average" in d or "mean" in d:
            return Aggregator.average(values)
        if "product" in d:
            return Aggregator.product(values)
        if "divide" in d or "ratio" in d:
            result = Aggregator.division(values)
            if result is not None:
                return result
        if "subtract" in d or "difference" in d:
            result = Aggregator.subtraction(values)
            if result is not None:
                return result
        if "standard deviation" in d or "std" in d:
            return Aggregator.standard_deviation(values)
        # Default aggregation is sum
        return Aggregator.sum(values)

    def preprocess(self) -> Dict[str, Dict[str, Dict[str, Dict[str, Any]]]]:
        """Run preprocessing and store results in the InputManager."""

        results: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {}
        info_map = {"class": self.__class__.__name__, "function": self.preprocess.__name__}

        for item in self.mapping:
            section_data = results.setdefault(item.section, {})
            category_data = section_data.setdefault(item.category, {})

            values_by_scenario = self._fetch_values_by_scenario(item.biophysical_simulation)
            input_values = self._fetch_input_values(item.input_manager)

            if values_by_scenario:
                for scenario, biophysical_values in values_by_scenario.items():
                    if not biophysical_values and input_values:
                        values_by_scenario[scenario] = list(input_values)
            elif input_values:
                values_by_scenario = {"baseline": list(input_values)}
            else:
                values_by_scenario = {"baseline": [ECONOMIC_QUANTITY_FALLBACK]}

            biophysical_values: List[float] = []
            for scenario_values in values_by_scenario.values():
                biophysical_values.extend(scenario_values)

            aggregated_value = self._aggregate(biophysical_values, item.preprocessing or "")
            if aggregated_value is None and biophysical_values:
                aggregated_value = Aggregator.sum(biophysical_values)
            if not biophysical_values and not input_values:
                self.om.add_warning(
                    "MissingBiophysicalData",
                    "No values found for "
                    f"'{item.name}' using patterns {item.biophysical_simulation} "
                    f"and input paths {item.input_manager}",
                    info_map,
                )

            price_data = self._fetch_prices(item.economics_files)
            if item.economics_files and not price_data:
                self.om.add_warning(
                    "MissingEconomicsFile",
                    f"No commodity pricing retrieved for '{item.name}'",
                    info_map,
                )

            price_values = self._extract_price_values(price_data)
            price_aggregate = self._aggregate(price_values, "average")
            if price_aggregate is None:
                flow_type = self._infer_flow_type(item) or "cost"
                if flow_type in ECONOMIC_PRICE_FALLBACK:
                    price_aggregate = ECONOMIC_PRICE_FALLBACK[flow_type]
            aggregates_by_scenario: Dict[str, float | None] = {}
            for scenario, scenario_values in values_by_scenario.items():
                scenario_aggregate = self._aggregate(scenario_values, item.preprocessing or "")
                if scenario_aggregate is None and scenario_values:
                    scenario_aggregate = Aggregator.sum(scenario_values)
                aggregates_by_scenario[scenario] = scenario_aggregate
            line_item_values_by_scenario: Dict[str, float] = {}
            if price_aggregate is not None:
                for scenario, aggregate_value in aggregates_by_scenario.items():
                    if aggregate_value is None:
                        continue
                    line_item_values_by_scenario[scenario] = aggregate_value * price_aggregate
            else:
                for scenario, aggregate_value in aggregates_by_scenario.items():
                    if aggregate_value is None:
                        continue
                    line_item_values_by_scenario[scenario] = aggregate_value
                if line_item_values_by_scenario:
                    self.om.add_warning(
                        "MissingPriceForLineItem",
                        f"No price found for '{item.name}'. Using aggregated values as totals.",
                        info_map,
                    )
            if not line_item_values_by_scenario and aggregated_value is not None:
                fallback_flow_type = self._infer_flow_type(item) or "cost"
                fallback_price = ECONOMIC_PRICE_FALLBACK.get(fallback_flow_type, 1.0)
                line_item_values_by_scenario["baseline"] = aggregated_value * fallback_price

            flow_type = self._infer_flow_type(item) or "cost"
            category_data[item.name] = {
                "biophysical_values": biophysical_values,
                "biophysical_aggregate": aggregated_value,
                "biophysical_values_by_scenario": values_by_scenario,
                "biophysical_aggregate_by_scenario": aggregates_by_scenario,
                "price_data": price_data,
                "price_values": price_values,
                "price_aggregate": price_aggregate,
                "line_item_values_by_scenario": line_item_values_by_scenario,
                "flow_type": flow_type,
            }

        # Store aggregated results back into the InputManager
        self.im.add_runtime_variable_to_pool(
            variable_name="economic_preprocessed",
            data=results,
            properties_blob_key="economic_preprocessing_properties",
            eager_termination=False,
        )
        self.om.add_log(
            "Economic preprocessing",
            "Economic preprocessing completed",
            info_map,
        )
        return results


__all__ = ["EconomicPreprocessor"]
