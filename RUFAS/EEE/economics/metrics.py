"""Utility functions for computing economic performance metrics."""

from __future__ import annotations

from typing import Iterable

import numpy as np


def calculate_roi(benefits: float, costs: float) -> float:
    """Return on Investment (ROI) as a percentage."""
    if costs == 0:
        return float("nan")
    return (benefits - costs) / costs * 100


def calculate_payback_period(cash_flows: Iterable[float]) -> float:
    """Compute the payback period from a sequence of annual cash flows."""
    cash_flows = np.asarray(list(cash_flows), dtype=float)
    cumulative = np.cumsum(cash_flows)
    for i, value in enumerate(cumulative):
        if value >= 0:
            if i == 0:
                return 0.0
            prev = cumulative[i - 1]
            if cash_flows[i] == 0:
                return float("inf")
            return (i - 1) + (-prev / cash_flows[i])
    return float("inf")


def calculate_net_annual_cash_flow(revenue: Iterable[float], costs: Iterable[float]) -> np.ndarray:
    """Return the net annual cash flow array (revenue minus costs)."""
    revenue_arr = np.asarray(list(revenue), dtype=float)
    cost_arr = np.asarray(list(costs), dtype=float)
    length = max(len(revenue_arr), len(cost_arr))
    if len(revenue_arr) < length:
        revenue_arr = np.pad(revenue_arr, (0, length - len(revenue_arr)))
    if len(cost_arr) < length:
        cost_arr = np.pad(cost_arr, (0, length - len(cost_arr)))
    return revenue_arr - cost_arr


# The true MPSP is obtained via goal seeking in the DCFROR analysis; this helper
# provides the simple ratio described in the documentation for quick estimates.


def calculate_mpsp(total_cost: float, total_output: float) -> float:
    """Return ``NaN`` because MPSP is solved via the DCFROR goal-seek workflow."""

    return float("nan")
