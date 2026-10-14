"""Internal child entry point. main.py is the public no-argument command."""
import contextlib
import io
import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
from scipy.optimize import OptimizeResult
from input_loader import initialize_globals, load_inputs
from RUFAS.biophysical.animal.ration.ration_optimizer import RationConfig, RationOptimizer
from RUFAS.output_manager import OutputManager


def validate_result(result, expected_ids, tolerance):
    if not isinstance(result, tuple) or len(result) != 2:
        raise ValueError("Expected tuple[OptimizeResult, RationConfig]")
    solution, config = result
    if not isinstance(solution, OptimizeResult) or not isinstance(config, RationConfig):
        raise ValueError("Wrong OptimizeResult or ration_optimizer.RationConfig type")
    if not isinstance(solution.get("success"), (bool, np.bool_)):
        raise ValueError("success must be boolean")
    if [f.rufas_id for f in config.feeds_used] != expected_ids:
        raise ValueError("config.feeds_used must match the input IDs in ascending order")
    vector = np.asarray(solution.get("x"))
    if vector.ndim != 1 or len(vector) != len(expected_ids):
        raise ValueError("x must be one-dimensional with one position per ingredient")
    if vector.dtype.kind not in "iuf" or not np.isfinite(vector).all():
        raise ValueError("x must contain only finite real numbers")
    if np.any(vector < -tolerance):
        raise ValueError(f"Negative quantities below {-tolerance:g} kg DM/animal/day")
    return vector.astype(float)


def _scalar(value):
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    return value if value is None or isinstance(value, (str, int, float, bool)) else str(value)


def execute(snapshot, strategy):
    args = load_inputs(snapshot)
    expected_ids = [f.rufas_id for f in args["pen_available_feeds"]]
    if strategy == "baseline":
        optimizer = RationOptimizer()
        description = "Original RuFaS attempt_optimization / SLSQP"
    elif strategy == "user":
        # Never imported in the baseline process or common evaluator.
        from user_optimizer import UserRationOptimizer, STRATEGY_DESCRIPTION
        optimizer = UserRationOptimizer()
        description = STRATEGY_DESCRIPTION
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
    initialize_globals(snapshot, args)
    report = {"valid": False, "description": description}
    start = time.perf_counter()
    try:
        result = optimizer.attempt_optimization(**args)  # exactly ONE attempt
        report["seconds"] = time.perf_counter() - start
        if isinstance(result, tuple) and result and isinstance(result[0], OptimizeResult):
            for key in ("success", "fun", "status", "message"):
                report[key] = _scalar(result[0].get(key))
        vector = validate_result(result, expected_ids, snapshot["scenario"]["tolerances"]["nonnegative_kg"])
        report.update(valid=True, x=vector.tolist(), ids=expected_ids)
    except Exception as exc:
        report.update(error=f"{type(exc).__name__}: {exc}")
    finally:
        report.setdefault("seconds", time.perf_counter() - start)
    report["warnings"] = [str(message) for entry in OutputManager().warnings_pool.values()
                          for message in entry["values"]]
    return report


if __name__ == "__main__":
    capture = io.StringIO()
    try:
        snapshot = json.load(sys.stdin)
        with contextlib.redirect_stdout(capture):
            report = execute(snapshot, sys.argv[1])
    except Exception as exc:
        report = {"valid": False, "error": f"{type(exc).__name__}: {exc}"}
    report["log"] = capture.getvalue()
    print(json.dumps(report, allow_nan=False))
