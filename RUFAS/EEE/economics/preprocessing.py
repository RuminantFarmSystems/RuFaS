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
from typing import Any, Dict, Iterable, List

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.util import Aggregator
from RUFAS.EEE.economics.mapping import ECONOMIC_MAP


@dataclass(frozen=True)
class EconomicItem:
    """Definition of a single economic preprocessing item."""

    section: str
    category: str
    name: str
    biophysical_simulation: List[str]
    economics_files: Any
    preprocessing: str | None


class EconomicPreprocessor:
    """Aggregate biophysical results for the economics module."""

    def __init__(
        self,
    ) -> None:
        self.im = InputManager()
        self.om = OutputManager()
        self.mapping = self._build_mapping()

    def _get_data_with_handling(self, path: str, info_map: Dict[str, str]) -> Any:
        """Fetch data from the InputManager while handling invalid paths."""

        if not isinstance(path, str) or not path:
            self.om.add_warning(
                "InvalidEconomicsFilePath",
                f"Economics pricing path '{path}' is invalid",
                info_map,
            )
            return None

        try:
            return self.im.get_data(path)
        except ValueError as exc:
            self.om.add_warning(
                "InvalidEconomicsFilePath",
                f"Failed to retrieve '{path}': {exc}",
                info_map,
            )
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
                    preprocessing = details.get("preprocessing")
                    economics_files = details.get("economics_files")
                    if not biophysical_simulation and not economics_files:
                        continue
                    if isinstance(biophysical_simulation, str):
                        biophysical_simulation = [biophysical_simulation]
                    items.append(
                        EconomicItem(
                            section=section,
                            category=category,
                            name=name,
                            biophysical_simulation=list(biophysical_simulation),
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
                self.om.add_warning(
                    "MissingBiophysicalData",
                    f"No biophysical outputs matched pattern '{path}'",
                    info_map,
                )
        return values

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

            values = self._fetch_values(item.biophysical_simulation)
            aggregated_value = self._aggregate(values, item.preprocessing or "")
            if not values:
                self.om.add_warning(
                    "MissingBiophysicalData",
                    f"No values found for '{item.name}' using patterns {item.biophysical_simulation}",
                    info_map,
                )

            price_data = self._fetch_prices(item.economics_files)
            if item.economics_files and not price_data:
                self.om.add_warning(
                    "MissingEconomicsFile",
                    f"No commodity pricing retrieved for '{item.name}'",
                    info_map,
                )

            category_data[item.name] = {
                "biophysical_values": values,
                "biophysical_aggregate": aggregated_value,
                "price_data": price_data,
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
