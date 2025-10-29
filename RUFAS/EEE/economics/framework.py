"""Entry points for economics calculations."""

from __future__ import annotations

from typing import Callable

import pandas as pd

from RUFAS.input_manager import InputManager
from .dcfror import DCFRORCalculator
from .partial_budget import PartialBudget
from .preprocessing import EconomicPreprocessor


class EconomicFramework:
    """Coordinator for DCFROR and partial budget economic routines."""

    def __init__(
        self,
        input_manager: InputManager | None = None,
        preprocessor_factory: Callable[[], EconomicPreprocessor] | None = None,
        dcfror_factory: Callable[[], DCFRORCalculator] | None = None,
        partial_budget_factory: Callable[[], PartialBudget] | None = None,
    ) -> None:
        self.im = input_manager or InputManager()
        self._preprocessor_factory = preprocessor_factory or EconomicPreprocessor
        self._dcfror_factory = dcfror_factory or DCFRORCalculator
        self._partial_budget_factory = partial_budget_factory or PartialBudget

    def _capital_cost_present(self) -> bool:
        """Return ``True`` if any capital cost is defined."""

        cost_df = self.im.get_data("capital_costs.capital_cost_breakdown")
        if isinstance(cost_df, pd.DataFrame) and not cost_df.empty:
            try:
                return float(cost_df.get("Cost", cost_df.sum()).sum()) > 0
            except Exception:
                return cost_df.sum().sum() > 0
        try:
            return float(cost_df) > 0
        except Exception:
            return False

    def _run_partial_budget(self, partial_budget: PartialBudget) -> None:
        """Execute the Partial Budget Analysis workflow."""

        partial_budget.calculate_partial_budget()

    def run_economic_analysis(self) -> None:
        """Execute economic analysis using the Flexible Economic Framework."""

        try:
            self._preprocessor_factory().preprocess()
        except KeyError:
            # Missing preprocessing metadata should not prevent downstream
            # economics routines from running. The preprocessor logs the
            # failure via the OutputManager, so we can safely proceed.
            pass
        capital_present = self._capital_cost_present()

        partial_budget = self._partial_budget_factory()
        partial_budget_requested = partial_budget.has_partial_budget_activity()

        if capital_present:
            calculator = self._dcfror_factory()
            calculator.calculate()
            if partial_budget_requested:
                self._run_partial_budget(partial_budget)
        else:
            self._run_partial_budget(partial_budget)

    @classmethod
    def run(cls) -> None:
        """Convenience wrapper for executing the economics framework."""

        cls().run_economic_analysis()


__all__ = ["EconomicFramework"]
