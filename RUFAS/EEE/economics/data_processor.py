import math
import re
from typing import Any, Iterable

from RUFAS.EEE.economics.fallback_values import BIOPHYSICAL_FALLBACKS, ECONOMIC_PRICE_FALLBACK
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager


class EconomicDataProcessor:
    """Stateless InputManager/OutputManager helpers shared by economics preprocessing and line-item handlers.

    All methods are static and resolve the ``InputManager`` and ``OutputManager`` singletons at call time.
    """

    @staticmethod
    def available_input_keys() -> set[str]:
        """Read the available input keys from the InputManager metadata."""
        # previously Preprocessing._load_available_input_keys()
        try:
            im = InputManager()
            metadata = im.get_metadata("files")
        except Exception:
            return set()

        if isinstance(metadata, dict):
            return set(metadata.keys())
        return set()

    @staticmethod
    def normalize_economics_key(path: str) -> str:
        """Map mapping file paths to InputManager data keys."""
        # previously Preprocessing._normalize_economics_key()
        candidate = path.removesuffix(".csv")
        available_input_keys = EconomicDataProcessor.available_input_keys()

        if not available_input_keys:
            return candidate

        if candidate in available_input_keys:
            return candidate

        prefix_matches = sorted(key for key in available_input_keys if key.startswith(f"{candidate}."))
        if prefix_matches:
            return prefix_matches[0]

        return candidate

    @staticmethod
    def get_data_with_handling(path: str, info_map: dict[str, str]) -> Any:
        """Fetch data from the InputManager while handling invalid paths."""
        # previously Preprocessing._get_data_with_handling()
        om = OutputManager()
        if not isinstance(path, str) or not path:
            om.add_warning(
                "InvalidEconomicsFilePath",
                f"Economics pricing path '{path}' is invalid",
                info_map,
            )
            return None

        candidate_paths = [path]
        normalized_path = EconomicDataProcessor.normalize_economics_key(path)
        if normalized_path != path:
            candidate_paths.append(normalized_path)

        last_error: ValueError | None = None
        for candidate in candidate_paths:
            if "*" in str(candidate):
                om.add_warning(
                    "MissingEconomicsFile",
                    f"Commodity pricing '{candidate}' uses wildcard and was skipped",
                    info_map,
                )
                continue

            data, error = EconomicDataProcessor._fetch_candidate(candidate)
            if error is not None:
                last_error = error
            if data is not None:
                return data

        if last_error is not None:
            detail = (
                f"Failed to retrieve '{path}'"
                + (f" (normalized to '{normalized_path}')" if normalized_path != path else "")
                + f": {last_error}"
            )
            om.add_warning("InvalidEconomicsFilePath", detail, info_map)

        return None

    @staticmethod
    def _fetch_candidate(candidate: str) -> tuple[Any, ValueError | None]:
        """Fetch one candidate path from the InputManager, returning the data and any lookup error."""

        im = InputManager()
        try:
            if hasattr(im, "check_property_exists_in_pool") and not im.check_property_exists_in_pool(candidate):
                return None, None
            return im.get_data(candidate), None
        except ValueError as exc:
            return None, exc

    @staticmethod
    def get_fallback_price(start_year: int, end_year: int, commodity: str) -> list[float]:
        """Get a fallback price for a commodity."""
        info_map = {
            "class": EconomicDataProcessor.__name__,
            "function": EconomicDataProcessor.get_fallback_price.__name__,
        }
        defaults: dict[str, list[float | str]] = InputManager().get_data("_default_values")
        defaults_fallback: dict[str, list[float | str]] = InputManager().get_data("_default_fallback_values")
        if commodity not in defaults["commodity"] and commodity not in defaults_fallback["commodity"]:
            OutputManager().add_warning(
                "MissingFallbackPrice",
                f"No fallback price found for commodity: {commodity}",
                info_map,
            )
            return [ECONOMIC_PRICE_FALLBACK.get("cost", 1.0)] * (end_year - start_year + 1)
        years = range(start_year, end_year + 1)
        primary_prices = EconomicDataProcessor._read_yearly_prices(defaults, commodity, years)
        if primary_prices is not None and not any(math.isnan(price) for price in primary_prices):
            return primary_prices
        fallback_prices = EconomicDataProcessor._read_yearly_prices(defaults_fallback, commodity, years) or [
            math.nan
        ] * len(years)
        values: list[float] = []
        for year, price in zip(years, fallback_prices):
            if math.isnan(price):
                OutputManager().add_warning(
                    "MissingFallbackPrice",
                    f"No fallback price found for commodity: {commodity} in year: {year}",
                    info_map,
                )
                price = ECONOMIC_PRICE_FALLBACK.get("cost", 1.0)
            values.append(price)
        return values

    @staticmethod
    def _read_yearly_prices(
        table: dict[str, list[float | str]], commodity: str, years: Iterable[int]
    ) -> list[float] | None:
        """Read a commodity's per-year prices from a defaults table, or None when the commodity is absent."""

        if commodity not in table["commodity"]:
            return None
        commodity_idx = table["commodity"].index(commodity)
        return [float(table[f"{year}"][commodity_idx]) for year in years]

    @staticmethod
    def scenario_names() -> list[str]:
        """
        Determine scenario names from the OutputManager variables pool.

        Returns
        -------
        list[str]
            Scenario names found as top-level keys of the variables pool, or
            ``["baseline"]`` when the pool is flat (plain variable payloads)
            or empty.
        """
        scenario_names: list[str] = []
        pool = getattr(OutputManager(), "variables_pool", {})
        if isinstance(pool, dict) and pool:
            if all(isinstance(value, dict) and "values" in value for value in pool.values()):
                scenario_names = ["baseline"]
            else:
                scenario_names = [name for name, data in pool.items() if isinstance(data, dict) and data]
        if not scenario_names:
            scenario_names = ["baseline"]
        return scenario_names

    @staticmethod
    def append_numeric(container: list[float], value: Any) -> None:
        """Append numeric value to container if possible."""
        try:
            container.append(float(value))
        except (TypeError, ValueError):
            pass

    @staticmethod
    def append_from_payload(container: list[float], payload: Any) -> None:
        """Append numeric values from an OutputManager payload."""

        if isinstance(payload, dict) and "values" in payload:
            for value in payload.get("values", []):
                EconomicDataProcessor.append_from_payload(container, value)
            return
        if isinstance(payload, dict):
            for value in payload.values():
                EconomicDataProcessor.append_from_payload(container, value)
            return
        if isinstance(payload, (list, tuple)):
            for value in payload:
                EconomicDataProcessor.append_from_payload(container, value)
            return
        EconomicDataProcessor.append_numeric(container, payload)

    @staticmethod
    def build_filter_content(path: str, expand_interval_to_daily: bool) -> dict[str, Any]:
        """Build OutputManager filter options, requesting daily expansion when applicable."""

        filter_content: dict[str, Any] = {"filters": [path]}
        if not expand_interval_to_daily:
            return filter_content

        om = OutputManager()
        if getattr(om, "time", None) is None:
            om.add_warning(
                "MissingTimeForIntervalExpansion",
                f"Cannot expand interval data to daily for '{path}' because the OutputManager time is not initialized",
                {
                    "class": EconomicDataProcessor.__name__,
                    "function": EconomicDataProcessor.build_filter_content.__name__,
                },
            )
            return filter_content
        filter_content["expand_data"] = True
        filter_content["fill_value"] = 0.0
        return filter_content

    @staticmethod
    def fetch_values_by_scenario(
        sim_paths: list[str], expand_interval_to_daily: bool = False
    ) -> dict[str, list[float]]:
        """Collect values per scenario from the OutputManager."""
        om = OutputManager()
        info_map = {
            "class": EconomicDataProcessor.__name__,
            "function": EconomicDataProcessor.fetch_values_by_scenario.__name__,
        }
        filtered_by_path: dict[str, dict[str, Any]] = {
            path: om.filter_variables_pool(EconomicDataProcessor.build_filter_content(path, expand_interval_to_daily))
            for path in sim_paths
        }
        if not any(filtered_by_path.values()):
            fallback_by_scenario = EconomicDataProcessor.fallback_values_by_scenario(sim_paths)
            if fallback_by_scenario:
                om.add_warning(
                    "BiophysicalFallbackSubstituted",
                    f"No biophysical outputs matched patterns {list(sim_paths)}; substituted fallback values",
                    info_map,
                )
            return fallback_by_scenario
        scenario_names = EconomicDataProcessor.scenario_names()
        values_by_scenario: dict[str, list[float]] = {scenario: [] for scenario in scenario_names}

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
                EconomicDataProcessor.append_from_payload(values_by_scenario[scenario_key], payload)
            if not matched:
                fallback_values = BIOPHYSICAL_FALLBACKS.get(path)
                if fallback_values:
                    scenario_key = scenario_names[0] if scenario_names else "baseline"
                    values_by_scenario.setdefault(scenario_key, [])
                    values_by_scenario[scenario_key].extend(fallback_values)
                    om.add_warning(
                        "BiophysicalFallbackSubstituted",
                        f"No biophysical outputs matched pattern '{path}'; substituted fallback values",
                        info_map,
                    )
                else:
                    om.add_warning(
                        "MissingBiophysicalData",
                        f"No biophysical outputs matched pattern '{path}'",
                        info_map,
                    )
        return values_by_scenario

    @staticmethod
    def fallback_values_by_scenario(sim_paths: list[str]) -> dict[str, list[float]]:
        """Build fallback values when no OutputManager data is available."""

        values_by_scenario: dict[str, list[float]] = {"baseline": []}
        for path in sim_paths:
            fallback_values = BIOPHYSICAL_FALLBACKS.get(path)
            if fallback_values:
                values_by_scenario["baseline"].extend(fallback_values)

        if values_by_scenario["baseline"]:
            return values_by_scenario
        return {}

    @staticmethod
    def collect_biophysical_wildcards(sim_paths: list[str]) -> list[tuple[str, ...]]:
        """Collect wildcard values from matched biophysical variable names."""
        captures: list[tuple[str, ...]] = []
        seen: set[tuple[str, ...]] = set()
        om = OutputManager()
        for path in sim_paths:
            capture_pattern = re.compile(f"^{path.replace('.*', '(.+)')}$")
            filtered_pool = om.filter_variables_pool({"filters": [path]})
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

    @staticmethod
    def expand_input_path_with_wildcards(
        path: str,
        wildcard_values: list[tuple[str, ...]],
        wildcard_value_map: dict[str, str] | None = None,
    ) -> list[str]:
        """Expand InputManager wildcard paths using biophysical wildcard matches."""

        if "*" not in path:
            return [path]

        expanded_paths: list[str] = []
        seen: set[str] = set()
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

    @staticmethod
    def fetch_input_values(
        input_paths: list[str],
        biophysical_wildcards: list[tuple[str, ...]] | None = None,
        wildcard_value_map: dict[str, str] | None = None,
    ) -> tuple[list[float], list[str]]:
        """Collect values from the InputManager for the provided paths."""

        values: list[float] = []
        exact_match_values: list[str] = []
        info_map = {
            "class": EconomicDataProcessor.__name__,
            "function": EconomicDataProcessor.fetch_input_values.__name__,
        }
        wildcard_values = list(biophysical_wildcards or [])
        om = OutputManager()
        im = InputManager()
        for path in input_paths:
            candidate_paths = [path]
            if "*" in path:
                expanded_paths = EconomicDataProcessor.expand_input_path_with_wildcards(
                    path, wildcard_values, wildcard_value_map
                )
                if expanded_paths:
                    candidate_paths = expanded_paths
                else:
                    om.add_warning(
                        "MissingEconomicInputWildcard",
                        f"Could not expand wildcard path '{path}' from biophysical matches",
                        info_map,
                    )
                    continue

            for candidate_path in candidate_paths:
                data = im.get_data(candidate_path)
                if data is None:
                    om.add_warning(
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
                EconomicDataProcessor.append_from_payload(values, data)
        return values, exact_match_values
