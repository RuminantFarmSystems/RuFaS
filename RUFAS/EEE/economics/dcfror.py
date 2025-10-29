from __future__ import annotations

from typing import Any, Dict, Iterable, Tuple

import numpy as np
import pandas as pd

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager

from .equations import (
    annual_capital_spent,
    annual_cash_income,
    annual_loan_payment,
    construct_timeline,
    construction_interest,
    depreciation_schedule,
    discount_factor,
    equity_contribution,
    income_tax,
    interest_payment,
    loan_principal,
    loss_carry_forward,
    net_present_value,
    net_revenue,
    npv_capital_plus_interest,
    present_value,
    principal_after_payment,
    taxable_income,
)
from .metrics import calculate_mpsp, calculate_net_annual_cash_flow, calculate_payback_period, calculate_roi


class DCFRORCalculator:
    """Compute the Discounted Cash Flow Rate of Return (DCFROR) analysis."""

    def __init__(self) -> None:
        self.im = InputManager()
        self.om = OutputManager()
        self.inputs = self._load_inputs()

    def _load_inputs(self) -> Dict[str, Any]:
        info_map = {"class": self.__class__.__name__, "function": self._load_inputs.__name__}
        try:
            # Retrieve input data
            loan_term = self.im.get_data("cashflow_inputs.loan_term")
            project_term = self.im.get_data("cashflow_inputs.project_term")
            if loan_term > project_term:
                # Loan duration should not exceed the project lifetime
                self.om.add_warning(
                    "LoanTermAdjusted",
                    "Loan term longer than project term; using project term instead.",
                    info_map,
                )
                loan_term = project_term

            inputs: Dict[str, Any] = {
                "cost_capital_multiple": self.im.get_data("capital_costs.capital_cost_breakdown"),
                "cost_operational_units": self.im.get_data("cashflow_inputs.operating_units"),
                "cost_operational_unit_cost": self.im.get_data("cashflow_inputs.operating_unit_costs"),
                "units_produced": self.im.get_data("cashflow_inputs.units_produced"),
                "unit_cost": self.im.get_data("cashflow_inputs.unit_price"),
                "loan_interest_rate": self.im.get_data("cashflow_inputs.loan_interest_rate"),
                # Loan term is capped to the project term above per the
                # guidance in `Documentation of Economic Data and Analytical
                # Methods (2).pdf`.
                "loan_term": loan_term,
                "loan_amount": self.im.get_data("cashflow_inputs.loan_fraction"),
                "equity_amount": self.im.get_data("cashflow_inputs.equity"),
                "interest_rate_construction": self.im.get_data("cashflow_inputs.const_int"),
                "construction_term": self.im.get_data("cashflow_inputs.const_term"),
                "construction_finish_pcts": self.im.get_data("cashflow_inputs.const_rate_i"),
                "tax_rate": self.im.get_data("cashflow_inputs.tax_rate"),
                "internal_rate_of_return": self.im.get_data("cashflow_inputs.target_internal_rate_of_return"),
                "project_term": project_term,
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

    def calculate(
        self, preprocessed_data: Dict[str, Dict[str, Dict[str, float | None]]] | None = None
    ) -> None:
        """Run the DCFROR calculation and export results."""

        info_map = {"class": self.__class__.__name__, "function": self.calculate.__name__}

        if not self.inputs.get("enable", False):
            self.om.add_log("DCFROR calculation skipped due to configuration flag.", info_map)
            return

        self.om.add_log("Starting DCFROR calculation", info_map)

        try:
            cost_inputs = self._prepare_costs()
            financing = self._prepare_financing(cost_inputs["project_term"])
            cash_flows, cash_flow_df = self._compute_cash_flows(
                **cost_inputs,
                **financing,
            )
            self._export_results(
                cash_flows,
                cash_flow_df,
                financing["internal_rate_of_return"],
                cost_inputs["capital_cost"],
                cost_inputs["revenue"],
                cost_inputs["operating_costs"],
            )
        except Exception as exc:
            self.om.add_error("DCFRORCalculationFailed", f"DCFROR calculation failed: {exc}", info_map)
            raise

    def _prepare_costs(self) -> Dict[str, Any]:
        """Collect project term, capital cost, and operating schedules."""

        info_map = {"class": self.__class__.__name__, "function": self._prepare_costs.__name__}

        cap_breakdown = self.inputs["cost_capital_multiple"]
        if isinstance(cap_breakdown, pd.DataFrame) and cap_breakdown.empty:
            self.om.add_warning("EmptyCapitalCostBreakdown", "Capital cost breakdown is empty", info_map)

        base_cost = float(np.asarray(cap_breakdown["Cost"], dtype=float).sum())
        if base_cost == 0:
            self.om.add_warning("ZeroCapitalCost", "Total capital cost is zero", info_map)

        interest_rate = self.inputs["interest_rate_construction"]
        # The construction-period financing uses the dedicated
        # ``interest_rate_construction`` input (IRCon in the documentation).
        construction_years = int(self.inputs["construction_term"])
        finish_percentages = self.inputs["construction_finish_pcts"]

        def _to_numpy(values: Any) -> np.ndarray:
            if isinstance(values, pd.DataFrame):
                return values.to_numpy(dtype=float)
            return np.asarray(values, dtype=float)

        operating_units = _to_numpy(self.inputs["cost_operational_units"])
        operating_unit_costs = _to_numpy(self.inputs["cost_operational_unit_cost"])
        revenue_units = _to_numpy(self.inputs["units_produced"])
        revenue_prices = _to_numpy(self.inputs["unit_cost"])

        # Interest accrued during construction should be accounted for in cash
        # flow calculations, not added to the depreciable capital cost.
        # Construction interest is accounted for later in the cash-flow stage
        # (Step 3 in `Documentation of Economic Data and Analytical Methods
        # (2).pdf`), so it does not increase the depreciable capital cost.
        capital_cost = base_cost
        operating_costs = np.asarray((operating_units * operating_unit_costs).sum(axis=0), dtype=float)
        revenue = np.asarray((revenue_units * revenue_prices).sum(axis=0), dtype=float)

        project_term = int(self.inputs["project_term"])
        if project_term <= 0:
            self.om.add_error("InvalidProjectTerm", "Project term must be positive.", info_map)
            raise ValueError("Project term must be positive.")

        return {
            "project_term": project_term,
            "capital_cost": base_cost,
            "construction_term": construction_years,
            "construction_rates": list(np.asarray(finish_percentages, dtype=float)),
            "revenue": revenue[:project_term],
            "operating_costs": operating_costs[:project_term],
        }

    def _prepare_financing(self, project_term: int) -> Dict[str, Any]:
        """Normalise the financing inputs used in the cash flow model."""

        input_dict = self.inputs
        depreciation_rate = input_dict["depreciation_rate"]
        depreciation_rate = depreciation_rate[~np.isnan(depreciation_rate)]

        equity_share_input = input_dict.get("equity_amount")
        financed_share_input = input_dict.get("loan_amount")
        financed_share = float(financed_share_input) if financed_share_input is not None else None
        equity_share = float(equity_share_input) if equity_share_input is not None else None

        if financed_share is None and equity_share is not None:
            financed_share = max(0.0, min(1.0, 1.0 - equity_share))
        if equity_share is None and financed_share is not None:
            equity_share = max(0.0, min(1.0, 1.0 - financed_share))

        if financed_share is None:
            financed_share = 1.0
        if equity_share is None:
            equity_share = max(0.0, min(1.0, 1.0 - financed_share))

        loan_term = int(input_dict["loan_term"])
        if loan_term > project_term:
            loan_term = project_term

        return {
            "depreciation_rate": depreciation_rate,
            "dep_term": len(depreciation_rate),
            "loan_interest_rate": float(input_dict["loan_interest_rate"]),
            "loan_term": loan_term,
            "financed_share": financed_share,
            "equity_share": equity_share,
            "construction_interest_rate": float(input_dict["interest_rate_construction"]),
            "tax_rate": float(input_dict["tax_rate"]),
            "internal_rate_of_return": float(input_dict["internal_rate_of_return"]),
        }

    def _compute_cash_flows(
        self,
        project_term: int,
        capital_cost: float,
        construction_term: int,
        construction_rates: Iterable[float],
        depreciation_rate: np.ndarray,
        dep_term: int,
        loan_interest_rate: float,
        loan_term: int,
        financed_share: float,
        equity_share: float,
        construction_interest_rate: float,
        revenue: np.ndarray,
        operating_costs: np.ndarray,
        tax_rate: float,
        internal_rate_of_return: float,
    ) -> Tuple[np.ndarray, pd.DataFrame]:
        """Build the annual cash flow table using Equations 7–26."""

        years = construct_timeline(construction_term, loan_term, project_term)
        n_years = years.size
        construction_mask = years <= 0
        operational_mask = years >= 1
        discount_factors = np.array(
            [discount_factor(internal_rate_of_return, year) for year in years],
            dtype=float,
        )

        n_construction = int(construction_mask.sum())
        rates = np.asarray(list(construction_rates), dtype=float)
        if n_construction:
            if rates.size < n_construction:
                rates = np.pad(rates, (0, n_construction - rates.size))
            rates = rates[:n_construction]
            if not np.allclose(rates.sum(), 1.0) and rates.sum() > 0:
                rates = rates / rates.sum()
            capital_schedule = annual_capital_spent(capital_cost, rates)
            equity_schedule = equity_contribution(capital_cost, rates, equity_share)
            loan_draw_schedule = capital_schedule * financed_share
            construction_interest_cost = construction_interest(loan_draw_schedule, construction_interest_rate)
            capital_interest_pv = np.zeros(n_years, dtype=float)
            capital_interest_pv[construction_mask] = npv_capital_plus_interest(
                capital_schedule,
                construction_interest_cost,
                internal_rate_of_return,
                years[construction_mask],
            )
            cumulative_draw = np.cumsum(loan_draw_schedule)
        else:
            capital_schedule = np.zeros(0, dtype=float)
            equity_schedule = np.zeros(0, dtype=float)
            loan_draw_schedule = np.zeros(0, dtype=float)
            construction_interest_cost = np.zeros(0, dtype=float)
            capital_interest_pv = np.zeros(n_years, dtype=float)
            cumulative_draw = np.zeros(0, dtype=float)

        annual_depreciation = depreciation_schedule(capital_cost, depreciation_rate)
        if dep_term and dep_term < annual_depreciation.size:
            annual_depreciation = annual_depreciation[:dep_term]

        op_years = int(operational_mask.sum())
        revenue_schedule = np.zeros(op_years, dtype=float)
        operating_schedule = np.zeros(op_years, dtype=float)
        depreciation_schedule_op = np.zeros(op_years, dtype=float)
        revenue_schedule[: min(len(revenue), op_years)] = revenue[:op_years]
        operating_schedule[: min(len(operating_costs), op_years)] = operating_costs[:op_years]
        depreciation_schedule_op[: min(len(annual_depreciation), op_years)] = annual_depreciation[:op_years]

        loan_payment = annual_loan_payment(capital_cost, loan_interest_rate, loan_term, financed_share)
        principal_balance = capital_cost * financed_share

        capital_column = np.zeros(n_years, dtype=float)
        loan_draw_column = np.zeros(n_years, dtype=float)
        construction_interest_column = np.zeros(n_years, dtype=float)
        revenue_column = np.zeros(n_years, dtype=float)
        operating_column = np.zeros(n_years, dtype=float)
        depreciation_column = np.zeros(n_years, dtype=float)
        loan_payment_column = np.zeros(n_years, dtype=float)
        interest_column = np.zeros(n_years, dtype=float)
        net_revenue_column = np.zeros(n_years, dtype=float)
        loss_forward_column = np.zeros(n_years, dtype=float)
        taxable_income_column = np.zeros(n_years, dtype=float)
        income_tax_column = np.zeros(n_years, dtype=float)
        cash_income_column = np.zeros(n_years, dtype=float)
        present_value_column = np.zeros(n_years, dtype=float)
        loan_balance_column = np.zeros(n_years, dtype=float)

        cash_flows = np.zeros(n_years, dtype=float)
        if n_construction:
            construction_indices = np.where(construction_mask)[0]
            capital_column[construction_indices] = capital_schedule
            loan_draw_column[construction_indices] = loan_draw_schedule
            construction_interest_column[construction_indices] = construction_interest_cost
            cash_flows[construction_indices] = -(equity_schedule + construction_interest_cost)
            loan_balance_column[construction_indices] = cumulative_draw

        prev_taxable = 0.0
        op_indices = np.where(operational_mask)[0]
        for idx, year_index in enumerate(op_indices):
            revenue_y = revenue_schedule[idx]
            operating_y = operating_schedule[idx]
            depreciation_y = depreciation_schedule_op[idx]
            loan_pay_y = loan_payment if idx < loan_term else 0.0
            interest_y = (
                interest_payment(principal_balance, loan_interest_rate)
                if financed_share > 0 and idx < loan_term
                else 0.0
            )

            if idx < loan_term:
                principal_balance = max(
                    0.0,
                    EconomicEquations.principal_after_payment(principal_balance, loan_pay_y, interest_y),
                )

            net_rev_y = EconomicEquations.net_revenue(revenue_y, operating_y, interest_y, depreciation_y)
            carried_loss = EconomicEquations.loss_carry_forward(prev_taxable)
            taxable_y = EconomicEquations.taxable_income(net_rev_y, carried_loss)
            tax_y = EconomicEquations.income_tax(taxable_y, tax_rate)
            cash_income_y = EconomicEquations.annual_cash_income(revenue_y, operating_y, loan_pay_y, tax_y)
            pv_y = EconomicEquations.present_value(cash_income_y, discount_factors[year_index])

            revenue_column[year_index] = revenue_y
            operating_column[year_index] = operating_y
            depreciation_column[year_index] = depreciation_y
            loan_payment_column[year_index] = loan_pay_y
            interest_column[year_index] = interest_y
            net_revenue_column[year_index] = net_rev_y
            loss_forward_column[year_index] = carried_loss
            taxable_income_column[year_index] = taxable_y
            income_tax_column[year_index] = tax_y
            cash_income_column[year_index] = cash_income_y
            present_value_column[year_index] = pv_y
            loan_balance_column[year_index] = principal_balance
            cash_flows[year_index] = cash_income_y
            prev_taxable = taxable_y

        cash_flow_df = pd.DataFrame(
            {
                "Year": years,
                "DiscountFactor": discount_factors,
                "Capital": capital_column,
                "LoanPrincipalDraw": loan_draw_column,
                "ConstructionInterest": construction_interest_column,
                "Revenue": revenue_column,
                "OperatingCost": operating_column,
                "LoanPayment": loan_payment_column,
                "InterestPayment": interest_column,
                "Depreciation": depreciation_column,
                "NetRevenue": net_revenue_column,
                "LossesForward": loss_forward_column,
                "TaxableIncome": taxable_income_column,
                "IncomeTax": income_tax_column,
                "CashIncome": cash_income_column,
                "PresentValue": present_value_column,
                "NPVCapitalPlusInterest": capital_interest_pv,
                "LoanBalance": loan_balance_column,
            }
        )

        return cash_flows, cash_flow_df

    def _export_results(
        self,
        CF: np.ndarray,
        cash_flow_df: pd.DataFrame,
        internal_rate_of_return: float,
        capital_cost: float,
        revenue: np.ndarray,
        operating_costs: np.ndarray,
    ) -> None:
        """Summarise and export the DCFROR results."""

        info_map = {"class": self.__class__.__name__, "function": self.calculate.__name__}

        construction_mask = cash_flow_df["Year"] <= 0
        operational_mask = cash_flow_df["Year"] >= 1
        npv = net_present_value(
            cash_flow_df.loc[operational_mask, "PresentValue"].to_numpy(),
            cash_flow_df.loc[construction_mask, "NPVCapitalPlusInterest"].to_numpy(),
        )

        positive_benefits = float(CF[CF > 0].sum())
        investment_costs = float(-CF[CF < 0].sum())
        roi = calculate_roi(positive_benefits, investment_costs)
        payback = calculate_payback_period(CF)
        net_cash_flow = calculate_net_annual_cash_flow(revenue, operating_costs)
        mpsp = calculate_mpsp(capital_cost + operating_costs.sum(), revenue.sum())

        self.om.add_variable("dcfror_npv", npv, info_map)
        self.om.add_variable("dcfror_roi", roi, info_map)
        self.om.add_variable("dcfror_payback_period", payback, info_map)
        self.om.add_variable("dcfror_net_cash_flow", net_cash_flow.tolist(), info_map)
        self.om.add_variable("dcfror_mpsp", mpsp, info_map)
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
        """Binary search utility for future goal-seek integrations."""

        info_map = {"class": self.__class__.__name__, "function": self.goal_seek.__name__}
        low, high = bounds

        for _ in range(max_iter):
            mid = (low + high) / 2
            override_inputs = {variable_name: self.inputs[variable_name] * mid}
            self.inputs.update(override_inputs)
            self.calculate()
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
                    "NPVNotFound", "NPV not found after DCFROR calculation. Check calculation logic.", info_map
                )
                return float("nan")

            if abs(npv - target_npv) < tol:
                return mid
            if npv > target_npv:
                high = mid
            else:
                low = mid

        self.om.add_error(
            "GoalSeekFailed", "Goal seek did not converge within the maximum number of iterations.", info_map
        )
        return float("nan")


if __name__ == "__main__":
    try:
        calculator = DCFRORCalculator()
        calculator.calculate()
    except Exception as exc:
        OutputManager().add_error(f"DCFROR main execution failed: {exc}", {"script": "EEE_manager.py"})
