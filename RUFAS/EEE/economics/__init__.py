"""Economics subpackage for RuFaS.

This package hosts financial analysis tools such as the
Discounted Cash Flow Rate of Return (DCFROR) calculator
and a Partial Budget Analysis (PBA) routine. These are
orchestrated via a Flexible Economic Framework that
selects the appropriate analysis based on input data.
"""

from .framework import EconomicFramework
from .metrics import EconomicMetrics
from .digester_costs import DigesterCostCalculator, LinearCostEquation, DigesterSystemCostProfile
from .equations import EconomicEquations

__all__ = [
    "EconomicFramework",
    "EconomicMetrics",
    "DigesterCostCalculator",
    "LinearCostEquation",
    "DigesterSystemCostProfile",
    "EconomicEquations",
]
