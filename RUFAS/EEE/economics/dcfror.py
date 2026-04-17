from __future__ import annotations

from typing import Any, Dict, Iterable, Tuple

import numpy as np
import pandas as pd

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.units import MeasurementUnits

from .equations import EconomicEquations
from .metrics import EconomicMetrics


class DCFRORCalculator:
    """Compute the Discounted Cash Flow Rate of Return (DCFROR) analysis."""

    def __init__(self) -> None:
        self.im = InputManager()
        self.om = OutputManager()
        self.inputs = self._load_inputs()

    def _require_input(self, path: str) -> Any:
        """Return a required input value or raise ``KeyError`` when missing."""
        if hasattr(self.im, "check_property_exists_in_pool"):
            if not self.im.check_property_exists_in_pool(path):
                raise KeyError(f"Missing required input: {path}")

        value = self.im.get_data(path)
        if value is None:
            raise KeyError(f"Missing required input: {path}")
        return value

    @staticmethod
    def _to_numpy(values: Any) -> np.ndarray:
        """Coerce inputs to float NumPy arrays while preserving matrix shape."""
        if isinstance(values, pd.DataFrame):
            return values.to_numpy(dtype=float)
        return np.asarray(values, dtype=float)

    @staticmethod
    def _bounded_candidate(
        variable_name: str,
        baseline_value: float,
        multiplier: float,
        project_term: int,
    ) -> float:
        """Bound goal-seek candidate values in the same way as the legacy logic."""
        candidate = baseline_value * multiplier
        if variable_name == "loan_term":
            return float(max(1, min(project_term, int(round(candidate)))))
        if variable_name == "internal_rate_of_return":
            return float(max(-0.99, candidate))
        if variable_name == "goal_seek_unit_price_multiplier":
            return float(max(0.0, candidate))
        return float(candidate)

    def _latest_goal_seek_npv(self) -> float | None:
        """Return the latest computed DCFROR NPV value from the OutputManager."""
        npv_result = self.om.filter_variables_pool(
            {
                "name": "NPV Retrieval",
                "description": "Retrieve the latest DCFROR NPV for goal seek; results are chronological so slice to newest entry.",
                "filters": [f"{self.__class__.__name__}.{self.calculate.__name__}.econ_dcfror_npv"],
                "slice_start": -1,
            }
        )
        npv_key = f"{self.__class__.__name__}.{self.calculate.__name__}.econ_dcfror_npv"
        npv_record = npv_result.get(npv_key, None)
        npv_values = npv_record.get("values") if isinstance(npv_record, dict) else None
        return float(npv_values[0]) if npv_values else None

    def _load_inputs(self) -> Dict[str, Any]:
        info_map = {"class": self.__class__.__name__, "function": self._load_inputs.__name__}
        try:
            # Retrieve input data
            loan_term = self._require_input("economic_inputs.cashflow_inputs.loan_term")
            project_term = self._require_input("economic_inputs.cashflow_inputs.project_term")
            if loan_term > project_term:
                # Loan duration should not exceed the project lifetime
                self.om.add_warning(
                    "LoanTermAdjusted",
                    "Loan term longer than project term; using project term instead.",
                    info_map,
                )
                loan_term = project_term

            cost_capital_multiple = self._require_input("economic_inputs.capital_costs.capital_cost_breakdown")

            inputs: Dict[str, Any] = {
                "cost_capital_multiple": cost_capital_multiple,
                "cost_operational_units": self._require_input("economic_inputs.cashflow_inputs.operating_units"),
                "cost_operational_unit_cost": self._require_input("economic_inputs.cashflow_inputs.operating_unit_costs"),
                "units_produced": self._require_input("economic_inputs.cashflow_inputs.units_produced"),
                "unit_cost": self._require_input("economic_inputs.cashflow_inputs.unit_price"),
                "loan_interest_rate": self._require_input("economic_inputs.cashflow_inputs.loan_interest_rate"),
                # Loan term is capped to the project term above per the
                # guidance in `Documentation of Economic Data and Analytical
                # Methods (2).pdf`.
                "loan_term": loan_term,
                "loan_amount": self._require_input("economic_inputs.cashflow_inputs.loan_fraction"),
                "equity_amount": self._require_input("economic_inputs.cashflow_inputs.equity"),
                "interest_rate_construction": self._require_input("economic_inputs.cashflow_inputs.const_int"),
                "construction_term": self._require_input("economic_inputs.cashflow_inputs.const_term"),
                "construction_finish_pcts": self._require_input("economic_inputs.cashflow_inputs.const_rate_i"),
                "tax_rate": self._require_input("economic_inputs.cashflow_inputs.tax_rate"),
                "internal_rate_of_return": self._require_input(
                    "economic_inputs.cashflow_inputs.target_internal_rate_of_return"
                ),
                "project_term": project_term,
                "depreciation_rate": np.array(self._require_input("economic_inputs.cashflow_inputs.depreciation_i")),
                "enable": self._require_input("economic_inputs.cashflow_inputs.enable_dcfror"),
                "tax_credit_used": self._require_input("economic_inputs.cashflow_inputs.tax_credit_used"),
                "enable_goal_seek": self._require_input("economic_inputs.cashflow_inputs.enable_goal_seek"),
                "goal_seek_target_npv": self._require_input("economic_inputs.cashflow_inputs.goal_seek_target_npv"),
                "goal_seek_bounds": self._require_input("economic_inputs.cashflow_inputs.goal_seek_bounds"),
                "goal_seek_unit_price_multiplier": self._require_input(
                    "economic_inputs.cashflow_inputs.goal_seek_unit_price_multiplier"
                ),
                "goal_seek_fixed_variables": self._require_input("economic_inputs.cashflow_inputs.goal_seek_fixed_variables"),
            }
            return inputs
        except KeyError as e:
            self.om.add_error("MissingInputKey", f"Missing input key: {str(e)}", info_map)
            raise

    def calculate(self, override_inputs: Dict[str, Any] | None = None) -> None:
        """Run the DCFROR cash-flow model and export summary outputs.

        Parameters
        ----------
        override_inputs : dict[str, Any] | None, optional
            Temporary input overrides applied only for this call. This is used
            by :meth:`goal_seek` so each trial evaluates a fresh DCFROR run
            with the candidate value.
        """

        info_map = {"class": self.__class__.__name__, "function": self.calculate.__name__}

        if not self.inputs.get("enable", False):
            self.om.add_log(
                "DCFROR calculation",
                "DCFROR calculation skipped due to configuration flag.",
                info_map,
            )
            return

        self.om.add_log("DCFROR calculation", "Starting DCFROR calculation", info_map)

        active_inputs = dict(self.inputs)
        if override_inputs:
            active_inputs.update(override_inputs)

        cost_inputs = self._prepare_costs(active_inputs)
        financing = self._prepare_financing(active_inputs, cost_inputs["project_term"])
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

    def _prepare_costs(self, input_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Build capital, operating-cost, and revenue schedules from inputs."""

        info_map = {"class": self.__class__.__name__, "function": self._prepare_costs.__name__}

        cap_breakdown = input_dict["cost_capital_multiple"]
        if isinstance(cap_breakdown, pd.DataFrame) and cap_breakdown.empty:
            self.om.add_warning("EmptyCapitalCostBreakdown", "Capital cost breakdown is empty", info_map)

        base_cost = sum(d["Cost"] for d in cap_breakdown)
        if base_cost == 0:
            self.om.add_warning("ZeroCapitalCost", "Total capital cost is zero", info_map)

        # The construction-period financing uses the dedicated
        # ``interest_rate_construction`` input (IRCon in the documentation).
        construction_years = int(input_dict["construction_term"])
        finish_percentages = input_dict["construction_finish_pcts"]
        operating_units = self._to_numpy(input_dict["cost_operational_units"])
        operating_unit_costs = self._to_numpy(input_dict["cost_operational_unit_cost"])
        revenue_units = self._to_numpy(input_dict["units_produced"])
        unit_price_multiplier = float(input_dict.get("goal_seek_unit_price_multiplier", 1.0))
        if unit_price_multiplier < 0:
            self.om.add_warning(
                "GoalSeekUnitPriceMultiplierAdjusted",
                "goal_seek_unit_price_multiplier was negative; clamped to 0.0.",
                info_map,
            )
            unit_price_multiplier = 0.0
        revenue_prices = self._to_numpy(input_dict["unit_cost"]) * unit_price_multiplier

        # Interest accrued during construction should be accounted for in cash
        # flow calculations, not added to the depreciable capital cost.
        # Construction interest is accounted for later in the cash-flow stage
        # (Step 3 in `Documentation of Economic Data and Analytical Methods
        # (2).pdf`), so it does not increase the depreciable capital cost.
        capital_cost = base_cost
        operating_costs = np.asarray((operating_units * operating_unit_costs).sum(axis=0), dtype=float)
        revenue = np.asarray((revenue_units * revenue_prices).sum(axis=0), dtype=float)

        project_term = int(input_dict["project_term"])
        if project_term <= 0:
            self.om.add_error("InvalidProjectTerm", "Project term must be positive.", info_map)
            raise ValueError("Project term must be positive.")

        return {
            "project_term": project_term,
            "capital_cost": capital_cost,
            "construction_term": construction_years,
            "construction_rates": list(np.asarray(finish_percentages, dtype=float)),
            "revenue": revenue[:project_term],
            "operating_costs": operating_costs[:project_term],
        }

    def _prepare_financing(self, input_dict: Dict[str, Any], project_term: int) -> Dict[str, Any]:
        """Normalise financing inputs and enforce valid borrowing shares."""
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

    @staticmethod
    def _build_cash_flow_dataframe(
        years: np.ndarray,
        discount_factors: np.ndarray,
        capital_column: np.ndarray,
        loan_draw_column: np.ndarray,
        construction_interest_column: np.ndarray,
        revenue_column: np.ndarray,
        operating_column: np.ndarray,
        loan_payment_column: np.ndarray,
        interest_column: np.ndarray,
        depreciation_column: np.ndarray,
        net_revenue_column: np.ndarray,
        loss_forward_column: np.ndarray,
        taxable_income_column: np.ndarray,
        income_tax_column: np.ndarray,
        cash_income_column: np.ndarray,
        present_value_column: np.ndarray,
        capital_interest_pv: np.ndarray,
        loan_balance_column: np.ndarray,
    ) -> pd.DataFrame:
        """Build the cash flow output table."""
        return pd.DataFrame(
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

    @staticmethod
    def _populate_operational_phase(
        op_indices: np.ndarray,
        revenue_schedule: np.ndarray,
        operating_schedule: np.ndarray,
        depreciation_schedule_op: np.ndarray,
        loan_term: int,
        loan_payment: float,
        principal_balance: float,
        financed_share: float,
        loan_interest_rate: float,
        tax_rate: float,
        discount_factors: np.ndarray,
        revenue_column: np.ndarray,
        operating_column: np.ndarray,
        depreciation_column: np.ndarray,
        loan_payment_column: np.ndarray,
        interest_column: np.ndarray,
        net_revenue_column: np.ndarray,
        loss_forward_column: np.ndarray,
        taxable_income_column: np.ndarray,
        income_tax_column: np.ndarray,
        cash_income_column: np.ndarray,
        present_value_column: np.ndarray,
        loan_balance_column: np.ndarray,
        cash_flows: np.ndarray,
    ) -> None:
        """Populate annual operational cash-flow columns."""
        prev_taxable = 0.0
        prev_loss = 0.0
        for idx, year_index in enumerate(op_indices):
            revenue_y = revenue_schedule[idx]
            operating_y = operating_schedule[idx]
            depreciation_y = depreciation_schedule_op[idx]
            loan_pay_y = loan_payment if idx < loan_term else 0.0
            interest_y = (
                EconomicEquations.interest_payment(principal_balance, loan_interest_rate)
                if financed_share > 0 and idx < loan_term
                else 0.0
            )

            if idx < loan_term:
                principal_balance = max(
                    0.0,
                    EconomicEquations.principal_after_payment(principal_balance, loan_pay_y, interest_y),
                )

            net_rev_y = EconomicEquations.net_revenue(revenue_y, operating_y, interest_y, depreciation_y)
            carried_loss = EconomicEquations.loss_carry_forward(prev_taxable, prev_loss)
            used_loss = EconomicEquations.max_loss_utilized(net_rev_y, carried_loss)
            taxable_y = EconomicEquations.taxable_income(net_rev_y, used_loss)
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
            prev_loss = carried_loss + used_loss  # Economic Equation 24

    @staticmethod
    def _construction_phase(
        n_construction: int,
        n_years: int,
        construction_mask: np.ndarray,
        construction_rates: Iterable[float],
        capital_cost: float,
        equity_share: float,
        financed_share: float,
        construction_interest_rate: float,
        internal_rate_of_return: float,
        years: np.ndarray,
    ) -> Dict[str, np.ndarray]:
        """Compute construction-period schedules and present value terms."""
        rates = np.asarray(list(construction_rates), dtype=float)
        if n_construction:
            if rates.size < n_construction:
                rates = np.pad(rates, (0, n_construction - rates.size))
            rates = rates[:n_construction]
            if not np.allclose(rates.sum(), 1.0) and rates.sum() > 0:
                rates = rates / rates.sum()

            capital_schedule = EconomicEquations.annual_capital_spent(capital_cost, rates)
            equity_schedule = EconomicEquations.equity_contribution(capital_cost, rates, equity_share)
            loan_draw_schedule = capital_schedule * financed_share
            construction_interest_cost = EconomicEquations.construction_interest(loan_draw_schedule, construction_interest_rate)
            capital_interest_pv = np.zeros(n_years, dtype=float)
            capital_interest_pv[construction_mask] = EconomicEquations.npv_capital_plus_interest(
                equity_schedule,
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

        return {
            "capital_schedule": capital_schedule,
            "equity_schedule": equity_schedule,
            "loan_draw_schedule": loan_draw_schedule,
            "construction_interest_cost": construction_interest_cost,
            "capital_interest_pv": capital_interest_pv,
            "cumulative_draw": cumulative_draw,
        }

    @staticmethod
    def _initialise_result_columns(n_years: int) -> Dict[str, np.ndarray]:
        """Initialise all per-year output columns."""
        return {
            "capital_column": np.zeros(n_years, dtype=float),
            "loan_draw_column": np.zeros(n_years, dtype=float),
            "construction_interest_column": np.zeros(n_years, dtype=float),
            "revenue_column": np.zeros(n_years, dtype=float),
            "operating_column": np.zeros(n_years, dtype=float),
            "depreciation_column": np.zeros(n_years, dtype=float),
            "loan_payment_column": np.zeros(n_years, dtype=float),
            "interest_column": np.zeros(n_years, dtype=float),
            "net_revenue_column": np.zeros(n_years, dtype=float),
            "loss_forward_column": np.zeros(n_years, dtype=float),
            "taxable_income_column": np.zeros(n_years, dtype=float),
            "income_tax_column": np.zeros(n_years, dtype=float),
            "cash_income_column": np.zeros(n_years, dtype=float),
            "present_value_column": np.zeros(n_years, dtype=float),
            "loan_balance_column": np.zeros(n_years, dtype=float),
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

        years = EconomicEquations.construct_timeline(construction_term, loan_term, project_term)
        n_years = years.size
        construction_mask = years <= 0
        operational_mask = years >= 1
        discount_factors = np.array(
            [EconomicEquations.discount_factor(internal_rate_of_return, year) for year in years],
            dtype=float,
        )

        n_construction = int(construction_mask.sum())
        construction_data = self._construction_phase(
            n_construction=n_construction,
            n_years=n_years,
            construction_mask=construction_mask,
            construction_rates=construction_rates,
            capital_cost=capital_cost,
            equity_share=equity_share,
            financed_share=financed_share,
            construction_interest_rate=construction_interest_rate,
            internal_rate_of_return=internal_rate_of_return,
            years=years,
        )
        capital_schedule = construction_data["capital_schedule"]
        equity_schedule = construction_data["equity_schedule"]
        loan_draw_schedule = construction_data["loan_draw_schedule"]
        construction_interest_cost = construction_data["construction_interest_cost"]
        capital_interest_pv = construction_data["capital_interest_pv"]
        cumulative_draw = construction_data["cumulative_draw"]

        annual_depreciation = EconomicEquations.depreciation_schedule(capital_cost, depreciation_rate)
        if dep_term and dep_term < annual_depreciation.size:
            annual_depreciation = annual_depreciation[:dep_term]

        op_years = int(operational_mask.sum())
        revenue_schedule = np.zeros(op_years, dtype=float)
        operating_schedule = np.zeros(op_years, dtype=float)
        depreciation_schedule_op = np.zeros(op_years, dtype=float)
        revenue_schedule[: min(len(revenue), op_years)] = revenue[:op_years]
        operating_schedule[: min(len(operating_costs), op_years)] = operating_costs[:op_years]
        depreciation_schedule_op[: min(len(annual_depreciation), op_years)] = annual_depreciation[:op_years]

        loan_payment = EconomicEquations.annual_loan_payment(
            capital_cost, loan_interest_rate, loan_term, financed_share
        )
        principal_balance = capital_cost * financed_share

        columns = self._initialise_result_columns(n_years)
        capital_column = columns["capital_column"]
        loan_draw_column = columns["loan_draw_column"]
        construction_interest_column = columns["construction_interest_column"]
        revenue_column = columns["revenue_column"]
        operating_column = columns["operating_column"]
        depreciation_column = columns["depreciation_column"]
        loan_payment_column = columns["loan_payment_column"]
        interest_column = columns["interest_column"]
        net_revenue_column = columns["net_revenue_column"]
        loss_forward_column = columns["loss_forward_column"]
        taxable_income_column = columns["taxable_income_column"]
        income_tax_column = columns["income_tax_column"]
        cash_income_column = columns["cash_income_column"]
        present_value_column = columns["present_value_column"]
        loan_balance_column = columns["loan_balance_column"]

        cash_flows = np.zeros(n_years, dtype=float)
        if n_construction:
            construction_indices = np.where(construction_mask)[0]
            capital_column[construction_indices] = capital_schedule
            loan_draw_column[construction_indices] = loan_draw_schedule
            construction_interest_column[construction_indices] = construction_interest_cost
            cash_flows[construction_indices] = -(equity_schedule + construction_interest_cost)
            loan_balance_column[construction_indices] = cumulative_draw

        op_indices = np.where(operational_mask)[0]
        self._populate_operational_phase(
            op_indices=op_indices,
            revenue_schedule=revenue_schedule,
            operating_schedule=operating_schedule,
            depreciation_schedule_op=depreciation_schedule_op,
            loan_term=loan_term,
            loan_payment=loan_payment,
            principal_balance=principal_balance,
            financed_share=financed_share,
            loan_interest_rate=loan_interest_rate,
            tax_rate=tax_rate,
            discount_factors=discount_factors,
            revenue_column=revenue_column,
            operating_column=operating_column,
            depreciation_column=depreciation_column,
            loan_payment_column=loan_payment_column,
            interest_column=interest_column,
            net_revenue_column=net_revenue_column,
            loss_forward_column=loss_forward_column,
            taxable_income_column=taxable_income_column,
            income_tax_column=income_tax_column,
            cash_income_column=cash_income_column,
            present_value_column=present_value_column,
            loan_balance_column=loan_balance_column,
            cash_flows=cash_flows,
        )

        cash_flow_df = self._build_cash_flow_dataframe(
            years=years,
            discount_factors=discount_factors,
            capital_column=capital_column,
            loan_draw_column=loan_draw_column,
            construction_interest_column=construction_interest_column,
            revenue_column=revenue_column,
            operating_column=operating_column,
            loan_payment_column=loan_payment_column,
            interest_column=interest_column,
            depreciation_column=depreciation_column,
            net_revenue_column=net_revenue_column,
            loss_forward_column=loss_forward_column,
            taxable_income_column=taxable_income_column,
            income_tax_column=income_tax_column,
            cash_income_column=cash_income_column,
            present_value_column=present_value_column,
            capital_interest_pv=capital_interest_pv,
            loan_balance_column=loan_balance_column,
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
        npv = EconomicEquations.net_present_value(
            cash_flow_df.loc[operational_mask, "PresentValue"].to_numpy(),
            cash_flow_df.loc[construction_mask, "NPVCapitalPlusInterest"].to_numpy(),
        )

        positive_benefits = float(CF[CF > 0].sum())
        investment_costs = float(-CF[CF < 0].sum())
        roi = EconomicMetrics.calculate_roi(positive_benefits, investment_costs)
        payback = EconomicMetrics.calculate_payback_period(CF)
        net_cash_flow = EconomicMetrics.calculate_net_annual_cash_flow(revenue, operating_costs)
        mpsp = EconomicMetrics.calculate_mpsp(capital_cost + operating_costs.sum(), revenue.sum())

        self.om.add_variable("econ_dcfror_npv", npv, {**info_map, "units": MeasurementUnits.DOLLARS})
        self.om.add_variable("econ_dcfror_roi", roi, {**info_map, "units": MeasurementUnits.UNITLESS})
        self.om.add_variable(
            "econ_dcfror_payback_period",
            payback,
            {**info_map, "units": MeasurementUnits.SIMULATION_YEAR},
        )
        self.om.add_variable(
            "econ_dcfror_net_cash_flow",
            net_cash_flow.tolist(),
            {**info_map, "units": MeasurementUnits.DOLLARS},
        )
        self.om.add_variable("econ_dcfror_mpsp", mpsp, {**info_map, "units": MeasurementUnits.DOLLARS})
        self.om.add_variable(
            "econ_dcfror_cash_flow_summary",
            cash_flow_df.to_dict(orient="list"),
            {**info_map, "units": MeasurementUnits.UNITLESS},
        )
        self.om.add_log(
            "DCFROR calculation",
            "DCFROR calculation completed successfully.",
            info_map,
        )

    def goal_seek(
        self,
        variable_name: str,
        target_npv: float = 0.0,
        bounds: Tuple[float, float] = (0.01, 100.0),
        tol: float = 1e-6,
        max_iter: int = 100,
    ) -> float:
        """Solve for one DCFROR input value that drives NPV toward a target.

        The solver performs a binary search over a *multiplier* (`mid`) and
        evaluates ``candidate_value = baseline_value * mid``. It then reruns
        :meth:`calculate` with that candidate override and reads the most
        recent ``econ_dcfror_npv`` output.

        Parameters
        ----------
        variable_name : str
            Name of the scalar input in ``self.inputs`` to perturb.
        target_npv : float, optional
            Desired NPV setpoint.
        bounds : tuple[float, float], optional
            Lower/upper bounds for the multiplier search interval.
        tol : float, optional
            Absolute tolerance on ``abs(npv - target_npv)``.
        max_iter : int, optional
            Maximum bisection iterations.
        """

        info_map = {"class": self.__class__.__name__, "function": self.goal_seek.__name__}
        if variable_name not in self.inputs:
            self.om.add_error("GoalSeekVariableMissing", f"Unknown variable: {variable_name}", info_map)
            return float("nan")
        if max_iter <= 0:
            self.om.add_error("GoalSeekInvalidMaxIter", "max_iter must be > 0.", info_map)
            return float("nan")

        low, high = map(float, bounds)
        if not np.isfinite(low) or not np.isfinite(high) or low >= high:
            self.om.add_error("GoalSeekInvalidBounds", f"Invalid bounds: {bounds}", info_map)
            return float("nan")

        baseline_value = float(self.inputs[variable_name])
        if not np.isfinite(baseline_value):
            self.om.add_error("GoalSeekInvalidBaseline", "Baseline goal-seek value must be finite.", info_map)
            return float("nan")

        project_term = int(self.inputs.get("project_term", 1))

        for _ in range(max_iter):
            mid = (low + high) / 2
            override_inputs = {
                variable_name: self._bounded_candidate(variable_name, baseline_value, mid, project_term)
            }
            self.calculate(override_inputs=override_inputs)
            npv = self._latest_goal_seek_npv()

            if npv is None:
                self.om.add_error(
                    "NPVNotFound", "NPV not found after DCFROR calculation. Check calculation logic.", info_map
                )
                return float("nan")

            if abs(npv - target_npv) < tol:
                self.inputs[variable_name] = override_inputs[variable_name]
                return mid
            if npv > target_npv:
                high = mid
            else:
                low = mid

        self.inputs[variable_name] = self._bounded_candidate(variable_name, baseline_value, (low + high) / 2, project_term)
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
