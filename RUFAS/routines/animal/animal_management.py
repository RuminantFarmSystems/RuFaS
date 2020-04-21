################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: animal_management.py
Description: The class which manages all of the animal routines and keeps track
    of all animals and pens. All operations are as described in the Animal
    Module Information Flow document on Basecamp (such as daily animal updates
    and pen allocation). Method calls cascade through from the animal management
    class to pen to each individual animal in that pen. The life cycle of each
    animal is controlled by an instance of the LifeCycleManager class, and this
    instance updates the animals daily.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
"""
################################################################################
from RUFAS.routines.animal.pen import Pen
from RUFAS.routines.animal.life_cycle.life_cycle import LifeCycleManager
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from collections import deque


def daily_animal_routine(animal_management, feed, weather, time):
    """
    Executes daily routines relating to Animals. This method is called every day
    in the simulation and calls @animal_management's daily_updates() method
    with @feed and @time as arguments. [Note that currently, @weather and
    @ time are not used in animal updates.]

    Args:
        animal_management: instance of the AnimalManagement class
        feed: instance of the Feed class
        weather: instance of the Weather class
        time: instance of the Time class
    """
    animal_management.daily_updates(feed)


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

    # these variables are the P concentrations of each class of animal. They
    # are calculated daily and are used when an animal is added to the
    # herd, whether by birth or replacement herd purchase. They are calculated
    # in calc_all_p_conc() and are the total body weight of the animals in the
    # respective class divided by the total P in the animals of the class
    calf_p_conc = 0
    heiferI_p_conc = 0
    heiferII_p_conc = 0
    heiferIII_p_conc = 0
    cow_p_conc = 0

    def __init__(self, data, config, feed):
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
        self.life_cycle_manager = LifeCycleManager(data['animal_config'])
        AnimalBase.set_config(data['animal_config'])
        AnimalBase.set_nutrient_list(feed.nutrient_rqmts)
        self.init_pens(data['pen_information'])
        self.init_animals(data['herd_information'], feed)
        self.housing = data['housing']
        self.pasture_concentrate = data['pasture_concentrate']
        self.ration_user_input = data['ration']['user_input']
        self.formulation_interval = data['ration']['formulation_interval']

    def init_pens(self, data):
        """
        Populates the list of pens with the information from the input
        JSON file, @data.

        Args:
            data: dictionary with pen information from the input JSON file
        """
        for pen_name in data:
            pen_data = data[pen_name]
            pen_id = pen_data['id']
            vertical_dist_to_parlor = \
                pen_data['vertical_dist_to_milking_parlor']
            horizontal_dist_to_parlor = \
                pen_data['horizontal_dist_to_milking_parlor']
            num_stalls = pen_data['number_of_stalls']
            housing_type = pen_data['housing_type']
            bedding_type = pen_data['bedding_type']
            pen_type = pen_data['pen_type']
            pen = Pen(pen_id, vertical_dist_to_parlor,
                      horizontal_dist_to_parlor, num_stalls, housing_type,
                      bedding_type, pen_type)
            self.all_pens.append(pen)

    def init_animals(self, data, feed):
        """
        Populates the list of animals with the information from the
        input JSON file: constructs the calves, heiferI’s, heiferII’s,
        heiferIII’s, and cows (the desired amounts of each is specified by
        @data), then calls life_cycle_manager's initialize_herd() with those
        numbers to create instances of the animals. The nutrient requirements
        are calculated and the animals are allocated to pens.

        Args:
            data: dictionary with the herd information from the input json file
            feed: instance of the Feed class
        """
        calf_num = data['calf_num']
        heiferI_num = data['heiferI_num']
        heiferII_num = data['heiferII_num']
        heiferIII_num = data['heiferIII_num']
        cow_num = data['cow_num']
        replace_num = data['replace_num']
        herd_num = data['herd_num']

        if herd_num == 0:
            self.simulate_animals = False
            print("herd_num is 0 -> no animals will be simulated")
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

        self.calves, self.heiferIs, self.heiferIIs, self.heiferIIIs, self.cows \
            = self.life_cycle_manager.initialize_herd(herd_num, calf_num,
                                                      heiferI_num, heiferII_num,
                                                      heiferIII_num, cow_num,
                                                      replace_num)

        self.init_nutrient_rqmts(feed)
        self.pen_allocation()

    def init_nutrient_rqmts(self, feed):
        """
        Calculates initial nutrient requirements at the beginning of the
        simulation for initial pen allocation. For the nutrient requirements
        of cows, the average walking distance of all the pens initialized
        is used.

        Args:
            feed: instance of the Feed class
        """
        # average vertical & horizontal distance (VD, HD) of pens to the
        # milking parlor
        avg_VD_parlor, avg_HD_parlor = self.avg_pen_dist()

        for calf in self.calves:
            calf.calc_nutrient_rqmts()

        for heiferI in self.heiferIs:
            heiferI.calc_nutrient_rqmts()

        for heiferII in self.heiferIIs:
            heiferII.calc_nutrient_rqmts()

        for heiferIII in self.heiferIIIs:
            heiferIII.calc_nutrient_rqmts()

        for cow in self.cows:
            # uses average distances from pens to milking parlor
            cow.calc_init_nutrient_rqmts(avg_VD_parlor, avg_HD_parlor,
                                         self.housing, self.pasture_concentrate,
                                         feed)

    def avg_pen_dist(self):
        """
        Calculates the average distance from a pen to the milking parlor.

        Returns: a tuple of (average vertical distance from milking parlor,
            average horizontal distance from milking parlor)
        """
        # vertical distance
        VD_sum = 0

        # horizontal distance
        HD_sum = 0
        for pen in self.all_pens:
            VD_sum += pen.vertical_parlor_dist
            HD_sum += pen.horizontal_parlor_dist

        return VD_sum / len(self.all_pens), HD_sum / len(self.all_pens)

    def calc_nutrient_rqmts(self, feed):
        """
        Calls each animal's method to calculate its nutrient requirements.

        Args:
            feed: instance of the feed class
        """
        for pen in self.all_pens:
            pen.call_animal_nutrient_rqmts(self.housing,
                                           self.pasture_concentrate, feed)

    def fully_update_id_pen(self):
        """
        Updates the entire id_pen dictionary so that each animal's ID is
        associated with the pen that animal is in.
        """
        for pen in self.all_pens:
            animals_in_pen = pen.animals_in_pen
            for animal in animals_in_pen:
                self.id_pen[animal.id] = pen.id

    def daily_update_id_pen(self, animals_added, ids_removed, calves_born):
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
            calves_born: list of Calf objects that have been added to the herd
            animals_added: list of animal IDs that have been added to the herd
            ids_removed: list of animal IDs that have been removed from the herd
        """
        for i in ids_removed:
            if i in self.id_pen:
                pen = self.id_pen[i]
                self.pens_needing_animals.append(pen)
                del self.id_pen[i]

        for animal in animals_added:
            pen = self.pens_needing_animals.popleft()
            self.id_pen[animal.id] = pen

            if type(animal).__name__ == 'Calf':
                animal_p_conc = self.calf_p_conc
            elif type(animal).__name__ == 'HeiferI':
                animal_p_conc = self.heiferI_p_conc
            elif type(animal).__name__ == 'HeiferII':
                animal_p_conc = self.heiferII_p_conc
            elif type(animal).__name__ == 'HeiferIII':
                animal_p_conc = self.heiferIII_p_conc
            else:  # animal is of class Cow
                animal_p_conc = self.cow_p_conc

            self.all_pens[pen].set_up_new_animal(animal, animal_p_conc)

        for calf in calves_born:
            # TODO: this is the hard coded calf pen value
            pen = 0
            self.all_pens[pen].set_up_new_animal(calf, self.calf_p_conc)

    def pen_allocation(self):
        """
        Allocates the animals in all_animals to pens in all_pens based on the
        animals' characteristics.
        TEMPORARY HARD-CODE FOR TESTING PURPOSES.
        """
        self.all_pens[0].update_animals(self.calves)
        self.all_pens[1].update_animals(self.heiferIs)
        self.all_pens[2].update_animals(self.heiferIIs)
        self.all_pens[3].update_animals(self.heiferIIIs)

        # separate into lactating and dry cow pens
        lactating_cows = []
        dry_cows = []
        for cow in self.cows:
            if cow.milking:
                lactating_cows.append(cow)
            else:
                dry_cows.append(cow)

        self.all_pens[4].update_animals(dry_cows)
        self.all_pens[5].update_animals(lactating_cows)

        self.fully_update_id_pen()

    def clear_pens(self):
        """
        Removes animals from pens for re-allocation. This is part of the
        routines that happen every ration interval.
        """
        for pen in self.all_pens:
            pen.clear()

    def calc_avg_nutrient_rqmts(self):
        """
        Calls each pens's method to calculate the average nutrient requirements
        of the animals inside it. This is part of the routines that happen every
        ration interval.
        """
        for pen in self.all_pens:
            if pen.pen_populated:
                pen.calc_avg_nutrient_rqmts()

    def calc_ration(self, feed):
        """
        Calls each pens's method to calculate the ration for that pen. This is
        part of the routines that happen every ration interval.

        Args:
            feed: instance of the Feed class
        """
        for pen in self.all_pens:
            if pen.pen_populated:
                pen.calc_ration(self.housing, self.pasture_concentrate, feed)

    def calc_manure_excretion(self, feed):
        """
        Calls each animal's method to calculate manure excretion to find the
        total for each pen. This is part of the routines that happen every
        ration interval.

        Args:
            feed: instance of the feed class
        """
        for pen in self.all_pens:
            if pen.pen_populated:
                pen.calc_manure(feed)

    def calc_avg_growth(self):
        """
        Calls each pen's method to calculate the average growth of animals in
        the pen. This is part of the routines that happen every
        ration interval.
        """
        for pen in self.all_pens:
            if pen.pen_populated:
                pen.calc_avg_growth()

    @staticmethod
    def p_conc(animals):
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
            total_bw = 0
            total_p_animal = 0
            for animal in animals:
                total_bw += animal.body_weight
                total_p_animal += animal.p_animal
            return total_p_animal / total_bw

    def calc_all_p_conc(self):
        """
        Calculates each animal class's P concentration.
        """
        self.calf_p_conc = self.p_conc(self.calves)
        self.heiferI_p_conc = self.p_conc(self.heiferIs)
        self.heiferII_p_conc = self.p_conc(self.heiferIIs)
        self.heiferIII_p_conc = self.p_conc(self.heiferIIIs)
        self.cow_p_conc = self.p_conc(self.cows)

    def calc_p_rqmts(self, feed):
        """
        Calls each pen's method to calculate each animal's phosphorus
        requirements. This method is called daily.

        Args:
            feed: instance of the Feed class
        """
        for pen in self.all_pens:
            if pen.pen_populated:
                pen.call_p_rqmts(feed)

    def daily_p_update(self):
        """
        Calls each pen's method to calculate each animal's daily phosphorus
        update. This method is called daily.
        """
        for pen in self.all_pens:
            if pen.pen_populated:
                pen.daily_p_update()

    def daily_updates(self, feed):
        """
        Executes the daily routines relating to Animals. All animals are
        updated through the life_cycle_manager's daily_update() method. The
        daily phosphorus calculations are also done. If it is the end of the
        ration interval, the animals are allocated to new pens and the ration &
        manure calculations are done.

        Args:
            feed: instance of the Feed class
        """
        if self.simulate_animals:
            for pen in self.all_pens:
                pen.pen_populated = len(pen.animals_in_pen) > 0

            ids_added, ids_removed, calves_born, self.calves, self.heiferIs, \
                self.heiferIIs, self.heiferIIIs, self.cows = \
                self.life_cycle_manager.daily_update(self.simulation_day,
                                                     self.sim_length,
                                                     self.calves,
                                                     self.heiferIs,
                                                     self.heiferIIs,
                                                     self.heiferIIIs, self.cows)

            self.daily_update_id_pen(ids_added, ids_removed, calves_born)

            # phosphorus calculations
            self.calc_p_rqmts(feed)  # per animal
            self.daily_p_update()  # per animal
            self.calc_all_p_conc()  # per animal

            if self.end_ration_interval():
                self.calc_nutrient_rqmts(feed)  # per animal
                self.clear_pens()
                self.pen_allocation()
                self.calc_avg_nutrient_rqmts()  # per pen
                self.calc_ration(feed)  # per pen
                self.calc_manure_excretion(feed)  # per animal
                self.calc_avg_growth()  # per pen

    def end_ration_interval(self):
        """
        Returns: True if today is the day a new ration has to be formulated,
                false otherwise.
        """
        return (self.simulation_day % self.formulation_interval) == 1 or \
            self.formulation_interval == 1

    def annual_reset(self):
        pass
