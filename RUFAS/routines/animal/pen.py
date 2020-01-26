################################################################################
"""
RUFAS: Ruminant Farm Systems Model
File name: pen.py
Description: The class which represents a pen on the farm. Each pen has
    operations as described in the Animal Module Information Flow document on
    Basecamp (such as calculating average nutrient requirements, ration,
    manure excretion, etc). Method calls cascade through from the animal
    management class to pen to each individual animal in that pen.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
"""
################################################################################
from RUFAS.routines.animal.ration.lactating_cow_ration import set_globals
from RUFAS.routines.animal.ration.lactating_cow_ration import \
    optimize as lactating_cow_optimize
from RUFAS.routines.animal.ration.calf_ration import optimize as calf_optimize
from RUFAS.routines.animal.ration.dry_cow_ration import \
    optimize as dry_cow_optimize
from RUFAS.routines.animal.ration.growing_heifer_ration import \
    optimize as growing_heifer_optimize
from RUFAS.routines.feed.feed import Feeds, Nutrients


class Pen:
    # unique pen ID, from input file
    id = -1

    # list of all animals in this pen
    animals_in_pen = []

    # boolean: False if len(self.animals_in_pen) == 0
    # (i.e. there are no animals in the pen)
    pen_populated = False

    # set (no repeats) of all the classes to which the animals in the pen belong
    classes_in_pen = set()

    # vertical distance to milking parlor, km, from input file
    vertical_parlor_dist = 0

    # horizontal distance to milking parlor, km, from input file
    horizontal_parlor_dist = 0

    # number of stalls, from input file
    num_stalls = 0

    # stocking density of pen, calculated when animals in pen are updated in
    # update_animals()
    stocking_density = 0

    # housing type of the pen, from input file
    housing_type = ""

    # bedding type of the pen, from input file
    bedding_type = ""

    # freestall or tiestall, from input file
    pen_type = ""

    # average nutrient requirements of the animals in the pen, used for
    # ration formulation
    avg_nutrient_rqmts = {}

    # average body weight of the animals in the pen, used for ration formulation
    avg_BW = 0

    # average dry matter intake estimation of the animals in the pen,
    # used for ration formulation
    avg_DMIest = 0

    # average change in (delta) body weight of the animals in the pen,
    # used for ration formulation
    avg_DBW = 0

    # average milk production of the animals in the pen,
    # used for (lactating cow) ration formulation
    avg_milk = 0

    # average milk crude protein content of the animals in the pen,
    # used for (lactating cow) ration formulation
    avg_CP_milk = 0

    # ration for all the animals in the pen
    ration = {}

    # total manure excretion of the animals in the pen
    manure = {}

    # average growth of the animals in the pen
    avg_growth = 0

    def __init__(self, id_number, vert_dist, horiz_dist, num_stalls,
                 housing_type, bedding_type, pen_type):
        """
        Initializes a pen with the given arguments.

        Args:
            id_number: the unique id number of the pen
            vert_dist: vertical distance to milking parlor, km
            horiz_dist: horizontal distance to milking parlor, km
            num_stalls: number of stalls in the pen
            housing_type: housing type of the pen
            bedding_type: bedding type of the pen
            pen_type: freestall or tiestall
        """
        self.id = id_number
        self.vertical_parlor_dist = vert_dist
        self.horizontal_parlor_dist = horiz_dist
        self.num_stalls = num_stalls
        self.housing_type = housing_type
        self.bedding_type = bedding_type
        self.pen_type = pen_type

    def update_animals(self, new_animals):
        """
        Sets the list of animals to @new_animals and calculates the stocking
        density and each animal's walking distance.

        Args:
            new_animals: list of new animals in the pen
        """
        self.animals_in_pen = new_animals
        self.pen_populated = not (len(self.animals_in_pen) == 0)
        self.stocking_density = len(self.animals_in_pen) / self.num_stalls * 100
        self.calc_daily_walking_dist()

        # sets the current animal classes in the pen
        for animal in self.animals_in_pen:
            stage = type(animal).__name__
            self.classes_in_pen.add(stage)

    def call_animal_nutrient_rqmts(self, housing, pasture_concentrate, feed):
        """
        Calls each animal's nutrient requirement calculation methods.

        Args:
            housing: housing type ("barn" or "pasture")
            pasture_concentrate: concentrate supplementation when farming type
                is "pasture", kg
            feed: an instance of the Feed class
        """
        for animal in self.animals_in_pen:
            if type(animal).__name__ == 'Cow':
                animal.calc_nutrient_rqmts(housing, pasture_concentrate,
                                           feed.nutrient_rqmts)
            else:
                animal.calc_nutrient_rqmts()

    def calc_avg_nutrient_rqmts(self):
        """
        Calculates and sets the average nutrient requirements and necessary
        ration statistics of the animals in the pen.
        """
        first_animal_rqmts = self.animals_in_pen[0].nutrient_rqmts
        sum_dict = {}
        for key in first_animal_rqmts.keys():
            sum_dict[key] = 0

        sum_BW = 0
        sum_DMIest = 0
        sum_DBW = 0
        sum_milk = 0
        sum_CP_milk = 0

        # find sums of nutrients and necessary ration statistics for each
        # animal in the pen
        for animal in self.animals_in_pen:
            curr_rqmts = animal.nutrient_rqmts
            for key in sum_dict.keys():
                sum_dict[key] += curr_rqmts[key]['val']

            sum_BW += animal.body_weight
            sum_DMIest += animal.DMIest
            sum_DBW += animal.DBW
            if type(animal).__name__ == 'Cow':
                sum_milk += animal.estimated_daily_milk_produced
                sum_CP_milk += animal.CP_milk

        # divide by number of animals to find averages
        num_animals = len(self.animals_in_pen)
        for key in sum_dict:
            avg_value = sum_dict[key] / num_animals
            self.avg_nutrient_rqmts[key] = {
                'op': self.animals_in_pen[0].nutrient_rqmts[key]['op'],
                'val': avg_value}

        self.avg_BW = sum_BW / num_animals
        self.avg_DMIest = sum_DMIest / num_animals
        self.avg_DBW = sum_DBW / num_animals
        self.avg_milk = sum_milk / num_animals
        self.avg_CP_milk = sum_CP_milk / num_animals

    def calc_ration(self, housing, pasture_concentrate, feed):
        """
        Calculates and sets the ration for the pen using the average nutrient
        requirements of the animals in the pen.

        Args:
            housing: housing type ("barn" or "pasture")
            pasture_concentrate: concentrate supplementation when farming type
                is "pasture", kg
            feed: instance of the Feed class

        Returns:

        """
        # sets ration's necessary fields for ration formulation calculation
        # there should only be one group of animals in a pen
        while True:

            if 'Calf' in self.classes_in_pen:
                ration_per_animal = calf_optimize()

            elif 'HeiferI' in self.classes_in_pen or \
                    'HeiferII' in self.classes_in_pen or \
                    'HeiferIII' in self.classes_in_pen:
                ration_per_animal = \
                    growing_heifer_optimize()

            elif 'Cow' in self.classes_in_pen and \
                    self.animals_in_pen[0].milking:  # lactating cow
                set_globals(self.avg_DMIest, self.avg_BW, self.avg_DBW,
                            self.avg_milk, self.avg_CP_milk)
                ration_per_animal = \
                    lactating_cow_optimize(feed, self.avg_nutrient_rqmts)

            elif 'Cow' in self.classes_in_pen and \
                    not self.animals_in_pen[0].milking:  # dry cow
                ration_per_animal = dry_cow_optimize()

            else:  # this should never occur
                print('error in pen ration calculation')
                ration_per_animal = {'status': 'Infeasible'}

            if ration_per_animal['status'] == 'Optimal':
                break

            # According to lactating cow ration formulation pseudocode,
            # if a ration isn't feasible, milk production is reduced by 0.5 kg
            # and the formulation is re-run until a feasible ration is obtained.

            # Reduce estimated milk production by 0.5 kg
            for animal in self.animals_in_pen:
                if type(animal).__name__ == 'Cow' and animal.milking:
                    animal.estimated_daily_milk_produced -= 0.5

            # Recalculate animal requirements
            self.call_animal_nutrient_rqmts(housing, pasture_concentrate, feed)

            # Recalculate average requirements
            self.calc_avg_nutrient_rqmts()

        DMI = calc_DMI(ration_per_animal, feed)

        for animal in self.animals_in_pen:
            animal.set_ration(ration_per_animal, DMI)

        # set ration for whole pen by multiplying calculated ration by number
        # of animals in the pen
        num_animals = len(self.animals_in_pen)
        for key in ration_per_animal:
            if key == 'status':
                self.ration[key] = ration_per_animal[key]

            else:  # feeds and price
                self.ration[key] = ration_per_animal[key] * num_animals

    def calc_manure(self, feed):
        """
        Calculates the total manure excretion of the animals in the pen.
        Args:
            feed: instance of the Feed class

        Returns:

        """
        for animal in self.animals_in_pen:
            animal.calc_manure_excretion(feed)

        # obtain keys of manure composition calculations
        first_animal_manure = self.animals_in_pen[0].manure_excretion
        for key in first_animal_manure.keys():
            self.manure[key] = 0

        # find sums of manure components for each animal in the pen for
        # total manure in pen
        for animal in self.animals_in_pen:
            curr_manure = animal.manure_excretion
            for key in self.manure.keys():
                self.manure[key] += curr_manure[key]

    def calc_avg_growth(self):
        """
        Calculates the average growth of the animals in the pen.
        """
        total_growth = 0
        for animal in self.animals_in_pen:
            total_growth += animal.daily_growth
        self.avg_growth = total_growth / len(self.animals_in_pen)

    def calc_daily_walking_dist(self):
        """
        Sets the daily walking distance for the cows in the pen
        """
        if 'Cow' in self.classes_in_pen:
            for animal in self.animals_in_pen:
                if type(animal).__name__ == 'Cow':
                    animal.calc_daily_walking_dist(self.vertical_parlor_dist,
                                                   self.horizontal_parlor_dist)

    def clear(self):
        """
        Clears the pen attributes for re-allocation.
        """
        self.animals_in_pen = []
        self.classes_in_pen = set()
        self.stocking_density = 0
        self.avg_nutrient_rqmts = {}
        self.avg_BW = 0
        self.avg_DMIest = 0
        self.avg_DBW = 0
        self.avg_milk = 0
        self.avg_CP_milk = 0
        self.ration = {}
        self.manure = {}
        self.avg_growth = 0


# methods used for additional ration calculations
def phosphorus_in_ration(ration, feed):
    """
    Args:
        feed: instance of the Feed class, used to determine characteristics
            of available feeds
        ration: the dictionary representing the ration formulation

    Returns: the amount of phosphorus (g) provided by the feed in @ration.
    """
    # amount of P in the formulated ration (g)
    p_intake = 0

    for key in ration:
        # not every key in the ration dictionary refers to a feed
        if key in feed.managed_feed_names:
            managed_feed = Feeds[key]
            nutrients = feed.values(managed_feed)
            p_feed_conc = nutrients[Nutrients.PHOSPHORUS.name]
            dmi_feed = ration[key]

            # amount of P from feed (A.#.A.1)
            p_feed_intake = p_feed_conc / 100 * dmi_feed * 1000

            # (A.#.A.2)
            p_intake += p_feed_intake

    return p_intake


def calc_DMI(ration, feed):
    """
    Args:
        ration: the ration formulation for which the DMI is calculated
        feed: an instance of the Feed class

    Returns: the total Dry Matter Intake from @ration.
    """
    DMI = 0
    for key in ration:
        if key in feed.managed_feed_names:
            DM_feed_amount = ration[key]
            DMI += DM_feed_amount
    return DMI
