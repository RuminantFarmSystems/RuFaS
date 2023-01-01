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
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.animal.clustering_pen_grouping import grouping
from RUFAS.routines.animal.life_cycle.life_cycle import LifeCycleManager
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.ration import ration_driver as ration_driver
from collections import deque
import random
from typing import Tuple
from statistics import mean

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
        self.simulate_animals = False

        # list of all the animals in the simulation
        self.calves = []
        self.heiferIs = []
        self.heiferIIs = []
        self.heiferIIIs = []
        self.cows = []
        self.heifers_sold = []
        self.cows_culled = []

        # list of all the pens on the farm
        self.all_pens_ids = []

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
        # in calc_all_p_conc() and are calculated by dividing the total P in the animals of the class
        # by the total body weight of the animals, on a per-animal basis
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

        self.init_pens(data['pen_information'], data['herd_information'])

        self.init_animals(data['herd_information'], self.all_pens_ids, weather, time, config, feed)

    def init_pens(self, all_pen_data, herd_data):
        """
        Populates the list of pens with the information from the input json file.
        Args:
            all_pen_data: dictionary containing information about the pens
            herd_data: dictionary containing information about the herd
        """

        # Initialize pens from all_pen_data
        for pen_data in all_pen_data.values():
            pen_data['pen_id'] = pen_data.pop('id')
            pen_data['animal_combination'] = Pen.AnimalCombination[pen_data.pop('animal_combination')]

            pen = Pen(**pen_data)

            self.all_pens_ids.append(pen)

        self.init_default_pens(herd_data['herd_num'])

    def init_default_pens(self, herd_num):
        # TODO: add unit test
        """
            Initializes default pens if not enough exist in the simulation.
            Args:
                herd_num: number of animals in the herd
            """

        # Minimum number of pens in the simulation
        MIN_NUM_PENS = 3

        num_pens_needed = MIN_NUM_PENS - len(self.all_pens_ids)

        # Check if any default pens need to be added
        if num_pens_needed > 0 and herd_num > 0:
            self.init_default_pens(num_pens_needed)
            print('Warning: herd_num > 0, but num_pens =', len(self.all_pens_ids), '. Initilizing', num_pens_needed,
                  'default pens.')
            for i in range(num_pens_needed):
                new_default_pen = Pen(0, 0.1, 1.6, 100, 'open air barn', 'sand', 'freestall',
                                      "manual_scraping", "sedimentation", "storage_pit",
                                      Pen.AnimalCombination.NONE, 1.2)
                self.all_pens_ids.append(new_default_pen)

    def init_animals(self, herd_data, pen_data, weather, time, config, feed):
        """
        Populates the list of animals with the information from the
        input JSON file: constructs the calves, heiferI’s, heiferII’s,
        heiferIII’s, and cows (the desired amounts of each is specified by
        @data), then calls life_cycle_manager's initialize_herd() with those
        numbers to create instances of the animals. The nutrient requirements
        are calculated and the animals are allocated to pens.

        Args:
            feed: an instance of the Feed class defined in feed.py
            config: an instance of the Config class defined in classes.py
                contains model configuration information
            herd_data: dictionary containing information about the herd
            pen_data: dictionary containing information about the pens
            weather: instance of the Weather class defined in classes.py
            time: instance of the Time class defined in classes.py
        """

        animal_keys = {"calf_num", "heiferI_num", "heiferII_num", "heiferIII_num", "cow_num"}
        animal_nums = dict()

        for key in animal_keys:
            animal_nums[key] = herd_data[key]

        calf_num = herd_data['calf_num']
        heiferI_num = herd_data['heiferI_num']
        heiferII_num = herd_data['heiferII_num']
        heiferIII_num = herd_data['heiferIII_num']
        cow_num = herd_data['cow_num']
        replace_num = herd_data['replace_num']
        herd_num = herd_data['herd_num']
        breed = herd_data['breed']

        # QUESTION: what do calf_num, heifer_num, etc do?
        # if herd_num ==

        # QUESTION: what is the point of simulate_animals?

        if herd_num == 0:
            self.simulate_animals = False
            if not calf_num == 0:
                print("Warning: herd_num is 0, but calf_num is not. "
                      "Setting calf_num = 0.")
                calf_num = 0
            if not heiferI_num == 0:
                print("Warning: herd_num is 0, but heiferI_num is not. "
                      "Setting heiferI_num = 0.")
                heiferI_num = 0
            if not heiferII_num == 0:
                print("Warning: herd_num is 0, but heiferII_num is not. "
                      "Setting heiferII_num = 0.")
                heiferII_num = 0
            if not heiferIII_num == 0:
                print("Warning: herd_num is 0, but heiferIII_num is not. "
                      "Setting heiferIII_num = 0.")
                heiferIII_num = 0
            if not cow_num == 0:
                print("Warning: herd_num is 0, but cow_num is not. "
                      "Setting cow_num = 0.")
                cow_num = 0
        else:
            self.simulate_animals = True

        herd_init = herd_data['herd_init']

        if self.simulate_animals:
            self.calves, self.heiferIs, self.heiferIIs, self.heiferIIIs, self.cows \
                = self.life_cycle_manager.initialize_herd(herd_num, calf_num,
                                                          heiferI_num, heiferII_num,
                                                          heiferIII_num, cow_num,
                                                          replace_num, herd_init,
                                                          breed, config)

        # QUESTION: Should this be moved to init_pens?
        if len(pen_data) > 0:
            self.init_nutrient_rqmts(weather, time, feed)
            self.allocate_all_pens()

    @staticmethod
    def print_animal_num_warnings(animal_keys, herd_data):
        for key in animal_keys:
            if herd_data[key] == 0:
                print("Warning: herd_num = 0, but", key, "!= 0.")

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

        return mean(pen.vertical_dist_to_parlor for pen in self.all_pens_ids), mean(
            pen.horizontal_dist_to_parlor for pen in self.all_pens_ids)

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
        for pen in self.all_pens_ids:
            animals_in_pen = pen.animals_in_pen
            for animal in animals_in_pen:
                self.animal_to_pen_id_map[animal.id] = pen.id

    def remove_animal_from_herd(self, ids_removed):
        """
        Removes the animal IDs from the animal_to_pen_id_map dictionary pertaining to the
        animals that have been removed from the herd, and updates the stocking density
        of the pens they were in. This function is void.

        Args:
            ids_removed: list of animal IDs that are to be removed from the herd
        """

        # Loops through ids_removed, which is a list of the animals IDs that have been removed from the herd.
        for id in ids_removed:
            # If the given animal ID is in the animal ID/pen ID dictionary
            # Here, we are looping through the keys of a dictionary pertaining to animal IDs
            if id in self.animal_to_pen_id_map:
                # Creates a "pen" variable that grabs the current pen of the animal removed
                pen = self.all_pens_ids[self.animal_to_pen_id_map[id]]
                # Readjusts the stocking density value of the pen in question
                pen.stocking_density = (len(pen.animals_in_pen) - 1) / pen.num_stalls
                # Deletes the animal ID key entry corresponding to the id of the animal removed
                del self.animal_to_pen_id_map[id]

    def track_former_pen_population(self):
        """
        Creates a list containing the original pen populations of a simulated
        farm before any updates are made to pens. The original pens' information
        would get lost as animals get added.

        Returns: a list of the populations of each pen on the farm prior to
                 any additions due to daily pen updates
        """
        # Initializes pen population list before additions are made
        pen_population_before_additions = [None] * len(self.all_pens_ids)
        # Loops through the pens objects on the farm and their indices from the all_pens_ids list
        for index, pen in enumerate(self.all_pens_ids):
            # Populates list with the number of animals as the values, and the indices pertaining to different pens
            #  since pens are zero-indexed
            pen_population_before_additions[index] = len(pen.animals_in_pen)

        return pen_population_before_additions

    def calculate_pen_rations(self, prior_pen_populations):
        """
        Calculates the ration of every pen in the simulated farm. This is done by
        updating the values of each Pen object's ration dictionary, where the keys
        pertain to certain food items in a ration. This function is void.

        Args:
            prior_pen_populations: list of the number of animals in each pen, since
                pens are zero-indexed
        """

        # We loop through the numbers of all the pens on the farm and their indices
        for index, pen in enumerate(self.all_pens_ids):
            # From Militsa: "We need to adjust the ration totals for the pen attributes now
            # that all new animals have been added"
            for key in pen.ration:
                if key != 'status' and key != 'objective':
                    pen.ration[key] = (pen.ration[key] / prior_pen_populations[index]) * \
                                      len(pen.animals_in_pen)

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

        # _____________________________________________________________________________________________
        # Calf preprocessing logic
        # _____________________________________________________________________________________________

        calf_ids = []
        for calf in calves_born:
            calf_ids.append(calf.id)
        animals_added.extend(calf_ids)

        # _____________________________________________________________________________________________
        # Animal removal logic
        # _____________________________________________________________________________________________
        self.remove_animal_from_herd(ids_removed)
        # From Doctor Reed: redesign how we assign new animals to a pen

        # _____________________________________________________________________________________________
        # Population tracker logic
        # _____________________________________________________________________________________________
        original_pen_populations = self.track_former_pen_population()

        # _____________________________________________________________________________________________
        # Pen selection/animal-to-pen insertion logic (could be split but for loop is rather long)
        # _____________________________________________________________________________________________
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

        for animal in animals_added:
            animal_class = type(animal).__name__

            if animal_class == 'Cow':
                if animal.milking:
                    animal_class = 'Lac_Cow'
                else:
                    animal_class = 'Dry_Cow'

            animal_p_conc = (animal_type_mapping_dict.get(animal_class))
            # print(animal_class)
            print(type(animal))
            print(animal_p_conc)
            # animal_conc_access = animal_p_conc['p_conc']
            animal_type_mapping_dict.get(animal_class)['animal_list'].append(animal)
            group = animal_type_mapping_dict.get(animal_class)['animal_group']

            candidate_pens = self.pens_by_animal_combination[group]
            pen_for_insert = min(candidate_pens, key=lambda p: p.stocking_density)

        self.animal_to_pen_id_map[animal.id] = pen_for_insert.id
        self.all_pens_ids[pen_for_insert.id].set_up_new_animal(animal, animal_p_conc, feed, temp,
                                                               original_pen_populations[pen_for_insert.id])

        # _____________________________________________________________________________________________
        # Ration-specific logic
        # _____________________________________________________________________________________________
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
        for pen in self.all_pens_ids:

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
                    "all_pens": self.all_pens_ids, }
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
        for pen in self.all_pens_ids:
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
        for i, pen in enumerate(self.all_pens_ids):
            if pen.pen_populated:
                self.all_pens_ids[i].ration = self.all_pens_ids[i].calc_ration(feed, available_feeds)

    def calc_manure_excretion(self, feed, methane_model):
        """
        Calls each animal's method to calculate manure excretion to find the
        total for each pen. This is part of the routines that happen every
        ration interval.

        Args:
            feed: instance of the feed class
            methane_model: methane model used for methane emission calculations
        """
        for pen in self.all_pens_ids:
            if pen.pen_populated:
                pen.calc_manure(feed, methane_model)
            else:
                pen.reset_manure()

    def calc_avg_growth(self):
        """
        Calls each pen's method to calculate the average growth of animals in
        the pen. This is part of the routines that happen every
        ration interval.
        """

        for pen in self.all_pens_ids:
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
            current_pen = self.animal_to_pen_id_map[cow_class.id]
            classes_in_pen = self.all_pens_ids[current_pen].classes_in_pen
            cow_class.update_pen_history(current_pen, self.simulation_day, classes_in_pen)

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
            return sum(a.p_animal for a in animals) / sum(a.body_weight for a in animals)

    def calc_all_p_conc(self):
        """
        Calculates each animal class's P concentration.
        """
        # TODO: see if there is a better way to do this using dictionary comprehension
        self.p_conc['calf'] = self._calc_p_conc(self.calves)
        self.p_conc['heiferI'] = self._calc_p_conc(self.heiferIs)
        self.p_conc['heiferII'] = self._calc_p_conc(self.heiferIIs)
        self.p_conc['cow'] = self._calc_p_conc(self.heiferIIIs)

    def calc_p_rqmts(self):
        """
        Calls each pen's method to calculate each animal's phosphorus
        requirements. This method is called daily.

        Args:
        """

        for pen in self.all_pens_ids:
            if pen.pen_populated:
                pen.call_p_rqmts()

    def daily_p_update(self):
        """
        Calls each pen's method to calculate each animal's daily phosphorus
        update. This method is called daily.
        """

        for pen in self.all_pens_ids:
            if pen.pen_populated:
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
            for pen in self.all_pens_ids:
                pen.pen_populated = len(pen.animals_in_pen) > 0

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
        if num_animals > minimum_num:
            print('\nThe smallest animal list is of size ' + str(minimum_num) +
                  ' so ' + str(num_animals) + ' of each animal class cannot ' +
                  'be in the life cycle output. Only ' + str(minimum_num) +
                  ' of each animal type will be in the life cycle output.')
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