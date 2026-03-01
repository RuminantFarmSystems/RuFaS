from collections import defaultdict
from datetime import date, timedelta
import math
from typing import Any

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_genetics.animal_genetics import AnimalGenetics
from RUFAS.biophysical.animal.animal_grouping_scenarios import AnimalGroupingScenario
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.biophysical.animal.data_types.animal_enums import AnimalStatus
from RUFAS.biophysical.animal.data_types.animal_events import AnimalEvents
from RUFAS.biophysical.animal.data_types.animal_population import AnimalPopulation
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import (
    NewBornCalfValuesTypedDict,
    SoldAnimalTypedDict,
    StillbornCalfTypedDict,
)
from RUFAS.biophysical.animal.data_types.herd_statistics import HerdStatistics
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.daily_routines_output import DailyRoutinesOutput
from RUFAS.biophysical.animal.data_types.milk_production import MilkProductionStatistics
from RUFAS.biophysical.animal.data_types.reproduction import HerdReproductionStatistics
from RUFAS.biophysical.animal.herd_factory import HerdFactory
from RUFAS.biophysical.animal.milk.lactation_curve import LactationCurve
from RUFAS.biophysical.animal.milk.milk_production import MilkProduction
from RUFAS.biophysical.animal.nutrients.nutrition_supply_calculator import NutritionSupplyCalculator
from RUFAS.biophysical.animal.pen import Pen
from RUFAS.biophysical.animal.ration.calf_ration_manager import CalfMilkType, CalfRationManager, WHOLE_MILK_ID
from RUFAS.biophysical.animal.ration.ration_manager import RationManager
from RUFAS.current_day_conditions import CurrentDayConditions
from RUFAS.biophysical.animal.data_types.animal_manure_excretions import AnimalManureExcretions
from RUFAS.data_structures.animal_to_manure_connection import ManureStream
from RUFAS.data_structures.feed_storage_to_animal_connection import (
    Feed,
    IdealFeeds,
    RequestedFeed,
    NutrientStandard,
    RUFAS_ID,
    TotalInventory,
    AdvancePurchaseAllowance,
)
from RUFAS.biophysical.animal.data_types.animal_combination import AnimalCombination
from RUFAS.general_constants import GeneralConstants
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime
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
        self, weather: Weather, time: RufasTime, is_ration_defined_by_user: bool, available_feeds: list[Feed]
    ) -> None:
        """
        Initializes the pens and the animal herd in the simulation with data from
        user inputs.

        Parameters
        ----------
        weather : Weather
            instance of the Weather class
        time : RufasTime
            instance of the RufasTime class
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
        ration_feed_config = self.im.get_data("feed")
        if self.is_ration_defined_by_user:
            RationManager.set_user_defined_rations(ration_feed_config)
            RationManager.set_user_defined_ration_tolerance(ration_feed_config)
        else:
            RationManager.set_ration_feeds(ration_feed_config)
        RationManager.maximum_ration_reformulation_attempts = animal_config_data["ration"][
            "maximum_ration_reformulation_attempts"
        ]
        self.set_milk_type_in_calf_ration_manager()
        self._max_daily_feeds: dict[RUFAS_ID, float] = {}

        allowances = self.im.get_data("feed.allowances")
        sorted_allowances = sorted(allowances, key=lambda x: x["purchased_feed"])
        self.advance_purchase_allowance = AdvancePurchaseAllowance(sorted_allowances)

        self.formulation_interval = animal_config_data["ration"]["formulation_interval"]
        nutrient_standard = NutrientStandard(config_data["nutrient_standard"])
        Animal.set_nutrient_standard(nutrient_standard)
        NutritionSupplyCalculator.nutrient_standard = nutrient_standard

        self.initialize_pens(animal_config_data["pen_information"])

        if self.simulate_animals:
            herd_population = HerdFactory.post_animal_population
            self.calves, self.heiferIs, self.heiferIIs, self.heiferIIIs, self.cows, self.replacement_market = (
                herd_population.calves,
                herd_population.heiferIs,
                herd_population.heiferIIs,
                herd_population.heiferIIIs,
                herd_population.cows,
                herd_population.replacement,
            )

            self.allocate_animals_to_pens(time.simulation_day)
            self.initialize_nutrient_requirements(weather, time, available_feeds)

        self._print_animal_num_warnings(animal_config_data["herd_information"])

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

    @property
    def heiferII_events_by_id(self) -> dict[str, AnimalEvents]:
        """
        Returns a dictionary that maps unique identifiers for HeiferII objects to their corresponding events.

        The unique identifier for each HeiferII object is a combination of its `animal_type.name` and `id`.

        Returns
        -------
        dict[str, AnimalEvents]
            A dictionary where each key is the unique identifier of a HeiferII,
            and the value is the string representation of the events associated with that HeiferII.

        """
        return {f"{heiferII.animal_type.name}_{heiferII.id}": heiferII.events for heiferII in self.heiferIIs}

    @property
    def cow_events_by_id(self) -> dict[str, AnimalEvents]:
        """
        Returns a dictionary that maps unique identifiers for Cow objects to their corresponding events.

        The unique identifier for each Cow object is a combination of its `animal_type.name` and `id`.

        Returns
        -------
        dict[str, AnimalEvents]
            A dictionary where each key is the unique identifier of a Cow,
            and the value is the string representation of the events associated with that Cow.

        """
        return {f"{cow.animal_type.name}_{cow.id}": cow.events for cow in self.cows}

    @property
    def daily_milk_report(self) -> list[MilkProductionStatistics]:
        """
        Returns a list of MilkProductionStatistics for all cows in the herd.

        Returns
        -------
        list[MilkProductionStatistics]
            A list of MilkProductionStatistics for all cows.

        """
        return [cow.milk_statistics for cow in self.cows]

    @property
    def average_herd_305_days_milk_production(self) -> float:
        """
        Calculates the herd average total past 305-day milk production.

        Returns
        -------
        float
            The herd mean of latest_milk_production_305days.
        """
        lactating_cow_305_days_milk_production = list(
            filter(
                lambda x: x > 0,
                [cow.milk_production.current_lactation_305_day_milk_produced for cow in self.cows if cow.is_milking],
            )
        )
        return (
            sum(lactating_cow_305_days_milk_production) / len(lactating_cow_305_days_milk_production)
            if len(lactating_cow_305_days_milk_production) > 0
            else 0.0
        )

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
            total_requested_feed += RequestedFeed(pen.ration) * len(pen.animals_in_pen)

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

    def _update_stillborn_calf_statistics(self, stillborn_calves: list[Animal]) -> None:
        """Updates the statistic regarding the stillborn calves."""
        self.herd_statistics.stillborn_calf_num += len(stillborn_calves)
        self.herd_statistics.stillborn_calf_info += [
            StillbornCalfTypedDict(id=calf.id, stillborn_day=calf.stillborn_day, birth_weight=calf.birth_weight)
            for calf in stillborn_calves
        ]

    def _update_sold_animal_statistics(
        self, sold_newborn_calves: list[Animal], sold_heiferIIs: list[Animal], sold_and_died_cows: list[Animal]
    ) -> None:
        """Call the corresponding functions to update the statistics for sold animals"""
        self._update_sold_and_died_cow_statistics(sold_and_died_cows)
        self._update_sold_heiferII_statistics(sold_heiferIIs)
        self._update_sold_newborn_calf_statistics(sold_newborn_calves)

    def _perform_daily_routines_for_animals(
        self, time: RufasTime, animals: list[Animal]
    ) -> tuple[list[Animal], list[Animal], list[Animal], list[Animal], list[Animal]]:
        """Perform daily routines for a given list of animals."""
        graduated_animals: list[Animal] = []
        sold_animals: list[Animal] = []
        stillborn_newborn_calves: list[Animal] = []
        sold_newborn_calves: list[Animal] = []
        newborn_calves: list[Animal] = []

        for animal in animals:
            animal_daily_routines_output: DailyRoutinesOutput = animal.daily_routines(time)
            self.herd_reproduction_statistics += animal_daily_routines_output.herd_reproduction_statistics
            if animal_daily_routines_output.animal_status == AnimalStatus.DEAD:
                self.herd_statistics.animals_deaths_by_stage[animal.animal_type] += 1
            if animal_daily_routines_output.animal_status == AnimalStatus.LIFE_STAGE_CHANGED:
                graduated_animals.append(animal)
                if animal_daily_routines_output.newborn_calf_config is not None:
                    newborn_calf = self._create_newborn_calf(
                        animal_daily_routines_output.newborn_calf_config, simulation_day=time.simulation_day
                    )
                    if newborn_calf.stillborn:
                        stillborn_newborn_calves.append(newborn_calf)
                    elif newborn_calf.sold:
                        sold_newborn_calves.append(newborn_calf)
                    else:
                        newborn_calves.append(newborn_calf)
            elif animal_daily_routines_output.animal_status in [AnimalStatus.DEAD, AnimalStatus.SOLD]:
                sold_animals.append(animal)
        return (graduated_animals, sold_animals, stillborn_newborn_calves, newborn_calves, sold_newborn_calves)

    def _update_herd_structure(
        self,
        graduated_animals: list[Animal],
        newborn_calves: list[Animal],
        newly_added_animals: list[Animal],
        removed_animals: list[Animal],
        available_feeds: list[Feed],
        current_day_conditions: CurrentDayConditions,
        total_inventory: TotalInventory,
        simulation_day: int,
    ) -> None:
        """Call the corresponding functions to update the herd structure and reassign animals to new pens."""
        self._handle_graduated_animals(
            graduated_animals, available_feeds, current_day_conditions, total_inventory, simulation_day
        )
        self._handle_newly_added_animals(
            newborn_calves, available_feeds, current_day_conditions, total_inventory, simulation_day
        )
        self._handle_newly_added_animals(
            newly_added_animals, available_feeds, current_day_conditions, total_inventory, simulation_day
        )

        for removed_animal in removed_animals:
            self._remove_animal_from_pen_and_id_map(removed_animal)

    def daily_routines(
        self, available_feeds: list[Feed], time: RufasTime, weather: Weather, total_inventory: TotalInventory
    ) -> dict[str, ManureStream]:
        """
        Perform daily routines for managing animal herds and updating associated data.

        This method handles all daily activities related to the management of animal herds,
        including animal transitions (graduation, removal), sales, births, updates to herd
        statistics, and manure data collection.

        Parameters
        ----------
        available_feeds : list[Feed]
            A list of feed resources available for the day.
        time : RufasTime
            An instance of the RufasTime object representing the current time and simulation day.
        weather : Weather
            An object providing weather conditions affecting herd activities.
        total_inventory : TotalInventory
            Object representing the total inventory of herd-related resources.

        Returns
        -------
        dict[str, ManureStream]
            A list of dictionaries containing manure data for each pen in the herd.

        """
        graduated_animals: list[Animal] = []
        newborn_calves: list[Animal] = []
        removed_animals: list[Animal] = []

        sold_newborn_calves: list[Animal] = []
        stillborn_newborn_calves: list[Animal] = []

        self._reset_daily_statistics()
        self.herd_reproduction_statistics = HerdReproductionStatistics()

        graduated_calves, sold_calves, _, _, _ = self._perform_daily_routines_for_animals(time, self.calves)
        graduated_animals += graduated_calves
        removed_animals += sold_calves

        graduated_heiferIs, sold_heiferIs, _, _, _ = self._perform_daily_routines_for_animals(time, self.heiferIs)
        graduated_animals += graduated_heiferIs
        removed_animals += sold_heiferIs

        graduated_heiferIIs, sold_heiferIIs, _, _, _ = self._perform_daily_routines_for_animals(time, self.heiferIIs)
        graduated_animals += graduated_heiferIIs
        removed_animals += sold_heiferIIs

        # TODO: Rank heifers to enter the herd or sold # GitHub Issue 1214
        (
            graduated_heiferIIIs,
            sold_heiferIIIs,
            stillborn_newborn_calves_from_heiferIIIs,
            newborn_calves_from_heiferIIIs,
            sold_newborn_calves_from_heiferIIIs,
        ) = self._perform_daily_routines_for_animals(time, self.heiferIIIs)
        graduated_animals += graduated_heiferIIIs
        removed_animals += sold_heiferIIIs
        stillborn_newborn_calves += stillborn_newborn_calves_from_heiferIIIs
        sold_newborn_calves += sold_newborn_calves_from_heiferIIIs
        newborn_calves += newborn_calves_from_heiferIIIs

        (
            graduated_cows,
            sold_and_died_cows,
            stillborn_newborn_calves_from_cows,
            newborn_calves_from_cows,
            sold_newborn_calves_from_cows,
        ) = self._perform_daily_routines_for_animals(time, self.cows)
        graduated_animals += graduated_cows
        removed_animals += sold_and_died_cows
        stillborn_newborn_calves += stillborn_newborn_calves_from_cows
        sold_newborn_calves += sold_newborn_calves_from_cows
        newborn_calves += newborn_calves_from_cows
        born_calf_num = len(stillborn_newborn_calves + sold_newborn_calves + newborn_calves)
        self.herd_statistics.born_calf_num = born_calf_num

        self._update_sold_animal_statistics(
            sold_newborn_calves=sold_newborn_calves,
            sold_heiferIIs=sold_heiferIIs,
            sold_and_died_cows=sold_and_died_cows,
        )

        self._update_stillborn_calf_statistics(stillborn_newborn_calves)

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
            simulation_day=time.simulation_day,
        )

        self.record_pen_history(time.simulation_day)
        enteric_methane_emission_by_pen: dict[str, float] = {}
        animal_manure_excretions_by_pen: dict[str, AnimalManureExcretions] = {}
        herd_manager_output: dict[str, ManureStream] = {}
        for pen in self.all_pens:
            animal_manure_excretions_by_pen[f"{pen.animal_combination.name}_PEN_{pen.id}"] = pen.total_manure_excretion
            herd_manager_output.update(pen.get_manure_streams())
            enteric_methane_emission_by_pen[f"{pen.animal_combination.name}_PEN_{pen.id}"] = pen.total_enteric_methane

        self.update_herd_statistics()

        AnimalModuleReporter.report_enteric_methane_emission(enteric_methane_emission_by_pen)
        AnimalModuleReporter.report_daily_animal_population(self.herd_statistics, time.simulation_day)
        AnimalModuleReporter.report_herd_statistics_data(self.herd_statistics, time.simulation_day)
        AnimalModuleReporter.report_manure_excretions(animal_manure_excretions_by_pen, time.simulation_day)
        AnimalModuleReporter.report_manure_streams(herd_manager_output, time.simulation_day)
        AnimalModuleReporter.report_milk(self.daily_milk_report, time.simulation_day)
        AnimalModuleReporter.report_305d_milk(self.average_herd_305_days_milk_production)
        self._report_ration(time.simulation_day)

        return herd_manager_output

    def _report_ration(self, simulation_day: int) -> None:
        """Report the ration for all pens."""
        herd_total_ration: dict[str, float] = {}
        for pen in self.all_pens:
            AnimalModuleReporter.report_daily_pen_total(
                str(pen.id),
                pen.animal_combination.name,
                len(pen.animals_in_pen),
                simulation_day,
            )

            current_pen_ration = pen.total_pen_ration
            AnimalModuleReporter.report_daily_ration_per_pen(
                str(pen.id), pen.animal_combination.name, current_pen_ration, simulation_day
            )
            for key, amount in current_pen_ration.items():
                if key not in herd_total_ration.keys():
                    herd_total_ration[key] = 0.0
                herd_total_ration[key] += amount

        AnimalModuleReporter.report_daily_herd_total_ration(herd_total_ration, simulation_day)

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
        if not (newborn_calf.sold or newborn_calf.stillborn):
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

    def _check_if_replacement_heifers_needed(self, time: RufasTime) -> list[Animal]:
        """
        Checks if replacement heifers are needed to maintain the herd size.

        This function determines whether additional heiferIIIs need to be added to the herd based on
        the current herd size, purchase thresholds, and the availability of heifers in the
        replacement market.

        Parameters
        ----------
        time : RufasTime
            An instance of the RufasTime class providing the current simulation day and date.

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
        simulation_day: int,
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
        simulation_day : int
            Day of simulation.

        """
        for animal in graduated_animals:
            self._remove_animal_from_pen_and_id_map(animal)
            self._update_animal_array(animal)
            self._add_animal_to_pen_and_id_map(
                animal, available_feeds, current_day_conditions, total_inventory, simulation_day
            )

    def _handle_newly_added_animals(
        self,
        new_animals: list[Animal],
        available_feeds: list[Feed],
        current_day_conditions: CurrentDayConditions,
        total_inventory: TotalInventory,
        simulation_day: int,
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
        simulation_day: int
            Day of simulation.

        """
        for animal in new_animals:
            self._add_animal_to_pen_and_id_map(
                animal, available_feeds, current_day_conditions, total_inventory, simulation_day
            )
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
        simulation_day: int,
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
        simulation_day : int
            Day of simulation.

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

            if self.is_ration_defined_by_user:
                user_defined_ration_feed_ids = RationManager.get_user_defined_ration_feeds(
                    pen_with_min_stocking_density.animal_combination
                )
                pen_available_feeds = self._find_pen_available_feeds(available_feeds, user_defined_ration_feed_ids)
            else:
                pen_available_feeds = self._find_pen_available_feeds(available_feeds, RationManager.ration_feeds)
            self._reformulate_ration_single_pen(
                pen=pen_with_min_stocking_density,
                pen_available_feeds=pen_available_feeds,
                current_temperature=current_day_conditions.mean_air_temperature,
                total_inventory=total_inventory,
                simulation_day=simulation_day,
            )

        self.animal_to_pen_id_map[animal.id] = pen_with_min_stocking_density.id

    def initialize_pens(self, all_pen_data: list[dict[str, Any]]) -> None:
        """
        Populates the list of pens with the information from the input json file.

        Parameters
        ----------
        all_pen_data: list[dict[str, Any]]
            List containing information about the pens.

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
            minutes_away_for_milking = pen_data.get("minutes_away_for_milking", 120)
            first_parlor_processor = pen_data.get("first_parlor_processor", None)
            parlor_stream_name = pen_data.get("parlor_stream_name", None)
            manure_streams = pen_data.get("manure_streams")

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
                minutes_away_for_milking=minutes_away_for_milking,
                first_parlor_processor=first_parlor_processor,
                parlor_stream_name=parlor_stream_name,
                manure_streams=manure_streams,
            )

            self.all_pens.append(pen)

    def allocate_animals_to_pens(self, simulation_day: int) -> None:
        """
        Allocate animals to pens based on the current animal population and the number of pens available.
        This method distributes the animals among the pens, ensuring that the animal density of each pen matches
        the overall density as closely as possible.

        """

        self._sort_cows_before_allocation()

        for animal_combination, animals in self.animals_by_combination.items():
            self._allocate_animals_to_pens_helper(
                animals,
                self.pens_by_animal_combination[animal_combination],
            )

        self.fully_update_animal_to_pen_id_map(simulation_day)

    def _plan_animal_allocation(
        self,
        num_animals: int,
        max_spaces_in_pens: list[int],
    ) -> list[int]:
        """
        Make an allocation plan to distribute animals across pens based on overall pen density,
        allowing controlled overstocking if the number of animals exceeds total pen capacity.

        General rules:
        1. Animals are allocated proportionally across pens based on overall density,
        ensuring even distribution relative to pen capacity.
        2. Each pen receives animals up to a calculated allocation limit:
        `ceil(overall_density * pen_capacity)`.
        3. If the total number of animals exceeds the sum of all pen capacities,
        the excess animals are distributed proportionally, allowing pens to exceed capacity.
        4. Warnings are logged for any pen that becomes overstocked.
        5. All animals are guaranteed to be allocated.

        Notes
        -----
        This allocation strategy prioritizes proportional and fair distribution by calculating
        an overall density and applying it to each pen's capacity. The result ensures that
        pen densities remain consistent even under overstocking scenarios.

        Pens are sorted by allocation limit, and animals are allocated in that order. The final
        pen receives any remaining animals to guarantee full allocation.

        Overstocking is permitted when necessary and is handled fairly based on capacity-derived
        allocation limits. Logging ensures that overstocked pens are tracked for review.

        Parameters
        ----------
        num_animals : int
            The total number of animals to allocate. Must be a non-negative integer.
        max_spaces_in_pens : list[int]
            A list of integers representing the maximum number of animals each pen can accommodate
            without overstocking. Each integer must be positive.

        Returns
        -------
        list[int]
            A list of integers representing the number of animals allocated to each pen.
            Each value may exceed the pen's capacity if overstocking occurs.

        Raises
        ------
        AssertionError
            If the total number of allocated animals does not match the number of animals provided.

        Examples
        --------
        >>> _plan_animal_allocation(num_animals=90, max_spaces_in_pens=[30, 30, 30], simulation_day=1)
        [30, 30, 30]

        >>> _plan_animal_allocation(num_animals=95, max_spaces_in_pens=[30, 30, 30], simulation_day=1)
        [32, 32, 31]

        >>> _plan_animal_allocation(num_animals=47, max_spaces_in_pens=[20, 15, 10], simulation_day=1)
        [20, 16, 11]  # Overstocked due to animal count exceeding total capacity

        >>> _plan_animal_allocation(num_animals=70, max_spaces_in_pens=[50, 30, 20], simulation_day=1)
        [35, 21, 14]
        """

        num_pens_for_combination = len(max_spaces_in_pens)
        total_capacity = sum(max_spaces_in_pens)
        allocation = [0] * num_pens_for_combination

        overall_density = num_animals / total_capacity
        allocation_limits = [math.ceil(overall_density * capacity) for capacity in max_spaces_in_pens]

        sorted_pen_indices = sorted(range(num_pens_for_combination), key=lambda i: (allocation_limits[i], i))

        remaining_animals = num_animals
        for pen_index in sorted_pen_indices[:-1]:
            allocation[pen_index] = min(allocation_limits[pen_index], remaining_animals)
            remaining_animals -= allocation[pen_index]

        last_pen = sorted_pen_indices[-1]
        allocation[last_pen] = remaining_animals

        assert (
            sum(allocation) == num_animals
        ), f"Sanity check failed: allocated {sum(allocation)} animals, expected {num_animals}"

        return allocation

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

        start_animal_count = 0
        for index, count in enumerate(allocation_plan):
            end = start_animal_count + count
            animal_pens[index].insert_animals_into_animals_in_pen_map(animals[start_animal_count:end])
            start_animal_count = end

    def _sort_cows_before_allocation(self) -> None:
        """Sort cows by days_in_milk in increasing order."""
        self.cows = list(filter(lambda cow: not cow.is_milking, self.cows)) + sorted(
            list(filter(lambda cow: cow.is_milking, self.cows)), key=lambda cow: cow.days_in_milk
        )

    def _calculate_max_animal_spaces_per_pen(self, num_stalls: int, max_stocking_density: float) -> int:
        """
        Calculate the maximum number of animal spaces available per pen based on the user density.

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

    def _allocate_animals_to_pens_helper(
        self,
        animals: list[Animal],
        pens: list[Pen],
    ) -> None:
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

    def fully_update_animal_to_pen_id_map(self, simulation_day: int) -> None:
        """
        Updates the entire animal_to_pen_id_map dictionary so that each animal's ID is
        associated with the pen that animal is in.

        """
        for pen in self.all_pens:
            animals_in_pen = pen.animals_in_pen
            if pen.current_stocking_density > pen.max_stocking_density:
                self.om.add_warning(
                    f"Warning: Pen {pen.id} is overstocked.",
                    f"Pen {pen.id} has {len(pen.animals_in_pen)} animals, exceeding max capacity "
                    f"of {self._calculate_max_animal_spaces_per_pen(pen.num_stalls, pen.max_stocking_density)} "
                    f"on simulation day {simulation_day}.",
                    info_map={
                        "class": self.__class__.__name__,
                        "function": self.fully_update_animal_to_pen_id_map.__name__,
                        "simulation_day": simulation_day,
                    },
                )

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
        if self.is_ration_defined_by_user:
            calf_feeds = list(RationManager.user_defined_rations[AnimalCombination.CALF].keys())
        else:
            calf_feeds = RationManager.ration_feeds[AnimalCombination.CALF]

        if WHOLE_MILK_ID in calf_feeds:
            milk_type = CalfMilkType.WHOLE
        else:
            milk_type = CalfMilkType.REPLACER

        CalfRationManager.set_milk_type(milk_type)

        info_map = {
            "class": self.__class__.__name__,
            "function": self.set_milk_type_in_calf_ration_manager.__name__,
            "milk_type": milk_type.value,
            "calf_feeds": calf_feeds,
        }
        self.om.add_log(
            "Milk type set for calf ration",
            f"Calf requirements routines will assume 100% of calves' milk intake is {milk_type.value}",
            info_map,
        )

    def initialize_nutrient_requirements(self, weather: Weather, time: RufasTime, available_feeds: list[Feed]) -> None:
        """
        Calculates initial nutrient requirements at the beginning of the simulation for initial pen allocation.

        Parameters
        ----------
        weather : Weather
            instance of the Weather class
        time : RufasTime
            instance of the RufasTime class
        available_feeds : list[Feed]
            Nutrition information of feeds available to formulate animals rations with.

        """
        for pen in self.all_pens:
            pen.set_animal_nutritional_requirements(
                weather.get_current_day_conditions(time).mean_air_temperature, available_feeds
            )

    def update_all_max_daily_feeds(
        self, total_inventory: TotalInventory, next_harvest_dates: dict[RUFAS_ID, date], time: RufasTime
    ) -> IdealFeeds:
        """
        Updates the max feeds of all available feeds types based on the current total inventory.

        Parameters
        ----------
        total_inventory : TotalInventory
            The total inventory of all available feeds.
        next_harvest_dates : Dict[RUFAS_ID, date]
            The next harvest date for each applicable feed type.
        time : RufasTime
            RufasTime object.

        Returns
        -------
        IdealFeeds
            The maximum daily feeds for each feed type.

        """
        if not self.simulate_animals:
            return IdealFeeds({})
        for rufas_id in next_harvest_dates.keys():
            self._update_single_max_daily_feed(rufas_id, next_harvest_dates[rufas_id], total_inventory, time)

        # TODO: calculate feeds that would ideally be purchased before next harvests based on "herd needs". Issue #2483.
        return IdealFeeds({})

    def _update_single_max_daily_feed(
        self, rufas_id: RUFAS_ID, next_harvest: date, total_inventory: TotalInventory, time: RufasTime
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
        time : RufasTime
            RufasTime object.

        """
        total_animal_population = len(self.animal_to_pen_id_map.keys())
        days_until_next_harvest = (next_harvest - time.current_date.date()).days

        self._max_daily_feeds[rufas_id] = (
            total_inventory.available_feeds.get(rufas_id, 0.0) / total_animal_population / days_until_next_harvest
        )

    def _find_pen_available_feeds(
        self, all_available_feeds: list[Feed], user_defined_ration_feed_ids: list[RUFAS_ID]
    ) -> list[Feed]:
        """Find the available feeds for the pen."""
        return [feed for feed in all_available_feeds if feed.rufas_id in user_defined_ration_feed_ids]

    def formulate_rations(
        self,
        available_feeds: list[Feed],
        current_temperature: float,
        ration_interval_length: int,
        total_inventory: TotalInventory,
        simulation_day: int,
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
        simulation_day : int
            Day of simulation.

        Returns
        -------
        RequestedFeed
            Feeds requested to be purchased for the newly formulated rations.

        """
        if not self.simulate_animals:
            return RequestedFeed({})
        self.clear_pens()
        self.allocate_animals_to_pens(simulation_day)

        total_requested_feed = RequestedFeed({})
        for pen in self.all_pens:
            if not pen.is_populated:
                pen.ration = {}
                continue
            if self.is_ration_defined_by_user:
                ration_feed_ids = RationManager.get_user_defined_ration_feeds(pen.animal_combination)
            else:
                ration_feed_ids = RationManager.get_ration_feeds(pen.animal_combination)
            pen_available_feeds = self._find_pen_available_feeds(available_feeds, ration_feed_ids)
            self._reformulate_ration_single_pen(
                pen, pen_available_feeds, current_temperature, total_inventory, simulation_day
            )
            total_requested_feed += pen.get_requested_feed(ration_interval_length)
        return total_requested_feed

    def _reformulate_ration_single_pen(
        self,
        pen: Pen,
        pen_available_feeds: list[Feed],
        current_temperature: float,
        total_inventory: TotalInventory,
        simulation_day: int,
    ) -> None:
        """
        Reformulates ration for a single pen.

        Parameters
        ----------
        pen : Pen
            Pen that requires ration reformulation.
        pen_available_feeds : List[Feed]
            List of available feeds in this pen.
        current_temperature : float
            Current temperature (C).
        total_inventory : TotalInventory
            Inventory currently available or projected to be available at a future date.
        simulation_day : int
            Day of simulation.

        """
        if pen.animal_combination == AnimalCombination.LAC_COW and pen.average_milk_production == 0.0:
            for animal in pen.animals_in_pen:
                pen.animals_in_pen[animal].daily_milking_update_without_history()
        if pen.animal_combination == AnimalCombination.CALF:
            if not self.is_ration_defined_by_user:
                ration_fraction = 100 / len(pen_available_feeds)
                RationManager.user_defined_rations = {}
                RationManager.user_defined_rations[AnimalCombination.CALF] = {
                    feed_id.rufas_id: ration_fraction for feed_id in pen_available_feeds
                }
            pen.use_user_defined_ration(pen_available_feeds, current_temperature)
        else:
            pen.formulate_optimized_ration(
                self.is_ration_defined_by_user,
                pen_available_feeds,
                current_temperature,
                self._max_daily_feeds,
                self.advance_purchase_allowance,
                total_inventory,
                simulation_day,
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
        parity_4_cows = [cow for cow in self.cows if cow.reproduction.calves == 4]
        parity_5_cows = [cow for cow in self.cows if cow.reproduction.calves == 5]
        parity_greater_than_5_cows = [cow for cow in self.cows if cow.reproduction.calves > 5]
        self.herd_statistics.num_cow_for_parity = {
            "1": len(parity_1_cows),
            "2": len(parity_2_cows),
            "3": len(parity_3_cows),
            "4": len(parity_4_cows),
            "5": len(parity_5_cows),
            "greater_than_5": len(parity_greater_than_5_cows),
        }
        self.herd_statistics.avg_age_for_parity = {
            "1": sum([cow.days_born for cow in parity_1_cows]) / len(parity_1_cows) if len(parity_1_cows) > 0 else 0,
            "2": sum([cow.days_born for cow in parity_2_cows]) / len(parity_2_cows) if len(parity_2_cows) > 0 else 0,
            "3": sum([cow.days_born for cow in parity_3_cows]) / len(parity_3_cows) if len(parity_3_cows) > 0 else 0,
            "4": sum([cow.days_born for cow in parity_4_cows]) / len(parity_4_cows) if len(parity_4_cows) > 0 else 0,
            "5": sum([cow.days_born for cow in parity_5_cows]) / len(parity_5_cows) if len(parity_5_cows) > 0 else 0,
            "greater_than_5": (
                sum([cow.days_born for cow in parity_greater_than_5_cows]) / len(parity_greater_than_5_cows)
                if len(parity_greater_than_5_cows) > 0
                else 0
            ),
        }

        parity_1_calving_age = [cow.events.get_most_recent_date(animal_constants.NEW_BIRTH) for cow in parity_1_cows]
        parity_2_calving_age = [cow.events.get_most_recent_date(animal_constants.NEW_BIRTH) for cow in parity_2_cows]
        parity_3_calving_age = [cow.events.get_most_recent_date(animal_constants.NEW_BIRTH) for cow in parity_3_cows]
        parity_4_calving_age = [cow.events.get_most_recent_date(animal_constants.NEW_BIRTH) for cow in parity_4_cows]
        parity_5_calving_age = [cow.events.get_most_recent_date(animal_constants.NEW_BIRTH) for cow in parity_5_cows]
        parity_greater_than_5_calving_age = [
            cow.events.get_most_recent_date(animal_constants.NEW_BIRTH) for cow in parity_greater_than_5_cows
        ]

        parity_1_calving_age = [calving_age for calving_age in parity_1_calving_age if calving_age > 0]
        parity_2_calving_age = [calving_age for calving_age in parity_2_calving_age if calving_age > 0]
        parity_3_calving_age = [calving_age for calving_age in parity_3_calving_age if calving_age > 0]
        parity_4_calving_age = [calving_age for calving_age in parity_4_calving_age if calving_age > 0]
        parity_5_calving_age = [calving_age for calving_age in parity_5_calving_age if calving_age > 0]
        parity_greater_than_5_calving_age = [
            calving_age for calving_age in parity_greater_than_5_calving_age if calving_age > 0
        ]
        self.herd_statistics.avg_age_for_calving = {
            "1": (sum(parity_1_calving_age) / len(parity_1_calving_age)) if len(parity_1_calving_age) > 0 else 0,
            "2": (sum(parity_2_calving_age) / len(parity_2_calving_age)) if len(parity_2_calving_age) > 0 else 0,
            "3": (sum(parity_3_calving_age) / len(parity_3_calving_age)) if len(parity_3_calving_age) > 0 else 0,
            "4": (sum(parity_4_calving_age) / len(parity_4_calving_age)) if len(parity_4_calving_age) > 0 else 0,
            "5": (sum(parity_5_calving_age) / len(parity_5_calving_age)) if len(parity_5_calving_age) > 0 else 0,
            "greater_than_5": (
                (sum(parity_greater_than_5_calving_age) / len(parity_greater_than_5_calving_age))
                if len(parity_greater_than_5_calving_age) > 0
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
        parity_4_calving_to_pregnancy_time = [
            cow.reproduction.reproduction_statistics.calving_to_pregnancy_time for cow in parity_4_cows
        ]
        parity_5_calving_to_pregnancy_time = [
            cow.reproduction.reproduction_statistics.calving_to_pregnancy_time for cow in parity_5_cows
        ]
        parity_greater_than_5_calving_to_pregnancy_time = [
            cow.reproduction.reproduction_statistics.calving_to_pregnancy_time for cow in parity_greater_than_5_cows
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
        parity_4_calving_to_pregnancy_time = [
            calving_to_pregnancy_time
            for calving_to_pregnancy_time in parity_4_calving_to_pregnancy_time
            if calving_to_pregnancy_time > 0
        ]
        parity_5_calving_to_pregnancy_time = [
            calving_to_pregnancy_time
            for calving_to_pregnancy_time in parity_5_calving_to_pregnancy_time
            if calving_to_pregnancy_time > 0
        ]
        parity_greater_than_5_calving_to_pregnancy_time = [
            calving_to_pregnancy_time
            for calving_to_pregnancy_time in parity_greater_than_5_calving_to_pregnancy_time
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
            "4": (
                (sum(parity_4_calving_to_pregnancy_time) / len(parity_4_calving_to_pregnancy_time))
                if len(parity_4_calving_to_pregnancy_time) > 0
                else 0
            ),
            "5": (
                (sum(parity_5_calving_to_pregnancy_time) / len(parity_5_calving_to_pregnancy_time))
                if len(parity_5_calving_to_pregnancy_time) > 0
                else 0
            ),
            "greater_than_5": (
                (
                    sum(parity_greater_than_5_calving_to_pregnancy_time)
                    / len(parity_greater_than_5_calving_to_pregnancy_time)
                )
                if len(parity_greater_than_5_calving_to_pregnancy_time) > 0
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
            if parity == "greater_than_5":
                culled_cows_with_current_parity = [cow for cow in sold_and_died_cows if cow.reproduction.calves > 5]
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

    def report_ration_interval_data(self, simulation_day: int) -> None:
        """Reports the ration interval data for the herd."""
        for pen in self.all_pens:
            if not pen.is_populated:
                continue

            pen_base_name = f"{pen.animal_combination.name}_PEN_{pen.id}"
            average_nutrition_supply = pen.average_nutrition_supply
            total_dry_matter = average_nutrition_supply.dry_matter
            num_animals = len(pen.animals_in_pen)

            AnimalModuleReporter.report_ration_per_animal(
                pen_base_name, pen.ration, total_dry_matter, num_animals, simulation_day
            )
            AnimalModuleReporter.report_nutrient_amounts(
                pen_base_name, average_nutrition_supply, num_animals, simulation_day
            )
            AnimalModuleReporter.report_me_diet(
                pen_base_name, average_nutrition_supply.metabolizable_energy, num_animals, simulation_day
            )

            if pen.animal_combination != AnimalCombination.CALF:
                AnimalModuleReporter.report_average_nutrient_requirements(
                    pen_base_name,
                    pen.average_nutrition_requirements,
                    pen.average_body_weight,
                    pen.average_milk_production_reduction,
                    num_animals,
                    simulation_day,
                )
                AnimalModuleReporter.report_average_nutrient_evaluation_results(
                    pen_base_name, pen.average_nutrition_evaluation, simulation_day
                )

    def _update_total_enteric_methane(self, digestive_outputs: list[dict[AnimalType, dict[str, float]]]) -> None:
        """Update the amount of total enteric methane in the herd statistics."""
        for methane_emission in digestive_outputs:
            for animal_type in methane_emission:
                if animal_type in self.herd_statistics.total_enteric_methane:
                    current_totals = self.herd_statistics.total_enteric_methane[animal_type]
                    new_emissions = methane_emission[animal_type]

                    all_keys = set(current_totals.keys()) | set(new_emissions.keys())
                    self.herd_statistics.total_enteric_methane[animal_type] = {
                        k: float(current_totals.get(k, 0) + new_emissions.get(k, 0)) for k in all_keys
                    }
