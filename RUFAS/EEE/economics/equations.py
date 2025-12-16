"""Implementation of economic equations 7–26 from the April 2025 guidance."""

from __future__ import annotations

from typing import Iterable

import numpy as np


class EconomicEquations:
    """Namespace grouping the reusable economic helper equations."""

    @staticmethod
    def _normalise_percentages(percentages: Iterable[float], length: int) -> np.ndarray:
        """Return a normalised array of construction percentages."""

        rates = np.asarray(list(percentages), dtype=float)
        if length and rates.size < length:
            rates = np.pad(rates, (0, length - rates.size))
        if rates.size == 0:
            return np.zeros(length, dtype=float)
        if np.allclose(rates.sum(), 0.0):
            return np.zeros_like(rates, dtype=float)
        return rates / rates.sum()

    @staticmethod
    def construct_timeline(construction_years: int, loan_term: int, project_term: int | None = None) -> np.ndarray:
        """Return the project year vector using Equation 7."""

        construction_years = max(int(construction_years), 0)
        loan_term = max(int(loan_term), 0)
        end_year = loan_term
        if project_term is not None:
            end_year = max(end_year, int(project_term))
        start_year = 1 - construction_years
        return np.arange(start_year, end_year + 1, dtype=int)

    @staticmethod
    def discount_factor(irr: float, year: int | float) -> float:
        """Discount factor for a given year using Equation 9."""

        period = abs(float(year))
        return 1 / ((1 + irr) ** period)

    @staticmethod
    def annual_capital_spent(total_capital: float, construction_rate_per_year: list[float] | np.ndarray) -> np.ndarray:
        """Capital spent each construction year using Equation 11."""

        rates = np.asarray(construction_rate_per_year, dtype=float)
        return total_capital * rates

    @staticmethod
    def equity_contribution(
        total_capital: float,
        construction_rate_per_year: list[float] | np.ndarray,
        equity_amount: float,
    ) -> np.ndarray:
        """Equity deployed during construction each year."""
        rates = np.asarray(construction_rate_per_year, dtype=float)
        return total_capital * rates * equity_amount

    # Equation 12 in `Documentation of Economic Data and Analytical Methods (2).pdf`
    # defines loan principal as the annual capital spent times the financed fraction.
    @staticmethod
    def loan_principal(
        total_capital: float | np.ndarray,
        construction_rate_per_year: list[float] | np.ndarray,
        loan_fraction: float | None = None,
    ) -> np.ndarray:
        """Loan principal for each construction year using Equation 12."""

        capital = np.asarray(total_capital, dtype=float)
        if loan_fraction is None:
            return capital * np.asarray(construction_rate_per_year, dtype=float)

        rates = np.asarray(construction_rate_per_year, dtype=float)
        return capital * rates * loan_fraction

    @staticmethod
    def construction_interest(loan_principal: np.ndarray, interest_rate: float) -> np.ndarray:
        """Interest accrued on loan during construction using Equation 13."""

        principal = np.asarray(loan_principal, dtype=float)
        outstanding = np.cumsum(principal)
        return outstanding * float(interest_rate)

    @staticmethod
    def npv_capital_plus_interest(
        capital: np.ndarray, interest: np.ndarray, irr: float, years: np.ndarray
    ) -> np.ndarray:
        """Present value of capital plus interest using Equation 14."""
        years = np.asarray(years, dtype=float)
        df = np.array([EconomicEquations.discount_factor(irr, y) for y in years], dtype=float)
        return (np.asarray(capital, dtype=float) + np.asarray(interest, dtype=float)) * df

    @staticmethod
    def annual_loan_payment(total_cost: float, rate: float, term: int, loan_fraction: float) -> float:
        """Annual loan payment using Equation 15."""
        if term <= 0:
            return 0.0
        numerator = total_cost * rate * loan_fraction
        denominator = 1 - (1 + rate) ** (-term)
        return numerator / denominator

    @staticmethod
    def interest_payment(previous_principal: float, rate: float) -> float:
        """Loan interest payment for a year using Equation 17."""
        return previous_principal * rate

    @staticmethod
    def principal_after_payment(previous_principal: float, payment: float, interest: float) -> float:
        """Remaining loan principal after payment using Equation 18."""
        return previous_principal - payment + interest

    @staticmethod
    def depreciation_schedule(total_cost: float, depreciation_rates: np.ndarray) -> np.ndarray:
        """Annual depreciation using Equation 19."""
        return total_cost * np.asarray(depreciation_rates, dtype=float)

    @staticmethod
    def net_revenue(
        revenue: float,
        operating_cost: float,
        interest: float,
        depreciation: float,
    ) -> float:
        # NOTE: Interest from ``interest_payment`` is used here; principal changes
        # are handled separately via ``principal_after_payment``.

        """Net revenue calculation using Equation 20."""
        return revenue - operating_cost - interest - depreciation

    @staticmethod
    def loss_carry_forward(prev_taxable: float) -> float:
        """Loss carry forward using Equation 21."""
        return prev_taxable if prev_taxable < 0 else 0.0

    @staticmethod
    def taxable_income(net_rev: float, carried_loss: float) -> float:
        """Taxable income using Equation 22."""
        return net_rev + carried_loss

    @staticmethod
    def income_tax(taxable: float, tax_rate: float) -> float:
        """Income tax using Equation 23."""
        taxable = max(taxable, 0.0)
        return taxable * tax_rate

    @staticmethod
    def annual_cash_income(revenue: float, operating_cost: float, loan_payment: float, tax_pay: float) -> float:
        """Annual cash income using Equation 24."""
        return revenue - operating_cost - loan_payment - tax_pay

    @staticmethod
    def present_value(cash_income: float, discount: float) -> float:
        """Present value of cash income using Equation 25."""
        return cash_income * discount

    @staticmethod
    def net_present_value(apv: np.ndarray, capital_interest_pv: np.ndarray) -> float:
        """Net present value using Equation 26."""
        return apv.sum() - capital_interest_pv.sum()
