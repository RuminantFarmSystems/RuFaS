import math
from collections import defaultdict
from typing import Any, Optional

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_genetics.animal_genetics import AnimalGenetics
from RUFAS.biophysical.animal.animal_grouping_scenarios import AnimalGroupingScenario
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_enums import AnimalStatus
from RUFAS.biophysical.animal.data_types.herd_statistics import HerdStatistics
from RUFAS.data_structures.animal_manure_excretions import AnimalManureExcretions
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.daily_routines_output import DailyRoutinesOutput
from RUFAS.biophysical.animal.herd_factory import HerdFactory
from RUFAS.biophysical.animal.milk.lactation_curve import LactationCurve
from RUFAS.biophysical.animal.pen import Pen
from RUFAS.biophysical.animal.ration.calf_ration import CalfRationManager
from RUFAS.biophysical.animal.ration.ration_driver import AvailableFeeds, RationManager, RationReporter
from RUFAS.biophysical.feed.feed import Feed
from RUFAS.biophysical.animal.ration.user_defined_ration import UserDefinedRationManager
from RUFAS.data_structures.herd_manager_output import HerdManagerOutput
from RUFAS.enums import AnimalCombination
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.routines.animal.purchased_feed_emissions_estimator import PurchasedFeedEmissionsEstimator
from RUFAS.time import Time
from RUFAS.util import Utility
from RUFAS.weather import Weather

