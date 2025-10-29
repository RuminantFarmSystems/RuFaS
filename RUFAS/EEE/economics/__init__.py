"""Economics subpackage for RuFaS.

This package hosts financial analysis tools such as the
Discounted Cash Flow Rate of Return (DCFROR) calculator
and a Partial Budget Analysis (PBA) routine. These are
orchestrated via a Flexible Economic Framework that
selects the appropriate analysis based on input data.
"""

from .framework import run_economic_analysis
from .metrics import (
    calculate_roi,
    calculate_payback_period,
    calculate_net_annual_cash_flow,
    calculate_mpsp,
)
from .digester_costs import (
    calculate_digester_capital_cost,
    capital_recovery_factor,
    scale_installed_cost,
    calculate_digester_capex,
    calculate_digester_operational_cost,
    get_digester_cost_profile,
    estimate_digester_costs,
    estimate_digester_trucking_cost,
    LinearCostEquation,
    DigesterSystemCostProfile,
)
from .equations import (
    construct_timeline,
    discount_factor,
    annual_capital_spent,
    loan_principal,
    construction_interest,
    npv_capital_plus_interest,
    annual_loan_payment,
    interest_payment,
    principal_after_payment,
    depreciation_schedule,
    net_revenue,
    loss_carry_forward,
    taxable_income,
    income_tax,
    annual_cash_income,
    present_value,
    net_present_value,
)

__all__ = [
    "run_economic_analysis",
    "calculate_roi",
    "calculate_payback_period",
    "calculate_net_annual_cash_flow",
    "calculate_mpsp",
    "calculate_digester_capital_cost",
    "calculate_digester_capex",
    "calculate_digester_operational_cost",
    "capital_recovery_factor",
    "scale_installed_cost",
    "get_digester_cost_profile",
    "estimate_digester_costs",
    "estimate_digester_trucking_cost",
    "LinearCostEquation",
    "DigesterSystemCostProfile",
    "construct_timeline",
    "discount_factor",
    "annual_capital_spent",
    "loan_principal",
    "construction_interest",
    "npv_capital_plus_interest",
    "annual_loan_payment",
    "interest_payment",
    "principal_after_payment",
    "depreciation_schedule",
    "net_revenue",
    "loss_carry_forward",
    "taxable_income",
    "income_tax",
    "annual_cash_income",
    "present_value",
    "net_present_value",
]
