from typing import Any, Dict, Tuple
import pandas as pd
import numpy as np
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager


# NOTE: ``dcfror.py`` is the maintained implementation described in
# `RuFaS_Economics_Module_Overview_Slides.pdf`. This duplicate remains for
# legacy compatibility and will be removed once users migrate to the dedicated
# module.


class DCFRORCalculator:
    """
    A class to compute the Discounted Cash Flow Rate of Return (DCFROR) analysis for RuFaS.
    """

    def __init__(self):
        self.im = InputManager()
        self.om = OutputManager()
        self.inputs = self._load_inputs()

    def _load_inputs(self) -> Dict[str, Any]:
        info_map = {"class": self.__class__.__name__, "function": self._load_inputs.__name__}
        try:
            inputs: Dict[str, Any] = {
                "cost_capital_multiple": self.im.get_data("capital_costs.capital_cost_breakdown"),
                "cost_operational_units": self.im.get_data("cashflow_inputs.operating_units"),
                "cost_operational_unit_cost": self.im.get_data("cashflow_inputs.operating_unit_costs"),
                "units_produced": self.im.get_data("cashflow_inputs.units_produced"),
                "unit_cost": self.im.get_data("cashflow_inputs.unit_price"),
                "loan_interest_rate": self.im.get_data("cashflow_inputs.loan_interest_rate"),
                "loan_term": self.im.get_data("cashflow_inputs.loan_term"),
                "loan_amount": self.im.get_data("cashflow_inputs.loan_fraction"),
                "equity_amount": self.im.get_data("cashflow_inputs.equity"),
                "interest_rate_construction": self.im.get_data("cashflow_inputs.const_int"),
                "construction_term": self.im.get_data("cashflow_inputs.const_term"),
                "construction_finish_pcts": self.im.get_data("cashflow_inputs.const_rate_i"),
                "tax_rate": self.im.get_data("cashflow_inputs.tax_rate"),
                "internal_rate_of_return": self.im.get_data("cashflow_inputs.target_internal_rate_of_return"),
                "project_term": self.im.get_data("cashflow_inputs.project_term"),
                "depreciation_rate": np.array(self.im.get_data("cashflow_inputs.depreciation_i")),
                "enable": self.im.get_data("cashflow_inputs.enable_dcfror"),
                "tax_credit_used": self.im.get_data("cashflow_inputs.tax_credit_used"),
                "tax_credit_revenue": self.im.get_data("cashflow_inputs.tax_credit_revenue"),
            }
            inputs["cost_capital_multiple"].set_index("Item", inplace=True)
            return inputs
        except KeyError as e:
            self.om.add_error("MissingInputKey", f"Missing input key: {str(e)}", info_map)
            raise

    def calculate(self) -> None:
        """
        Main function to execute DCFROR calculation and export results.
        """
        info_map = {"class": self.__class__.__name__, "function": self.calculate.__name__}

        if not self.inputs.get("enable", False):
            self.om.add_log("DCFROR calculation skipped due to configuration flag.", info_map)
            return

        self.om.add_log("Starting DCFROR calculation", info_map)

        try:
            cost_inputs = self._prepare_costs()
            financing = self._prepare_financing()
            cash_flows, cash_flow_df = self._compute_cash_flows(**cost_inputs, **financing)
            self._export_results(cash_flows, cash_flow_df, financing["internal_rate_of_return"])
        except Exception as e:
            self.om.add_error("DCFRORCalculationFailed", f"DCFROR calculation failed: {str(e)}", info_map)
            raise

    def _prepare_costs(self) -> Dict[str, Any]:
        """
        Calculate total capital cost including construction interest, and extract revenue and cost arrays.

        Returns
        -------
        dict
            Dictionary containing project term, capital cost, revenue array, and operating cost array.
        """
        info_map = {"class": self.__class__.__name__, "function": self._prepare_costs.__name__}

        cap_breakdown = self.inputs["cost_capital_multiple"]
        if cap_breakdown.empty:
            self.om.add_warning("EmptyCapitalCostBreakdown", "Capital cost breakdown is empty", info_map)

        base_cost = cap_breakdown["Cost"].sum()
        if base_cost == 0:
            self.om.add_warning("ZeroCapitalCost", "Total capital cost is zero", info_map)

        interest_rate = self.inputs["interest_rate_construction"]
        construction_years = self.inputs["construction_term"]
        finish_percentages = self.inputs["construction_finish_pcts"]

        annual_expenditures = [base_cost * finish_percentages[i] for i in range(construction_years)]
        interest_charges = [sum(annual_expenditures[: i + 1]) * interest_rate for i in range(construction_years)]
        capital_cost = base_cost + sum(interest_charges)

        operating_costs = (self.inputs["cost_operational_units"] * self.inputs["cost_operational_unit_cost"]).sum(
            axis=0
        )
        revenue = (self.inputs["units_produced"] * self.inputs["unit_cost"]).sum(axis=0)

        project_term = self.inputs["project_term"]
        if project_term <= 0:
            self.om.add_error("InvalidProjectTerm", "Project term must be positive.", info_map)
            raise ValueError("Project term must be positive.")

        return {
            "project_term": project_term,
            "capital_cost": capital_cost,
            "revenue": revenue[:project_term],
            "operating_costs": operating_costs[:project_term],
        }

    def _prepare_financing(self) -> Dict[str, Any]:
        """
        Extract financing parameters for depreciation, loan, and tax.

        Returns
        -------
        dict
            Dictionary of financing parameters.
        """
        input_dict = self.inputs
        depreciation_rate = input_dict["depreciation_rate"]
        depreciation_rate = depreciation_rate[~np.isnan(depreciation_rate)]
        return {
            "depreciation_rate": depreciation_rate,
            "dep_term": len(depreciation_rate),
            "loan_interest_rate": input_dict["loan_interest_rate"],
            "loan_term": input_dict["loan_term"],
            "loan_amount": input_dict["loan_amount"],
            "equity_amount": input_dict["equity_amount"],
            "tax_rate": input_dict["tax_rate"],
            "internal_rate_of_return": input_dict["internal_rate_of_return"],
        }

    def _compute_cash_flows(
        self,
        project_term: int,
        capital_cost: float,
        depreciation_rate: np.ndarray,
        dep_term: int,
        loan_interest_rate: float,
        loan_term: int,
        loan_amount: float,
        equity_amount: float,
        revenue: np.ndarray,
        operating_costs: np.ndarray,
        tax_rate: float,
    ) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Compute annual cash flows and build a DataFrame with financial details.

        Returns
        -------
        cash_flows : np.ndarray
            Net cash flows over the project term.
        cash_flow_df : pd.DataFrame
            DataFrame containing detailed breakdown for each year.
        """
        operating_expense = np.zeros(project_term)
        depreciation = np.zeros(project_term)
        debt_payment = np.zeros(project_term)
        interest_payment = np.zeros(project_term)
        earnings_before_tax = np.zeros(project_term)
        tax_paid = np.zeros(project_term)
        net_income = np.zeros(project_term)
        net_cash_flow = np.zeros(project_term)

        annual_depreciation = np.zeros(project_term)
        for i in range(min(dep_term, project_term)):
            annual_depreciation[i] = depreciation_rate[i] * capital_cost

        debt_total = loan_amount * capital_cost
        annual_debt_payment = np.pmt(loan_interest_rate, loan_term, -debt_total) if loan_term > 0 else 0

        carry_forward_limit = 0.8
        losses_forward = 0.0

        for t in range(project_term):
            op_exp = operating_costs[t] if t < len(operating_costs) else 0
            depr = annual_depreciation[t] if t < len(annual_depreciation) else 0
            dp = annual_debt_payment if t < loan_term else 0
            ip = loan_interest_rate * (debt_total - np.sum(debt_payment[:t])) if t < loan_term else 0

            operating_expense[t] = op_exp
            depreciation[t] = depr
            debt_payment[t] = dp
            interest_payment[t] = ip

            earnings_before_tax[t] = revenue[t] - op_exp - depr - dp - ip

            if earnings_before_tax[t] <= 0:
                losses_forward += earnings_before_tax[t]
                taxable_income = 0
            else:
                usable_loss = min(-losses_forward * carry_forward_limit, earnings_before_tax[t])
                taxable_income = earnings_before_tax[t] - usable_loss
                losses_forward += -usable_loss

            tax_paid[t] = tax_rate * taxable_income
            net_income[t] = earnings_before_tax[t] - tax_paid[t]
            net_cash_flow[t] = net_income[t] + depr

        cash_flow_df = pd.DataFrame(
            {
                "Year": np.arange(1, project_term + 1),
                "Revenue": revenue,
                "Operating Cost": operating_expense,
                "Depreciation": depreciation,
                "Debt Payment": debt_payment,
                "Interest": interest_payment,
                "EBT": earnings_before_tax,
                "Taxes": tax_paid,
                "Net Income": net_income,
                "Cash Flow": net_cash_flow,
            }
        )

        return net_cash_flow, cash_flow_df

    def _export_results(self, CF: np.ndarray, cash_flow_df: pd.DataFrame, internal_rate_of_return: float) -> None:
        """
        Export results to the OutputManager.

        Parameters
        ----------
        CF : np.ndarray
            Net cash flows.
        cash_flow_df : pd.DataFrame
            Detailed cash flow breakdown.
        internal_rate_of_return : float
            Internal Rate of Return.
        """
        info_map = {"class": self.__class__.__name__, "function": self.calculate.__name__}
        npv = np.npv(internal_rate_of_return, CF)
        self.om.add_variable("dcfror_npv", npv, info_map)
        self.om.add_variable("dcfror_cash_flow_summary", cash_flow_df.to_dict(orient="list"), info_map)
        self.om.add_log("DCFROR calculation completed successfully.", info_map)

    def goal_seek(
        self,
        variable_name: str,
        target_npv: float = 0.0,
        bounds: Tuple[float, float] = (0.01, 100.0),
        tol: float = 1e-6,
        max_iter: int = 100,
    ) -> float:
        """
        Iteratively adjusts the specified input variable to achieve the target NPV using binary search.

        Parameters
        ----------
        variable_name : str
            The name of the input variable to adjust.
        target_npv : float, optional
            The desired net present value (NPV), by default 0.0.
        bounds : Tuple[float, float], optional
            Lower and upper bounds for the multiplier applied to the variable, by default (0.01, 100.0).
        tol : float, optional
            Tolerance for convergence, by default 1e-6.
        max_iter : int, optional
            Maximum number of iterations to try, by default 100.

        Returns
        -------
        float
            The multiplier that achieves the target NPV within tolerance. Returns NaN if not found.
        """
        info_map = {"class": self.__class__.__name__, "function": self.goal_seek.__name__}
        low, high = bounds

        for _ in range(max_iter):
            mid = (low + high) / 2
            override_inputs = {variable_name: self.inputs[variable_name] * mid}
            self.calculate(override_inputs=override_inputs)
            npv_result = self.om.filter_variables_pool(
                {
                    "name": "NPV Retrieval",
                    "description": "Retrieve the latest DCFROR NPV for goal seek.",
                    "filters": [f"{self.__class__.__name__}.{self.calculate.__name__}.dcfror_npv"],
                }
            )
            npv = npv_result.get(
                f"{self.__class__.__name__}.{self.calculate.__name__}.dcfror_npv",
                None,
            )

            if npv is None:
                self.om.add_error(
                    "NPVNotFound",
                    "NPV not found after DCFROR calculation. Check calculation logic.",
                    info_map,
                )
                return float("nan")

            if abs(npv - target_npv) < tol:
                return mid
            elif npv > target_npv:
                high = mid
            else:
                low = mid

        self.om.add_error(
            "GoalSeekFailed", "Goal seek did not converge within the maximum number of iterations.", info_map
        )
        return float("nan")


# Hook: Call DCFROR in EEE_manager.py
if __name__ == "__main__":
    try:
        dcfror = DCFRORCalculator()
        dcfror.calculate()
    except Exception as e:
        OutputManager().add_error(f"DCFROR main execution failed: {str(e)}", {"script": "EEE_manager.py"})
