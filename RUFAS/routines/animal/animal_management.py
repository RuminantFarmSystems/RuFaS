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
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.general_constants import GeneralConstants
from RUFAS.routines.animal.clustering_pen_grouping import grouping
from RUFAS.routines.animal.life_cycle.life_cycle import LifeCycleManager
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.animal.ration import ration_driver as ration_driver
from RUFAS.routines.feed.feed import Feed

import random
from statistics import mean
from typing import Any, Dict, Tuple, List

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
        self.animal_to_pen_id_map = {}

        # dictionary for keeping track of what animal types each pen is holding
        # (value of the dictionaries are lists of pen objects)
        self.pens_by_animal_combination = {Pen.AnimalCombination.CALF: [], Pen.AnimalCombination.GROWING: [],
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

            self.allocate_all_pens()

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

    def fully_update_animal_to_pen_id_map(self):
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

        Args:
            animals_removed: list of animal objects that are to be removed from the herd
        """

        for animal in animals_removed:
            if animal.id in self.animal_to_pen_id_map:
                pen = self.all_pens[self.animal_to_pen_id_map[animal.id]]
                pen.animals_in_pen.remove(animal)
                pen.stocking_density = len(pen.animals_in_pen) / pen.num_stalls
                del self.animal_to_pen_id_map[animal.id]

    def track_former_pen_population(self) -> List[int]:
        """
        Creates a list containing the original pen populations of a simulated
        farm before any updates are made to pens. The original pens' information
        would get lost as animals get added.

        Returns: a list of the populations of each pen on the farm prior to
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

        Args:
            prior_pen_populations: list of the number of animals in each pen, since
                pens are zero-indexed
        """

        for index, pen in enumerate(self.all_pens):
            for key in pen.ration:
                if key != 'status' and key != 'objective':
                    pen.ration[key] = (pen.ration[key] / prior_pen_populations[index]) * len(pen.animals_in_pen)

    def daily_update_id_map(self, animals_added: List[AnimalBase], animals_removed: List[AnimalBase],
                            calves_born: List[Calf], feed: Feed, temp: float):
        """
        Updates the dictionary that maps animal IDs to the ID of the pen they are housed in when
        new animals are born or purchased and when animals leave the herd due to death or culling

        Args:
            animals_added: list of animal objects that have been added to the herd
            animals_removed: list of animal objects that have been removed from the herd
            calves_born: list of Calf objects that have been added to the herd
            feed: an instance of the Feed class defined in feed.py
            temp: the temperature on the current day
        """

        all_animals_added = animals_added + calves_born

        self.remove_animals_from_herd(animals_removed)

        original_pen_populations = self.track_former_pen_population()

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

        self.fully_update_animal_to_pen_id_map()

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
        and pen composition of all animals of a given cow class, before then updating the
        pen history for that class using the update_pen_history() method

        Args:
            cow_class: list of instances of whatever cow type's pen history is being gathered
        """
        for cow in cow_class:
            current_pen_id = self.animal_to_pen_id_map[cow.id]
            classes_in_pen = self.all_pens[current_pen_id].classes_in_pen
            cow.update_pen_history(current_pen_id, self.simulation_day, classes_in_pen)

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

            animals_added, animals_removed, calves_born, self.calves, self.heiferIs, \
                self.heiferIIs, self.heiferIIIs, self.cows = \
                self.life_cycle_manager.daily_update(self.simulation_day,
                                                     self.calves,
                                                     self.heiferIs,
                                                     self.heiferIIs,
                                                     self.heiferIIIs, self.cows)
            temp = weather.T_avg[time.year - 1][time.day - 1]
            self.daily_update_id_map(animals_added, animals_removed, calves_born, feed, temp)

            # phosphorus requirements for daily updates
            self.calc_p_rqmts()  # per animal

            if self.end_ration_interval():
                self.calc_nutrient_rqmts(feed, temp)  # per animal
                self.clear_pens()
                self.allocate_all_pens()
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
