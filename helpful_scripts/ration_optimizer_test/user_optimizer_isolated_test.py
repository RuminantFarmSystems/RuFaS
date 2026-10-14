"""Run only the user strategy once, validate its contract and display its result."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from comparison import _fmt, evaluate, reference_problem, run_strategy
from input_loader import load_inputs, read_snapshot


def print_result(snapshot, report):
    print("\nUSER OPTIMIZER — ONE ISOLATED ATTEMPT")
    print(snapshot["scenario"]["description"])
    print(f"Seed: {snapshot['scenario']['seed']}")
    print(f"Strategy: {report.get('description', 'Unavailable')}")
    for label, key in (
        ("Solver success", "success"),
        ("Structurally valid return", "valid"),
        ("Original constraints feasible", "feasible"),
        ("Status", "status"),
        ("Message", "message"),
        ("Attempt time (s)", "seconds"),
        ("Recalculated cost ($/animal/day)", "cost"),
        ("Total DM (kg/animal/day)", "dry_matter"),
        ("Solver objective (fun)", "fun"),
    ):
        print(f"  {label}: {_fmt(report.get(key))}")
    for key in ("error", "evaluation_error", "log", "stderr"):
        if report.get(key):
            print(f"  {key}: {report[key]}")
    for warning in report.get("warnings", []):
        print(f"  RuFaS warning: {warning}")

    tolerances = snapshot["scenario"]["tolerances"]
    print(f"\nNonnegativity tolerance: {tolerances['nonnegative_kg']:g} kg DM (no clipping).")
    if not report.get("valid"):
        print("No valid ration vector available; ingredient and constraint tables are unavailable.")
        return

    config, _, bounds = reference_problem(snapshot)
    print("\nRATION — quantities and effective bounds in kg DM/animal/day")
    print(f"{'ID / ingredient':48} {'quantity':>14} {'lower':>14} {'upper':>14}")
    for feed, amount, (lower, upper) in zip(config.feeds_used, report["x"], bounds):
        name = f"{feed.rufas_id} / {getattr(feed, 'Name', feed.feed_type.value)}"
        print(f"{name:48} {_fmt(amount):>14} {_fmt(lower):>14} {_fmt(upper):>14}")

    print(f"\nORIGINAL CONSTRAINTS — pass when residual >= -{tolerances['constraint_residual']:g}")
    print("Units: energy Mcal; protein/Ca/P g; DMI/feed bounds kg; NDF/forage NDF/fat percentage points.")
    print(f"{'Constraint':38} {'residual':>16} {'pass':>8}")
    for row in report.get("constraints", []):
        print(f"{row['name']:38} {_fmt(row['residue']):>16} {_fmt(row['ok']):>8}")
        if row.get("error"):
            print(f"  Evaluation error: {row['error']}")
    if not report.get("constraints"):
        print("Constraint evaluation unavailable; see the evaluation error above.")


def main():
    try:
        snapshot = read_snapshot()
        load_inputs(snapshot)
        # The worker validates tuple/OptimizeResult/RationConfig, success, x and IDs.
        # evaluate() checks original constraints without running the baseline solver.
        report = evaluate(snapshot, run_strategy(snapshot, "user"))
        print_result(snapshot, report)
    except Exception as exc:
        print(f"Scenario/result error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    return 0 if report.get("valid") and report.get("success") and report.get("feasible") else 1


if __name__ == "__main__":
    raise SystemExit(main())
