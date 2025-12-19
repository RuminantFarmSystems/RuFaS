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
        """Return ``True`` when the capital cost table is available.

        The calculation is still executed when all declared costs are zero so
        the economics module can emit outputs (and warnings) instead of
        silently skipping DCFROR altogether.
        """

        info_map = {"class": __name__, "function": self._capital_cost_present.__name__}

        if hasattr(self.im, "check_property_exists_in_pool"):
            try:
                if not self.im.check_property_exists_in_pool("capital_costs.capital_cost_breakdown"):
                    self.om.add_warning(
                        "MissingCapitalCostData",
                        "Capital cost breakdown not found in InputManager",
                        info_map,
                    )
                    return False
            except ValueError:
                self.om.add_warning(
                    "MissingCapitalCostData",
                    "Capital cost breakdown not found in InputManager",
                    info_map,
                )
                return False

        try:
            cost_data = self.im.get_data("capital_costs.capital_cost_breakdown")
        except Exception:
            self.om.add_warning(
                "MissingCapitalCostData",
                "Capital cost breakdown not found in InputManager",
                info_map,
            )
            return False
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
                if total_declared_costs == 0.0:
                    self.om.add_warning(
                        "ZeroCapitalCost",
                        "Capital cost breakdown sums to zero; continuing DCFROR with zero costs.",
                        info_map,
                    )
                return True

            numeric_columns = capital_cost_df.select_dtypes(include=["number"])
            has_numeric_columns = not numeric_columns.empty

            if not has_numeric_columns:
                return False

            numeric_values = numeric_columns.fillna(0.0).to_numpy()
            total_numeric_costs = float(numeric_values.sum())
            if total_numeric_costs == 0.0:
                self.om.add_warning(
                    "ZeroCapitalCost",
                    "Capital cost breakdown sums to zero; continuing DCFROR with zero costs.",
                    info_map,
                )
            return True

        is_iterable = hasattr(cost_data, "__iter__") and not isinstance(cost_data, (str, bytes))

        if is_iterable:
            iterable_values = list(cost_data)
            try:
                numeric_values = pd.to_numeric(pd.Series(iterable_values), errors="coerce").fillna(0.0)
            except Exception:
                return False
            iterable_total = float(numeric_values.sum())
            if iterable_total == 0.0:
                self.om.add_warning(
                    "ZeroCapitalCost",
                    "Capital cost breakdown sums to zero; continuing DCFROR with zero costs.",
                    info_map,
                )
            return True

        try:
            scalar_cost = float(cost_data)
        except (TypeError, ValueError):
            return False
        if scalar_cost == 0.0:
            self.om.add_warning(
                "ZeroCapitalCost",
                "Capital cost breakdown sums to zero; continuing DCFROR with zero costs.",
                info_map,
            )
        return True

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
