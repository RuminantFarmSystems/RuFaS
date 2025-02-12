from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import (
    NutritionRequirements,
    NutritionEvaluationResults,
    NutritionSupply,
)
from RUFAS.data_structures.animal_manure_excretions import AnimalManureExcretions
from RUFAS.data_structures.feed_storage_to_animal_connection import RequestedFeed, AdvancePurchaseAllowance, TotalInventory
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.pen_statistics import PenStatistics
from RUFAS.biophysical.animal.nutrients.nutrition_evaluator import NutritionEvaluator
from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import NutritionSupplyCalculator
from RUFAS.biophysical.animal.ration.user_defined_ration_manager import UserDefinedRationManager
from RUFAS.data_structures.pen_manure_data import PenManureData
from RUFAS.data_structures.feed_storage_to_animal_connection import RUFAS_ID, Feed
from RUFAS.enums import AnimalCombination


class Pen:
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

        Attributes
        ----------
        ration : dict[RUFAS_ID, float], default {}
            Maps RuFaS Feed ID to the amount of that feed in the ration (kg dry matter).
        average_nutrition_supply : NutritionSupply
            Average nutrition supplied by the ration to an animal in the pen.
        average_nutrition_evaluation : NutritionEvaluationResults
            Average surpluses and/or deficits of nutrients supplied to animal in the pen.


        """
        self.pen_statistics = PenStatistics()
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
        self.average_nutrition_supply: NutritionSupply = NutritionSupply.make_empty_nutrition_supply()
        self.average_nutrition_requirements: NutritionRequirements = (
            NutritionRequirements.make_empty_nutrition_requirements()
        )
        self.average_nutrition_evaluation: NutritionEvaluationResults = (
            NutritionEvaluationResults.make_empty_evaluation_results()
        )

        # set of all the ids for the feeds allocated for this pen object
        self.allocated_feeds = set()

        # the animal_combinations in this pen, utilizes the AnimalCombination Enum
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

        This is currently written to cover the case in which a ration was not formulated due to the pen being empty,
         but was populated in subsequent days.

        Returns
        -------
        bool
            True if pen needs ration formulation.
        """
        return not self.ration and self.is_populated

    @property
    def animal_types_in_pen(self) -> set[AnimalType]:
        animal_types = set([animal.animal_type for animal in self.animals_in_pen.values()])
        return animal_types

    @property
    def number_of_lactating_cows_in_pen(self) -> int:
        return len([animal for animal in self.animals_in_pen.values() if animal.animal_type == AnimalType.LAC_COW])

    @property
    def cows_in_pen(self) -> list[Animal]:
        return [
            animal
            for animal in self.animals_in_pen.values()
            if animal.animal_type == AnimalType.LAC_COW or animal.animal_type == AnimalType.DRY_COW
        ]

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

        """
        if not animal_ids:
            return
        animal_ids = set(animal_ids)
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

        """
        self.add_new_animals(new_animals, available_feeds)
        self.calculate_daily_walking_distance()
        self.update_animal_combination(animal_combination)
        # self.update_classes_in_pen()

    def add_new_animals(self, new_animals: list[Animal], available_feeds: list[Feed]) -> None:
        """
        Adds all animals in new_animals to the pen.

        Parameters
        ----------
        new_animals: List[Calf | Cow | HeiferI | HeiferII | HeiferIII]
            list of new animals to be added to the pen
        available_feeds : list[Feed]
            Nutrition information of feeds available formulate animals rations with.

        """
        for animal in new_animals:
            self.animals_in_pen[animal.id] = animal
            animal.set_nutrition_requirements(self.housing_type, animal.daily_distance, 20.0, available_feeds)

    def update_animal_combination(self, animal_combination: AnimalCombination) -> None:
        """
        Sets the pen's animal combination to animal_combination

        Parameters
        ----------
        animal_combination: AnimalCombination
            the new AnimalCombination
        """
        self.animal_combination = animal_combination

    def calculate_daily_walking_distance(self) -> None:
        """
        Sets the daily walking distance for the cows in the pen (if any).
        """
        animal_types_in_pen = self.animal_types_in_pen
        if AnimalType.LAC_COW in animal_types_in_pen or AnimalType.DRY_COW in animal_types_in_pen:
            for animal in list(self.animals_in_pen.values()):
                if animal.animal_type.is_cow:
                    animal.set_daily_walking_distance(self.vertical_dist_to_parlor, self.horizontal_dist_to_parlor)

    @property
    def average_growth(self) -> float:
        if not self.is_populated:
            return 0
        total_growth = sum([animal.growth.daily_growth for animal in self.animals_in_pen.values()])
        return total_growth / len(self.animals_in_pen)

    @property
    def total_manure_excretion(self) -> AnimalManureExcretions:
        total_manure_excretion = AnimalManureExcretions()
        for animal in self.animals_in_pen.values():
            total_manure_excretion += animal.digestive_system.manure_excretion
        return total_manure_excretion

    @property
    def average_animal_requirements(self) -> NutritionRequirements:
        """Calculates the average nutrient requirements of all animals in the pen."""
        if len(self.animals_in_pen) <= 0:
            return NutritionRequirements.make_empty_nutrition_requirements()
        animal_requirements: list[NutritionRequirements] = [
            animal.nutrition_requirements for animal in self.animals_in_pen.values()
        ]
        return sum(animal_requirements, NutritionRequirements.make_empty_nutrition_requirements()) / len(
            self.animals_in_pen
        )

    def update_daily_walking_distance(self) -> None:
        if AnimalType.LAC_COW in self.animal_types_in_pen or AnimalType.DRY_COW in self.animal_types_in_pen:
            for animal in self.cows_in_pen:
                animal.set_daily_walking_distance(self.vertical_dist_to_parlor, self.horizontal_dist_to_parlor)

    @property
    def average_phosphorus_requirements(self) -> float:
        animal_phosphorus_requirements = [
            animal.nutrients.phosphorus_requirement for animal in self.animals_in_pen.values()
        ]
        return sum(animal_phosphorus_requirements) / len(self.animals_in_pen)

    def clear(self) -> None:
        """
        Clears the pen attributes for re-allocation.
        """
        # All other attributes are kept the same so that if a pen becomes empty
        # and animals are to be added to it, there are previous initial values
        # that are non-zero.
        self.animals_in_pen = {}

    def subset_class_feeds(self, feed) -> None:
        """
        Subsets the feed_ids list to appropriately include the feeds necessary for that pen object,
        based on the animal type(s) that are currently in the pen.

        Parameters
        ----------
        feed : Feed
            An object of the Feed class.
        """

        self.allocated_feeds = feed.input_feed_combinations[self.animal_combination]

    def get_manure_data(self) -> PenManureData:
        """Packages manure data from this pen."""
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

        """
        for animal in self.animals_in_pen.values():
            animal.set_nutrition_requirements(
                housing=self.housing_type,
                walking_distance=animal.daily_distance,
                previous_temperature=temperature,
                available_feeds=available_feeds,
            )

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

    def formulate_optimized_ration(
        self,
        available_feeds: list[Feed],
        max_daily_feeds: dict[RUFAS_ID, float],
        advanced_purchase_allowance: AdvancePurchaseAllowance,
        total_inventory: TotalInventory,
        ration_interval_length: int,
    ) -> None:
        """
        Formulates a ration while optimizing for multiple goals.

        Parameters
        ----------
        available_feeds : list[Feed]
            List of feeds available to formulate a new ration with.
        max_daily_feeds : dict[RUFAS_ID, float]
            Maximum amounts of each feed type that may be fed per animal per day.
        advanced_purchase_allowance : AdvancePurchaseAllowance
            Maximum amounts of each feed type that may be purchased at the beginning of a feed interval.
        total_inventory : TotalInventory
            Amounts of feeds currently held in storage.
        ration_interval_length : int
            Number of days until the next ration reformulation.

        """
        # optimized_ration = optimize_ration(self.average_animal_requirements, max_daily_feeds, advanced_purchase_allowance)
        optimized_ration: dict[RUFAS_ID, float] = {}  # Maps RuFaS Feed ID to mass of feed in ration per animal per day.

        self.ration = optimized_ration

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

        """
        animal_combination = self.animal_combination
        ration = UserDefinedRationManager.get_user_defined_ration(animal_combination, self.average_animal_requirements)

        total_nutrition_supply = NutritionSupply.make_empty_nutrition_supply()
        total_nutrition_requirements = NutritionRequirements.make_empty_nutrition_requirements()
        total_nutrition_evaluation_results = NutritionEvaluationResults.make_empty_evaluation_results()

        ration_sufficient_for_milk_production = True
        for animal in self.animals_in_pen.values():
            while ration_sufficient_for_milk_production:
                nutrition_supply: NutritionSupply = NutritionSupplyCalculator.calculate_nutrient_supply(
                    feeds_used=available_feeds, ration_formulation=ration, body_weight=animal.body_weight
                )

                walking_distance = (
                    animal.daily_distance if self.animal_combination == AnimalCombination.LAC_COW else 0.0
                )

                animal.set_nutrition_requirements(
                    housing=self.housing_type,
                    walking_distance=walking_distance,
                    previous_temperature=temperature,
                    available_feeds=available_feeds,
                )
                is_ration_adequate, evaluation_result = NutritionEvaluator.evaluate_nutrition_supply(
                    animal.nutrition_requirements, nutrition_supply, animal.animal_type.is_cow
                )

                if is_ration_adequate is True:
                    break

                if self.animal_combination == AnimalCombination.LAC_COW:
                    is_production_reduced: bool = animal.reduce_milk_production()
                    if not is_production_reduced:
                        break

                if self.average_milk_production < AnimalModuleConstants.MINIMUM_AVG_PEN_MILK:
                    ration_sufficient_for_milk_production = False
                    break

            animal.previous_nutrition_supply = animal.nutrition_supply
            animal.nutrition_supply = nutrition_supply
            total_nutrition_supply += nutrition_supply
            total_nutrition_requirements += animal.nutrition_requirements
            total_nutrition_evaluation_results += evaluation_result

        if self.animals_in_pen:
            number_animals_in_pen = len(self.animals_in_pen.values())
            self.average_nutrition_supply = total_nutrition_supply / number_animals_in_pen
            self.average_nutrition_requirements = total_nutrition_requirements / number_animals_in_pen
            self.average_nutrition_evaluation = total_nutrition_evaluation_results / number_animals_in_pen
        else:
            self.average_nutrition_supply = NutritionSupply.make_empty_nutrition_supply()
            self.average_nutrition_requirements = NutritionRequirements.make_empty_nutrition_requirements()
            self.average_nutrition_evaluation = NutritionEvaluationResults.make_empty_evaluation_results()

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
