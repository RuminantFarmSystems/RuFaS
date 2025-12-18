"""Preprocessing utilities for the economics module.

This module translates biophysical simulation outputs into
inputs required by the economic analysis. The translation is
based on the mapping stored in ``input/data/EEE/economics_map.json``
and loaded through the :class:`~RUFAS.input_manager.InputManager`.

The :class:`EconomicPreprocessor` collects values from the
:class:`~RUFAS.input_manager.InputManager`, aggregates them using
:class:`~RUFAS.util.Aggregator`, and stores the aggregated
results back into the :class:`~RUFAS.input_manager.InputManager`
under the key ``economic_preprocessed``. The structure of the
stored data is intentionally flexible and is validated using the
``economic_preprocessing_properties`` metadata.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.util import Aggregator


class EconomicPreprocessor:
    """Aggregate biophysical results for the economics module."""

    def __init__(
        self,
    ) -> None:
        self.im = InputManager()
        self.om = OutputManager()
        self.mapping = self._load_map()

    def _load_map(self) -> Dict[str, Any]:
        """Load the economics mapping from the Input Manager."""
        info_map = {"class": self.__class__.__name__, "function": self._load_map.__name__}
        mapping_name = "economics_map"
        mapping = self.im.get_data(mapping_name)
        if mapping is None:
            self.om.add_error(
                "MissingEconomicsMap",
                f"Economics mapping '{mapping_name}' not found in InputManager",
                info_map,
            )
            raise KeyError(f"Economics mapping '{mapping_name}' not found")
        return mapping

    def _append_numeric(self, container: List[float], value: Any) -> None:
        """Append numeric value to container if possible."""
        try:
            container.append(float(value))
        except (TypeError, ValueError):
            pass

    def _fetch_values(self, sim_paths: Iterable[str]) -> List[float]:
        """Collect values from the InputManager for the provided paths."""
        values: List[float] = []
        info_map = {"class": self.__class__.__name__, "function": self._fetch_values.__name__}
        for path in sim_paths:
            try:
                data = self.im.get_data(path)
            except Exception as exc:  # pragma: no cover - logging only
                self.om.add_warning("MissingBiophysicalData", f"{path}: {exc}", info_map)
                continue
            if isinstance(data, dict):
                for v in data.values():
                    self._append_numeric(values, v)
            elif isinstance(data, (list, tuple)):
                for v in data:
                    self._append_numeric(values, v)
            else:
                self._append_numeric(values, data)
        return values

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

    def preprocess(self) -> Dict[str, Dict[str, Dict[str, float | None]]]:
        """Run preprocessing and store results in the InputManager."""
        results: Dict[str, Dict[str, Dict[str, float | None]]] = {}
        info_map = {"class": self.__class__.__name__, "function": self.preprocess.__name__}

        for section, categories in self.mapping.items():
            section_data: Dict[str, Dict[str, float | None]] = {}
            for category, items in categories.items():
                if not isinstance(items, dict):
                    continue
                category_data: Dict[str, float | None] = {}
                for name, details in items.items():
                    sim_paths = details.get("biophysical_simulation")
                    if not sim_paths:
                        continue
                    if isinstance(sim_paths, str):
                        sim_paths = [sim_paths]
                    values = self._fetch_values(sim_paths)
                    agg_value = self._aggregate(values, details.get("preprocessing", ""))
                    category_data[name] = agg_value
                section_data[category] = category_data
            results[section] = section_data

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
