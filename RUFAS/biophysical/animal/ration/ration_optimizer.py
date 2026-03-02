import random
from scipy.optimize import OptimizeResult, minimize
import numpy as np
import numpy.typing as npt
from typing import Callable, Any, Sequence, Optional
from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import NutritionSupplyCalculator, FeedInRation
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.units import MeasurementUnits
from RUFAS.general_constants import GeneralConstants
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants

from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements
from RUFAS.data_structures.feed_storage_to_animal_connection import RUFAS_ID, Feed, NutrientStandard

from RUFAS.output_manager import OutputManager


class RationConfig:
    """
    RationConfig provides a structured way to represent the collection of animal requirements and feed supply
    information for the ration formulation process.

    Attributes
    ----------
    nutrient_standard : NutrientStandard
        Nutrient standard used in supply and requirement calculations.
    animal_requirements : NutritionRequirements
        Nutrition requirements for pen, used in constraint methods.
    pen_average_body_weight : float
        Average body weight in pen, used in constraint methods.
    initial_dry_matter_requirement : float
        Dry matter intake requirement at start of ration formulation.
    initial_protein_requirement : float
        Metabolizable protein requirement at start of ration formulation.
    feeds_used : list[Feed]
        List of Feeds used in ration formulation.
    price_list : list[float]
        Price for each feed used in ration formulation.
    feed_minimum_list : list[float]
        Minimum amount allowed for each feed used in formulation, kg.
    feed_maximum_list : list[float]
        Maxmimum amount allowed for each feed used in formulation, kg.
    TDN_list : list[float]
        TDN for each feed used in ration formulation.
    NDF_list: list[float]
        NDF for each feed used in ration formulation.
    EE_list : list[float]
        EE for each feed used in ration formulation.

    Parameters
    ----------
    animal_requirements : NutritionRequirements
        Nutrition requirements for pen, used in constraint methods.
    pen_available_feeds : list[Feed], optional
        List of available feeds in pen.
    pen_average_body_weight : float
        Average body weight in pen, used in constraint methods.

    """

    def __init__(
        self,
        nutrient_standard: NutrientStandard,
        animal_requirements: NutritionRequirements,
        pen_available_feeds: Optional[list[Feed]],
        initial_dry_matter_requirement: float,
        initial_protein_requirement: float,
        pen_average_body_weight: float = 0,
        pen_average_enteric_methane: float | None = None,
        pen_average_urine_nitrogen: float | None = None,
    ) -> None:
        """
        Initialize the RationConfig class with the provided feed information. If the input
        is a list, it should have a length corresponding to the decision vector.

        Parameters
        ----------
        nutrient_standard : NutrientStandard
            Nutrient standard used in supply and requirement calculations.
        animal_requirements : NutritionRequirements
            Nutrition requirements for pen, used in constraint methods.
        pen_available_feeds : list[Feed], optional
            List of Feeds used in ration formulation.
        initial_dry_matter_requirement : float
            Dry matter intake requirement at start of ration formulation, kg per cow per day.
        initial_protein_requirement : float
            Metabolizable protein requirement at start of ration formulation.
        pen_average_body_weight : float
            Average body weight in pen, used in constraint methods, kg.
        pen_average_enteric_methane : float
            Average enteric methane produced in pen, used in constraint methods, g.
        pen_average_urine_nitrogen : float
            Average urine nitrogen generated in pen, used in constraint methods, kg.
        """
        self.nutrient_standard = nutrient_standard
        if pen_available_feeds is None:
            pen_available_feeds = []
        self.animal_requirements = animal_requirements
        self.pen_average_body_weight = pen_average_body_weight
        self.pen_average_enteric_methane = pen_average_enteric_methane
        self.pen_average_urine_nitrogen = pen_average_urine_nitrogen
        self.initial_dry_matter_requirement: float = initial_dry_matter_requirement
        self.initial_protein_requirement: float = initial_protein_requirement

        self.feeds_used = pen_available_feeds

        self.price_list: list[float] = [feed.purchase_cost for feed in self.feeds_used]
        self.feed_minimum_list: list[float] = [feed.lower_limit for feed in self.feeds_used]
        self.feed_maximum_list: list[float] = [feed.limit for feed in self.feeds_used]
        self.TDN_list: list[float] = [feed.TDN for feed in self.feeds_used]
        self.NDF_list: list[float] = [feed.NDF for feed in self.feeds_used]
        self.EE_list: list[float] = [feed.EE for feed in self.feeds_used]


