import random
from scipy.optimize import OptimizeResult, minimize
import numpy as np
import numpy.typing as npt
from typing import List, Tuple, Dict, Callable, Any
from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import NutritionSupplyCalculator, FeedInRation
from RUFAS.routines.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.enums import AnimalCombination

from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionSupply, NutritionRequirements
from RUFAS.data_structures.feed_storage_to_animal_connection import RUFAS_ID, Feed

x0: List[float] = []
# change from x0 to ration_attempt

# constraints_to_use: List[Dict[str, Callable[[Any, Any], float] | Tuple[RationConfig] | str] | str] = []

# bnds: List[Tuple[float, float]] = [(0, 100)]


class RationConfig:
    """
    stuff
    """
    def __init__(self,
             animal_requirements: NutritionRequirements,
             feeds: List[Feed],
             pen_average_body_weight: float) -> None:
        self.animal_requirements = animal_requirements
        self.pen_average_body_weight = pen_average_body_weight

        self.feeds_used = feeds

        self.price_list: List[float] = [feed.purchase_cost for feed in self.feeds_used]
        self.feed_minimum_list: List[float] = [feed.lower_limit for feed in self.feeds_used]
        self.feed_maximum_list: List[float] = [feed.limit for feed in self.feeds_used]
        self.TDN_list: List[float] = [feed.TDN for feed in self.feeds_used]
        self.NDF_list: List[float] = [feed.NDF for feed in self.feeds_used]
        self.EE_list: List[float] = [feed.NDF for feed in self.feeds_used]

