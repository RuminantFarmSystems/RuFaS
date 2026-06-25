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

import math
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Set

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.general_constants import GeneralConstants
from RUFAS.util import Aggregator, Utility
from RUFAS.EEE.economics.mapping import ECONOMIC_MAP
from RUFAS.EEE.economics.fallback_values import (
    BIOPHYSICAL_FALLBACKS,
    ECONOMIC_PRICE_FALLBACK,
    ECONOMIC_QUANTITY_FALLBACK,
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
    match_source: str | None
    wildcard_value_map: Dict[str, str] | None
    preprocessing: str | None
    dedicated_processor: str | None = None
    bedding_type_to_file_key: Dict[str, str] | None = None
    bedding_configs_path: str | None = None


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

        last_error: ValueError | None = None
        for candidate in candidate_paths:
            # Skip InputManager access entirely for wildcard paths (e.g., "*").
            # These selectors cannot be resolved to a concrete file and only
            # generate validation spam inside the InputManager. Emit a single
            # warning and continue.
            if "*" in str(candidate):
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
                    match_source = details.get("match_source")
                    wildcard_value_map = details.get("wildcard_value_map")
                    dedicated_processor = details.get("dedicated_processor")
                    bedding_type_to_file_key = details.get("bedding_type_to_file_key")
                    bedding_configs_path = details.get("bedding_configs_path")
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
                            match_source=match_source,
                            wildcard_value_map=wildcard_value_map if isinstance(wildcard_value_map, dict) else None,
                            preprocessing=preprocessing,
                            dedicated_processor=dedicated_processor,
                            bedding_type_to_file_key=(
                                bedding_type_to_file_key if isinstance(bedding_type_to_file_key, dict) else None
                            ),
                            bedding_configs_path=bedding_configs_path,
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
        for path in sim_paths:
            filtered_pool = self.om.filter_variables_pool({"filters": [path]})
            matched = False
            for payload in filtered_pool.values():
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

        filtered_by_path: Dict[str, Dict[str, Any]] = {
            path: self.om.filter_variables_pool({"filters": [path]}) for path in sim_paths
        }
        if not any(filtered_by_path.values()):
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
            matched = False
            for variable_name, payload in filtered_by_path.get(path, {}).items():
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

    def _collect_biophysical_wildcards(self, sim_paths: Iterable[str]) -> List[tuple[str, ...]]:
        """Collect wildcard values from matched biophysical variable names."""

        captures: List[tuple[str, ...]] = []
        seen: Set[tuple[str, ...]] = set()

        for path in sim_paths:
            capture_pattern = re.compile(f"^{path.replace('.*', '(.+)')}$")
            filtered_pool = self.om.filter_variables_pool({"filters": [path]})
            for variable_name in filtered_pool:
                capture_match = capture_pattern.fullmatch(variable_name)
                if capture_match is None:
                    continue
                groups = capture_match.groups()
                groups = tuple(group for group in groups if group != "")
                if not groups:
                    continue
                if groups in seen:
                    continue
                seen.add(groups)
                captures.append(groups)

        return captures

    def _expand_input_path_with_wildcards(
        self,
        path: str,
        wildcard_values: Iterable[tuple[str, ...]],
        wildcard_value_map: Dict[str, str] | None = None,
    ) -> List[str]:
        """Expand InputManager wildcard paths using biophysical wildcard matches."""

        if "*" not in path:
            return [path]

        expanded_paths: List[str] = []
        seen: Set[str] = set()
        wildcard_count = path.count("*")

        for groups in wildcard_values:
            if len(groups) < wildcard_count:
                continue

            replacement_values = groups[:wildcard_count]
            expanded = path
            for replacement in replacement_values:
                mapped_replacement = (
                    wildcard_value_map.get(replacement, replacement) if wildcard_value_map else replacement
                )
                expanded = expanded.replace("*", mapped_replacement, 1)

            if expanded in seen:
                continue
            seen.add(expanded)
            expanded_paths.append(expanded)

        return expanded_paths

    def _fetch_input_values(
        self,
        input_paths: Iterable[str],
        biophysical_wildcards: Iterable[tuple[str, ...]] | None = None,
        wildcard_value_map: Dict[str, str] | None = None,
    ) -> tuple[List[float], List[str]]:
        """Collect values from the InputManager for the provided paths."""

        values: List[float] = []
        exact_match_values: List[str] = []
        info_map = {"class": self.__class__.__name__, "function": self._fetch_input_values.__name__}
        wildcard_values = list(biophysical_wildcards or [])

        for path in input_paths:
            candidate_paths = [path]
            if "*" in path:
                expanded_paths = self._expand_input_path_with_wildcards(path, wildcard_values, wildcard_value_map)
                if expanded_paths:
                    candidate_paths = expanded_paths
                else:
                    self.om.add_warning(
                        "MissingEconomicInputWildcard",
                        f"Could not expand wildcard path '{path}' from biophysical matches",
                        info_map,
                    )
                    continue

            for candidate_path in candidate_paths:
                data = self.im.get_data(candidate_path)
                if data is None:
                    self.om.add_warning(
                        "MissingEconomicInput",
                        f"No economic input found at '{candidate_path}'",
                        info_map,
                    )
                    continue
                if isinstance(data, str):
                    exact_match_values.append(data)
                elif isinstance(data, (list, tuple, set)):
                    for value in data:
                        if isinstance(value, str):
                            exact_match_values.append(value)
                self._append_from_payload(values, data)
        return values, exact_match_values

    def _extract_price_values(self, price_data: Any) -> List[float]:
        """Extract numeric price values from pricing payloads."""

        info_map = {"class": self.__class__.__name__, "function": self._extract_price_values.__name__}
        start_year: int = int(self.im.get_data("config.start_date").split(":")[0])
        end_year: int = int(self.im.get_data("config.end_date").split(":")[0])
        fips_code: int = self.im.get_data("config.FIPS_county_code")
        values: List[float] = []
        for key, value in price_data.items():
            if not isinstance(value, dict) or "fips" not in value or not isinstance(value["fips"], list):
                self.om.add_warning(
                    "MissingPriceData",
                    f"Price data missing for key: {key}, FIPS: '{fips_code}' is not in expected format."
                    "Using fallback price.",
                    info_map,
                )
                values.extend(self._get_fallback_price(start_year, end_year, key))
                continue
            fips_idx = value["fips"].index(fips_code)
            for year in range(start_year, end_year + 1):
                try:
                    price = value[f"{year}"][fips_idx]
                    values.append(price)
                except (KeyError, IndexError):
                    self.om.add_warning(
                        "MissingPriceData",
                        f"Price data missing for year '{year}' and FIPS '{fips_code}' in '{key}'."
                        "Using fallback price.",
                        info_map,
                    )
                    values.extend(self._get_fallback_price(start_year, end_year, key))
                    continue
        return values

    def _get_fallback_price(self, start_year: int, end_year: int, commodity: str) -> List[float]:
        """Get a fallback price for a commodity."""
        info_map = {"class": self.__class__.__name__, "function": self._get_fallback_price.__name__}
        defaults: Dict[str, List[float | str]] = self.im.get_data("_default_values")
        defaults_fallback: Dict[str, List[float | str]] = self.im.get_data("_default_fallback_values")
        if commodity not in defaults["commodity"] and commodity not in defaults_fallback["commodity"]:
            self.om.add_warning(
                "MissingFallbackPrice",
                f"No fallback price found for commodity: {commodity}",
                info_map,
            )
            return [ECONOMIC_PRICE_FALLBACK.get("cost", 1.0)] * (end_year - start_year + 1)
        commodity_idx = defaults["commodity"].index(commodity)
        values: List[float] = []
        use_fallback = False
        for year in range(start_year, end_year + 1):
            price = defaults[f"{year}"][commodity_idx]
            if math.isnan(price):
                use_fallback = True
                break
            values.append(price)
        if use_fallback:
            commodity_idx = defaults_fallback["commodity"].index(commodity)
            values = []
            for year in range(start_year, end_year + 1):
                price = defaults_fallback[f"{year}"][commodity_idx]
                if math.isnan(price):
                    self.om.add_warning(
                        "MissingFallbackPrice",
                        f"No fallback price found for commodity: {commodity} in year: {year}",
                        info_map,
                    )
                    price = ECONOMIC_PRICE_FALLBACK.get("cost", 1.0)
                values.append(price)
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

        if economics_files is None:
            return prices

        if isinstance(economics_files, list):
            for file_key in economics_files:
                price_data = self._get_data_with_handling(file_key, info_map)
                if price_data is None:
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

    def _extract_selector_values(self, selection: Any) -> List[str]:
        """Normalize selector values into lowercase keys."""

        if selection is None:
            return []
        if isinstance(selection, dict):
            values = list(selection.keys())
        elif isinstance(selection, (list, tuple, set)):
            values = list(selection)
        else:
            values = [selection]
        return [str(value).lower() for value in values]

    def _fetch_prices_with_exact_matches(
        self,
        economics_files: Any,
        match_source: str | None = None,
        input_match_values: Iterable[str] | None = None,
        biophysical_match_values: Iterable[str] | None = None,
    ) -> Dict[str, Any]:
        """Collect pricing by exact key match against mapping options when requested."""

        if not isinstance(economics_files, dict):
            return self._fetch_prices(economics_files)

        source = str(match_source or "").lower()
        if source not in {"input_manager", "biophysical_simulation"}:
            return self._fetch_prices(economics_files)

        requested_values = (
            list(input_match_values or []) if source == "input_manager" else list(biophysical_match_values or [])
        )
        requested = {str(value).lower() for value in requested_values if str(value).strip()}
        if not requested:
            return self._fetch_prices(economics_files)

        info_map = {"class": self.__class__.__name__, "function": self._fetch_prices_with_exact_matches.__name__}
        prices: Dict[str, Any] = {}
        for option, file_key in economics_files.items():
            if option in {"input_manager_location", "biophysical_simulation_location"}:
                continue
            if str(option).lower() not in requested or not isinstance(file_key, str):
                continue
            price_data = self._get_data_with_handling(file_key, info_map)
            if price_data is not None:
                prices[option] = price_data
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

    # ------------------------------------------------------------------
    # Bedding (issue #3088): per-pen, per-year cost handled separately
    # because the generic engine lumps every pen into one average and
    # cannot pair a pen's animal count with that pen's bedding price.
    # ------------------------------------------------------------------

    def _bedding_type_value(self, raw: Any) -> Any:
        """Return a bedding type as a plain value (handles enum-like objects)."""

        return getattr(raw, "value", raw)

    def _build_bedding_name_to_type(self, item: EconomicItem) -> Dict[str, Any]:
        """Map each bedding config ``name`` to its canonical ``bedding_type``."""

        path = item.bedding_configs_path or "animal.bedding_configs"
        configs = self.im.get_data(path)
        name_to_type: Dict[str, Any] = {}
        if isinstance(configs, (list, tuple)):
            for config in configs:
                if isinstance(config, dict) and "name" in config:
                    name_to_type[str(config["name"])] = self._bedding_type_value(config.get("bedding_type"))
        return name_to_type

    def _simulation_start(self) -> tuple[int, datetime]:
        """Return the simulation start year and start date (``YYYY:day_of_year``)."""

        raw = self.im.get_data("config.start_date")
        parts = str(raw).split(":")
        year = int(parts[0])
        day_of_year = int(parts[1]) if len(parts) > 1 and str(parts[1]).strip() else 1
        start_date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
        return year, start_date

    def _payload_series(self, payload: Any) -> tuple[List[float], List[Any]]:
        """Extract aligned daily values and their info maps from a pen payload."""

        if isinstance(payload, dict) and "values" in payload:
            raw_values = payload.get("values", [])
            raw_info_maps = payload.get("info_maps", [])
        elif isinstance(payload, (list, tuple)):
            raw_values, raw_info_maps = list(payload), []
        else:
            raw_values, raw_info_maps = [payload], []

        values: List[float] = []
        info_maps: List[Any] = []
        for index, value in enumerate(raw_values):
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                continue
            values.append(numeric)
            info_maps.append(raw_info_maps[index] if index < len(raw_info_maps) else {})
        return values, info_maps

    def _collect_pen_series(self, sim_paths: Iterable[str]) -> Dict[str, Dict[str, Dict[str, List[Any]]]]:
        """Collect per-pen daily head counts (with info maps), grouped by scenario.

        Returns ``{scenario: {pen_capture: {"values": [...], "info_maps": [...]}}}``
        where ``pen_capture`` is the regex match for ``.*`` (e.g. ``"0_CALF"``).
        """

        pool = getattr(self.om, "variables_pool", {})
        baseline_mode = True
        scenario_names: Set[str] = set()
        if isinstance(pool, dict) and pool:
            baseline_mode = all(isinstance(value, dict) and "values" in value for value in pool.values())
            if not baseline_mode:
                scenario_names = {name for name, data in pool.items() if isinstance(data, dict) and data}

        series: Dict[str, Dict[str, Dict[str, List[Any]]]] = {}
        for path in sim_paths:
            capture_pattern = re.compile(path.replace(".*", "(.+?)") + "$")
            filtered_pool = self.om.filter_variables_pool({"filters": [path]})
            for variable_name, payload in filtered_pool.items():
                match = capture_pattern.search(variable_name)
                if match is None:
                    continue
                groups = [group for group in match.groups() if group]
                if not groups:
                    continue
                capture = groups[0]
                if baseline_mode:
                    scenario = "baseline"
                else:
                    # Mirror the generic engine: only accept a discovered scenario
                    # name, otherwise fall back to "baseline".
                    candidate = variable_name.split(".", 1)[0]
                    scenario = candidate if candidate in scenario_names else "baseline"
                values, info_maps = self._payload_series(payload)
                bucket = series.setdefault(scenario, {}).setdefault(capture, {"values": [], "info_maps": []})
                bucket["values"].extend(values)
                bucket["info_maps"].extend(info_maps)
        return series

    def _bedding_counts_by_year(
        self, values: List[float], info_maps: List[Any], start_date: datetime
    ) -> Dict[int, List[float]]:
        """Group daily head counts by calendar year using ``simulation_day``.

        ``simulation_day`` is 0-indexed (``(current_date - start_date).days``), so
        the calendar date is ``start_date + simulation_day`` with no offset. When a
        day lacks a recorded ``simulation_day`` the positional (0-indexed) order is
        used as a fallback.
        """

        counts_by_year: Dict[int, List[float]] = defaultdict(list)
        for index, value in enumerate(values):
            sim_day = None
            if index < len(info_maps) and isinstance(info_maps[index], dict):
                sim_day = info_maps[index].get("simulation_day")
            if sim_day is None:
                sim_day = index
            calendar_date = start_date + timedelta(days=int(sim_day))
            counts_by_year[calendar_date.year].append(value)
        return counts_by_year

    def _annual_bedding_price(
        self,
        price_dict: Any,
        year: int,
        fips: Any,
        file_key: str,
        warned_years: Set[str],
        info_map: Dict[str, str],
    ) -> float:
        """Look up a ``dollar_per_head`` price for ``year`` at the simulation FIPS.

        The bedding price files currently carry only a single year column, so a
        requested year with no column falls back to the nearest available year.
        """

        fallback = ECONOMIC_PRICE_FALLBACK.get("cost", 1.0)
        if not isinstance(price_dict, dict) or not isinstance(price_dict.get("fips"), list):
            warn_key = f"{file_key}:malformed"
            if warn_key not in warned_years:
                warned_years.add(warn_key)
                self.om.add_warning(
                    "MissingPriceData",
                    f"Bedding price data for '{file_key}' is missing or malformed; using fallback cost ${fallback}/head.",
                    info_map,
                )
            return fallback
        try:
            fips_idx = price_dict["fips"].index(fips)
        except ValueError:
            warn_key = f"{file_key}:fips:{fips}"
            if warn_key not in warned_years:
                warned_years.add(warn_key)
                self.om.add_warning(
                    "MissingPriceData",
                    f"FIPS county '{fips}' not found in bedding price file '{file_key}'; "
                    f"using fallback cost ${fallback}/head.",
                    info_map,
                )
            return fallback

        year_columns = sorted(int(key) for key in price_dict if str(key).isdigit())
        if not year_columns:
            return fallback

        use_year = year if year in year_columns else min(year_columns, key=lambda candidate: abs(candidate - year))
        if use_year != year:
            warn_key = f"{file_key}:{year}"
            if warn_key not in warned_years:
                warned_years.add(warn_key)
                self.om.add_warning(
                    "MissingPriceYear",
                    f"No bedding price column for year {year} in '{file_key}'; using nearest year {use_year}.",
                    info_map,
                )
        try:
            return float(price_dict[str(use_year)][fips_idx])
        except (KeyError, IndexError, TypeError, ValueError):
            return fallback

    def _navigate_path(self, data: Any, keys: List[str]) -> Any:
        """Walk ``data`` by dict keys / list indices, returning ``None`` on a miss."""

        for key in keys:
            if isinstance(data, (list, tuple)):
                try:
                    index = int(key)
                except (TypeError, ValueError):
                    return None
                if not 0 <= index < len(data):
                    return None
                data = data[index]
            elif isinstance(data, dict):
                if key not in data:
                    return None
                data = data[key]
            else:
                return None
        return data

    def _build_pen_id_to_bedding_name(self, item: EconomicItem) -> Dict[str, Any]:
        """Map each pen's ``id`` to its first manure stream's ``bedding_name``.

        Pen totals are reported under the pen's ``id`` field, while the input
        ``pen_information`` is a list whose order need not match those ids. Matching
        on ``id`` (rather than list position) keeps each pen paired with its own
        bedding even when ids are reordered or non-contiguous (issue #3088).
        """

        template = (
            item.input_manager[0] if item.input_manager else "animal.pen_information.*.manure_streams.0.bedding_name"
        )
        if "*" not in template:
            return {}
        prefix, _, suffix = template.partition(".*.")
        pens = self.im.get_data(prefix)
        pen_map: Dict[str, Any] = {}
        if isinstance(pens, (list, tuple)):
            suffix_keys = suffix.split(".") if suffix else []
            for entry in pens:
                if isinstance(entry, dict) and "id" in entry:
                    pen_map[str(entry["id"])] = self._navigate_path(entry, suffix_keys)
        return pen_map

    def _preprocess_bedding(self, item: EconomicItem) -> Dict[str, Any]:
        """Compute bedding cost per pen, per year, then sum (issue #3088).

        For each pen the bedding name (an input config name) is resolved to its
        canonical ``bedding_type`` and then to a price file. For each simulation
        year the cost is ``(average head present that year) * (that year's
        dollar-per-head price)``; pens with no bedding (``bedding_type`` ``none``)
        incur no cost. The returned dict mirrors the generic engine's keys so
        downstream consumers are unaffected.
        """

        info_map = {"class": self.__class__.__name__, "function": self._preprocess_bedding.__name__}

        name_to_type = self._build_bedding_name_to_type(item)
        pen_id_to_bedding_name = self._build_pen_id_to_bedding_name(item)
        type_to_key = item.bedding_type_to_file_key or {}
        normalized_type_to_key = {str(key).strip().lower(): value for key, value in type_to_key.items()}
        economics_files = item.economics_files if isinstance(item.economics_files, dict) else {}

        _, start_date = self._simulation_start()
        fips = self.im.get_data("config.FIPS_county_code")

        series_by_scenario = self._collect_pen_series(item.biophysical_simulation)
        if not series_by_scenario:
            series_by_scenario = {"baseline": {}}

        price_cache: Dict[str, Any] = {}
        price_data: Dict[str, Any] = {}
        warned_years: Set[str] = set()
        price_values: List[float] = []

        line_item_values_by_scenario: Dict[str, float] = {}
        values_by_scenario: Dict[str, List[float]] = {}
        aggregates_by_scenario: Dict[str, float] = {}

        for scenario, pens in series_by_scenario.items():
            scenario_cost = 0.0
            scenario_values: List[float] = []
            for capture, payload in pens.items():
                pen_id = capture.split("_", 1)[0]
                bedding_name = pen_id_to_bedding_name.get(pen_id)
                if bedding_name is None:
                    self.om.add_warning("MissingBeddingName", f"No bedding_name for pen '{pen_id}'", info_map)
                    continue

                bedding_type = name_to_type.get(str(bedding_name))
                if bedding_type is None:
                    self.om.add_warning(
                        "UnknownBeddingConfig",
                        f"Bedding '{bedding_name}' (pen '{pen_id}') is not in bedding_configs; no cost applied",
                        info_map,
                    )
                    continue

                normalized_type = str(bedding_type).strip().lower()
                if not normalized_type or normalized_type == "none":
                    # Pen has no bedding -> no bedding cost.
                    scenario_values.extend(payload.get("values", []))
                    continue

                file_key = normalized_type_to_key.get(normalized_type)
                economics_file = economics_files.get(file_key) if file_key else None
                if file_key is None or economics_file is None:
                    self.om.add_warning(
                        "UnmappedBeddingType",
                        f"Bedding type '{bedding_type}' (pen '{pen_id}') has no economics price file; no cost applied",
                        info_map,
                    )
                    continue

                if file_key not in price_cache:
                    fetched = self._get_data_with_handling(economics_file, info_map)
                    price_cache[file_key] = fetched
                    if fetched is not None:
                        price_data[file_key] = fetched
                pen_price_dict = price_cache[file_key]
                if pen_price_dict is None:
                    self.om.add_warning(
                        "MissingBeddingPriceFile",
                        f"Bedding type '{bedding_type}' (pen '{pen_id}') maps to '{economics_file}' "
                        "which could not be loaded; no cost applied",
                        info_map,
                    )
                    scenario_values.extend(payload.get("values", []))
                    continue

                daily_values = payload.get("values", [])
                daily_info_maps = payload.get("info_maps", [])
                scenario_values.extend(daily_values)

                counts_by_year = self._bedding_counts_by_year(daily_values, daily_info_maps, start_date)
                for year, daily in counts_by_year.items():
                    if not daily:
                        continue
                    days_in_year = (
                        GeneralConstants.LEAP_YEAR_LENGTH
                        if Utility.is_leap_year(year)
                        else GeneralConstants.YEAR_LENGTH
                    )
                    average_head = sum(daily) / days_in_year
                    price = self._annual_bedding_price(pen_price_dict, year, fips, file_key, warned_years, info_map)
                    price_values.append(price)
                    scenario_cost += average_head * price

            line_item_values_by_scenario[scenario] = scenario_cost
            values_by_scenario[scenario] = scenario_values
            aggregates_by_scenario[scenario] = scenario_cost

        if item.economics_files and not price_data:
            self.om.add_warning(
                "MissingEconomicsFile",
                f"No commodity pricing retrieved for '{item.name}'",
                info_map,
            )

        all_values: List[float] = []
        for scenario_values in values_by_scenario.values():
            all_values.extend(scenario_values)

        total_cost = sum(line_item_values_by_scenario.values())
        price_aggregate = self._aggregate(price_values, "average")

        return {
            "biophysical_values": all_values,
            "biophysical_aggregate": total_cost,
            "biophysical_values_by_scenario": values_by_scenario,
            "biophysical_aggregate_by_scenario": aggregates_by_scenario,
            "price_data": price_data,
            "price_values": price_values,
            "price_aggregate": price_aggregate,
            "line_item_values_by_scenario": line_item_values_by_scenario,
            "flow_type": "cost",
        }

    def preprocess(self) -> Dict[str, Dict[str, Dict[str, Dict[str, Any]]]]:
        """Run preprocessing and store results in the InputManager."""

        results: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {}
        info_map = {"class": self.__class__.__name__, "function": self.preprocess.__name__}

        for item in self.mapping:
            section_data = results.setdefault(item.section, {})
            category_data = section_data.setdefault(item.category, {})

            # Items flagged with a dedicated processor bypass the generic engine,
            # which cannot express per-pen pairing of a quantity with a selected
            # price file (see issue #3088). ``continue`` is the loop continue, so
            # the runtime variable is still stored after the loop.
            if item.dedicated_processor == "bedding":
                category_data[item.name] = self._preprocess_bedding(item)
                continue

            values_by_scenario = self._fetch_values_by_scenario(item.biophysical_simulation)
            wildcard_values = self._collect_biophysical_wildcards(item.biophysical_simulation)
            input_values, input_match_values = self._fetch_input_values(
                item.input_manager,
                wildcard_values,
                item.wildcard_value_map,
            )

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

            biophysical_match_values = [groups[0] for groups in wildcard_values if groups]
            price_data = self._fetch_prices_with_exact_matches(
                item.economics_files,
                match_source=item.match_source,
                input_match_values=input_match_values,
                biophysical_match_values=biophysical_match_values,
            )
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
