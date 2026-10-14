"""Edit this file to experiment. The initial strategy delegates to the baseline."""
from scipy.optimize import OptimizeResult

from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.biophysical.animal.ration.ration_optimizer import RationConfig, RationOptimizer
from RUFAS.data_structures.feed_storage_to_animal_connection import Feed, NutrientStandard, RUFAS_ID

STRATEGY_DESCRIPTION = "Delegates to original RuFaS; no different strategy implemented yet."


class UserRationOptimizer:
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
        # REPLACE THIS DELEGATION with your objective, variables, constraints and
        # solver. Helpers on RationOptimizer and the nutritional calculators can
        # be reused. Return (OptimizeResult(x=..., success=...), RationConfig(...)).
        # x and config.feeds_used MUST both follow ascending rufas_id order.
        # Import RationConfig from ration_optimizer, not another homonymous class.
        return RationOptimizer().attempt_optimization(
            nutrient_standard=nutrient_standard,
            pen_average_body_weight=pen_average_body_weight,
            pen_average_enteric_methane=pen_average_enteric_methane,
            pen_average_urine_nitrogen=pen_average_urine_nitrogen,
            requirements=requirements,
            initial_dry_matter_requirement=initial_dry_matter_requirement,
            initial_protein_requirement=initial_protein_requirement,
            pen_available_feeds=pen_available_feeds,
            animal_combination=animal_combination,
            previous_ration=previous_ration,
            user_defined_ration_dictionary=user_defined_ration_dictionary,
            user_defined_ration_tolerance=user_defined_ration_tolerance,
        )
