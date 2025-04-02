import math
from collections import defaultdict
from datetime import date, timedelta
from typing import Any, Optional

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_genetics.animal_genetics import AnimalGenetics
from RUFAS.biophysical.animal.animal_grouping_scenarios import AnimalGroupingScenario
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.biophysical.animal.data_types.animal_enums import AnimalStatus
from RUFAS.biophysical.animal.data_types.animal_population import AnimalPopulation
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import NewBornCalfValuesTypedDict, SoldAnimalTypedDict
from RUFAS.biophysical.animal.data_types.herd_statistics import HerdStatistics
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.daily_routines_output import DailyRoutinesOutput
from RUFAS.biophysical.animal.data_types.reproduction import HerdReproductionStatistics
from RUFAS.biophysical.animal.herd_factory import HerdFactory
from RUFAS.biophysical.animal.milk.lactation_curve import LactationCurve
from RUFAS.biophysical.animal.milk.milk_production import MilkProduction
from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import NutritionSupplyCalculator
from RUFAS.biophysical.animal.pen import Pen
from RUFAS.biophysical.animal.ration.calf_ration_manager import CalfMilkType, CalfRationManager, WHOLE_MILK_ID
from RUFAS.biophysical.animal.ration.user_defined_ration_manager import UserDefinedRationManager
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.data_structures.pen_manure_data import PenManureData
from RUFAS.data_structures.feed_storage_to_animal_connection import (
    Feed,
    IdealFeeds,
    RequestedFeed,
    NutrientStandard,
    RUFAS_ID,
    TotalInventory,
    AdvancePurchaseAllowance,
)
from RUFAS.enums import AnimalCombination
from RUFAS.general_constants import GeneralConstants
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.purchased_feed_emissions_estimator import PurchasedFeedEmissionsEstimator
from RUFAS.time import Time
from RUFAS.util import Utility
from RUFAS.weather import Weather


