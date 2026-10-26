from __future__ import annotations

from typing import Any

import numpy as np
import numpy.typing as npt
from scipy.optimize import OptimizeResult, linprog

from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import (
    FeedInRation,
    NutritionSupplyCalculator,
)
from RUFAS.biophysical.animal.ration.ration_optimizer import RationConfig, RationOptimizer

from RUFAS.general_constants import GeneralConstants
from RUFAS.data_structures.feed_storage_to_animal_connection import (
    Feed,
    FeedComponentType,
    NutrientStandard,
    RUFAS_ID,
)

STRATEGY_DESCRIPTION = (
    "LINEAR PROGRAMMING (HiGHS dual simplex): exact NDF/fat; frozen MP/energy; "
    "two MP upper-bound LP branches; original-model validation"
)

# Original functions return different units: g, Mcal, kg, percentage points.
# This is a numerical feasibility check in EACH original function's unit.
ORIGINAL_CONSTRAINT_TOLERANCE = 1e-5
MIN_REFERENCE_DMI = 1e-8


class UserRationOptimizer(RationOptimizer):
    """Use the original RuFaS helpers, replacing only the solver/model builder."""

    # The four composition constraints are EXACTLY equivalent for total DMI > 0.
    @staticmethod
    def NDF_constraint_lower_linear(x: npt.NDArray[np.float64], cfg: RationConfig) -> float:
        return float(np.dot(x, np.asarray(cfg.NDF_list) - AnimalModuleConstants.MINIMUM_RATION_NDF))

    @staticmethod
    def NDF_constraint_upper_linear(x: npt.NDArray[np.float64], cfg: RationConfig) -> float:
        return float(np.dot(x, AnimalModuleConstants.MAXIMUM_RATION_NDF - np.asarray(cfg.NDF_list)))

    @staticmethod
    def forage_NDF_constraint_linear(x: npt.NDArray[np.float64], cfg: RationConfig) -> float:
        forage_ndf = np.array(
            [feed.NDF if feed.feed_type is FeedComponentType.FORAGE else 0.0 for feed in cfg.feeds_used],
            dtype=float,
        )
        return float(np.dot(x, forage_ndf - AnimalModuleConstants.MINIMUM_RATION_FORAGE_NDF))

    @staticmethod
    def fat_constraint_linear(x: npt.NDArray[np.float64], cfg: RationConfig) -> float:
        return float(np.dot(x, AnimalModuleConstants.MAXIMUM_RATION_FAT - np.asarray(cfg.EE_list)))

    @staticmethod
    def _reference_ration(
        cfg: RationConfig,
        bounds: list[tuple[float, float]],
        previous_ration: dict[RUFAS_ID | str, float | str] | None,
    ) -> npt.NDArray[np.float64]:
        """Deterministic, bounded reference. Prefer actual previous quantities."""
        lo = np.array([pair[0] for pair in bounds], dtype=float)
        hi = np.array([pair[1] for pair in bounds], dtype=float)
        if len(lo) == 0 or not np.all(np.isfinite(lo)) or not np.all(np.isfinite(hi)) or np.any(hi < lo):
            raise ValueError("Missing/invalid ingredient bounds for LP reference")

        if previous_ration:
            values: list[float] = []
            for feed in cfg.feeds_used:
                value = previous_ration.get(feed.rufas_id, previous_ration.get(str(feed.rufas_id)))
                if value is None:
                    break
                try:
                    values.append(float(value))
                except (TypeError, ValueError):
                    break
            if len(values) == len(lo) and np.all(np.isfinite(values)):
                candidate = np.clip(np.asarray(values, dtype=float), lo, hi)
                if candidate.sum() > MIN_REFERENCE_DMI:
                    return candidate

        # When no complete previous ration exists, distribute target DMI across
        # inclusion capacities; do NOT randomize digestibility estimates.
        required = float(cfg.initial_dry_matter_requirement)
        if not np.isfinite(required):
            raise ValueError("Invalid reference DMI")
        total_target = np.clip(required, lo.sum(), hi.sum())
        capacities = hi - lo
        if capacities.sum() > 0.0:
            candidate = lo + (total_target - lo.sum()) * capacities / capacities.sum()
        else:
            candidate = lo.copy()
        if candidate.sum() <= MIN_REFERENCE_DMI:
            raise ValueError("Reference ration has no positive DMI")
        return candidate

    @staticmethod
    def _freeze_protein_coefficients(
        cfg: RationConfig, reference_x: npt.NDArray[np.float64]
    ) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        """Return g MP/kg ingredient for the TDN-limited and RDP-limited branches.

        Matches the RuFaS MP calculation at reference_x (up to roundoff).
        Only the TDN discount and each ingredient's RDP are frozen.
        The endogenous 4.72*g/kg contribution remains variable through DMI.
        """
        calc = NutritionSupplyCalculator
        feeds = RationOptimizer.convert_decision_vec_to_feeds(cfg, reference_x)
        dmi = float(np.sum(reference_x))
        body_weight = float(cfg.pen_average_body_weight)
        if dmi <= 0.0 or body_weight <= 0.0:
            raise ValueError("Reference DMI and body weight must be positive")

        discount = calc.calculate_nutrient_intake_discount(feeds=feeds, body_weight=body_weight)
        pct_concentrates = calc._calculate_percentage_of_concentrates(feeds, dmi)
        passage = calc._calculate_protein_passage_rates(feeds, dmi, body_weight, pct_concentrates)
        rdp_percent = calc._calculate_rumen_degradable_protein_percentages(feeds, passage)
        rup_percent = calc._calculate_rumen_undegradable_protein_percentages(feeds, rdp_percent)

        tdn_limiting = []
        rdp_limiting = []
        for feed in feeds:
            info = feed.info
            rdp_pct = float(rdp_percent[info.rufas_id])
            rup_pct = float(rup_percent[info.rufas_id])
            # 1000 g/kg * percentage fractions; RuFaS endogenous MP = 0.4*11.8*DMI
            rup_and_endogenous = 1000.0 * (rup_pct / 100.0) * (info.dRUP / 100.0) + 4.72
            tdn_limiting.append(
                rup_and_endogenous + 0.64 * (0.13 * 1000.0) * (info.TDN * discount / 100.0)
            )
            rdp_limiting.append(
                rup_and_endogenous + 0.64 * (0.85 * 1000.0) * (rdp_pct / 100.0)
            )
        return np.asarray(tdn_limiting, dtype=float), np.asarray(rdp_limiting, dtype=float)

    @staticmethod
    def _freeze_energy_coefficients(
        cfg: RationConfig, reference_x: npt.NDArray[np.float64]
    ) -> tuple[npt.NDArray[np.float64], float]:
        """Return net-energy Mcal/kg coefficients and FIXED net-energy losses.

        Each ingredient's NASEM digestible-energy density is computed using the
        original RuFaS function at the reference DMI and total starch intake.
        Thereafter, those densities are frozen for the LP. Enteric methane and
        urinary N are treated as the given pen-level values, as in the original.
        """
        dmi = float(np.sum(reference_x))
        body_weight = float(cfg.pen_average_body_weight)
        if dmi <= 0.0 or body_weight <= 0.0:
            raise ValueError("Reference DMI and body weight must be positive")
        if cfg.pen_average_enteric_methane is None or cfg.pen_average_urine_nitrogen is None:
            raise ValueError("NASEM LP requires pen-average methane and urinary N values")

        total_starch = sum(
            float(amount) * float(feed.starch) / 100.0
            for amount, feed in zip(reference_x, cfg.feeds_used)
        )
        efficiency = AnimalModuleConstants.EFF_OF_ME_USE
        energy_per_kg = []
        for feed in cfg.feeds_used:
            digestible_mcal_per_kg = NutritionSupplyCalculator.calculate_NASEM_digestible_energy(
                feeds=[FeedInRation(amount=1.0, info=feed)],
                dry_matter_intake=dmi,
                body_weight=body_weight,
                total_starch=total_starch,
            )
            energy_per_kg.append(efficiency * digestible_mcal_per_kg)

        # Exact RuFaS units: methane g -> kg; urinary nitrogen kg -> g.
        energy_losses = efficiency * (
            13.28 * float(cfg.pen_average_enteric_methane) * GeneralConstants.GRAMS_TO_KG
            + 0.0146 * float(cfg.pen_average_urine_nitrogen) * GeneralConstants.KG_TO_GRAMS
        )
        return np.asarray(energy_per_kg, dtype=float), float(energy_losses)

    @staticmethod
    def _mineral_coefficients(cfg: RationConfig) -> tuple[np.ndarray, np.ndarray]:
        """Digestible Ca and P in grams per kg, matching RuFaS supply methods."""
        calcium_d = {
            FeedComponentType.FORAGE: 0.30,
            FeedComponentType.CONC: 0.60,
            FeedComponentType.MINERAL: 0.95,
        }
        phosphorus_d = {
            FeedComponentType.FORAGE: 0.64,
            FeedComponentType.CONC: 0.70,
            FeedComponentType.MINERAL: 0.80,
        }
        calcium = [1000.0 * f.calcium / 100.0 * calcium_d.get(f.feed_type, 0.0) for f in cfg.feeds_used]
        phosphorus = [1000.0 * f.phosphorus / 100.0 * phosphorus_d.get(f.feed_type, 0.0) for f in cfg.feeds_used]
        return np.asarray(calcium, dtype=float), np.asarray(phosphorus, dtype=float)

    @classmethod
    def _build_linear_model(
        cls, cfg: RationConfig, ref: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, list[str]]:
        """Build common LP inequalities; MP upper bound is handled in two branches.

        A_ub @ x <= b_ub. All coefficients are fixed before the solver runs.
        """
        ndf = np.asarray(cfg.NDF_list, dtype=float)
        fat = np.asarray(cfg.EE_list, dtype=float)
        forage_ndf = np.array(
            [feed.NDF if feed.feed_type is FeedComponentType.FORAGE else 0.0 for feed in cfg.feeds_used],
            dtype=float,
        )
        mp_tdn, mp_rdp = cls._freeze_protein_coefficients(cfg, ref)
        net_energy, net_energy_losses = cls._freeze_energy_coefficients(cfg, ref)
        calcium, phosphorus = cls._mineral_coefficients(cfg)
        req = cfg.animal_requirements
        ones = np.ones(len(cfg.feeds_used), dtype=float)
        mp_req = float(req.metabolizable_protein)
        energy_req = float(req.total_energy_requirement)
        p_req = max(float(req.phosphorus), float(req.process_based_phosphorus))

        rows = [
            -calcium,
            -phosphorus,
            -mp_tdn,  # MP >= min from TDN-limited branch
            -mp_rdp,  # MP >= min from RDP-limited branch
            AnimalModuleConstants.MINIMUM_RATION_NDF - ndf,
            ndf - AnimalModuleConstants.MAXIMUM_RATION_NDF,
            AnimalModuleConstants.MINIMUM_RATION_FORAGE_NDF - forage_ndf,
            fat - AnimalModuleConstants.MAXIMUM_RATION_FAT,
            ones,
            -ones,
            -net_energy,
        ]
        rhs = [
            -float(req.calcium),
            -p_req,
            -mp_req,
            -mp_req,
            0.0,
            0.0,
            0.0,
            0.0,
            float(cfg.initial_dry_matter_requirement) * (1.0 + cfg.dmi_constraint_fraction),
            -float(req.dry_matter) * (1.0 - cfg.dmi_constraint_fraction),
            -energy_req - net_energy_losses,
        ]
        names = [
            "calcium", "phosphorus", "protein_lower_tdn", "protein_lower_rdp",
            "ndf_lower", "ndf_upper", "forage_ndf", "fat", "dmi_upper", "dmi_lower", "nasem_energy",
        ]
        A_ub, b_ub = np.asarray(rows, dtype=float), np.asarray(rhs, dtype=float)
        if not (np.all(np.isfinite(A_ub)) and np.all(np.isfinite(b_ub))):
            raise ValueError("Non-finite linear constraint coefficient detected")
        return A_ub, b_ub, mp_tdn, mp_rdp, names

    @staticmethod
    def _original_constraint_diagnostics(
        cfg: RationConfig, x: np.ndarray
    ) -> tuple[bool, dict[str, float], dict[str, str]]:
        """Evaluate original NASEM functions without calling any optimizer."""
        functions = [
            RationOptimizer.calcium_constraint,
            RationOptimizer.phosphorus_constraint,
            RationOptimizer.protein_constraint_lower,
            RationOptimizer.protein_constraint_upper,
            RationOptimizer.NDF_constraint_lower,
            RationOptimizer.NDF_constraint_upper,
            RationOptimizer.forage_NDF_constraint,
            RationOptimizer.fat_constraint,
            RationOptimizer.DMI_constraint_upper,
            RationOptimizer.DMI_constraint_lower,
            RationOptimizer.NASEM_net_energy_constraint,
        ]
        residuals: dict[str, float] = {}
        errors: dict[str, str] = {}
        for fn in functions:
            try:
                value = float(fn(x, cfg))
                residuals[fn.__name__] = value
                if not np.isfinite(value) or value < -ORIGINAL_CONSTRAINT_TOLERANCE:
                    errors[fn.__name__] = f"original residual = {value:.8g}"
            except Exception as exc:
                residuals[fn.__name__] = float("nan")
                errors[fn.__name__] = f"{type(exc).__name__}: {exc}"
        return not errors, residuals, errors

    def attempt_optimization(
        self,
        nutrient_standard: NutrientStandard,
        pen_average_body_weight: float,
        pen_average_enteric_methane: float | None,
        pen_average_urine_nitrogen: float | None,
        requirements: NutritionRequirements,
        initial_dry_matter_requirement: float,
        initial_protein_requirement: float,
        pen_available_feeds: list[Feed],
        animal_combination: AnimalCombination,
        previous_ration: dict[RUFAS_ID | str, float | str] | None = None,
        user_defined_ration_dictionary: dict[RUFAS_ID, float] | None = None,
        user_defined_ration_tolerance: float | None = None,
    ) -> tuple[OptimizeResult, RationConfig]:
        """Solve two LPs and select the cheapest original-model-feasible candidate.

        Both LPs include the same 11 common inequalities; the MP upper bound
        is a DISJUNCTION (min(A,B) <= U), represented exactly in the *frozen*
        model by separate LPs: A <= U, or B <= U. No nonlinear solve is used.
        """
        sorted_feeds = sorted(pen_available_feeds, key=lambda feed: feed.rufas_id)
        cfg = RationConfig(
            nutrient_standard,
            requirements,
            sorted_feeds,
            initial_dry_matter_requirement,
            initial_protein_requirement,
            pen_average_body_weight,
            pen_average_enteric_methane,
            pen_average_urine_nitrogen,
            animal_combination,
        )
        if nutrient_standard is not NutrientStandard.NASEM:
            raise NotImplementedError("Experimental LP currently supports only NASEM")
        # Preserve baseline failure diagnostics, which inspect cow/heifer constraints.
        self.set_constraints(cfg)

        if user_defined_ration_dictionary:
            if user_defined_ration_tolerance is None:
                raise ValueError("user_defined_ration_tolerance required for user-defined rations")
            user_defined_ration_dictionary = {
                int(k): v for k, v in user_defined_ration_dictionary.items()
            }
            bounds = self._build_bounds_user_defined_ration(
                ration_config=cfg,
                user_defined_ration_dictionary=dict(sorted(user_defined_ration_dictionary.items())),
                user_defined_ration_tolerance=user_defined_ration_tolerance,
            )
        else:
            bounds = self._build_bounds(cfg)
        if not sorted_feeds:
            return OptimizeResult(
                x=np.array([], dtype=float), fun=float("nan"),
                success=False, status=2, message="No feeds available for LP",
                solver="linprog(highs-ds)", original_feasible=False,
            ), cfg
        ref = self._reference_ration(cfg, bounds, previous_ration)

        def failed(message: str, *, status: int = 2) -> tuple[OptimizeResult, RationConfig]:
            return OptimizeResult(
                x=ref.copy(), fun=float(np.dot(cfg.price_list, ref)),
                success=False, status=status, message=message,
                solver="linprog(highs-ds)", original_feasible=False,
                reference_x=ref.copy(),
            ), cfg

        if float(cfg.initial_dry_matter_requirement) <= 0.0:
            return failed("Target DMI must be positive for exact percentage reformulations")
        if float(cfg.animal_requirements.dry_matter) * (1.0 - cfg.dmi_constraint_fraction) <= 0.0:
            return failed("Lower DMI must be positive; otherwise zero-DMI is not equivalent to original constraints")
        if len(bounds) != len(sorted_feeds):
            return failed("LP bounds count differs from feed count")

        A_common, b_common, mp_tdn, mp_rdp, common_names = self._build_linear_model(cfg, ref)
        cfg.linearized_reference_x = ref.copy()
        cfg.linearized_mp_tdn_coefficients = mp_tdn.copy()
        cfg.linearized_mp_rdp_coefficients = mp_rdp.copy()
        cfg.linearized_lp_constraint_names = common_names
        cfg.linearized_lp_constraint_matrix = A_common.copy()
        cfg.linearized_lp_constraint_rhs = b_common.copy()

        upper_mp = float(cfg.initial_protein_requirement) * AnimalModuleConstants.PROTEIN_UPPER_LIMIT_FACTOR
        prices = np.asarray(cfg.price_list, dtype=float)
        attempts: list[dict[str, Any]] = []
        feasible_candidates: list[dict[str, Any]] = []

        for label, upper_coeffs in (("tdn_upper", mp_tdn), ("rdp_upper", mp_rdp)):
            A_ub = np.vstack((A_common, upper_coeffs))
            b_ub = np.append(b_common, upper_mp)
            result = linprog(c=prices, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs-ds")
            record: dict[str, Any] = {
                "branch": label, "lp_success": bool(result.success),
                "lp_status": int(result.status), "lp_message": str(result.message),
            }
            if result.success:
                x = np.asarray(result.x, dtype=float)
                original_feasible, residuals, violations = self._original_constraint_diagnostics(cfg, x)
                record.update({
                    "x": x.copy(), "fun": float(result.fun),
                    "original_feasible": original_feasible,
                    "original_residuals": residuals,
                    "original_violations": violations,
                    "nit": int(result.nit),
                })
                feasible_candidates.append(record)
            attempts.append(record)

        if not feasible_candidates:
            return failed(
                "Neither MP-upper LP branch has a feasible linear solution: "
                + "; ".join(f"{r['branch']}: {r['lp_message']}" for r in attempts)
            )

        # IMPORTANT: priority is original-model feasibility, then lowest cost.
        # If no original-model-feasible LP solution exists, return the cheapest
        # LP candidate but success=False (do not silently feed an invalid ration).
        best = min(
            feasible_candidates,
            key=lambda r: (not r["original_feasible"], r["fun"]),
        )
        original_feasible = bool(best["original_feasible"])
        violated = best["original_violations"]
        message = (
            f"LP ({best['branch']}) succeeded and original NASEM constraints passed"
            if original_feasible
            else f"LP ({best['branch']}) succeeded, but original NASEM constraints failed: "
            + ", ".join(f"{k} ({v})" for k, v in violated.items())
        )
        return OptimizeResult(
            x=best["x"],
            fun=best["fun"],
            success=original_feasible,
            status=0 if original_feasible else 4,
            message=message,
            nit=best["nit"],
            solver="linprog(highs-ds)",
            selected_branch=best["branch"],
            lp_success=True,
            original_feasible=original_feasible,
            original_constraint_residuals=best["original_residuals"],
            original_constraint_violations=violated,
            lp_attempts=attempts,
            reference_x=ref.copy(),
        ), cfg
