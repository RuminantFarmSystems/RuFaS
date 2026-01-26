import math
from typing import NamedTuple, Any
from scipy.optimize import OptimizeResult
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.bedding.bedding import Bedding
from RUFAS.biophysical.animal.data_types.bedding_types import BeddingType
from RUFAS.biophysical.animal.data_types.nutrition_data_structures import (
    NutritionRequirements,
    NutritionEvaluationResults,
    NutritionSupply,
)
from RUFAS.biophysical.manure.manure_constants import ManureConstants
from RUFAS.biophysical.animal.data_types.animal_manure_excretions import AnimalManureExcretions
from RUFAS.data_structures.animal_to_manure_connection import (
    ManureStream,
    PenManureData,
    StreamType,
)
from RUFAS.data_structures.feed_storage_to_animal_connection import (
    RequestedFeed,
    AdvancePurchaseAllowance,
    TotalInventory,
    NutrientStandard,
)
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.nutrients.nutrition_evaluator import NutritionEvaluator
from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import NutritionSupplyCalculator
from RUFAS.biophysical.animal.ration.ration_manager import RationManager
from RUFAS.data_structures.feed_storage_to_animal_connection import RUFAS_ID, Feed
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.general_constants import GeneralConstants
from RUFAS.input_manager import InputManager

from RUFAS.biophysical.animal.ration.ration_optimizer import RationOptimizer, RationConfig
from RUFAS.output_manager import OutputManager

om = OutputManager()