class HerdManager:
    DEFAULT_NUM_STALLS_BY_COMBINATION = {
        AnimalCombination.CALF: AnimalModuleConstants.DEFAULT_NUM_STALLS_FOR_CALF_PEN,
        AnimalCombination.GROWING: AnimalModuleConstants.DEFAULT_NUM_STALLS_FOR_GROWING_PEN,
        AnimalCombination.CLOSE_UP: AnimalModuleConstants.DEFAULT_NUM_STALLS_FOR_CLOSE_UP_PEN,
        AnimalCombination.LAC_COW: AnimalModuleConstants.DEFAULT_NUM_STALLS_FOR_LAC_COW_PEN,
        AnimalCombination.GROWING_AND_CLOSE_UP: AnimalModuleConstants.DEFAULT_NUM_STALLS_FOR_GROWING_AND_CLOSE_UP_PEN,
    }
    ANIMAL_GROUPING_SCENARIO: AnimalGroupingScenario

    @classmethod
    def set_animal_grouping_scenario(cls, scenario: AnimalGroupingScenario) -> None:
        """
        Sets the animal grouping scenario to the given scenario.

        Parameters
        ----------
        scenario : AnimalGroupingScenario
                The scenario to set the animal grouping scenario to.

        """

        cls.ANIMAL_GROUPING_SCENARIO = scenario

    def __init__(
        self,
        weather: Weather,
        time: Time,
        is_ration_defined_by_user: bool,
        available_feeds: list[Feed],
        feed_emissions_estimator: PurchasedFeedEmissionsEstimator | None = None,
    ) -> None:
        """
        Initializes the pens and the animal herd in the simulation with data from
        user inputs.

        Parameters
        ----------
        weather : Weather
            instance of the Weather class
        time : Time
            instance of the Time class
        is_ration_defined_by_user : bool
            True if user-defined rations are used for the herd, otherwise false.
        available_feeds : list[Feed]
            Nutrition information of feeds available to formulate animals rations with.
        feed_emissions_estimator : PurchasedFeedEmissionsEstimator, default=None
            Instance of the PurchasedFeedEmissionsEstimator class.

        """
        self.im = InputManager()
        self.om = OutputManager()
        config_data: dict[str, Any] = self.im.get_data("config")
        animal_config_data: dict[str, Any] = self.im.get_data("animal")
        manure_management_config_data: list[dict[str, Any]] = self.im.get_data("manure_management")[
            "manure_management_scenarios"
        ]

        AnimalConfig.initialize_animal_config()

        LactationCurve.set_lactation_parameters(time)
        MilkProduction.set_milk_quality(
            AnimalConfig.milk_fat_percent, AnimalConfig.true_protein_percent, AnimalModuleConstants.MILK_LACTOSE
        )

        self.simulate_animals = config_data.get("simulate_animals", True)

        self.calves: list[Animal] = []
        self.heiferIs: list[Animal] = []
        self.heiferIIs: list[Animal] = []
        self.heiferIIIs: list[Animal] = []
        self.cows: list[Animal] = []
        self.replacement_market: list[Animal] = []

        self.heifers_sold: list[Animal] = []
        self.cows_culled: list[Animal] = []

        self.all_pens: list[Pen] = []
        self.animal_to_pen_id_map: dict[int, int] = {}

        self.set_animal_grouping_scenario(AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW)

        self.herd_statistics = HerdStatistics()
        self.herd_statistics.herd_num = animal_config_data["herd_information"]["herd_num"]
        self.herd_reproduction_statistics = HerdReproductionStatistics()

        self.housing = animal_config_data["housing"]
        self.pasture_concentrate = animal_config_data["pasture_concentrate"]

        self.is_ration_defined_by_user = is_ration_defined_by_user
        if self.is_ration_defined_by_user:
            ration_feed_config = self.im.get_data("feed")
            UserDefinedRationManager.set_user_defined_rations(ration_feed_config)
            self.set_milk_type_in_calf_ration_manager()
        self._max_daily_feeds: dict[RUFAS_ID, float] = {}

        allowances = self.im.get_data("feed.allowances")
        self.advance_purchase_allowance = AdvancePurchaseAllowance(allowances)

        self.formulation_interval = animal_config_data["ration"]["formulation_interval"]
        nutrient_standard = NutrientStandard(config_data["nutrient_standard"])
        Animal.set_nutrient_standard(nutrient_standard)
        NutritionSupplyCalculator.nutrient_standard = nutrient_standard

        self.initialize_pens(animal_config_data["pen_information"], manure_management_config_data)

        if self.simulate_animals:
            herd_population = HerdFactory.post_animal_population
            (self.calves, self.heiferIs, self.heiferIIs, self.heiferIIIs, self.cows, self.replacement_market) = (
                herd_population.calves,
                herd_population.heiferIs,
                herd_population.heiferIIs,
                herd_population.heiferIIIs,
                herd_population.cows,
                herd_population.replacement,
            )

            self.allocate_animals_to_pens()
            self.initialize_nutrient_requirements(weather, time, available_feeds)

        self._print_animal_num_warnings(animal_config_data["herd_information"])

        self.feeds_emissions_estimator: Optional[PurchasedFeedEmissionsEstimator] = (
            feed_emissions_estimator or PurchasedFeedEmissionsEstimator()
        )

    @property
    def animals_by_type(self) -> dict[AnimalType, list[Animal]]:
        """
        Group animals by type.

        Returns
        -------
        dict[AnimalType, list[Animal]]
            A dictionary where each key corresponds to an `AnimalType` enum and
            each value is a list of `Animal` objects belonging to that type.

        """
        return {
            AnimalType.CALF: self.calves,
            AnimalType.HEIFER_I: self.heiferIs,
            AnimalType.HEIFER_II: self.heiferIIs,
            AnimalType.HEIFER_III: self.heiferIIIs,
            AnimalType.LAC_COW: [cow for cow in self.cows if cow.is_milking],
            AnimalType.DRY_COW: [cow for cow in self.cows if not cow.is_milking],
        }

    @property
    def animals_by_combination(self) -> dict[AnimalCombination, list[Animal]]:
        """
        Group animals by combination.

        Returns
        -------
        dict[AnimalCombination, list[Animal]]
            A dictionary where the keys are instances of `AnimalCombination`, and
            the values are lists of `Animal` instances belonging to the corresponding
            combination.

        """
        animals_by_combination = defaultdict(list)
        for animal in [
            *self.calves,
            *self.heiferIs,
            *self.heiferIIs,
            *self.heiferIIIs,
            *self.cows,
        ]:
            animal_combination = self.ANIMAL_GROUPING_SCENARIO.find_animal_combination(animal)
            animals_by_combination[animal_combination].append(animal)
        return animals_by_combination

    @property
    def pens_by_animal_combination(self) -> dict[AnimalCombination, list[Pen]]:
        """
        Group a list of pens by animal combination.

        Returns
        -------
        Dict[AnimalCombination, list[Pen]]
            Dictionary of pens grouped by animal combination.

        """

        pen_group_by_animal_combination = defaultdict(list)
        for pen in self.all_pens:
            pen_group_by_animal_combination[pen.animal_combination].append(pen)
        return pen_group_by_animal_combination

    @property
    def phosphorus_concentration_by_animal_class(self) -> dict[AnimalType, float]:
        """
        Retrieves the phosphorus concentration for each animal type.

        Returns
        -------
        dict[AnimalType, float]
            A dictionary mapping each animal type to its corresponding phosphorus
            concentration. If the total body weight of an animal class is zero, the
            phosphorus concentration is set to 0.0 for that class.

        Notes
        -----
        These variables are the P concentrations of each class of animal. They are calculated daily and are used when an
        animal is added to the herd, whether by birth or replacement herd purchase. They  are calculated by dividing the
        total P in the animals of the class by the total body weight of the animals, on a per-animal basis.

        """
        phosphorus_concentration_by_animal_class: dict[AnimalType, float] = {
            animal_type: 0.0 for animal_type in AnimalType
        }

        for animal_type in AnimalType:
            animals = self.animals_by_type[animal_type]
            total_phosphorus = sum(
                [animal.nutrients.total_phosphorus_in_animal * GeneralConstants.GRAMS_TO_KG for animal in animals]
            )
            total_body_weight = sum([animal.body_weight for animal in animals])
            phosphorus_concentration_by_animal_class[animal_type] = (
                total_phosphorus / total_body_weight if total_body_weight > 0 else 0.0
            )

        return phosphorus_concentration_by_animal_class

    @property
    def current_herd_size(self) -> int:
        """
        Calculates the current size of the herd based on the number of heiferIIIs and cows.

        Returns
        -------
        int
            The current size of the herd.

        """
        return len(self.heiferIIIs) + len(self.cows)

    def collect_pen_manure_data(self) -> list[PenManureData]:
        """
        Returns the manure information from all pens in PenManureData.

        Returns
        -------
        list[PenManureData]
            A list of all pens' manure information.

        """
        return [pen.get_manure_data() for pen in self.all_pens]

    def collect_daily_feed_request(self) -> RequestedFeed:
        """
        Collects total amount of feeds needed for all animals on the current day.

        Returns
        -------
        dict[RUFAS_ID, float]
            Mapping of the feed ID's requested to the amounts of feed (kg dry matter).

        """
        total_requested_feed = RequestedFeed({})
        for pen in self.all_pens:
            total_requested_feed += RequestedFeed(pen.ration) * len(pen.animals_in_pen.values())

        return total_requested_feed

    def print_herd_snapshot(self, txt: str) -> None:
        """
        Prints a formatted snapshot of the herd, showing the current count of
        different categories of cattle such as calves, heifer groups, and cows.

        Parameters
        ----------
        txt : str
            A descriptive prefix to the snapshot summary, typically used to
            identify the context or timestamp of the snapshot.

        """
        print(
            f"{txt}\tcalves: {len(self.calves)}\t"
            f"heiferIs: {len(self.heiferIs)}\t"
            f"heiferIIs: {len(self.heiferIIs)}\t"
            f"heiferIIIs: {len(self.heiferIIIs)}\t"
            f"cows: {len(self.cows)}\t"
        )

    def _print_animal_num_warnings(self, herd_data: dict[str, Any]) -> None:
        """
        If simulate_animals is false, creates warnings if there are more than 0 animals for any of the animal types,
            and logs how many warnings were generated
        Otherwise, if simulate_animals is true, logs that it is true

        Parameters
        ----------
        herd_data : Dict[str, Any]
            dictionary containing information about the herd

        """

        animal_keys = {
            "calf_num",
            "heiferI_num",
            "heiferII_num",
            "heiferIII_num_springers",
            "cow_num",
        }

        info_map = {
            "class": self.__class__.__name__,
            "function": self._print_animal_num_warnings.__name__,
            "simulate_animals": self.simulate_animals,
            "herd_data_animal_nums": {key: herd_data[key] for key in animal_keys},
        }

        counter = 0

        if not self.simulate_animals:
            for key in animal_keys:
                if herd_data[key] != 0:
                    self.om.add_warning(
                        f"invalid_{key}_warning",
                        f"Warning: simulate_animals is false, but {key} is not.",
                        info_map,
                    )
                    counter += 1
            self.om.add_log(
                "num_warnings_associated_with_simulate_animals",
                f"{counter} warnings were associated with simulate_animals",
                info_map,
            )
        else:
            self.om.add_log("simulate_animals_flag", "simulate_animals is true", info_map)

    def _reset_daily_statistics(self) -> None:
        """Reset the daily herd statistics."""
        self.herd_statistics.reset_daily_stats()
        self.herd_statistics.reset_parity()
        self.herd_statistics.reset_cull_reason_stats()

    def _update_sold_animal_statistics(
        self, sold_newborn_calves: list[Animal], sold_heiferIIs: list[Animal], sold_and_died_cows: list[Animal]
    ) -> None:
        """Call the corresponding functions to update the statistics for sold animals"""
        self._update_sold_and_died_cow_statistics(sold_and_died_cows)
        self._update_sold_heiferII_statistics(sold_heiferIIs)
        self._update_sold_newborn_calf_statistics(sold_newborn_calves)

    def _perform_daily_routines_for_animals(
        self, time: Time, animals: list[Animal]
    ) -> tuple[list[Animal], list[Animal], list[Animal], list[Animal]]:
        """Perform daily routines for a given list of animals."""
        graduated_animals: list[Animal] = []
        sold_animals: list[Animal] = []
        sold_newborn_calves: list[Animal] = []
        newborn_calves: list[Animal] = []

        for animal in animals:
            animal_daily_routines_output: DailyRoutinesOutput = animal.daily_routines(time)
            self.herd_reproduction_statistics += animal_daily_routines_output.herd_reproduction_statistics
            if animal_daily_routines_output.animal_status == AnimalStatus.LIFE_STAGE_CHANGED:
                graduated_animals.append(animal)
                if animal_daily_routines_output.newborn_calf_config is not None:
                    newborn_calf = self._create_newborn_calf(
                        animal_daily_routines_output.newborn_calf_config, simulation_day=time.simulation_day
                    )
                    if newborn_calf.sold:
                        sold_newborn_calves.append(newborn_calf)
                    else:
                        newborn_calves.append(newborn_calf)
            elif animal_daily_routines_output.animal_status in [AnimalStatus.DEAD, AnimalStatus.SOLD]:
                sold_animals.append(animal)
        return graduated_animals, sold_animals, sold_newborn_calves, newborn_calves

    def _update_herd_structure(
        self,
        graduated_animals: list[Animal],
        newborn_calves: list[Animal],
        newly_added_animals: list[Animal],
        removed_animals: list[Animal],
        available_feeds: list[Feed],
        current_day_conditions: CurrentDayConditions,
        total_inventory: TotalInventory,
    ) -> None:
        """Call the corresponding functions to update the herd structure and reassign animals to new pens."""
        self._handle_graduated_animals(graduated_animals, available_feeds, current_day_conditions, total_inventory)
        self._handle_newly_added_animals(newborn_calves, available_feeds, current_day_conditions, total_inventory)
        self._handle_newly_added_animals(newly_added_animals, available_feeds, current_day_conditions, total_inventory)

        for removed_animal in removed_animals:
            self._remove_animal_from_pen_and_id_map(removed_animal)

    def daily_routines(
        self, available_feeds: list[Feed], time: Time, weather: Weather, total_inventory: TotalInventory
    ) -> list[PenManureData]:
        """
        Perform daily routines for managing animal herds and updating associated data.

        This method handles all daily activities related to the management of animal herds,
        including animal transitions (graduation, removal), sales, births, updates to herd
        statistics, and manure data collection.

        Parameters
        ----------
        available_feeds : list[Feed]
            A list of feed resources available for the day.
        time : Time
            An object representing the current time and simulation day.
        weather : Weather
            An object providing weather conditions affecting herd activities.
        total_inventory : TotalInventory
            Object representing the total inventory of herd-related resources.

        Returns
        -------
        list[PenManureData]
            A list of manure data for each pen after performing daily activities.

        """
        graduated_animals: list[Animal] = []
        newborn_calves: list[Animal] = []
        removed_animals: list[Animal] = []

        sold_newborn_calves: list[Animal] = []

        self._reset_daily_statistics()
        self.herd_reproduction_statistics = HerdReproductionStatistics()

        graduated_calves, sold_calves, _, _ = self._perform_daily_routines_for_animals(time, self.calves)
        graduated_animals += graduated_calves
        removed_animals += sold_calves

        graduated_heiferIs, sold_heiferIs, _, _ = self._perform_daily_routines_for_animals(time, self.heiferIs)
        graduated_animals += graduated_heiferIs
        removed_animals += sold_heiferIs

        graduated_heiferIIs, sold_heiferIIs, _, _ = self._perform_daily_routines_for_animals(time, self.heiferIIs)
        graduated_animals += graduated_heiferIIs
        removed_animals += sold_heiferIIs

        (graduated_heiferIIIs, sold_heiferIIIs, sold_newborn_calves_from_heiferIIIs, newborn_calves_from_heiferIIIs) = (
            self._perform_daily_routines_for_animals(time, self.heiferIIIs)
        )
        graduated_animals += graduated_heiferIIIs
        removed_animals += sold_heiferIIIs
        sold_newborn_calves += sold_newborn_calves_from_heiferIIIs
        newborn_calves += newborn_calves_from_heiferIIIs

        (graduated_cows, sold_and_died_cows, sold_newborn_calves_from_cows, newborn_calves_from_cows) = (
            self._perform_daily_routines_for_animals(time, self.cows)
        )
        graduated_animals += graduated_cows
        removed_animals += sold_and_died_cows
        sold_newborn_calves += sold_newborn_calves_from_cows
        newborn_calves += newborn_calves_from_cows

        self._update_sold_animal_statistics(
            sold_newborn_calves=sold_newborn_calves,
            sold_heiferIIs=sold_heiferIIs,
            sold_and_died_cows=sold_and_died_cows,
        )

        removed_animals += self._check_if_heifers_need_to_be_sold(simulation_day=time.simulation_day)
        newly_added_animals = self._check_if_replacement_heifers_needed(time=time)

        self._update_herd_structure(
            graduated_animals=graduated_animals,
            newborn_calves=newborn_calves,
            newly_added_animals=newly_added_animals,
            removed_animals=removed_animals,
            available_feeds=available_feeds,
            current_day_conditions=weather.get_current_day_conditions(time),
            total_inventory=total_inventory,
        )

        self.record_pen_history(time.simulation_day)

        herd_manager_output: list[PenManureData] = [pen.get_manure_data() for pen in self.all_pens]
        enteric_methane_emission_by_pen: dict[str, float] = {
            f"{pen.id}_{pen.animal_combination.name}": pen.total_enteric_methane for pen in self.all_pens
        }

        self.update_herd_statistics()

        self.herd_statistics.newborn_calves_num = len(newborn_calves)
        
        AnimalModuleReporter.report_animal_module_manure(herd_manager_output)
        AnimalModuleReporter.report_enteric_methane_emission(enteric_methane_emission_by_pen)
        AnimalModuleReporter.report_daily_reports(self, time.simulation_day)

        return herd_manager_output

    def _create_newborn_calf(self, newborn_calf_config: NewBornCalfValuesTypedDict, simulation_day: int) -> Animal:
        """
        Creates a new newborn calf instance and records its entry event in the herd if it
        is not sold.

        Parameters
        ----------
        newborn_calf_config : NewBornCalfValuesTypedDict
            Configuration for the newborn calf containing its attributes.
        simulation_day : int
            The current day in the simulation.

        Returns
        -------
        Animal
            An instance of the Animal class representing the newly created newborn calf.

        """
        newborn_calf_config["id"] = AnimalPopulation.next_id()
        newborn_calf: Animal = Animal(args=newborn_calf_config, simulation_day=simulation_day)
        if not newborn_calf.sold:
            newborn_calf.events.add_event(newborn_calf.days_born, simulation_day, animal_constants.ENTER_HERD)
        return newborn_calf

    def _check_if_heifers_need_to_be_sold(
        self,
        simulation_day: int,
    ) -> list[Animal]:
        """
        Checks if surplus heifers need to be sold based on herd size.

        This method evaluates if the current number of heifers and cows exceeds a
        specified threshold (defined as 3% over the herd statistics' target
        herd size). If the threshold is surpassed, heiferIIIs are removed from the
        herd until the herd size falls within the acceptable range.

        Parameters
        ----------
        simulation_day : int
            The simulation day on which the check and potential sale is conducted.

        Returns
        -------
        list[Animal]
            A list of heiferIIIs to be sold.

        """
        animals_removed: list[Animal] = []
        while (
            self.current_herd_size > self.herd_statistics.herd_num * animal_constants.SELLING_THRESHOLD
            and len(self.heiferIIIs) > 0
        ):
            removed_heiferIII = self.heiferIIIs.pop()
            animals_removed.append(removed_heiferIII)
            removed_heiferIII.sold_at_day = simulation_day
            self.herd_statistics.sold_heiferIIIs_info.append(
                SoldAnimalTypedDict(
                    id=removed_heiferIII.id,
                    animal_type=removed_heiferIII.animal_type.value,
                    sold_at_day=removed_heiferIII.sold_at_day,
                    body_weight=removed_heiferIII.body_weight,
                    cull_reason="NA",
                    days_in_milk="NA",
                    parity="NA",
                )
            )
            self.herd_statistics.sold_heiferIII_oversupply_num += 1
            self.herd_statistics.heiferIII_num -= 1
        return animals_removed

    def _check_if_replacement_heifers_needed(self, time: Time) -> list[Animal]:
        """
        Checks if replacement heifers are needed to maintain the herd size.

        This function determines whether additional heiferIIIs need to be added to the herd based on
        the current herd size, purchase thresholds, and the availability of heifers in the
        replacement market.

        Parameters
        ----------
        time : Time
            An instance of the `Time` class providing the current simulation day and date.

        Returns
        -------
        list[Animal]
            A list of heiferIIIs bought.

        """
        animals_added: list[Animal] = []
        while (
            self.current_herd_size + self.herd_statistics.bought_heifer_num
            < self.herd_statistics.herd_num * animal_constants.BUYING_THRESHOLD
            and time.simulation_day > 1
        ):
            if len(self.replacement_market) == 0:
                break
            replacement = self.replacement_market.pop(0)
            replacement.events.add_event(replacement.days_born, time.simulation_day, animal_constants.ENTER_HERD)
            replacement.nutrients.total_phosphorus_in_animal = (
                0.0072 * replacement.body_weight * GeneralConstants.KG_TO_GRAMS
            )
            replacement_birth_date = time.current_date.date() - timedelta(days=replacement.days_born)
            replacement.net_merit = AnimalGenetics.assign_net_merit_value_to_animals_entering_herd(
                replacement_birth_date.strftime("%Y-%m-%d"), replacement.breed
            )
            animals_added.append(replacement)
            self.herd_statistics.bought_heifer_num += 1

        return animals_added

    def _remove_animal_from_current_array(self, animal: Animal) -> None:
        """
        Remove an animal object from the current array that it belongs to.

        Parameters
        ----------
        animal : Animal
            The animal instance to be removed from its current array.

        """
        self.calves = [calf for calf in self.calves if calf != animal]
        self.heiferIs = [heiferI for heiferI in self.heiferIs if heiferI != animal]
        self.heiferIIs = [heiferII for heiferII in self.heiferIIs if heiferII != animal]
        self.heiferIIIs = [heiferIII for heiferIII in self.heiferIIIs if heiferIII != animal]
        self.cows = [cow for cow in self.cows if cow != animal]

    def _add_animal_to_new_array(self, animal: Animal) -> None:
        """
        Adds an animal to the appropriate array based on its type.

        Parameters
        ----------
        animal : Animal
            The animal object to be added to the respective array based on its `animal_type`.

        """
        animal_type_to_array_map: dict[AnimalType, list[Animal]] = {
            AnimalType.CALF: self.calves,
            AnimalType.HEIFER_I: self.heiferIs,
            AnimalType.HEIFER_II: self.heiferIIs,
            AnimalType.HEIFER_III: self.heiferIIIs,
            AnimalType.LAC_COW: self.cows,
            AnimalType.DRY_COW: self.cows,
        }
        new_array = animal_type_to_array_map[animal.animal_type]
        new_array.append(animal)

    def _update_animal_array(self, animal: Animal) -> None:
        """
        Updates the internal animal array by removing the given animal from its current
        array and adding it to a new array.

        Parameters
        ----------
        animal : Animal
            The animal object to update in the internal arrays.

        """
        self._remove_animal_from_current_array(animal)
        self._add_animal_to_new_array(animal)

    def _handle_graduated_animals(
        self,
        graduated_animals: list[Animal],
        available_feeds: list[Feed],
        current_day_conditions: CurrentDayConditions,
        total_inventory: TotalInventory,
    ) -> None:
        """
        Reassigns animals that have graduated to a new pen, and updates the pen id map.

        Parameters
        ----------
        graduated_animals : list[Animal]
            List of animals that have graduated and need to be reassigned to a new pen.
        available_feeds : list[Feed]
            Nutrition information of feeds available to formulate animals rations with.
        current_day_conditions : CurrentDayConditions
            Object representing the current conditions of the day.
        total_inventory : TotalInventory
            Inventory currently available or projected to be available at a future date.

        """
        for animal in graduated_animals:
            self._remove_animal_from_pen_and_id_map(animal)
            self._update_animal_array(animal)
            self._add_animal_to_pen_and_id_map(animal, available_feeds, current_day_conditions, total_inventory)

    def _handle_newly_added_animals(
        self,
        new_animals: list[Animal],
        available_feeds: list[Feed],
        current_day_conditions: CurrentDayConditions,
        total_inventory: TotalInventory,
    ) -> None:
        """
        Adds newly added animals to their appropriate pen and updates the pen id map.

        Parameters
        ----------
        new_animals : list[Animal]
            List of newly added animals.
        available_feeds : list[Feed]
            Nutrition information of feeds available to formulate animals rations with.
        current_day_conditions : CurrentDayConditions
            Object representing the current conditions of the day.
        total_inventory : TotalInventory
            Inventory currently available or projected to be available at a future date.

        """
        for animal in new_animals:
            self._add_animal_to_pen_and_id_map(animal, available_feeds, current_day_conditions, total_inventory)
            self._add_animal_to_new_array(animal)

    def _remove_animal_from_pen_and_id_map(self, animal: Animal) -> None:
        """
        Removes animal from its current pen, and removes it from the pen id map.

        Parameters
        ----------
        animal : Animal
            The animal to be removed from its current pen and the pen id map.

        """
        pen_id = self.animal_to_pen_id_map[animal.id]
        self.all_pens[pen_id].remove_animals_by_ids([animal.id])
        del self.animal_to_pen_id_map[animal.id]
        self._remove_animal_from_current_array(animal)

    def _add_animal_to_pen_and_id_map(
        self,
        animal: Animal,
        available_feeds: list[Feed],
        current_day_conditions: CurrentDayConditions,
        total_inventory: TotalInventory,
    ) -> None:
        """
        Adds animal to pen with the lowest stocking density, and updates the pen id map accordingly.

        Parameters
        ----------
        animal : Animal
            The animal to be added to a pen.
        available_feeds : list[Feed]
            Nutrition information of feeds available to formulate animals rations with.
        current_day_conditions : CurrentDayConditions
            Object representing the current conditions of the day.
        total_inventory : TotalInventory
            Inventory currently available or projected to be available at a future date.

        """
        animal_combination = self.ANIMAL_GROUPING_SCENARIO.find_animal_combination(animal)
        pen_with_min_stocking_density = min(
            self.pens_by_animal_combination[animal_combination],
            key=lambda p: p.current_stocking_density,
        )
        if pen_with_min_stocking_density.is_populated:
            pen_with_min_stocking_density.update_animals([animal], animal_combination, available_feeds)
        else:
            pen_with_min_stocking_density.insert_single_animal_into_animals_in_pen_map(animal)
            pen_with_min_stocking_density.set_animal_nutritional_requirements(
                temperature=current_day_conditions.mean_air_temperature, available_feeds=available_feeds
            )
            self._reformulate_ration_single_pen(
                pen=pen_with_min_stocking_density,
                available_feeds=available_feeds,
                current_temperature=current_day_conditions.mean_air_temperature,
                total_inventory=total_inventory,
            )

        self.animal_to_pen_id_map[animal.id] = pen_with_min_stocking_density.id

    def initialize_pens(
        self, all_pen_data: list[dict[str, Any]], manure_management_scenarios: list[dict[str, Any]]
    ) -> None:
        """
        Populates the list of pens with the information from the input json file.

        Parameters
        ----------
        all_pen_data: list[dict[str, Any]]
            List containing information about the pens.
        manure_management_scenarios : Dict[str, Any]
            Dictionary containing information about the manure management scenarios.

        """
        for pen_data in all_pen_data:
            animal_combination_value: str = pen_data.get("animal_combination", "")
            pen_id = pen_data.get("id", 0)
            pen_name = pen_data.get("name", "")
            animal_combination = AnimalCombination(AnimalCombination[animal_combination_value].value)
            vertical_dist_to_milking_parlor = pen_data.get("vertical_dist_to_milking_parlor", 0.0)
            horizontal_dist_to_milking_parlor = pen_data.get("horizontal_dist_to_milking_parlor", 0.0)
            number_of_stalls = pen_data.get("number_of_stalls", 0)
            housing_type = pen_data.get("housing_type", "")
            pen_type = pen_data.get("pen_type", "")
            max_stocking_density = pen_data.get("max_stocking_density", 0.0)

            manure_management_scenario_id = pen_data.get("manure_management_scenario_id")
            manure_management_scenario = [
                scenario
                for scenario in manure_management_scenarios
                if scenario["scenario_id"] == manure_management_scenario_id
            ][0]
            bedding_type = manure_management_scenario["bedding_type"]
            manure_handling = manure_management_scenario["manure_handler"]
            manure_separator = manure_management_scenario["manure_separator"]
            manure_separator_after_digestion = manure_management_scenario["manure_separator_after_digestion"]
            manure_storage = manure_management_scenario["manure_treatment"]

            pen = Pen(
                pen_id=pen_id,
                pen_name=pen_name,
                vertical_dist_to_milking_parlor=vertical_dist_to_milking_parlor,
                horizontal_dist_to_milking_parlor=horizontal_dist_to_milking_parlor,
                number_of_stalls=number_of_stalls,
                housing_type=housing_type,
                pen_type=pen_type,
                max_stocking_density=max_stocking_density,
                animal_combination=animal_combination,
                bedding_type=bedding_type,
                manure_handling=manure_handling,
                manure_separator=manure_separator,
                manure_separator_after_digestion=manure_separator_after_digestion,
                manure_storage=manure_storage,
            )

            self.all_pens.append(pen)

    def allocate_animals_to_pens(self) -> None:
        """
        Allocate animals to pens based on the current animal population and the number of pens available.
        New default pens will be created if necessary. This method distributes the animals among the pens,
        ensuring that the animal density of each pen matches the overall density as closely as possible.

        """

        self._sort_cows_before_allocation()

        for animal_combination, animals in self.animals_by_combination.items():
            animal_space_shortage = self._calculate_animal_space_shortage(
                num_animals=len(animals), pens=self.pens_by_animal_combination[animal_combination]
            )
            if animal_space_shortage > 0:
                new_default_pens = self._create_additional_pens(
                    pens=self.pens_by_animal_combination[animal_combination],
                    animal_combination=animal_combination,
                    start_pen_id=len(self.all_pens),
                    animal_space_shortage=animal_space_shortage,
                )
                self.all_pens.extend(new_default_pens)
            self._allocate_animals_to_pens_helper(animals, self.pens_by_animal_combination[animal_combination])

        self.fully_update_animal_to_pen_id_map()

    def _plan_animal_allocation(self, num_animals: int, max_spaces_in_pens: list[int]) -> list[int]:
        """
        Make an allocation plan to move animals to pens and match pen density as closely as possible
         to the overall density.

        General rules:
        1. The number of animals allocated to each pen cannot exceed the maximum number of spaces available in that pen.
        2. The total number of animals allocated to all pens must be equal to num_animals.
        3. The density in each pen must be as close as possible to the overall density.
        4. Generally, it is expected that the density in each pen will be slightly greater than or equal to
        the overall density, except the last pen.
        5. The last pen considered by the algorithm is the pen with the highest allocation limit.
        6. That last pen will hold the remaining animals, likely resulting in a density that is lower than
            the overall density.

        Notes
        -----
        The overall density is calculated as the ratio of the total number of animals to the total number of spaces.
        The allocation limit of a pen `math.ceil(overall_density * max_spaces_in_pens[i])`.
        It is the smallest integer greater than or equal to the overall density multiplied by the maximum number of
        spaces in that pen.
        This ensures that the individual pen density will be the same as the overall density or only slightly higher
        due to the addition of exactly one extra animal.

        Here, allocating animals to the pens with the higher allocation limits last gives a more even density
        distribution across all pens, because those with lower allocation limits will get filled first
        and won't be ignored.

        An alternative approach would be to allocate animals to the pens with the higher allocation limits first.
        This would use up the animal count more quickly, so the later the allocation, the fewer animals are left
        to allocate. Depending on the dynamics between the given numbers, some pens may end up with a very low density.

        Parameters
        ----------
        num_animals : int
            The total number of animals to allocate. Must be a non-negative integer and not be greater than the
            total number of spaces.
        max_spaces_in_pens : List[int]
            A list of integers representing the number of maximum spaces in each pen. Each integer must be positive.

        Returns
        -------
        List[int]
            A list of integers representing the allocation of animals in each pen. Each integer will be less than or
            equal to `math.ceil(overall_density * max_spaces_in_pens[i])]`.

        Raises
        ------
        ValueError
            If the number of animals is greater than the total number of spaces.

        Examples
        --------
        >>> HerdManager._plan_animal_allocation(num_animals=90, max_spaces_in_pens=[50, 30, 20])
        [45, 27, 18]

        >>> HerdManager._plan_animal_allocation(num_animals=70, max_spaces_in_pens=[50, 30, 20])
        [35, 21, 14]

        >>> HerdManager._plan_animal_allocation(num_animals=47, max_spaces_in_pens=[50, 30, 20])
        [22, 15, 10]

        """
        num_pens_for_combination = len(max_spaces_in_pens)
        overall_density = self._calculate_density(num_animals=num_animals, num_spaces=sum(max_spaces_in_pens))

        if overall_density > 1.0:
            raise ValueError("The number of animals cannot exceed the total number of spaces.")

        num_animals_in_pens = [0] * num_pens_for_combination
        allocation_limits = [math.ceil(overall_density * max_spaces) for max_spaces in max_spaces_in_pens]

        sorted_pen_indices = sorted(
            range(num_pens_for_combination),
            key=lambda pen_idx: (allocation_limits[pen_idx], pen_idx),
        )

        for i in sorted_pen_indices[: num_pens_for_combination - 1]:
            num_animals_to_allocate = min(num_animals, allocation_limits[i])
            num_animals_in_pens[i] = num_animals_to_allocate
            num_animals -= num_animals_to_allocate
        num_animals_in_pens[sorted_pen_indices[-1]] += num_animals

        return num_animals_in_pens

    def _execute_allocation_plan(
        self,
        allocation_plan: list[int],
        animals: list[Animal],
        animal_pens: list[Pen],
    ) -> None:
        """
        Execute an allocation plan to distribute animals into pens according to the given plan.

        This method iterates over the provided allocation plan and updates each pen with the specified number
        of animals.

        Parameters
        ----------
        allocation_plan : list[int]
            A list of integers representing the number of animals to be allocated to each pen.
            The length of the allocation_plan list must match the number of pens in animal_pens.
        animals : list[Animal]
            A list of animals to be allocated among the pens.
        animal_pens : list[Pen]
            A list of Pen objects representing the pens to which animals will be allocated.

        Raises
        ------
        ValueError
            If the length of the allocation plan does not match the number of pens.
            If the sum of the allocation plan does not match the number of animals.

        """

        if len(allocation_plan) != len(animal_pens):
            raise ValueError("The length of the allocation plan must match the number of pens.")
        elif sum(allocation_plan) != len(animals):
            raise ValueError("The sum of the allocation plan must match the number of animals.")

        for i, count in enumerate(allocation_plan):
            animal_pens[i].insert_animals_into_animals_in_pen_map(animals[:count])
            animals = animals[count:]

    def _sort_cows_before_allocation(self) -> None:
        """Sort cows by days_in_milk in increasing order."""
        self.cows = list(filter(lambda cow: not cow.is_milking, self.cows)) + sorted(
            list(filter(lambda cow: cow.is_milking, self.cows)), key=lambda cow: cow.days_in_milk
        )

    def _create_additional_pens(
        self,
        pens: list[Pen],
        animal_combination: AnimalCombination,
        animal_space_shortage: int,
        start_pen_id: int = 0,
    ) -> list[Pen]:
        """
        Create a list of additional pens to accommodate potential animal space shortage.

        This method defines the first pen in the pens list as the 'reference' pen, which means that it uses those
        attributes as a template for the creation of new pens. This assumes the incoming pen list is uniform, as they
        are the same AnimalCombination.

        Parameters
        ----------
        pens : List[Pen]
            A list of Pen objects representing the currently available pens.
        animal_combination : AnimalCombination
            The animal combination for the new default pens.
        start_pen_id : int, default=0
            The starting pen ID for the new pens.

        Returns
        -------
        List[Pen]
            A list of new default Pen objects to accommodate the potential animal space shortage.

        """
        additional_pens: list[Pen] = []

        reference_pen = pens[0]
        max_stocking_density = reference_pen.max_stocking_density
        num_stalls_custom_pen = int(math.ceil(animal_space_shortage * max_stocking_density))
        num_stalls_per_additional_pen = min(
            self.DEFAULT_NUM_STALLS_BY_COMBINATION[animal_combination], num_stalls_custom_pen
        )

        max_animal_spaces_per_additional_pen = self._calculate_max_animal_spaces_per_pen(
            num_stalls=num_stalls_per_additional_pen, max_stocking_density=max_stocking_density
        )
        num_new_pens = math.ceil(animal_space_shortage / max_animal_spaces_per_additional_pen)
        for i in range(num_new_pens):
            new_pen_id = start_pen_id + i
            additional_pens.append(
                Pen(
                    pen_id=new_pen_id,
                    pen_name=str(new_pen_id),
                    vertical_dist_to_milking_parlor=reference_pen.vertical_dist_to_parlor,
                    horizontal_dist_to_milking_parlor=reference_pen.horizontal_dist_to_parlor,
                    number_of_stalls=num_stalls_per_additional_pen,
                    housing_type=reference_pen.housing_type,
                    bedding_type=reference_pen.bedding_type,
                    pen_type=reference_pen.pen_type,
                    manure_handling=reference_pen.manure_handling,
                    manure_separator=reference_pen.manure_separator,
                    manure_separator_after_digestion=reference_pen.manure_separator_after_digestion,
                    manure_storage=reference_pen.manure_storage,
                    animal_combination=animal_combination,
                    max_stocking_density=max_stocking_density,
                )
            )

        return additional_pens

    def _calculate_max_animal_spaces_per_pen(self, num_stalls: int, max_stocking_density: float) -> int:
        """
        Calculate the maximum number of animal spaces available per pen.

        Parameters
        ----------
        num_stalls : int
            The number of stalls in the pen. Must be greater than or equal to 0.
        max_stocking_density : float
            The maximum stocking density for the pen. Must be greater than or equal to 0.

        Returns
        -------
        int
            The maximum number of animal spaces available in the pen.

        Raises
        ------
        ValueError
            If the number of stalls or maximum stocking density is less than 0.

        Examples
        --------
        >>> HerdManager._calculate_max_animal_spaces_per_pen(num_stalls=10, max_stocking_density=1.5)
        15
        >>> HerdManager._calculate_max_animal_spaces_per_pen(num_stalls=5, max_stocking_density=2.0)
        10

        """

        if num_stalls < 0 or max_stocking_density < 0:
            raise ValueError("The number of stalls and maximum stocking density must be greater than or equal to 0.")

        return int(num_stalls * max_stocking_density)

    def _calculate_animal_space_shortage(self, num_animals: int, pens: list[Pen]) -> int:
        """
        Calculate the shortage of animal spaces given the number of animals and a list of pens.

        Parameters
        ----------
        num_animals : int
            The total number of animals to be accommodated.
        pens : List[Pen]
            A list of Pen objects representing the available pens.

        Returns
        -------
        int
            The shortage of animal spaces. If there is a shortage, this will be a positive integer.

        """
        max_animal_spaces = 0
        for pen in pens:
            max_animal_spaces += self._calculate_max_animal_spaces_per_pen(pen.num_stalls, pen.max_stocking_density)
        return num_animals - max_animal_spaces

    def _calculate_density(self, num_animals: int, num_spaces: int) -> float:
        """
        Calculate the animal density in pens given the number of animals and spaces.

        Parameters
        ----------
        num_animals : int
            The number of animals in the pen. Must be a non-negative integer.
        num_spaces : int
            The number of spaces in the pen to hold the animals. Must be a positive integer.

        Returns
        -------
        float
            The animal density, calculated as the ratio of the number of animals to the number of spaces available.

        Raises
        ------
        ValueError
            If num_animals is negative.
            IF num_spaces is non-positive.

        Notes
        -----
        This method does not raise an error if the number of animals is greater than the number of spaces.
        Instead, it returns a density greater than 1.0.

        """

        if num_animals < 0:
            raise ValueError("num_animals must be a non-negative integer")

        if num_spaces <= 0:
            raise ValueError("num_spaces must be a positive integer")

        return num_animals / num_spaces

    def _allocate_animals_to_pens_helper(self, animals: list[Animal], pens: list[Pen]) -> None:
        """
        Allocate animals to pens based on overall density while preventing overcrowding.

        This method distributes the animals among the available pens, ensuring that the density
        in each pen matches the overall density as closely as possible.

        Parameters
        ----------
        animals : List[Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]]
            A list of animal to be allocated to pens.
        pens : List[Pen]
            A list of Pen objects representing the available pens. All these pens should have
            the same animal combination.

        """
        allocation_plan = self._plan_animal_allocation(
            num_animals=len(animals),
            max_spaces_in_pens=[
                self._calculate_max_animal_spaces_per_pen(pen.num_stalls, pen.max_stocking_density) for pen in pens
            ],
        )

        self._execute_allocation_plan(allocation_plan=allocation_plan, animals=animals, animal_pens=pens)

    def fully_update_animal_to_pen_id_map(self) -> None:
        """
        Updates the entire animal_to_pen_id_map dictionary so that each animal's ID is
        associated with the pen that animal is in.

        """
        for pen in self.all_pens:
            animals_in_pen = pen.animals_in_pen
            for animal_id in animals_in_pen:
                self.animal_to_pen_id_map[animal_id] = pen.id

    def _gather_pen_history(self, animal_type_list: list[Animal], simulation_day: int) -> None:
        """
        Updates pen history data for a given animal type.

        Checks the current pen ID and pen composition of all animals for a given animal class, and then updates the
        pen history for that type using the update_pen_history() method.

        Parameters
        ----------
        animal_type_list : List[Animal]
            List of animals.
        simulation_day : int
            The current simulation day.

        """
        animal_classes_in_pen_by_pen_id = {pen.id: pen.animal_types_in_pen for pen in self.all_pens}

        for animal in animal_type_list:
            current_pen_id = self.animal_to_pen_id_map[animal.id]
            classes_in_pen = animal_classes_in_pen_by_pen_id[current_pen_id]
            animal.update_pen_history(current_pen_id, simulation_day, classes_in_pen)

    def record_pen_history(self, simulation_day: int) -> None:
        """
        Records the pen history of all the animals.

        Parameters
        ----------
        simulation_day : int
            The current simulation day.

        """
        self._gather_pen_history(self.calves, simulation_day)
        self._gather_pen_history(self.heiferIs, simulation_day)
        self._gather_pen_history(self.heiferIIs, simulation_day)
        self._gather_pen_history(self.heiferIIIs, simulation_day)
        self._gather_pen_history(self.cows, simulation_day)

    def clear_pens(self) -> None:
        """
        Removes animals from pens for re-allocation. This is part of the
        routines that happen every ration interval.

        """

        for pen in self.all_pens:
            pen.clear()

    def end_ration_interval(self, simulation_day: int) -> bool:
        """
        Checks if a new ration should be formulated for the current simulation_day.

        Returns
        -------
        bool
            True if today is the day a new ration has to be formulated,
            False otherwise.

        """
        return simulation_day % self.formulation_interval == 1 or self.formulation_interval == 1 or simulation_day == 0

    def set_milk_type_in_calf_ration_manager(self) -> None:
        """
        Sets the milk type of calves to be either whole or replacement depending on the diet configured by the user.

        """
        calf_ration = UserDefinedRationManager.user_defined_rations[AnimalCombination.CALF]

        if WHOLE_MILK_ID in calf_ration.keys():
            milk_type = CalfMilkType.WHOLE
        else:
            milk_type = CalfMilkType.REPLACER

        CalfRationManager.set_milk_type(milk_type)

        info_map = {
            "class": self.__class__.__name__,
            "function": self.set_milk_type_in_calf_ration_manager.__name__,
            "milk_type": milk_type.value,
            "calf_ration": calf_ration,
        }
        self.om.add_log(
            "Milk type set for calf ration",
            f"Calf requirements routines will assume 100% of calves' milk intake is {milk_type.value}",
            info_map,
        )

    def initialize_nutrient_requirements(self, weather: Weather, time: Time, available_feeds: list[Feed]) -> None:
        """
        Calculates initial nutrient requirements at the beginning of the simulation for initial pen allocation.

        Parameters
        ----------
        weather : Weather
            instance of the Weather class
        time : Time
            instance of the Time class
        available_feeds : list[Feed]
            Nutrition information of feeds available to formulate animals rations with.

        """
        for pen in self.all_pens:
            pen.set_animal_nutritional_requirements(
                weather.get_current_day_conditions(time).mean_air_temperature, available_feeds
            )

    def update_all_max_daily_feeds(
        self, total_inventory: TotalInventory, next_harvest_dates: dict[RUFAS_ID, date], time: Time
    ) -> IdealFeeds:
        """
        Updates the max feeds of all available feeds types based on the current total inventory.

        Parameters
        ----------
        total_inventory : TotalInventory
            The total inventory of all available feeds.
        next_harvest_dates : Dict[RUFAS_ID, date]
            The next harvest date for each applicable feed type.
        time : Time
            Time object.

        Returns
        -------
        IdealFeeds
            The maximum daily feeds for each feed type.

        """
        for rufas_id in next_harvest_dates.keys():
            self._update_single_max_daily_feed(rufas_id, next_harvest_dates[rufas_id], total_inventory, time)

        # TODO: calculate feeds that would ideally be purchased before next harvests based on "herd needs"
        return IdealFeeds({})

    def _update_single_max_daily_feed(
        self, rufas_id: RUFAS_ID, next_harvest: date, total_inventory: TotalInventory, time: Time
    ) -> None:
        """
        Updates a single max daily feed based on the current amount available, number of animals, and next harvest date.

        Parameters
        ----------
        rufas_id : RUFAS_ID
            The RuFaS Feed ID of the max daily feed to be updated.
        next_harvest : date
            When next harvest of the given RuFaS feed will be.
        total_inventory : TotalInventory
            Total amounts of feeds in inventory.
        time : Time
            Time object.

        """
        total_animal_population = len(self.animal_to_pen_id_map.keys())
        days_until_next_harvest = (next_harvest - time.current_date.date()).days

        self._max_daily_feeds[rufas_id] = (
            total_inventory.available_feeds.get(rufas_id, 0.0) / total_animal_population / days_until_next_harvest
        )

    def formulate_rations(
        self,
        available_feeds: list[Feed],
        current_temperature: float,
        ration_interval_length: int,
        total_inventory: TotalInventory,
    ) -> RequestedFeed:
        """
        Formulates rations for all pens.

        Parameters
        ----------
        available_feeds : List[Feed]
            List of available feeds.
        current_temperature : float
            Current temperature (C).
        ration_interval_length : int
            Length of the ration interval (days).
        total_inventory : TotalInventory
            The total inventory of all available feeds.

        Returns
        -------
        RequestedFeed
            Feeds requested to be purchased for the newly formulated rations.

        """
        self.clear_pens()
        self.allocate_animals_to_pens()

        total_requested_feed = RequestedFeed({})
        for pen in self.all_pens:
            self._reformulate_ration_single_pen(pen, available_feeds, current_temperature, total_inventory)
            total_requested_feed += pen.get_requested_feed(ration_interval_length)
        return total_requested_feed

    def _reformulate_ration_single_pen(
        self, pen: Pen, available_feeds: list[Feed], current_temperature: float, total_inventory: TotalInventory
    ) -> None:
        """
        Reformulates ration for a single pen.

        Parameters
        ----------
        pen : Pen
            Pen that requires ration reformulation.
        available_feeds : List[Feed]
            List of available feeds.
        current_temperature : float
            Current temperature (C).
        total_inventory : TotalInventory
            Inventory currently available or projected to be available at a future date.

        """
        if self.is_ration_defined_by_user is True:
            pen.use_user_defined_ration(available_feeds, current_temperature)
        else:
            pen.formulate_optimized_ration(
                available_feeds, self._max_daily_feeds, self.advance_purchase_allowance, total_inventory
            )

    def update_herd_statistics(self) -> None:
        """Calculates and updates herd statistics."""
        (
            self.herd_statistics.calf_num,
            self.herd_statistics.heiferI_num,
            self.herd_statistics.heiferII_num,
            self.herd_statistics.heiferIII_num,
            self.herd_statistics.cow_num,
        ) = (len(self.calves), len(self.heiferIs), len(self.heiferIIs), len(self.heiferIIIs), len(self.cows))
        self._calculate_herd_percentages()

        self._update_heifer_reproduction_statistics()

        self._update_cow_reproduction_statistics()
        self._update_cow_milking_statistics()
        self._update_cow_pregnancy_statistics()
        self._update_cow_parity_statistics()
        self._calculate_cow_percentages()

        self._update_average_mature_body_weight()
        self._update_average_cow_body_weight()
        self._update_average_cow_parity()

    def _calculate_herd_percentages(self) -> None:
        """Calculates and updates the herd percentages for different animal types."""
        denominator = sum(
            [len(self.calves), len(self.heiferIs), len(self.heiferIIs), len(self.heiferIIIs), len(self.cows)]
        )
        denominator = denominator if denominator > 0 else 1
        pc = Utility.percent_calculator(denominator)
        self.herd_statistics.calf_percent = pc(self.herd_statistics.calf_num)
        self.herd_statistics.heiferI_percent = pc(self.herd_statistics.heiferI_num)
        self.herd_statistics.heiferII_percent = pc(self.herd_statistics.heiferII_num)
        self.herd_statistics.heiferIII_percent = pc(self.herd_statistics.heiferIII_num)
        self.herd_statistics.cow_percent = pc(self.herd_statistics.cow_num)

    def _calculate_cow_percentages(self) -> None:
        """
        Calculates percentages of various cow categories within the herd and updates
        the corresponding attributes of the `herd_statistics` object.

        """
        denominator = self.herd_statistics.cow_num if self.herd_statistics.cow_num > 0 else 1
        pc = Utility.percent_calculator(denominator)
        self.herd_statistics.dry_cow_percent = pc(self.herd_statistics.dry_cow_num)
        self.herd_statistics.milking_cow_percent = pc(self.herd_statistics.milking_cow_num)
        self.herd_statistics.preg_cow_percent = pc(self.herd_statistics.preg_cow_num)
        self.herd_statistics.non_preg_cow_percent = pc(self.herd_statistics.open_cow_num)

    def _calculate_cull_reason_percentages(self) -> None:
        """Calculates the percentage distribution for each culling reason in the herd statistics."""
        denominator = self.herd_statistics.cow_herd_exit_num if self.herd_statistics.cow_herd_exit_num > 0 else 1
        pc = Utility.percent_calculator(denominator)
        for cull_reason in self.herd_statistics.cull_reason_stats:
            self.herd_statistics.cull_reason_stats_percent[cull_reason] = pc(
                self.herd_statistics.cull_reason_stats[cull_reason]
            )

    def _update_cow_parity_statistics(self) -> None:
        """
        Updates statistics related to the parity of cows in the herd.

        Parity-related statistics include:
            - the number of cows for each parity level
            - the average age of cows at different parities
            - the average calving age for each parity
            - the average time between calving and subsequent pregnancy
        This method also calculates the percentage distribution of cows across parity levels relative to the herd
        population. All computed statistics are stored in the `herd_statistics` attribute of the class.

        """
        denominator = self.herd_statistics.cow_num if self.herd_statistics.cow_num > 0 else 1
        parity_1_cows = [cow for cow in self.cows if cow.reproduction.calves == 1]
        parity_2_cows = [cow for cow in self.cows if cow.reproduction.calves == 2]
        parity_3_cows = [cow for cow in self.cows if cow.reproduction.calves == 3]
        parity_greater_than_3_cows = [cow for cow in self.cows if cow.reproduction.calves > 3]
        self.herd_statistics.num_cow_for_parity = {
            "1": len(parity_1_cows),
            "2": len(parity_2_cows),
            "3": len(parity_3_cows),
            "greater_than_3": len(parity_greater_than_3_cows),
        }
        self.herd_statistics.avg_age_for_parity = {
            "1": sum([cow.days_born for cow in parity_1_cows]) / len(parity_1_cows) if len(parity_1_cows) > 0 else 0,
            "2": sum([cow.days_born for cow in parity_2_cows]) / len(parity_2_cows) if len(parity_2_cows) > 0 else 0,
            "3": sum([cow.days_born for cow in parity_3_cows]) / len(parity_3_cows) if len(parity_3_cows) > 0 else 0,
            "greater_than_3": (
                sum([cow.days_born for cow in parity_greater_than_3_cows]) / len(parity_greater_than_3_cows)
                if len(parity_greater_than_3_cows) > 0
                else 0
            ),
        }

        parity_1_calving_age = [cow.events.get_most_recent_date(animal_constants.NEW_BIRTH) for cow in parity_1_cows]
        parity_2_calving_age = [cow.events.get_most_recent_date(animal_constants.NEW_BIRTH) for cow in parity_2_cows]
        parity_3_calving_age = [cow.events.get_most_recent_date(animal_constants.NEW_BIRTH) for cow in parity_3_cows]
        parity_greater_than_3_calving_age = [
            cow.events.get_most_recent_date(animal_constants.NEW_BIRTH) for cow in parity_greater_than_3_cows
        ]

        parity_1_calving_age = [calving_age for calving_age in parity_1_calving_age if calving_age > 0]
        parity_2_calving_age = [calving_age for calving_age in parity_2_calving_age if calving_age > 0]
        parity_3_calving_age = [calving_age for calving_age in parity_3_calving_age if calving_age > 0]
        parity_greater_than_3_calving_age = [
            calving_age for calving_age in parity_greater_than_3_calving_age if calving_age > 0
        ]
        self.herd_statistics.avg_age_for_calving = {
            "1": (sum(parity_1_calving_age) / len(parity_1_calving_age)) if len(parity_1_calving_age) > 0 else 0,
            "2": (sum(parity_2_calving_age) / len(parity_2_calving_age)) if len(parity_2_calving_age) > 0 else 0,
            "3": (sum(parity_3_calving_age) / len(parity_3_calving_age)) if len(parity_3_calving_age) > 0 else 0,
            "greater_than_3": (
                (sum(parity_greater_than_3_calving_age) / len(parity_greater_than_3_calving_age))
                if len(parity_greater_than_3_calving_age) > 0
                else 0
            ),
        }

        parity_1_calving_to_pregnancy_time = [
            cow.reproduction.reproduction_statistics.calving_to_pregnancy_time for cow in parity_1_cows
        ]
        parity_2_calving_to_pregnancy_time = [
            cow.reproduction.reproduction_statistics.calving_to_pregnancy_time for cow in parity_2_cows
        ]
        parity_3_calving_to_pregnancy_time = [
            cow.reproduction.reproduction_statistics.calving_to_pregnancy_time for cow in parity_3_cows
        ]
        parity_greater_than_3_calving_to_pregnancy_time = [
            cow.reproduction.reproduction_statistics.calving_to_pregnancy_time for cow in parity_greater_than_3_cows
        ]

        parity_1_calving_to_pregnancy_time = [
            calving_to_pregnancy_time
            for calving_to_pregnancy_time in parity_1_calving_to_pregnancy_time
            if calving_to_pregnancy_time > 0
        ]
        parity_2_calving_to_pregnancy_time = [
            calving_to_pregnancy_time
            for calving_to_pregnancy_time in parity_2_calving_to_pregnancy_time
            if calving_to_pregnancy_time > 0
        ]
        parity_3_calving_to_pregnancy_time = [
            calving_to_pregnancy_time
            for calving_to_pregnancy_time in parity_3_calving_to_pregnancy_time
            if calving_to_pregnancy_time > 0
        ]
        parity_greater_than_3_calving_to_pregnancy_time = [
            calving_to_pregnancy_time
            for calving_to_pregnancy_time in parity_greater_than_3_calving_to_pregnancy_time
            if calving_to_pregnancy_time > 0
        ]
        self.herd_statistics.avg_calving_to_preg_time = {
            "1": (
                (sum(parity_1_calving_to_pregnancy_time) / len(parity_1_calving_to_pregnancy_time))
                if len(parity_1_calving_to_pregnancy_time) > 0
                else 0
            ),
            "2": (
                (sum(parity_2_calving_to_pregnancy_time) / len(parity_2_calving_to_pregnancy_time))
                if len(parity_2_calving_to_pregnancy_time) > 0
                else 0
            ),
            "3": (
                (sum(parity_3_calving_to_pregnancy_time) / len(parity_3_calving_to_pregnancy_time))
                if len(parity_3_calving_to_pregnancy_time) > 0
                else 0
            ),
            "greater_than_3": (
                (
                    sum(parity_greater_than_3_calving_to_pregnancy_time)
                    / len(parity_greater_than_3_calving_to_pregnancy_time)
                )
                if len(parity_greater_than_3_calving_to_pregnancy_time) > 0
                else 0
            ),
        }

        pc = Utility.percent_calculator(denominator)
        for parity in self.herd_statistics.num_cow_for_parity:
            self.herd_statistics.percent_cow_for_parity[parity] = pc(self.herd_statistics.num_cow_for_parity[parity])

    def _update_cow_milking_statistics(self) -> None:
        """
        Updates the herd's milking statistics.

        This method performs calculations for both lactating and dry cows and updates the `herd_statistics`.
        The metrics include:
            - average days in milk
            - daily milk production
            - milk fat content
            - milk protein content
            - voluntary waiting period statistics.

        Raises
        ------
        ValueError
            If any milk production, fat content, or protein content is detected
            from dry cows. An error entry is also added to the error log with
            details on the issue.

        """
        info_map = {
            "class": HerdManager.__class__.__name__,
            "function": HerdManager._update_cow_milking_statistics.__name__,
        }
        lactating_cows: list[Animal] = [cow for cow in self.cows if cow.is_milking]
        dry_cows: list[Animal] = [cow for cow in self.cows if not cow.is_milking]
        vwp_cows: list[Animal] = [cow for cow in self.cows if cow.days_in_milk < AnimalConfig.voluntary_waiting_period]
        self.herd_statistics.milking_cow_num = len(lactating_cows)
        self.herd_statistics.dry_cow_num = len(dry_cows)
        self.herd_statistics.vwp_cow_num = len(vwp_cows)

        self.herd_statistics.avg_days_in_milk = (
            (sum([cow.days_in_milk for cow in lactating_cows]) / len(lactating_cows)) if len(lactating_cows) > 0 else 0
        )

        self.herd_statistics.daily_milk_production = sum([cow.milk_production.daily_milk_produced for cow in self.cows])
        self.herd_statistics.herd_milk_fat_kg = sum([cow.milk_production.fat_content for cow in lactating_cows])
        self.herd_statistics.herd_milk_fat_percent = (
            (self.herd_statistics.herd_milk_fat_kg / self.herd_statistics.daily_milk_production) * 100
            if self.herd_statistics.daily_milk_production > 0
            else 0
        )
        self.herd_statistics.herd_milk_protein_kg = sum(
            cow.milk_production.true_protein_content for cow in lactating_cows
        )
        self.herd_statistics.herd_milk_protein_percent = (
            (self.herd_statistics.herd_milk_protein_kg / self.herd_statistics.daily_milk_production) * 100
            if self.herd_statistics.daily_milk_production > 0
            else 0
        )

        dry_cows_daily_milk_production = sum([cow.milk_production.daily_milk_produced for cow in dry_cows])
        dry_cows_milk_fat_kg = sum([cow.milk_production.fat_content for cow in dry_cows])
        dry_cows_milk_protein_kg = sum([cow.milk_production.true_protein_content for cow in dry_cows])
        if dry_cows_daily_milk_production > 0 or dry_cows_milk_fat_kg > 0 or dry_cows_milk_protein_kg > 0:
            self.om.add_error("Dry cow milking error", "Unexpected milking from dry cows", info_map)
            raise ValueError("Unexpected milking from dry cows")

    def _update_cow_pregnancy_statistics(self) -> None:
        """
        Updates the pregnancy statistics for the cows in the herd.

        This method calculates and updates the statistics related to pregnant cows, open (non-pregnant)
        cows, and the average number of days in pregnancy.

        """
        pregnant_cows: list[Animal] = [cow for cow in self.cows if cow.is_pregnant]
        self.herd_statistics.preg_cow_num = len(pregnant_cows)
        self.herd_statistics.open_cow_num = len(self.cows) - len(pregnant_cows)

        self.herd_statistics.avg_days_in_preg = (
            (sum([cow.days_in_pregnancy for cow in pregnant_cows]) / len(pregnant_cows))
            if len(pregnant_cows) > 0
            else 0
        )

    def _update_sold_and_died_cow_statistics(self, sold_and_died_cows: list[Animal]) -> None:
        """
        Updates the herd statistics with details of cows that are sold or have died.
        This method records the culling age, updates statistics related to culled cows, and categorizes
        the cows based on specific attributes such as cull reason and parity.

        Parameters
        ----------
        sold_and_died_cows : list[Animal]
            A list of cows that were either sold or died.

        """
        sum_cow_culling_age = self.herd_statistics.avg_cow_culling_age * self.herd_statistics.cow_herd_exit_num + sum(
            [cow.days_born for cow in sold_and_died_cows]
        )
        self.herd_statistics.cow_herd_exit_num += len(sold_and_died_cows)
        self.herd_statistics.avg_cow_culling_age = (
            (sum_cow_culling_age / self.herd_statistics.cow_herd_exit_num)
            if self.herd_statistics.cow_herd_exit_num > 0
            else 0
        )

        self.herd_statistics.sold_and_died_cows_info += [
            SoldAnimalTypedDict(
                id=cow.id,
                animal_type=cow.animal_type.value,
                sold_at_day=cow.sold_at_day if cow.sold_at_day is not None else cow.dead_at_day,
                body_weight=cow.body_weight,
                cull_reason=cow.cull_reason,
                days_in_milk=cow.days_in_milk,
                parity=cow.reproduction.calves,
            )
            for cow in sold_and_died_cows
        ]
        for cull_reason in self.herd_statistics.cull_reason_stats.keys():
            self.herd_statistics.cull_reason_stats[cull_reason] += len(
                [cow for cow in sold_and_died_cows if cow.cull_reason == cull_reason]
            )

        sold_cows: list[Animal] = [cow for cow in sold_and_died_cows if cow.cull_reason != animal_constants.DEATH_CULL]
        self.herd_statistics.sold_cows_info += [
            SoldAnimalTypedDict(
                id=cow.id,
                animal_type=cow.animal_type.value,
                sold_at_day=cow.sold_at_day,
                body_weight=cow.body_weight,
                cull_reason=cow.cull_reason,
                days_in_milk=cow.days_in_milk,
                parity=cow.reproduction.calves,
            )
            for cow in sold_cows
        ]
        self.herd_statistics.sold_cow_num += len(sold_cows)

        for parity in self.herd_statistics.parity_culling_stats_range.keys():
            if parity == "greater_than_3":
                culled_cows_with_current_parity = [cow for cow in sold_and_died_cows if cow.reproduction.calves > 3]
            else:
                current_parity = int(parity)
                culled_cows_with_current_parity = [
                    cow for cow in sold_and_died_cows if cow.reproduction.calves == current_parity
                ]
            self.herd_statistics.parity_culling_stats_range[parity] += len(culled_cows_with_current_parity)
        self._calculate_cull_reason_percentages()

    def _update_sold_heiferII_statistics(self, sold_heiferIIs: list[Animal]) -> None:
        """
        Updates sold heiferII statistics in the herd statistics.

        This method updates the herd's statistical values relating to sold heiferIIs.
        The updates include incrementing the number of sold heiferIIs, appending details
        about each sold heiferII, and calculating the average heiferII culling age.

        Parameters
        ----------
        sold_heiferIIs : list[Animal]
            A list of heiferII animals that have been sold.

        """
        sum_heifer_culling_age = (
            self.herd_statistics.avg_heifer_culling_age * self.herd_statistics.sold_heiferII_num
        ) + sum([heiferII.days_born for heiferII in sold_heiferIIs])

        self.herd_statistics.sold_heiferII_num += len(sold_heiferIIs)
        self.herd_statistics.sold_heiferIIs_info += [
            SoldAnimalTypedDict(
                id=heiferII.id,
                animal_type=heiferII.animal_type.value,
                sold_at_day=heiferII.sold_at_day,
                body_weight=heiferII.body_weight,
                cull_reason="NA",
                days_in_milk="NA",
                parity="NA",
            )
            for heiferII in sold_heiferIIs
        ]
        self.herd_statistics.avg_heifer_culling_age = (
            (sum_heifer_culling_age / self.herd_statistics.sold_heiferII_num)
            if self.herd_statistics.sold_heiferII_num > 0
            else 0
        )

    def _update_sold_newborn_calf_statistics(self, sold_newborn_calves: list[Animal]) -> None:
        """
        Updates the statistics of sold newborn calves in the herd statistics.
        It increments the count of sold calves and appends detailed information about each sold newborn
        calf to the corresponding statistics.

        Parameters
        ----------
        sold_newborn_calves : list[Animal]
            A list of newborn calves that were sold.

        """
        self.herd_statistics.sold_calf_num += len(sold_newborn_calves)
        self.herd_statistics.sold_calves_info += [
            SoldAnimalTypedDict(
                id=calf.id,
                animal_type=calf.animal_type.value,
                sold_at_day=calf.sold_at_day,
                body_weight=calf.body_weight,
                cull_reason="NA",
                days_in_milk="NA",
                parity="NA",
            )
            for calf in sold_newborn_calves
        ]

    def _update_cow_reproduction_statistics(self) -> None:
        """Updates the reproduction statistics of cows in the herd."""
        self.herd_statistics.GnRH_injection_num = sum(
            [cow.reproduction.reproduction_statistics.GnRH_injections for cow in self.cows]
        )
        self.herd_statistics.PGF_injection_num = sum(
            [cow.reproduction.reproduction_statistics.PGF_injections for cow in self.cows]
        )
        self.herd_statistics.CIDR_count = sum(
            [cow.reproduction.reproduction_statistics.CIDR_injections for cow in self.cows]
        )
        self.herd_statistics.preg_check_num = sum(
            [cow.reproduction.reproduction_statistics.pregnancy_diagnoses for cow in self.cows]
        )
        self.herd_statistics.semen_num = sum(
            [cow.reproduction.reproduction_statistics.semen_number for cow in self.cows]
        )
        self.herd_statistics.ai_num = sum([cow.reproduction.reproduction_statistics.AI_times for cow in self.cows])
        self.herd_statistics.ed_period = len(
            [cow for cow in self.cows if cow.reproduction.reproduction_statistics.ED_days > 0]
        )
        self.herd_statistics.avg_calving_interval = (
            sum([cow.reproduction.calving_interval for cow in self.cows]) / len(self.cows) if len(self.cows) > 0 else 0
        )

    def _update_heifer_reproduction_statistics(self) -> None:
        """Updates the reproduction statistics of heifers in the herd."""
        self.herd_statistics.GnRH_injection_num_h = sum(
            [heiferII.reproduction.reproduction_statistics.GnRH_injections for heiferII in self.heiferIIs]
        )
        self.herd_statistics.PGF_injection_num_h = sum(
            [heiferII.reproduction.reproduction_statistics.PGF_injections for heiferII in self.heiferIIs]
        )
        self.herd_statistics.CIDR_count = sum(
            [heiferII.reproduction.reproduction_statistics.CIDR_injections for heiferII in self.heiferIIs]
        )
        self.herd_statistics.preg_check_num_h = sum(
            [heiferII.reproduction.reproduction_statistics.pregnancy_diagnoses for heiferII in self.heiferIIs]
        )
        self.herd_statistics.semen_num_h = sum(
            [heiferII.reproduction.reproduction_statistics.semen_number for heiferII in self.heiferIIs]
        )
        self.herd_statistics.ai_num_h = sum(
            [heiferII.reproduction.reproduction_statistics.AI_times for heiferII in self.heiferIIs]
        )
        self.herd_statistics.ed_period_h = len(
            [heiferII for heiferII in self.heiferIIs if heiferII.reproduction.reproduction_statistics.ED_days > 0]
        )
        pregnant_heiferIIs = [heiferII for heiferII in self.heiferIIs if heiferII.is_pregnant]
        self.herd_statistics.avg_breeding_to_preg_time = (
            sum([heiferII.reproduction.breeding_to_preg_time for heiferII in pregnant_heiferIIs])
            / len(pregnant_heiferIIs)
            if len(pregnant_heiferIIs) > 0
            else 0
        )

    def _update_average_mature_body_weight(self) -> None:
        """Updates the average mature body weight of the animals in the herd."""
        all_animals: list[Animal] = self.calves + self.heiferIs + self.heiferIIs + self.heiferIIIs + self.cows
        self.herd_statistics.avg_mature_body_weight = (
            sum([animal.mature_body_weight for animal in all_animals]) / len(all_animals) if len(all_animals) > 0 else 0
        )

    def _update_average_cow_body_weight(self) -> None:
        """Updates the average body weight of cows in the herd."""
        self.herd_statistics.avg_cow_body_weight = (
            sum([cow.body_weight for cow in self.cows]) / len(self.cows) if len(self.cows) > 0 else 0
        )

    def _update_average_cow_parity(self) -> None:
        """Updates the average cow parity number in the herd statistics."""
        self.herd_statistics.avg_parity_num = (
            sum([cow.reproduction.calves for cow in self.cows]) / len(self.cows) if len(self.cows) > 0 else 0
        )
