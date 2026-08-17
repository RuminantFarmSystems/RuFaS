"""Shared services for economics preprocessing.

Houses :class:`PreprocessingContext`, a small facade over the
:class:`~RUFAS.input_manager.InputManager` and
:class:`~RUFAS.output_manager.OutputManager` that exposes the data-access,
pricing, scenario, and aggregation helpers shared by the main
:class:`~RUFAS.EEE.economics.preprocessing.EconomicPreprocessor` and by the
special-case handlers in :mod:`RUFAS.EEE.economics.special_cases`.

Keeping these helpers in one place lets the main preprocessor and every
special-case handler resolve InputManager data, fall back to default prices,
enumerate scenarios, and aggregate value series through a single, tested
implementation.
"""

import math
from typing import TYPE_CHECKING, Any

from RUFAS.util import Aggregator
from RUFAS.EEE.economics.fallback_values import ECONOMIC_PRICE_FALLBACK

if TYPE_CHECKING:
    from RUFAS.input_manager import InputManager
    from RUFAS.output_manager import OutputManager


class PreprocessingContext:
    """Shared InputManager/OutputManager services for economics preprocessing.

    Parameters
    ----------
    im : InputManager
        Input manager used to resolve economic inputs and commodity pricing.
    om : OutputManager
        Output manager used to read biophysical outputs and record warnings.
    """

    def __init__(self, im: "InputManager", om: "OutputManager") -> None:
        self.im = im
        self.om = om
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
        # Default aggregation is sum
        return Aggregator.sum(values)

    def fetch_prices(self, economics_files: Any) -> dict[str, Any]:
        """Collect commodity pricing using the InputManager.

        Accepts the ``economics_files`` mapping value in any of its supported
        forms (a list of file keys, a selector dict with
        ``input_manager_location``, or a plain label/file-key dict) and returns
        the resolved pricing payloads keyed by file key or label.
        """

        prices: dict[str, Any] = {}
        info_map = {"class": self.__class__.__name__, "function": self.fetch_prices.__name__}

        if economics_files is None:
            return prices

        if isinstance(economics_files, list):
            for file_key in economics_files:
                price_data = self.get_data_with_handling(file_key, info_map)
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
            selection = self.get_data_with_handling(selector_path, info_map)
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
                    price_data = self.get_data_with_handling(file_key, info_map)
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
                    price_data = self.get_data_with_handling(file_key, info_map)
                    if price_data is not None:
                        prices[file_key] = price_data
                if prices:
                    self.om.add_warning(
                        "UnknownSelectionFallback",
                        f"No matching selection; using all available pricing options for '{selector_path}'.",
                        info_map,
                    )
                return prices
            price_data = self.get_data_with_handling(selected_file, info_map)
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
            price_data = self.get_data_with_handling(file_key, info_map)
            if price_data is None:
                self.om.add_warning(
                    "MissingEconomicsFile",
                    f"Commodity pricing '{file_key}' not found in InputManager",
                    info_map,
                )
                continue
            prices[label] = price_data
        return prices

    def extract_price_values(self, price_data: Any) -> list[float]:
        """Extract numeric price values from pricing payloads.

        Prices are read for the configured FIPS county across every year in the
        simulation window, falling back to default prices when a payload is
        malformed or a year is missing.
        """

        info_map = {"class": self.__class__.__name__, "function": self.extract_price_values.__name__}
        start_year: int = int(self.im.get_data("config.start_date").split(":")[0])
        end_year: int = int(self.im.get_data("config.end_date").split(":")[0])
        fips_code: int = self.im.get_data("config.FIPS_county_code")
        values: list[float] = []
        for key, value in price_data.items():
            if not isinstance(value, dict) or "fips" not in value or not isinstance(value["fips"], list):
                self.om.add_warning(
                    "MissingPriceData",
                    f"Price data missing for key: {key}, FIPS: '{fips_code}' is not in expected format."
                    "Using fallback price.",
                    info_map,
                )
                values.extend(self.get_fallback_price(start_year, end_year, key))
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
                    values.extend(self.get_fallback_price(start_year, end_year, key))
                    continue
        return values


__all__ = ["PreprocessingContext"]
