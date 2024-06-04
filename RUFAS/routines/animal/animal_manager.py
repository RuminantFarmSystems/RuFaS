from __future__ import annotations

import collections
import math
from statistics import mean
from typing import Any, Dict, Tuple, List, Set, Union, Optional

from RUFAS.units import MeasurementUnits
from RUFAS.general_constants import GeneralConstants
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.animal_grouping_scenarios import AnimalGroupingScenario
from RUFAS.routines.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.routines.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.routines.animal.animal_types import AnimalType
from RUFAS.routines.animal.life_cycle import animal_constants
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.life_cycle.life_cycle import LifeCycleManager
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.animal.ration import ration_driver as ration_driver
from RUFAS.routines.animal.ration.calf_ration import CalfRationManager
from RUFAS.routines.animal.ration.ration_driver import RationManager
from RUFAS.routines.animal.purchased_feed_emissions_estimator import (
    PurchasedFeedEmissionsEstimator,
)

from RUFAS.routines.animal.ration import user_defined_ration as udr
from RUFAS.routines.animal.ration.ration_driver import RationReporter
from RUFAS.routines.feed.feed import Feed
from RUFAS.time import Time
from RUFAS.weather import Weather
from ...shared_structures.animal_combinations import AnimalCombination
from ...shared_structures.pen_manure_data import PenManureData

im = InputManager()
om = OutputManager()


