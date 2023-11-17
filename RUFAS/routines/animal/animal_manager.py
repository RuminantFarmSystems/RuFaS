"""
RUFAS: Ruminant Farm Systems Model
File name: animal_manager.py

Description: The class which manages all of the animal routines and keeps track of
    all animals and pens. All operations are as described in the Animal Module
    Information Flow document on Basecamp (such as daily animal updates and
    pen allocation). Method calls cascade through from the animal manager
    class to pen to each individual animal in that pen. The life cycle of each animal
    is controlled by an instance of the LifeCycleManager class, and this instance
    updates the animals daily.

Author(s): Militsa Sotirova, militsasotirova@gmail.com
           Chris VanKerkhove, cjv47@cornell.edu
           Joseph Merhi, jm2257@cornell.edu
"""
import collections
import math
import random
from statistics import mean
from typing import Any, Dict, Tuple, List, Set, Union

from RUFAS.general_constants import GeneralConstants
from RUFAS.time import Time
from RUFAS.weather import Weather
from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.animal_grouping_scenarios import AnimalGroupingScenario
from RUFAS.routines.animal.animal_typed_dicts import InitializationDBSummaryTypedDict
from RUFAS.routines.animal.animal_types import AnimalType
from RUFAS.routines.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.life_cycle.life_cycle import LifeCycleManager
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.animal.ration import ration_driver as ration_driver
from RUFAS.routines.feed.feed import Feed
from RUFAS.routines.animal.ration.calf_ration import CalfRationManager
from RUFAS.routines.animal.ration.ration_driver import RationReporter
from RUFAS.routines.animal.ration.ration_driver import RationManager

from RUFAS.routines.animal.ration import user_defined_ration as udr

om = OutputManager()


def daily_animal_routine(animal_manager, feed, weather: Weather, time: Time):
    """
    Executes daily routines relating to Animals. This method is called every day
    in the simulation and calls @animal_manager's daily_updates() method
    with @feed and @time as arguments. [Note that currently, @weather and
    @ time are not used in animal updates.]

    Parameters
    ----------
    animal_manager : AnimalManager
        instance of the AnimalManager class
    feed : Feed
        instance of the Feed class
    weather : Weather
        instance of the Weather class
    time : Time
        instance of the Time class
    """

    animal_manager.daily_updates(feed, weather, time)


