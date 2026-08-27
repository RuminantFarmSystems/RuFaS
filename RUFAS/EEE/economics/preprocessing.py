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

Line items whose preprocessing cannot be expressed by the generic
biophysical/input/price pipeline are delegated to dedicated
:class:`~RUFAS.EEE.economics.special_cases.base.SpecialCaseHandler`
subclasses. :class:`EconomicPreprocessor` builds a ``(section, name)``
handler map from :data:`~RUFAS.EEE.economics.special_cases.SPECIAL_CASE_HANDLERS`
and routes matching line items to them, keeping the main pipeline free of
per-item special casing.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.util import Aggregator
from RUFAS.EEE.economics.mapping import ECONOMIC_MAP
from RUFAS.EEE.economics.preprocessing_context import PreprocessingContext
from RUFAS.EEE.economics.special_cases import (
    SpecialCaseHandler,
    HomegrownFeedHandler,
)
from RUFAS.EEE.economics.fallback_values import (
    BIOPHYSICAL_FALLBACKS,
    ECONOMIC_PRICE_FALLBACK,
    ECONOMIC_QUANTITY_FALLBACK,
)

# Provenance marker for pool variables computed in-memory rather than loaded
# from an input file; used only in InputManager validation messages.
COMPUTED_PREPROCESSING_INPUT_PATH = Path("<computed: EconomicPreprocessor.preprocess>")

# Registry of special-case handlers keyed by (section, name) at build time.
# Register a new handler by appending its class here.
SPECIAL_CASE_HANDLERS: list[type[SpecialCaseHandler]] = [
    HomegrownFeedHandler,
]


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


class EconomicPreprocessor:
    """Aggregate biophysical results for the economics module."""

    def __init__(
        self,
    ) -> None:
        self.im = InputManager()
        self.om = OutputManager()
        self.context = PreprocessingContext(self.im, self.om)
        self.mapping = self._build_mapping()
        self.special_case_handlers = self._build_special_case_handlers()

    def _build_special_case_handlers(self) -> dict[tuple[str, str], SpecialCaseHandler]:
        """Instantiate registered special-case handlers keyed by ``(section, name)``.

        A handler that owns several line items contributes one entry per pair in
        its :attr:`~RUFAS.EEE.economics.special_cases.base.SpecialCaseHandler.keys`.
        """

        handlers: dict[tuple[str, str], SpecialCaseHandler] = {}
        for handler_cls in SPECIAL_CASE_HANDLERS:
            handler = handler_cls(self.context)
            for key in handler.keys:
                handlers[key] = handler
        return handlers

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
                        )
                    )
        return items

    def _fetch_values_by_scenario(self, sim_paths: Iterable[str]) -> Dict[str, List[float]]:
        """Collect values per scenario from the OutputManager."""

        filtered_by_path: Dict[str, Dict[str, Any]] = {
            path: self.om.filter_variables_pool({"filters": [path]}) for path in sim_paths
        }
        if not any(filtered_by_path.values()):
            fallback_values = self._fallback_values_by_scenario(sim_paths)
            return fallback_values
        scenario_names = self.context.scenario_names()
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
                self.context.append_from_payload(values_by_scenario[scenario_key], payload)
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
                self.context.append_from_payload(values, data)
        return values, exact_match_values

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
            return self.context.fetch_prices(economics_files)

        source = str(match_source or "").lower()
        if source not in {"input_manager", "biophysical_simulation"}:
            return self.context.fetch_prices(economics_files)

        requested_values = (
            list(input_match_values or []) if source == "input_manager" else list(biophysical_match_values or [])
        )
        requested = {str(value).lower() for value in requested_values if str(value).strip()}
        if not requested:
            return self.context.fetch_prices(economics_files)

        info_map = {"class": self.__class__.__name__, "function": self._fetch_prices_with_exact_matches.__name__}
        prices: Dict[str, Any] = {}
        for option, file_key in economics_files.items():
            if option in {"input_manager_location", "biophysical_simulation_location"}:
                continue
            if str(option).lower() not in requested or not isinstance(file_key, str):
                continue
            price_data = self.context.get_data_with_handling(file_key, info_map)
            if price_data is not None:
                prices[option] = price_data
        return prices

    def preprocess(self) -> Dict[str, Dict[str, Dict[str, Dict[str, Any]]]]:
        """Run preprocessing and store results in the InputManager."""

        results: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {}
        info_map = {"class": self.__class__.__name__, "function": self.preprocess.__name__}

        for item in self.mapping:
            section_data = results.setdefault(item.section, {})
            category_data = section_data.setdefault(item.category, {})

            handler = self.special_case_handlers.get((item.section, item.name))
            if handler is not None:
                special_result = handler.process(item)
                if special_result is not None:
                    category_data[item.name] = special_result
                    continue

            values_by_scenario = self._fetch_values_by_scenario(item.biophysical_simulation)
            wildcard_values = self.context.collect_biophysical_wildcards(item.biophysical_simulation)

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

            aggregated_value = self.context.aggregate(biophysical_values, item.preprocessing or "")
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

            price_values = self.context.extract_price_values(price_data)
            price_aggregate = self.context.aggregate(price_values, "average")
            if price_aggregate is None:
                flow_type = self._infer_flow_type(item) or "cost"
                if flow_type in ECONOMIC_PRICE_FALLBACK:
                    price_aggregate = ECONOMIC_PRICE_FALLBACK[flow_type]
            aggregates_by_scenario: Dict[str, float | None] = {}
            for scenario, scenario_values in values_by_scenario.items():
                scenario_aggregate = self.context.aggregate(scenario_values, item.preprocessing or "")
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
            input_path=COMPUTED_PREPROCESSING_INPUT_PATH,
        )
        self.om.add_log(
            "Economic preprocessing",
            "Economic preprocessing completed",
            info_map,
        )
        return results


__all__ = ["EconomicPreprocessor"]
