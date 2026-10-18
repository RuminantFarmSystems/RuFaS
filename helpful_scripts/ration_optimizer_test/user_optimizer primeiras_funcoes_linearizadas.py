"""Edit this file to experiment. The initial strategy delegates to the baseline."""
import random
from scipy.optimize import OptimizeResult, minimize
import numpy as np
import numpy.typing as npt

from RUFAS.data_structures.feed_storage_to_animal_connection import FeedComponentType
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.biophysical.animal.ration.ration_optimizer import RationConfig, RationOptimizer
from RUFAS.data_structures.feed_storage_to_animal_connection import Feed, NutrientStandard, RUFAS_ID

STRATEGY_DESCRIPTION = "LINEARIZANDO CONSTRAINTS: NDF, Forage NDF, Fat"


class UserRationOptimizer(RationOptimizer):
    """Inherit the original helpers and initializer; customize the attempt below.

    Use self.set_constraints(...), self._build_bounds(...), self.objective(...),
    and other inherited methods. super().attempt_optimization(...) calls the
    original implementation when needed.
    """

    @staticmethod
    def NDF_constraint_lower_linear(
        decision_vector, ration_configuration
    ) -> float:

        ndf = np.asarray(ration_configuration.NDF_list)

        minimum = AnimalModuleConstants.MINIMUM_RATION_NDF

        return float(np.dot(decision_vector, ndf - minimum))


    @staticmethod
    def NDF_constraint_upper_linear(
        decision_vector, ration_configuration
    ) -> float:

        ndf = np.asarray(ration_configuration.NDF_list)

        maximum = AnimalModuleConstants.MAXIMUM_RATION_NDF

        return float(np.dot(decision_vector, maximum - ndf))


    @staticmethod
    def forage_NDF_constraint_linear(
        decision_vector, ration_configuration
    ) -> float:

        forage_ndf = np.array([
            feed.NDF
            if feed.feed_type == FeedComponentType.FORAGE
            else 0.0
            for feed in ration_configuration.feeds_used
        ])

        minimum = AnimalModuleConstants.MINIMUM_RATION_FORAGE_NDF

        return float(np.dot(decision_vector, forage_ndf - minimum))


    @staticmethod
    def fat_constraint_linear(
        decision_vector, ration_configuration
    ) -> float:

        fat = np.asarray(ration_configuration.EE_list)

        maximum = AnimalModuleConstants.MAXIMUM_RATION_FAT

        return float(np.dot(decision_vector, maximum - fat))


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
        sorted_pen_available_feeds = sorted(pen_available_feeds, key=lambda feed: feed.rufas_id)

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

        
        #Ingredientes list
        price_list_length = len(ration_config.price_list)
        initial_decision_vector= [1.0] + [random.random() * 10 for _ in range(price_list_length - 1)]
        initial_decision_vector=np.array(initial_decision_vector,dtype=float)

        #Bounds
        bounds = list(zip(ration_config.feed_minimum_list, ration_config.feed_maximum_list))

        #Cut the initial decision vector to be within the bounds
        initial_decision_vector = self._check_initial_bounds(bounds, initial_decision_vector)

        #Set NASEM constraints
        self.NASEM_constraint_functions = [
            self.calcium_constraint,#Linear
            self.phosphorus_constraint,#Linear
            self.protein_constraint_lower,#N Linear
            self.protein_constraint_upper,#N Linear
            self.NDF_constraint_lower_linear,#To be converted as linear
            self.NDF_constraint_upper_linear,#To be converted as linear
            self.forage_NDF_constraint_linear,#To be converted as linear
            self.fat_constraint_linear,#To be converted as linear
            self.DMI_constraint_upper,#Linear
            self.DMI_constraint_lower,#Linear
            self.NASEM_net_energy_constraint,#N Linear
        ]

        self.cow_constraints = [
            {"type": "ineq", "fun": func, "args": (ration_config,)} for func in self.NASEM_constraint_functions
        ]
        
        self.heifer_constraints = self.cow_constraints

        constraints_to_use = self._select_constraints(animal_combination)

        optimized_ration_attempt = minimize(
            self.objective,
            initial_decision_vector,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints_to_use,
            args=ration_config,
        )

        return optimized_ration_attempt, ration_config
