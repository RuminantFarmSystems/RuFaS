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
    # list of all the animals in the simulation
    calves = []
    heiferIs = []
    heiferIIs = []
    heiferIIIs = []
    cows = []
    heifers_sold = []
    cows_culled = []

    # list of all the pens on the farm
    all_pens = []

    # simulation length, days
    sim_length = -1

    # instance of LifeCycleManager class
    life_cycle_manager = None

    # housing type: barn or pasture
    housing = ""

    # concentrate supplementation when farming type is "pasture", kg
    pasture_concentrate = -1

    ration_user_input = False

    # how often a ration is calculated, days
    formulation_interval = 0

    # day in the simulation
    simulation_day = 1

    # if False, there are no animals being simulated on the farm
    simulate_animals = False

    # dictionary: key is animal ID, value is the pen ID that animal is in
    id_pen = {}

    # queue: pens from which animals have been removed in the order in which
    # they have had animals removed. Elements (pen ids) will be added to the
    # right of the queue and popped off the left. Pen ids are popped off the
    # queue when animals are added (i.e. calves are born or animals are
    # purchased from the replacement herd), and those new animals are placed in
    # the popped pen.
    pens_needing_animals = deque([])

    # dictionary for keeping track of what animal types each pen is holding
    # (value of the dictionaries are lists of pen objects)
    pens_by_animal_combination = {Pen.AnimalCombination.CALF: [], Pen.AnimalCombination.GROWING: [],
                                  Pen.AnimalCombination.CLOSE_UP: [], Pen.AnimalCombination.GROWING_AND_CLOSE_UP: [],
                                  Pen.AnimalCombination.LAC_COW: []}

    # these variables are the P compositions of each class of animal. They
    # are calculated daily and are used when an animal is added to the
    # herd, whether by birth or replacement herd purchase. They are calculated
    # in calc_all_p_comp() and are the total body weight of the animals in the
    # respective class divided by the total P in the animals of the class
    p_comp = {
        'calf': 0,
        'heiferI': 0,
        'heiferII': 0,
        'heiferIII': 0,
        'cow': 0
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

        self.sim_length = config.sim_length
        animal_config = self.get_animal_config(data['animal_config'])
        self.life_cycle_manager = LifeCycleManager(animal_config)
        AnimalBase.set_config(animal_config)
        AnimalBase.set_nutrient_list(feed.nutrient_rqmts)
        self.init_pens(data['pen_information'], data['herd_information'], data['manure_management_scenarios'])
        self.init_animals(data['herd_information'], self.all_pens, weather, time, config, feed)
        self.housing = data['housing']
        self.pasture_concentrate = data['pasture_concentrate']
        self.ration_user_input = data['ration']['user_input']
        self.formulation_interval = data['ration']['formulation_interval']
        self.methane_model = data['methane_model']

    def init_pens(self, all_pens_data, herd_data, manure_management_scenarios):
        """
        Populates the list of pens with the information from the input json file.
        Args:
            all_pens_data: dictionary containing information about the pens
            herd_data: dictionary containing information about the herd
            manure_management_scenarios: dictionary containing information about
                different manure management scenarios
        """

        for pen_name in all_pens_data:
            pen_data = all_pens_data[pen_name]
            pen_id = pen_data['id']
            # animal_groups = pen_data['animal_groups']

            animal_combination = Pen.AnimalCombination[pen_data['animal_combination']]

            max_stocking_density = pen_data['max_stocking_density']
            vertical_dist_to_parlor = \
                pen_data['vertical_dist_to_milking_parlor']
            horizontal_dist_to_parlor = \
                pen_data['horizontal_dist_to_milking_parlor']
            num_stalls = pen_data['number_of_stalls']
            housing_type = pen_data['housing_type']
            pen_type = pen_data['pen_type']

            manure_management_scenario_id = pen_data['manure_management_scenario_id']
            manure_management_scenario = manure_management_scenarios[manure_management_scenario_id]
            bedding_type = manure_management_scenario['bedding_type']
            manure_handler = manure_management_scenario['manure_handler']
            manure_separator = manure_management_scenario['manure_separator']
            manure_treatment = manure_management_scenario['manure_treatment']

            pen = Pen(pen_id, vertical_dist_to_parlor, horizontal_dist_to_parlor,
                      num_stalls, housing_type, bedding_type, pen_type, manure_handler,
                      manure_separator, manure_treatment, animal_combination,
                      max_stocking_density)

            self.all_pens.append(pen)

        herd_num = herd_data['herd_num']

        manure_handler = "manual_scraping"
        manure_separator = "sedimentation"
        manure_treatment = "storage_pit"
        animal_combination = None
        if (len(self.all_pens) == 0) and (herd_num > 0):
            print('Warning: herd_num > 0, but pen_num = 0. Initializing 3 default pens.')
            pen_1 = Pen(0, 0.1, 1.6, 100, 'open air barn', 'sand', 'freestall',
                        manure_handler, manure_separator, manure_treatment,
                        animal_combination, 1.2)
            pen_2 = Pen(1, 0.1, 1.6, 200, 'open air barn', 'sawdust', 'freestall',
                        manure_handler, manure_separator, manure_treatment,
                        animal_combination, 1.2)
            pen_3 = Pen(2, 0.1, 1.6, 100, 'open air barn', 'sand', 'freestall',
                        manure_handler, manure_separator, manure_treatment,
                        animal_combination, 1.2)
            self.all_pens.append(pen_1)
            self.all_pens.append(pen_2)
            self.all_pens.append(pen_3)
        elif (len(self.all_pens) == 1) and (herd_num > 0):
            print('Warning: herd_num > 0, but pen_num = 1. Initializing 2 default pens.')
            pen_2 = Pen(1, 0.1, 1.6, 300, 'open air barn', 'sawdust', 'freestall',
                        manure_handler, manure_separator, manure_treatment,
                        animal_combination, 1.2)
            pen_3 = Pen(2, 0.1, 1.6, 300, 'open air barn', 'straw', 'tiestall',
                        manure_handler, manure_separator, manure_treatment,
                        animal_combination, 1.2)
            self.all_pens.append(pen_2)
            self.all_pens.append(pen_3)
        elif (len(self.all_pens) == 2) and (herd_num > 0):
            print('Warning: herd_num > 0, but pen_num = 2. Initializing 1 default pen.')
            pen_3 = Pen(2, 0.1, 1.6, 300, 'open air barn', 'straw', 'tiestall',
                        manure_handler, manure_separator, manure_treatment,
                        animal_combination, 1.2)
            self.all_pens.append(pen_3)

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

        calf_num = herd_data['calf_num']
        heiferI_num = herd_data['heiferI_num']
        heiferII_num = herd_data['heiferII_num']
        heiferIII_num = herd_data['heiferIII_num']
        cow_num = herd_data['cow_num']
        replace_num = herd_data['replace_num']
        herd_num = herd_data['herd_num']
        breed = herd_data['breed']

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

        if len(pen_data) > 0:
            self.init_nutrient_rqmts(weather, time, feed)
            self.pen_allocation()

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

        # stratefying the pens that lost animals by animal group
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
                animal_p_conc = self.p_comp['calf']
                self.calves.append(animal)
                group = Pen.AnimalCombination.CALF
            elif type(animal).__name__ == 'HeiferI':
                animal_p_conc = self.p_comp['heiferI']
                self.heiferIs.append(animal)
                group = Pen.AnimalCombination.GROWING
            elif type(animal).__name__ == 'HeiferII':
                animal_p_conc = self.p_comp['heiferII']
                self.heiferIIs.append(animal)
                group = Pen.AnimalCombination.GROWING
            elif type(animal).__name__ == 'HeiferIII':
                animal_p_conc = self.p_comp['heiferIII']
                self.heiferIIIs.append(animal)
                group = Pen.AnimalCombination.CLOSE_UP
            elif not animal.milking:
                animal_p_conc = self.p_comp['cow']
                self.cows.append(animal)
                group = Pen.AnimalCombination.CLOSE_UP
            else:  # animal is of class Cow
                animal_p_conc = self.p_comp['cow']
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

        for pen in range(len(self.all_pens)):
            if len(self.all_pens[pen].animals_in_pen) > 0 and 'Cow' in self.all_pens[pen].classes_in_pen and \
                    self.all_pens[pen].ration == {}:
                available_feeds = ration_driver.AvailableFeeds()
                available_feeds.feed_nutrients(feed)
                self.all_pens[pen].ration = self.all_pens[pen].calc_ration(feed, available_feeds)
            else:
                # Need to adjust the ration totals for the pen attributes now
                # that all new animals have been added
                for key in self.all_pens[pen].ration:
                    if key != 'status' and key != 'objective':
                        self.all_pens[pen].ration[key] = \
                            (self.all_pens[pen].ration[key] /
                             pen_population_before_additions[pen]) * len(
                                self.all_pens[pen].animals_in_pen)

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

    def pen_allocation(self):
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
        # organzing pens by class and ensuring sufficeint storage
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
                    print('Warning: shortage of ', max_key[0].name, ' pens, initializing new pen')
                    # initalizing a default pen to be used for any class
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

        #####################
        # Pen Allocation for lactating cows
        #####################
        stalls = [pen.num_stalls for pen in lac_cow_pens]
        # density per-pen for even distribution
        density = len(lactating_cows) / sum(stalls)
        # Grouping for Lactating Cows
        pen_grouping = grouping(lactating_cows, lac_cow_pens, density)
        # Assigning Lactating Cows to Pens based on the grouping output
        for key in pen_grouping:
            lac_cow_pens[0].update_animals(pen_grouping[key], Pen.AnimalCombination.LAC_COW)
            lac_cow_pens.remove(lac_cow_pens[0])

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
            if pen.pen_populated:
                self.all_pens[i].ration = self.all_pens[i].calc_ration(feed, available_feeds)

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

        for pen in self.all_pens:
            pen.calc_avg_growth()

    def record_pen_history(self):
        """
        Records the pen history of all of the animals.
        """
        for calf in self.calves:
            curr_pen = self.id_pen[calf.id]
            classes_in_pen = self.all_pens[curr_pen].classes_in_pen
            calf.update_pen_history(curr_pen, self.simulation_day, classes_in_pen)

        for heiferI in self.heiferIs:
            curr_pen = self.id_pen[heiferI.id]
            classes_in_pen = self.all_pens[curr_pen].classes_in_pen
            heiferI.update_pen_history(curr_pen, self.simulation_day, classes_in_pen)

        for heiferII in self.heiferIIs:
            curr_pen = self.id_pen[heiferII.id]
            classes_in_pen = self.all_pens[curr_pen].classes_in_pen
            heiferII.update_pen_history(curr_pen, self.simulation_day, classes_in_pen)

        for heiferIII in self.heiferIIIs:
            curr_pen = self.id_pen[heiferIII.id]
            classes_in_pen = self.all_pens[curr_pen].classes_in_pen
            heiferIII.update_pen_history(curr_pen, self.simulation_day, classes_in_pen)

        for cow in self.cows:
            curr_pen = self.id_pen[cow.id]
            classes_in_pen = self.all_pens[curr_pen].classes_in_pen
            cow.update_pen_history(curr_pen, self.simulation_day, classes_in_pen)

    @staticmethod
    def _calc_p_comp(animals):
        """
        Args:
            animals: the list of animals for which the P composition should be
                calculated
        Returns:
            p_comp: the P composition of @animals
        """

        if len(animals) == 0:
            return 0
        else:
            return sum(a.p_animal for a in animals) / sum(a.body_weight for a in animals)

    def calc_all_p_comp(self):
        """
        Calculates each animal class's P concentration.
        """
        # TODO: see if there is a better way to do this using dictionary comprehension
        self.p_comp['calf'] = self._calc_p_comp(self.calves)
        self.p_comp['heiferI'] = self._calc_p_comp(self.heiferIs)
        self.p_comp['heiferII'] = self._calc_p_comp(self.heiferIIs)
        self.p_comp['cow'] = self._calc_p_comp(self.heiferIIIs)

    def calc_p_rqmts(self):
        """
        Calls each pen's method to calculate each animal's phosphorus
        requirements. This method is called daily.

        Args:
        """

        for pen in self.all_pens:
            if pen.pen_populated:
                pen.call_p_rqmts()

    def daily_p_update(self):
        """
        Calls each pen's method to calculate each animal's daily phosphorus
        update. This method is called daily.
        """

        for pen in self.all_pens:
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
            for pen in self.all_pens:
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
                self.pen_allocation()
                self.calc_ration(feed)  # per pen
                self.calc_avg_growth()  # per pen

            # manure excretion
            self.calc_manure_excretion(feed, self.methane_model)  # per animal

            # phosphorus updates
            self.daily_p_update()  # per animal
            self.calc_all_p_comp()  # per animal

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
