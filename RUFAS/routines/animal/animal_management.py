"""
RUFAS: Ruminant Farm Systems Model
File name: animal_management.py

Description: The class which manages all of the animal routines and keeps track of
    all animals and pens. All operations are as described in the Animal Module
    Information Flow document on Basecamp (such as daily animal updates and
    pen allocation). Method calls cascade through from the animal management
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
from typing import Any, Dict, Tuple, List

from RUFAS.general_constants import GeneralConstants
from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.routines.animal.clustering_pen_grouping import grouping
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.life_cycle import LifeCycleManager
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.animal.ration import ration_driver as ration_driver

om = OutputManager()


def daily_animal_routine(animal_management, feed, weather, time):
    """
    Executes daily routines relating to Animals. This method is called every day
    in the simulation and calls @animal_management's daily_updates() method
    with @feed and @time as arguments. [Note that currently, @weather and
    @ time are not used in animal updates.]

    Args:
        animal_management: instance of the AnimalManagement class
        feed: instance of the Feed class
        weather: instance of the Weather class as defined in classes.py
        time: instance of the Time class as defined in classes.py
    """

    animal_management.daily_updates(feed, weather, time)


class AnimalManagement:
    """
    Manages all animal routines (i.e. calling daily updates, allocating animals
    to pens, etc). Stores a list of all animals and pens in the simulation as
    well as an instance of the LifeCycleManager class in order to update the
    animals' life cycles.
    """

    DEFAULT_NUM_STALLS_BY_COMBINATION = {
        Pen.AnimalCombination.CALF: AnimalModuleConstants.DEFAULT_NUM_STALLS_FOR_CALF_PEN,
        Pen.AnimalCombination.GROWING: AnimalModuleConstants.DEFAULT_NUM_STALLS_FOR_GROWING_PEN,
        Pen.AnimalCombination.CLOSE_UP: AnimalModuleConstants.DEFAULT_NUM_STALLS_FOR_CLOSE_UP_PEN,
        Pen.AnimalCombination.LAC_COW: AnimalModuleConstants.DEFAULT_NUM_STALLS_FOR_LAC_COW_PEN
    }

    @staticmethod
    def get_animal_config(data):
        config = {}
        config.update(data['management_decisions'])
        config.update(data['farm_level']['calf'])
        config.update(data['farm_level']['repro']['ED_related'])
        config.update(data['farm_level']['repro']['TAI_related'])
        config.update(data['farm_level']['repro'])
        config.update(data['farm_level']['bodyweight'])
        config.update(data['from_literature']['repro'])
        config.update(data['from_literature']['milking'])
        config.update(data['from_literature']['culling'])
        config.update(data['from_literature']['life_cycle'])
        return config

    def __init__(self, data, config, feed, weather, time):
        """
        Initializes the pens and animals in the simulation with data from the
        JSON file by calling init_pens() and init_animals(). Creates instance
        of LifeCycleManager class and sets up the animal environment.

        Args:
            data: dictionary with animal information from the input JSON file
            config: instance of the Config class
            feed: instance of the Feed class
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
        self.all_pens = []

        # dictionary: key is animal ID, value is the pen ID that animal is in
        self.id_pen = {}

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
        # in calc_all_p_conc() and are calculated by dividing the total P in the animals
        # of the class by the total body weight of the animals, on a per-animal basis
        self.p_conc = {
            'calf': 0,
            'heiferI': 0,
            'heiferII': 0,
            'heiferIII': 0,
            'cow': 0
        }

        # housing type: barn or pasture
        self.housing = data['housing']

        # concentrate supplementation when farming type is "pasture", kg
        self.pasture_concentrate = data['pasture_concentrate']

        self.ration_user_input = data['ration']['user_input']

        # how often a ration is calculated, days
        self.formulation_interval = data['ration']['formulation_interval']

        self.methane_model = data['methane_model']

        # Minimum number of pens in the simulation (for default pen initialization)
        self.MIN_NUM_PENS = 3

        self.init_pens(data['pen_information'], data['herd_information'], data['manure_management_scenarios'])

        if self.simulate_animals:
            self.init_animals(config, data['herd_information'])

            self.init_nutrient_rqmts(weather, time, feed)

            # self.allocate_all_pens()
            self.allocate_animals_to_pens()

        self._print_animal_num_warnings(data['herd_information'])

    def init_pens(self, all_pen_data, herd_data: Dict[str, Any], manure_management_scenarios):
        """
        Populates the list of pens with the information from the input json file.
        Args:
            all_pen_data: dictionary containing information about the pens
            herd_data: dictionary containing information about the herd
            manure_management_scenarios: dictionary containing information about the manure management scenarios
        """

        # Initialize pens from all_pen_data
        for pen_data in all_pen_data.values():
            pen_data['pen_id'] = pen_data.pop('id')
            pen_data['animal_combination'] = Pen.AnimalCombination[pen_data.pop('animal_combination')]

            manure_management_scenario_id = pen_data.pop('manure_management_scenario_id')
            manure_management_scenario = [scenario for scenario in manure_management_scenarios
                                          if scenario['scenario_id'] ==
                                          manure_management_scenario_id][0]
            pen_data['bedding_type'] = manure_management_scenario['bedding_type']
            pen_data['manure_handling'] = manure_management_scenario['manure_handler']
            pen_data['manure_separator'] = manure_management_scenario['manure_separator']
            pen_data['manure_storage'] = manure_management_scenario['manure_treatment']

            pen = Pen(**pen_data)

            self.all_pens.append(pen)

        self._init_default_pens(herd_data['herd_num'])

    def _init_default_pens(self, herd_num):
        """
            Initializes default pens if not enough exist in the simulation.
            Args:
                herd_num: number of animals in the herd
            """

        num_pens = len(self.all_pens)
        num_additional_pens_needed = self.MIN_NUM_PENS - len(self.all_pens)

        info_map = {"class": self.__class__.__name__,
                    "function": self.init_pens.__name__,
                    "MIN_NUM_PENS": self.MIN_NUM_PENS,
                    "num_pens": num_pens,
                    "num_additional_pens_needed": num_additional_pens_needed
                    }

        # Check if any default pens need to be added
        if num_additional_pens_needed > 0 and herd_num > 0:
            om.add_warning("invalid_pen_num_warning",
                           f"Warning: herd_num > 0, but num_pens = {num_pens}."
                           + f" Initializing {num_additional_pens_needed} additional pens.",
                           info_map)
            for i in range(num_additional_pens_needed):
                new_default_pen = Pen(0, 0.1, 1.6, 100, 'open air barn', 'sawdust', 'freestall',
                                      "manual scraping", "screw press", "slurry storage outdoor",
                                      Pen.AnimalCombination.NONE, 1.2)
                self.all_pens.append(new_default_pen)

    def init_animals(self, config, herd_data: Dict[str, Any]):
        """
        Populates the list of animals with the information from the
        input JSON file: constructs the calves, heiferI’s, heiferII’s,
        heiferIII’s, and cows (the desired amounts of each is specified by
        @data), then calls life_cycle_manager's initialize_herd() with those
        numbers to create instances of the animals. The nutrient requirements
        are calculated and the animals are allocated to pens.

        Args:
            config: an instance of the Config class defined in classes.py
                contains model configuration information
            herd_data: dictionary containing information about the herd
        """

        self.calves, self.heiferIs, self.heiferIIs, self.heiferIIIs, self.cows \
            = self.life_cycle_manager.initialize_herd(config, herd_data)

    def _print_animal_num_warnings(self, herd_data: Dict[str, Any]):
        """
        If simulate_animals is false, creates warnings if there are more than 0 animals for any of the animal types,
            and logs how many warnings were generated
        Otherwise, if simulate_animals is true, logs that it is true

        Args:
            herd_data: dictionary containing information about the herd
        """

        animal_keys = {"calf_num", "heiferI_num", "heiferII_num", "heiferIII_num", "cow_num"}

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

    def init_nutrient_rqmts(self, weather, time, feed):
        """
        Calculates initial nutrient requirements at the beginning of the
        simulation for initial pen allocation. For the nutrient requirements
        of cows, the average walking distance of all the pens initialized
        is used.

        Args:
            feed: an instance of the Feed class defined in feed.py
            weather: instance of the Weather class defined in classes.py
            time: instance of the Time class defined in classes.py
        """

        # average vertical & horizontal distance (VD, HD) of pens to the
        # milking parlor
        # avg_VD_parlor, avg_HD_parlor = self.avg_pen_dist()
        for calf in self.calves:
            temp = weather.T_avg[time.year - 1][time.day - 1]
            calf.calc_nutrient_rqmts(feed, temp)
            calf.p_animal = 0.0072 * calf.body_weight * 1000

        for heiferI in self.heiferIs:
            heiferI.set_nutrient_rqmts(temp)
            heiferI.p_animal = 0.0072 * heiferI.body_weight * 1000

        for heiferII in self.heiferIIs:
            heiferII.set_nutrient_rqmts(temp)
            heiferII.p_animal = 0.0072 * heiferII.body_weight * 1000

        for heiferIII in self.heiferIIIs:
            heiferIII.set_nutrient_rqmts(temp)
            heiferIII.p_animal = 0.0072 * heiferIII.body_weight * 1000

        for cow in self.cows:
            cow.set_nutrient_rqmts()
            cow.p_animal = 0.0072 * cow.body_weight * 1000

    def avg_pen_dist(self) -> Tuple[float, float]:
        """
        Calculates the average distance from a pen to the milking parlor.
        Returns: a tuple of (average vertical distance from milking parlor,
            average horizontal distance from milking parlor)
        """

        return mean(pen.vertical_dist_to_parlor for pen in self.all_pens), \
            mean(pen.horizontal_dist_to_parlor for pen in self.all_pens)

    def calc_nutrient_rqmts(self, feed, temp):
        """
        Calls each animal's method to calculate its nutrient requirements.

        Args:
            feed: instance of the feed class
            temp: the temperature on the current day
        """
        for calf in self.calves:
            calf.calc_nutrient_rqmts(feed, temp)

        for heiferI in self.heiferIs:
            heiferI.set_nutrient_rqmts(temp)

        for heiferII in self.heiferIIs:
            heiferII.set_nutrient_rqmts(temp)

        for heiferIII in self.heiferIIIs:
            heiferIII.set_nutrient_rqmts(temp)

        for cow in self.cows:
            cow.set_nutrient_rqmts()

    def fully_update_id_pen(self):
        """
        Updates the entire id_pen dictionary so that each animal's ID is
        associated with the pen that animal is in.
        """
        for pen in self.all_pens:
            animals_in_pen = pen.animals_in_pen
            for animal in animals_in_pen:
                self.id_pen[animal.id] = pen.id

    def daily_update_id_pen(self, animals_added, ids_removed, calves_born, feed, temp):
        """
        For animals removed from the herd in daily animal updates, the ids of
        the pens from which they were removed are stored in the
        pens_needing_animals queue.
        Animals added to the herd from the replacement herd are temporarily
        assigned to a pen that had animals removed from it.
        Calves that were born are assigned (currently) to the hard coded pen
        for calves.
        All new animals are set up with the characteristics of the pen to which
        they were assigned.

        Args:
            animals_added: list of animal IDs that have been added to the herd
            ids_removed: list of animal IDs that have been removed from the herd
            calves_born: list of Calf objects that have been added to the herd
            feed: an instance of the Feed class defined in feed.py
            temp: the temperature on the current day
        """

        # stratifying the pens that lost animals by animal group
        # (values are dictionaries of pen IDs, with values being the number of animals removed)
        grouped_pens_short = {Pen.AnimalCombination.CALF: {}, Pen.AnimalCombination.GROWING: {},
                              Pen.AnimalCombination.CLOSE_UP: {}, Pen.AnimalCombination.GROWING_AND_CLOSE_UP: {},
                              Pen.AnimalCombination.LAC_COW: {}}
        for i in ids_removed:
            if i in self.id_pen:
                pen = self.all_pens[self.id_pen[i]]
                # adding count to animals that left pen
                if pen.id in grouped_pens_short[pen.animal_combination]:
                    grouped_pens_short[pen.animal_combination][pen.id] += 1
                else:
                    grouped_pens_short[pen.animal_combination][pen.id] = 1

                del self.id_pen[i]

        pen_population_before_additions = {}
        for i, pen in enumerate(self.all_pens):
            pen_population_before_additions[i] = len(pen.animals_in_pen)

        for animal in animals_added:
            if type(animal).__name__ == 'Calf':
                animal_p_conc = self.p_conc['calf']
                self.calves.append(animal)
                group = Pen.AnimalCombination.CALF
            elif type(animal).__name__ == 'HeiferI':
                animal_p_conc = self.p_conc['heiferI']
                self.heiferIs.append(animal)
                group = Pen.AnimalCombination.GROWING
            elif type(animal).__name__ == 'HeiferII':
                animal_p_conc = self.p_conc['heiferII']
                self.heiferIIs.append(animal)
                group = Pen.AnimalCombination.GROWING
            elif type(animal).__name__ == 'HeiferIII':
                animal_p_conc = self.p_conc['heiferIII']
                self.heiferIIIs.append(animal)
                group = Pen.AnimalCombination.CLOSE_UP
            elif not animal.milking:
                animal_p_conc = self.p_conc['cow']
                self.cows.append(animal)
                group = Pen.AnimalCombination.CLOSE_UP
            else:  # animal is of class Cow
                animal_p_conc = self.p_conc['cow']
                # self.all_pens[pen].animals_in_pen.append(animal)
                self.cows.append(animal)
                group = Pen.AnimalCombination.LAC_COW

            # Choosing pen to place new animal first by checking if there are
            # pens that lost animals, and choosing the pen with the lowest
            # stocking density
            # if there are no pens of group calves that lost animals
            if grouped_pens_short[group] == {}:
                # variable to track lowest stocking density
                dens = 10000
                for p in self.pens_by_animal_combination[group]:
                    if p.stocking_density < dens:
                        pen = p
                        dens = p.stocking_density
            # if there are pens of group calves that lost animals
            else:
                # variable to track highest animal shortage across these pens
                n = 0
                for id, v in grouped_pens_short[group].items():
                    if v > n:
                        pen = self.all_pens[id]
                        n = v

            # updating id_pen variable
            self.id_pen[animal.id] = pen.id
            # setting up new animal
            self.all_pens[pen.id].set_up_new_animal(animal, animal_p_conc,
                                                    feed, temp, pen_population_before_additions[pen.id])

        for i in range(len(self.all_pens)):
            if len(self.all_pens[i].animals_in_pen) > 0:
                if self.all_pens[i].ration == {}:
                    available_feeds = ration_driver.AvailableFeeds()
                    available_feeds.feed_nutrients(feed)
                    self.all_pens[i].allocated_feeds = feed.input_feed_combinations[self.all_pens[i].animal_combination]
                    pen_specific_feed_data = available_feeds.get_feed_data_from_feed_ids(
                        self.all_pens[i].allocated_feeds)
                    self.all_pens[i].ration = self.all_pens[i].calc_ration(feed, pen_specific_feed_data)
            else:
                if len(self.all_pens[i].animals_in_pen) > 0:
                    # Need to adjust the ration totals for the pen attributes now
                    # that all new animals have been added
                    for key in self.all_pens[i].ration:
                        if key != 'status' and key != 'objective' and pen_population_before_additions[i] > 0:
                            self.all_pens[i].ration[key] = \
                                (self.all_pens[i].ration[key] /
                                 pen_population_before_additions[i]) * len(
                                    self.all_pens[i].animals_in_pen)

        for calf in calves_born:
            # getting valid pen to place calves in
            # if there are no pens of group calves that lost animals
            pen = None
            if grouped_pens_short[Pen.AnimalCombination.CALF] == {}:
                # variable to track lowest stocking density
                dens = 10000
                for p in self.pens_by_animal_combination[Pen.AnimalCombination.CALF]:
                    if p.stocking_density < dens:
                        pen = p
                        dens = p.stocking_density
            # if there are pens of group calves that lost animals
            else:
                # variable to track highest animal shortage across these pens
                n = 0
                for id, v in grouped_pens_short[Pen.AnimalCombination.CALF].items():
                    if v > n:
                        pen = self.all_pens[id]
                        n = v
            self.id_pen[calf.id] = pen.id
            self.calves.append(calf)
            self.all_pens[pen.id].set_up_new_animal(calf, self.pasture_concentrate,
                                                    feed, temp, pen_population_before_additions[pen.id])
            # self.all_pens[pen].animals_in_pen.append(calf)

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
        >>> AnimalManagement._calc_max_animal_spaces_per_pen(num_stalls=10, max_stocking_density=1.5)
        15
        >>> AnimalManagement._calc_max_animal_spaces_per_pen(num_stalls=5, max_stocking_density=2.0)
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
            The shortage of animal spaces. If there is no shortage, the result will be 0.

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
        >>> pen = AnimalManagement._create_default_pen(pen_id=1, \
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
    def _allocate_animals_to_pens_helper(cls, animals, pens: List[Pen]) -> None:
        """
        Allocate animals to pens based on overall density while preventing overcrowding.

        This method distributes the animals among the available pens, ensuring that the density
        in each pen matches the overall density as closely as possible.

        Parameters
        ----------
        animals :
            A list of animal to be allocated to pens.
            # TODO: Add type hint for animals later
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
                                animals,
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

        animals
            A list of animals to be allocated among the pens.
            # TODO: Add type hint for animals later

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
        >>> AnimalManagement.plan_animal_allocation(num_animals=90, max_spaces_in_pens=[50, 30, 20])
        [45, 27, 18]

        >>> AnimalManagement.plan_animal_allocation(num_animals=70, max_spaces_in_pens=[50, 30, 20])
        [35, 21, 14]

        >>> AnimalManagement.plan_animal_allocation(num_animals=47, max_spaces_in_pens=[50, 30, 20])
        [22, 15, 10]

        """
        num_pens = len(max_spaces_in_pens)
        overall_density = cls._calc_density(num_animals=num_animals, num_spaces=sum(max_spaces_in_pens))

        if overall_density > 1.0:
            raise ValueError("The number of animals cannot exceed the total number of spaces.")

        num_animals_in_pens = [0] * num_pens
        allocation_limits = [math.ceil(overall_density * max_spaces) for max_spaces in max_spaces_in_pens]
        # Sort pens by allocation limit, then by index
        sorted_pen_indices = sorted(range(num_pens), key=lambda pen_idx: (allocation_limits[pen_idx], pen_idx))

        for i in sorted_pen_indices[:num_pens - 1]:
            num_animals_to_allocate = min(num_animals, allocation_limits[i])
            num_animals_in_pens[i] += num_animals_to_allocate
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

        self.pens_by_animal_combination = self._group_pens_by_animal_combination(self.all_pens)

        # For now, we are only considering the following animal combinations:
        animals_by_combination = {
            Pen.AnimalCombination.CALF: self.calves,
            Pen.AnimalCombination.GROWING: self.heiferIs + self.heiferIIs,
            Pen.AnimalCombination.CLOSE_UP: self.heiferIIIs + self._get_dry_cows(self.cows),
            Pen.AnimalCombination.LAC_COW: self._get_lactating_cows(self.cows),
        }

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

        self.fully_update_id_pen()

    def allocate_all_pens(self):
        # TODO: Refactor this function, currently nearly 200 lines long
        # TODO
        # -mark pens after grouping
        # -adding new animals to pens with lowest stocking density

        # separate into lactating and dry cow pens
        lactating_cows = []
        dry_cows = []
        for cow in self.cows:
            if cow.milking:
                lactating_cows.append(cow)
            else:
                dry_cows.append(cow)
        # lists for sorting the type of pen types
        # TODO: change these lists to a dictionary instead
        lac_cow_pens = []
        close_up_pens = []
        growing_pens = []
        calf_pens = []

        self.pens_by_animal_combination = {Pen.AnimalCombination.CALF: [], Pen.AnimalCombination.GROWING: [],
                                           Pen.AnimalCombination.CLOSE_UP: [],
                                           Pen.AnimalCombination.GROWING_AND_CLOSE_UP: [],
                                           Pen.AnimalCombination.LAC_COW: []}
        # hasable mixed type pens (by pen_id)
        mixed_type_pens = {}
        # lists of types hashed pen_id
        mixed_types = {}
        # dictionary showing the shortage of animals
        stall_shortage = {Pen.AnimalCombination.CALF: len(self.calves),
                          Pen.AnimalCombination.GROWING: len(self.heiferIs) + len(self.heiferIIs),
                          Pen.AnimalCombination.CLOSE_UP: len(self.heiferIIIs) + len(dry_cows),
                          Pen.AnimalCombination.LAC_COW: len(lactating_cows)}

        # sorting the available pen types
        # Pen types : [calf, growing, close_up, 'lac_cow']
        for pen in self.all_pens:

            if pen.animal_combination == Pen.AnimalCombination.CALF:
                calf_pens.append(pen)
                self.pens_by_animal_combination[Pen.AnimalCombination.CALF].append(pen)
                stall_shortage[Pen.AnimalCombination.CALF] -= pen.num_stalls * pen.max_stocking_density
            elif pen.animal_combination == Pen.AnimalCombination.GROWING:
                growing_pens.append(pen)
                self.pens_by_animal_combination[Pen.AnimalCombination.GROWING].append(pen)
                stall_shortage[Pen.AnimalCombination.GROWING] -= pen.num_stalls * pen.max_stocking_density
            elif pen.animal_combination == Pen.AnimalCombination.CLOSE_UP:
                close_up_pens.append(pen)
                self.pens_by_animal_combination[Pen.AnimalCombination.CLOSE_UP].append(pen)
                stall_shortage[Pen.AnimalCombination.CLOSE_UP] -= pen.num_stalls * pen.max_stocking_density
            elif pen.animal_combination == Pen.AnimalCombination.LAC_COW:
                lac_cow_pens.append(pen)
                self.pens_by_animal_combination[Pen.AnimalCombination.LAC_COW].append(pen)
                stall_shortage[Pen.AnimalCombination.LAC_COW] -= pen.num_stalls * pen.max_stocking_density
            else:
                # TODO: Update mixed_types and mixed_type_pens to use enum
                # also figure out what mixed type does
                mixed_type_pens[pen.id] = pen
                if pen.animal_combination == Pen.AnimalCombination.NONE:
                    mixed_types[pen.id] = [Pen.AnimalCombination.CALF, Pen.AnimalCombination.GROWING,
                                           Pen.AnimalCombination.CLOSE_UP, Pen.AnimalCombination.LAC_COW]
                else:
                    mixed_types[pen.id] = pen.animal_combination
        # organizing pens by class and ensuring sufficient storage
        info_map = {"class": self.__class__.__name__,
                    "function": self.allocate_all_pens.__name__,
                    "all_pens": self.all_pens, }
        while True:
            max_value = max(stall_shortage.values())
            if max_value > 0:
                max_key = [k for k, v in stall_shortage.items() if v == max_value]
                pen = None
                stalls = 0
                # finding best pen for group with max stall_shortage
                # (AKA, a pen that allows this group with most stalls)
                for key, val in mixed_types.items():
                    if (max_key[0] in val) and (mixed_type_pens[key].num_stalls > stalls):
                        pen = mixed_type_pens[key]
                        stalls = pen.num_stalls
                # if no available pens for this group in mixed types
                if pen is None:
                    om.add_warning("pen_shortage_warning",
                                   f"Warning: shortage of {max_key[0].name} pens,"
                                   + " initializing new pen,",
                                   info_map)
                    # initializing a default pen to be used for any class
                    pen = Pen(len(self.all_pens), 0.1, 1.6, max_value,
                              'open air barn', 'straw', 'tiestall', 'manual_scraping',
                              'sedimentation', 'storage_pit', max_key[0], 1.2)

                    self.all_pens.append(pen)
                # if available pen
                else:
                    del mixed_type_pens[pen.id]
                    del mixed_types[pen.id]

                # Assigning pen to relevant pen list
                if max_key[0].name == 'CALF':
                    calf_pens.append(pen)
                    self.pens_by_animal_combination[Pen.AnimalCombination.CALF].append(pen)
                elif max_key[0].name == 'GROWING':
                    growing_pens.append(pen)
                    self.pens_by_animal_combination[Pen.AnimalCombination.GROWING].append(pen)
                elif max_key[0].name == 'CLOSE_UP':
                    close_up_pens.append(pen)
                    self.pens_by_animal_combination[Pen.AnimalCombination.CLOSE_UP].append(pen)
                else:
                    lac_cow_pens.append(pen)
                    self.pens_by_animal_combination[Pen.AnimalCombination.LAC_COW].append(pen)
                # updating stall shortage
                stall_shortage[max_key[0]] -= pen.num_stalls * pen.max_stocking_density

            else:
                break

        ###########################
        # Assigning animals (sans Lactating Cows) to appropriate pens
        ###########################

        # Calf pen allocation
        stalls = [pen.num_stalls for pen in calf_pens]
        # density per-pen for even distribution across pens for calves
        density = len(self.calves) / sum(stalls)
        group = []
        for calf in self.calves:
            if len(group) / calf_pens[0].num_stalls <= density:
                group.append(calf)
            else:
                # condition to make sure all animals are grouped
                if len(calf_pens) > 1:
                    calf_pens[0].update_animals(group, Pen.AnimalCombination.CALF)
                    calf_pens.pop(0)
                    group = [calf]
        # final pen for this class
        calf_pens[0].update_animals(group, Pen.AnimalCombination.CALF)

        # Growing Pen Allocation
        stalls = [pen.num_stalls for pen in growing_pens]
        # density per-pen for even distribution
        density = (len(self.heiferIs) + len(self.heiferIIs)) / sum(stalls)
        group = []
        # grouping by heiferIs first
        for hef1 in self.heiferIs:
            if len(group) / growing_pens[0].num_stalls <= density:
                group.append(hef1)
            else:
                growing_pens[0].update_animals(group, Pen.AnimalCombination.GROWING)
                growing_pens.pop(0)
                group = [hef1]
        # continuing with heiferIIs
        for hef2 in self.heiferIIs:
            if len(group) / growing_pens[0].num_stalls <= density:
                group.append(hef2)
            else:
                if len(growing_pens) > 1:
                    growing_pens[0].update_animals(group, Pen.AnimalCombination.GROWING)
                    growing_pens.pop(0)
                    group = [hef2]
        # final pen for this class
        growing_pens[0].update_animals(group, Pen.AnimalCombination.GROWING)

        # Close_up Pen Allocation
        stalls = [pen.num_stalls for pen in close_up_pens]
        # density per-pen for even distribution
        density = (len(self.heiferIIIs) + len(dry_cows)) / sum(stalls)
        group = []
        # grouping by heiferIIs first
        for hef3 in self.heiferIIIs:
            if len(group) / close_up_pens[0].num_stalls <= density:
                group.append(hef3)
            else:
                close_up_pens[0].update_animals(group, Pen.AnimalCombination.CLOSE_UP)
                close_up_pens.pop(0)
                group = [hef3]
        # continuing with dry cows
        for cow in dry_cows:
            if len(group) / close_up_pens[0].num_stalls <= density:
                group.append(cow)
            else:
                if len(close_up_pens) > 1:
                    close_up_pens[0].update_animals(group, Pen.AnimalCombination.CLOSE_UP)
                    close_up_pens.pop(0)
                    group = [cow]
        # final pen for this class
        close_up_pens[0].update_animals(group, Pen.AnimalCombination.CLOSE_UP)

        # Lactating Cow Pen Allocation
        stalls = [pen.num_stalls for pen in lac_cow_pens]
        # density per-pen for even distribution
        density = len(lactating_cows) / sum(stalls)
        # Grouping for Lactating Cows
        pen_grouping = grouping(lactating_cows, lac_cow_pens, density)
        # Assigning Lactating Cows to Pens based on the grouping output
        for key in pen_grouping:
            lac_cow_pens[0].update_animals(pen_grouping[key], Pen.AnimalCombination.LAC_COW)
            lac_cow_pens.remove(lac_cow_pens[0])
        #####################

        self.fully_update_id_pen()

    def clear_pens(self):
        """
        Removes animals from pens for re-allocation. This is part of the
        routines that happen every ration interval.
        """

        for pen in self.all_pens:
            pen.clear()

    def calc_ration(self, feed):
        """
        Calls each pens's method to calculate the ration for that pen. This is
        part of the routines that happen every ration interval.

        Args:
            feed: instance of the Feed class
        """
        available_feeds = ration_driver.AvailableFeeds()
        available_feeds.feed_nutrients(feed)
        for i, pen in enumerate(self.all_pens):
            if pen.populated:
                pen.subset_class_feeds(feed)
                pen_specific_feed_data = available_feeds.get_feed_data_from_feed_ids(pen.allocated_feeds)
                self.all_pens[i].ration = self.all_pens[i].calc_ration(feed, pen_specific_feed_data)

    def calc_manure_excretion(self, feed, methane_model):
        """
        Calls each animal's method to calculate manure excretion to find the
        total for each pen. This is part of the routines that happen every
        ration interval.

        Args:
            feed: instance of the feed class
            methane_model: methane model used for methane emission calculations
        """
        for pen in self.all_pens:
            if pen.populated:
                pen.calc_manure(feed, methane_model)
            else:
                pen.reset_manure()

    def calc_avg_growth(self):
        """
        Calls each pen's method to calculate the average growth of animals in
        the pen. This is part of the routines that happen every
        ration interval.
        """

        for pen in self.all_pens:
            pen.calc_avg_growth()

    def gather_cow_class_history(self, cow_class):
        """
        Gathers all the pen history data for a given cow class type. Checks the current pen
        and pen composition of all animals of a given cow class, before then update the
        pen history for that class using the update_pen_history() method

        Args:
            cow_class: instance of whatever cow type's pen history is being gathered
        """
        for cow in cow_class:
            current_pen = self.id_pen[cow.id]
            classes_in_pen = self.all_pens[current_pen].classes_in_pen
            cow.update_pen_history(current_pen, self.simulation_day, classes_in_pen)

    def record_pen_history(self):
        """
        Records the pen history of all of the animals.
        """
        self.gather_cow_class_history(self.calves)
        self.gather_cow_class_history(self.heiferIs)
        self.gather_cow_class_history(self.heiferIIs)
        self.gather_cow_class_history(self.heiferIIIs)
        self.gather_cow_class_history(self.cows)

    @staticmethod
    def _calc_p_conc(animals):
        """
        Args:
            animals: the list of animals for which the P concentration should be
                calculated
        Returns:
            p_conc: the P concentration of @animals
        """

        if len(animals) == 0:
            return 0
        else:
            return (sum(a.p_animal for a in animals) * GeneralConstants.GRAMS_TO_KG) / sum(
                a.body_weight for a in animals)

    def calc_all_p_conc(self):
        """
        Calculates each animal class's P concentration.
        """

        # TODO: see if there is a better way to do this using dictionary comprehension
        self.p_conc['calf'] = self._calc_p_conc(self.calves)
        self.p_conc['heiferI'] = self._calc_p_conc(self.heiferIs)
        self.p_conc['heiferII'] = self._calc_p_conc(self.heiferIIs)
        self.p_conc['cow'] = self._calc_p_conc(self.heiferIIIs)
        # TODO check if this is set up correctly. Currently p_comp for the cow class is
        # being set by calculating the p_comp for heiferIIIs (line 889 directly above)

    def calc_p_rqmts(self):
        """
        Calls each pen's method to calculate each animal's phosphorus
        requirements. This method is called daily.

        Args:
        """

        for pen in self.all_pens:
            if pen.populated:
                pen.call_p_rqmts()

    def daily_p_update(self):
        """
        Calls each pen's method to calculate each animal's daily phosphorus
        update. This method is called daily.
        """

        for pen in self.all_pens:
            if pen.populated:
                pen.daily_p_update()

    def daily_updates(self, feed, weather, time):
        """
        Executes the daily routines relating to Animals. All animals are
        updated through the life_cycle_manager's daily_update() method. The
        daily phosphorus calculations are also done. If it is the end of the
        ration interval, the animals are allocated to new pens and the ration &
        manure calculations are done.

        Args:
            feed: instance of the Feed class defined in feed.py
            weather: instance of the Weather class defined in classes.py
            time: instance of the Time class defined in classes.py
        """
        if self.simulate_animals:
            for pen in self.all_pens:
                pen.populated = len(pen.animals_in_pen) > 0

            animals_added, ids_removed, calves_born, self.calves, self.heiferIs, \
                self.heiferIIs, self.heiferIIIs, self.cows = \
                self.life_cycle_manager.daily_update(self.simulation_day,
                                                     self.calves,
                                                     self.heiferIs,
                                                     self.heiferIIs,
                                                     self.heiferIIIs, self.cows)
            temp = weather.T_avg[time.year - 1][time.day - 1]
            self.daily_update_id_pen(animals_added, ids_removed, calves_born, feed, temp)

            # phosphorus requirements for daily updates
            self.calc_p_rqmts()  # per animal

            if self.end_ration_interval():
                self.calc_nutrient_rqmts(feed, temp)  # per animal
                self.clear_pens()
                # self.allocate_all_pens()
                self.allocate_animals_to_pens()
                self.calc_ration(feed)  # per pen
                self.calc_avg_growth()  # per pen

            # manure excretion
            self.calc_manure_excretion(feed, self.methane_model)  # per animal

            # phosphorus updates
            self.daily_p_update()  # per animal
            self.calc_all_p_conc()  # per animal

            self.record_pen_history()

    def end_ration_interval(self):
        """
        Returns: True if today is the day a new ration has to be formulated,
                false otherwise.
        """
        return self.simulation_day % self.formulation_interval == 1 or self.formulation_interval == 1

    def annual_reset(self):
        pass

    def generate_animal_output(self, animal_type, index):
        """
        Returns the information (ID, breed, birthday, breeding method,
        semen used, pen history, bodyweight history, milk production history,
        event history) of the animal at the index of the respective
        animal_type list.

        Args:
            animal_type: a string. One of 'calf', 'heiferI', 'heiferII',
                'heiferIII', 'cow', 'sold_heifer', or 'culled cow'
            index: the index of the animal in the respective animal_type list
                whose information will be returned

        Returns: a dictionary with an animal of animal_type's information. Not
            all information is available for each animal_type.
        """
        is_cow = False
        is_heifer_repr = False  # True if animal is heiferII or heiferIII

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

    def get_life_cycle_output(self, num_animals):
        """
        Returns the life cycle output on an individual level, which is the
        information of some of each type of animal as well as some animal
        statistics.

        Args:
            num_animals: the number of each type of animal (calves, heiferIs,
            heiferIIs, heiferIIIs, cows, sold_heifers, and culled_cows) for
            which information will be collected and returned. If num_animals is
            larger than the minimum length of the animal lists, then num_animals
            will be set to the minimum length of the animal lists

        Returns: a dictionary which contains the individual life cycle output
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

    def get_initialize_db_summary(self):
        """
        Returns: a dictionary which is the summary of the animal initialization
        database
        """
        return self.life_cycle_manager.initialize_db_summary
