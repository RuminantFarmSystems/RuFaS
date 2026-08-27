import math
from typing import Any, Iterable

from RUFAS.util import Aggregator
from RUFAS.EEE.economics.fallback_values import BIOPHYSICAL_FALLBACKS, ECONOMIC_PRICE_FALLBACK
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager


class EconomicDataProcessor:
    """Shared InputManager/OutputManager services for economics preprocessing.

    Parameters
    ----------
    im : InputManager, optional
        Input manager used to resolve economic inputs and commodity pricing.
        Defaults to the ``InputManager`` singleton.
    om : OutputManager, optional
        Output manager used to read biophysical outputs and record warnings.
        Defaults to the ``OutputManager`` singleton.
    """

    def __init__(self, im: InputManager | None = None, om: OutputManager | None = None) -> None:
        self.im = im if im is not None else InputManager()
        self.om = om if om is not None else OutputManager()
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

            if hasattr(self.im, "check_property_exists_in_pool"):
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
        commodity_idx = defaults["commodity"].index(commodity)
        values: list[float] = []
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
        if not any(filtered_by_path.values()):
            fallback_values = self._fallback_values_by_scenario(sim_paths)
            return fallback_values
        scenario_names = self.scenario_names()
        values_by_scenario: dict[str, list[float]] = {scenario: [] for scenario in scenario_names}
        info_map = {"class": self.__class__.__name__, "function": self.fetch_values_by_scenario.__name__}

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

    def aggregate(self, values: list[float], desc: str) -> float | None:
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
        return Aggregator.sum(values)


__all__ = ["EconomicDataProcessor"]
