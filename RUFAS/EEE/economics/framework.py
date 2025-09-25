"""Entry points for economics calculations."""

from __future__ import annotations

import pandas as pd

from RUFAS.input_manager import InputManager
from .dcfror import DCFRORCalculator
from .partial_budget import calculate_partial_budget, has_partial_budget_activity


def _capital_cost_present(im: InputManager) -> bool:
    """Return ``True`` if any capital cost is defined."""

    cost_df = im.get_data("capital_costs.capital_cost_breakdown")
    if isinstance(cost_df, pd.DataFrame) and not cost_df.empty:
        try:
            return float(cost_df.get("Cost", cost_df.sum()).sum()) > 0
        except Exception:
            return cost_df.sum().sum() > 0
    try:
        return float(cost_df) > 0
    except Exception:
        return False


def run_economic_analysis() -> None:
    """Execute economic analysis using the Flexible Economic Framework."""

    im = InputManager()
    capital_present = _capital_cost_present(im)
    partial_budget_requested = has_partial_budget_activity(im)

    if capital_present:
        calculator = DCFRORCalculator()
        calculator.calculate()
        if partial_budget_requested:
            calculate_partial_budget()
    else:
        calculate_partial_budget()
