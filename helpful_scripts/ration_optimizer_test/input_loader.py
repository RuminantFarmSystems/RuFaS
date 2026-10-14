"""Rebuild the real RuFaS objects without starting InputManager or a simulation."""
import copy
import json
import random
from pathlib import Path

import numpy as np

from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.data_types.intake_option import IntakeOption
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import NutritionSupplyCalculator
from RUFAS.biophysical.animal.ration.amino_acid import EssentialAminoAcidRequirements
from RUFAS.biophysical.animal.ration.ration_manager import RationManager
from RUFAS.data_structures.feed_storage_to_animal_connection import (
    FeedCategorization, FeedComponentType, NASEMFeed, NRCFeed, NutrientStandard,
)
from RUFAS.units import MeasurementUnits

HERE = Path(__file__).resolve().parent


def read_snapshot(directory=HERE):
    """Read once; both child processes and the common evaluator use this snapshot."""
    return {
        "scenario": json.loads((Path(directory) / "scenario.json").read_text(encoding="utf-8")),
        "feeds": json.loads((Path(directory) / "feeds.json").read_text(encoding="utf-8")),
    }


def _id_map(value, ids, name, metadata=False):
    if value is None:
        return None
    # The original optimizer sorts keys before discarding status/objective. Mixed
    # str/int keys fail in Python; those non-input metadata fields are removed here.
    pairs = [(int(k), v) for k, v in value.items() if not (metadata and k in ("status", "objective"))]
    result = dict(pairs)
    if len(result) != len(pairs) or set(result) != set(ids):
        raise ValueError(f"{name} must contain exactly the feed IDs {ids}, without aliases/duplicates")
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not np.isfinite(v) or v < 0
           for v in result.values()):
        raise ValueError(f"{name} values must be finite nonnegative numbers")
    return dict(sorted(result.items()))


def load_inputs(snapshot):
    """Return independent arguments with precisely the attempt_optimization names."""
    scenario = copy.deepcopy(snapshot["scenario"])
    args = scenario["arguments"]
    args["nutrient_standard"] = standard = NutrientStandard(args["nutrient_standard"])
    args["animal_combination"] = AnimalCombination(args["animal_combination"])
    req = args["requirements"]
    req["essential_amino_acids"] = EssentialAminoAcidRequirements(**req["essential_amino_acids"])
    args["requirements"] = NutritionRequirements(**req)
    cls = NASEMFeed if standard is NutrientStandard.NASEM else NRCFeed
    feeds = []
    for raw in copy.deepcopy(snapshot["feeds"]["feeds"]):
        raw["rufas_id"] = int(raw["rufas_id"])
        raw["Fd_Category"] = FeedCategorization(raw["Fd_Category"])
        raw["feed_type"] = FeedComponentType(raw["feed_type"])
        raw["units"] = MeasurementUnits(raw["units"])
        feed = cls(**raw)
        if not 0 <= feed.lower_limit <= feed.limit or not np.isfinite(feed.limit):
            raise ValueError(f"Invalid ingredient bounds for {feed.rufas_id}")
        feeds.append(feed)
    args["pen_available_feeds"] = sorted(feeds, key=lambda f: f.rufas_id)
    ids = [f.rufas_id for f in args["pen_available_feeds"]]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError("Feed IDs must be unique; at least one feed is required")
    args["previous_ration"] = _id_map(args["previous_ration"], ids, "previous_ration", metadata=True)
    manual = args["user_defined_ration_dictionary"] = _id_map(
        args["user_defined_ration_dictionary"], ids, "user_defined_ration_dictionary"
    )
    if manual is not None:
        tolerance = args["user_defined_ration_tolerance"]
        if tolerance is None or not 0 <= tolerance <= 1:
            raise ValueError("Manual ration tolerance must be a fraction in [0, 1]")
        if not np.isclose(sum(manual.values()), 100.0):
            raise ValueError("Manual ration percentages must sum to 100")
    if standard is NutrientStandard.NASEM and any(args[k] is None for k in (
        "pen_average_enteric_methane", "pen_average_urine_nitrogen"
    )):
        raise ValueError("NASEM requires methane (g/day) and urine nitrogen (kg/day)")
    return args


def initialize_globals(snapshot, args):
    """Only globals read by this isolated path; model constants remain unmodified."""
    settings = snapshot["scenario"]["globals"]
    NutritionSupplyCalculator.nutrient_standard = args["nutrient_standard"]
    RationManager.intake_options = {AnimalCombination(k): IntakeOption(v)
                                   for k, v in settings["intake_options"].items()}
    RationManager.intake_values = {AnimalCombination(k): v for k, v in settings["intake_values"].items()}
    RationManager.tolerance = args["user_defined_ration_tolerance"]
    combination = args["animal_combination"]
    RationManager.ration_feeds = {combination: [f.rufas_id for f in args["pen_available_feeds"]]}
    RationManager.user_defined_rations = {combination: args["user_defined_ration_dictionary"]}
    random.seed(snapshot["scenario"]["seed"])
    np.random.seed(snapshot["scenario"]["seed"])
