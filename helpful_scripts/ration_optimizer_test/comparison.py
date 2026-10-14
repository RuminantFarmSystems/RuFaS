"""Evaluate both vectors against fresh original constraints and original prices."""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from input_loader import HERE, initialize_globals, load_inputs
from RUFAS.biophysical.animal.ration.ration_optimizer import RationConfig, RationOptimizer


def run_strategy(snapshot, strategy, directory=HERE):
    """Process isolation also protects against class-level changes and import effects."""
    try:
        completed = subprocess.run(
            [sys.executable, str(Path(directory) / "worker.py"), strategy],
            input=json.dumps(snapshot), text=True, capture_output=True,
            timeout=snapshot["scenario"]["timeout_seconds"], check=False,
        )
        if completed.returncode:
            raise RuntimeError(f"Process exited {completed.returncode}: {completed.stderr.strip()}")
        report = json.loads(completed.stdout)
        if completed.stderr:
            report["stderr"] = completed.stderr.strip()
        return report
    except (subprocess.TimeoutExpired, ValueError, RuntimeError, OSError) as exc:
        return {"valid": False, "error": f"{type(exc).__name__}: {exc}"}


def reference_problem(snapshot):
    args = load_inputs(snapshot)
    initialize_globals(snapshot, args)
    config = RationConfig(
        args["nutrient_standard"], args["requirements"], args["pen_available_feeds"],
        args["initial_dry_matter_requirement"], args["initial_protein_requirement"],
        args["pen_average_body_weight"], args["pen_average_enteric_methane"],
        args["pen_average_urine_nitrogen"], args["animal_combination"],
    )
    original = RationOptimizer()
    original.set_constraints(config)
    constraints = original._select_constraints(args["animal_combination"])
    bounds = original._build_bounds(config)
    if args["user_defined_ration_dictionary"]:
        bounds = original._build_bounds_user_defined_ration(
            config, args["user_defined_ration_dictionary"], args["user_defined_ration_tolerance"]
        )
    return config, constraints, bounds


def evaluate(snapshot, report):
    """Ignore the strategy's objective, prices, requirements and constraint list."""
    report = dict(report)
    report["feasible"] = None
    if not report.get("valid"):
        return report
    try:
        config, constraints, bounds = reference_problem(snapshot)
        x = np.array(report["x"], dtype=float)
        ids = [f.rufas_id for f in config.feeds_used]
        if report["ids"] != ids or x.shape != (len(ids),) or not np.isfinite(x).all():
            raise ValueError("Invalid worker vector/ID mapping")
        report["cost"] = float(np.dot(x, config.price_list))
        report["dry_matter"] = float(x.sum())
        tolerance = snapshot["scenario"]["tolerances"]["constraint_residual"]
        rows = []
        for constraint in constraints:
            name = constraint["fun"].__name__
            try:
                residue = float(constraint["fun"](x, config))
                ok = bool(np.isfinite(residue) and (
                    residue >= -tolerance if constraint["type"] == "ineq" else abs(residue) <= tolerance
                ))
                rows.append({"name": name, "residue": residue, "ok": ok})
            except Exception as exc:
                rows.append({"name": name, "residue": None, "ok": False, "error": str(exc)})
        for feed, amount, (lower, upper) in zip(config.feeds_used, x, bounds):
            for suffix, residue in (("lower", amount - lower), ("upper", upper - amount)):
                rows.append({"name": f"feed_{feed.rufas_id}_{suffix}",
                             "residue": float(residue), "ok": bool(residue >= -tolerance)})
        report["constraints"] = rows
        report["feasible"] = all(row["ok"] for row in rows)
    except Exception as exc:
        report["evaluation_error"] = f"{type(exc).__name__}: {exc}"
    return report


def _fmt(value):
    if value is None:
        return "N/A"
    if isinstance(value, bool):
        return "YES" if value else "NO"
    if isinstance(value, (float, np.floating)):
        return f"{value:.8g}"
    return str(value)