class RationOptimizer:
    """
    Nonlinear programming methods to optimally formulate a ration by comparing feed supply and the requirements for
    animals in a given pen.

    This class sets an objective, defines constraints, attempts optimization using scipy's minimize method, and
    reports unsuccessful optimization attempts to the user.

    Constraint methods compare the supply of an attempted ration to specific limits on a per nutrient/energy basis.

    For constraints with lower thresholds, the minimum value is subtracted from the supply.

    For constraints with upper thresholds, the supply is subtracted from the maximum value.

    In either case, if the difference is non negative, then the solution is considered a 'success' in scipy.minimize.

    """

    def __init__(self) -> None:
        """Initializes RationOptimizer object"""

        self.constraint_functions: list[Callable[[Any, Any], float]] = []
        self.cow_constraints: list[dict[str, Callable[[Any, Any], float] | tuple[RationConfig] | str] | str] = []
        self.heifer_constraints: list[dict[str, Callable[[Any, Any], float] | tuple[RationConfig] | str] | str] = []

    def set_constraints(self, ration_config: RationConfig) -> None:
        """
        Defines lists of constraint methods to use for different pens.

        Parameters
        ----------
        ration_config : tuple[RationConfig]
            RationConfig used in constraint methods.

        """

        self.NRC_constraint_functions = [
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
        self.NASEM_constraint_functions = [
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
            self.NASEM_net_energy_constraint,
        ]

        if ration_config.nutrient_standard is NutrientStandard.NRC:
            self.cow_constraints = [
                {"type": "ineq", "fun": func, "args": (ration_config,)} for func in self.NRC_constraint_functions
            ]

            self.heifer_constraints = [
                constraint
                for constraint in self.cow_constraints
                if constraint["fun"] not in [self.NE_total_constraint, self.NE_lactation_constraint]
            ]
        elif ration_config.nutrient_standard is NutrientStandard.NASEM:
            self.cow_constraints = [
                {"type": "ineq", "fun": func, "args": (ration_config,)} for func in self.NASEM_constraint_functions
            ]
            self.heifer_constraints = self.cow_constraints

    @staticmethod
    def convert_decision_vec_to_feeds(
        ration_configuration: RationConfig, decision_vector: npt.NDArray[np.float64]
    ) -> list[FeedInRation]:
        """
        Converts the decision vector to a Feeds object for use in NutritionSupplyCalculator methods.

        Parameters
        ----------
        ration_configuration: RationConfig object
            Stored information relevant to ration formulation.
        decision_vector : numpy.ndarray
            The decision vector used in scipy.minimize.

        Returns
        -------
        list[FeedInRation]
            List of feeds and their attributes used in ration formulation.
        """
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
        pen_available_feeds: list[Feed],
        solution: OptimizeResult,
    ) -> dict[str, float | str]:
        """
        Generates ration from scipy result.

        Parameters
        ----------
        pen_available_feeds : list[Feed]
            List of Feeds used in ration formulation.
        solution : OptimizeResult
            Object from scipy package.

        Returns
        -------
        dict[str, float | str]
            Formulated ration, with keys as feed IDs, values as kg fed per animal.

        """
        ration: dict[str, float | str] = {}
        for position_in_list in range(len(pen_available_feeds)):
            kg_to_feed = solution.x[position_in_list]
            ration[getattr(pen_available_feeds[position_in_list], "rufas_id")] = round(kg_to_feed, 6)
        return ration

    @staticmethod
    def NE_total_constraint(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:
        """
        Constraint method for total net energy, as sum of net energy required for lactation, pregnancy, maintenance,
        growth, and activity. Only applicable to lactating cows.
        Total energy supply here assumed to be the "largest" supply of net energy available for any individual
        requirement.
        This constraint is a simple check that the supply exceeds the requirement.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector used in the scipy minimize method.
        ration_configuration: RationConfig object
            Collection of animal requirements and feed supply information for the ration formulation process.

        Returns
        -------
        float
            The difference between supplied and required total net energy.
            Non-negative value indicates that supply meets or exceeds the requirement for total net energy.

        """
        feeds, _, actual_digestible_energy, actual_metabolizable_energy = RationOptimizer._calculate_NE_parameters(
            decision_vector, ration_configuration
        )

        maintenance_energy_supply = NutritionSupplyCalculator.calculate_actual_maintenance_net_energy(
            feeds=feeds, actual_metabolizable_energy=actual_metabolizable_energy
        )

        growth_energy_supply = NutritionSupplyCalculator.calculate_actual_growth_net_energy(
            feeds=feeds, actual_metabolizable_energy=actual_metabolizable_energy
        )

        lactation_energy_supply = NutritionSupplyCalculator.calculate_actual_lactation_net_energy(
            feeds=feeds,
            actual_metabolizable_energy=actual_metabolizable_energy,
            actual_digestible_energy=actual_digestible_energy,
        )

        total_energy_supply = max(maintenance_energy_supply, growth_energy_supply, lactation_energy_supply)

        total_energy_requirement = ration_configuration.animal_requirements.total_energy_requirement
        return total_energy_supply - total_energy_requirement

    @staticmethod
    def NE_maintenance_and_activity_constraint(
        decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig
    ) -> float:
        """
        Constraint method for maintenance and activity.
        This constraint is a simple check that the supply exceeds the requirement.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector used in the scipy minimize method.
        ration_configuration: RationConfig
            Collection of animal requirements and feed supply information for the ration formulation process.

        Returns
        -------
        float
            Non-negative value indicates that supply is greater than the requirements for maintenance and activity.

        """
        feeds, _, _, actual_metabolizable_energy = RationOptimizer._calculate_NE_parameters(
            decision_vector, ration_configuration
        )
        actual_maintenance_net_energy_supply = NutritionSupplyCalculator.calculate_actual_maintenance_net_energy(
            actual_metabolizable_energy=actual_metabolizable_energy, feeds=feeds
        )

        actual_maintenance_and_activity_net_energy_requirement = (
            ration_configuration.animal_requirements.maintenance_energy
            + ration_configuration.animal_requirements.activity_energy
        )

        return actual_maintenance_net_energy_supply - actual_maintenance_and_activity_net_energy_requirement

    @staticmethod
    def NE_lactation_constraint(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:
        """
        Constraint method for net energy for lactation. Only applicable to lactating cows.
        This constraint is a simple check that the supply exceeds the requirement.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector used in the scipy minimize method.
        ration_configuration: RationConfig object
            Collection of animal requirements and feed supply information for the ration formulation process.

        Returns
        -------
        float
            Non-negative value indicates that supply is greater than the requirements for lactation.

        """
        feeds, _, actual_digestible_energy, actual_metabolizable_energy = RationOptimizer._calculate_NE_parameters(
            decision_vector, ration_configuration
        )

        actual_lactation_net_energy_supply = NutritionSupplyCalculator.calculate_actual_lactation_net_energy(
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
    def NASEM_net_energy_constraint(
        decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig
    ) -> float:
        """
        Constraint method for net energy for lactation. Applicable to all animal classes,
        differing from NRC net energy calculations.
        This constraint is a simple check that the supply exceeds the requirement.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector used in the scipy minimize method.
        ration_configuration: RationConfig object
            Collection of animal requirements and feed supply information for the ration formulation process.

        Returns
        -------
        float
            Non-negative value indicates that supply is greater than the requirements for lactation.

        """
        feeds = RationOptimizer.convert_decision_vec_to_feeds(ration_configuration, decision_vector)
        dry_matter_intake = sum(decision_vector)
        total_starch = sum([feed.amount * feed.info.starch * GeneralConstants.PERCENTAGE_TO_FRACTION for feed in feeds])

        total_metabolizable_energy = NutritionSupplyCalculator.calculate_NASEM_metabolizable_energy(
            feeds=feeds,
            dry_matter_intake=dry_matter_intake,
            body_weight=ration_configuration.pen_average_body_weight,
            total_starch=total_starch,
            enteric_methane=ration_configuration.pen_average_enteric_methane,
            urinary_nitrogen=ration_configuration.pen_average_urine_nitrogen,
        )
        actual_lactation_net_energy_supply = NutritionSupplyCalculator.calculate_NASEM_net_energy(
            total_metabolizable_energy=total_metabolizable_energy
        )
        actual_lactation_net_energy_requirement = ration_configuration.animal_requirements.total_energy_requirement

        return actual_lactation_net_energy_supply - actual_lactation_net_energy_requirement

    @staticmethod
    def NE_growth_constraint(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:
        """
        Constraint method for net energy for growth.
        This constraint is a simple check that the supply exceeds the requirement.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector used in the scipy minimize method.
        ration_configuration: RationConfig object
            Collection of animal requirements and feed supply information for the ration formulation process.

        Returns
        -------
        float
            Non-negative value indicates that supply is greater than the requirements for growth.

        """
        feeds, _, _, actual_metabolizable_energy = RationOptimizer._calculate_NE_parameters(
            decision_vector, ration_configuration
        )

        actual_growth_net_energy_supply = NutritionSupplyCalculator.calculate_actual_growth_net_energy(
            feeds=feeds, actual_metabolizable_energy=actual_metabolizable_energy
        )
        actual_growth_net_energy_requirement = ration_configuration.animal_requirements.growth_energy

        return actual_growth_net_energy_supply - actual_growth_net_energy_requirement

    @staticmethod
    def _calculate_NE_parameters(
        decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig
    ) -> tuple[list[FeedInRation], float, dict[int, float], dict[int, float]]:
        """
        Calculates the necessary net energy related parameters for all net energy constraints.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector used in the scipy minimize method.
        ration_configuration: RationConfig object
            Collection of animal requirements and feed supply information for the ration formulation process.

        Returns
        -------
        tuple[list[FeedInRation], float, dict[int, float], dict[int, float]]
            List of Feeds for calculations.
            Actual metabolizable energy.

        """
        feeds = RationOptimizer.convert_decision_vec_to_feeds(ration_configuration, decision_vector)
        intake_nutrient_discount = NutritionSupplyCalculator.calculate_nutrient_intake_discount(
            feeds=feeds, body_weight=ration_configuration.pen_average_body_weight
        )
        actual_digestible_energy = {feed.info.rufas_id: feed.info.DE * intake_nutrient_discount for feed in feeds}
        actual_metabolizable_energy = NutritionSupplyCalculator.calculate_actual_metabolizable_energy(
            feeds=feeds, actual_digestible_energy=actual_digestible_energy
        )
        return feeds, intake_nutrient_discount, actual_digestible_energy, actual_metabolizable_energy

    @staticmethod
    def phosphorus_constraint(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:
        """
        Constraint method for phosphorus.
        This constraint is a simple check that the supply exceeds the requirement.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector used in the scipy minimize method.
        ration_configuration: RationConfig object
            Collection of animal requirements and feed supply information for the ration formulation process.

        Returns
        -------
        float
            Non-negative value indicates that supply is greater than the requirements for phosphorus.

        """
        feeds = RationOptimizer.convert_decision_vec_to_feeds(ration_configuration, decision_vector)
        phosphorus_supply = NutritionSupplyCalculator.calculate_phosphorus_supply(feeds=feeds)
        actual_phosphorus_requirement = max(
            ration_configuration.animal_requirements.phosphorus,
            ration_configuration.animal_requirements.process_based_phosphorus,
        )

        return phosphorus_supply - actual_phosphorus_requirement

    @staticmethod
    def protein_constraint_lower(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:
        """
        Constraint method for the lower bound of metabolizable protein.
        This constraint is a simple check that the supply exceeds the requirement.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector used in the scipy minimize method.
        ration_configuration: RationConfig object
            Collection of animal requirements and feed supply information for the ration formulation process.

        Returns
        -------
        float
            Non-negative value indicates that supply is greater than the requirements for protein.

        """
        metabolizable_protein_supply, actual_metabolizable_protein_requirement = (
            RationOptimizer._calculate_protein_constraint_parameters(
                decision_vector, ration_configuration, use_initial_requirement=False
            )
        )

        return metabolizable_protein_supply - actual_metabolizable_protein_requirement

    @staticmethod
    def protein_constraint_upper(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:
        """
        Constraint method for the upper bound of metabolizable protein.
        This constraint is a simple check that the supply does not exceed the limit.
        See the upper limit factor as defined in AnimalModuleConstants.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector used in the scipy minimize method.
        ration_configuration: RationConfig object
            Collection of animal requirements and feed supply information for the ration formulation process.

        Returns
        -------
        float
            Non-negative value indicates that supply is less than the maximum allowable protein.

        """
        metabolizable_protein_supply, actual_metabolizable_protein_requirement = (
            RationOptimizer._calculate_protein_constraint_parameters(
                decision_vector, ration_configuration, use_initial_requirement=True
            )
        )

        return (
            actual_metabolizable_protein_requirement * AnimalModuleConstants.PROTEIN_UPPER_LIMIT_FACTOR
        ) - metabolizable_protein_supply

    @staticmethod
    def _calculate_protein_constraint_parameters(
        decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig, use_initial_requirement: bool
    ) -> tuple[float, float]:
        """
        Calculates the necessary parameters for protein constraints.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector used in the scipy minimize method.
        ration_configuration: RationConfig object
            Collection of animal requirements and feed supply information for the ration formulation process.

        Returns
        -------
        tuple[float, float]
            Metabolizable protein supply.
            Actual metabolizable protein requirement.

        """
        feeds = RationOptimizer.convert_decision_vec_to_feeds(ration_configuration, decision_vector)
        dry_matter_intake = sum(decision_vector)
        intake_nutrient_discount = NutritionSupplyCalculator.calculate_nutrient_intake_discount(
            feeds=feeds, body_weight=ration_configuration.pen_average_body_weight
        )
        actual_tdn_percentages = {feed.info.rufas_id: feed.info.TDN * intake_nutrient_discount for feed in feeds}
        metabolizable_protein_supply = NutritionSupplyCalculator.calculate_metabolizable_protein_supply(
            feeds=feeds,
            dry_matter_intake=dry_matter_intake,
            actual_tdn_percentages=actual_tdn_percentages,
            body_weight=ration_configuration.pen_average_body_weight,
        )
        if use_initial_requirement:
            actual_metabolizable_protein_requirement = ration_configuration.initial_protein_requirement
        else:
            actual_metabolizable_protein_requirement = ration_configuration.animal_requirements.metabolizable_protein
        return metabolizable_protein_supply, actual_metabolizable_protein_requirement

    @staticmethod
    def calcium_constraint(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:
        """
        Constraint method for calcium.
        This constraint is a simple check that the supply exceeds the requirement.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector used in the scipy minimize method.
        ration_configuration: RationConfig object
            Collection of animal requirements and feed supply information for the ration formulation process.

        Returns
        -------
        float
            Non-negative value indicates that supply is greater than the requirements for calcium.

        """
        feeds = RationOptimizer.convert_decision_vec_to_feeds(ration_configuration, decision_vector)

        calcium_supply = NutritionSupplyCalculator.calculate_calcium_supply(feeds)
        calcium_requirement = ration_configuration.animal_requirements.calcium

        return calcium_supply - calcium_requirement

    @staticmethod
    def NDF_constraint_lower(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:
        """
        Constraint method for the minimum amount of NDF in a ration.
        This constraint is a simple check that the supply exceeds the amount of NDF desired for a formulated ration.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector used in the scipy minimize method.
        ration_config: RationConfig object
            Attributes are animal requirement and feed supply information required for optimization

        Returns
        -------
        float
            Non-negative value indicates that supply is greater than the minimum ration percent value for NDF.

        """
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
        """
        Constraint method for the maximum amount of NDF in a ration.
        This constraint is a simple check that the supply does not exceed the NDF desired for a formulated ration.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector used in the scipy minimize method.
        ration_config: RationConfig object
            Attributes are animal requirement and feed supply information required for optimization

        Returns
        -------
        float
            Non-negative value indicates that supply is less than the maximum ration percent value for NDF.

        """
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
        """
        Constraint method for the minimum amount of forage NDF in a ration.
        This constraint is a simple check that the supply exceeds the amount of forage NDF desired
        for a formulated ration.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector used in the scipy minimize method.
        ration_configuration: RationConfig
            Collection of animal requirements and feed supply information for the ration formulation process.

        Returns
        -------
        float
            Non-negative value indicates that supply is greater than the minimum ration percent value for forage NDF.

        """
        dry_matter_intake = sum(decision_vector)
        if dry_matter_intake != 0:
            feeds = RationOptimizer.convert_decision_vec_to_feeds(ration_configuration, decision_vector)
            forage_NDF_supply = NutritionSupplyCalculator.calculate_forage_neutral_detergent_fiber_content(feeds)
            return (
                forage_NDF_supply / dry_matter_intake
            ) * GeneralConstants.FRACTION_TO_PERCENTAGE - AnimalModuleConstants.MINIMUM_RATION_FORAGE_NDF
        else:
            return -1.0

    @staticmethod
    def fat_constraint(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:
        """
        Constraint method for fat.
        This constraint is a simple check that the supply does not exceed the percentage of fat desired for a
        formulated ration.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector used in the scipy minimize method.
        ration_configuration: RationConfig object
            Collection of animal requirements and feed supply information for the ration formulation process.

        Returns
        -------
        float
            Non-negative value indicates that supply is less than the maximum percentage of fat.

        """
        dry_matter_intake = sum(decision_vector)
        if dry_matter_intake != 0:
            return float(
                -(sum(np.multiply(decision_vector, ration_configuration.EE_list)) / dry_matter_intake)
                + AnimalModuleConstants.MAXIMUM_RATION_FAT
            )
        else:
            return -1.0

    @staticmethod
    def DMI_constraint_lower(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:
        """
        Constraint method for the minimum amount of dry matter intake.
        This constraint is a simple check that the formulated ration supplies enough dry matter.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector used in the scipy minimize method.
        ration_configuration: RationConfig
            Collection of animal requirements and feed supply information for the ration formulation process.

        Returns
        -------
        float
            Non-negative value indicates that supply is exceeds the minimum dry matter intake.

        """
        return float(
            (sum(decision_vector))
            - (
                ration_configuration.animal_requirements.dry_matter
                * (1 - AnimalModuleConstants.DMI_CONSTRAINT_FRACTION)
            )
        )

    @staticmethod
    def DMI_constraint_upper(decision_vector: npt.NDArray[np.float64], ration_configuration: RationConfig) -> float:
        """
        Constraint method for the maximum amount of dry matter intake.
        This constraint is a simple check that the formulated ration does not supply too much dry matter.

        Parameters
        ----------
        decision_vector : numpy.ndarray
            The decision vector used in the scipy minimize method.
        ration_configuration: RationConfig
            Collection of animal requirements and feed supply information for the ration formulation process.

        Returns
        -------
        float
            Non-negative value indicates that supply is less than the maximum dry matter intake.

        """
        return float(
            -(sum(decision_vector))
            + (
                ration_configuration.initial_dry_matter_requirement
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
        ration_config: RationConfig
            Attributes are animal requirement and feed supply information required for optimization.

        Returns
        -------
        float

        """
        return float(sum(np.multiply(decision_vector, ration_config.price_list)))

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
        """
        Function that sets up the nutrients and requirements lists into structured
        inputs for non-linear optimization.

        Parameters
        ----------
        nutrient_standard : NutrientStandard
            Nutrient standard used in supply and requirement calculations.
        pen_average_body_weight : float
            Average body weight of animals in pen.
        pen_average_enteric_methane : float
            Average enteric methane produced in pen, used in constraint methods, g.
        pen_average_urine_nitrogen : float
            Average urine nitrogen generated in pen, used in constraint methods, kg.
        requirements : AnimalRequirements
            Summary of requirements for a group of animals.
        pen_available_feeds : list[Feed]
            A list of Feeds available during ration formulation.
        animal_combination : AnimalCombination
            The animal combination to optimize the ration for.
        previous_ration : dict[RUFAS_ID, str | float] | None
            Ration from previous formulation interval, if available.
        user_defined_ration_dictionary : dict[RUFAS_ID, float]
            Dictionary of feed IDs and inclusion rate.
        user_defined_ration_tolerance : float
            Allowable tolerance of user defined ration inclusion rate.
        Returns
        -------
        OptimizeResult
            Scipy object with information regarding the minimization attempt.
        RationConfig
            RationCofig object.

        Notes
        -----
        Note that the optimization equation cited here is implemented in scipy's minimize method.
        [AN.RAT.1]

        """
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
        )
        sorted_previous_ration = dict(sorted(previous_ration.items())) if previous_ration else None
        initial_decision_vector = np.array(
            self._build_initial_value(sorted_previous_ration, ration_config), dtype=float
        )

        if user_defined_ration_dictionary:
            sorted_user_defined_ration_dictionary = dict(sorted(user_defined_ration_dictionary.items()))
            bounds = self._build_bounds_user_defined_ration(
                ration_config=ration_config,
                user_defined_ration_dictionary=sorted_user_defined_ration_dictionary,
                user_defined_ration_tolerance=user_defined_ration_tolerance,
            )
        else:
            bounds = self._build_bounds(ration_config)

        initial_decision_vector = self._check_initial_bounds(bounds, initial_decision_vector)

        self.set_constraints(ration_config=ration_config)

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

    @staticmethod
    def _check_initial_bounds(
        bounds: list[tuple[float, float]], initial_decision_vector: np.ndarray[tuple[int, ...], np.dtype]
    ) -> np.ndarray[tuple[int, ...], np.dtype]:
        for i in range(0, len(initial_decision_vector)):
            if initial_decision_vector[i] < bounds[i][0] or initial_decision_vector[i] > bounds[i][1]:
                initial_decision_vector[i] = np.clip(initial_decision_vector[i], bounds[i][0], bounds[i][1])

        return initial_decision_vector

    @staticmethod
    def _build_initial_value(
        previous_ration: Optional[dict[RUFAS_ID | str, float | str]], ration_config: RationConfig
    ) -> list[float]:
        """Builds the initial decision vector (`x0`) for the optimizer."""
        if previous_ration:
            return [value for key, value in previous_ration.items() if key not in ("status", "objective")]
        price_list_length = len(ration_config.price_list)
        return [1.0] + [random.random() * 10 for _ in range(price_list_length - 1)]

    @staticmethod
    def _build_bounds(ration_config: RationConfig) -> list[tuple[float, float]]:
        """Zips min/max lists into solver bounds."""
        return list(zip(ration_config.feed_minimum_list, ration_config.feed_maximum_list))

    @staticmethod
    def _build_bounds_user_defined_ration(
        ration_config: RationConfig,
        user_defined_ration_dictionary: dict[RUFAS_ID, float],
        user_defined_ration_tolerance: float,
    ) -> list[tuple[float, float]]:
        """
        Builds the initial decision vector (`x0`) for the optimizer for a user defined ration.

        Parameters
        ----------
        ration_config : dict[str, dict[str, list[dict[str, int | float]] | float]]
            Collection of animal requirements and feed supply information for ration formulation.
        user_defined_ration_dictionary : dict[RUFAS_ID, float]
            Dictionary of feeds and their percentage of dry matter intake prediction for a ration.
        user_defined_ration_tolerance : float
            Allowable +/- variance in each of the defined ration inclusion percentage values.

        Returns
        -------
        list[tuple[float, float]]
            List of upper and lower bounds for each feed ingredient.
        """
        feed_bound_list = list(zip(ration_config.feed_minimum_list, ration_config.feed_maximum_list))
        user_defined_boundlist = []
        udr_tolerance = user_defined_ration_tolerance
        ration_key_list = sorted([int(key) for key in user_defined_ration_dictionary.keys()])
        for key in ration_key_list:
            target_lower = (
                user_defined_ration_dictionary[key]
                / 100
                * (1 - udr_tolerance)
                * (ration_config.initial_dry_matter_requirement * AnimalModuleConstants.DMI_REQUIREMENT_BOOST)
            )
            target_upper = (
                user_defined_ration_dictionary[key]
                / 100
                * (1 + udr_tolerance)
                * (ration_config.initial_dry_matter_requirement * AnimalModuleConstants.DMI_REQUIREMENT_BOOST)
            )
            targetbounds = (max(0.0, target_lower), target_upper)
            user_defined_boundlist.append(targetbounds)

        user_defined_boundlist_trimmed = [
            (max(t1[0], t2[0]), min(t1[1], t2[1])) for t1, t2 in zip(feed_bound_list, user_defined_boundlist)
        ]
        return user_defined_boundlist_trimmed

    def _select_constraints(self, animal_combination: AnimalCombination) -> Sequence[dict[str, Any]]:
        """Returns the pre-computed constraint set based on animal type."""
        if animal_combination is AnimalCombination.LAC_COW:
            return self.cow_constraints
        if animal_combination in (
            AnimalCombination.GROWING,
            AnimalCombination.CLOSE_UP,
            AnimalCombination.GROWING_AND_CLOSE_UP,
        ):
            return self.heifer_constraints
        raise ValueError(f"Invalid animal combination: {animal_combination}")

    @staticmethod
    def is_constraint_violated(
        solution_x: npt.NDArray[np.float64],
        constraint: dict[str, Callable[[Any, Any], float] | tuple[RationConfig] | str],
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
        constraints: list[Any],
        ration_config: RationConfig,
    ) -> list[dict[str, Callable[[Any, Any], float]]]:
        """
        Returns list of constraints that were not met during optimization step.

        Parameters
        ----------
        solution_x: numpy nd array, e.g. npt.NDArray
            solution.x is from minimize function used in ration_NLP.py,
                solution obj itself is returned as  <dict class 'scipy.optimize._optimize.OptimizeResult'>

        constraints: list[dict[str, Callable]]
            list of constraint functions as defined in ration_NLP.py

        ration_config : RationConfig object
            Attributes are animal requirement and feed supply information required for optimization

        Returns
        -------
        list[dict[str,Callable]]
            the same type of list as the constraints themselves
                just filtered such that the ones that failed are returned
        """
        return list(
            filter(
                lambda c: RationOptimizer.is_constraint_violated(solution_x, c, ration_config),
                constraints,
            )
        )

    def handle_failed_constraints(
        self,
        num_attempts: int,
        solution: OptimizeResult,
        ration_config: RationConfig,
        animal_combination: AnimalCombination,
        pen_id: RUFAS_ID,
        pen_available_feeds: Any,
        average_nutrient_requirements: NutritionRequirements,
        initial_dry_matter_requirement: float,
        initial_protein_requirement: float,
        sim_day: int,
    ) -> list[str]:
        """
        Handle and log failed constraints during the ration optimization process.

        This method identifies and logs the constraints that failed during the optimization
        process for a specific pen of animals. It gathers relevant information about the
        failed attempt, including the simulation day, the number of attempts, the failed
        constraints, the attempted ration, and the pen's nutrient requirements. This
        information is then added to the output manager via a variable.

        Parameters:
        -----------
        num_attempts : int
            The number of ration formulation attempts made so far.
        solution : scipy.optimize.OptimizeResult
            The result of the optimization process.
        ration_config : RationConfig
            A RationConfig object.
        animal_combination : AnimalCombination
            The combination of animals for which the failed constraints are being handled.
        pen_id : RUFAS_ID
            The ID for the pen.
        pen_available_feeds : AvailableFeedsTypedDict
            A dictionary of available feeds for ration formulation.
        average_nutrient_requirements : NutritionRequirements
            The pen's average requirements used in ration formulation.
        initial_dry_matter_requirement : float
            Dry matter intake requirement at start of ration formulation.
        initial_protein_requirement : float
            Metabolizable protein requirement at start of ration formulation.
        sim_day : int
            Day of simulation.

        Returns:
        --------
        list[str]
            List of which constraints were failed.
        """
        om = OutputManager()

        constraints_failed_list = []
        if animal_combination == AnimalCombination.LAC_COW:
            failed_constraints = RationOptimizer.find_failed_constraints(
                solution.x, self.cow_constraints, ration_config
            )
        else:
            failed_constraints = RationOptimizer.find_failed_constraints(
                solution.x, self.heifer_constraints, ration_config
            )

        if failed_constraints:
            for constraint in failed_constraints:
                constraints_failed_list.append(constraint["fun"].__name__)
        fail_summary = {
            "simulation day": sim_day,
            "attempt number": num_attempts,
            "constraints_failed_dict": constraints_failed_list,
            "ration_attempted": self.make_ration_from_solution(pen_available_feeds, solution),
            "pen requirements": average_nutrient_requirements,
            "initial_dry_matter_requirement": initial_dry_matter_requirement,
            "initial_protein_requirement": initial_protein_requirement,
        }
        fail_summary_units = {
            "simulation day": MeasurementUnits.SIMULATION_DAY,
            "attempt number": MeasurementUnits.UNITLESS,
            "constraints_failed_dict": MeasurementUnits.UNITLESS,
            "ration_attempted": MeasurementUnits.UNITLESS,
            "pen requirements": {
                "maintenance_energy": MeasurementUnits.MEGACALORIES,
                "growth_energy": MeasurementUnits.MEGACALORIES,
                "pregnancy_energy": MeasurementUnits.MEGACALORIES,
                "lactation_energy": MeasurementUnits.MEGACALORIES,
                "metabolizable_protein": MeasurementUnits.GRAMS,
                "calcium": MeasurementUnits.GRAMS,
                "phosphorus": MeasurementUnits.GRAMS,
                "process_based_phosphorus": MeasurementUnits.GRAMS,
                "dry_matter": MeasurementUnits.KILOGRAMS,
                "activity_energy": MeasurementUnits.MEGACALORIES,
            },
            "initial_dry_matter_requirement": MeasurementUnits.KILOGRAMS,
            "initial_protein_requirement": MeasurementUnits.GRAMS,
        }
        info_map = {
            "class": self.__class__.__name__,
            "function": self.handle_failed_constraints.__name__,
        }

        om.add_variable(
            f"failed_constraint_summary_for_pen_{pen_id}",
            fail_summary,
            dict(info_map, **{"units": fail_summary_units}),
        )

        return constraints_failed_list
