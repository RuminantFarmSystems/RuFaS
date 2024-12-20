from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_grouping_scenarios import AnimalGroupingScenario
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import NutritionRequirements, NutritionEvaluationResults, NutritionSupply
from RUFAS.biophysical.feed.feed import Feed
from RUFAS.data_structures.animal_manure_excretions import AnimalManureExcretions
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.pen_statistics import PenStatistics
from RUFAS.biophysical.animal.nutrients.nutrition_evaluator import NutritionEvaluator
from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import NutritionSupplyCalculator
from RUFAS.biophysical.animal.ration.user_defined_ration_manager import UserDefinedRationManager
from RUFAS.data_structures.pen_manure_data import PenManureData
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

        self.ration = {}
        self.ration_per_animal = {}
        self.ration_nutrient_amount = {
            "dm": 0.0,
            "CP": 0.0,
            "ADF": 0.0,
            "NDF": 0.0,
            "lignin": 0.0,
            "ash": 0.0,
            "phosphorus": 0.0,
            "potassium": 0.0,
            "N": 0.0,
        }
        self.ration_nutrient_concentration = {
            "dm": 0.0,
            "CP": 0.0,
            "ADF": 0.0,
            "NDF": 0.0,
            "lignin": 0.0,
            "ash": 0.0,
            "phosphorus": 0.0,
            "potassium": 0.0,
            "N": 0.0,
        }
        self.dry_matter_intake = 0.0
        self.MEdiet = 0.0

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
        return [animal for animal in self.animals_in_pen.values()
                if animal.animal_type == AnimalType.LAC_COW or animal.animal_type == AnimalType.DRY_COW]

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

    def update_animals(self, new_animals: list[Animal], animal_combination: AnimalCombination) -> None:
        """
        Calls functions that will add new animals to the pen and update associated attributes.

        Parameters
        ----------
        new_animals: List[Calf | Cow | HeiferI | HeiferII | HeiferIII]
            list of new animals to be added to the pen
        animal_combination: AnimalCombination
            an AnimalCombination Enum representing the type of the new animals
        """
        self.add_new_animals(new_animals)
        self.calculate_daily_walking_distance()
        self.update_animal_combination(animal_combination)
        # self.update_classes_in_pen()

    def add_new_animals(self, new_animals: list[Animal]) -> None:
        """
        Adds all animals in new_animals to the pen.

        Parameters
        ----------
        new_animals: List[Calf | Cow | HeiferI | HeiferII | HeiferIII]
            list of new animals to be added to the pen

        """
        for animal in new_animals:
            self.animals_in_pen[animal.id] = animal
            self._set_animal_nutrient_values(animal)

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
                    animal.calculate_daily_walking_distance(
                        self.vertical_dist_to_parlor, self.horizontal_dist_to_parlor)

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
        animal_requirements: NutritionRequirements = [
            animal.nutrition_requirements for animal in self.animals_in_pen.values()
        ]
        return sum(animal_requirements) / len(self.animals_in_pen)

    def update_daily_walking_distance(self) -> None:
        if AnimalType.LAC_COW in self.animal_types_in_pen or AnimalType.DRY_COW in self.animal_types_in_pen:
            for animal in self.cows_in_pen:
                animal.calculate_daily_walking_distance(self.vertical_dist_to_parlor, self.horizontal_dist_to_parlor)

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

    def set_animal_nutritional_requirements(self, temperature: float) -> None:
        """
        Set the nutritional requirements for all animals in the pen.

        Parameters
        ----------
        temperature : float
            The temperature of the pen (C).

        """
        for animal in self.animals_in_pen.values():
            animal.set_nutrition_requirements(
                housing=self.housing_type,
                walking_distance=self.calculate_daily_walking_distance(),  # TODO: Make this function return distance
                previous_temperature=temperature,
            )

    @property
    def average_milk_production(self) -> float:
        """
        Calculate the average milk production for the cows in the pen.

        Returns
        -------
        float
            The average milk production reduction for the cows in the pen (kg).

        """
        return sum([cow.milk_production.daily_milk_produced for cow in self.cows_in_pen]) / len(self.cows_in_pen)

    def use_user_defined_ration(self, available_feeds: list[Feed]) -> None:
        """
        Calculate new ration for the pen based on the number of animals in the pen.

        Parameters
        ----------
        available_feeds : list[Feed]
            List of available feeds to be used in the ration formulation.

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
        average_animal_requirements: NutritionRequirements = self.average_animal_requirements
        ration = UserDefinedRationManager.get_user_defined_ration(animal_combination, average_animal_requirements)

        total_nutrient_evaluation_results = NutritionEvaluationResults(
            total_energy=0.0,
            maintenance=0.0,
            growth=0.0,
            protein=0.0,
            calcium=0.0,
            phosphorus=0.0,
            dry_matter=0.0,
            ndf=0.0,
            fat=0.0,
        )
        ration_sufficient_for_milk_production = True
        for animal in self.animals_in_pen.values():
            while ration_sufficient_for_milk_production:
                nutrition_supply: NutritionSupply = NutritionSupplyCalculator.calculate_nutrient_supply(
                    feeds_used=available_feeds, ration=ration, body_weight=animal.body_weight
                )

                animal.set_nutrition_requirements()
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

            animal.nutrition_supply = nutrition_supply
            total_nutrient_evaluation_results += evaluation_result

        self.average_nutrient_evaluation = total_nutrient_evaluation_results / len(self.animals_in_pen.values())

    def _calculate_dry_matter_intake(self) -> None:
        """Placeholder function to calculate the DMI for each animal on a daily basis."""
        pass