def print_comparison(snapshot, reports):
    config, constraints, bounds = reference_problem(snapshot)
    baseline, user = reports
    print("\nONE RATION ATTEMPT — kg DM / animal / day")
    print(snapshot["scenario"]["description"])
    print(f"Seed: {snapshot['scenario']['seed']}; sorted feed IDs: {[f.rufas_id for f in config.feeds_used]}")
    for name, report in zip(("BASELINE", "USER"), reports):
        print(f"\n{name}: {report.get('description', 'Unavailable')}")
        for label, key in (("Solver success", "success"), ("Structurally valid", "valid"),
                           ("Original constraints feasible", "feasible"), ("Status", "status"),
                           ("Message", "message"), ("Attempt time (s)", "seconds"),
                           ("Recalculated cost ($/animal/day)", "cost"),
                           ("Total DM (kg/animal/day)", "dry_matter"), ("Solver objective (fun)", "fun")):
            print(f"  {label}: {_fmt(report.get(key))}")
        for key in ("error", "evaluation_error", "log", "stderr"):
            if report.get(key):
                print(f"  {key}: {report[key]}")
        for warning in report.get("warnings", []):
            print(f"  RuFaS warning: {warning}")
    if "cost" in baseline and "cost" in user:
        difference = user["cost"] - baseline["cost"]
        percent = difference / baseline["cost"] * 100 if baseline["cost"] != 0 else None
        print(f"\nCost delta (user - baseline): {difference:+.8g} $/animal/day; {_fmt(percent)} %")
        print(f"Absolute cost difference: {abs(difference):.8g} $/animal/day")
        if not (baseline.get("feasible") and user.get("feasible")):
            print("Cost comparison is descriptive only: at least one ration is infeasible or unevaluated.")
    else:
        print("\nCost delta: N/A (a comparable vector is missing).")
    print("\nINGREDIENTS (effective bounds include manual inclusion limits when configured)")
    print(f"{'ID / name':48} {'baseline':>12} {'user':>12} {'delta':>12} {'[lower, upper]':>22}")
    for i, (feed, bound) in enumerate(zip(config.feeds_used, bounds)):
        a = baseline["x"][i] if baseline.get("valid") else None
        b = user["x"][i] if user.get("valid") else None
        delta = b - a if a is not None and b is not None else None
        name = f"{feed.rufas_id} / {getattr(feed, 'Name', feed.feed_type.value)}"
        print(f"{name:48} {_fmt(a):>12} {_fmt(b):>12} {_fmt(delta):>12} {str(bound):>22}")
    tol = snapshot["scenario"]["tolerances"]
    print(f"\nORIGINAL CONSTRAINT RESIDUALS: pass when residual >= -{tol['constraint_residual']:g}")
    print(f"Negative-vector structural tolerance: {tol['nonnegative_kg']:g} kg DM; values are NOT clipped.")
    print("Units: energy Mcal; protein/Ca/P g; DMI/feed bounds kg; NDF/forage NDF/fat percentage points.")
    row_maps = [{row["name"]: row for row in r.get("constraints", [])} for r in reports]
    names = [c["fun"].__name__ for c in constraints]
    names += [f"feed_{f.rufas_id}_{side}" for f in config.feeds_used for side in ("lower", "upper")]
    print(f"{'Constraint':38} {'baseline residual / pass':>28} {'user residual / pass':>28}")
    for name in names:
        cells = []
        for rows in row_maps:
            row = rows.get(name)
            cells.append(f"{_fmt(row['residue'])} / {_fmt(row['ok'])}" if row else "N/A")
        print(f"{name:38} {cells[0]:>28} {cells[1]:>28}")
        for label, rows in zip(("baseline", "user"), row_maps):
            if rows.get(name, {}).get("error"):
                print(f"  {label} evaluation error: {rows[name]['error']}")
    print("\nOne attempt only: no milk/DMI retry, manual fallback, herd, weather or simulation loop.")
