"""Targeted integration/contract checks; run this file directly with Python."""
import copy
from dataclasses import fields
import inspect
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
from scipy.optimize import OptimizeResult
from comparison import evaluate, reference_problem, run_strategy
from input_loader import HERE, initialize_globals, load_inputs, read_snapshot
from user_optimizer import UserRationOptimizer
from worker import validate_result
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.biophysical.animal.ration.amino_acid import EssentialAminoAcidRequirements
from RUFAS.biophysical.animal.ration.ration_manager import RationManager
from RUFAS.biophysical.animal.ration.ration_optimizer import RationOptimizer
from RUFAS.data_structures.feed_storage_to_animal_connection import Feed, NASEMFeed, NRCFeed, NutrientStandard


class HarnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = read_snapshot()
        cls.baseline = evaluate(cls.snapshot, run_strategy(cls.snapshot, "baseline"))
        cls.user = evaluate(cls.snapshot, run_strategy(cls.snapshot, "user"))

    def test_real_baseline_feasible_and_delegation_identical(self):
        for report in (self.baseline, self.user):
            self.assertTrue(report["valid"], report)
            self.assertTrue(report["success"], report)
            self.assertTrue(report["feasible"], report)
        np.testing.assert_array_equal(self.baseline["x"], self.user["x"])
        self.assertEqual(self.baseline["cost"], self.user["cost"])
        self.assertEqual(inspect.signature(RationOptimizer.attempt_optimization),
                         inspect.signature(UserRationOptimizer.attempt_optimization))

    def test_loader_real_types_independent_inputs_and_integer_keys(self):
        snapshot = copy.deepcopy(self.snapshot)
        ids = self.baseline["ids"]
        snapshot["scenario"]["arguments"]["previous_ration"] = dict(zip(map(str, ids), self.baseline["x"]))
        snapshot["scenario"]["arguments"]["previous_ration"].update(status="ok", objective=1)
        args = load_inputs(snapshot)
        self.assertIs(args["nutrient_standard"], NutrientStandard.NASEM)
        self.assertIs(args["animal_combination"], AnimalCombination.LAC_COW)
        self.assertIsInstance(args["requirements"], NutritionRequirements)
        self.assertIsInstance(args["requirements"].essential_amino_acids, EssentialAminoAcidRequirements)
        self.assertTrue(all(isinstance(f, NASEMFeed) for f in args["pen_available_feeds"]))
        self.assertEqual(list(args["previous_ration"]), ids)
        self.assertTrue(all(type(k) is int for k in args["previous_ration"]))
        self.assertIsNone(args["user_defined_ration_dictionary"])
        self.assertNotEqual(args["initial_dry_matter_requirement"], args["requirements"].dry_matter)
        self.assertNotEqual(args["initial_protein_requirement"], args["requirements"].metabolizable_protein)
        args["requirements"].calcium = -100
        args["pen_available_feeds"][0].purchase_cost = -100
        self.assertGreater(load_inputs(snapshot)["requirements"].calcium, 0)
        self.assertGreater(load_inputs(snapshot)["pen_available_feeds"][0].purchase_cost, 0)

    def test_nrc_reconstruction_and_optional_none(self):
        snapshot = copy.deepcopy(self.snapshot)
        args = snapshot["scenario"]["arguments"]
        args.update(nutrient_standard="NRC", pen_average_enteric_methane=None, pen_average_urine_nitrogen=None)
        # Synthetic schema fixture only; this does not claim NASEM composition is NRC data.
        base_fields = {f.name for f in fields(Feed)}
        snapshot["feeds"]["feeds"] = [dict({k: v for k, v in f.items() if k in base_fields},
                                           non_fiber_carb=25.0, PAF=1.0) for f in snapshot["feeds"]["feeds"]]
        loaded = load_inputs(snapshot)
        self.assertIs(loaded["nutrient_standard"], NutrientStandard.NRC)
        self.assertIsNone(loaded["pen_average_enteric_methane"])
        self.assertTrue(all(isinstance(f, NRCFeed) for f in loaded["pen_available_feeds"]))

    def test_invalid_vectors_and_wrong_mapping(self):
        config, _, _ = reference_problem(self.snapshot)
        ids = self.baseline["ids"]
        bad_vectors = [np.zeros((1, len(ids))), np.zeros(len(ids)-1),
                       [float("nan")]*len(ids), [float("inf")]*len(ids),
                       [-1.0]*len(ids), ["1"]*len(ids), [1j]*len(ids)]
        for vector in bad_vectors:
            with self.subTest(vector=vector), self.assertRaises(ValueError):
                validate_result((OptimizeResult(x=vector, success=True), config), ids, 1e-8)
        for result in [None, (OptimizeResult(success=True), config),
                       (OptimizeResult(x=self.baseline["x"], success="yes"), config),
                       (OptimizeResult(x=self.baseline["x"], success=True), object())]:
            with self.subTest(result=result), self.assertRaises(ValueError):
                validate_result(result, ids, 1e-8)
        config.feeds_used.reverse()
        with self.assertRaises(ValueError):
            validate_result((OptimizeResult(x=self.baseline["x"], success=True), config), ids, 1e-8)

    def test_numerical_tolerance_does_not_clip(self):
        config, _, _ = reference_problem(self.snapshot)
        x = np.array(self.baseline["x"])
        x[0] = -5e-9
        checked = validate_result((OptimizeResult(x=x, success=True), config), self.baseline["ids"], 1e-8)
        self.assertEqual(checked[0], -5e-9)

    def test_infeasible_despite_success_and_independent_objective(self):
        report = dict(self.baseline, x=[0.01]*len(self.baseline["ids"]), success=True, fun=-1e9)
        checked = evaluate(self.snapshot, report)
        self.assertTrue(checked["success"])
        self.assertFalse(checked["feasible"])
        self.assertGreater(checked["cost"], 0)
        self.assertTrue(any(not c["ok"] for c in checked["constraints"]))
        report = dict(self.baseline, success=False)
        self.assertTrue(evaluate(self.snapshot, report)["feasible"])

    def test_original_phosphorus_and_protein_rules(self):
        config, constraints, _ = reference_problem(self.snapshot)
        x = np.array(self.baseline["x"])
        p1 = RationOptimizer.phosphorus_constraint(x, config)
        config.animal_requirements.phosphorus += 1  # still below process-based 55 g
        self.assertEqual(p1, RationOptimizer.phosphorus_constraint(x, config))
        lo = RationOptimizer.protein_constraint_lower(x, config)
        hi = RationOptimizer.protein_constraint_upper(x, config)
        config.animal_requirements.metabolizable_protein += 10
        self.assertAlmostEqual(RationOptimizer.protein_constraint_lower(x, config), lo-10)
        self.assertAlmostEqual(RationOptimizer.protein_constraint_upper(x, config), hi)

    def test_manual_bounds_and_dmi_globals(self):
        snapshot = copy.deepcopy(self.snapshot)
        args = snapshot["scenario"]["arguments"]
        ids = self.baseline["ids"]
        manual = {str(k): 0.0 for k in ids}
        manual["110"] = 100.0
        args.update(user_defined_ration_dictionary=manual, user_defined_ration_tolerance=0.1)
        config, _, bounds = reference_problem(snapshot)
        self.assertEqual(bounds[ids.index(110)], (25*1.1*0.9, 25*1.1*1.1))
        self.assertEqual(bounds[0], (0.0, 0.0))
        snapshot["scenario"]["globals"]["intake_options"]["lac_cow"] = "set_DMI"
        snapshot["scenario"]["globals"]["intake_values"]["lac_cow"] = 24.0
        config, _, bounds = reference_problem(snapshot)
        self.assertEqual(config.dmi_constraint_fraction, 0.0)
        np.testing.assert_allclose(bounds[ids.index(110)], (22.5, 27.5), rtol=0, atol=1e-12)
        invalid = dict(self.baseline, x=[1.0]*len(ids))
        rows = {c["name"]: c for c in evaluate(snapshot, invalid)["constraints"]}
        self.assertFalse(rows["feed_44_upper"]["ok"])
        # Original clipping semantics pin a disjoint manual target at the feed limit.
        snapshot["feeds"]["feeds"][ids.index(110)]["limit"] = 10.0
        _, _, bounds = reference_problem(snapshot)
        self.assertEqual(bounds[ids.index(110)], (10.0, 10.0))

    def test_user_failure_and_mutations_do_not_contaminate_baseline(self):
        snapshot_before = copy.deepcopy(self.snapshot)
        initialize_globals(self.snapshot, load_inputs(self.snapshot))
        globals_before = copy.deepcopy(RationManager.intake_options)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            folder = root / "helpful_scripts" / "ration_optimizer_test"
            shutil.copytree(HERE, folder, ignore=shutil.ignore_patterns("__pycache__"))
            (root / "RUFAS").symlink_to(HERE.parents[1] / "RUFAS", target_is_directory=True)
            (folder / "user_optimizer.py").write_text('''\
from RUFAS.biophysical.animal.ration.ration_optimizer import RationOptimizer
from RUFAS.biophysical.animal.ration.ration_manager import RationManager
STRATEGY_DESCRIPTION = "Mutation then deliberate failure"
class UserRationOptimizer:
    def attempt_optimization(self, **args):
        args["requirements"].calcium = -10000
        args["pen_available_feeds"].clear()
        RationManager.intake_options.clear()
        RationOptimizer.objective = staticmethod(lambda *args: -10000)
        raise RuntimeError("deliberate failure")
''')
            failure = run_strategy(self.snapshot, "user", folder)
            self.assertFalse(failure["valid"])
            self.assertIn("deliberate failure", failure["error"])
            after = evaluate(self.snapshot, run_strategy(self.snapshot, "baseline", folder))
            np.testing.assert_array_equal(self.baseline["x"], after["x"])
            self.assertEqual(self.baseline["cost"], after["cost"])
            cli = subprocess.run([sys.executable, str(folder / "main.py")], text=True, capture_output=True)
            self.assertEqual(cli.returncode, 1, cli.stderr)
            self.assertIn("deliberate failure", cli.stdout)
            self.assertIn("Original constraints feasible: YES", cli.stdout)
            self.assertIn("Cost delta: N/A", cli.stdout)
        self.assertEqual(self.snapshot, snapshot_before)
        self.assertEqual(RationManager.intake_options, globals_before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