om = OutputManager()


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

        Returns
        -------
        None

        """

        cls.ANIMAL_GROUPING_SCENARIO = scenario

    def __init__(
        self,
        feed: Feed,
        weather: Weather,
        time: Time,
        feed_emissions_estimator: PurchasedFeedEmissionsEstimator = None,
    ) -> None:
        """
        Initializes the pens and animals in the simulation with data from the
        JSON file by calling init_pens() and init_animals(). Creates instance
        of LifeCycleManager class and sets up the animal environment.

        Parameters
        ----------
        data : Dict[str, Any]
            dictionary with animal information from the input JSON file
        feed : Feed
            instance of the Feed class
        weather : Weather
            instance of the Weather class
        time : Time
            instance of the Time class
        feed_emissions_estimator : PurchasedFeedEmissionsEstimator, default=None
            Instance of the PurchasedFeedEmissionsEstimator class.

        """
        self.im = InputManager()
        config_data: dict[str, Any] = self.im.get_data("config")
        animal_config_data: dict[str, Any] = self.im.get_data("animal")
        manure_management_config_data: list[dict[str, Any]] = self.im.get_data(
            "manure_management")["manure_management_scenarios"]

        AnimalConfig.initialize_animal_config()

        # how do we set lactation curve
        LactationCurve.set_lactation_parameters(time)

        # if False, there are no animals being simulated on the farm
        self.simulate_animals = config_data.get("simulate_animals", True)

        # list of all the animals in the simulation
        self.calves: list[Animal] = []
        self.heiferIs: list[Animal] = []
        self.heiferIIs: list[Animal] = []
        self.heiferIIIs: list[Animal] = []
        self.cows: list[Animal] = []
        self.replacement_market: list[Animal] = []

        self.heifers_sold: list[Animal] = []
        self.cows_culled: list[Animal] = []

        # list of all the pens on the farm
        self.all_pens: list[Pen] = []

        # dictionary: key is animal ID, value is the pen ID that animal is in
        self.animal_to_pen_id_map: dict[int, int] = {}

        # alternative option: AnimalGroupingScenario.CALF__GROWING_AND_CLOSE_UP__LACCOW
        self.set_animal_grouping_scenario(AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW)

        # dictionary for keeping track of what animal types each pen is holding
        # (value of the dictionaries are lists of pen objects)
        self.pens_by_animal_combination = {
            AnimalCombination.CALF: [],
            AnimalCombination.GROWING: [],
            AnimalCombination.CLOSE_UP: [],
            AnimalCombination.GROWING_AND_CLOSE_UP: [],
            AnimalCombination.LAC_COW: [],
        }

        # these variables are the P concentrations of each class of animal. They
        # are calculated daily and are used when an animal is added to the
        # herd, whether by birth or replacement herd purchase. They are calculated
        # in _update_phosphorus_concentrations() and are calculated by dividing the total P in the animals
        # of the class by the total body weight of the animals, on a per-animal basis
        self.phosphorus_concentration_by_animal_class = {
            animal_type: 0.0 for animal_type in [
                AnimalType.CALF, AnimalType.HEIFER_I, AnimalType.HEIFER_II, AnimalType.HEIFER_III, AnimalType.LAC_COW,
                AnimalType.CALF.DRY_COW
            ]
        }
        self.herd_statistics = HerdStatistics()
        self.herd_statistics.herd_num = animal_config_data["herd_information"]["herd_num"]

        self.housing = animal_config_data["housing"]
        self.pasture_concentrate = animal_config_data["pasture_concentrate"]

        user_defined_ration_manager = UserDefinedRationManager()
        self.ration_user_input = animal_config_data["ration"]["user_input"]
        user_defined_ration_manager.use_user_defined_ration = self.ration_user_input

        # how often a ration is calculated, days
        self.formulation_interval = animal_config_data["ration"]["formulation_interval"]

        self.initialize_pens(animal_config_data["pen_information"], manure_management_config_data)

        if self.simulate_animals:
            herd_factory = HerdFactory()
            (
                self.calves,
                self.heiferIs,
                self.heiferIIs,
                self.heiferIIIs,
                self.cows,
                self.replacement_market
            ) = herd_factory.initialize_herd()

            self.initialize_nutrient_requirements(weather, time, feed)

            self.allocate_animals_to_pens()

        self._print_animal_num_warnings(animal_config_data["herd_information"])

        self.feeds_emissions_estimator: Optional[PurchasedFeedEmissionsEstimator] = (
            feed_emissions_estimator or PurchasedFeedEmissionsEstimator()
        )

    @property
    def animals_by_type(self) -> dict[AnimalType, list[Animal]]:
        return {
            AnimalType.CALF: self.calves,
            AnimalType.HEIFER_I: self.heiferIs,
            AnimalType.HEIFER_II: self.heiferIIs,
            AnimalType.HEIFER_III: self.heiferIIIs,
            AnimalType.LAC_COW: [cow for cow in self.cows if cow.is_milking],
            AnimalType.DRY_COW: [cow for cow in self.cows if not cow.is_milking],
        }

    def daily_routines(self, feed: Feed, weather: Weather, time: Time) -> list[HerdManagerOutput]:
        current_conditions = weather.get_current_day_conditions(time)
        current_temperature = current_conditions.mean_air_temperature

        graduated_animals: list[Animal] = []
        newborn_calves: list[Animal] = []
        removed_animals: list[Animal] = []

        sold_heiferIIs: list[Animal] = []
        sold_newborn_calves: list[Animal] = []
        sold_and_died_cows: list[Animal] = []

        self.herd_statistics.reset_daily_stats()
        self.herd_statistics.reset_parity()
        self.herd_statistics.reset_cull_reason_stats()

        # calf update
        for calf in self.calves:
            calf_daily_routines_output: DailyRoutinesOutput = calf.daily_routines(time)
            if calf_daily_routines_output.animal_status == AnimalStatus.LIFE_STAGE_CHANGED:
                graduated_animals.append(calf)
            elif calf_daily_routines_output.animal_status in [
                AnimalStatus.DEAD, AnimalStatus.CULLED, AnimalStatus.SOLD
            ]:
                removed_animals.append(calf)
        # heiferI update
        for heiferI in self.heiferIs:
            heiferI_routines_output: DailyRoutinesOutput = heiferI.daily_routines(time)
            if heiferI_routines_output.animal_status == AnimalStatus.LIFE_STAGE_CHANGED:
                graduated_animals.append(heiferI)
            elif heiferI_routines_output.animal_status in [
                AnimalStatus.DEAD, AnimalStatus.CULLED, AnimalStatus.SOLD
            ]:
                removed_animals.append(heiferI)
        # heiferII update
        for heiferII in self.heiferIIs:
            heiferII_routines_output: DailyRoutinesOutput = heiferII.daily_routines(time)
            if heiferII_routines_output.animal_status == AnimalStatus.LIFE_STAGE_CHANGED:
                graduated_animals.append(heiferII)
            elif heiferII_routines_output.animal_status in [
                AnimalStatus.DEAD, AnimalStatus.CULLED, AnimalStatus.SOLD
            ]:
                removed_animals.append(heiferII)
                sold_heiferIIs.append(heiferII)
        # heiferIII update
        for heiferIII in self.heiferIIIs:
            heiferIII_routines_output: DailyRoutinesOutput = heiferIII.daily_routines(time)
            if heiferIII_routines_output.animal_status == AnimalStatus.LIFE_STAGE_CHANGED:
                graduated_animals.append(heiferIII)
            elif heiferIII_routines_output.animal_status in [
                AnimalStatus.DEAD, AnimalStatus.CULLED, AnimalStatus.SOLD
            ]:
                removed_animals.append(heiferIII)
        # cow update
        for cow in self.cows:
            cow_routines_output: DailyRoutinesOutput = cow.daily_routines(time)
            if cow_routines_output.animal_status == AnimalStatus.NEW_CALF_BORN:
                newborn_calf = Animal(args={**cow_routines_output.animal_values})
                if not (newborn_calf.sold or newborn_calf.culled):
                    newborn_calf.events.add_event(
                        newborn_calf.days_born, time.simulation_day, animal_constants.ENTER_HERD
                    )
                    newborn_calves.append(newborn_calf)
                if newborn_calf.sold:
                    sold_newborn_calves.append(newborn_calf)

            elif cow_routines_output.animal_status in [
                AnimalStatus.DEAD, AnimalStatus.CULLED, AnimalStatus.SOLD
            ]:
                removed_animals.append(cow)
                sold_and_died_cows.append(cow)
        self._update_sold_and_died_cows(sold_and_died_cows)
        self._update_sold_heiferIIs(sold_heiferIIs)
        self._update_sold_newborn_calves(sold_newborn_calves)

        removed_animals += self._check_if_heifers_need_to_be_sold(simulation_day=time.simulation_day)
        newly_added_animals = self._check_if_replacement_heifers_needed(simulation_day=time.simulation_day)

        self._handle_graduated_animals(graduated_animals, feed, current_temperature)
        self._handle_newly_added_animals(newborn_calves, feed, current_temperature)
        self._handle_newly_added_animals(newly_added_animals, feed, current_temperature)
        for removed_animal in removed_animals:
            self._remove_animal_from_pen_and_id_map(removed_animal)


        self.record_pen_history(time.simulation_day)

        if self.end_ration_interval(time.simulation_day):
            self.clear_pens()
            self.allocate_animals_to_pens()

        for pen in self.all_pens:
            if pen.needs_ration_formulation or self.end_ration_interval(time.simulation_day):
                self.reformulate_ration_single_pen(pen, current_temperature, feed)

        herd_manager_output: list[HerdManagerOutput] = []
        for pen in self.all_pens:
            herd_manager_output.append(HerdManagerOutput(
                pen_manure=pen.get_manure_data,
                manure_excretion=pen.total_manure_excretion
            ))

        self.update_herd_statistics()

        AnimalModuleReporter.report_animal_module_manure(herd_manager_output)

        AnimalModuleReporter.report_daily_reports(self, feed.available_feeds, time.simulation_day)

        return herd_manager_output

    def initialize_pens(
            self,
            all_pen_data: list[dict[str, Any]],
            manure_management_scenarios: list[dict[str, Any]]
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
        # Initialize pens from all_pen_data
        for pen_data in all_pen_data:
            animal_combination_value: int = AnimalCombination[pen_data.get("animal_combination")].value
            pen_id = pen_data.get('id')
            pen_name = pen_data.get("name", "")
            animal_combination=AnimalCombination(animal_combination_value)
            vertical_dist_to_milking_parlor = pen_data.get("vertical_dist_to_milking_parlor")
            horizontal_dist_to_milking_parlor = pen_data.get("horizontal_dist_to_milking_parlor")
            number_of_stalls = pen_data.get("number_of_stalls")
            housing_type = pen_data.get("housing_type")
            pen_type = pen_data.get("pen_type")
            max_stocking_density = pen_data.get("max_stocking_density")

            manure_management_scenario_id = pen_data.get("manure_management_scenario_id")
            manure_management_scenario = [
                scenario
                for scenario in manure_management_scenarios
                if scenario["scenario_id"] == manure_management_scenario_id
            ][0]
            bedding_type = manure_management_scenario["bedding_type"]
            manure_handling = manure_management_scenario["manure_handler"]
            manure_separator = manure_management_scenario["manure_separator"]
            manure_separator_after_digestion = manure_management_scenario[
                "manure_separator_after_digestion"]
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

    def initialize_nutrient_requirements(self, weather: Weather, time: Time, feed: Feed) -> None:
        """
        Calculates initial nutrient requirements at the beginning of the
        simulation for initial pen allocation. For the nutrient requirements
        of cows, the average walking distance of all the pens initialized
        is used.

        Parameters
        ----------
        feed : Feed
            an instance of the Feed class defined in feed.py
        weather : Weather
            instance of the Weather class
        time : Time
            instance of the Time class

        """

        pass

    def allocate_animals_to_pens(self) -> None:
        """
        Allocate animals to pens based on the current animal population and the number of pens available.
        New default pens will be created if necessary. This method distributes the animals among the pens,
        ensuring that the animal density of each pen matches the overall density as closely as possible.

        Returns
        -------
        None

        """

        self._sort_cows_before_allocation()
        self.pens_by_animal_combination = self._group_pens_by_animal_combination(self.all_pens)
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
        for animal_combination, animals in animals_by_combination.items():
            new_default_pens = self._create_additional_pens_for_potential_space_shortage(
                num_animals=len(animals),
                pens=self.pens_by_animal_combination[animal_combination],
                animal_combination=animal_combination,
                start_pen_id=len(self.all_pens),
            )
            self.all_pens.extend(new_default_pens)
            self.pens_by_animal_combination[animal_combination].extend(new_default_pens)
            self._allocate_animals_to_pens_helper(animals, self.pens_by_animal_combination[animal_combination])

        self.fully_update_animal_to_pen_id_map()

    def _handle_pen_ration(self, feed: Feed, pen: Pen) -> None:
        """
        Calculate the ration for each pen at the given interval and update the
        ration for each animal in the pen.

        Notes
        -----
        It is important to set the variable `ration_per_animal` for each pen object. This forms the
        basis for scaling the ration for each pen based on the current number of animals in the pen.

        Parameters
        ----------
        feed : Feed
            Instance of the Feed class
        pen : Pen
            Instance of Pen class.

        """
        pass

    def _check_if_heifers_need_to_be_sold(
        self,
        simulation_day: int,
    ) -> list[Animal]:
        """Checks if any heifers need to be sold.

        If the number of heifers exceeds what is needed for the herd,
        sell those as replacement

        Args:
            heiferIIIs: The list of heiferIIIs.
            cows: The list of cows.
            animals_removed: The list of animals removed from the herd.

        """
        animals_removed: list[Animal] = []
        sell_threshold = 1.03
        while (len(self.heiferIIIs) + len(self.cows) > self.herd_statistics.herd_num * sell_threshold
               and len(self.heiferIIIs) > 0):
            removed_heiferIII = self.heiferIIIs.pop()
            animals_removed.append(removed_heiferIII)
            removed_heiferIII.sold_at_day = simulation_day
            self.herd_statistics.sold_heiferIIIs_info.append(
                {
                    "id": removed_heiferIII.id,
                    "animal_type": removed_heiferIII.animal_type,
                    "sold_at_day": removed_heiferIII.sold_at_day,
                    "body_weight": removed_heiferIII.body_weight,
                    "cull_reason": "NA",
                    "days_in_milk": "NA",
                    "parity": "NA",
                }
            )
            self.herd_statistics.sold_heiferIII_oversupply_num += 1
            self.herd_statistics.heiferIII_num -= 1
        return animals_removed

    def _check_if_replacement_heifers_needed(
        self,
        simulation_day: int
    ) -> list[Animal]:
        """Checks if replacement heifers are needed.

        If the number of heifers is less than what is needed for the herd,
        add replacement heifers.

        Args:
            sim_day: The current simulation day.
            heiferIIIs: The list of heiferIIIs.
            cows: The list of cows.
            animals_added: The list of animals added to the herd.

        """
        animals_added: list[Animal] = []
        buy_threshold = 1.01
        while (len(self.cows) + len(self.heiferIIIs) + self.herd_statistics.bought_heifer_num <
               self.herd_statistics.herd_num * buy_threshold and simulation_day > 1):
            if len(self.replacement_market) == 0:
                break
            replacement = self.replacement_market.pop(0)
            replacement.events.add_event(replacement.days_born, simulation_day, animal_constants.ENTER_HERD)
            replacement.set_p_purchased()
            replacement.net_merit = AnimalGenetics.assign_net_merit_value_to_animals_entering_herd(
                replacement.birth_date, replacement.breed
            )
            animals_added.append(replacement)
            self.herd_statistics.bought_heifer_num += 1
        return animals_added

    def _handle_graduated_animals(
        self,
        graduated_animals: list[Animal],
        feed: Feed,
        current_temperature: float,
    ) -> None:
        """
        Finds animals that have graduated (moved from one class to another), moves them between pens,
         and updates pen id map accordingly.

        Parameters
        ----------
        animals_snapshot_before_update : Dict[str, set | Dict]
            Snapshot of the animals before the update. This should be a dictionary with animal
            class names as keys and sets of animals as values. There should also be a special key
            'animal_combination_by_id' that maps animal IDs to their animal combinations.
        animals_snapshot_after_update : Dict[str, set | Dict]
            Snapshot of the animals after the update. This should be a dictionary with the same
            structure as animals_snapshot_before_update.
        feed : Feed
            instance of the Feed class defined in feed.py.
        current_temperature : float
            The temperature on the current day.

        """
        for animal in graduated_animals:
            self._add_animal_to_pen_and_id_map(animal, feed, current_temperature)

    def _handle_newly_added_animals(
        self,
        new_animals: list[Animal],
        feed: Feed,
        current_temperature: float,
    ) -> None:
        """
        For all new animals, adds animal to a pen, and updates the pen id map.

        Parameters
        ----------
        animal : List[Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]]
            One of the possible animal types.
        feed : Feed
            instance of the Feed class defined in feed.py.
        current_temperature : float
            The temperature on the current day.

        """
        for animal in new_animals:
            self._add_animal_to_pen_and_id_map(animal, feed, current_temperature)
            self.animals_by_type[animal.animal_type].append(animal)

    def _remove_animal_from_pen_and_id_map(self, animal: Animal) -> None:
        """
        Removes animal from its current pen, and removes it from the pen id map.

        Parameters
        ----------
        animal : Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]
            One of the possible animal types.

        """
        pen_id = self.animal_to_pen_id_map[animal.id]
        self.all_pens[pen_id].remove_animals_by_ids([animal.id])
        del self.animal_to_pen_id_map[animal.id]

    def _add_animal_to_pen_and_id_map(
        self,
        animal: Animal,
        feed: Feed,
        current_temperature: float,
    ) -> None:
        """
        Adds animal to pen with lowest stocking density, and updates the pen id map accordingly.

        Parameters
        ----------
        animal : Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]
            One of the possible animal types.
        feed : Feed
            instance of the Feed class defined in feed.py.
        current_temperature : float
            The temperature on the current day.

        """
        animal_combination = self.ANIMAL_GROUPING_SCENARIO.find_animal_combination(animal)
        pen_with_min_stocking_density = min(
            self.pens_by_animal_combination[animal_combination],
            key=lambda p: p.current_stocking_density,
        )
        pen_with_min_stocking_density.update_animals(
            [animal],
            self.ANIMAL_GROUPING_SCENARIO,
            feed,
            current_temperature,
            self.phosphorus_concentration_by_animal_class[animal.animal_type],
        )
        self.animal_to_pen_id_map[animal.id] = pen_with_min_stocking_density.id

    def _sort_cows_before_allocation(self) -> None:
        """
        Sort lactating cows by days in milk in increasing order.
        """
        self.cows = list(filter(lambda cow: not cow.is_milking, self.cows)) + sorted(
            list(filter(lambda cow: cow.is_milking, self.cows)), key=lambda cow: cow.days_in_milk
        )

    def _group_pens_by_animal_combination(self, all_pens: list[Pen]) -> dict[AnimalCombination, list[Pen]]:
        """
        Group a list of pens by animal combination.

        Parameters
        ----------
        all_pens : List[Pen]
            List of pens to group by animal combination.

        Returns
        -------
        Dict[AnimalCombination, List[Pen]]
            Dictionary of pens grouped by animal combination.

        """

        pen_group_by_animal_combination = defaultdict(list)
        for pen in all_pens:
            pen_group_by_animal_combination[pen.animal_combination].append(pen)
        return pen_group_by_animal_combination

    def _create_additional_pens_for_potential_space_shortage(
        self,
        num_animals: int,
        pens: list[Pen],
        animal_combination: AnimalCombination,
        start_pen_id: int = 0,
    ) -> list[Pen]:
        """
        Create a list of additional pens to accommodate potential animal space shortage.

        This method defines the first pen in the pens list as the 'reference' pen, which means that it uses those
        attributes as a template for the creation of new pens. This assumes the incoming pen list is uniform, as they
        are the same AnimalCombination.

        Parameters
        ----------
        num_animals : int
            The total number of animals to be accommodated.
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

        animal_space_shortage = self._calculate_animal_space_shortage(num_animals=num_animals, pens=pens)
        additional_pens: list[Pen] = []

        if animal_space_shortage > 0:
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
        >>> AnimalManager._calc_max_animal_spaces_per_pen(num_stalls=10, max_stocking_density=1.5)
        15
        >>> AnimalManager._calc_max_animal_spaces_per_pen(num_stalls=5, max_stocking_density=2.0)
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

    def plan_animal_allocation(self, num_animals: int, max_spaces_in_pens: list[int]) -> list[int]:
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
        >>> AnimalManager.plan_animal_allocation(num_animals=90, max_spaces_in_pens=[50, 30, 20])
        [45, 27, 18]

        >>> AnimalManager.plan_animal_allocation(num_animals=70, max_spaces_in_pens=[50, 30, 20])
        [35, 21, 14]

        >>> AnimalManager.plan_animal_allocation(num_animals=47, max_spaces_in_pens=[50, 30, 20])
        [22, 15, 10]

        """
        num_pens_for_combination = len(max_spaces_in_pens)
        overall_density = self._calculate_density(num_animals=num_animals, num_spaces=sum(max_spaces_in_pens))

        if overall_density > 1.0:
            raise ValueError("The number of animals cannot exceed the total number of spaces.")

        num_animals_in_pens = [0] * num_pens_for_combination
        allocation_limits = [math.ceil(overall_density * max_spaces) for max_spaces in max_spaces_in_pens]
        # Sort pens by allocation limit, then by index
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

    def execute_allocation_plan(
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
        allocation_plan : List[int]
            A list of integers representing the number of animals to be allocated to each pen.
            The length of the allocation_plan list must match the number of pens in animal_pens.

        animals : List[Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]]
            A list of animals to be allocated among the pens.

        animal_pens : List[Pen]
            A list of Pen objects representing the pens to which animals will be allocated.

        Returns
        -------
        None

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
            animal_combination = animal_pens[i].animal_combination
            animal_pens[i].update_animals(animals[:count], animal_combination)
            animals = animals[count:]

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

        Returns
        -------
        None

        """
        allocation_plan = self.plan_animal_allocation(
            num_animals=len(animals),
            max_spaces_in_pens=[
                self._calculate_max_animal_spaces_per_pen(pen.num_stalls, pen.max_stocking_density) for pen in pens
            ],
        )

        self.execute_allocation_plan(
            allocation_plan=allocation_plan,
            animals=animals,
            animal_pens=pens,
        )

    def fully_update_animal_to_pen_id_map(self) -> None:
        """
        Updates the entire animal_to_pen_id_map dictionary so that each animal's ID is
        associated with the pen that animal is in.
        """
        for pen in self.all_pens:
            animals_in_pen = pen.animals_in_pen
            for animal_id in animals_in_pen:
                self.animal_to_pen_id_map[animal_id] = pen.id

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
                    om.add_warning(
                        f"invalid_{key}_warning",
                        f"Warning: simulate_animals is false, but {key} is not.",
                        info_map,
                    )
                    counter += 1
            om.add_log(
                "num_warnings_associated_with_simulate_animals",
                f"{counter} warnings were associated with simulate_animals",
                info_map,
            )
        else:
            om.add_log("simulate_animals_flag", "simulate_animals is true", info_map)

    def gather_pen_history(self, animal_type_list: list[Animal], simulation_day: int) -> None:
        """
        Updates pen history data for a given animal type.

        Checks the current pen ID and pen composition of all animals for a given animal class, and then updates the
        pen history for that type using the update_pen_history() method.

        Parameters
        ----------
        animal_type_list : List[Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]]
            List of animals.
        """
        for animal in animal_type_list:
            current_pen_id = self.animal_to_pen_id_map[animal.id]
            classes_in_pen = self.all_pens[current_pen_id].animal_types_in_pen
            animal.update_pen_history(current_pen_id, simulation_day, classes_in_pen)

    def record_pen_history(self, simulation_day: int) -> None:
        """
        Records the pen history of all the animals.
        """
        self.gather_pen_history(self.calves, simulation_day)
        self.gather_pen_history(self.heiferIs, simulation_day)
        self.gather_pen_history(self.heiferIIs, simulation_day)
        self.gather_pen_history(self.heiferIIIs, simulation_day)
        self.gather_pen_history(self.cows, simulation_day)

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

        Returns: True if today is the day a new ration has to be formulated,
                False otherwise.
        """
        return (
            simulation_day % self.formulation_interval == 1
            or self.formulation_interval == 1
            or simulation_day == 0
        )

    def reformulate_ration_single_pen(self, pen: Pen, current_temperature: float, feed: Feed) -> None:
        """
        Reformulates ration for a single pen.

        Parameters
        ----------
        pen : Pen
            Pen that requires ration reformulation.
        current_temperature : float
            Current temperature.
        """
        pass

    def update_herd_statistics(self) -> None:
        (
            self.herd_statistics.calf_num,
            self.herd_statistics.heiferI_num,
            self.herd_statistics.heiferII_num,
            self.herd_statistics.heiferIII_num,
            self.herd_statistics.cow_num,
        ) = (
            len(self.calves), len(self.heiferIs), len(self.heiferIIs), len(self.heiferIIIs), len(self.cows)
        )
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
        """Calculates percentage of each animal class in the herd.

        When the total number of animals is 0, it is assumed that the count of
        each animal class has already been set to or initialized with 0.

        Args:
            total_animal_num: The total number of animals in the herd.

        """
        denominator = sum([len(self.calves), len(self.heiferIs), len(self.heiferIIs), len(self.heiferIIIs),
                           len(self.cows)])
        denominator = denominator if denominator > 0 else 1
        pc = Utility.percent_calculator(denominator)
        self.herd_statistics.calf_percent = pc(self.herd_statistics.calf_num)
        self.herd_statistics.heiferI_percent = pc(self.herd_statistics.heiferI_num)
        self.herd_statistics.heiferII_percent = pc(self.herd_statistics.heiferII_num)
        self.herd_statistics.heiferIII_percent = pc(self.herd_statistics.heiferIII_num)
        self.herd_statistics.cow_percent = pc(self.herd_statistics.cow_num)

    def _calculate_cow_percentages(self) -> None:
        """Calculates percentages of different kinds of cows"""
        denominator = self.herd_statistics.cow_num if self.herd_statistics.cow_num > 0 else 1
        pc = Utility.percent_calculator(denominator)
        self.herd_statistics.dry_cow_percent = pc(self.herd_statistics.dry_cow_num)
        self.herd_statistics.milking_cow_percent = pc(self.herd_statistics.milking_cow_num)
        self.herd_statistics.preg_cow_percent = pc(self.herd_statistics.preg_cow_num)
        self.herd_statistics.non_preg_cow_percent = pc(self.herd_statistics.open_cow_num)

    def _calculate_cull_reason_stats_percent(self) -> None:
        """Calculates the percentage of culled cows for each cull reason."""
        denominator = self.herd_statistics.cow_herd_exit_num if self.herd_statistics.cow_herd_exit_num > 0 else 1
        pc = Utility.percent_calculator(denominator)
        for cull_reason in self.herd_statistics.cull_reason_stats:
            self.herd_statistics.cull_reason_stats_percent[cull_reason] = pc(
                self.herd_statistics.cull_reason_stats[cull_reason])

    def _update_cow_parity_statistics(self) -> None:
        """Calculates the percentage of cows for each parity number."""
        denominator = self.herd_statistics.cow_num if self.herd_statistics.cow_num > 0 else 1
        parity_1_cows = [cow for cow in self.cows if cow.reproduction.calves == 1]
        parity_2_cows = [cow for cow in self.cows if cow.reproduction.calves == 2]
        parity_3_cows = [cow for cow in self.cows if cow.reproduction.calves == 3]
        parity_greater_than_3_cows = [cow for cow in self.cows if cow.reproduction.calves > 3]
        self.herd_statistics.num_cow_for_parity = {
            "1": len(parity_1_cows),
            "2": len(parity_2_cows),
            "3": len(parity_3_cows),
            "greater_than_3": len(parity_greater_than_3_cows)
        }
        self.herd_statistics.avg_age_for_parity = {
            "1": sum([cow.days_born for cow in parity_1_cows]) / denominator,
            "2": sum([cow.days_born for cow in parity_2_cows]) / denominator,
            "3": sum([cow.days_born for cow in parity_3_cows]) / denominator,
            "greater_than_3": sum([cow.days_born for cow in parity_greater_than_3_cows]) / denominator
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
                    sum(parity_greater_than_3_calving_age) / len(parity_greater_than_3_calving_age)
            ) if len(parity_greater_than_3_calving_age) > 0 else 0,
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
            calving_to_pregnancy_time for calving_to_pregnancy_time in parity_1_calving_to_pregnancy_time
            if calving_to_pregnancy_time > 0
        ]
        parity_2_calving_to_pregnancy_time = [
            calving_to_pregnancy_time for calving_to_pregnancy_time in parity_2_calving_to_pregnancy_time
            if calving_to_pregnancy_time > 0
        ]
        parity_3_calving_to_pregnancy_time = [
            calving_to_pregnancy_time for calving_to_pregnancy_time in parity_3_calving_to_pregnancy_time
            if calving_to_pregnancy_time > 0
        ]
        parity_greater_than_3_calving_to_pregnancy_time = [
            calving_to_pregnancy_time for calving_to_pregnancy_time in parity_greater_than_3_calving_to_pregnancy_time
            if calving_to_pregnancy_time > 0
        ]
        self.herd_statistics.avg_calving_to_preg_time = {
            "1": (
                    sum(parity_1_calving_to_pregnancy_time) / len(parity_1_calving_to_pregnancy_time)
            ) if len(parity_1_calving_to_pregnancy_time) > 0 else 0,
            "2": (
                    sum(parity_2_calving_to_pregnancy_time) / len(parity_2_calving_to_pregnancy_time)
            ) if len(parity_2_calving_to_pregnancy_time) > 0 else 0,
            "3": (
                    sum(parity_3_calving_to_pregnancy_time) / len(parity_3_calving_to_pregnancy_time)
            ) if len(parity_3_calving_to_pregnancy_time) > 0 else 0,
            "greater_than_3": (
                    sum(
                        parity_greater_than_3_calving_to_pregnancy_time
                    ) / len(parity_greater_than_3_calving_to_pregnancy_time)
            ) if len(parity_greater_than_3_calving_to_pregnancy_time) > 0 else 0,
        }

        pc = Utility.percent_calculator(denominator)
        for parity in self.herd_statistics.num_cow_for_parity:
            self.herd_statistics.percent_cow_for_parity[parity] = pc(self.herd_statistics.num_cow_for_parity[parity])

    def _update_cow_milking_statistics(self) -> None:
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

        self.herd_statistics.avg_days_in_milk = (sum(
            [cow.days_in_milk for cow in lactating_cows]) / len(lactating_cows)) if len(lactating_cows) > 0 else 0


        self.herd_statistics.daily_milk_production = sum(cow.milk_production.daily_milk_produced for cow in self.cows)
        self.herd_statistics.herd_milk_fat_kg = sum(cow.milk_production.fat_content for cow in lactating_cows)
        self.herd_statistics.herd_milk_fat_percent = (
                                                             self.herd_statistics.herd_milk_fat_kg /
                                                             self.herd_statistics.daily_milk_production
                                                     ) * 100
        self.herd_statistics.herd_milk_protein_kg = sum(cow.milk_production.true_protein_content for cow in lactating_cows)
        self.herd_statistics.herd_milk_protein_percent = (
                                                                 self.herd_statistics.herd_milk_protein_kg /
                                                                 self.herd_statistics.daily_milk_production
                                                         ) * 100

        dry_cows_daily_milk_production = sum(cow.milk_production.daily_milk_produced for cow in dry_cows)
        dry_cows_milk_fat_kg = sum(cow.milk_production.fat_content for cow in dry_cows)
        dry_cows_milk_protein_kg = sum(cow.milk_production.true_protein_content for cow in dry_cows)
        if dry_cows_daily_milk_production > 0 or dry_cows_milk_fat_kg > 0 or dry_cows_milk_protein_kg > 0:
            om.add_error("Dry cow milking error", "Unexpected milking from dry cows", info_map)
            raise ValueError("Unexpected milking from dry cows")


    def _update_cow_pregnancy_statistics(self) -> None:
        pregnant_cows: list[Animal] = [cow for cow in self.cows if cow.is_pregnant]
        self.herd_statistics.preg_cow_num = len(pregnant_cows)
        self.herd_statistics.open_cow_num = len(self.cows) - len(pregnant_cows)

        self.herd_statistics.avg_days_in_preg = (sum(
            [cow.days_in_pregnancy for cow in pregnant_cows]) / len(pregnant_cows)) if len(pregnant_cows) > 0 else 0

    def _update_sold_and_died_cows(self, sold_and_died_cows: list[Animal]) -> None:
        sum_cow_culling_age = self.herd_statistics.avg_cow_culling_age * self.herd_statistics.cow_herd_exit_num + sum(
            [cow.days_born for cow in sold_and_died_cows]
        )
        self.herd_statistics.cow_herd_exit_num += len(sold_and_died_cows)
        self.herd_statistics.avg_cow_culling_age = (
                sum_cow_culling_age / self.herd_statistics.cow_herd_exit_num
        ) if self.herd_statistics.cow_herd_exit_num > 0 else 0

        self.herd_statistics.sold_and_died_cows_info += [
            {
                "id": cow.id,
                "animal_type": cow.animal_type,
                "sold_at_day": cow.sold_at_day,
                "body_weight": cow.body_weight,
                "cull_reason": cow.cull_reason,
                "days_in_milk": cow.days_in_milk,
                "parity": cow.reproduction.calves,
            } for cow in sold_and_died_cows
        ]
        for cull_reason in self.herd_statistics.cull_reason_stats.keys():
            self.herd_statistics.cull_reason_stats[cull_reason] += len([cow for cow in sold_and_died_cows if
                                                                        cow.cull_reason == cull_reason])

        sold_cows: list[Animal] = [cow for cow in sold_and_died_cows if cow.cull_reason != animal_constants.DEATH_CULL]
        self.herd_statistics.sold_cows_info += [
            {
                "id": cow.id,
                "animal_type": cow.animal_type,
                "sold_at_day": cow.sold_at_day,
                "body_weight": cow.body_weight,
                "cull_reason": cow.cull_reason,
                "days_in_milk": cow.days_in_milk,
                "parity": cow.reproduction.calves,
            } for cow in sold_cows
        ]
        self.herd_statistics.sold_cow_num += len(sold_cows)

        for parity in self.herd_statistics.parity_culling_stats_range.keys():
            if parity == "greater_than_3":
                culled_cows_with_current_parity = [cow for cow in sold_and_died_cows if cow.reproduction.calves > 3]
            else:
                current_parity = int(parity)
                culled_cows_with_current_parity = [cow for cow in sold_and_died_cows
                                                   if cow.reproduction.calves == current_parity]
            self.herd_statistics.parity_culling_stats_range[parity] += len(culled_cows_with_current_parity)
        self._calculate_cull_reason_stats_percent()

    def _update_sold_heiferIIs(self, sold_heiferIIs: list[Animal]) -> None:
        sum_heifer_culling_age = (
            self.herd_statistics.avg_heifer_culling_age * self.herd_statistics.cow_herd_exit_num
        ) + sum([heiferII.days_born for heiferII in sold_heiferIIs])

        self.herd_statistics.sold_heiferII_num += len(sold_heiferIIs)
        self.herd_statistics.sold_heiferIIs_info += [
                {
                    "id": heiferII.id,
                    "animal_type": heiferII.animal_type,
                    "sold_at_day": heiferII.sold_at_day,
                    "body_weight": heiferII.body_weight,
                    "cull_reason": "NA",
                    "days_in_milk": "NA",
                    "parity": "NA",
                }
            for heiferII in sold_heiferIIs]
        self.herd_statistics.avg_heifer_culling_age = (
                sum_heifer_culling_age / self.herd_statistics.sold_heiferII_num
        ) if self.herd_statistics.sold_heiferII_num > 0 else 0

    def _update_sold_newborn_calves(self, sold_newborn_calves: list[Animal]) -> None:
        self.herd_statistics.sold_calf_num += len(sold_newborn_calves)
        self.herd_statistics.sold_calves_info += [
                {
                    "id": calf.id,
                    "animal_type": calf.animal_type,
                    "sold_at_day": calf.sold_at_day,
                    "body_weight": calf.body_weight,
                    "cull_reason": "NA",
                    "days_in_milk": "NA",
                    "parity": "NA",
                }
            for calf in sold_newborn_calves]

    def _update_cow_reproduction_statistics(self) -> None:
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
        self.herd_statistics.ai_num = sum(
            [cow.reproduction.reproduction_statistics.AI_times for cow in self.cows]
        )
        self.herd_statistics.avg_CI = sum(
            [cow.reproduction.calving_interval for cow in self.cows]
        ) / len(self.cows) if len(self.cows) > 0 else 0
        self.herd_statistics.avg_CI_for_calving = sum(
            [cow.reproduction.calving_interval for cow in self.cows]
        ) / len(self.cows) if len(self.cows) > 0 else 0

    def _update_heifer_reproduction_statistics(self) -> None:
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
        self.herd_statistics.ed_period_h = sum(
            [heiferII.reproduction.reproduction_statistics.ED_days for heiferII in self.heiferIIs]
        )
        self.herd_statistics.avg_breeding_to_preg_time = sum(
            [heiferII.reproduction.breeding_to_preg_time for heiferII in self.heiferIIs if heiferII.is_pregnant]
        ) / len(self.heiferIIs) if len(self.heiferIIs) > 0 else 0

    def _update_average_mature_body_weight(self) -> None:
        all_animals: list[Animal] = self.calves + self.heiferIs + self.heiferIIs + self.heiferIIIs + self.cows
        self.herd_statistics.avg_mature_body_weight = sum(
            [animal.mature_body_weight for animal in all_animals]) / len(all_animals) if len(all_animals) > 0 else 0

    def _update_average_cow_body_weight(self) -> None:
        self.herd_statistics.avg_cow_body_weight = sum(
            [cow.body_weight for cow in self.cows]
        ) / len(self.cows) if len(self.cows) > 0 else 0

    def _update_average_cow_parity(self) -> None:
        self.herd_statistics.avg_parity_num = sum(
            [cow.reproduction.calves for cow in self.cows]
        ) / len(self.cows) if len(self.cows) > 0 else 0
