"""Entry points for economics calculations."""

from __future__ import annotations

import pandas as pd

from RUFAS.input_manager import InputManager
from .dcfror import DCFRORCalculator
from .partial_budget import PartialBudget


class EconomicFramework:
    def __init__(self) -> None:
        self.im = InputManager()
        self.partial_budget = PartialBudget()

    @classmethod
    def run(cls) -> None:
        """Convenience entry point mirroring the legacy function API."""

        cls().run_economic_analysis()

    def _capital_cost_present(self, im: InputManager) -> bool:
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

    def run_economic_analysis(self) -> None:
        """Execute economic analysis using the Flexible Economic Framework."""

        capital_present = self._capital_cost_present(self.im)
        partial_budget_requested = self.partial_budget.has_partial_budget_activity()

        if capital_present:
            calculator = DCFRORCalculator()
            calculator.calculate()
            if partial_budget_requested:
                self.partial_budget.calculate_partial_budget()
        else:
            self.partial_budget.calculate_partial_budget()
