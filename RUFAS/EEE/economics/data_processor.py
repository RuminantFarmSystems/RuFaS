import math
from typing import Any, Iterable

from RUFAS.EEE.economics.fallback_values import BIOPHYSICAL_FALLBACKS, ECONOMIC_PRICE_FALLBACK
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager


class EconomicDataProcessor:
    """Shared InputManager/OutputManager services for economics preprocessing.

    Attributes
    ----------
    im : InputManager
        Input manager used to resolve economic inputs and commodity pricing.
    om : OutputManager
        Output manager used to read biophysical outputs and record warnings.
    available_input_keys : set[str]
        Input keys available in the InputManager metadata.
    """

    def __init__(self) -> None:
        self.im = InputManager()
        self.om = OutputManager()
        self.available_input_keys: set[str] = self._load_available_input_keys()

    def _load_available_input_keys(self) -> set[str]:
        """Cache the available input keys from the InputManager metadata."""

        try:
            metadata = self.im.get_metadata("files")
        except Exception:
            return set()

        if isinstance(metadata, dict):
            return set(metadata.keys())
        return set()

    def normalize_economics_key(self, path: str) -> str:
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

    def get_data_with_handling(self, path: str, info_map: dict[str, str]) -> Any:
        """Fetch data from the InputManager while handling invalid paths."""

        if not isinstance(path, str) or not path:
            self.om.add_warning(
                "InvalidEconomicsFilePath",
                f"Economics pricing path '{path}' is invalid",
                info_map,
            )
            return None

        candidate_paths = [path]
        normalized_path = self.normalize_economics_key(path)
        if normalized_path != path:
            candidate_paths.append(normalized_path)

        last_error: ValueError | None = None
        for candidate in candidate_paths:
            if "*" in str(candidate):
                self.om.add_warning(
                    "MissingEconomicsFile",
                    f"Commodity pricing '{candidate}' uses wildcard and was skipped",
                    info_map,
                )
                continue

            data, error = self._fetch_candidate(candidate)
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
            self.om.add_warning("InvalidEconomicsFilePath", detail, info_map)

        return None

    def _fetch_candidate(self, candidate: str) -> tuple[Any, ValueError | None]:
        """Fetch one candidate path from the InputManager, returning the data and any lookup error."""

        try:
            if hasattr(self.im, "check_property_exists_in_pool") and not self.im.check_property_exists_in_pool(
                candidate
            ):
                return None, None
            return self.im.get_data(candidate), None
        except ValueError as exc:
            return None, exc

    def get_fallback_price(self, start_year: int, end_year: int, commodity: str) -> list[float]:
        """Get a fallback price for a commodity."""
        info_map = {"class": self.__class__.__name__, "function": self.get_fallback_price.__name__}
        defaults: dict[str, list[float | str]] = self.im.get_data("_default_values")
        defaults_fallback: dict[str, list[float | str]] = self.im.get_data("_default_fallback_values")
        if commodity not in defaults["commodity"] and commodity not in defaults_fallback["commodity"]:
            self.om.add_warning(
                "MissingFallbackPrice",
                f"No fallback price found for commodity: {commodity}",
                info_map,
            )
            return [ECONOMIC_PRICE_FALLBACK.get("cost", 1.0)] * (end_year - start_year + 1)
        years = range(start_year, end_year + 1)
        primary_prices = self._read_yearly_prices(defaults, commodity, years)
        if primary_prices is not None and not any(math.isnan(price) for price in primary_prices):
            return primary_prices
        fallback_prices = self._read_yearly_prices(defaults_fallback, commodity, years) or [math.nan] * len(years)
        values: list[float] = []
        for year, price in zip(years, fallback_prices):
            if math.isnan(price):
                self.om.add_warning(
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

    def scenario_names(self) -> list[str]:
        """Determine scenario names from the OutputManager variables pool.

        Returns
        -------
        list[str]
            Scenario names found as top-level keys of the variables pool, or
            ``["baseline"]`` when the pool is flat (plain variable payloads)
            or empty.
        """
        scenario_names: list[str] = []
        pool = getattr(self.om, "variables_pool", {})
        if isinstance(pool, dict) and pool:
            if all(isinstance(value, dict) and "values" in value for value in pool.values()):
                scenario_names = ["baseline"]
            else:
                scenario_names = [name for name, data in pool.items() if isinstance(data, dict) and data]
        if not scenario_names:
            scenario_names = ["baseline"]
        return scenario_names

    def append_numeric(self, container: list[float], value: Any) -> None:
        """Append numeric value to container if possible."""
        try:
            container.append(float(value))
        except (TypeError, ValueError):
            pass

    def append_from_payload(self, container: list[float], payload: Any) -> None:
        """Append numeric values from an OutputManager payload."""

        if isinstance(payload, dict) and "values" in payload:
            for value in payload.get("values", []):
                self.append_from_payload(container, value)
            return
        if isinstance(payload, dict):
            for value in payload.values():
                self.append_from_payload(container, value)
            return
        if isinstance(payload, (list, tuple)):
            for value in payload:
                self.append_from_payload(container, value)
            return
        self.append_numeric(container, payload)

    def build_filter_content(self, path: str, expand_interval_to_daily: bool) -> dict[str, Any]:
        """Build OutputManager filter options, requesting daily expansion when applicable."""

        filter_content: dict[str, Any] = {"filters": [path]}
        if not expand_interval_to_daily:
            return filter_content

        if getattr(self.om, "time", None) is None:
            self.om.add_warning(
                "MissingTimeForIntervalExpansion",
                f"Cannot expand interval data to daily for '{path}' because the OutputManager time is not initialized",
                {"class": self.__class__.__name__, "function": self.build_filter_content.__name__},
            )
            return filter_content

        # Interval-reported variables (e.g. ration interval feed purchases) are only recorded on the days
        # they occur; pad the gap days with zeros so the series aligns with daily-reported data.
        filter_content["expand_data"] = True
        filter_content["fill_value"] = 0.0
        return filter_content

    def fetch_values_by_scenario(
        self, sim_paths: Iterable[str], expand_interval_to_daily: bool = False
    ) -> dict[str, list[float]]:
        """Collect values per scenario from the OutputManager."""

        filtered_by_path: dict[str, dict[str, Any]] = {
            path: self.om.filter_variables_pool(self.build_filter_content(path, expand_interval_to_daily))
            for path in sim_paths
        }
        info_map = {"class": self.__class__.__name__, "function": self.fetch_values_by_scenario.__name__}
        if not any(filtered_by_path.values()):
            fallback_by_scenario = self._fallback_values_by_scenario(sim_paths)
            if fallback_by_scenario:
                self.om.add_warning(
                    "BiophysicalFallbackSubstituted",
                    f"No biophysical outputs matched patterns {list(sim_paths)}; substituted fallback values",
                    info_map,
                )
            return fallback_by_scenario
        scenario_names = self.scenario_names()
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
                self.append_from_payload(values_by_scenario[scenario_key], payload)
            if not matched:
                fallback_values = BIOPHYSICAL_FALLBACKS.get(path)
                if fallback_values:
                    scenario_key = scenario_names[0] if scenario_names else "baseline"
                    values_by_scenario.setdefault(scenario_key, [])
                    values_by_scenario[scenario_key].extend(fallback_values)
                    self.om.add_warning(
                        "BiophysicalFallbackSubstituted",
                        f"No biophysical outputs matched pattern '{path}'; substituted fallback values",
                        info_map,
                    )
                else:
                    self.om.add_warning(
                        "MissingBiophysicalData",
                        f"No biophysical outputs matched pattern '{path}'",
                        info_map,
                    )
        return values_by_scenario

    def _fallback_values_by_scenario(self, sim_paths: Iterable[str]) -> dict[str, list[float]]:
        """Build fallback values when no OutputManager data is available."""

        values_by_scenario: dict[str, list[float]] = {"baseline": []}
        for path in sim_paths:
            fallback_values = BIOPHYSICAL_FALLBACKS.get(path)
            if fallback_values:
                values_by_scenario["baseline"].extend(fallback_values)

        if values_by_scenario["baseline"]:
            return values_by_scenario
        return {}
