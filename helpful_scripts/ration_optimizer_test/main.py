"""Run from any working directory; no PYTHONPATH or simulation setup required."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from input_loader import read_snapshot, load_inputs
from comparison import evaluate, print_comparison, run_strategy


def main():
    try:
        snapshot = read_snapshot()
        load_inputs(snapshot)  # fail early on malformed shared input, before either attempt
        reports = [evaluate(snapshot, run_strategy(snapshot, name)) for name in ("baseline", "user")]
        print_comparison(snapshot, reports)
    except Exception as exc:
        print(f"Scenario/comparison error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    return 0 if all(r.get("valid") and r.get("success") and r.get("feasible") for r in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())
