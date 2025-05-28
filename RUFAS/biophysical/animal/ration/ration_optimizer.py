import random
from scipy.optimize import OptimizeResult, minimize
import numpy as np
import scipy
import numpy.typing as npt
from typing import List, Tuple, Dict, Callable, Any
from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import NutritionSupplyCalculator, FeedInRation
from RUFAS.enums import AnimalCombination
from RUFAS.units import MeasurementUnits
from RUFAS.general_constants import GeneralConstants
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants

from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.data_structures.feed_storage_to_animal_connection import RUFAS_ID, Feed

from RUFAS.output_manager import OutputManager

om = OutputManager()


class RationConfig:
    """
    stuff
    """

    def __init__(
        self,
        animal_requirements: NutritionRequirements = None,
        pen_available_feeds: List[Feed] = [],
        pen_average_body_weight: float = 0,
    ) -> None:
        self.animal_requirements = animal_requirements
        self.pen_average_body_weight = pen_average_body_weight
        self.print_print = False

        self.feeds_used = pen_available_feeds

        self.price_list: List[float] = [feed.purchase_cost for feed in self.feeds_used]
        self.feed_minimum_list: List[float] = [feed.lower_limit for feed in self.feeds_used]
        self.feed_maximum_list: List[float] = [feed.limit for feed in self.feeds_used]
        self.TDN_list: List[float] = [feed.TDN for feed in self.feeds_used]
        self.NDF_list: List[float] = [feed.NDF for feed in self.feeds_used]
        self.EE_list: List[float] = [feed.EE for feed in self.feeds_used]


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
            self.NE_maintenance_and_activity_constraint,
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
            cons
            for cons in self.cow_constraints
            if cons["fun"] not in [self.NE_total_constraint, self.NE_lactation_constraint]
        ]

    @staticmethod
    def convert_decision_vec_to_feeds(
        ration_configuration: RationConfig, decision_vector: npt.NDArray[np.float64]
    ) -> List[FeedInRation]:
        decision_vector_dict = dict(
            zip([feed.rufas_id for feed in ration_configuration.feeds_used], decision_vector)
        ).items()

        feeds = [
            FeedInRation(
                amount=amount,
                info=next((feed for feed in ration_configuration.feeds_used if feed.rufas_id == rufas_id), None),
            )
            for rufas_id, amount in decision_vector_dict
        ]
        return feeds

    @classmethod
    def make_ration_from_solution(
        cls,
        pen_available_feeds: List[Feed],
        solution: scipy.optimize.OptimizeResult,
    ) -> Dict[str, float | str]:
        ration: Dict[str, float | str] = {}
        for position_in_list in range(len(pen_available_feeds)):
            kg_to_feed = solution.x[position_in_list]
            ration[getattr(pen_available_feeds[position_in_list], "rufas_id")] = round(kg_to_feed, 6)
        return ration

    @staticmethod
    def NE_total_constraint(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:
        feeds = RationOptimizer.convert_decision_vec_to_feeds(ration_configuration, decision_vector)
        intake_nutrient_discount = NutritionSupplyCalculator._calculate_nutrient_intake_discount(
            feeds, ration_configuration.pen_average_body_weight
        )
        # TODO reduce the overlap in all methods, if "saving" to ration_confguration is more efficient
        actual_digestible_energy = {feed.info.rufas_id: feed.info.DE * intake_nutrient_discount for feed in feeds}
        actual_metabolizable_energy = NutritionSupplyCalculator._calculate_actual_metabolizable_energy(
            feeds, actual_digestible_energy
        )

        maintenance_energy_supply = NutritionSupplyCalculator._calculate_actual_maintenance_net_energy(
            feeds=feeds, actual_metabolizable_energy=actual_metabolizable_energy
        )

        growth_energy_supply = NutritionSupplyCalculator._calculate_actual_growth_net_energy(
            feeds=feeds, actual_metabolizable_energy=actual_metabolizable_energy
        )

        lactation_energy_supply = NutritionSupplyCalculator._calculate_actual_lactation_net_energy(
            feeds=feeds,
            actual_metabolizable_energy=actual_metabolizable_energy,
            actual_digestible_energy=actual_digestible_energy,
        )

        total_energy_supply = max(maintenance_energy_supply, growth_energy_supply, lactation_energy_supply)
        # total_energy_supply = maintenance_energy_supply + growth_energy_supply + lactation_energy_supply

        total_energy_requirement = ration_configuration.animal_requirements.total_energy_requirement
        return total_energy_supply - total_energy_requirement

    @staticmethod
    def NE_maintenance_and_activity_constraint(
        decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig
    ) -> float:
        feeds = RationOptimizer.convert_decision_vec_to_feeds(ration_configuration, decision_vector)
        intake_nutrient_discount = NutritionSupplyCalculator._calculate_nutrient_intake_discount(
            feeds=feeds, body_weight=ration_configuration.pen_average_body_weight
        )
        actual_digestible_energy = {feed.info.rufas_id: feed.info.DE * intake_nutrient_discount for feed in feeds}
        actual_metabolizable_energy = NutritionSupplyCalculator._calculate_actual_metabolizable_energy(
            feeds=feeds, actual_digestible_energy=actual_digestible_energy
        )
        actual_maintenance_net_energy_supply = NutritionSupplyCalculator._calculate_actual_maintenance_net_energy(
            actual_metabolizable_energy=actual_metabolizable_energy, feeds=feeds
        )

        actual_maintenance_and_activity_net_energy_requirement = (
            ration_configuration.animal_requirements.maintenance_energy
            + ration_configuration.animal_requirements.activity_energy
        )

        return actual_maintenance_net_energy_supply - actual_maintenance_and_activity_net_energy_requirement

    @staticmethod
    def NE_lactation_constraint(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:

        feeds = RationOptimizer.convert_decision_vec_to_feeds(ration_configuration, decision_vector)
        intake_nutrient_discount = NutritionSupplyCalculator._calculate_nutrient_intake_discount(
            feeds=feeds, body_weight=ration_configuration.pen_average_body_weight
        )
        actual_digestible_energy = {feed.info.rufas_id: feed.info.DE * intake_nutrient_discount for feed in feeds}
        actual_metabolizable_energy = NutritionSupplyCalculator._calculate_actual_metabolizable_energy(
            feeds=feeds, actual_digestible_energy=actual_digestible_energy
        )

        actual_lactation_net_energy_supply = NutritionSupplyCalculator._calculate_actual_lactation_net_energy(
            feeds=feeds,
            actual_metabolizable_energy=actual_metabolizable_energy,
            actual_digestible_energy=actual_digestible_energy,
        )
        actual_lactation_net_energy_requirement = ration_configuration.animal_requirements.lactation_energy
        actual_pregnancy_net_energy_requirement = ration_configuration.animal_requirements.pregnancy_energy

        return actual_lactation_net_energy_supply - (
            actual_lactation_net_energy_requirement + actual_pregnancy_net_energy_requirement
        )

    @staticmethod
    def NE_growth_constraint(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:
        feeds = RationOptimizer.convert_decision_vec_to_feeds(ration_configuration, decision_vector)
        intake_nutrient_discount = NutritionSupplyCalculator._calculate_nutrient_intake_discount(
            feeds=feeds, body_weight=ration_configuration.pen_average_body_weight
        )
        actual_digestible_energy = {feed.info.rufas_id: feed.info.DE * intake_nutrient_discount for feed in feeds}
        actual_metabolizable_energy = NutritionSupplyCalculator._calculate_actual_metabolizable_energy(
            feeds=feeds, actual_digestible_energy=actual_digestible_energy
        )
        actual_growth_net_energy_supply = NutritionSupplyCalculator._calculate_actual_growth_net_energy(
            feeds=feeds, actual_metabolizable_energy=actual_metabolizable_energy
        )
        actual_growth_net_energy_requirement = ration_configuration.animal_requirements.growth_energy

        return actual_growth_net_energy_supply - actual_growth_net_energy_requirement

    @staticmethod
    def phosphorus_constraint(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:
        feeds = RationOptimizer.convert_decision_vec_to_feeds(ration_configuration, decision_vector)
        phosphorus_supply = NutritionSupplyCalculator._calculate_phosphorus_supply(feeds=feeds)
        actual_phosphorus_requirement = max(
            ration_configuration.animal_requirements.phosphorus,
            ration_configuration.animal_requirements.process_based_phosphorus,
        )

        return phosphorus_supply - actual_phosphorus_requirement

    @staticmethod
    def protein_constraint_lower(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:
        feeds = RationOptimizer.convert_decision_vec_to_feeds(ration_configuration, decision_vector)
        dry_matter_intake = sum(decision_vector)
        intake_nutrient_discount = NutritionSupplyCalculator._calculate_nutrient_intake_discount(
            feeds=feeds, body_weight=ration_configuration.pen_average_body_weight
        )
        actual_tdn_percentages = {feed.info.rufas_id: feed.info.TDN * intake_nutrient_discount for feed in feeds}
        metabolizable_protein_supply = NutritionSupplyCalculator._calculate_metabolizable_protein_supply(
            feeds=feeds,
            dry_matter_intake=dry_matter_intake,
            actual_tdn_percentages=actual_tdn_percentages,
            body_weight=ration_configuration.pen_average_body_weight,
        )
        actual_metabolizable_protein_requirement = ration_configuration.animal_requirements.metabolizable_protein

        return metabolizable_protein_supply - actual_metabolizable_protein_requirement

    @staticmethod
    def protein_constraint_upper(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:
        feeds = RationOptimizer.convert_decision_vec_to_feeds(ration_configuration, decision_vector)
        dry_matter_intake = sum(decision_vector)
        intake_nutrient_discount = NutritionSupplyCalculator._calculate_nutrient_intake_discount(
            feeds=feeds, body_weight=ration_configuration.pen_average_body_weight
        )
        actual_tdn_percentages = {feed.info.rufas_id: feed.info.TDN * intake_nutrient_discount for feed in feeds}
        metabolizable_protein_supply = NutritionSupplyCalculator._calculate_metabolizable_protein_supply(
            feeds=feeds,
            dry_matter_intake=dry_matter_intake,
            actual_tdn_percentages=actual_tdn_percentages,
            body_weight=ration_configuration.pen_average_body_weight,
        )
        actual_metabolizable_protein_requirement = ration_configuration.animal_requirements.metabolizable_protein

        return (
            actual_metabolizable_protein_requirement * AnimalModuleConstants.PROTEIN_UPPER_LIMIT_FACTOR
        ) - metabolizable_protein_supply

    @staticmethod
    def calcium_constraint(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:

        feeds = RationOptimizer.convert_decision_vec_to_feeds(ration_configuration, decision_vector)

        calcium_supply = NutritionSupplyCalculator._calculate_calcium_supply(feeds)
        calcium_requirement = ration_configuration.animal_requirements.calcium

        return calcium_supply - calcium_requirement

    @staticmethod
    def NDF_constraint_lower(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:
        dry_matter_intake = sum(decision_vector)
        if dry_matter_intake != 0:
            return float(
                (
                    (sum(np.multiply(decision_vector, ration_configuration.NDF_list)) / dry_matter_intake)
                    - AnimalModuleConstants.MINIMUM_RATION_NDF
                )
            )
        else:
            return -1.0

    @staticmethod
    def NDF_constraint_upper(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:
        dry_matter_intake = sum(decision_vector)
        if dry_matter_intake != 0:
            return float(
                (
                    -(sum(np.multiply(decision_vector, ration_configuration.NDF_list)) / dry_matter_intake)
                    + AnimalModuleConstants.MAXIMUM_RATION_NDF
                )
            )
        else:
            return -1.0

    @staticmethod
    def forage_NDF_constraint(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:
        dry_matter_intake = sum(decision_vector)
        if dry_matter_intake != 0:
            feeds = RationOptimizer.convert_decision_vec_to_feeds(ration_configuration, decision_vector)
            forage_NDF_supply = NutritionSupplyCalculator._calculate_forage_neutral_detergent_fiber_content(feeds)
            return (
                forage_NDF_supply / dry_matter_intake
            ) * GeneralConstants.FRACTION_TO_PERCENTAGE - AnimalModuleConstants.MINIMUM_RATION_FORAGE_NDF
        else:
            return -1.0

    @staticmethod
    def fat_constraint(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:
        dry_matter_intake = sum(decision_vector)
        if dry_matter_intake != 0:
            return float(
                -(sum(np.multiply(decision_vector, ration_configuration.EE_list)) / dry_matter_intake)
                + AnimalModuleConstants.MINIMUM_RATION_FAT
            )
        else:
            return -1.0

    @staticmethod
    def DMI_constraint_lower(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:
        return float(
            (sum(decision_vector))
            - (
                ration_configuration.animal_requirements.dry_matter
                * (1 - AnimalModuleConstants.DMI_CONSTRAINT_FRACTION)
            )
        )

    @staticmethod
    def DMI_constraint_upper(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:
        return float(
            -(sum(decision_vector))
            + (
                ration_configuration.animal_requirements.dry_matter
                * (1 + AnimalModuleConstants.DMI_CONSTRAINT_FRACTION)
            )
        )

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

    def attempt_optimization(
        self,
        pen_average_body_weight: float,
        requirements: NutritionRequirements,
        pen_available_feeds: List[Feed],
        animal_combination: AnimalCombination,
        previous_ration: Dict[RUFAS_ID | str, float | str] | None = None,
    ) -> Tuple[OptimizeResult | None, RationConfig]:
        ration_config = RationConfig(requirements, pen_available_feeds, pen_average_body_weight)

        if previous_ration:
            x0: List[float] = []
            prev_ration = previous_ration.copy()
            for key, value in prev_ration.items():
                if key not in ["status", "objective"]:
                    x0.append(value)
        else:
            n = len(ration_config.price_list)
            x0 = [1] + [random.random() * 10 for _ in range(n - 1)]

        set_bounds = list(
            zip([(lim) for lim in ration_config.feed_minimum_list], [(lim) for lim in ration_config.feed_maximum_list])
        )
        for i in range(0, len(set_bounds)):
            if x0[i] < set_bounds[i][0] or x0[i] > set_bounds[i][1]:
                x0[i] = np.clip(x0[i], set_bounds[i][0], set_bounds[i][1])

        arguments = (ration_config,)
        self.set_constraints(arguments=arguments)

        if animal_combination is AnimalCombination.LAC_COW:
            constraints_to_use = self.cow_constraints
        elif animal_combination in [
            AnimalCombination.GROWING,
            AnimalCombination.CLOSE_UP,
            AnimalCombination.GROWING_AND_CLOSE_UP,
        ]:
            constraints_to_use = self.heifer_constraints
        else:
            raise ValueError("Invalid animal combination: " + str(animal_combination))

        optimized_ration_attempt = minimize(
            self.objective,
            x0,
            method="SLSQP",
            bounds=set_bounds,
            constraints=constraints_to_use,
            args=arguments,
        )

        return optimized_ration_attempt, ration_config

    @staticmethod
    def is_constraint_violated(
        solution_x: npt.NDArray[np.float64],
        constraint: Dict[str, Callable[[Any, Any], float] | Tuple[RationConfig] | str],
        ration_config: RationConfig,
    ) -> bool:
        """
        Helper function to check a solution dictionary to see if a given constraint
            in a list of constraints was met.

        Parameters
        ----------
        solution_x: numpy nd array, e.g. npt.NDArray
            solution.x array from minimize function used in ration_NLP.py
        constraint: dict[str, Any]
            constraint function as defined in ration_NLP.py
        ration_config : RationConfig object
            Attributes are animal requirement and feed supply information required for optimization

        Returns
        -------
        bool
            True if the constraint method was not met.
        """
        result = constraint["fun"](solution_x, ration_config)
        if constraint["type"] == "ineq" and result < 0:
            return True
        elif constraint["type"] == "eq" and not np.isclose(result, 0):
            return True
        else:
            return False

    @staticmethod
    def find_failed_constraints(
        solution_x: npt.NDArray[np.float64],
        constraints: List[Dict[str, Callable[[Any, Any], float]]],
        ration_config: RationConfig,
    ) -> List[Dict[str, Callable[[Any, Any], float]]]:
        """
        Returns list of constraints that were not met during optmization step.

        Parameters
        ----------
        solution_x: numpy nd array, e.g. npt.NDArray
            solution.x is from minimize function used in ration_NLP.py,
                solution obj itself is returned as  <dict class 'scipy.optimize._optimize.OptimizeResult'>

        constraints: List[dict[str, Callable]]
            list of constraint functions as defined in ration_NLP.py

        ration_config : RationConfig object
            Attributes are animal requirement and feed supply information required for optimization

        Returns
        -------
        List[dict[str,Callable]]
            the same type of list as the constraints themselves
                just filtered such that the ones that failed are returned
        """
        return list(
            filter(
                lambda c: RationOptimizer.is_constraint_violated(solution_x, c, ration_config),
                constraints,
            )
        )

    @staticmethod
    def handle_failed_constraints(
        num_attempts: int,
        solution: scipy.optimize.OptimizeResult,
        ration_config: RationConfig,
        animal_combination: AnimalCombination,
        pen_id: RUFAS_ID,
        pen_available_feeds: Any,
        average_nutrient_requirements: NutritionRequirements,
        sim_day: int = 9999,
        info_map: Dict[str, Any] = {},
    ) -> None:
        """
        Handle and log failed constraints during the ration optimization process.

        This method identifies and logs the constraints that failed during the optimization
        process for a specific pen of animals. It gathers relevant information about the
        failed attempt, including the simulation day, the number of attempts, the failed
        constraints, the attempted ration, and the pen's nutrient requirements. This
        information is then added to the output manager via a variable.

        Parameters:
        -----------
        # TODO fill these in fully

        info_map : Dict[str, Any]
            A dictionary containing additional information to be logged with the failed
            constraints summary.

        Returns:
        --------
        None
        """
        # TODO get the time! For sim day
        constraints_failed_list = []
        ro = RationOptimizer()
        arguments = (ration_config,)
        ro.set_constraints(arguments=arguments)
        if animal_combination == AnimalCombination.LAC_COW:
            failed_constraints = RationOptimizer.find_failed_constraints(solution.x, ro.cow_constraints, ration_config)
        else:
            failed_constraints = RationOptimizer.find_failed_constraints(
                solution.x, ro.heifer_constraints, ration_config
            )

        if failed_constraints:
            for constr in failed_constraints:
                constraints_failed_list.append(constr["fun"].__name__)
        fail_summary = {
            "simulation day": sim_day,
            "attempt number": num_attempts,
            "constraints_failed_dict": constraints_failed_list,
            "ration_attempted": ro.make_ration_from_solution(pen_available_feeds, solution),
            "pen requirements": average_nutrient_requirements,
        }
        fail_summary_units = {
            "simulation day": MeasurementUnits.SIMULATION_DAY,
            "attempt number": MeasurementUnits.UNITLESS,
            "constraints_failed_dict": MeasurementUnits.UNITLESS,
            "ration_attempted": MeasurementUnits.UNITLESS,
            "pen requirements": {
                "NEmaint_requirement": MeasurementUnits.MEGACALORIES,
                "NEa_requirement": MeasurementUnits.MEGACALORIES,
                "NEg_requirement": MeasurementUnits.MEGACALORIES,
                "NEpreg_requirement": MeasurementUnits.MEGACALORIES,
                "NEl_requirement": MeasurementUnits.MEGACALORIES,
                "MP_requirement": MeasurementUnits.GRAMS,
                "Ca_requirement": MeasurementUnits.GRAMS,
                "P_req": MeasurementUnits.GRAMS,
                "DMIest_requirement": MeasurementUnits.KILOGRAMS,
                "avg_BW": MeasurementUnits.KILOGRAMS,
                "avg_milk_production_reduction_pen": MeasurementUnits.KILOGRAMS,
            },
        }
        om.add_variable(
            f"failed_constraint_summary_for_pen_{pen_id}",
            fail_summary,
            dict(info_map, **{"units": fail_summary_units}),
        )