class Pen:
    """
    This class represents a pen that houses animals during the simulation.

    Parameters
    ----------
    pen_id : int
        Unique identifier for the pen.
    pen_name : str
        Name of the pen.
    vertical_dist_to_milking_parlor : float
        Vertical distance from the pen to the milking parlor (m).
    horizontal_dist_to_milking_parlor : float
        Horizontal distance from the pen to the milking parlor (m).
    number_of_stalls : int
        Number of stalls available in the pen.
    housing_type : str
        Type of housing used in the pen.
    pen_type : str
        The pen type (freestall, tiestall, open lot, or bedded pack).
    animal_combination : AnimalCombination
        Combination of animal categories housed in the pen.
    max_stocking_density : float
        Maximum allowable stocking density for animals in the pen.
    minutes_away_for_milking : int
        Time required to reach the milking parlor from the pen (in minutes).
    first_parlor_processor : str | None
        Name of the processor to which the parlor stream will be sent.
    parlor_stream_name : str | None
        Name of the parlor stream.
    manure_streams : list[dict[str, str | float]]
        List of dictionaries containing manure stream information.

    Attributes
    ----------
    id : int
        Internal identifier for the pen.
    pen_name : str
        Name of the pen.
    vertical_dist_to_parlor : float
        Vertical distance from the pen to the milking parlor, in meters.
    horizontal_dist_to_parlor : float
        Horizontal distance from the pen to the milking parlor, in meters.
    num_stalls : int
        Total number of stalls available in the pen.
    housing_type : str
        Type of housing used in the pen.
    pen_type : str
        The pen type (freestall, tiestall, open lot, or bedded pack).
    animal_combination : AnimalCombination
        Combination of animal categories housed in the pen.
    max_stocking_density : float
        Maximum allowable stocking density for animals in the pen.
    minutes_away_for_milking : int
        Time required to reach the milking parlor from the pen (in minutes).
    first_parlor_processor : str
        Name of the processor to which the parlor stream will be sent.
    parlor_stream_name : str | None
        Name of the parlor stream.
    manure_streams : list[dict[str, str | float]]
        List of dictionaries containing manure stream information.
    animals_in_pen : dict[int, Animal]
        Dictionary mapping animal IDs to `Animal` objects housed in the pen.
    ration : dict[RUFAS_ID, float]
        Maps RuFaS Feed ID to the amount of that feed in the ration (kg dry matter).
    average_nutrition_evaluation : NutritionEvaluationResults
        Average surpluses and/or deficits of nutrients supplied to animals in the pen.
    allocated_feeds : set
        Set of IDs for the feeds allocated to this pen.
    om : OutputManager
        The output manager instance used to store and manage output data.
    """

    def __init__(
        self,
        pen_id: int,
        pen_name: str,
        vertical_dist_to_milking_parlor: float,
        horizontal_dist_to_milking_parlor: float,
        number_of_stalls: int,
        housing_type: str,
        pen_type: str,
        animal_combination: AnimalCombination,
        max_stocking_density: float,
        minutes_away_for_milking: int,
        first_parlor_processor: str | None,
        parlor_stream_name: str | None,
        manure_streams: list[dict[str, str | float]],
    ) -> None:
        self.id = pen_id
        self.pen_name = pen_name
        self.vertical_dist_to_parlor = vertical_dist_to_milking_parlor
        self.horizontal_dist_to_parlor = horizontal_dist_to_milking_parlor
        self.num_stalls = number_of_stalls
        self.housing_type = housing_type
        self.pen_type = pen_type
        self.animal_combination = animal_combination
        self.max_stocking_density = max_stocking_density
        self.minutes_away_for_milking = minutes_away_for_milking
        self.first_parlor_processor = first_parlor_processor
        self.parlor_stream_name = parlor_stream_name
        self.manure_streams = manure_streams

        self.beddings: dict[str, Bedding] = {}
        self._initialize_beddings()

        self.animals_in_pen: dict[int, Animal] = {}
        self.ration: dict[RUFAS_ID, float] = {}
        self.average_nutrition_evaluation: NutritionEvaluationResults = (
            NutritionEvaluationResults.make_empty_evaluation_results()
        )
        self.allocated_feeds: set[Any] = set()
        self.ration_optimizer = RationOptimizer()
        self.om = OutputManager()

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
    def total_enteric_methane(self) -> float:
        """Calculate the total enteric methane produced by all animals in the pen on the current day (g)."""
        return sum([animal.digestive_system.enteric_methane_emission for animal in self.animals_in_pen.values()])

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
    def total_pen_ration(self) -> dict[str, float]:
        """Returns the total ration of the pen."""
        if (number_of_animals_in_pen := len(self.animals_in_pen)) == 0:
            return {}
        current_pen_ration: dict[str, float] = {
            str(rufas_id): amount * number_of_animals_in_pen for rufas_id, amount in self.ration.items()
        }
        current_pen_ration["dry_matter_intake_total"] = sum([total_feed for total_feed in current_pen_ration.values()])
        current_pen_ration["byproducts_total"] = (
            self.average_nutrition_supply.byproduct_supply * number_of_animals_in_pen
        )
        return current_pen_ration

    def _initialize_beddings(self) -> None:
        """Initialize all beddings for manure streams in the pen."""
        im = InputManager()
        bedding_configs: list[dict[str, Any]] = im.get_data("animal.bedding_configs")
        bedding_configs_by_name: dict[str, dict[str, Any]] = {
            bedding_config["name"]: bedding_config for bedding_config in bedding_configs
        }

        for manure_stream in self.manure_streams:
            bedding_name: str = str(manure_stream["bedding_name"])
            if bedding_name not in bedding_configs_by_name:
                om.add_error(
                    "Unknown Bedding Name",
                    f"The bedding name '{bedding_name}' for pen {self.id} is not found in the bedding configs.",
                    info_map={
                        "class": self.__class__.__name__,
                        "function": self._initialize_beddings.__name__,
                    },
                )
                raise KeyError(
                    f"The bedding name '{bedding_name}' for pen {self.id} is not found in the bedding configs."
                )
            bedding_config = bedding_configs_by_name[bedding_name]
            bedding_config["bedding_type"] = BeddingType(bedding_config["bedding_type"])
            self.beddings[bedding_name] = Bedding(**bedding_config)

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
                feeds_used=available_feeds,
                ration_formulation=self.ration,
                body_weight=animal.body_weight,
                enteric_methane=animal.digestive_system.enteric_methane_emission,
                urinary_nitrogen=animal.digestive_system.manure_excretion.urine_nitrogen,
            )
            animal.nutrition_supply = nutrient_supply
            animal.nutrients.set_dry_matter_intake(nutrient_supply.dry_matter)
            animal.nutrients.set_phosphorus_intake(nutrient_supply.phosphorus)

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

    def get_manure_streams(self) -> dict[str, ManureStream]:
        """
        Constructs and returns ManureStream objects based on total manure excreted in a pen and user-defined
        stream splitting proportions. The ManureStream objects created here are representative of the total manure
        produced by the animals in any given pen.

        For pens with lactating cows, manure is partitioned between a parlor stream and general stream(s).
        For all other animal combinations, manure is routed only to general stream(s). The split ratios
        for general streams are user-defined and validated to sum to 1.0.

        Returns
        -------
        dict[str, ManureStream]:
            A dictionary mapping stream names to their corresponding ManureStream objects.

        Notes
        -----
        - The function first constructs a `total_stream` representing the full manure excretion from a pen.
        - If the animal combination is `LAC_COW`, a portion of this stream is split to a parlor stream
        based on the `minutes_away_for_milking` ratio using the `split_stream` method. Parlor deposition
        is set to 0.0, as manure deposition in the parlor is accounted for in source methodology (IFSM, 2023).
        - The remaining manure is split into one or more general streams according to the proportions
        specified in `self.manure_streams` and each assigned a `first_processor` directing it how to be routed once
        it reaches the manure module.
        - The function validates that all general stream proportions sum to 1.0 (or 100% of the general portion).
        - Manure methane potential is assigned according to animal combination. Manure from lactating, dry and close up
        animals are assigned a value of 0.24 m3 methane per kg of manure volatile solids, and calves and heifers are
        assigned a value of 0.17, based on the 2024 USDA method for entity scale inventory. If a pen contains heifers,
        dry and close up animals, methane potential is assigned as a weighted average based on number of dry/close up
        vs. heifers.

        """
        animal_manure_streams: dict[str, ManureStream] = {}
        if self.animal_combination == AnimalCombination.GROWING_AND_CLOSE_UP:
            total_animals_in_pen = len(self.animals_in_pen)
            num_growing = len(
                [
                    animal
                    for animal in self.animals_in_pen.values()
                    if animal.animal_type in [AnimalType.HEIFER_I, AnimalType.HEIFER_II]
                ]
            )
            num_close_up = len(
                [
                    animal
                    for animal in self.animals_in_pen.values()
                    if animal.animal_type in [AnimalType.HEIFER_III, AnimalType.DRY_COW]
                ]
            )
            methane_production_potential = (
                (0.17 * num_growing / total_animals_in_pen + 0.24 * num_close_up / total_animals_in_pen)
                if total_animals_in_pen > 0
                else 0.0
            )
        else:
            methane_production_potential = (
                0.17 if self.animal_combination in [AnimalCombination.CALF, AnimalCombination.GROWING] else 0.24
            )

        pen_animal_excretions = self.total_manure_excretion
        total_pen_manure_data = PenManureData(
            num_animals=len(self.animals_in_pen),
            manure_deposition_surface_area=self._calculate_manure_surface_area(),
            animal_combination=self.animal_combination,
            pen_type=self.pen_type,
            manure_urine_mass=pen_animal_excretions.urine,
            manure_urine_nitrogen=pen_animal_excretions.urine_nitrogen,
            stream_type=StreamType.GENERAL,
        )

        total_stream = ManureStream(
            water=pen_animal_excretions.manure_mass - pen_animal_excretions.total_solids,
            ammoniacal_nitrogen=pen_animal_excretions.manure_total_ammoniacal_nitrogen,
            nitrogen=pen_animal_excretions.manure_nitrogen,
            phosphorus=pen_animal_excretions.phosphorus * GeneralConstants.GRAMS_TO_KG,
            potassium=pen_animal_excretions.potassium * GeneralConstants.GRAMS_TO_KG,
            ash=0,
            non_degradable_volatile_solids=pen_animal_excretions.non_degradable_volatile_solids,
            degradable_volatile_solids=pen_animal_excretions.degradable_volatile_solids,
            total_solids=pen_animal_excretions.total_solids,
            volume=pen_animal_excretions.manure_mass / ManureConstants.SLURRY_MANURE_DENSITY,
            methane_production_potential=methane_production_potential,
            pen_manure_data=total_pen_manure_data,
            bedding_non_degradable_volatile_solids=0.0,
        )

        parlor_stream_proportion = None
        if self.animal_combination == AnimalCombination.LAC_COW:
            parlor_stream_proportion = self.minutes_away_for_milking / 1440
            general_stream_proportion = 1 - parlor_stream_proportion
            parlor_stream = total_stream.split_stream(
                split_ratio=parlor_stream_proportion,
                stream_type=StreamType.PARLOR,
                manure_stream_deposition_split=0.0,
            )
            if parlor_stream.pen_manure_data is not None and self.first_parlor_processor is not None:
                parlor_stream.pen_manure_data.set_first_processor(self.first_parlor_processor)
            base_parlor_stream_name = f"{self.parlor_stream_name}" if self.parlor_stream_name else "parlor_stream"
            parlor_stream_name = f"{base_parlor_stream_name}_PEN_{self.id}"
            animal_manure_streams[parlor_stream_name] = parlor_stream
        else:
            general_stream_proportion = 1.0

        self._validate_general_manure_stream_proportions()
        for stream in self.manure_streams:
            general_substream_proportion = float(stream.get("stream_proportion", 1.0))
            split_ratio = general_substream_proportion * general_stream_proportion
            manure_stream_deposit_split = (
                general_substream_proportion if parlor_stream_proportion is not None else split_ratio
            )
            manure_stream = total_stream.split_stream(
                split_ratio=split_ratio,
                stream_type=StreamType.GENERAL,
                manure_stream_deposition_split=manure_stream_deposit_split,
            )
            if manure_stream.pen_manure_data is not None:
                manure_stream.pen_manure_data.set_first_processor(str(stream.get("first_processor")))
            manure_stream = self._apply_bedding(manure_stream, str(stream.get("bedding_name")))
            stream_name = f"{str(stream.get('stream_name'))}_{self.animal_combination.name}_PEN_{self.id}"
            animal_manure_streams[stream_name] = manure_stream

        return animal_manure_streams

    def _apply_bedding(self, manure_stream: ManureStream, bedding_name: str) -> ManureStream:
        """
        Applies bedding to the given manure stream.

        Parameters
        ----------
        manure_stream : ManureStream
            The manure stream object.
        bedding_name : str
            The name of the bedding, this should correspond to a key in the `beddings` attribute.

        Returns
        -------
        ManureStream
            A new ManureStream object with updated attributes reflecting the impact of the applied bedding.

        """
        bedding = self.beddings[bedding_name]
        if manure_stream.pen_manure_data is None:
            raise ValueError(f"No PenManureData for pen {self.id}: pen_manure_data must be set to apply bedding.")
        num_animals = manure_stream.pen_manure_data.num_animals
        total_bedding_mass = bedding.calculate_total_bedding_mass(num_animals)
        total_bedding_volume = bedding.calculate_total_bedding_volume(num_animals)
        total_bedding_dry_solids = bedding.calculate_total_bedding_dry_solids(num_animals)

        manure_stream.pen_manure_data.set_bedding_mass_and_volume(
            bedding_mass=total_bedding_mass, bedding_volume=total_bedding_volume
        )

        return ManureStream(
            water=manure_stream.water + bedding.calculate_bedding_water(num_animals),
            ammoniacal_nitrogen=manure_stream.ammoniacal_nitrogen,
            nitrogen=manure_stream.nitrogen,
            phosphorus=manure_stream.phosphorus + (total_bedding_mass * bedding.bedding_phosphorus_content),
            potassium=manure_stream.potassium,
            ash=(
                manure_stream.ash
                if bedding.bedding_type != BeddingType.SAND
                else manure_stream.ash + total_bedding_dry_solids
            ),
            non_degradable_volatile_solids=manure_stream.non_degradable_volatile_solids,
            degradable_volatile_solids=manure_stream.degradable_volatile_solids,
            total_solids=manure_stream.total_solids + total_bedding_dry_solids,
            volume=manure_stream.volume + total_bedding_volume,
            methane_production_potential=manure_stream.methane_production_potential,
            pen_manure_data=manure_stream.pen_manure_data,
            bedding_non_degradable_volatile_solids=(
                0 if bedding.bedding_type == BeddingType.SAND else total_bedding_dry_solids
            ),
        )

    def _calculate_manure_surface_area(self) -> float:
        """
        Get the exposed manure surface area based on the pen type and whether there are lactating cows in the pen.

        Notes
        -----
        The exposed manure surface area is looked up from the following table:

        +---------------------------+-------------------+-------------------+
        | Pen Type                  | Has Lac Cows      | No Lac Cows       |
        +===========================+===================+===================+
        | Freestall                 | 3.5               | 2.5               |
        +---------------------------+-------------------+-------------------+
        | Tiestall                  | 1.2               | 1.0               |
        +---------------------------+-------------------+-------------------+
        | Bedded Pack               | 5.0               | 3.0               |
        +---------------------------+-------------------+-------------------+
        | Open Lot                  | 5.0               | 3.0               |
        +---------------------------+-------------------+-------------------+

        Returns
        -------
        float
            Exposed manure surface area (:math:`m^2`).

        Raises
        ------
        ValueError
            If the pen type is not one of the following: "freestall", "tiestall",
            "bedded pack", or "open lot".
        """

        ExposedManureSurfaceArea = NamedTuple(
            "ExposedManureSurfaceArea", [("has_lac_cows", float), ("no_lac_cows", float)]
        )
        freestall = ExposedManureSurfaceArea(has_lac_cows=3.5, no_lac_cows=2.5)
        tiestall = ExposedManureSurfaceArea(has_lac_cows=1.2, no_lac_cows=1.0)
        bedded_pack = ExposedManureSurfaceArea(has_lac_cows=5.0, no_lac_cows=3.0)
        open_lot = ExposedManureSurfaceArea(has_lac_cows=5.0, no_lac_cows=3.0)

        exposed_manure_surface_area_by_pen_type = {
            "freestall": freestall,
            "tiestall": tiestall,
            "bedded pack": bedded_pack,
            "open lot": open_lot,
        }

        if self.pen_type not in exposed_manure_surface_area_by_pen_type:
            raise ValueError(f"Invalid pen type: {self.pen_type}")

        exposed_manure_surface_area = exposed_manure_surface_area_by_pen_type[self.pen_type]

        if self.animal_combination == AnimalCombination.LAC_COW:
            return exposed_manure_surface_area.has_lac_cows * self.num_stalls
        return exposed_manure_surface_area.no_lac_cows * self.num_stalls

    def _validate_general_manure_stream_proportions(self) -> None:
        """
        Validates that the proportions of general manure streams sum to 1.0.

        Raises
        ------
        ValueError
            If the sum of the proportions is not equal to 1.0.
        """
        total_proportion = sum(float(stream.get("stream_proportion", 0.0)) for stream in self.manure_streams)
        if not math.isclose(total_proportion, 1.0, abs_tol=1e-6):
            om.add_error(
                "Pen manure stream proportions error",
                f"Manure stream proportions must sum to 1.0, but got {total_proportion:.6f}",
                info_map={
                    "class": self.__class__.__name__,
                    "function": self._validate_general_manure_stream_proportions.__name__,
                },
            )
            raise ValueError(f"Manure stream proportions must sum to 1.0, but got {total_proportion:.6f}")

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
                feeds_used=feeds_used,
                ration_formulation=ration_formulation,
                body_weight=animal.body_weight,
                enteric_methane=animal.digestive_system.enteric_methane_emission,
                urinary_nitrogen=animal.digestive_system.manure_excretion.urine_nitrogen,
            )
            animal.nutrients.set_dry_matter_intake(animal.nutrition_supply.dry_matter)
            animal.nutrients.set_phosphorus_intake(animal.nutrition_supply.phosphorus)

    def formulate_optimized_ration(  # noqa: C901
        self,
        is_ration_defined_by_user: bool,
        pen_available_feeds: list[Feed],
        temperature: float,
        max_daily_feeds: dict[RUFAS_ID, float],
        advance_purchase_allowance: AdvancePurchaseAllowance,
        total_inventory: TotalInventory,
        simulation_day: int,
    ) -> None:
        """
        Formulates a ration while optimizing for multiple goals.

        Parameters
        ----------
        is_ration_defined_by_user : bool
            True if user defined ration methodology to be used.
        pen_available_feeds : list[Feed]
            List of feeds available to formulate a new ration with for a pen.
        max_daily_feeds : dict[RUFAS_ID, float]
            Maximum amounts of each feed type that may be fed per animal per day.
        advance_purchase_allowance : AdvancePurchaseAllowance
            Maximum amounts of each feed type that may be purchased at the beginning of a feed interval.
        total_inventory : TotalInventory
            Amounts of feeds currently held in storage.
        simulation_day : int
            Day of simulation.

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
        previous_ration = getattr(self, "ration", None)
        num_attempts = 0
        self.set_animal_nutritional_requirements(temperature=temperature, available_feeds=pen_available_feeds)
        initial_pen_average_nutrition_requirements = self.average_nutrition_requirements
        initial_dry_matter_requirement = initial_pen_average_nutrition_requirements.dry_matter
        initial_protein_requirement = initial_pen_average_nutrition_requirements.metabolizable_protein

        initial_dry_matter_requirement_fixed = initial_dry_matter_requirement

        while True:
            num_attempts += 1
            solution, ration_config = self._attempt_formulation(
                is_ration_defined_by_user,
                pen_available_feeds,
                temperature,
                previous_ration,
                initial_dry_matter_requirement,
                initial_protein_requirement,
            )

            if not solution.success:
                constraints_failed_list = self.ration_optimizer.handle_failed_constraints(
                    num_attempts=num_attempts,
                    solution=solution,
                    ration_config=ration_config,
                    animal_combination=self.animal_combination,
                    pen_id=self.id,
                    pen_available_feeds=pen_available_feeds,
                    average_nutrient_requirements=self.average_nutrition_requirements,
                    initial_dry_matter_requirement=initial_dry_matter_requirement,
                    initial_protein_requirement=initial_protein_requirement,
                    sim_day=simulation_day,
                )

            # Lac cow success exit and non lac cow one time run only exit
            if solution.success or (self.animal_combination is not AnimalCombination.LAC_COW):
                break
            if num_attempts > RationManager.maximum_ration_reformulation_attempts:
                om.add_log(
                    "Maximum ration reformulation attempts exceeded.",
                    f"See output variable failed_constraint_summary_for_pen_{self.id} for more information.",
                    info_map,
                )
                break
            adjusted_dry_matter_lower = initial_dry_matter_requirement_fixed * (
                1 - AnimalModuleConstants.DMI_CONSTRAINT_FRACTION + RationManager.tolerance
            )
            adjusted_dry_matter_upper = initial_dry_matter_requirement_fixed * (
                1 + AnimalModuleConstants.DMI_CONSTRAINT_FRACTION - RationManager.tolerance
            )
            need_dry_matter_increase = bool(
                set(
                    [
                        "NE_total_constraint",
                        "NE_maintenance_and_activity_constraint",
                        "NE_lactation_constraint",
                        "NE_growth_constraint",
                        "calcium_constraint",
                        "phosphorus_constraint",
                        "protein_constraint_lower",
                        "DMI_constraint_lower",
                    ]
                )
                & set(constraints_failed_list)
            )

            if is_ration_defined_by_user and (
                adjusted_dry_matter_lower < initial_dry_matter_requirement < adjusted_dry_matter_upper
            ):
                if need_dry_matter_increase:
                    initial_dry_matter_requirement = initial_dry_matter_requirement * 1.1
                    continue

            if is_ration_defined_by_user:
                if self._reduce_on_lactation_failure_user_defined(info_map=info_map):
                    break
            else:
                self._reduce_on_lactation_failure(info_map=info_map)

        if solution.success:
            self._apply_successful_solution(solution, pen_available_feeds)
        elif is_ration_defined_by_user:
            self._apply_user_defined_ration(pen_available_feeds)
            self.om.add_log(
                "User defined ration used for non lactating cow pen after failed formulation attempt.",
                f"Check failed_constraint_summary_for_pen_{self.id} to see what caused formulation to fail. ",
                info_map,
            )
        elif self.ration == {}:
            self.om.add_error(
                "No previous ration available",
                f"Check failed_constraint_summary_for_pen_{self.id} to see what caused formulation to fail. "
                f"Possible solution is to provide additional feed ingredients to {self.animal_combination.name}.",
                info_map,
            )
            raise ValueError("No previous ration available")
        else:
            self.om.add_log(
                "Previous ration used because automated ration formulation failed for non lactating cow pen.",
                f"Automated ration formulation for a {self.animal_combination.name} pen failed."
                "Used most recently formulated ration instead."
                f"If this was unexpected, check failed_constraint_summary_for_pen_{self.id} to see what "
                "caused formulation to fail.",
                info_map,
            )

    def _attempt_formulation(
        self,
        is_ration_defined_by_user: bool,
        pen_feeds: list[Feed],
        temperature: float,
        previous_ration: Any,
        initial_dry_matter_requirement: float,
        initial_protein_requirement: float,
    ) -> tuple[OptimizeResult, RationConfig]:
        """Runs the optimizer and returns solution and config."""
        self.set_animal_nutritional_requirements(temperature=temperature, available_feeds=pen_feeds)
        if is_ration_defined_by_user:
            user_defined_ration_dictionary = RationManager.user_defined_rations[self.animal_combination]
            tolerance = RationManager.tolerance
        else:
            user_defined_ration_dictionary = None
            tolerance = None
        nutrient_standard = list(self.animals_in_pen.values())[0].nutrient_standard

        if nutrient_standard is NutrientStandard.NASEM:
            enteric_methane_list = []
            urine_nitrogen_list = []
            for animal in self.animals_in_pen.values():
                enteric_methane_list.append(animal.digestive_system.enteric_methane_emission)
                urine_nitrogen_list.append(animal.digestive_system.manure_excretion.urine_nitrogen)
            pen_average_enteric_methane = sum(enteric_methane_list) / len(enteric_methane_list)
            pen_average_urine_nitrogen = sum(urine_nitrogen_list) / len(urine_nitrogen_list)
        else:
            pen_average_enteric_methane = None
            pen_average_urine_nitrogen = None

        return self.ration_optimizer.attempt_optimization(
            nutrient_standard=nutrient_standard,
            pen_average_body_weight=self.average_body_weight,
            pen_average_enteric_methane=pen_average_enteric_methane,
            pen_average_urine_nitrogen=pen_average_urine_nitrogen,
            requirements=self.average_nutrition_requirements,
            initial_dry_matter_requirement=initial_dry_matter_requirement,
            initial_protein_requirement=initial_protein_requirement,
            pen_available_feeds=pen_feeds,
            animal_combination=self.animal_combination,
            previous_ration=previous_ration,
            user_defined_ration_dictionary=user_defined_ration_dictionary,
            user_defined_ration_tolerance=tolerance,
        )

    def _apply_successful_solution(self, solution: OptimizeResult | None, pen_feeds: list[Feed]) -> None:
        """Applies the optimizer solution to the pen."""
        self.ration = self.ration_optimizer.make_ration_from_solution(pen_available_feeds=pen_feeds, solution=solution)
        self.set_animal_nutritional_supply(feeds_used=pen_feeds, ration_formulation=self.ration)
        _, evaluation = NutritionEvaluator.evaluate_nutrition_supply(
            self.average_nutrition_requirements,
            self.average_nutrition_supply,
            self.animal_combination is AnimalCombination.LAC_COW,
        )
        self.average_nutrition_evaluation = (
            evaluation if self.is_populated else NutritionEvaluationResults.make_empty_evaluation_results()
        )

    def _apply_user_defined_ration(self, pen_feeds: list[Feed]) -> None:
        """
        Generates and applies a user defined ration to a pen.

        Parameters
        ----------
        pen_feeds : list[Feed]
            Feeds available in a given pen.
        """
        self.ration = RationManager.get_user_defined_ration(
            self.animal_combination, self.average_nutrition_requirements
        )
        self.set_animal_nutritional_supply(feeds_used=pen_feeds, ration_formulation=self.ration)
        _, evaluation = NutritionEvaluator.evaluate_nutrition_supply(
            self.average_nutrition_requirements,
            self.average_nutrition_supply,
            self.animal_combination is AnimalCombination.LAC_COW,
        )
        self.average_nutrition_evaluation = (
            evaluation if self.is_populated else NutritionEvaluationResults.make_empty_evaluation_results()
        )

    def _reduce_on_lactation_failure(self, info_map: dict[str, str]) -> None:
        """Processes failures and attempts milk reduction if needed for lactating cows."""
        if self.average_milk_production < AnimalModuleConstants.MINIMUM_AVG_PEN_MILK:
            self.om.add_error(
                "Milk production too low",
                f"Check failed_constraint_summary_for_pen_{self.id} to see cause.",
                info_map,
            )
            raise ValueError("Cannot meet minimum milk production.")

        if not self.reduce_milk_production():
            self.om.add_error(
                "Milk production reduction limit reached.",
                f"Check failed_constraint_summary_for_pen_{self.id} and consider adjusting input.",
                info_map,
            )
            raise ValueError("Milk production reduction limit reached.")

    def _reduce_on_lactation_failure_user_defined(self, info_map: dict[str, str]) -> bool:
        """Processes failures and attempts milk reduction if needed for lactating cows.
        Returns True if the ration formulation loop needs to be broken, modified for user defined ration logic,
        returning True instead of raising errors, while logging said outcome.

        Parameters
        ----------
        info_map : dict[str, Any]
            The info map to be added to the output pool.

        Returns
        -------
        bool
            True if ration formulation loop needs to be broken.
        """
        if self.average_milk_production < AnimalModuleConstants.MINIMUM_AVG_PEN_MILK:
            self.om.add_log(
                "Milk production too low",
                f"Check failed_constraint_summary_for_pen_{self.id} to see cause.",
                info_map,
            )
            return True

        if not self.reduce_milk_production():
            self.om.add_log(
                "Milk production reduction limit reached.",
                f"Check failed_constraint_summary_for_pen_{self.id} and consider adjusting input.",
                info_map,
            )
            return True

        return False

    def use_user_defined_ration(self, pen_available_feeds: list[Feed], temperature: float) -> None:
        """
        Calculate new ration for the pen based on the number of animals in the pen.

        Parameters
        ----------
        pen_available_feeds : list[Feed]
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
        self.set_animal_nutritional_requirements(temperature=temperature, available_feeds=pen_available_feeds)
        ration = RationManager.get_user_defined_ration(animal_combination, self.average_nutrition_requirements)
        self.set_animal_nutritional_supply(feeds_used=pen_available_feeds, ration_formulation=ration)

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
                self.set_animal_nutritional_requirements(temperature=temperature, available_feeds=pen_available_feeds)
                ration = RationManager.get_user_defined_ration(animal_combination, self.average_nutrition_requirements)
                self.set_animal_nutritional_supply(feeds_used=pen_available_feeds, ration_formulation=ration)
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
