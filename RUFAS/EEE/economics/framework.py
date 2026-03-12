"""Entry points for economics calculations."""

from __future__ import annotations

import pandas as pd

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits
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

        cost_data = self.im.get_data("economic_inputs.capital_costs.capital_cost_breakdown")
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
        self.om.add_variable(
            "econ_preprocessed_economic_inputs",
            preprocessed_results,
            info_map={
                "class": __name__,
                "function": self.run_economic_analysis.__name__,
                "units": MeasurementUnits.UNITLESS,
            },
        )
        capital_present = self._capital_cost_present()
        partial_budget_requested = self.partial_budget.has_partial_budget_activity(preprocessed_results)

        if capital_present:
            calculator = DCFRORCalculator()

            calculator_inputs = calculator.inputs if isinstance(calculator.inputs, dict) else {}
            goal_seek_name_map = {
                "target_internal_rate_of_return": "internal_rate_of_return",
                "loan_term": "loan_term",
                "goal_seek_unit_price_multiplier": "goal_seek_unit_price_multiplier",
            }
            allowed_goal_seek_variables = set(goal_seek_name_map.keys())

            calculator.calculate()

            calculator_inputs = calculator.inputs if isinstance(calculator.inputs, dict) else {}
            if calculator_inputs.get("enable_goal_seek", False):
                fixed_variables = calculator_inputs.get("goal_seek_fixed_variables", [])
                if not isinstance(fixed_variables, list):
                    fixed_variables = []

                invalid_fixed = [name for name in fixed_variables if name not in allowed_goal_seek_variables]

                if invalid_fixed:
                    self.om.add_error(
                        "InvalidGoalSeekFixedVariables",
                        f"Unknown fixed goal-seek variable names: {invalid_fixed}",
                        {"class": __name__, "function": self.run_economic_analysis.__name__},
                    )
                    solved_value = float("nan")
                    solved_variable = ""
                elif len(fixed_variables) != 2:
                    self.om.add_error(
                        "GoalSeekFixedVariableCount",
                        "Exactly two fixed variables must be provided for goal-seek.",
                        {"class": __name__, "function": self.run_economic_analysis.__name__},
                    )
                    solved_value = float("nan")
                    solved_variable = ""
                else:
                    remaining = list(allowed_goal_seek_variables.difference(set(fixed_variables)))
                    if len(remaining) != 1:
                        self.om.add_error(
                            "GoalSeekSolveVariableInferenceFailed",
                            "Unable to infer a single variable to solve from fixed variables.",
                            {"class": __name__, "function": self.run_economic_analysis.__name__},
                        )
                        solved_value = float("nan")
                        solved_variable = ""
                    else:
                        solved_variable = remaining[0]
                        solved_value = calculator.goal_seek(
                            variable_name=goal_seek_name_map[solved_variable],
                            target_npv=float(calculator_inputs.get("goal_seek_target_npv", 0.0)),
                            bounds=tuple(calculator_inputs.get("goal_seek_bounds", [0.01, 100.0])),
                        )

                self.om.add_variable(
                    "econ_dcfror_goal_seek_solution",
                    solved_value,
                    info_map={
                        "class": __name__,
                        "function": self.run_economic_analysis.__name__,
                        "units": MeasurementUnits.UNITLESS,
                    },
                )
                self.om.add_variable(
                    "econ_dcfror_goal_seek_variable",
                    solved_variable,
                    info_map={
                        "class": __name__,
                        "function": self.run_economic_analysis.__name__,
                        "units": MeasurementUnits.UNITLESS,
                    },
                )

            if partial_budget_requested:
                self.partial_budget.calculate_partial_budget(preprocessed_results)
        else:
            self.partial_budget.calculate_partial_budget(preprocessed_results)
