"""Edit this file to experiment. The initial strategy delegates to the baseline."""
from scipy.optimize import OptimizeResult

from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.biophysical.animal.ration.ration_optimizer import RationConfig, RationOptimizer
from RUFAS.data_structures.feed_storage_to_animal_connection import Feed, NutrientStandard, RUFAS_ID

STRATEGY_DESCRIPTION = "First test"


class UserRationOptimizer(RationOptimizer):
    """Inherit the original helpers and initializer; customize the attempt below.

    Use self.set_constraints(...), self._build_bounds(...), self.objective(...),
    and other inherited methods. super().attempt_optimization(...) calls the
    original implementation when needed.
    """

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

        ration_config = RationConfig(
            nutrient_standard,
            requirements,
            sorted_pen_available_feeds,
            initial_dry_matter_requirement,
            initial_protein_requirement,
            pen_average_body_weight,
            pen_average_enteric_methane,
            pen_average_urine_nitrogen,
            animal_combination,
        )

        sorted_pen_available_feeds = sorted(pen_available_feeds, key=lambda feed: feed.rufas_id)
        
        #Ingredientes list
        price_list_length = len(ration_config.price_list)
        initial_decision_vector= [1.0] + [random.random() * 10 for _ in range(price_list_length - 1)]
        initial_decision_vector=np.array(initial_decision_vector,dtype=float)

        #Bounds
        bounds = list(zip(ration_config.feed_minimum_list, ration_config.feed_maximum_list))



        ration_config = RationConfig(
            nutrient_standard,
            requirements,
            sorted_pen_available_feeds,
            initial_dry_matter_requirement,
            initial_protein_requirement,
            pen_average_body_weight,
            pen_average_enteric_methane,
            pen_average_urine_nitrogen,
            animal_combination
        )

        
        return 2
