"""Specialized cost calculations for manure digesters and equipment."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Mapping


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


class DigesterCostCalculator:
    """Collection of digester-related economic calculations."""

    @staticmethod
    def get_digester_system_name(digester_config: Any) -> str:
        """Return the digester cost-profile name from the manure-management config."""

        config = digester_config[0] if isinstance(digester_config, list) else digester_config

        digester_type = str(config["digester_type"]).lower()
        biogas_use = str(config["biogas_use"]).lower()

        if "lagoon" in digester_type:
            system_type = "Covered Lagoon"
        elif "plug" in digester_type:
            system_type = "Plug Flow"
        else:
            raise ValueError(f"Unsupported digester type for costing: {digester_type}")

        if "rng" in biogas_use:
            use_case = "RNG"
        elif "chp" in biogas_use:
            use_case = "CHP"
        else:
            raise ValueError(f"Unsupported digester biogas use case for costing: {biogas_use}")

        return f"{system_type} - {use_case}"

    @staticmethod
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

    @classmethod
    def get_digester_cost_profile(cls, system: str) -> DigesterSystemCostProfile:
        """Return the cost profile for a supported digester configuration.

        The coefficients are sourced from ``economic_docs/Variables Update for Joe
        and Pooya.xlsx`` and provide linear estimates for capital and operational
        expenses as a function of the number of cows contributing manure to the
        digester.
        """

        key = cls._normalize_system_name(system)
        try:
            return cls._DIGESTER_SYSTEMS[key]
        except KeyError as exc:  # pragma: no cover - defensive branch
            available = ", ".join(sorted(cls._DIGESTER_SYSTEMS))
            raise KeyError(f"Unknown digester system '{system}'. Available: {available}") from exc

    @classmethod
    def estimate_digester_costs(cls, system: str, cows: float) -> Dict[str, object]:
        """Return CAPEX and OPEX estimates for the requested digester system."""

        profile = cls.get_digester_cost_profile(system)
        return {
            "capital_expenditure": profile.capital_cost(cows),
            "operating_costs": profile.annual_operating_costs(cows),
            "useful_life_years": profile.useful_life_years,
            "salvage_value_fraction": profile.salvage_value_fraction,
            "biogas_yield_ft3_per_cow_day": profile.biogas_yield_ft3_per_cow_day,
            "methane_content_fraction": profile.methane_content_fraction,
        }

    @classmethod
    def estimate_digester_trucking_cost(cls, cows: float) -> float:
        """Estimate the RNG trucking and injection cost for the herd size."""

        return cls._TRANSPORT_COST.evaluate(cows)
