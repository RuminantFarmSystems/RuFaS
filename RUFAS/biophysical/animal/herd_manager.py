from typing import Any, Optional

from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_grouping_scenarios import AnimalGroupingScenario
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.data_types.animal_enums import AnimalStatus
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.daily_routines_output import DailyRoutinesOutput
from RUFAS.biophysical.animal.pen import Pen
from RUFAS.biophysical.feed.feed import Feed
from RUFAS.enums import AnimalCombination
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.purchased_feed_emissions_estimator import PurchasedFeedEmissionsEstimator
from RUFAS.time import Time
from RUFAS.weather import Weather
from tests.animal_module_tests.test_pen import calf_daily_growth_values

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
        data: dict[str, Any],
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
        AnimalConfig.initialize_animal_config()

        # how do we set lactation curve
        AnimalBase.setup_lactation_curve_parameters(time)

        # if False, there are no animals being simulated on the farm
        self.simulate_animals = config_data.get("simulate_animals", True)

        # list of all the animals in the simulation
        self.calves: list[Animal] = []
        self.heiferIs: list[Animal] = []
        self.heiferIIs: list[Animal] = []
        self.heiferIIIs: list[Animal] = []
        self.cows: list[Animal] = []
        self.heifers_sold: list[Animal] = []
        self.cows_culled: list[Animal] = []

        # list of all the pens on the farm
        self.all_pens: list[Pen] = []

        # dictionary: key is animal ID, value is the pen ID that animal is in
        self.animal_to_pen_id_map = {}

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
        self.p_conc = {"calf": 0, "heiferI": 0, "heiferII": 0, "heiferIII": 0, "cow": 0}

        self.phosphorus_concentration_by_animal_class = {
            animal_type: 0.0 for animal_type in [Calf, HeiferI, HeiferII, HeiferIII, Cow]
        }

        self.housing = data["housing"]
        self.pasture_concentrate = data["pasture_concentrate"]

        udrm = udr.UserDefinedRationManager()
        self.ration_user_input = data["ration"]["user_input"]
        udrm.use_user_defined_ration = self.ration_user_input

        # how often a ration is calculated, days
        self.formulation_interval = data["ration"]["formulation_interval"]

        self.init_pens(data["pen_information"], data["manure_management_scenarios"])

        if self.simulate_animals:
            self.init_animals(data["herd_information"])

            self.init_nutrient_rqmts(weather, time, feed)

            self.allocate_animals_to_pens()

        self._print_animal_num_warnings(data["herd_information"])

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
            AnimalType.LAC_COW: self.cows,
            AnimalType.DRY_COW: self.cows,
        }

    def daily_routines(self, feed: Feed, weather: Weather, time: Time) -> None:
        current_conditions = weather.get_current_day_conditions(time)
        current_temperature = current_conditions.mean_air_temperature

        graduated_animals: list[Animal] = []
        newborn_calves: list[Animal] = []
        removed_animals: list[Animal] = []

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
                newborn_calf = Animal(**cow_routines_output.animal_values)
                newborn_calves.append(newborn_calf)
            elif cow_routines_output.animal_status in [
                AnimalStatus.DEAD, AnimalStatus.CULLED, AnimalStatus.SOLD
            ]:
                removed_animals.append(cow)

        self._handle_graduated_animals(graduated_animals, feed, current_temperature)
        self._handle_newly_added_animals(newborn_calves, feed, current_temperature)
        for removed_animal in removed_animals:
            self._remove_animal_from_pen_and_id_map(removed_animal)

    # -------------------------#
    def init_pens(self, all_pen_data: list, manure_management_scenarios: dict[str, Any]) -> None:
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
            pen_data["pen_id"] = pen_data.pop("id")
            pen_data["animal_combination"] = AnimalCombination[pen_data.pop("animal_combination")]

            manure_management_scenario_id = pen_data.pop("manure_management_scenario_id")
            manure_management_scenario = [
                scenario
                for scenario in manure_management_scenarios
                if scenario["scenario_id"] == manure_management_scenario_id
            ][0]
            pen_data["bedding_type"] = manure_management_scenario["bedding_type"]
            pen_data["manure_handling"] = manure_management_scenario["manure_handler"]
            pen_data["manure_separator"] = manure_management_scenario["manure_separator"]
            pen_data["manure_separator_after_digestion"] = manure_management_scenario[
                "manure_separator_after_digestion"
            ]
            pen_data["manure_storage"] = manure_management_scenario["manure_treatment"]

            pen = Pen(**pen_data)

            self.all_pens.append(pen)

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
        available_feeds = ration_driver.AvailableFeeds()
        available_feeds.feed_nutrients(feed)
        if not pen.is_populated:
            return
        pen.subset_class_feeds(feed)
        pen_specific_feed_data = available_feeds.get_feed_data_from_feed_ids(pen.allocated_feeds)

        ration_per_animal: Dict[str, float | str] = {}
        ration_vals = {}

        while "status" not in ration_per_animal or ration_per_animal["status"].lower() != "optimal":
            if pen.animal_combination == AnimalCombination.CALF:
                ration_per_animal = CalfRationManager.optimize()
                ration_vals = {"ME_total": 0}
            else:
                ration_per_animal, ration_vals = RationManager.formulate_ration(
                    pen, pen_specific_feed_data, self.ANIMAL_GROUPING_SCENARIO, self.simulation_day
                )

        # recording ration nutrition information in pen
        nutrient_amount, nutrient_conc = RationReporter.report_ration(ration_per_animal, feed.available_feeds)
        pen.ration_nutrient_amount = nutrient_amount
        pen.ration_nutrient_conc = nutrient_conc
        pen.MEdiet = ration_vals["ME_total"]
        pen.dry_matter_intake = nutrient_amount["dm"]

        ration_report = {}
        ration_report["nutrient_amount"] = nutrient_amount
        ration_report["nutrient_conc"] = nutrient_conc

        for animal in list(pen.animals_in_pen.values()):
            animal.set_ration(ration_per_animal, nutrient_amount["dm"])
            animal.set_p_intake(nutrient_amount["phosphorus"], nutrient_conc["phosphorus"])

        ration_per_pen = {}
        num_animals = len(pen.animals_in_pen)
        for key in ration_per_animal:
            if key == "status":
                ration_per_pen[key] = ration_per_animal[key]
            else:
                ration_per_pen[key] = ration_per_animal[key] * num_animals

        pen.ration = ration_per_pen
        pen.ration_per_animal = ration_per_animal

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
        self.all_pens[pen_id].remove_animal(animal.id)
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
        pen_with_min_stocking_density.add_animal(
            animal,
            self.ANIMAL_GROUPING_SCENARIO,
            feed,
            current_temperature,
            self.phosphorus_concentration_by_animal_class[type(animal)],
        )
        self.animal_to_pen_id_map[animal.id] = pen_with_min_stocking_density.id