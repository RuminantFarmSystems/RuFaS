"""Partial Budget Analysis (PBA) calculations."""

from __future__ import annotations

from typing import Any, Dict

import numpy as np
import pandas as pd

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits


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


def _load_inputs(im: InputManager) -> Dict[str, np.ndarray]:
    """Load and normalise PBA inputs from the ``InputManager``."""

    raw_inputs = {
        "additional_revenue": im.get_data("economics.partial_budget.additional_revenue"),
        "reduced_costs": im.get_data("economics.partial_budget.reduced_costs"),
        "additional_costs": im.get_data("economics.partial_budget.additional_costs"),
        "reduced_revenue": im.get_data("economics.partial_budget.reduced_revenue"),
    }

    arrays = {key: _to_array(value) for key, value in raw_inputs.items()}
    horizon = max(arr.size for arr in arrays.values()) or 1
    for key, arr in arrays.items():
        if arr.size < horizon:
            arrays[key] = np.pad(arr, (0, horizon - arr.size))
    return arrays


# Supporting multi-year scenarios will require accumulating results across
# scenarios as outlined in `Documentation of Economic Data and Analytical
# Methods (2).pdf`.


def calculate_partial_budget() -> None:
    """Perform a partial budget analysis and export multi-year net changes."""

    om = OutputManager()
    im = InputManager()

    info_map = {
        "class": __name__,
        "function": calculate_partial_budget.__name__,
        "units": MeasurementUnits.DOLLARS,
    }
    inputs = _load_inputs(im)

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

    om.add_variable("pba_net_change", net_change.tolist(), info_map)
    om.add_variable("pba_cumulative_net_change", cumulative_change.tolist(), info_map)
    om.add_variable("pba_summary", result_df.to_dict(orient="list"), info_map)
    om.add_variable("pba_net_change", [net_change], info_map)
    om.add_log("PartialBudget", "Partial budget analysis completed.", info_map)


def has_partial_budget_activity(im: InputManager | None = None) -> bool:
    """Return ``True`` when any partial budget inputs contain non-zero values."""

    manager = im or InputManager()
    arrays = _load_inputs(manager)
    return any(np.any(arr != 0.0) for arr in arrays.values())
