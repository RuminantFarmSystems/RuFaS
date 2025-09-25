"""Specialized cost calculations for manure digesters and equipment."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Mapping


# Equation 1 from the economics documentation
#  A_FC_ij = EXP(alpha + R1*ln(A_j) + R2*ln(V_j) + psi1*F_j + psi2*G_j + psi3*C_j + psi4*S_j + epsilon_j)


def calculate_digester_capital_cost(
    animal_units: float | None = None,
    digester_volume: float | None = None,
    farm_type_flag: float | None = None,
    below_ground_flag: float | None = None,
    concrete_flag: float | None = None,
    steel_flag: float | None = None,
    *,
    alpha: float = 10.4,
    r1: float = -0.413,
    r2: float = -0.147,
    psi1: float = -1.085,
    psi2: float = -0.582,
    psi3: float = 0.519,
    psi4: float = -0.007,
    epsilon: float = 0.35,
    area: float | None = None,
    volume: float | None = None,
    f_j: float | None = None,
    g_j: float | None = None,
    c_j: float | None = None,
    s_j: float | None = None,
) -> float:
    """Return the estimated digester capital cost using Equation 1."""

    if animal_units is None:
        animal_units = float(area) if area is not None else None
    if digester_volume is None:
        digester_volume = float(volume) if volume is not None else None
    if animal_units is None or digester_volume is None:
        raise ValueError("animal_units and digester_volume are required inputs")
    if animal_units <= 0 or digester_volume <= 0:
        raise ValueError("animal_units and digester_volume must be positive")

    if farm_type_flag is None:
        farm_type_flag = float(f_j) if f_j is not None else 1.0
    if below_ground_flag is None:
        below_ground_flag = float(g_j) if g_j is not None else 1.0
    if concrete_flag is None:
        concrete_flag = float(c_j) if c_j is not None else 1.0
    if steel_flag is None:
        steel_flag = float(s_j) if s_j is not None else 0.0

    return math.exp(
        alpha
        + r1 * math.log(animal_units)
        + r2 * math.log(digester_volume)
        + psi1 * farm_type_flag
        + psi2 * below_ground_flag
        + psi3 * concrete_flag
        + psi4 * steel_flag
        + epsilon
    )


# Equation 2 - Capital Recovery Factor


def capital_recovery_factor(rate: float, periods: int) -> float:
    """Compute the capital recovery factor (Equation 2)."""
    if periods <= 0:
        raise ValueError("periods must be positive")
    if rate == 0:
        return 1 / periods
    numerator = rate * (1 + rate) ** periods
    denominator = (1 + rate) ** periods - 1
    return numerator / denominator


# Equation 5 - Generalized equipment scaling


def scale_installed_cost(base_cost: float, volume: float, base_volume: float, install_factor: float) -> float:
    """Scale equipment cost to a new volume using Equation 5."""
    if base_volume <= 0:
        raise ValueError("base_volume must be positive")
    ratio = volume / base_volume
    return base_cost * (ratio**install_factor)


# Equation 3 - Digester CAPEX derived from annual fixed cost and CRF


def calculate_digester_capex(afc_ij: float, crf: float) -> float:
    """Return the digester capital expenditure using Equation 3."""
    if crf == 0:
        raise ValueError("capital recovery factor cannot be zero")
    return afc_ij / crf


# Equation 4 - Digester variable operational cost


def calculate_digester_operational_cost(
    use_cost_function: bool,
    animal_units: float,
    farm_type_flag: float,
    below_ground_flag: float,
    concrete_flag: float,
    steel_flag: float,
    *,
    beta: float = 3.531,
    omega1: float = -0.321,
    phi1: float = -0.686,
    phi2: float = -0.418,
    phi3: float = 0.488,
    phi4: float = -0.113,
    epsilon: float = 0.237,
) -> float:
    """Return the variable operational cost using Equation 4."""

    if not use_cost_function:
        return 0.0
    if animal_units <= 0:
        raise ValueError("animal_units must be positive to evaluate the AVC function")

    return math.exp(
        beta
        + omega1 * math.log(animal_units)
        + phi1 * farm_type_flag
        + phi2 * below_ground_flag
        + phi3 * concrete_flag
        + phi4 * steel_flag
        + epsilon
    )


@dataclass(frozen=True)
class LinearCostEquation:
    """Simple linear cost curve of the form ``slope * cows + intercept``."""

    slope: float
    intercept: float = 0.0

    def evaluate(self, cows: float) -> float:
        """Return the cost for a given number of cows."""
        return self.slope * cows + self.intercept


@dataclass(frozen=True)
class DigesterSystemCostProfile:
    """Encapsulate CAPEX/OPEX equations for a digester configuration."""

    capex: LinearCostEquation
    labor: LinearCostEquation
    energy: LinearCostEquation
    repairs: LinearCostEquation
    useful_life_years: int
    salvage_value_fraction: float
    biogas_yield_ft3_per_cow_day: float
    methane_content_fraction: float

    def capital_cost(self, cows: float) -> float:
        """Return the system CAPEX for the provided herd size."""

        return self.capex.evaluate(cows)

    def annual_operating_costs(self, cows: float) -> Dict[str, float]:
        """Return the labor, energy, and repair costs for the herd size."""

        return {
            "labor": self.labor.evaluate(cows),
            "energy": self.energy.evaluate(cows),
            "repairs": self.repairs.evaluate(cows),
        }


def _normalize_system_name(system: str) -> str:
    """Return a normalized key for digester system lookups."""

    normalized = []
    prev_sep = False
    for ch in system.lower():
        if ch.isalnum():
            normalized.append(ch)
            prev_sep = False
        else:
            if not prev_sep:
                normalized.append("_")
            prev_sep = True
    return "".join(normalized).strip("_")


_DIGESTER_SYSTEMS: Mapping[str, DigesterSystemCostProfile] = {
    _normalize_system_name("Covered Lagoon - RNG"): DigesterSystemCostProfile(
        capex=LinearCostEquation(875.0, 625_000.0),
        labor=LinearCostEquation(94.5, 67_500.0),
        energy=LinearCostEquation(34.80, 21.0),
        repairs=LinearCostEquation(66.69, 40.25),
        useful_life_years=20,
        salvage_value_fraction=0.15,
        biogas_yield_ft3_per_cow_day=72.0,
        methane_content_fraction=0.6,
    ),
    _normalize_system_name("Covered Lagoon - CHP"): DigesterSystemCostProfile(
        capex=LinearCostEquation(1_312.5, 937_500.0),
        labor=LinearCostEquation(188.48, 113.75),
        energy=LinearCostEquation(15.75, 11_250.0),
        repairs=LinearCostEquation(47.25, 33_750.0),
        useful_life_years=20,
        salvage_value_fraction=0.15,
        biogas_yield_ft3_per_cow_day=72.0,
        methane_content_fraction=0.6,
    ),
    _normalize_system_name("Plug Flow - RNG"): DigesterSystemCostProfile(
        capex=LinearCostEquation(1_750.0, 1_000_000.0),
        labor=LinearCostEquation(287.47, 2_670.0),
        energy=LinearCostEquation(47.91, 445.0),
        repairs=LinearCostEquation(143.73, 1_335.0),
        useful_life_years=20,
        salvage_value_fraction=0.15,
        biogas_yield_ft3_per_cow_day=120.0,
        methane_content_fraction=0.6,
    ),
    _normalize_system_name("Plug Flow - CHP"): DigesterSystemCostProfile(
        capex=LinearCostEquation(2_625.0, 2_000_000.0),
        labor=LinearCostEquation(75.0, 45_000.0),
        energy=LinearCostEquation(12.5, 7_500.0),
        repairs=LinearCostEquation(37.5, 22_500.0),
        useful_life_years=20,
        salvage_value_fraction=0.15,
        biogas_yield_ft3_per_cow_day=120.0,
        methane_content_fraction=0.6,
    ),
}

_TRANSPORT_COST = LinearCostEquation(137.5, 0.0)


def get_digester_cost_profile(system: str) -> DigesterSystemCostProfile:
    """Return the cost profile for a supported digester configuration.

    The coefficients are sourced from ``economic_docs/Variables Update for Joe
    and Pooya.xlsx`` and provide linear estimates for capital and operational
    expenses as a function of the number of cows contributing manure to the
    digester.
    """

    key = _normalize_system_name(system)
    try:
        return _DIGESTER_SYSTEMS[key]
    except KeyError as exc:  # pragma: no cover - defensive branch
        available = ", ".join(sorted(_DIGESTER_SYSTEMS))
        raise KeyError(f"Unknown digester system '{system}'. Available: {available}") from exc


def estimate_digester_costs(system: str, cows: float) -> Dict[str, object]:
    """Return CAPEX and OPEX estimates for the requested digester system."""

    profile = get_digester_cost_profile(system)
    return {
        "capital_expenditure": profile.capital_cost(cows),
        "operating_costs": profile.annual_operating_costs(cows),
        "useful_life_years": profile.useful_life_years,
        "salvage_value_fraction": profile.salvage_value_fraction,
        "biogas_yield_ft3_per_cow_day": profile.biogas_yield_ft3_per_cow_day,
        "methane_content_fraction": profile.methane_content_fraction,
    }


def estimate_digester_trucking_cost(cows: float) -> float:
    """Estimate the RNG trucking and injection cost for the herd size."""

    return _TRANSPORT_COST.evaluate(cows)