class RationOptimizer:
    """
    stuff
    """
    def __init__(self) -> None:
        """initializes RationOptimizer object"""

        self.constraint_functions: List[Callable[[Any, Any], float]] = []
        self.cow_constraints: List[Dict[str, Callable[[Any, Any], float] | Tuple[RationConfig] | str] | str] = []
        self.heifer_constraints: List[Dict[str, Callable[[Any, Any], float] | Tuple[RationConfig] | str] | str] = []

    def set_constraints(self, arguments: Tuple[RationConfig]) -> None:
        # establishing the constraints of the NLP

        self.constraint_functions = [
            self.NE_total_constraint,
            self.NE_maintenance_constraint,
            self.NE_lactation_constraint,
            self.NE_growth_constraint,
            self.calcium_constraint,
            self.phosphorus_constraint,
            self.protein_constraint_lower,
            self.protein_constraint_upper,
            self.NDF_constraint_lower,
            self.NDF_constraint_upper,
            self.forage_NDF_constraint,
            self.fat_constraint,
            self.DMI_constraint_upper,
            self.DMI_constraint_lower,
        ]

        self.cow_constraints = [{"type": "ineq", "fun": func, "args": arguments} for func in self.constraint_functions]

        self.heifer_constraints = [
            cons for cons in self.cow_constraints if cons["fun"] not in [
                self.NE_total_constraint, self.NE_lactation_constraint]
        ]
    # helpers

    @staticmethod
    def convert_decision_vec_to_feeds(ration_configuration: RationConfig,
                                      decision_vector: npt.NDArray[np.float64]) -> List[FeedInRation]:
        
        decision_vector_dict = dict(zip(ration_configuration.price_list, decision_vector)).items()

        feeds = [
            FeedInRation(amount=amount,
                         info=next((feed for feed in ration_configuration.feeds_used if feed.rufas_id == rufas_id), None))
            for rufas_id, amount in decision_vector_dict
        ]
        return feeds

    # all of the constraints
    @staticmethod
    def NE_total_constraint(
        decision_vector: npt.NDArray[np.float64],
        ration_configuration: RationConfig
    ) -> float:
        feeds = RationOptimizer.convert_decision_vec_to_feeds(ration_configuration,
                                                              decision_vector)
        intake_nutrient_discount = NutritionSupplyCalculator._calculate_nutrient_intake_discount(
            feeds,
            ration_configuration.pen_average_body_weight)
        # TODO reduce the overlap in all methods, if "saving" to ration_confguration is possible
        actual_digestible_energy = {feed.info.rufas_id: feed.info.DE * intake_nutrient_discount for feed in feeds}
        actual_metabolizable_energy = NutritionSupplyCalculator._calculate_actual_metabolizable_energy(
            feeds,
            actual_digestible_energy)

        maintenance_energy_supply = NutritionSupplyCalculator._calculate_actual_maintenance_net_energy(
            feeds=feeds,
            actual_metabolizable_energy=actual_metabolizable_energy)

        growth_energy_supply = NutritionSupplyCalculator._calculate_actual_growth_net_energy(
            feeds=feeds,
            actual_metabolizable_energy=actual_metabolizable_energy)
        
        lactation_energy_supply = NutritionSupplyCalculator._calculate_actual_lactation_net_energy(
            feeds=feeds,
            actual_metabolizable_energy=actual_metabolizable_energy,
            actual_digestible_energy=actual_digestible_energy)
        
        total_energy_supply = maintenance_energy_supply + growth_energy_supply + lactation_energy_supply

        total_energy_requirement = ration_configuration.animal_requirements.total_energy_requirement

        return total_energy_supply - total_energy_requirement

    @staticmethod
    def NE_maintenance_constraint(
        decision_vector: npt.NDArray[np.float64],
        ration_configuration: RationConfig
    ) -> float:
        feeds = RationOptimizer.convert_decision_vec_to_feeds(ration_configuration,
                                                              decision_vector)
        intake_nutrient_discount = NutritionSupplyCalculator._calculate_nutrient_intake_discount(
            feeds=feeds,
            body_weight=ration_configuration.pen_average_body_weight)
        actual_digestible_energy = {feed.info.rufas_id: feed.info.DE * intake_nutrient_discount for feed in feeds}
        actual_metabolizable_energy = NutritionSupplyCalculator._calculate_actual_metabolizable_energy(
        feeds=feeds,
        actual_digestible_energy=actual_digestible_energy)
        actual_maintenance_net_energy_supply = NutritionSupplyCalculator._calculate_actual_maintenance_net_energy(
        actual_metabolizable_energy=actual_metabolizable_energy,
                                                                                                                feeds=feeds)
    
        actual_maintenance_net_energy_requirement = ration_configuration.animal_requirements.maintenance_energy
        return actual_maintenance_net_energy_requirement - actual_maintenance_net_energy_supply

    @staticmethod
    def NE_lactation_constraint(
        decision_vector: npt.NDArray[np.float64],
        ration_configuration: RationConfig
    ) -> float:
        
        feeds = RationOptimizer.convert_decision_vec_to_feeds(
            ration_configuration,
            decision_vector)
        intake_nutrient_discount = NutritionSupplyCalculator._calculate_nutrient_intake_discount(
            feeds=feeds,
            body_weight=ration_configuration.pen_average_body_weight)
        actual_digestible_energy = {feed.info.rufas_id: feed.info.DE * intake_nutrient_discount for feed in feeds}
        actual_metabolizable_energy = NutritionSupplyCalculator._calculate_actual_metabolizable_energy(
            feeds=feeds,
            actual_digestible_energy=actual_digestible_energy)
        
        actual_lactation_net_energy_supply = NutritionSupplyCalculator._calculate_actual_lactation_net_energy(
            feeds=feeds,
            actual_metabolizable_energy=actual_metabolizable_energy,
            actual_digestible_energy=actual_digestible_energy)    
        actual_lactation_net_energy_requirement = ration_configuration.animal_requirements.lactation_energy

        return actual_lactation_net_energy_requirement - actual_lactation_net_energy_supply

    @staticmethod
    def NE_growth_constraint(
        decision_vector: npt.NDArray[np.float64],
        ration_configuration: RationConfig
    ) -> float:
        feeds = RationOptimizer.convert_decision_vec_to_feeds(
            ration_configuration,
            decision_vector)
        intake_nutrient_discount = NutritionSupplyCalculator._calculate_nutrient_intake_discount(
            feeds=feeds,
            body_weight=ration_configuration.pen_average_body_weight)
        actual_digestible_energy = {feed.info.rufas_id: feed.info.DE * intake_nutrient_discount for feed in feeds}
        actual_metabolizable_energy = NutritionSupplyCalculator._calculate_actual_metabolizable_energy(
            feeds=feeds,
            actual_digestible_energy=actual_digestible_energy
        )
        actual_growth_net_energy_supply = NutritionSupplyCalculator._calculate_actual_growth_net_energy(
            feeds=feeds,
            actual_metabolizable_energy=actual_metabolizable_energy
        )
        actual_growth_net_energy_requirement = ration_configuration.animal_requirements.growth_energy
        return actual_growth_net_energy_supply - actual_growth_net_energy_requirement
        

    @staticmethod
    def phosphorus_constraint(
        decision_vector: npt.NDArray[np.float64],
        ration_configuration: RationConfig
    ) -> float:
        feeds = RationOptimizer.convert_decision_vec_to_feeds(
            ration_configuration,
            decision_vector)
        phosphorus_supply = NutritionSupplyCalculator._calculate_phosphorus_supply(
            feeds=feeds
        )
        actual_phosphorus_requirement = max(ration_configuration.animal_requirements.phosphorus,
                                            ration_configuration.animal_requirements.process_based_phosphorus)
        return phosphorus_supply - actual_phosphorus_requirement

    @staticmethod
    def protein_constraint_lower(
        decision_vector: npt.NDArray[np.float64],
        ration_configuration: RationConfig
    ) -> float:
        feeds = RationOptimizer.convert_decision_vec_to_feeds(
            ration_configuration,
            decision_vector)
        dry_matter_intake = sum(decision_vector)
        intake_nutrient_discount = NutritionSupplyCalculator._calculate_nutrient_intake_discount(
            feeds=feeds,
            body_weight=ration_configuration.pen_average_body_weight)
        actual_tdn_percentages = {feed.info.rufas_id: feed.info.TDN * intake_nutrient_discount for feed in feeds}
        metabolizable_protein_supply = NutritionSupplyCalculator._calculate_metabolizable_protein_supply(
            feeds=feeds,
            dry_matter_intake=dry_matter_intake,
            actual_tdn_percentages=actual_tdn_percentages,
            body_weight=ration_configuration.pen_average_body_weight
        )
        actual_metabolizable_protein_requirement = ration_configuration.animal_requirements.metabolizable_protein
        return metabolizable_protein_supply - actual_metabolizable_protein_requirement

    @staticmethod
    def protein_constraint_upper(
        decision_vector: npt.NDArray[np.float64],
        ration_configuration: RationConfig
    ) -> float:
        feeds = RationOptimizer.convert_decision_vec_to_feeds(
            ration_configuration,
            decision_vector)
        dry_matter_intake = sum(decision_vector)
        intake_nutrient_discount = NutritionSupplyCalculator._calculate_nutrient_intake_discount(
            feeds=feeds,
            body_weight=ration_configuration.pen_average_body_weight)
        actual_tdn_percentages = {feed.info.rufas_id: feed.info.TDN * intake_nutrient_discount for feed in feeds}
        metabolizable_protein_supply = NutritionSupplyCalculator._calculate_metabolizable_protein_supply(
            feeds=feeds,
            dry_matter_intake=dry_matter_intake,
            actual_tdn_percentages=actual_tdn_percentages,
            body_weight=ration_configuration.pen_average_body_weight
        )
        actual_metabolizable_protein_requirement = ration_configuration.animal_requirements.metabolizable_protein
        return (actual_metabolizable_protein_requirement * AnimalModuleConstants.PROTEIN_UPPER_LIMIT_FACTOR)\
            - metabolizable_protein_supply

    @staticmethod
    def calcium_constraint(
        decision_vector: npt.NDArray[np.float64],
        ration_configuration: RationConfig
    ) -> float:

        feeds = RationOptimizer.convert_decision_vec_to_feeds(ration_configuration,
                                                              decision_vector)
        
        calcium_supply = NutritionSupplyCalculator._calculate_calcium_supply(feeds)
        calcium_requirement = ration_configuration.animal_requirements.calcium
        return calcium_supply - calcium_requirement

    @staticmethod
    def NDF_constraint_lower(
        decision_vector: npt.NDArray[np.float64],
        ration_configuration: RationConfig
    ) -> float:
        dry_matter_intake = sum(decision_vector)
        if dry_matter_intake != 0:
            return float((
                -(sum(np.multiply(decision_vector, ration_configuration.NDF_list)) / dry_matter_intake) - 25))
            # TODO Make the 25 above a constant or ration_config value
        else:
            return -1.0

    @staticmethod
    def NDF_constraint_upper(
        decision_vector: npt.NDArray[np.float64],
        ration_configuration: RationConfig
    ) -> float:
        dry_matter_intake = sum(decision_vector)
        if dry_matter_intake != 0:
            return float((
                -(sum(np.multiply(decision_vector, ration_configuration.NDF_list)) / dry_matter_intake) + 45))
            # TODO Make the 45 above a constant or ration_config value
        else:
            return -1.0

    @staticmethod
    def forage_NDF_constraint(
        decision_vector: npt.NDArray[np.float64],
        ration_configuration: RationConfig
    ) -> float:
        dry_matter_intake = sum(decision_vector)
        if dry_matter_intake != 0:
            feeds = RationOptimizer.convert_decision_vec_to_feeds(
                ration_configuration,
                decision_vector)
            forage_NDF_supply = NutritionSupplyCalculator._calculate_forage_neutral_detergent_fiber_content(feeds)
            return forage_NDF_supply - 15
            # TODO make this 15 a constant or rationconfig val
        else:
            return -1.0
    
    @staticmethod
    def fat_constraint(
        decision_vector: npt.NDArray[np.float64],
        ration_configuration: RationConfig
    ) -> float:
        dry_matter_intake = sum(decision_vector)    
        if dry_matter_intake != 0:
            return float(-(sum(np.multiply(decision_vector, ration_configuration.EE_list)) / dry_matter_intake) + 7)
        # TODO make the 7 a constant or ration config val
        else:
            return -1.0

    @staticmethod
    def DMI_constraint_lower(
        decision_vector: npt.NDArray[np.float64],
        ration_configuration: RationConfig
    ) -> float:
        return float((sum(decision_vector)) - (
            ration_configuration.animal_requirements.dry_matter
            * (1 - AnimalModuleConstants.DMI_CONSTRAINT_PERCENT)
        ))

    @staticmethod
    def DMI_constraint_upper(
        decision_vector: npt.NDArray[np.float64],
        ration_configuration: RationConfig
    ) -> float:
        return float(-(sum(decision_vector)) - (
            ration_configuration.animal_requirements.dry_matter
            * (1 + AnimalModuleConstants.DMI_CONSTRAINT_PERCENT)
        ))

    # the objective

    @staticmethod
    def objective(decision_vector: npt.NDArray[np.float64], ration_config: RationConfig) -> float:
        """
        Sets up the objective function in the optimize function for the non-linear
        program. Whenever the paramert x is used, it refers to the "decision vetor
        of the NLP" which means it is a list of solutions where each value in the
        list corresponds to the amount of a given feed (kg) in the formulated diet.
        The goal of this NLP is to minimize the cost of all feeds while satisfying
        all "constraints", which just means the diet fulfills the average nutrient
        requirements in the pen.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector of the NLP.
        ration_config: RationConfig object
            Attributes are animal requirement and feed supply information required for optimization.

        Returns
        -------
        float

        """
        return float(sum(np.multiply(decision_vector, ration_config.price_list)))


    def attempt_optimization(self,
                             pen_average_body_weight: float,
                             requirements: NutritionRequirements,
                             available_feeds: List[Feed],
                             animal_combination: AnimalCombination,
                             previous_ration: Dict[RUFAS_ID | str, float | str] | None = None,
                             ) -> Tuple[OptimizeResult | None, RationConfig]:
        ration_config = RationConfig(
            requirements,
            available_feeds,
            pen_average_body_weight)

        if previous_ration:
            x0: List[float] = []
            prev_ration = previous_ration.copy()
            for key, value in prev_ration.items():
                if key not in ["status", "objective"]:
                    x0.append(value)
        else:
            n = len(ration_config.price_list)
            x0 = [1] + [random.random() * 10 for _ in range(n - 1)]

        set_bounds = list(zip(
            [(lim) for lim in ration_config.feed_minimum_list],
            [(lim) for lim in ration_config.feed_maximum_list]))

        if animal_combination is AnimalCombination.LAC_COW:
            constraints_to_use = self.cow_constraints
        elif animal_combination in [AnimalCombination.GROWING,
                                    AnimalCombination.CLOSE_UP,
                                    AnimalCombination.GROWING_AND_CLOSE_UP,]:
            constraints_to_use = self.heifer_constraints
        else:
            raise ValueError("Invalid animal combination: " + str(animal_combination))        
        
        arguments = (ration_config,)
        
        # kronk.jpg
        optimized_ration_attempt = minimize(
            RationOptimizer.objective,
            x0,
            method="SLSQP",
            bounds=set_bounds,
            constraints=constraints_to_use,
            args=arguments,
            )

        return optimized_ration_attempt, ration_config



