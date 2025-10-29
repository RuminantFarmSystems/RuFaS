"""Entry points for economics calculations."""

from __future__ import annotations

import pandas as pd

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from .dcfror import DCFRORCalculator
from .partial_budget import PartialBudget
from .preprocessing import EconomicPreprocessor


class EconomicFramework:
    def __init__(self) -> None:
        self.im = InputManager()
        self.om = OutputManager()
        self.partial_budget = PartialBudget()
        self.preprocessor = EconomicPreprocessor()

    def _capital_cost_present(self) -> bool:
        """Return ``True`` when the capital cost table contains any value > 0."""

        cost_data = self.im.get_data("capital_costs.capital_cost_breakdown")
        is_dataframe = isinstance(cost_data, pd.DataFrame)

        if is_dataframe:
            capital_cost_df = cost_data
            has_cost_column = "Cost" in capital_cost_df.columns
            dataframe_is_empty = capital_cost_df.empty

            if dataframe_is_empty:
                return False

            if has_cost_column:
                declared_costs = capital_cost_df["Cost"]
                numeric_costs = pd.to_numeric(declared_costs, errors="coerce").fillna(0.0)
                total_declared_costs = float(numeric_costs.sum())
                return total_declared_costs > 0.0

            numeric_columns = capital_cost_df.select_dtypes(include=["number"])
            has_numeric_columns = not numeric_columns.empty

            if not has_numeric_columns:
                return False

            numeric_values = numeric_columns.fillna(0.0).to_numpy()
            total_numeric_costs = float(numeric_values.sum())
            return total_numeric_costs > 0.0

        is_iterable = hasattr(cost_data, "__iter__") and not isinstance(cost_data, (str, bytes))

        if is_iterable:
            iterable_values = list(cost_data)
            try:
                numeric_values = pd.to_numeric(pd.Series(iterable_values), errors="coerce").fillna(0.0)
            except Exception:
                return False
            iterable_total = float(numeric_values.sum())
            return iterable_total > 0.0

        try:
            scalar_cost = float(cost_data)
        except (TypeError, ValueError):
            return False
        return scalar_cost > 0.0

    def run_economic_analysis(self) -> None:
        """Execute economic analysis using the Flexible Economic Framework."""

        preprocessed_results = self.preprocessor.preprocess()
        capital_present = self._capital_cost_present()
        partial_budget_requested = self.partial_budget.has_partial_budget_activity()

        if capital_present:
            calculator = DCFRORCalculator()
            calculator.calculate(preprocessed_results)
            if partial_budget_requested:
                self.partial_budget.calculate_partial_budget(preprocessed_results)
        else:
            self.partial_budget.calculate_partial_budget(preprocessed_results)