class AnimalManager:
    """
    Manages all animal routines (i.e. calling daily updates, allocating animals
    to pens, etc). Stores a list of all animals and pens in the simulation as
    well as an instance of the LifeCycleManager class in order to update the
    animals' life cycles.
    """

    DEFAULT_NUM_STALLS_BY_COMBINATION = {
        AnimalCombination.CALF: AnimalModuleConstants.DEFAULT_NUM_STALLS_FOR_CALF_PEN,
        AnimalCombination.GROWING: AnimalModuleConstants.DEFAULT_NUM_STALLS_FOR_GROWING_PEN,
        AnimalCombination.CLOSE_UP: AnimalModuleConstants.DEFAULT_NUM_STALLS_FOR_CLOSE_UP_PEN,
        AnimalCombination.LAC_COW: AnimalModuleConstants.DEFAULT_NUM_STALLS_FOR_LAC_COW_PEN,
        AnimalCombination.GROWING_AND_CLOSE_UP: AnimalModuleConstants.DEFAULT_NUM_STALLS_FOR_GROWING_AND_CLOSE_UP_PEN,
    }

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

    @staticmethod
    def get_animal_config(data):
        config = {}
        config.update(data["management_decisions"])
        config.update(data["farm_level"]["calf"])
        config.update(data["farm_level"]["repro"])
        config.update(data["farm_level"]["bodyweight"])
        config.update(data["from_literature"]["repro"])
        config.update(data["from_literature"]["milking"])
        config.update(data["from_literature"]["culling"])
        config.update(data["from_literature"]["life_cycle"])
        return config

    def __init__(
        self,
        data: Dict[str, Any],
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
        config_data: Dict[str, Any] = im.get_data("config")

        # simulation length, days
        self.sim_length = time.simulation_length

        # day in the simulation
        self.simulation_day = 1

        animal_config = self.get_animal_config(data["animal_config"])

        # instance of LifeCycleManager class
        self.life_cycle_manager = LifeCycleManager(animal_config)

        AnimalBase.set_config(animal_config)
        AnimalBase.set_nutrient_list(feed.nutrient_rqmts)

        # if False, there are no animals being simulated on the farm
        self.simulate_animals = config_data.get("simulate_animals", True)

        # list of all the animals in the simulation
        self.calves = []
        self.heiferIs = []
        self.heiferIIs = []
        self.heiferIIIs = []
        self.cows = []
        self.heifers_sold = []
        self.cows_culled = []

        # list of all the pens on the farm
        self.all_pens: List[Pen] = []

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

        # housing type: barn or pasture
        self.housing = data["housing"]

        # concentrate supplementation when farming type is "pasture", kg
        self.pasture_concentrate = data["pasture_concentrate"]

        udrm = udr.UserDefinedRationManager()
        self.ration_user_input = data["ration"]["user_input"]
        udrm.is_udr = self.ration_user_input

        # how often a ration is calculated, days
        self.formulation_interval = data["ration"]["formulation_interval"]

        self.methane_model = data["methane_model"]
        self.methane_mitigation_method = data["methane_mitigation"]["methane_mitigation_method"]
        self.methane_mitigation_additive_amount = data["methane_mitigation"]["methane_mitigation_additive_amount"]

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
    def animals_by_type(self):
        return {
            Calf: self.calves,
            HeiferI: self.heiferIs,
            HeiferII: self.heiferIIs,
            HeiferIII: self.heiferIIIs,
            Cow: self.cows,
        }

    def init_pens(self, all_pen_data: list, manure_management_scenarios: Dict[str, Any]) -> None:
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

    def init_animals(self, herd_data: Dict[str, Any]) -> None:
        """
        Populates the list of animals with the information from the
        input JSON file: constructs the calves, heiferI's, heiferII's,
        heiferIII's, and cows (the desired amounts of each is specified by
        @data), then calls life_cycle_manager's initialize_herd() with those
        numbers to create instances of the animals. The nutrient requirements
        are calculated and the animals are allocated to pens.

        Parameters
        ----------
        herd_data: Dict[str, Any]
            A dictionary containing information about the herd.
        """

        (
            self.calves,
            self.heiferIs,
            self.heiferIIs,
            self.heiferIIIs,
            self.cows,
        ) = self.life_cycle_manager.initialize_herd(herd_data)

    def _print_animal_num_warnings(self, herd_data: Dict[str, Any]) -> None:
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

    def init_nutrient_rqmts(self, weather: Weather, time: Time, feed: Feed) -> None:
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

        # average vertical & horizontal distance (VD, HD) of pens to the
        # milking parlor
        # avg_VD_parlor, avg_HD_parlor = self.avg_pen_dist()
        current_conditions = weather.get_current_day_conditions(time)
        current_temperature = current_conditions.mean_air_temperature
        for calf in self.calves:
            calf.calc_nutrient_rqmts(feed, current_temperature)
            calf.p_animal = 0.0072 * calf.body_weight * 1000

        for heiferI in self.heiferIs:
            heiferI.set_nutrient_rqmts(current_temperature, self.ANIMAL_GROUPING_SCENARIO)
            heiferI.p_animal = 0.0072 * heiferI.body_weight * 1000

        for heiferII in self.heiferIIs:
            heiferII.set_nutrient_rqmts(current_temperature, self.ANIMAL_GROUPING_SCENARIO)
            heiferII.p_animal = 0.0072 * heiferII.body_weight * 1000

        for heiferIII in self.heiferIIIs:
            heiferIII.set_nutrient_rqmts(current_temperature, self.ANIMAL_GROUPING_SCENARIO)
            heiferIII.p_animal = 0.0072 * heiferIII.body_weight * 1000

        for cow in self.cows:
            cow.set_nutrient_rqmts(self.ANIMAL_GROUPING_SCENARIO)
            cow.p_animal = 0.0072 * cow.body_weight * 1000

    def avg_pen_dist(self) -> Tuple[float, float]:
        """
        Calculates the average distance from a pen to the milking parlor.

        Returns
        -------
        Tuple : (average vertical distance from milking parlor, average horizontal distance from milking parlor)

        """

        return mean(pen.vertical_dist_to_parlor for pen in self.all_pens), mean(
            pen.horizontal_dist_to_parlor for pen in self.all_pens
        )

    def calc_nutrient_rqmts(self, feed: Feed, current_temperature: float) -> None:
        """
        Calls each animal's method to calculate its nutrient requirements.

        Parameters
        ----------
        feed : Feed
            Instance of the Feed class.
        current_temperature : float
            The temperature on the current day.

        """
        for calf in self.calves:
            calf.calc_nutrient_rqmts(feed, current_temperature)

        for heiferI in self.heiferIs:
            latest_pen = heiferI.pen_history[-1].pen
            heiferI.set_nutrient_rqmts(
                current_temperature,
                self.ANIMAL_GROUPING_SCENARIO,
                nutrient_conc=self.all_pens[latest_pen].ration_nutrient_conc,
                metabolizable_energy=self.all_pens[latest_pen].MEdiet,
                previous_DMI=self.all_pens[latest_pen].dry_matter_intake,
            )

        for heiferII in self.heiferIIs:
            latest_pen = heiferII.pen_history[-1].pen
            heiferII.set_nutrient_rqmts(
                current_temperature,
                self.ANIMAL_GROUPING_SCENARIO,
                nutrient_conc=self.all_pens[latest_pen].ration_nutrient_conc,
                metabolizable_energy=self.all_pens[latest_pen].MEdiet,
                previous_DMI=self.all_pens[latest_pen].dry_matter_intake,
            )

        for heiferIII in self.heiferIIIs:
            latest_pen = heiferIII.pen_history[-1].pen
            heiferIII.set_nutrient_rqmts(
                current_temperature,
                self.ANIMAL_GROUPING_SCENARIO,
                nutrient_conc=self.all_pens[latest_pen].ration_nutrient_conc,
                metabolizable_energy=self.all_pens[latest_pen].MEdiet,
                previous_DMI=self.all_pens[latest_pen].dry_matter_intake,
            )

        for cow in self.cows:
            latest_pen = cow.pen_history[-1].pen
            cow.set_nutrient_rqmts(
                self.ANIMAL_GROUPING_SCENARIO,
                nutrient_conc=self.all_pens[latest_pen].ration_nutrient_conc,
            )

    def reset_milk_production_reduction(self) -> None:
        """
        Resets reduction value for milk production to 0.0 for all animals in all pens

        The milk_production_reduction attribute is a value generated in ration_driver.py,
            in cases where a ration cannot be formulated such that it meets animal requirements

        """
        for pen in self.all_pens:
            if pen.animal_combination.name == "LAC_COW" or pen.animal_combination.name == "CLOSE_UP":
                for animal in list(pen.animals_in_pen.values()):
                    animal.milk_production_reduction = 0.0

    def fully_update_animal_to_pen_id_map(self) -> None:
        """
        Updates the entire animal_to_pen_id_map dictionary so that each animal's ID is
        associated with the pen that animal is in.
        """
        for pen in self.all_pens:
            animals_in_pen = pen.animals_in_pen
            for animal_id in animals_in_pen:
                self.animal_to_pen_id_map[animal_id] = pen.id

    @classmethod
    def _get_dry_cows(cls, cows: List[Cow]) -> List[Cow]:
        """
        Return a list of dry cows from a list of cows.

        Here, a dry cow can be either far-off dry or close-up dry.

        Parameters
        ----------
        cows : List[Cow]
            List of cows to filter dry cows from.

        Returns
        -------
        List[Cow]
            List of dry cows.

        """

        return list(filter(lambda cow: cow.is_dry, cows))

    @classmethod
    def _get_lactating_cows(cls, cows: List[Cow]) -> List[Cow]:
        """
        Return a list of lactating cows from a list of cows.

        Parameters
        ----------
        cows : List[Cow]
            List of cows to filter lactating cows from.

        Returns
        -------
        List[Cow]
            List of lactating cows.

        """

        return list(filter(lambda cow: cow.is_lactating, cows))

    @classmethod
    def _group_pens_by_animal_combination(cls, all_pens: List[Pen]) -> Dict[AnimalCombination, List[Pen]]:
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

        pen_group_by_animal_combination = collections.defaultdict(list)
        for pen in all_pens:
            pen_group_by_animal_combination[pen.animal_combination].append(pen)
        return pen_group_by_animal_combination

    @classmethod
    def _calc_max_animal_spaces_per_pen(cls, num_stalls: int, max_stocking_density: float) -> int:
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

    @classmethod
    def _calc_animal_space_shortage(cls, num_animals: int, pens: List[Pen]) -> int:
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
            max_animal_spaces += cls._calc_max_animal_spaces_per_pen(pen.num_stalls, pen.max_stocking_density)
        return num_animals - max_animal_spaces

    @classmethod
    def _create_duplicate_pen(
        cls,
        pen_id: int,
        animal_combination: AnimalCombination,
        num_stalls: int,
        max_stocking_density: float,
        reference_pen: Pen,
    ) -> Pen:
        """
        Duplicate a Pen object using a handful of parameters and a reference Pen.

        Parameters
        ----------
        pen_id : int
            The unique identifier for the pen.
        animal_combination : AnimalCombination
            The animal combination for the pen.
        num_stalls : int
            The number of stalls in the pen.
        max_stocking_density : float
            The maximum stocking density for the pen.
        reference_pen : Pen
            Pen object that has more animals than available space.

        Returns
        -------
        Pen
            A new Pen object with the specified parameters and duplicate values for other attributes of reference pen.

        """

        return Pen(
            pen_id=pen_id,
            pen_name=str(pen_id),
            vertical_dist_to_milking_parlor=reference_pen.vertical_dist_to_parlor,
            horizontal_dist_to_milking_parlor=reference_pen.horizontal_dist_to_parlor,
            number_of_stalls=num_stalls,
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

    def _create_additional_pens_for_potential_space_shortage(
        self,
        num_animals: int,
        pens: List[Pen],
        animal_combination: AnimalCombination,
        start_pen_id: int = 0,
    ) -> List[Pen]:
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

        animal_space_shortage = self._calc_animal_space_shortage(num_animals=num_animals, pens=pens)
        additional_pens: List[Pen] = []

        if animal_space_shortage > 0:
            reference_pen = pens[0]
            max_stocking_density = reference_pen.max_stocking_density
            num_stalls_custom_pen = int(math.ceil(animal_space_shortage * max_stocking_density))
            num_stalls_per_additional_pen = min(
                self.DEFAULT_NUM_STALLS_BY_COMBINATION[animal_combination], num_stalls_custom_pen
            )

            max_animal_spaces_per_additional_pen = self._calc_max_animal_spaces_per_pen(
                num_stalls=num_stalls_per_additional_pen, max_stocking_density=max_stocking_density
            )
            num_new_pens = math.ceil(animal_space_shortage / max_animal_spaces_per_additional_pen)
            for i in range(num_new_pens):
                additional_pens.append(
                    self._create_duplicate_pen(
                        pen_id=start_pen_id + i,
                        animal_combination=animal_combination,
                        num_stalls=num_stalls_per_additional_pen,
                        max_stocking_density=max_stocking_density,
                        reference_pen=reference_pen,
                    )
                )

        return additional_pens

    @classmethod
    def _calc_density(cls, num_animals: int, num_spaces: int) -> float:
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

    @classmethod
    def _allocate_animals_to_pens_helper(
        cls,
        animals: List[Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]],
        pens: List[Pen],
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

        allocation_plan = cls.plan_animal_allocation(
            num_animals=len(animals),
            max_spaces_in_pens=[
                cls._calc_max_animal_spaces_per_pen(pen.num_stalls, pen.max_stocking_density) for pen in pens
            ],
        )

        cls.execute_allocation_plan(
            allocation_plan=allocation_plan,
            animals=animals,
            animal_pens=pens,
        )

    @classmethod
    def execute_allocation_plan(
        cls,
        allocation_plan: List[int],
        animals: List[Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]],
        animal_pens: List[Pen],
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

    @classmethod
    def plan_animal_allocation(cls, num_animals: int, max_spaces_in_pens: List[int]) -> List[int]:
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
        overall_density = cls._calc_density(num_animals=num_animals, num_spaces=sum(max_spaces_in_pens))

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

    def allocate_animals_to_pens(self) -> None:
        """
        Allocate animals to pens based on the current animal population and the number of pens available.
        New default pens will be created if necessary. This method distributes the animals among the pens,
        ensuring that the animal density of each pen matches the overall density as closely as possible.

        Returns
        -------
        None

        """

        self._sort_animals_before_allocation()
        self.pens_by_animal_combination = self._group_pens_by_animal_combination(self.all_pens)
        animals_by_combination = collections.defaultdict(list)
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

    def _sort_animals_before_allocation(self) -> None:
        """
        Sort lactating cows by days in milk in increasing order.
        """
        self.cows = self._get_dry_cows(self.cows) + sorted(
            self._get_lactating_cows(self.cows), key=lambda cow: cow.days_in_milk
        )

    def clear_pens(self) -> None:
        """
        Removes animals from pens for re-allocation. This is part of the
        routines that happen every ration interval.
        """

        for pen in self.all_pens:
            pen.clear()

    def calc_manure_excretion(self, feed: Feed, methane_model: str) -> None:
        """
        Calls each animal's method to calculate manure excretion to find the
        total for each pen. This is part of the routines that happen every
        ration interval.

        Parameters
        ----------
        feed : Feed
            instance of the feed class
        methane_model : str
            Methane model used for methane emission calculations

        """
        for pen in self.all_pens:
            if pen.is_populated:
                pen.calc_manure(feed, methane_model)
            else:
                pen.reset_manure()

    def calc_avg_growth(self) -> None:
        """
        Calls each pen's method to calculate the average growth of animals in
        the pen. This is part of the routines that happen every
        ration interval.
        """

        for pen in self.all_pens:
            pen.calc_avg_growth()

    def sum_daily_milk(self, cows: List[Cow]) -> float:
        """
        sums the daily milk production across all cows

        Parameters
        ----------
        cows: List
            List of cows in the animal manager class.

        Returns
        -------
        float: The total milk produced in the herd (kg milk/day)
        """
        return sum(cow.estimated_daily_milk_produced for cow in cows)

    def gather_pen_history(self, animal_type_list: List[Calf | HeiferI | HeiferII | HeiferIII | Cow]) -> None:
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
            classes_in_pen = self.all_pens[current_pen_id].classes_in_pen
            animal.update_pen_history(current_pen_id, self.simulation_day, classes_in_pen)

    def collect_pen_manure_data(self) -> list[PenManureData]:
        """Returns the manure information from all pens in PenManureData."""
        return [pen.get_manure_data() for pen in self.all_pens]

    def record_pen_history(self) -> None:
        """
        Records the pen history of all the animals.
        """
        self.gather_pen_history(self.calves)
        self.gather_pen_history(self.heiferIs)
        self.gather_pen_history(self.heiferIIs)
        self.gather_pen_history(self.heiferIIIs)
        self.gather_pen_history(self.cows)

    def calc_p_rqmts(self) -> None:
        """
        Calls each pen's method to calculate each animal's phosphorus
        requirements. This method is called daily.

        """
        for pen in self.all_pens:
            if pen.is_populated:
                pen.call_p_rqmts()

    def daily_p_update(self) -> None:
        """
        Calls each pen's method to calculate each animal's daily phosphorus
        update. This method is called daily.
        """
        for pen in self.all_pens:
            if pen.is_populated:
                pen.daily_p_update()

    def end_ration_interval(self) -> bool:
        """
        Checks if a new ration should be formulated for the current simulation_day.

        Returns: True if today is the day a new ration has to be formulated,
                False otherwise.
        """
        return (
            self.simulation_day % self.formulation_interval == 1
            or self.formulation_interval == 1
            or self.simulation_day == 0
        )

    @classmethod
    def _calc_phosphorus_concentration(cls, animals: List[Calf | HeiferI | HeiferII | HeiferIII | Cow]) -> float:
        """
        Calculate the phosphorus concentration of a group of animals.

        Parameters
        ----------
        animals
            A list of animals.

        Returns
        -------
        float
            The phosphorus concentration of the group of animals.

        """

        if len(animals) == 0:
            return 0.0

        total_phosphorus = 0.0
        total_body_weight = 0.0
        for animal in animals:
            total_phosphorus += animal.p_animal * GeneralConstants.GRAMS_TO_KG
            total_body_weight += animal.body_weight

        return total_phosphorus / total_body_weight

    def _update_phosphorus_concentrations(self) -> None:
        """
        Update the phosphorus concentration for each animal type.

        Returns
        -------
        None

        """

        for animal_type in self.phosphorus_concentration_by_animal_class:
            animals = self.animals_by_type[animal_type]
            self.phosphorus_concentration_by_animal_class[animal_type] = self._calc_phosphorus_concentration(animals)

    def _calc_ration_at_interval(self, feed: Feed) -> None:
        """
        Calculate the ration for each pen at the given interval and update the
        ration for each animal in the pen.

        Notes
        -----
        It is important to set the variable `ration_per_animal` for each pen object. This forms the
        basis for scaling the ration for each pen based on the current number of animals in the pen.

        Parameters
        ----------
        feed
            Instance of the Feed class

        """
        available_feeds = ration_driver.AvailableFeeds()
        available_feeds.feed_nutrients(feed)
        for pen in self.all_pens:
            if pen.is_populated:
                pen.subset_class_feeds(feed)
                pen_specific_feed_data = available_feeds.get_feed_data_from_feed_ids(pen.allocated_feeds)

                ration_per_animal = {}
                ration_vals = {}

                while "status" not in ration_per_animal or ration_per_animal["status"].lower() != "optimal":
                    if pen.animal_combination == AnimalCombination.CALF:
                        ration_per_animal = CalfRationManager.optimize()
                        ration_vals = {"ME_total": 0}
                    else:
                        ration_per_animal, ration_vals = RationManager.formulate_ration(
                            pen, pen_specific_feed_data, self.ANIMAL_GROUPING_SCENARIO
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
                    else:  # feeds and price
                        ration_per_pen[key] = ration_per_animal[key] * num_animals

                pen.ration = ration_per_pen
                pen.ration_per_animal = ration_per_animal  # Important

    @classmethod
    def _get_animal_types_in_pen(cls, pen: Pen) -> Set[AnimalType]:
        """
        Get the animal types in the pen.

        Notes
        -----
        This method returns a set of animal types. By definition of a set, there will be no repeats.
        Note that removing an animal from a pen doesn't necessarily mean that we can remove the animal's
        type from the set, because there may still be other animals with the same type in the pen.
        Therefore, to improve efficiency, if there is a need to remove multiple animals at the same time,
        this method should be called after all the animals have been removed.

        Parameters
        ----------
        pen : Pen
            The pen to get the animal types from.

        Returns
        -------
        Set
            The set of animal types in the pen.

        """

        animal_types_in_pen = set()
        for animal in list(pen.animals_in_pen.values()):
            animal_type = cls.ANIMAL_GROUPING_SCENARIO.get_animal_type(animal)
            animal_types_in_pen.add(animal_type)

        return animal_types_in_pen

    @classmethod
    def _determine_classes_in_pen(cls, pen: Pen) -> Set[str]:
        """
        Get the classes of animals in the pen.

        Parameters
        ----------
        pen : Pen
            The pen to get the classes of animals from.

        Returns
        -------
        Set
            The set of classes of animals in the pen.

        """

        animal_types_in_pen = cls._get_animal_types_in_pen(pen)
        return {animal_type.value for animal_type in animal_types_in_pen}

    def _get_animals_snapshot(self) -> Dict[str, set]:
        """
        Create a snapshot of the current state of all the animals in the system.

        This function generates a dictionary that maps each animal group name to a set of animals within that group.
        Additionally, it includes a mapping from each animal's ID to its associated animal combination as determined
        by the current ANIMAL_GROUPING_SCENARIO.

        The snapshot dictionary serves as a summary of the current state of all animals in the system,
        allowing for efficient comparison of animal states before and after life cycle's updates.

        Returns
        -------
        dict
            A dictionary with the following structure:
            - 'calves': a set containing all calves currently in the system.
            - 'heiferIs': a set containing all heiferIs currently in the system.
            - 'heiferIIs': a set containing all heiferIIs currently in the system.
            - 'heiferIIIs': a set containing all heiferIIIs currently in the system.
            - 'cows': a set containing all cows currently in the system.
            - 'animal_combination_by_id': a dictionary mapping each animal's ID to its
                associated animal combination according to the current ANIMAL_GROUPING_SCENARIO.

        """
        snapshot = {
            "calves": set(self.calves),
            "heiferIs": set(self.heiferIs),
            "heiferIIs": set(self.heiferIIs),
            "heiferIIIs": set(self.heiferIIIs),
            "cows": set(self.cows),
            "animal_combination_by_id": {},
        }
        for animal in [
            *self.calves,
            *self.heiferIs,
            *self.heiferIIs,
            *self.heiferIIIs,
            *self.cows,
        ]:
            snapshot["animal_combination_by_id"][animal.id] = self.ANIMAL_GROUPING_SCENARIO.find_animal_combination(
                animal
            )
        return snapshot

    def _handle_removed_animals_after_update(
        self,
        animals_snapshot_before_update: Dict[str, set | Dict],
        animals_snapshot_after_update: Dict[str, set | Dict],
    ) -> None:
        """
        Dict[str, Dict[Union[Calf | HeiferI | HeiferII | HeiferIII]]]
        Identifies and handles animals that were present prior to the update, but not afterwards.

        This function detects any animals that have been removed between updates (e.g., due to graduation,
        being sold, or being culled), and then updates the internal state accordingly by calling
        '_remove_animal_from_pen_and_id_map' for each removed animal.

        Parameters
        ----------
        animals_snapshot_before_update : Dict[str, set | Dict]
            A snapshot of the state of all the animals before the update. This dictionary uses
            animal class names as keys ('calves', 'heiferIs', etc.) and sets of animal instances
            as values.

        animals_snapshot_after_update : Dict[str, set | Dict]
            A snapshot of the state of all the animals after the update. This dictionary should
            have the same structure as `animals_snapshot_before_update`.

        Returns
        -------
        None
            This function doesn't return any value. Its purpose is to modify the internal state of the
            class instance by calling '_remove_animal_from_pen_and_id_map' for each animal that
            has been removed.
        """
        animal_class_names = ["calves", "heiferIs", "heiferIIs", "heiferIIIs", "cows"]

        removed_animals = set()
        for animal_type_name in animal_class_names:
            removed_animals.update(
                animals_snapshot_before_update[animal_type_name] - animals_snapshot_after_update[animal_type_name]
            )

        for animal in removed_animals:
            self._remove_animal_from_pen_and_id_map(animal)

    def _handle_animals_with_unchanged_class_and_changed_combination(
        self,
        animals_snapshot_before_update: Dict[str, set | Dict],
        animals_snapshot_after_update: Dict[str, set | Dict],
        feed: Feed,
        current_temperature: float,
    ):
        """
        Handle animals that didn't change their classes but changed their animal combination.

        The reason for the change in animal combination is that the animal's physiological states have changed.
        Because each pen is associated with a specific animal combination, the animal needs to be moved to
        a different pen with the new animal combination.

        For example, a cow can be in the dry state or lactating state, but depending on the
        current state of the cow, she can be in a different pen with a different animal combination.

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
            Instance of the Feed class.
        current_temperature : float
            Current temperature.

        Returns
        -------
        None
            This function does not return anything. It operates by side effects, changing the
            assignments of animals to pens.

        """
        animal_class_names = ["calves", "heiferIs", "heiferIIs", "heiferIIIs", "cows"]
        animals_with_unchanged_class = set()
        for animal_class_name in animal_class_names:
            animals_with_unchanged_class.update(
                animals_snapshot_before_update[animal_class_name] & animals_snapshot_after_update[animal_class_name]
            )
        animals_with_unchanged_class_and_changed_combination = set()
        for animal in animals_with_unchanged_class:
            if (
                animals_snapshot_before_update["animal_combination_by_id"][animal.id]
                != animals_snapshot_after_update["animal_combination_by_id"][animal.id]
            ):
                animals_with_unchanged_class_and_changed_combination.add(animal)

        for animal in animals_with_unchanged_class_and_changed_combination:
            self._remove_animal_from_pen_and_id_map(animal)
            self._add_animal_to_pen_and_id_map(animal, feed, current_temperature)

    def _handle_graduated_animals(
        self,
        animals_snapshot_before_update: Dict[str, set | Dict],
        animals_snapshot_after_update: Dict[str, set | Dict],
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
        graduated_animals = set()
        for animal_class_name in ["heiferIs", "heiferIIs", "heiferIIIs", "cows"]:
            graduated_animals.update(
                animals_snapshot_after_update[animal_class_name] - animals_snapshot_before_update[animal_class_name]
            )
        for animal in graduated_animals:
            self._add_animal_to_pen_and_id_map(animal, feed, current_temperature)

    def _handle_newly_added_animals(
        self,
        new_animals: List[Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]],
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
            self.animals_by_type[type(animal)].append(animal)

    def _remove_animal_from_pen_and_id_map(self, animal: Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]) -> None:
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
        animal: Union[Calf, HeiferI, HeiferII, HeiferIII, Cow],
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

    def collect_manure_excretions_output_data(self, pen: Pen, manure_excretions_output_data: Dict) -> None:
        pen.classes_in_pen = self._determine_classes_in_pen(pen)
        pen.calc_total_manure(
            self.methane_model,
            self.methane_mitigation_method,
            self.methane_mitigation_additive_amount,
            manure_excretions_output_data,
        )

    def daily_updates(self, feed: Feed, weather: Weather, time: Time) -> None:
        """
        Execute the daily routines relating to Animals. All animals are
        updated through the life_cycle_manager's daily_update() method. The
        daily phosphorus calculations are also done. If it is the end of the
        ration interval, the animals are allocated to new pens and the ration &
        manure calculations are done.

        It is important that the Pen class has the ability to add and remove one animal at a time and
        adjust relevant variables accordingly based solely on the addition or removal of that animal.

        Parameters
        ----------
        feed : Feed
            instance of the Feed class defined in feed.py
        weather : Weather
            instance of the Weather class
        time : Time
            instance of the Time class

        """
        if self.simulate_animals:
            if self.end_ration_interval():
                self.reset_milk_production_reduction()
            current_conditions = weather.get_current_day_conditions(time)
            current_temperature = current_conditions.mean_air_temperature
            animals_snapshot_before_update = self._get_animals_snapshot()

            (
                animals_added,
                animals_removed,
                calves_born,
                *rest,
            ) = self.life_cycle_manager.daily_update(
                self.simulation_day,
                self.calves,
                self.heiferIs,
                self.heiferIIs,
                self.heiferIIIs,
                self.cows,
            )

            animals_snapshot_after_update = self._get_animals_snapshot()

            self._handle_removed_animals_after_update(animals_snapshot_before_update, animals_snapshot_after_update)
            self._handle_animals_with_unchanged_class_and_changed_combination(
                animals_snapshot_before_update,
                animals_snapshot_after_update,
                feed,
                current_temperature,
            )

            self._handle_graduated_animals(
                animals_snapshot_before_update,
                animals_snapshot_after_update,
                feed,
                current_temperature,
            )

            self._handle_newly_added_animals([*animals_added, *calves_born], feed, current_temperature)

            self._record_animal_counts()
            self._record_culling_stats()
            if time.is_last_day_of_simulation:
                self._record_animal_events(self.cows)
                self._record_animal_events(self.heiferIIs)
                self._record_heiferIIs_conception_rate()
                self._record_cows_conception_rate()

            self.calc_p_rqmts()
            self.daily_p_update()
            self._update_phosphorus_concentrations()
            self.record_pen_history()

            if self.end_ration_interval():
                self.reset_milk_production_reduction()
                self.calc_nutrient_rqmts(feed, current_temperature)
                self.clear_pens()
                self.allocate_animals_to_pens()
                self._calc_ration_at_interval(feed)
                AnimalModuleReporter.report_ration_interval_data(self.all_pens, feed, self.simulation_day)
                self.calc_avg_growth()
                for pen in self.all_pens:
                    if pen.animal_combination.name == "LAC_COW":
                        for animal in list(pen.animals_in_pen.values()):
                            animal.update_milk_production_history(self.simulation_day)

            manure_excretions_output_data = {}
            for pen in self.all_pens:
                self.collect_manure_excretions_output_data(pen, manure_excretions_output_data)
            AnimalModuleReporter.report_animal_module_manure(manure_excretions_output_data)

            self.life_cycle_manager.daily_milk_production = self.sum_daily_milk(self.cows)
            AnimalModuleReporter.report_daily_reports(self, feed.available_feeds)

    def _record_animal_events(self, animals: list[Calf | HeiferI | HeiferII | HeiferIII | Cow]) -> None:
        """
        Record the events of the animals.

        Parameters
        ----------
        animals : list[Calf, HeiferI, HeiferII, HeiferIII, Cow]
            A list of animals.

        Returns
        -------
        None
        """

        info_map = {
            "class": self.__class__.__name__,
            "function": self._record_animal_events.__name__,
        }
        for animal in animals:
            om.add_variable(
                f"{animal.__class__.__name__}_{animal.id}_day_{self.simulation_day}",
                animal.events,
                dict(info_map, **{"units": MeasurementUnits.UNITLESS}),
            )

    def _record_animal_counts(self) -> None:
        """
        Record the number of animals in each animal class.

        Returns
        -------
        None
        """

        info_map = {
            "class": self.__class__.__name__,
            "function": self._record_animal_counts.__name__,
        }
        om.add_variable("sim_day", self.simulation_day, dict(info_map, **{"units": MeasurementUnits.SIMULATION_DAY}))
        om.add_variable(
            "num_animals",
            len(self.calves) + len(self.heiferIs) + len(self.heiferIIs) + len(self.heiferIIIs) + len(self.cows),
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable("num_calves", len(self.calves), dict(info_map, **{"units": MeasurementUnits.ANIMALS}))
        om.add_variable("num_heiferIs", len(self.heiferIs), dict(info_map, **{"units": MeasurementUnits.ANIMALS}))
        om.add_variable("num_heiferIIs", len(self.heiferIIs), dict(info_map, **{"units": MeasurementUnits.ANIMALS}))
        om.add_variable("num_heiferIIIs", len(self.heiferIIIs), dict(info_map, **{"units": MeasurementUnits.ANIMALS}))
        om.add_variable(
            "num_lactating_cows",
            len([cow for cow in self.cows if cow.is_lactating]),
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "num_dry_cows",
            len([cow for cow in self.cows if not cow.is_lactating]),
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable("num_cows", len(self.cows), dict(info_map, **{"units": MeasurementUnits.ANIMALS}))
        om.add_variable(
            "num_cow_parity_1",
            self.life_cycle_manager.num_cow_for_parity["1"],
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "num_cow_parity_2",
            self.life_cycle_manager.num_cow_for_parity["2"],
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "num_cow_parity_3",
            self.life_cycle_manager.num_cow_for_parity["3"],
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "num_cow_parity_4+",
            self.life_cycle_manager.num_cow_for_parity["greater_than_3"],
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )

    def _record_heiferIIs_conception_rate(self) -> None:
        """
        Record the conception rate of heiferIIs.
        """

        info_map = {
            "class": self.__class__.__name__,
            "function": self._record_heiferIIs_conception_rate.__name__,
        }
        om.add_variable(
            "heiferII_total_num_ai_performed",
            HeiferII.stats["num_ai_performed"],
            dict(info_map, **{"units": MeasurementUnits.ARTIFICIAL_INSEMINATIONS}),
        )
        om.add_variable(
            "heiferII_total_num_successful_conceptions",
            HeiferII.stats["num_successful_conceptions"],
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS}),
        )
        heiferII_overall_conception_rate = (
            (HeiferII.stats["num_successful_conceptions"] / HeiferII.stats["num_ai_performed"])
            if HeiferII.stats["num_ai_performed"] > 0
            else 0
        )
        om.add_variable(
            "heiferII_overall_conception_rate",
            heiferII_overall_conception_rate,
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS_PER_SERVICE}),
        )

        om.add_variable(
            "heiferII_num_ai_performed_in_ED",
            HeiferII.stats["num_ai_performed_in_ED"],
            dict(info_map, **{"units": MeasurementUnits.ARTIFICIAL_INSEMINATIONS}),
        )
        om.add_variable(
            "heiferII_num_successful_conceptions_in_ED",
            HeiferII.stats["num_successful_conceptions_in_ED"],
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS}),
        )
        ed_conception_rate = (
            (HeiferII.stats["num_successful_conceptions_in_ED"] / HeiferII.stats["num_ai_performed_in_ED"])
            if HeiferII.stats["num_ai_performed_in_ED"] > 0
            else 0
        )
        om.add_variable(
            "heiferII_ED_conception_rate",
            ed_conception_rate,
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS_PER_SERVICE}),
        )

        om.add_variable(
            "heiferII_num_ai_performed_in_TAI",
            HeiferII.stats["num_ai_performed_in_TAI"],
            dict(info_map, **{"units": MeasurementUnits.ARTIFICIAL_INSEMINATIONS}),
        )
        om.add_variable(
            "heiferII_num_successful_conceptions_in_TAI",
            HeiferII.stats["num_successful_conceptions_in_TAI"],
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS}),
        )
        tai_conception_rate = (
            (HeiferII.stats["num_successful_conceptions_in_TAI"] / HeiferII.stats["num_ai_performed_in_TAI"])
            if HeiferII.stats["num_ai_performed_in_TAI"] > 0
            else 0
        )
        om.add_variable(
            "heiferII_TAI_conception_rate",
            tai_conception_rate,
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS_PER_SERVICE}),
        )

        om.add_variable(
            "heiferII_num_ai_performed_in_SynchED",
            HeiferII.stats["num_ai_performed_in_SynchED"],
            dict(info_map, **{"units": MeasurementUnits.ARTIFICIAL_INSEMINATIONS}),
        )
        om.add_variable(
            "heiferII_num_successful_conceptions_in_SynchED",
            HeiferII.stats["num_successful_conceptions_in_SynchED"],
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS}),
        )
        synch_ed_conception_rate = (
            (HeiferII.stats["num_successful_conceptions_in_SynchED"] / HeiferII.stats["num_ai_performed_in_SynchED"])
            if HeiferII.stats["num_ai_performed_in_SynchED"] > 0
            else 0
        )
        om.add_variable(
            "heiferII_SynchED_conception_rate",
            synch_ed_conception_rate,
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS_PER_SERVICE}),
        )

    def _record_cows_conception_rate(self) -> None:
        """
        Record the conception rate of cows.
        """

        info_map = {
            "class": self.__class__.__name__,
            "function": self._record_cows_conception_rate.__name__,
        }
        om.add_variable(
            "cow_total_num_ai_performed",
            Cow.stats["num_ai_performed"],
            dict(info_map, **{"units": MeasurementUnits.ARTIFICIAL_INSEMINATIONS}),
        )
        om.add_variable(
            "cow_total_num_successful_conceptions",
            Cow.stats["num_successful_conceptions"],
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS}),
        )
        cow_overall_conception_rate = (
            (Cow.stats["num_successful_conceptions"] / Cow.stats["num_ai_performed"])
            if Cow.stats["num_ai_performed"] > 0
            else 0
        )
        om.add_variable(
            "cow_overall_conception_rate",
            cow_overall_conception_rate,
            dict(info_map, **{"units": MeasurementUnits.CONCEPTIONS_PER_SERVICE}),
        )

    def _record_culling_stats(self) -> None:
        """
        Record the culling stats of cows.
        """

        info_map = {
            "class": self.__class__.__name__,
            "function": self._record_culling_stats.__name__,
        }
        om.add_variable(
            "num_cows_by_death_cull",
            self.life_cycle_manager.cull_reason_stats_range[animal_constants.DEATH_CULL],
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "num_cows_by_low_prod_cull",
            self.life_cycle_manager.cull_reason_stats_range[animal_constants.LOW_PROD_CULL],
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "num_cows_by_lameness_cull",
            self.life_cycle_manager.cull_reason_stats_range[animal_constants.LAMENESS_CULL],
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "num_cows_by_injury_cull",
            self.life_cycle_manager.cull_reason_stats_range[animal_constants.INJURY_CULL],
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "num_cows_by_mastitis_cull",
            self.life_cycle_manager.cull_reason_stats_range[animal_constants.MASTITIS_CULL],
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "num_cows_by_disease_cull",
            self.life_cycle_manager.cull_reason_stats_range[animal_constants.DISEASE_CULL],
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "num_cows_by_udder_cull",
            self.life_cycle_manager.cull_reason_stats_range[animal_constants.UDDER_CULL],
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "num_cows_by_unknown_cull",
            self.life_cycle_manager.cull_reason_stats_range[animal_constants.UNKNOWN_CULL],
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
        om.add_variable(
            "total_num_cows_culled",
            sum(self.life_cycle_manager.cull_reason_stats_range.values()),
            dict(info_map, **{"units": MeasurementUnits.ANIMALS}),
        )