class AnimalManager:
    """
    Manages all animal routines (i.e. calling daily updates, allocating animals
    to pens, etc). Stores a list of all animals and pens in the simulation as
    well as an instance of the LifeCycleManager class in order to update the
    animals' life cycles.
    """
    # TODO: make this a method?
    DEFAULT_NUM_STALLS_BY_COMBINATION = {
        Pen.AnimalCombination.CALF: AnimalModuleConstants.DEFAULT_NUM_STALLS_FOR_CALF_PEN,
        Pen.AnimalCombination.GROWING: AnimalModuleConstants.DEFAULT_NUM_STALLS_FOR_GROWING_PEN,
        Pen.AnimalCombination.CLOSE_UP: AnimalModuleConstants.DEFAULT_NUM_STALLS_FOR_CLOSE_UP_PEN,
        Pen.AnimalCombination.LAC_COW: AnimalModuleConstants.DEFAULT_NUM_STALLS_FOR_LAC_COW_PEN,
        Pen.AnimalCombination.GROWING_AND_CLOSE_UP:
        AnimalModuleConstants.DEFAULT_NUM_STALLS_FOR_GROWING_AND_CLOSE_UP_PEN,
    }

    ANIMAL_GROUPING_SCENARIO = AnimalGroupingScenario.CALF__GROWING__CLOSE_UP__LACCOW

    # ANIMAL_GROUPING_SCENARIO = AnimalGroupingScenario.CALF__GROWING_AND_CLOSE_UP__LACCOW

    # TODO use this method! Determine if we want to add another user input
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
        config.update(data['management_decisions'])
        config.update(data['farm_level']['calf'])
        config.update(data['farm_level']['repro'])
        config.update(data['farm_level']['bodyweight'])
        config.update(data['from_literature']['repro'])
        config.update(data['from_literature']['milking'])
        config.update(data['from_literature']['culling'])
        config.update(data['from_literature']['life_cycle'])
        return config

    def __init__(self, data, config, feed, weather: Weather, time: Time):
        """
        Initializes the pens and animals in the simulation with data from the
        JSON file by calling init_pens() and init_animals(). Creates instance
        of LifeCycleManager class and sets up the animal environment.

        Parameters
        ----------
        data : Dict
            dictionary with animal information from the input JSON file
        config : Config
            instance of the Config class
        feed : Feed
            instance of the Feed class
        weather : Weather
            instance of the Weather class
        time : Time
            instance of the Time class

        """

        # simulation length, days
        self.sim_length = config.sim_length

        # day in the simulation
        self.simulation_day = 1

        animal_config = self.get_animal_config(data['animal_config'])

        # instance of LifeCycleManager class
        self.life_cycle_manager = LifeCycleManager(animal_config)

        AnimalBase.set_config(animal_config)
        AnimalBase.set_nutrient_list(feed.nutrient_rqmts)

        # if False, there are no animals being simulated on the farm
        self.simulate_animals = config.simulate_animals

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

        # dictionary for keeping track of what animal types each pen is holding
        # (value of the dictionaries are lists of pen objects)
        self.pens_by_animal_combination = {Pen.AnimalCombination.CALF: [],
                                           Pen.AnimalCombination.GROWING: [],
                                           Pen.AnimalCombination.CLOSE_UP: [],
                                           Pen.AnimalCombination.GROWING_AND_CLOSE_UP: [],
                                           Pen.AnimalCombination.LAC_COW: []}

        # these variables are the P concentrations of each class of animal. They
        # are calculated daily and are used when an animal is added to the
        # herd, whether by birth or replacement herd purchase. They are calculated
        # in _update_phosphorus_concentrations() and are calculated by dividing the total P in the animals
        # of the class by the total body weight of the animals, on a per-animal basis
        self.p_conc = {
            'calf': 0,
            'heiferI': 0,
            'heiferII': 0,
            'heiferIII': 0,
            'cow': 0
        }

        self.phosphorus_concentration_by_animal_class = {animal_type: 0.0
                                                         for animal_type in [Calf, HeiferI, HeiferII, HeiferIII, Cow]}

        # housing type: barn or pasture
        self.housing = data['housing']

        # concentrate supplementation when farming type is "pasture", kg
        self.pasture_concentrate = data['pasture_concentrate']

        udrm = udr.UserDefinedRationManager()
        self.ration_user_input = data['ration']['user_input']
        udrm.is_udr = self.ration_user_input

        # how often a ration is calculated, days
        self.formulation_interval = data['ration']['formulation_interval']

        self.methane_model = data['methane_model']
        self.methane_mitigation_method = data['methane_mitigation']['methane_mitigation_method']
        self.methane_mitigation_additive_amount = data['methane_mitigation']['methane_mitigation_additive_amount']

        self.init_pens(data['pen_information'], data['herd_information'], data['manure_management_scenarios'])

        if self.simulate_animals:
            self.init_animals(config, data['herd_information'])

            self.init_nutrient_rqmts(weather, time, feed)

            self.allocate_animals_to_pens()

        self._print_animal_num_warnings(data['herd_information'])

    @property
    def animals_by_type(self):
        return {
            Calf: self.calves,
            HeiferI: self.heiferIs,
            HeiferII: self.heiferIIs,
            HeiferIII: self.heiferIIIs,
            Cow: self.cows
        }

    def init_pens(self, all_pen_data: list, herd_data: Dict[str, Any], manure_management_scenarios) -> None:
        """
        Populates the list of pens with the information from the input json file.

        Parameters
        ----------
        all_pen_data: list[dict[str, Any]]
            List containing information about the pens.
        herd_data: Dict[str, Any]
            Dictionary containing information about the herd.
        manure_management_scenarios : Dict TODO: [str, Any]?
            Dictionary containing information about the manure management scenarios.

        """

        # Initialize pens from all_pen_data
        for pen_data in all_pen_data:
            pen_data['pen_id'] = pen_data.pop('id')
            pen_data['animal_combination'] = Pen.AnimalCombination[pen_data.pop('animal_combination')]

            manure_management_scenario_id = pen_data.pop('manure_management_scenario_id')
            manure_management_scenario = [scenario for scenario in manure_management_scenarios
                                          if scenario['scenario_id'] ==
                                          manure_management_scenario_id][0]
            pen_data['bedding_type'] = manure_management_scenario['bedding_type']
            pen_data['manure_handling'] = manure_management_scenario['manure_handler']
            pen_data['manure_separator'] = \
                manure_management_scenario['manure_separator']
            pen_data['manure_storage'] = \
                manure_management_scenario['manure_treatment']

            pen = Pen(**pen_data)

            self.all_pens.append(pen)

    def init_animals(self, config, herd_data: Dict[str, Any]) -> None:
        """
        Populates the list of animals with the information from the
        input JSON file: constructs the calves, heiferI's, heiferII's,
        heiferIII's, and cows (the desired amounts of each is specified by
        @data), then calls life_cycle_manager's initialize_herd() with those
        numbers to create instances of the animals. The nutrient requirements
        are calculated and the animals are allocated to pens.

        Parameters
        ----------
        config : Config
            an instance of the Config class contains model configuration information
        herd_data : Dict[str, Any]
            dictionary containing information about the herd
        """

        self.calves, self.heiferIs, self.heiferIIs, self.heiferIIIs, self.cows \
            = self.life_cycle_manager.initialize_herd(config, herd_data)

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

        animal_keys = {"calf_num", "heiferI_num", "heiferII_num", "heiferIII_num_springers", "cow_num"}

        info_map = {
            "class": self.__class__.__name__,
            "function": self._print_animal_num_warnings.__name__,
            "simulate_animals": self.simulate_animals,
            "herd_data_animal_nums": {key: herd_data[key] for key in animal_keys}
        }

        counter = 0

        if not self.simulate_animals:
            for key in animal_keys:
                if herd_data[key] != 0:
                    om.add_warning(f"invalid_{key}_warning",
                                   f"Warning: simulate_animals is false, but {key} is not.",
                                   info_map)
                    counter += 1
            om.add_log("num_warnings_associated_with_simulate_animals",
                       f"{counter} warnings were associated with simulate_animals",
                       info_map)
        else:
            om.add_log("simulate_animals_flag",
                       "simulate_animals is true",
                       info_map)

    def init_nutrient_rqmts(self, weather: Weather, time: Time, feed):
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

        # TODO reevaluate the below: walking distance was removed because it is calculated at a later step.
        # average vertical & horizontal distance (VD, HD) of pens to the
        # milking parlor
        # avg_VD_parlor, avg_HD_parlor = self.avg_pen_dist()
        current_conditions = weather.get_current_day_conditions(time)
        temp = current_conditions.mean_air_temperature
        for calf in self.calves:
            calf.calc_nutrient_rqmts(feed, temp)
            calf.p_animal = 0.0072 * calf.body_weight * 1000

        for heiferI in self.heiferIs:
            heiferI.set_nutrient_rqmts(temp, self.ANIMAL_GROUPING_SCENARIO)
            heiferI.p_animal = 0.0072 * heiferI.body_weight * 1000

        for heiferII in self.heiferIIs:
            heiferII.set_nutrient_rqmts(temp, self.ANIMAL_GROUPING_SCENARIO)
            heiferII.p_animal = 0.0072 * heiferII.body_weight * 1000

        for heiferIII in self.heiferIIIs:
            heiferIII.set_nutrient_rqmts(temp, self.ANIMAL_GROUPING_SCENARIO)
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

        return mean(pen.vertical_dist_to_parlor for pen in self.all_pens), \
            mean(pen.horizontal_dist_to_parlor for pen in self.all_pens)

    def calc_nutrient_rqmts(self, feed, temp: float) -> None:
        """
        Calls each animal's method to calculate its nutrient requirements.

        Parameters
        ----------
        feed : Feed
            instance of the feed class
        temp : float
            the temperature on the current day

        """
        for calf in self.calves:
            calf.calc_nutrient_rqmts(feed, temp)

        for heiferI in self.heiferIs:
            latest_pen = heiferI.pen_history[-1].pen
            heiferI.set_nutrient_rqmts(temp, self.ANIMAL_GROUPING_SCENARIO,
                                       nutrient_conc=self.all_pens[latest_pen].ration_nutrient_conc,
                                       metabolizable_energy=self.all_pens[latest_pen].MEdiet,
                                       previous_DMI=self.all_pens[latest_pen].dry_matter_intake)

        for heiferII in self.heiferIIs:
            latest_pen = heiferII.pen_history[-1].pen
            heiferII.set_nutrient_rqmts(temp, self.ANIMAL_GROUPING_SCENARIO,
                                        nutrient_conc=self.all_pens[latest_pen].ration_nutrient_conc,
                                        metabolizable_energy=self.all_pens[latest_pen].MEdiet,
                                        previous_DMI=self.all_pens[latest_pen].dry_matter_intake)

        for heiferIII in self.heiferIIIs:
            latest_pen = heiferIII.pen_history[-1].pen
            heiferIII.set_nutrient_rqmts(temp, self.ANIMAL_GROUPING_SCENARIO,
                                         nutrient_conc=self.all_pens[latest_pen].ration_nutrient_conc,
                                         metabolizable_energy=self.all_pens[latest_pen].MEdiet,
                                         previous_DMI=self.all_pens[latest_pen].dry_matter_intake)

        for cow in self.cows:
            latest_pen = cow.pen_history[-1].pen
            cow.set_nutrient_rqmts(self.ANIMAL_GROUPING_SCENARIO,
                                   nutrient_conc=self.all_pens[latest_pen].ration_nutrient_conc)

    def reset_milk_production_reduction(self) -> None:
        """
        Resets reduction value for milk production to 0.0 for all animals in all pens

        The milk_production_reduction attribute is a value generated in ration_driver.py,
            in cases where a ration cannot be formulated such that it meets animal requirements

        """
        for pen in self.all_pens:
            if pen.animal_combination.name == 'LAC_COW' or pen.animal_combination.name == 'CLOSE_UP':
                for animal in pen.animals_in_pen:
                    animal.milk_production_reduction = 0.0

    def fully_update_animal_to_pen_id_map(self) -> None:
        """
        Updates the entire animal_to_pen_id_map dictionary so that each animal's ID is
        associated with the pen that animal is in.
        """
        for pen in self.all_pens:
            animals_in_pen = pen.animals_in_pen
            for animal in animals_in_pen:
                self.animal_to_pen_id_map[animal.id] = pen.id

    def remove_animals_from_herd(self, animals_removed: List[AnimalBase]) -> None:
        """
        Deletes the IDs of animals from animal_to_pen_id_map dictionary when the animal
        was removed from the herd; updates the relevant pen's stocking density.

        Parameters
        ----------
        animals_removed : List[AnimalBase]
            list of animal objects that are to be removed from the herd

        """

        for animal in animals_removed:
            if animal.id in self.animal_to_pen_id_map:
                pen = self.all_pens[self.animal_to_pen_id_map[animal.id]]
                pen.remove_animals_by_ids([animal.id])
                pen.stocking_density = len(pen.animals_in_pen) / pen.num_stalls
                del self.animal_to_pen_id_map[animal.id]

    def track_former_pen_population(self) -> List[int]:
        """
        Creates a list containing the original pen populations of a simulated
        farm before any updates are made to pens. The original pens' information
        would get lost as animals get added.

        Returns
        -------
        a list of the populations of each pen on the farm prior to
            any additions due to daily pen updates
        """

        pen_population_before_additions = [0] * len(self.all_pens)

        for index, pen in enumerate(self.all_pens):
            pen_population_before_additions[index] = len(pen.animals_in_pen)

        return pen_population_before_additions

    def calculate_pen_rations(self, prior_pen_populations: List[int]) -> None:
        """
        Adjusts the amount of each feed within a ration that is delivered to a pen
            when the number of animals in the pen is changed

        Parameters
        ----------
        prior_pen_populations : List[int]
            list of the number of animals in each pen, since
             pens are zero-indexed
        """

        for index, pen in enumerate(self.all_pens):
            for key in pen.ration:
                if key != 'status' and key != 'objective':
                    pen.ration[key] = (pen.ration[key] / prior_pen_populations[index]) * len(pen.animals_in_pen)

    def daily_update_id_map(self, animals_added: List[AnimalBase], animals_removed: List[AnimalBase],
                            calves_born: List[Calf], feed: Feed, temp: float) -> None:
        """
        Updates the dictionary that maps animal IDs to the ID of the pen they are housed in when
        new animals are born or purchased and when animals leave the herd due to death or culling

        Parameters
        ----------
        animals_added : List[AnimalBase]
            list of animal objects that have been added to the herd
        animals_removed : List[AnimalBase]
            list of animal objects that have been removed from the herd
        calves_born : List[Calf]
            list of Calf objects that have been added to the herd
        feed : Feed
            an instance of the Feed class defined in feed.py
        temp : float
            the temperature on the current day

        """

        all_animals_added = animals_added + calves_born

        original_pen_populations = self.track_former_pen_population()

        self.remove_animals_from_herd(animals_removed)

        animal_type_mapping_dict = {
            'Calf': {'p_conc': self.p_conc['calf'], 'animal_list': self.calves,
                     'animal_group': Pen.AnimalCombination.CALF},
            'HeiferI': {'p_conc': self.p_conc['heiferI'], 'animal_list': self.heiferIs,
                        'animal_group': Pen.AnimalCombination.GROWING},
            'HeiferII': {'p_conc': self.p_conc['heiferII'], 'animal_list': self.heiferIIs,
                         'animal_group': Pen.AnimalCombination.GROWING},
            'HeiferIII': {'p_conc': self.p_conc['heiferIII'], 'animal_list': self.heiferIIIs,
                          'animal_group': Pen.AnimalCombination.CLOSE_UP},
            'Lac_Cow': {'p_conc': self.p_conc['cow'], 'animal_list': self.cows,
                        'animal_group': Pen.AnimalCombination.LAC_COW},
            'Dry_Cow': {'p_conc': self.p_conc['cow'], 'animal_list': self.cows,
                        'animal_group': Pen.AnimalCombination.CLOSE_UP}}

        for animal in all_animals_added:
            animal_class = type(animal).__name__

            if animal_class == 'Cow':
                if animal.milking:
                    animal_class = 'Lac_Cow'
                else:
                    animal_class = 'Dry_Cow'

            animal_p_conc = (animal_type_mapping_dict.get(animal_class)['p_conc'])
            animal_type_mapping_dict.get(animal_class)['animal_list'].append(animal)
            group = animal_type_mapping_dict.get(animal_class)['animal_group']

            candidate_pens = self.pens_by_animal_combination[group]
            pen_for_insert = min(candidate_pens, key=lambda p: p.stocking_density)

            new_pen_population = (pen_for_insert.stocking_density * pen_for_insert.num_stalls) + 1
            pen_for_insert.stocking_density = new_pen_population / pen_for_insert.num_stalls

            self.animal_to_pen_id_map[animal.id] = pen_for_insert.id
            self.all_pens[pen_for_insert.id].set_up_new_animal(animal, animal_p_conc, feed, temp,
                                                               original_pen_populations[pen_for_insert.id])

        self.calculate_pen_rations(original_pen_populations)

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
    def _group_pens_by_animal_combination(cls, all_pens: List[Pen]) -> Dict[Pen.AnimalCombination, List[Pen]]:
        """
        Group a list of pens by animal combination.

        Parameters
        ----------
        all_pens : List[Pen]
            List of pens to group by animal combination.

        Returns
        -------
        Dict[Pen.AnimalCombination, List[Pen]]
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
            raise ValueError('The number of stalls and maximum stocking density must be greater than or equal to 0.')

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
    def _create_default_pen(cls,
                            pen_id: int,
                            animal_combination: Pen.AnimalCombination,
                            num_stalls: int,
                            max_stocking_density: float
                            ) -> Pen:
        """
        Create a default Pen object with the given parameters.

        Parameters
        ----------
        pen_id : int
            The unique identifier for the pen.
        animal_combination : Pen.AnimalCombination
            The animal combination for the pen.
        num_stalls : int
            The number of stalls in the pen.
        max_stocking_density : float
            The maximum stocking density for the pen.

        Returns
        -------
        Pen
            A new Pen object with the specified parameters and default values for other attributes.

        Examples
        --------
        >>> pen = AnimalManager._create_default_pen(pen_id=1, \
        animal_combination=Pen.AnimalCombination.CALF, num_stalls=10, max_stocking_density=1.5)
        >>> pen.id
        1
        >>> pen.animal_combination
        <AnimalCombination.CALF: 0>
        >>> pen.num_stalls
        10
        >>> pen.max_stocking_density
        1.5

        """

        return Pen(
            pen_id=pen_id,
            vertical_dist_to_milking_parlor=AnimalModuleConstants.VERTICAL_DIST_TO_MILKING_PARLOR,
            horizontal_dist_to_milking_parlor=AnimalModuleConstants.HORIZONTAL_DIST_TO_MILKING_PARLOR,
            number_of_stalls=num_stalls,
            housing_type=AnimalModuleConstants.DEFAULT_HOUSING_TYPE,
            bedding_type=AnimalModuleConstants.DEFAULT_BEDDING_TYPE,
            pen_type=AnimalModuleConstants.DEFAULT_PEN_TYPE,
            manure_handling=AnimalModuleConstants.DEFAULT_MANURE_HANDLER,
            manure_separator=AnimalModuleConstants.DEFAULT_MANURE_SEPARATOR,
            manure_storage=AnimalModuleConstants.DEFAULT_MANURE_STORAGE,
            animal_combination=animal_combination,
            max_stocking_density=max_stocking_density,
        )

    def _create_default_pens_for_potential_space_shortage(self, num_animals: int,
                                                          pens: List[Pen],
                                                          animal_combination: Pen.AnimalCombination,
                                                          start_pen_id=0) -> List[Pen]:
        """
        Create a list of default pens to accommodate potential animal space shortage.

        Parameters
        ----------
        num_animals : int
            The total number of animals to be accommodated.
        pens : List[Pen]
            A list of Pen objects representing the currently available pens.
        animal_combination : Pen.AnimalCombination
            The animal combination for the new default pens.
        start_pen_id : int, optional, default=0
            The starting pen ID for the new default pens. The default value is 0.

        Returns
        -------
        List[Pen]
            A list of new default Pen objects to accommodate the potential animal space shortage.

        """

        animal_space_shortage = self._calc_animal_space_shortage(num_animals=num_animals, pens=pens)
        new_default_pens: List[Pen] = []

        if animal_space_shortage > 0:
            num_stalls_per_pen = self.DEFAULT_NUM_STALLS_BY_COMBINATION[animal_combination]
            max_stocking_density = AnimalModuleConstants.DEFAULT_MAX_STOCKING_DENSITY

            max_animal_spaces_per_default_pen = self._calc_max_animal_spaces_per_pen(
                num_stalls=num_stalls_per_pen,
                max_stocking_density=max_stocking_density
            )
            num_new_default_pens = math.ceil(animal_space_shortage / max_animal_spaces_per_default_pen)
            for i in range(num_new_default_pens):
                new_default_pens.append(self._create_default_pen(
                    pen_id=start_pen_id + i,
                    animal_combination=animal_combination,
                    num_stalls=num_stalls_per_pen,
                    max_stocking_density=max_stocking_density
                ))

        return new_default_pens

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
            If num_animals is negative, or num_spaces is non-positive.

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
    def _allocate_animals_to_pens_helper(cls, animals: List[Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]],
                                         pens: List[Pen]) -> None:
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
            max_spaces_in_pens=[cls._calc_max_animal_spaces_per_pen(pen.num_stalls, pen.max_stocking_density)
                                for pen in pens]
        )

        cls.execute_allocation_plan(
            allocation_plan=allocation_plan,
            animals=animals,
            animal_pens=pens,
        )

    @classmethod
    def execute_allocation_plan(cls,
                                allocation_plan: List[int],
                                animals: List[Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]],
                                animal_pens: List[Pen]) -> None:
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
            If the length of the allocation plan does not match the number of pens, or if the sum of the
            allocation plan does not match the number of animals.

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
        sorted_pen_indices = sorted(range(num_pens_for_combination),
                                    key=lambda pen_idx: (allocation_limits[pen_idx], pen_idx))

        for i in sorted_pen_indices[:num_pens_for_combination - 1]:
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
        for animal in [*self.calves, *self.heiferIs, *self.heiferIIs, *self.heiferIIIs, *self.cows]:
            animal_combination = self.ANIMAL_GROUPING_SCENARIO.find_animal_combination(animal)
            animals_by_combination[animal_combination].append(animal)

        for animal_combination, animals in animals_by_combination.items():
            new_default_pens = self._create_default_pens_for_potential_space_shortage(
                num_animals=len(animals),
                pens=self.pens_by_animal_combination[animal_combination],
                animal_combination=animal_combination,
                start_pen_id=len(self.all_pens)
            )
            self.all_pens.extend(new_default_pens)
            self.pens_by_animal_combination[animal_combination].extend(new_default_pens)
            self._allocate_animals_to_pens_helper(animals, self.pens_by_animal_combination[animal_combination])

        self.fully_update_animal_to_pen_id_map()

    def _sort_animals_before_allocation(self) -> None:
        """
        Sort lactating cows by days in milk in increasing order.
        """
        self.cows = self._get_dry_cows(self.cows) + \
            sorted(self._get_lactating_cows(self.cows), key=lambda cow: cow.days_in_milk)

    def clear_pens(self) -> None:
        """
        Removes animals from pens for re-allocation. This is part of the
        routines that happen every ration interval.
        """

        for pen in self.all_pens:
            pen.clear()

    def calc_manure_excretion(self, feed, methane_model: str) -> None:
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
            if pen.populated:
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

    def sum_daily_milk(self, cows) -> float:
        """
        sums the daily milk production across all cows

        Parameters
        ----------
        cows: List
            the list of cows in the animal manager class

        Returns
        -------
        float: The total milk produced in the herd (kg milk/day)
        """
        return sum(cow.estimated_daily_milk_produced for cow in cows)

    def gather_cow_class_history(self, cow_class) -> None:
        """
        Gathers all the pen history data for a given cow class type. Checks the current pen
        and pen composition of all animals of a given cow class, before then updating the
        pen history for that class using the update_pen_history() method

        Parameters
        ----------
        cow_class : List
            list of instances of whatever cow type's pen history is being gathered
        """
        for cow in cow_class:
            current_pen_id = self.animal_to_pen_id_map[cow.id]
            classes_in_pen = self.all_pens[current_pen_id].classes_in_pen
            cow.update_pen_history(current_pen_id, self.simulation_day, classes_in_pen)

    def record_pen_history(self) -> None:
        """
        Records the pen history of all of the animals.
        """
        self.gather_cow_class_history(self.calves)
        self.gather_cow_class_history(self.heiferIs)
        self.gather_cow_class_history(self.heiferIIs)
        self.gather_cow_class_history(self.heiferIIIs)
        self.gather_cow_class_history(self.cows)

    def calc_p_rqmts(self) -> None:
        """
        Calls each pen's method to calculate each animal's phosphorus
        requirements. This method is called daily.

        """
        for pen in self.all_pens:
            if pen.populated:
                pen.call_p_rqmts()

    def daily_p_update(self) -> None:
        """
        Calls each pen's method to calculate each animal's daily phosphorus
        update. This method is called daily.
        """
        for pen in self.all_pens:
            if pen.populated:
                pen.daily_p_update()

    def end_ration_interval(self) -> int:
        """
        Checks if a new ration should be formulated for the current simulation_day.

        Returns: 1 (True) if today is the day a new ration has to be formulated,
                0 (False) otherwise.
        """
        return self.simulation_day % self.formulation_interval == 1 or self.formulation_interval == 1 or \
            self.simulation_day == 0

# TODO revisit this method
    def annual_reset(self) -> None:
        pass

    def generate_animal_output(self, animal_type: str, index: int):
        """
        Returns the information (ID, breed, birthday, breeding method,
        semen used, pen history, bodyweight history, milk production history,
        event history) of the animal at the index of the respective
        animal_type list.

        Parameters
        ----------
        animal_type : str
            One of 'calf', 'heiferI', 'heiferII',
            'heiferIII', 'cow', 'sold_heifer', or 'culled cow'
        index : int
            the index of the animal in the respective animal_type list
            whose information will be returned

        Returns
        -------
        Dict with an animal of animal_type's information. Not
            all information is available for each animal_type.

        """
        is_cow = False
        is_heifer_repr = False  # True if animal is heiferII or heiferIII
        # TODO reevaluate the above, as Life Cycle refactor may have better method for assignment

        if animal_type == 'calf':
            animal = self.calves[index]
        elif animal_type == 'heiferI':
            animal = self.heiferIs[index]
        elif animal_type == 'heiferII':
            animal = self.heiferIIs[index]
            is_heifer_repr = True
        elif animal_type == 'heiferIII':
            animal = self.heiferIIIs[index]
            is_heifer_repr = True
        elif animal_type == 'cow':
            animal = self.cows[index]
            is_cow = True
        elif animal_type == 'sold_heifer':
            animal = self.life_cycle_manager.sold_heifers[index]
            is_heifer_repr = True
        else:  # animal_type == 'culled_cow':
            animal = self.life_cycle_manager.culled_cows[index]
            is_cow = True

        CI_avg = None
        if is_cow:
            if len(animal.CI_history) == 0:
                CI_avg = 0
            else:
                CI_avg = sum(animal.CI_history) / len(animal.CI_history)

        return animal, is_cow, {
            'ID': animal.id,
            'breed': animal.breed,
            'birthday': animal.birth_date,
            'repro_program': None if not is_cow else animal.repro_program,
            'tai_method_h': None if not is_heifer_repr else animal.tai_method_h,
            'synch_ed_method_h':
                None if not is_heifer_repr else animal.synch_ed_method_h,
            'presynch_method': None if not is_cow else animal.presynch_method,
            'tai_method_c': None if not is_cow else animal.tai_method_c,
            'resynch_method': None if not is_cow else animal.resynch_method,
            'semen_used': animal.semen_used,
            'pen_history':
                [pen_hist.__dict__ for pen_hist in animal.pen_history],
            'event_history': animal.events.events,
            'CI_avg': CI_avg
        }

    def get_life_cycle_output(self, num_animals: int) -> Tuple[List[Tuple[AnimalBase, str, bool]],
                                                               Dict[str, Dict | int]]:
        """
        Returns the life cycle output on an individual level, which is the
        information of some of each type of animal as well as some animal
        statistics.

        Parameters
        ----------
        num_animals: int
            the number of each type of animal (calves, heiferIs, heiferIIs, heiferIIIs, cows, sold_heifers, and
            culled_cows) for which information will be collected and returned. If num_animals is largerthan the minimum
            length of the animal lists, then num_animals will be set to the minimum length of the animal lists.

        Returns : Tuple[List[Tuple[AnimalBase, str, bool]], Dict[str, Dict | int]]
            A list of animals, and a dictionary which contains the individual life cycle output.

        """
        minimum_num = min(len(self.calves), len(self.heiferIs),
                          len(self.heiferIIs), len(self.heiferIIIs),
                          len(self.cows),
                          len(self.life_cycle_manager.sold_heifers),
                          len(self.life_cycle_manager.culled_cows))

        info_map = {"class": self.__class__.__name__,
                    "function": self.get_life_cycle_output.__name__,
                    "num_animals": num_animals,
                    "minimum_num": minimum_num, }

        if num_animals > minimum_num:
            om.add_warning("invalid_animal_list_size",
                           f"The smallest animal list is of size {minimum_num}"
                           + f" so {num_animals} of each animal class cannot be"
                           + f" in the life cycle output. Only {minimum_num} of"
                           + " each animal type will be in the life cycle output.",
                           info_map)
            num_animals = minimum_num

        output = {
            'calves': {},
            'heiferIs': {},
            'heiferIIs': {},
            'heiferIIIs': {},
            'cows': {},
            'sold_heifers': {},
            'culled_cows': {},
            'num_calves_sold': 0,
            'num_sold_heifers': 0,
            'num_cows_culled': 0
        }
        animals = []
        indices = random.sample(range(len(self.calves)), num_animals)
        for i in indices:
            animal, is_cow, output['calves'][i] = \
                self.generate_animal_output('calf', i)
            animals.append((animal, 'calf', is_cow))

        indices = random.sample(range(len(self.heiferIs)), num_animals)
        for i in indices:
            animal, is_cow, output['heiferIs'][i] = \
                self.generate_animal_output('heiferI', i)
            animals.append((animal, 'heiferI', is_cow))

        indices = random.sample(range(len(self.heiferIIs)), num_animals)
        for i in indices:
            animal, is_cow, output['heiferIIs'][i] = \
                self.generate_animal_output('heiferII', i)
            animals.append((animal, 'heiferII', is_cow))

        indices = random.sample(range(len(self.heiferIIIs)), num_animals)
        for i in indices:
            animal, is_cow, output['heiferIIIs'][i] = \
                self.generate_animal_output('heiferIII', i)
            animals.append((animal, 'heiferIII', is_cow))

        indices = random.sample(range(len(self.cows)), num_animals)
        for i in indices:
            animal, is_cow, output['cows'][i] = \
                self.generate_animal_output('cow', i)
            animals.append((animal, 'cow', is_cow))

        indices = random.sample(
            range(len(self.life_cycle_manager.sold_heifers)), num_animals)
        for i in indices:
            animal, is_cow, output['sold_heifers'][i] = \
                self.generate_animal_output('sold_heifer', i)
            animals.append((animal, 'sold_heifer', is_cow))

        indices = random.sample(
            range(len(self.life_cycle_manager.culled_cows)), num_animals)
        for i in indices:
            animal, is_cow, output['culled_cows'][i] = \
                self.generate_animal_output('culled_cow', i)
            animals.append((animal, 'culled_cow', is_cow))

        output['num_calves_sold'] = self.life_cycle_manager.sold_calf_num
        output['num_sold_heifers'] = len(self.life_cycle_manager.sold_heifers)
        output['num_cows_culled'] = len(self.life_cycle_manager.culled_cows)

        return animals, output

    def get_initialize_db_summary(self) -> InitializationDBSummaryTypedDict:
        """

        Returns
        -------
        InitializationDBSummaryTypedDict
            a dictionary which is the summary of the animal initialization database

        """
        return self.life_cycle_manager.initialize_db_summary

    @classmethod
    def _calc_phosphorus_concentration(cls, animals) -> float:
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
            self.phosphorus_concentration_by_animal_class[animal_type] = \
                self._calc_phosphorus_concentration(animals)

    def _calc_ration_at_interval(self, feed):
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

                counter = 1
                while 'status' not in ration_per_animal or ration_per_animal['status'].lower() != 'optimal':
                    if pen.animal_combination == Pen.AnimalCombination.CALF:
                        ration_per_animal = CalfRationManager.optimize()
                        ration_vals = {'ME_total': 0}

                    else:
                        ration_per_animal, ration_vals = \
                            RationManager.formulate_ration(pen, pen_specific_feed_data, self.ANIMAL_GROUPING_SCENARIO)

                    # TODO: Remove this check before merging to master
                    counter += 1
                    if counter > 50:
                        raise Exception('Too many attempts at optimizing ration.')

                # recording ration nutrition information in pen
                nutrient_amount, nutrient_conc = RationReporter.report_ration(ration_per_animal, feed.available_feeds)
                pen.ration_nutrient_amount = nutrient_amount
                pen.ration_nutrient_conc = nutrient_conc
                pen.MEdiet = ration_vals['ME_total']
                pen.dry_matter_intake = nutrient_amount['dm']

                ration_report = {}
                ration_report['nutrient_amount'] = nutrient_amount
                ration_report['nutrient_conc'] = nutrient_conc

                for animal in pen.animals_in_pen:
                    animal.set_ration(ration_per_animal, nutrient_amount['dm'])
                    animal.set_p_intake(nutrient_amount['phosphorus'], nutrient_conc['phosphorus'])

                ration_per_pen = {}
                num_animals = len(pen.animals_in_pen)
                for key in ration_per_animal:
                    if key == 'status':
                        ration_per_pen[key] = ration_per_animal[key]
                    else:  # feeds and price
                        ration_per_pen[key] = ration_per_animal[key] * num_animals

                pen.ration = ration_per_pen
                pen.ration_per_animal = ration_per_animal  # Important

                info_map = {"class": self.__class__.__name__,
                            "function": self._calc_ration_at_interval.__name__,
                            f'number_animals_in_pen_{pen.id}': len(pen.animals_in_pen)}
                om.add_variable(f'ration_nutrient_amount_pen_{pen.id}', nutrient_amount, info_map)
                om.add_variable(f'MEdiet_pen_{pen.id}', pen.MEdiet, info_map)
                om.add_variable(f'avg_rqmts_pen_{pen.id}', pen.avg_nutrient_rqmts, info_map)
                om.add_variable(f'ration_per_animal_for_pen_{pen.id}', pen.ration_per_animal, info_map)
                if pen.animal_combination != Pen.AnimalCombination.CALF:
                    ration_supply_report = RationReporter.report_ration_supply(ration_per_animal,
                                                                               feed.available_feeds,
                                                                               ration_report,
                                                                               pen.avg_nutrient_rqmts['avg_BW'])
                    om.add_variable(f'ration_supply_report_for_pen_{pen.id}', ration_supply_report, info_map)

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
        for animal in pen.animals_in_pen:
            animal_type = cls.ANIMAL_GROUPING_SCENARIO.get_animal_type(animal)
            animal_types_in_pen.add(animal_type)

        return animal_types_in_pen

    @classmethod
    def _get_classes_in_pen(cls, pen: Pen) -> Set[str]:
        """
        Get the classes of animals in the pen.

        TODO: Eventually, we want to get rid of this method and use _get_animal_types_in_pen() instead.

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
            'calves': set(self.calves),
            'heiferIs': set(self.heiferIs),
            'heiferIIs': set(self.heiferIIs),
            'heiferIIIs': set(self.heiferIIIs),
            'cows': set(self.cows),
            'animal_combination_by_id': {}
        }
        for animal in [*self.calves, *self.heiferIs, *self.heiferIIs, *self.heiferIIIs, *self.cows]:
            snapshot['animal_combination_by_id'][animal.id] = \
                self.ANIMAL_GROUPING_SCENARIO.find_animal_combination(animal)
        return snapshot

    def _handle_removed_animals_after_update(self, animals_snapshot_before_update: Dict,
                                             animals_snapshot_after_update: Dict) -> None:
        """
        Identifies and handles animals that were present prior to the update, but not afterwards.

        This function detects any animals that have been removed between updates (e.g., due to graduation,
        being sold, or being culled), and then updates the internal state accordingly by calling
        '_remove_animal_from_pen_and_id_map' for each removed animal.

        Parameters
        ----------
        animals_snapshot_before_update : dict
            A snapshot of the state of all the animals before the update. This dictionary uses
            animal class names as keys ('calves', 'heiferIs', etc.) and sets of animal instances
            as values.

        animals_snapshot_after_update : dict
            A snapshot of the state of all the animals after the update. This dictionary should
            have the same structure as `animals_snapshot_before_update`.

        Returns
        -------
        None
            This function doesn't return any value. Its purpose is to modify the internal state of the
            class instance by calling '_remove_animal_from_pen_and_id_map' for each animal that
            has been removed.
        """
        animal_class_names = ['calves', 'heiferIs', 'heiferIIs', 'heiferIIIs', 'cows']

        # Reasons for removal: graduated, sold, culled
        removed_animals = set()
        for animal_type_name in animal_class_names:
            removed_animals.update(animals_snapshot_before_update[animal_type_name]
                                   - animals_snapshot_after_update[animal_type_name])

        for animal in removed_animals:
            self._remove_animal_from_pen_and_id_map(animal)

    def _handle_animals_with_unchanged_class_and_changed_combination(self, animals_snapshot_before_update: Dict,
                                                                     animals_snapshot_after_update: Dict,
                                                                     feed, temp: float):
        """
        Handle animals that didn't change their classes but changed their animal combination.

        The reason for the change in animal combination is that the animal's physiological states have changed.
        Because each pen is associated with a specific animal combination, the animal needs to be moved to
        a different pen with the new animal combination.

        For example, a cow can be in the dry state or lactating state, but depending on the
        current state of the cow, she can be in a different pen with a different animal combination.

        Parameters
        ----------
        animals_snapshot_before_update : dict
            Snapshot of the animals before the update. This should be a dictionary with animal
            class names as keys and sets of animals as values. There should also be a special key
            'animal_combination_by_id' that maps animal IDs to their animal combinations.
        animals_snapshot_after_update : dict
            Snapshot of the animals after the update. This should be a dictionary with the same
            structure as animals_snapshot_before_update.
        feed : Feed
            Instance of the Feed class.
        temp : float
            Current temperature.

        Returns
        -------
        None
            This function does not return anything. It operates by side effects, changing the
            assignments of animals to pens.

        """
        animal_class_names = ['calves', 'heiferIs', 'heiferIIs', 'heiferIIIs', 'cows']
        animals_with_unchanged_class = set()
        for animal_class_name in animal_class_names:
            animals_with_unchanged_class.update(animals_snapshot_before_update[animal_class_name]
                                                & animals_snapshot_after_update[animal_class_name])
        animals_with_unchanged_class_and_changed_combination = set()
        for animal in animals_with_unchanged_class:
            if animals_snapshot_before_update['animal_combination_by_id'][animal.id] \
                    != animals_snapshot_after_update['animal_combination_by_id'][animal.id]:
                animals_with_unchanged_class_and_changed_combination.add(animal)

        for animal in animals_with_unchanged_class_and_changed_combination:
            self._remove_animal_from_pen_and_id_map(animal)
            self._add_animal_to_pen_and_id_map(animal, feed, temp)

    def _handle_graduated_animals(self, animals_snapshot_before_update,
                                  animals_snapshot_after_update,
                                  feed: Feed, temp: float) -> None:
        """
        Finds animals that have graduated (moved from one class to another), moves them between pens,
         and updates pen id map accordingly.

        Parameters
        ----------
        animals_snapshot_before_update : TODO

        animals_snapshot_after_update : TODO

        feed : Feed
            instance of the Feed class defined in feed.py.
        temp : float
            The temperature on the current day.

        """
        graduated_animals = set()
        for animal_class_name in ['heiferIs', 'heiferIIs', 'heiferIIIs', 'cows']:
            graduated_animals.update(animals_snapshot_after_update[animal_class_name]
                                     - animals_snapshot_before_update[animal_class_name])
        for animal in graduated_animals:
            self._add_animal_to_pen_and_id_map(animal, feed, temp)

    def _handle_newly_added_animals(self, new_animals: List[Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]],
                                    feed: Feed, temp: float) -> None:
        """
        For all new animals, adds animal to a pen, and updates the pen id map.

        Parameters
        ----------
        animal : List[Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]]
            One of the possible animal types.
        feed : Feed
            instance of the Feed class defined in feed.py.
        temp : float
            The temperature on the current day.

        """
        for animal in new_animals:
            self._add_animal_to_pen_and_id_map(animal, feed, temp)
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

    def _add_animal_to_pen_and_id_map(self, animal: Union[Calf, HeiferI, HeiferII, HeiferIII, Cow], feed: Feed,
                                      temp: float) -> None:
        """
        Adds animal to pen with lowest stocking density, and updates the pen id map accordingly.

        Parameters
        ----------
        animal : Union[Calf, HeiferI, HeiferII, HeiferIII, Cow]
            One of the possible animal types.
        feed : Feed
            instance of the Feed class defined in feed.py.
        temp : float
            The temperature on the current day.

        """
        animal_combination = self.ANIMAL_GROUPING_SCENARIO.find_animal_combination(animal)
        pen_with_min_stocking_density = min(self.pens_by_animal_combination[animal_combination],
                                            key=lambda p: p.current_stocking_density)
        pen_with_min_stocking_density.add_animal(animal, self.ANIMAL_GROUPING_SCENARIO,
                                                 feed, temp,
                                                 self.phosphorus_concentration_by_animal_class[type(animal)])
        self.animal_to_pen_id_map[animal.id] = pen_with_min_stocking_density.id

    def daily_updates(self, feed, weather: Weather, time: Time):
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
            temp = current_conditions.mean_air_temperature
            animals_snapshot_before_update = self._get_animals_snapshot()

            animals_added, animals_removed, calves_born, *rest = \
                self.life_cycle_manager.daily_update(self.simulation_day, self.calves,
                                                     self.heiferIs, self.heiferIIs,
                                                     self.heiferIIIs, self.cows)

            animals_snapshot_after_update = self._get_animals_snapshot()

            self._handle_removed_animals_after_update(
                animals_snapshot_before_update, animals_snapshot_after_update
            )
            self._handle_animals_with_unchanged_class_and_changed_combination(
                animals_snapshot_before_update, animals_snapshot_after_update, feed, temp
            )

            self._handle_graduated_animals(
                animals_snapshot_before_update, animals_snapshot_after_update, feed, temp
            )

            self._handle_newly_added_animals([*animals_added, *calves_born], feed, temp)

            info_map = {"class": self.__class__.__name__, "function": self.daily_updates.__name__}
            om.add_variable('sim_day', self.simulation_day, info_map)
            om.add_variable('num_animals', len(self.calves) + len(self.heiferIs) + len(self.heiferIIs) +
                            len(self.heiferIIIs) + len(self.cows), info_map)
            om.add_variable('num_calves', len(self.calves), info_map)
            om.add_variable('num_heiferIs', len(self.heiferIs), info_map)
            om.add_variable('num_heiferIIs', len(self.heiferIIs), info_map)
            om.add_variable('num_heiferIIIs', len(self.heiferIIIs), info_map)
            om.add_variable('num_lactating_cows', len([cow for cow in self.cows if cow.is_lactating]), info_map)
            om.add_variable('num_dry_cows', len([cow for cow in self.cows if not cow.is_lactating]), info_map)

            manure_excretions_output_data = {}
            for pen in self.all_pens:
                pen.classes_in_pen = self._get_classes_in_pen(pen)
                pen.calc_total_manure(feed, self.methane_model, self.methane_mitigation_method,
                                      self.methane_mitigation_additive_amount,
                                      manure_excretions_output_data)
                pen.call_p_rqmts()
                pen.daily_p_update()  # Average phosphorus concentration per pen

            for output_data_dict in manure_excretions_output_data.values():
                for manure_property, manure_value in output_data_dict['manure'].items():
                    info_map = {
                        'class': self.__class__.__name__,
                        'function': self.daily_updates.__name__,
                    }
                    om.add_variable(f'{output_data_dict["prefix"]}_{str(manure_property)}',
                                    manure_value,
                                    info_map=info_map)

            self._update_phosphorus_concentrations()  # Average phosphorus concentration per animal type
            self.record_pen_history()

            if self.end_ration_interval():
                self.reset_milk_production_reduction()
                self.calc_nutrient_rqmts(feed, temp)  # per animal
                self.clear_pens()
                self.allocate_animals_to_pens()
                self._calc_ration_at_interval(feed)  # per pen
                self.calc_avg_growth()  # per pen
                for pen in self.all_pens:
                    if pen.animal_combination.name == 'LAC_COW':
                        for animal in pen.animals_in_pen:
                            animal.update_milk_production_history(self.simulation_day)

            self.life_cycle_manager.daily_milk_production = self.sum_daily_milk(self.cows)
