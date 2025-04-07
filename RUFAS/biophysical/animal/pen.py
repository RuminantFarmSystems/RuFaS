from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import (
    NutritionRequirements,
    NutritionEvaluationResults,
    NutritionSupply,
)
from RUFAS.data_structures.animal_manure_excretions import AnimalManureExcretions
from RUFAS.data_structures.feed_storage_to_animal_connection import (
    RequestedFeed,
    AdvancePurchaseAllowance,
    TotalInventory,
)
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.nutrients.nutrition_evaluator import NutritionEvaluator
from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import NutritionSupplyCalculator
from RUFAS.biophysical.animal.ration.user_defined_ration_manager import UserDefinedRationManager
from RUFAS.data_structures.pen_manure_data import PenManureData
from RUFAS.data_structures.feed_storage_to_animal_connection import RUFAS_ID, Feed
from RUFAS.enums import AnimalCombination

from RUFAS.biophysical.animal.ration.ration_optimizer import RationOptimizer
from RUFAS.output_manager import OutputManager

ration_optimizer = RationOptimizer()
om = OutputManager()

class Pen:
    """
    This class represents a pen that houses animals during the simulation.

    Attributes
    ----------
    id : int
        Internal identifier for the pen.
    pen_name : str
        Name of the pen.
    max_stocking_density : float
        Maximum allowable stocking density for animals in the pen.
    vertical_dist_to_parlor : float
        Vertical distance from the pen to the milking parlor, in meters.
    horizontal_dist_to_parlor : float
        Horizontal distance from the pen to the milking parlor, in meters.
    num_stalls : int
        Total number of stalls available in the pen.
    housing_type : str
        Type of housing in the pen.
    bedding_type : str
        Type of bedding material used in the pen.
    pen_type : str
        The pen type.
    manure_handling : str
        Method of manure handling associated with the pen.
    manure_separator : str
        Type of manure separator applied in the pen.
    manure_separator_after_digestion : str
        Additional manure separation methods utilized after digestion.
    manure_storage : str
        Storage method for manure from the pen.
    animals_in_pen : dict[int, Animal], default {}
        Dictionary mapping animal IDs to `Animal` objects housed in the pen.
    ration : dict[RUFAS_ID, float], default {}
        Maps RuFaS Feed ID to the amount of that feed in the ration (kg dry matter).
    average_nutrition_supply : NutritionSupply
        Average nutrition supplied by the ration to an animal in the pen.
    average_nutrition_requirements : NutritionRequirements
        Average nutritional requirements of an animal in the pen.
    average_nutrition_evaluation : NutritionEvaluationResults
        Average surpluses and/or deficits of nutrients supplied to animals in the pen.
    allocated_feeds : set
        Set of IDs for the feeds allocated for this pen.
    animal_combination : AnimalCombination
        Combination of animal categories housed in the pen.
    """

    def __init__(
        self,
        pen_id: int,
        pen_name: str,
        vertical_dist_to_milking_parlor: float,
        horizontal_dist_to_milking_parlor: float,
        number_of_stalls: int,
        housing_type: str,
        bedding_type: str,
        pen_type: str,
        manure_handling: str,
        manure_separator: str,
        manure_separator_after_digestion: str,
        manure_storage: str,
        animal_combination: AnimalCombination,
        max_stocking_density: float,
    ) -> None:
        """
        Represents a pen used in animal housing systems with attributes related to its layout, structure,
        and management, including nutrition and manure handling specifics.

        Parameters
        ----------
        pen_id : int
            Unique identifier for the pen.
        pen_name : str
            Name of the pen.
        vertical_dist_to_milking_parlor : float
            Vertical distance from the pen to the milking parlor, (m).
        horizontal_dist_to_milking_parlor : float
            Horizontal distance from the pen to the milking parlor, (m).
        number_of_stalls : int
            Number of stalls available in the pen.
        housing_type : str
            Type of housing type of the pen.
        bedding_type : str
            Type of bedding material used in the pen.
        pen_type : str
            The pen type.
        manure_handling : str
            Method of manure handling associated with the pen.
        manure_separator : str
            Type of manure separator applied in the pen.
        manure_separator_after_digestion : str
            Additional manure separation methods utilized after digestion.
        manure_storage : str
            Storage method for manure from the pen.
        animal_combination : AnimalCombination
            Combination of animal categories housed in the pen.
        max_stocking_density : float
            Maximum allowable stocking density for animals in the pen.

        Returns
        -------
        None

        """
        self.id = pen_id
        self.max_stocking_density = max_stocking_density

        self.vertical_dist_to_parlor = vertical_dist_to_milking_parlor
        self.horizontal_dist_to_parlor = horizontal_dist_to_milking_parlor
        self.num_stalls = number_of_stalls
        self.housing_type = housing_type
        self.bedding_type = bedding_type
        self.pen_type = pen_type
        self.pen_name = pen_name

        self.manure_handling = manure_handling
        self.manure_separator = manure_separator
        self.manure_separator_after_digestion = manure_separator_after_digestion
        self.manure_storage = manure_storage

        self.animals_in_pen: dict[int, Animal] = {}

        self.ration: dict[RUFAS_ID, float] = {}
        self.average_nutrition_evaluation: NutritionEvaluationResults = (
            NutritionEvaluationResults.make_empty_evaluation_results()
        )

        self.allocated_feeds = set()

        self.animal_combination = animal_combination

    @property
    def current_stocking_density(self) -> float:
        """
        Returns the current stocking density of the pen.

        Returns
        -------
        float
            the current stocking density of the pen.

        """
        return len(self.animals_in_pen) / self.num_stalls

    @property
    def is_populated(self) -> bool:
        """
        Returns whether the pen is populated.

        Returns
        -------
        bool
            True if the pen is populated, False otherwise.

        """
        return len(self.animals_in_pen) > 0

    @property
    def needs_ration_formulation(self) -> bool:
        """
        Returns whether pen needs a ration formulated.

        Returns
        -------
        bool
            True if pen needs ration formulation.

        Notes
        -----
        This is currently written to cover the case in which a ration was not formulated due to the pen being empty,
         but was populated in subsequent days.

        """
        return not self.ration and self.is_populated

    @property
    def animal_types_in_pen(self) -> set[AnimalType]:
        """
        Returns a set of animal types currently in the pen.

        Returns
        -------
        set[AnimalType]
            A set of unique animal types defined by the `animal_type` property
            of the animals in the pen.

        """
        animal_types = set([animal.animal_type for animal in self.animals_in_pen.values()])
        return animal_types

    @property
    def number_of_lactating_cows_in_pen(self) -> int:
        """
        Returns the number of lactating cows in the pen.

        Returns
        -------
        int
            The number of lactating cows present in the pen.

        """
        return len([animal for animal in self.animals_in_pen.values() if animal.animal_type == AnimalType.LAC_COW])

    @property
    def cows_in_pen(self) -> list[Animal]:
        """
        Returns all the cows in the current pen.

        Returns
        -------
        list[Animal]
            A list of cows in pen.

        """
        return [
            animal
            for animal in self.animals_in_pen.values()
            if animal.animal_type == AnimalType.LAC_COW or animal.animal_type == AnimalType.DRY_COW
        ]

    @property
    def average_growth(self) -> float:
        """
        Computes the average daily growth of all animals in the pen.

        Returns
        -------
        float
            The average daily growth of the animals, or 0 if the pen is empty.

        """
        if not self.is_populated:
            return 0
        total_growth = sum([animal.growth.daily_growth for animal in self.animals_in_pen.values()])
        return total_growth / len(self.animals_in_pen)

    @property
    def total_manure_excretion(self) -> AnimalManureExcretions:
        """
        Calculates the total manure excretion of all animals in the pen
        by summing up the individual manure excretions from the digestive
        systems of each animal.

        Returns
        -------
        AnimalManureExcretions
            The total manure excretion for all animals in the pen.

        """
        total_manure_excretion = AnimalManureExcretions()
        for animal in self.animals_in_pen.values():
            total_manure_excretion += animal.digestive_system.manure_excretion
        return total_manure_excretion

    @property
    def average_nutrition_requirements(self) -> NutritionRequirements:
        """
        Computes the average nutritional requirements for all animals in a pen.

        Returns
        -------
        NutritionRequirements
            The average nutritional requirements across all animals in the pen, or
            an empty NutritionRequirements object if the pen contains no animals.

        """
        if len(self.animals_in_pen) <= 0:
            return NutritionRequirements.make_empty_nutrition_requirements()
        animal_requirements: list[NutritionRequirements] = [
            animal.nutrition_requirements for animal in self.animals_in_pen.values()
        ]
        return sum(animal_requirements, NutritionRequirements.make_empty_nutrition_requirements()) / len(
            self.animals_in_pen
        )

    @property
    def average_nutrition_supply(self) -> NutritionSupply:
        """
        Computes the average nutritional supply for all animals in a pen.

        Returns
        -------
        NutritionSupply
            The average nutritional supply across all animals in the pen, or
            an empty NutritionSupply object if the pen contains no animals.

        """
        if len(self.animals_in_pen) <= 0:
            return NutritionSupply.make_empty_nutrition_supply()
        nutrition_supplies: list[NutritionSupply] = [animal.nutrition_supply for animal in self.animals_in_pen.values()]
        return sum(nutrition_supplies, NutritionSupply.make_empty_nutrition_supply()) / len(self.animals_in_pen)

    @property
    def average_phosphorus_requirements(self) -> float:
        """
        Calculates the average phosphorus requirements for all animals within the pen.

        Returns
        -------
        float
            The computed average of phosphorus requirements for all animals in the pen, or 0 if the pen is empty.

        """
        animal_phosphorus_requirements = [
            animal.nutrients.phosphorus_requirement for animal in self.animals_in_pen.values()
        ]
        return sum(animal_phosphorus_requirements) / len(self.animals_in_pen) if len(self.animals_in_pen) > 0 else 0.0

    @property
    def average_body_weight(self) -> float:
        """
        Calculate the average body weight of animals in the pen.

        Returns
        -------
        float
            Average body weight of animals in the pen (kg).

        """
        if (number_of_animals_in_pen := len(self.animals_in_pen.values())) == 0:
            return 0.0
        return sum([animal.body_weight for animal in self.animals_in_pen.values()]) / number_of_animals_in_pen

    @property
    def average_milk_production(self) -> float:
        """
        Calculate the average milk production for the cows in the pen.

        Returns
        -------
        float
            The average milk production reduction for the cows in the pen (kg).

        """
        if self.animal_combination != AnimalCombination.LAC_COW:
            return 0.0
        if (number_of_cows_in_pen := len(self.cows_in_pen)) == 0:
            return 0.0
        return sum([cow.milk_production.daily_milk_produced for cow in self.cows_in_pen]) / number_of_cows_in_pen

    @property
    def average_milk_production_reduction(self) -> float:
        """
        Calculate the average milk production reduction for the cows in the pen.

        Returns
        -------
        float
            The average milk production reduction for the cows in the pen (kg).

        """
        if (number_of_cows_in_pen := len(self.cows_in_pen)) == 0:
            return 0.0
        return sum([cow.milk_production.milk_production_reduction for cow in self.cows_in_pen]) / number_of_cows_in_pen

    @property
    def total_enteric_methane(self) -> float:
        """Calculate the total enteric methane produced by all animals in the pen on the current day (g)."""
        return sum([animal.digestive_system.enteric_methane_emission for animal in self.animals_in_pen.values()])

    def reset_milk_production_reduction(self) -> None:
        """Resets the milk production reduction to 0 for all animals in the pen."""
        for animal in self.animals_in_pen.values():
            animal.milk_production.milk_production_reduction = 0

    def reduce_milk_production(self) -> bool:
        """
        Attempts to reduce the milk production of all animals in the pen.

        Returns
        -------
        bool
            False if all animals in the pen have already reached the maximum reduction, True otherwise.
        """
        is_production_reduced: list[bool] = []
        for animal in self.animals_in_pen.values():
            is_production_reduced.append(animal.reduce_milk_production())
        return any(is_production_reduced)

    def remove_animals_by_ids(self, animal_ids: list[int]) -> None:
        """
        Removes animals from the pen by their ids.

        Notes
        -----
        Because this method takes O(n) time, it is recommended that the caller of this method
        should prepare a list of animal ids to be removed from the pen first, and then call this
        method with that list once.

        Parameters
        ----------
        animal_ids : List[int]
            List of animals that match the given ids to be removed from the pen.

        Returns
        -------
        None

        """
        if not animal_ids:
            return
        animal_ids = list(set(animal_ids))
        self.animals_in_pen = {
            animal_id: animal for animal_id, animal in self.animals_in_pen.items() if animal_id not in animal_ids
        }

    def update_animals(
        self, new_animals: list[Animal], animal_combination: AnimalCombination, available_feeds: list[Feed]
    ) -> None:
        """
        Calls functions that will add new animals to the pen and update associated attributes.

        Parameters
        ----------
        new_animals: List[Calf | Cow | HeiferI | HeiferII | HeiferIII]
            list of new animals to be added to the pen
        animal_combination: AnimalCombination
            an AnimalCombination Enum representing the type of the new animals
        available_feeds : list[Feed]
            Nutrition information of feeds available formulate animals rations with.

        Returns
        -------
        None

        """
        self._add_new_animals(new_animals, available_feeds)
        self.update_animal_combination(animal_combination)

    def _add_new_animals(self, new_animals: list[Animal], available_feeds: list[Feed]) -> None:
        """
        Adds all animals in new_animals to the pen animals_in_pen map, and set the nutrition requirements and the
        nutrition supply for each new animal.

        Parameters
        ----------
        new_animals: List[Calf | Cow | HeiferI | HeiferII | HeiferIII]
            list of new animals to be added to the pen
        available_feeds : list[Feed]
            Nutrition information of feeds available formulate animals rations with.

        Returns
        -------
        None

        """
        for animal in new_animals:
            self.insert_single_animal_into_animals_in_pen_map(animal)
            animal.set_nutrition_requirements(self.housing_type, animal.daily_distance, 20.0, available_feeds)
            nutrient_supply = NutritionSupplyCalculator.calculate_nutrient_supply(
                feeds_used=available_feeds, ration_formulation=self.ration, body_weight=animal.body_weight
            )
            animal.nutrition_supply = nutrient_supply

    def insert_animals_into_animals_in_pen_map(self, animals: list[Animal]) -> None:
        """
        This method will add a list of new animals in the animals_in_pen map and set the daily walking distance for all
        the new cows.

        Parameters
        ----------
        animals : list[Animal]

        Returns
        -------
        None

        Notes
        -----
        This method only inserts a list of new animals in the animals_in_pen map, and updates the daily walking distance
        for all the new cows. It does not set the nutrition requirements or the nutrient supply of the new animals, nor
        does it update pen attributes like ration or animal combination.
        This method is intended to assign animals to pen during the initialization process where no ration is set for
        the pen.

        """
        for animal in animals:
            self.insert_single_animal_into_animals_in_pen_map(animal)

    def insert_single_animal_into_animals_in_pen_map(self, animal: Animal) -> None:
        """
        This method will add a new animal in the animals_in_pen map and set the daily walking distance if the new animal
        is a cow.

        Parameters
        ----------
        animal: Animal
            The animal to insert into pen.

        Returns
        -------
        None

        Notes
        -----
        This method only inserts a new animal in the animals_in_pen map, and updates the daily walking distance if it is
        a cow. It does not set the nutrition requirements or the nutrient supply of the new animal, nor does it
        update pen attributes like ration or animal combination.

        """
        self.animals_in_pen[animal.id] = animal
        if animal.animal_type.is_cow:
            animal.set_daily_walking_distance(self.vertical_dist_to_parlor, self.horizontal_dist_to_parlor)

    def update_animal_combination(self, animal_combination: AnimalCombination) -> None:
        """
        Sets the pen's animal combination to animal_combination

        Parameters
        ----------
        animal_combination: AnimalCombination
            the new AnimalCombination

        Returns
        -------
        None

        """
        self.animal_combination = animal_combination

    def update_daily_walking_distance(self) -> None:
        """
        Updates the daily walking distance for cows in the pen.

        Returns
        -------
        None

        """
        if AnimalType.LAC_COW in self.animal_types_in_pen or AnimalType.DRY_COW in self.animal_types_in_pen:
            for animal in self.cows_in_pen:
                animal.set_daily_walking_distance(self.vertical_dist_to_parlor, self.horizontal_dist_to_parlor)

    def clear(self) -> None:
        """
        Clears the pen attributes for re-allocation.

        Notes
        -----
        All other attributes are kept the same so that if a pen becomes empty
        and animals are to be added to it, there are previous initial values
        that are non-zero.

        Returns
        -------
        None

        """
        self.animals_in_pen = {}

    def get_manure_data(self) -> PenManureData:
        """
        Packages manure data from this pen.

        Returns
        -------
        PenManureData
            The manure data for this pen.
        """
        return PenManureData(
            id=self.id,
            num_animals=len(self.animals_in_pen),
            classes_in_pen=self.animal_types_in_pen,
            animal_combination=self.animal_combination,
            housing_type=self.housing_type,
            pen_type=self.pen_type,
            bedding_type=self.bedding_type,
            manure_handler=self.manure_handling,
            manure_separator=self.manure_separator,
            manure_separator_after_digestion=self.manure_separator_after_digestion,
            manure_treatment=self.manure_storage,
            manure=self.total_manure_excretion,
            num_lactating_cows=self.number_of_lactating_cows_in_pen,
            num_stalls=self.num_stalls,
        )

    def set_animal_nutritional_requirements(self, temperature: float, available_feeds: list[Feed]) -> None:
        """
        Set the nutritional requirements for all animals in the pen.

        Parameters
        ----------
        temperature : float
            The temperature of the pen (C).
        available_feeds : list[Feed]
            Nutrition information of feeds available to formulate animals rations with.

        Returns
        -------
        None

        """
        for animal in self.animals_in_pen.values():
            animal.set_nutrition_requirements(
                housing=self.housing_type,
                walking_distance=animal.daily_distance,
                previous_temperature=temperature,
                available_feeds=available_feeds,
            )

    def set_animal_nutritional_supply(self, feeds_used: list[Feed], ration_formulation: dict[RUFAS_ID, float]) -> None:
        """
        Set the nutritional supply for all animals in the pen.

        Parameters
        ----------
        feeds_used : list[Feed]
            The list of feeds used to formulate the ration.
        ration_formulation : dict[RUFAS_ID, float]
            The formulated ration dictionary, mapping RuFaS Feed ID to mass of feed in ration per animal per day.

        Returns
        -------
        None

        """
        for animal in self.animals_in_pen.values():
            animal.previous_nutrition_supply = animal.nutrition_supply
            animal.nutrition_supply = NutritionSupplyCalculator.calculate_nutrient_supply(
                feeds_used=feeds_used, ration_formulation=ration_formulation, body_weight=animal.body_weight
            )

    def formulate_optimized_ration(
        self,
        available_feeds: list[Feed],
        temperature: float,
        max_daily_feeds: dict[RUFAS_ID, float],
        advance_purchase_allowance: AdvancePurchaseAllowance,
        total_inventory: TotalInventory,
    ) -> None:
        """
        Formulates a ration while optimizing for multiple goals.

        Parameters
        ----------
        available_feeds : list[Feed]
            List of feeds available to formulate a new ration with.
        max_daily_feeds : dict[RUFAS_ID, float]
            Maximum amounts of each feed type that may be fed per animal per day.
        advance_purchase_allowance : AdvancePurchaseAllowance
            Maximum amounts of each feed type that may be purchased at the beginning of a feed interval.
        total_inventory : TotalInventory
            Amounts of feeds currently held in storage.

        Returns
        -------
        None

        """
        info_map = {
            "class": "Pen",
            "function": self.formulate_optimized_ration.__name__,
        }
        if self.animal_combination == AnimalCombination.LAC_COW:
            self.reset_milk_production_reduction()

        self.set_animal_nutritional_requirements(temperature=temperature, available_feeds=available_feeds)
        previous_ration = None
        if hasattr(self, "ration"):
            previous_ration = self.ration
        solution, ration_config = ration_optimizer.attempt_optimization(
            pen_average_body_weight=self.average_body_weight,
            requirements=self.average_nutrition_requirements,
            available_feeds=available_feeds,
            animal_combination=self.animal_combination,
            previous_ration=previous_ration,
            )
        # solution, ration_vals, ration_config = ration_optimizer.attempt_optimization(req, available_feeds, pen.animal_combination, previous_ration)
        num_attempts: int = 1
        if solution and not solution.success:
            ration_config
            # handle the failed constraints
            # THIS IS WHERE RATION CONFIG IS NEEDED AS OUTPUT
            pass
        if self.animal_combination == AnimalCombination.LAC_COW:
            while not solution.success:
                if self.average_milk_production < AnimalModuleConstants.MINIMUM_AVG_PEN_MILK:
                    om.add_error(
                        "Milk production too low",
                        (
                            f"Check failed_constraint_summary_for_pen_{self.id} to see what caused formulation to fail. "
                            f"Possible solution is to provide additional feed ingredients to "
                            f"{self.animal_combination.name}."
                        ),
                        info_map,
                    )
                    raise ValueError
                self.reduce_milk_production()
                self.set_animal_nutritional_requirements(temperature=temperature, available_feeds=available_feeds)
                (
                    solution,
                    ration_config,
                ) = SOMETHING_AGAIN
                num_attempts += 1
                if solution and not solution.success:
                    # handle failed constraints
                    # THIS IS WHERE RATION CONFIG IS NEEDED AS OUTPUT
                    pass

        if solution is not None and solution.success:
            self.ration = make_ration_from_solution()
        elif self.ration == {}:
            om.add_error(
                "No previous ration available",
                f" Check failed_constraint_summary_for_pen_{self.id} to see what caused formulation to fail. "
                f"Possible solution is to provide additional feed ingredients to {self.animal_combination.name}.",
                info_map,
            )
            raise ValueError 
        # optimized_ration = optimize_ration(
        #     available_feeds,
        #     self.average_animal_requirements,
        #     max_daily_feeds,
        #     advance_purchase_allowance,
        #     total_inventory
        # )
        ############ optimized_ration: dict[RUFAS_ID, float] = {}  # Maps RuFaS Feed ID to mass of feed in ration per animal per day.

        # self.ration = optimized_ration

    def use_user_defined_ration(self, available_feeds: list[Feed], temperature: float) -> None:
        """
        Calculate new ration for the pen based on the number of animals in the pen.

        Parameters
        ----------
        available_feeds : list[Feed]
            List of available feeds to be used in the ration formulation.
        temperature : float
            Temperature of the animals' environment (°C).

        Notes
        -----
        The average nutrition requirements of the pen are calculated, and then used to determine the ration given to
        each animal. Then ration is checked against the nutrition requirements of every individual animal in the pen. If
        the animal is a lactating cow and the ration does not meet its requirements, then its milk production is reduced
        until one of three conditions is met:
        1. The ration meets the animal's requirement.
        2. The milk production of the animal is reduced by the maximum amount allowed.
        3. The average milk production of the pen falls below the minimum allowable average milk production.

        If the animal is not a lactating cow, the outcomes of that animal are not affected and its nutrition
        requirements are not met.

        Returns
        -------
        None

        """
        animal_combination = self.animal_combination
        if animal_combination == AnimalCombination.LAC_COW:
            self.reset_milk_production_reduction()
        self.set_animal_nutritional_requirements(temperature=temperature, available_feeds=available_feeds)
        ration = UserDefinedRationManager.get_user_defined_ration(
            animal_combination, self.average_nutrition_requirements
        )
        self.set_animal_nutritional_supply(feeds_used=available_feeds, ration_formulation=ration)

        is_ration_adequate, evaluation_result = NutritionEvaluator.evaluate_nutrition_supply(
            self.average_nutrition_requirements,
            self.average_nutrition_supply,
            (animal_combination == AnimalCombination.LAC_COW),
        )
        if animal_combination == AnimalCombination.LAC_COW:
            ration_sufficient_for_milk_production = True
            while ration_sufficient_for_milk_production:
                if is_ration_adequate is True:
                    break
                if not self.reduce_milk_production():
                    break
                if self.average_milk_production < AnimalModuleConstants.MINIMUM_AVG_PEN_MILK:
                    break
                self.set_animal_nutritional_requirements(temperature=temperature, available_feeds=available_feeds)
                ration = UserDefinedRationManager.get_user_defined_ration(
                    animal_combination, self.average_nutrition_requirements
                )
                self.set_animal_nutritional_supply(feeds_used=available_feeds, ration_formulation=ration)
                is_ration_adequate, evaluation_result = NutritionEvaluator.evaluate_nutrition_supply(
                    self.average_nutrition_requirements,
                    self.average_nutrition_supply,
                    (animal_combination == AnimalCombination.LAC_COW),
                )
        self.average_nutrition_evaluation = (
            evaluation_result if self.is_populated else NutritionEvaluationResults.make_empty_evaluation_results()
        )

        self.ration = ration

    def get_requested_feed(self, ration_interval_length: int) -> RequestedFeed:
        """
        Returns the requested feed for the pen.

        Parameters
        ----------
        ration_interval_length : int
            The length of the ration interval (days).

        Returns
        -------
        RequestedFeed
            The requested feed for the pen.

        """
        ration_for_all_animals = {
            rufas_id: amount * len(self.animals_in_pen) * ration_interval_length
            for rufas_id, amount in self.ration.items()
        }
        return RequestedFeed(requested_feed=ration_for_all_animals)
