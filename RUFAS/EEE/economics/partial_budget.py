"""Partial Budget Analysis (PBA) calculations."""

from __future__ import annotations

from typing import Any, Dict

import numpy as np
import pandas as pd
import math

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits


class PartialBudget:
    """Container for partial budget inputs and analysis."""

    def __init__(self) -> None:
        self.im = InputManager()
        self.om = OutputManager()

    @staticmethod
    def _to_array(value: Any) -> np.ndarray:
        """Convert partial budget inputs to a one-dimensional float array."""

        if isinstance(value, np.ndarray):
            arr = value.astype(float, copy=True)
        else:
            try:
                arr = np.asarray(value, dtype=float)
            except Exception:
                arr = np.asarray([0.0], dtype=float)
        if arr.ndim == 0:
            arr = arr.reshape(1)
        arr = np.where(np.isnan(arr), 0.0, arr)
        return arr.astype(float)

    def _load_inputs(self) -> Dict[str, np.ndarray]:
        """Deprecated: retained for backwards compatibility."""

        zero = self._to_array(0.0)
        return {
            "additional_revenue": zero.copy(),
            "reduced_costs": zero.copy(),
            "additional_costs": zero.copy(),
            "reduced_revenue": zero.copy(),
        }

    @staticmethod
    def _pick_scenario(scenario_names: set[str], candidates: list[str]) -> str | None:
        """Pick a scenario name by case-insensitive matching against candidates."""
        for candidate in candidates:
            for name in scenario_names:
                if name.lower() == candidate:
                    return name
        return None

    @staticmethod
    def _coerce_finite(value: Any) -> float:
        """Convert to float and coerce non-finite/invalid values to 0."""
        try:
            coerced = float(value)
        except (TypeError, ValueError):
            return 0.0
        return coerced if math.isfinite(coerced) else 0.0

    def _summarize_single_scenario(
        self,
        scenario: str,
        items: list[tuple[str | None, Dict[str, Any], Dict[str, float]]],
    ) -> Dict[str, Any]:
        """Aggregate one-scenario partial budget totals."""
        revenue_total = 0.0
        cost_total = 0.0
        for flow_type, _, line_items in items:
            normalized_flow_type = flow_type or "cost"
            if normalized_flow_type not in {"revenue", "cost"}:
                continue
            value = self._coerce_finite(line_items.get(scenario, 0.0))
            if normalized_flow_type == "revenue":
                revenue_total += value
            else:
                cost_total += value

        return {
            "mode": "single",
            "scenario": scenario,
            "revenue_total": revenue_total,
            "cost_total": cost_total,
            "net_annual_cash_flow": revenue_total - cost_total,
        }

    def _accumulate_delta_components(
        self,
        items: list[tuple[str | None, Dict[str, Any], Dict[str, float]]],
        baseline: str,
        alternative: str,
        info_map: Dict[str, str],
    ) -> Dict[str, float]:
        """Accumulate delta-mode partial budget buckets."""
        additional_revenue = 0.0
        reduced_revenue = 0.0
        additional_costs = 0.0
        reduced_costs = 0.0

        for flow_type, _, line_items in items:
            normalized_flow_type = flow_type or "cost"
            if normalized_flow_type not in {"revenue", "cost"}:
                continue
            if baseline not in line_items or alternative not in line_items:
                self.om.add_warning(
                    "MissingScenarioData",
                    f"Partial budget line item missing scenario values for '{baseline}' or '{alternative}'.",
                    info_map,
                )
            value_a = self._coerce_finite(line_items.get(baseline, 0.0) or 0.0)
            value_b = self._coerce_finite(line_items.get(alternative, 0.0) or 0.0)
            delta = value_b - value_a

            if normalized_flow_type == "revenue":
                if delta > 0:
                    additional_revenue += delta
                elif delta < 0:
                    reduced_revenue += abs(delta)
            else:
                if delta > 0:
                    additional_costs += delta
                elif delta < 0:
                    reduced_costs += abs(delta)

        return {
            "additional_revenue": additional_revenue,
            "reduced_revenue": reduced_revenue,
            "additional_costs": additional_costs,
            "reduced_costs": reduced_costs,
        }

    def _publish_delta_outputs(self, info_map: Dict[str, str], derived_inputs: Dict[str, Any]) -> None:
        inputs = {
            key: self._to_array(derived_inputs[key])
            for key in ("additional_revenue", "reduced_costs", "additional_costs", "reduced_revenue")
        }
        net_change = (inputs["additional_revenue"] + inputs["reduced_costs"]) - (
            inputs["additional_costs"] + inputs["reduced_revenue"]
        )
        cumulative_change = np.cumsum(net_change)
        horizon = net_change.size

        result_df = pd.DataFrame(
            {
                "Period": np.arange(1, horizon + 1),
                "AdditionalRevenue": inputs["additional_revenue"],
                "ReducedCosts": inputs["reduced_costs"],
                "AdditionalCosts": inputs["additional_costs"],
                "ReducedRevenue": inputs["reduced_revenue"],
                "NetChange": net_change,
                "CumulativeNetChange": cumulative_change,
            }
        )

        self.om.add_variable("econ_pba_additional_revenue", inputs["additional_revenue"].tolist(), info_map)
        self.om.add_variable("econ_pba_reduced_costs", inputs["reduced_costs"].tolist(), info_map)
        self.om.add_variable("econ_pba_additional_costs", inputs["additional_costs"].tolist(), info_map)
        self.om.add_variable("econ_pba_reduced_revenue", inputs["reduced_revenue"].tolist(), info_map)
        self.om.add_variable("econ_pba_net_change", net_change.tolist(), info_map)
        self.om.add_variable("econ_pba_cumulative_net_change", cumulative_change.tolist(), info_map)
        self.om.add_variable("econ_pba_summary", result_df.to_dict(orient="list"), info_map)
        self.om.add_log("PartialBudget", "Partial budget analysis completed.", info_map)

    def _publish_single_outputs(self, info_map: Dict[str, str], derived_inputs: Dict[str, Any]) -> None:
        net_annual_cash_flow = self._to_array(derived_inputs.get("net_annual_cash_flow", 0.0))
        revenue_total = self._to_array(derived_inputs.get("revenue_total", 0.0))
        cost_total = self._to_array(derived_inputs.get("cost_total", 0.0))
        inputs = {
            "additional_revenue": self._to_array(0.0),
            "reduced_costs": self._to_array(0.0),
            "additional_costs": self._to_array(0.0),
            "reduced_revenue": self._to_array(0.0),
        }
        horizon = net_annual_cash_flow.size
        result_df = pd.DataFrame(
            {
                "Period": np.arange(1, horizon + 1),
                "RevenueTotal": revenue_total,
                "CostTotal": cost_total,
                "NetAnnualCashFlow": net_annual_cash_flow,
            }
        )
        self.om.add_variable("econ_pba_additional_revenue", inputs["additional_revenue"].tolist(), info_map)
        self.om.add_variable("econ_pba_reduced_costs", inputs["reduced_costs"].tolist(), info_map)
        self.om.add_variable("econ_pba_additional_costs", inputs["additional_costs"].tolist(), info_map)
        self.om.add_variable("econ_pba_reduced_revenue", inputs["reduced_revenue"].tolist(), info_map)
        self.om.add_variable("econ_pba_revenue_total", revenue_total.tolist(), info_map)
        self.om.add_variable("econ_pba_cost_total", cost_total.tolist(), info_map)
        self.om.add_variable("econ_pba_net_annual_cash_flow", net_annual_cash_flow.tolist(), info_map)
        self.om.add_variable("econ_pba_summary", result_df.to_dict(orient="list"), info_map)
        self.om.add_log("PartialBudget", "Partial budget analysis completed.", info_map)

    def _publish_fallback_outputs(self, info_map: Dict[str, str]) -> None:
        self.om.add_warning(
            "MissingPartialBudgetData",
            "No scenario-aware economics data was available to derive partial budget inputs.",
            info_map,
        )
        inputs = self._load_inputs()
        net_change = (inputs["additional_revenue"] + inputs["reduced_costs"]) - (
            inputs["additional_costs"] + inputs["reduced_revenue"]
        )
        cumulative_change = np.cumsum(net_change)
        horizon = net_change.size

        result_df = pd.DataFrame(
            {
                "Period": np.arange(1, horizon + 1),
                "AdditionalRevenue": inputs["additional_revenue"],
                "ReducedCosts": inputs["reduced_costs"],
                "AdditionalCosts": inputs["additional_costs"],
                "ReducedRevenue": inputs["reduced_revenue"],
                "NetChange": net_change,
                "CumulativeNetChange": cumulative_change,
            }
        )
        self.om.add_variable("econ_pba_additional_revenue", inputs["additional_revenue"].tolist(), info_map)
        self.om.add_variable("econ_pba_reduced_costs", inputs["reduced_costs"].tolist(), info_map)
        self.om.add_variable("econ_pba_additional_costs", inputs["additional_costs"].tolist(), info_map)
        self.om.add_variable("econ_pba_reduced_revenue", inputs["reduced_revenue"].tolist(), info_map)
        self.om.add_variable("econ_pba_net_change", net_change.tolist(), info_map)
        self.om.add_variable("econ_pba_cumulative_net_change", cumulative_change.tolist(), info_map)
        self.om.add_variable("econ_pba_summary", result_df.to_dict(orient="list"), info_map)
        self.om.add_log("PartialBudget", "Partial budget analysis completed.", info_map)

    # Supporting multi-year scenarios will require accumulating results across
    # scenarios as outlined in `Documentation of Economic Data and Analytical
    # Methods (2).pdf`.

    def _calculate_from_preprocessed(
        self, preprocessed_data: Dict[str, Dict[str, Dict[str, Any]]] | None
    ) -> Dict[str, Any] | None:
        """Compute partial budget inputs from preprocessed scenario data."""

        if not preprocessed_data:
            return None

        scenario_names: set[str] = set()
        items: list[tuple[str | None, Dict[str, Any], Dict[str, float]]] = []
        for section_data in preprocessed_data.values():
            if not isinstance(section_data, dict):
                continue
            for category_data in section_data.values():
                if not isinstance(category_data, dict):
                    continue
                for _, item in category_data.items():
                    if not isinstance(item, dict):
                        continue
                    line_items = item.get("line_item_values_by_scenario")
                    if not isinstance(line_items, dict):
                        continue
                    scenario_names.update(line_items.keys())
                    items.append((item.get("flow_type"), item, line_items))

        if len(scenario_names) == 1:
            return self._summarize_single_scenario(next(iter(scenario_names)), items)

        if len(scenario_names) < 2:
            return None

        baseline = self._pick_scenario(scenario_names, ["baseline", "base", "scenario_a", "a"])
        alternative = self._pick_scenario(scenario_names, ["alternative", "scenario", "scenario_b", "b", "alt"])
        if baseline is None:
            baseline = sorted(scenario_names)[0]
        if alternative is None:
            alternative = next(name for name in sorted(scenario_names) if name != baseline)

        info_map = {"class": __name__, "function": self._calculate_from_preprocessed.__name__}

        delta_components = self._accumulate_delta_components(items, baseline, alternative, info_map)

        if not any(delta_components.values()):
            return None

        return {
            "mode": "delta",
            "baseline": baseline,
            "alternative": alternative,
            **delta_components,
        }

    def calculate_partial_budget(self, preprocessed_data: Dict[str, Dict[str, Dict[str, Any]]] | None = None) -> None:
        """Perform a partial budget analysis and export multi-year net changes."""

        info_map = {
            "class": __name__,
            "function": self.calculate_partial_budget.__name__,
            "units": MeasurementUnits.DOLLARS,
        }
        derived_inputs = self._calculate_from_preprocessed(preprocessed_data)
        if derived_inputs and derived_inputs.get("mode") == "delta":
            self._publish_delta_outputs(info_map, derived_inputs)
            return

        if derived_inputs and derived_inputs.get("mode") == "single":
            self._publish_single_outputs(info_map, derived_inputs)
            return

        self._publish_fallback_outputs(info_map)

    def has_partial_budget_activity(
        self, preprocessed_data: Dict[str, Dict[str, Dict[str, Any]]] | None = None
    ) -> bool:
        """Return ``True`` when any partial budget inputs contain non-zero values."""
        derived_inputs = self._calculate_from_preprocessed(preprocessed_data)
        if derived_inputs and derived_inputs.get("mode") == "single":
            return bool(derived_inputs.get("net_annual_cash_flow"))
        if derived_inputs and derived_inputs.get("mode") == "delta":
            return any(
                derived_inputs.get(key, 0.0) != 0.0
                for key in ("additional_revenue", "reduced_revenue", "additional_costs", "reduced_costs")
            )

        return False
