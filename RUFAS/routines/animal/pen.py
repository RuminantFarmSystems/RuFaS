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
    """
    Manages a pen's operation. Stores the characteristics of the pen and the
    animals that are housed in it any point in the simulation. This class also
    keeps track of some key characteristics of the average animal in the pen.
    """
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
    vertical_dist_to_parlor = 0

    # horizontal distance to milking parlor, km, from input file
    horizontal_dist_to_parlor = 0

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

    # average daily change in (delta) body weight of the animals in the pen,
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
    manure = {"U": 0,
              "TAN_s": 0,
              "MN": 0,
              "Mkg": 0,
              "VSd": 0,
              "VSnd": 0,
              "WIP_frac": 0,
              "WOP_frac": 0,
              "p_excrt_manure": 0,
              "p_frac": 0}

    # average growth of the animals in the pen
    avg_growth = 0

    # average phosphorus of the animals in the pen
    avg_p_animal = 0

    # average phosphorus requirement of the animals in the pen
    avg_p_req = 0

    avg_p_intake = 0

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
        self.vertical_dist_to_parlor = vert_dist
        self.horizontal_dist_to_parlor = horiz_dist
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
            # currently, only lactating cows have ration calculations, so there
            # are different arguments
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
                ration_per_animal = calf_optimize(feed, self.avg_nutrient_rqmts)

            elif 'HeiferI' in self.classes_in_pen or \
                    'HeiferII' in self.classes_in_pen or \
                    'HeiferIII' in self.classes_in_pen:
                ration_per_animal = \
                    growing_heifer_optimize(feed, self.avg_nutrient_rqmts)

            elif 'Cow' in self.classes_in_pen and \
                    self.animals_in_pen[0].milking:  # lactating cow
                set_globals(self.avg_DMIest, self.avg_BW, self.avg_DBW,
                            self.avg_milk, self.avg_CP_milk)
                ration_per_animal = \
                    lactating_cow_optimize(feed, self.avg_nutrient_rqmts)

            elif 'Cow' in self.classes_in_pen and \
                    not self.animals_in_pen[0].milking:  # dry cow
                ration_per_animal = \
                    dry_cow_optimize(feed, self.avg_nutrient_rqmts)

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
        self.avg_p_intake, p_conc = \
            phosphorus_in_ration(DMI, ration_per_animal, feed)

        for animal in self.animals_in_pen:
            animal.set_ration(ration_per_animal, DMI)
            animal.set_p_intake(self.avg_p_intake, p_conc)

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
        Sets the daily walking distance for the cows in the pen (if any).
        """
        if 'Cow' in self.classes_in_pen:
            for animal in self.animals_in_pen:
                if type(animal).__name__ == 'Cow':
                    animal.calc_daily_walking_dist(self.vertical_dist_to_parlor,
                                                   self.horizontal_dist_to_parlor)

    def call_p_rqmts(self, feed):
        """
        Calls each animal's method to calculate phosphorus requirements.

        Args:
            feed: instance of the Feed class
        """
        # since each animal in the pen receives the same ration
        if len(self.animals_in_pen) > 0:
            DMI = calc_DMI(self.animals_in_pen[0].ration_formulation, feed)

            total_p_req = 0
            for animal in self.animals_in_pen:
                animal.phosphorus_rqmts(DMI)
                total_p_req += animal.p_req
            self.avg_p_req = total_p_req / len(self.animals_in_pen)

    def daily_p_update(self):
        """
        Calls each animal's method to calculate daily phosphorus update.
        """
        if not len(self.animals_in_pen) == 0:
            total_p_animal = 0
            for animal in self.animals_in_pen:
                animal.daily_p_update()
                total_p_animal += animal.p_animal
            self.avg_p_animal = total_p_animal / len(self.animals_in_pen)

    def set_up_new_animal(self, animal, p_comp):
        """
        Sets the necessary attributes for @animal to be a replacement in this
        pen.

        Args:
            p_comp: P composition of @animal's class, used to calculate the
                P in @animal. -1 for this value indicates that @animal is a
                calf and that its p_animal attribute has already been calculated
            animal: the replacement animal which needs to have necessary values
                for later computations
        """
        num_animals = len(self.animals_in_pen)
        if num_animals == 0:
            # for the case that there are no animals currently in this pen.
            # Avoids a division by 0 error in below calculations
            # TODO is there a better way?
            num_animals = 1

        # set animal's ration to be the intake of all other animals in pen
        for key in self.ration:
            if key == 'status':
                animal.ration_formulation[key] = self.ration[key]

            else:  # feeds and price
                animal.ration_formulation[key] = self.ration[key] / num_animals

        # set animal's manure to be the average manure of all other
        # animals in pen
        for key in self.manure.keys():
            animal.manure_excretion[key] = self.manure[key] / num_animals

        # set animal's nutrient requirements to be the average requirements of
        # all other animals in pen
        animal.nutrient_rqmts = self.avg_nutrient_rqmts

        # set animal's DVD and DHD if it is a cow
        if type(animal).__name__ == 'Cow':
            animal.calc_daily_walking_dist(
                self.vertical_parlor_dist, self.horizontal_parlor_dist)

        # set this animal's p_animal to be the average P concentration of other
        # animals in its class times its body weight
        if not p_comp == -1:
            animal.p_animal = animal.body_weight * p_comp

        animal.p_intake = self.avg_p_intake

        # self.animals_in_pen.append(animal)

    def clear(self):
        """
        Clears the pen attributes for re-allocation.
        """
        # All other attributes are kept the same so that if a pen becomes empty
        # and animals are to be added to it, there are previous initial values
        # that are non-zero.
        self.animals_in_pen = []
        self.pen_populated = False
        self.classes_in_pen = set()
        self.avg_p_animal = 0


# methods used for additional ration calculations
def phosphorus_in_ration(DMI, ration, feed):
    """
    Args:
        DMI: the total dry matter intake of the ration
        feed: instance of the Feed class, used to determine characteristics
            of available feeds
        ration: the dictionary representing the ration formulation

    Returns: the amount of phosphorus (g) provided by the feed in @ration and
            the concentration of P in @ration (%)

    TODO: These calculations could be placed in ration subfolder with ration update
    """
    # amount of P in the formulated ration (g)
    p_intake = 0

    for key in ration:
        # not every key in the ration dictionary refers to a feed
        if key in feed.managed_feed_names:
            managed_feed = Feeds[key]
            nutrients = feed.values(managed_feed)
            p_feed_conc = nutrients[Nutrients.P_DM.name]
            dmi_feed = ration[key]

            # amount of P from feed (g) (A.4.A.1)
            p_feed_intake = p_feed_conc / 100 * dmi_feed * 1000

            # P intake from ration (g) (A.4.A.2)
            p_intake += p_feed_intake

    # P concentration in ration (%) (A.4.A.3)
    p_conc = p_intake / DMI * (1 / 1000) * 100

    return p_intake, p_conc


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
