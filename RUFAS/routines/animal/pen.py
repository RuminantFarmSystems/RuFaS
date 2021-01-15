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
from RUFAS.routines.animal.ration.calf_ration import optimize as calf_optimize
from RUFAS.routines.animal.ration import ration_driver as ration_driver
from RUFAS.routines.animal.ration import animal_requirements as req

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
    avg_calf_nutrient_rqmts = {}

    # average body weight of the animals in the pen, used for ration formulation
    avg_BW = 0

    # average dry matter intake estimation of the animals in the pen,
    # used for ration formulation
    avg_DMIest = 0

    # average daily change in (delta) body weight of the animals in the pen,
    # used for ration formulation
    #avg_DBW = 0

    # average milk production of the animals in the pen,
    # used for (lactating cow) ration formulation
    avg_milk = 0

    # average milk crude protein content of the animals in the pen,
    # used for (lactating cow) ration formulation
    avg_CP_milk = 0

    # ration for all the animals in the pen
    ration = {}

    # total amount of different nutrients in current ration
    ration_nutrient_amount = {'dm_amount': 0, 'cp_amount': 0, 'adf_amount': 0,
                              'ndf_amount': 0, 'lignin_amount': 0, 'ash_amount': 0,
                              'P_amount': 0, 'K_amount': 0, 'N_amount': 0}

    # concentration of different nutrients in current ration
    ration_nutrient_conc = {}

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
        #self.DBW = 0.0
        self.daily_growth = 0.0

    def update_animals(self, new_animals):
        """
        Sets the list of animals to @new_animals and calculates the stocking
        density and each animal's walking distance.

        Args:
            new_animals: list of new animals in the pen
        """
        # self.animals_in_pen = new_animals
        for animal in new_animals:
            self.animals_in_pen.append(animal)
        self.pen_populated = not (len(self.animals_in_pen) == 0)
        self.stocking_density = len(self.animals_in_pen) / self.num_stalls * 100
        self.calc_daily_walking_dist()

        # sets the current animal classes in the pen
        self.classes_in_pen = set()
        for animal in self.animals_in_pen:
            stage = type(animal).__name__
            self.classes_in_pen.add(stage)

    def calc_avg_nutrient_rqmts(self):
        """
        Calculates and sets the average nutrient requirements and necessary
        ration statistics of the animals in the pen.
        """
        first_animal_rqmts = self.animals_in_pen[0].nutrient_rqmts
        sum_dict = {}
        avg_dict = {}
        for key in first_animal_rqmts.keys():
            sum_dict[key] = 0

        sum_BW = 0
        sum_DMIest = 0
        #sum_DBW = 0
        sum_milk = 0
        sum_CP_milk = 0

        # find sums of nutrients and necessary ration statistics for each
        # animal in the pen
        for animal in self.animals_in_pen:
            curr_rqmts = animal.nutrient_rqmts
            if curr_rqmts == {}:
                print(type(animal).__name__, animal.id, self.id, self.avg_calf_nutrient_rqmts)

            for key in sum_dict.keys():
                sum_dict[key] += curr_rqmts[key]['val']

            sum_BW += animal.body_weight
            sum_DMIest += animal.DMIest
            #sum_DBW += animal.DBW
            #sum_DBW += animal.DBW
            if type(animal).__name__ == 'Cow':
                sum_milk += animal.estimated_daily_milk_produced
                sum_CP_milk += animal.CP_milk

        # divide by number of animals to find averages
        num_animals = len(self.animals_in_pen)
        for key in sum_dict:
            avg_value = sum_dict[key] / num_animals
            avg_dict[key] = {
                'op': self.animals_in_pen[0].nutrient_rqmts[key]['op'],
                'val': avg_value}

        if 'Calf' in self.classes_in_pen:
            self.avg_calf_nutrient_rqmts = avg_dict
        else:
            self.avg_nutrient_rqmts = avg_dict

        self.avg_BW = sum_BW / num_animals
        self.avg_DMIest = sum_DMIest / num_animals
        #self.avg_DBW = sum_DBW / num_animals
        self.avg_milk = sum_milk / num_animals
        self.avg_CP_milk = sum_CP_milk / num_animals

    def calc_avg_stats(self):
        """
        Calculates the pen's average statistics for a ration calculation that
        is not during the normal ration formulation, i.e. when animals are
        added to a pen with no animals currently in it and the ration needs
        to be calculated for those animals.
        """
        num_animals = len(self.animals_in_pen)
        sum_BW = 0
        sum_DMIest = 0
        #sum_DBW = 0
        sum_milk = 0
        sum_CP_milk = 0

        for animal in self.animals_in_pen:
            sum_BW += animal.body_weight
            sum_DMIest += animal.DMIest
            #sum_DBW += animal.DBW
            if type(animal).__name__ == 'Cow':
                sum_milk += animal.estimated_daily_milk_produced
                sum_CP_milk += animal.CP_milk

        self.avg_BW = sum_BW / num_animals
        self.avg_DMIest = sum_DMIest / num_animals
        #self.avg_DBW = sum_DBW / num_animals
        self.avg_milk = sum_milk / num_animals
        self.avg_CP_milk = sum_CP_milk / num_animals


    def calc_ration(self, feed, available_feeds):
        """
        Calculates and sets the ration for the pen using the average nutrient
        requirements of the animals in the pen.

        Args:
            feed: instance of the Feed class
            available_feeds: instance of the AvailableFeeds class defined in ration_driver.py
        """
        # sets ration's necessary fields for ration formulation calculation
        # there should only be one group of animals in a pen
        while True:
            #TODO: Instead of checking if animal is in a class, check pen tag
            #an error may be caused as result of heifers and dry cows in same pen
            #if we only simulate with 3 pens
            if 'Calf' in self.classes_in_pen:
                ration_per_animal = calf_optimize()

            elif 'HeiferI' in self.classes_in_pen or \
                    'HeiferII' in self.classes_in_pen or \
                    'HeiferIII' in self.classes_in_pen:
                ration_per_animal = \
                    ration_driver.ration_formulation(self, available_feeds, \
                                                    'heifer', False)

            elif 'Cow' in self.classes_in_pen and \
                    self.animals_in_pen[0].milking:  # lactating cow
                ration_per_animal = \
                    ration_driver.ration_formulation(self, available_feeds, \
                                                                'cow', True)

            elif 'Cow' in self.classes_in_pen and \
                    not self.animals_in_pen[0].milking:  # dry cow
                ration_per_animal = \
                    ration_driver.ration_formulation(self, available_feeds, \
                                                                'cow', False)

            else:  # this should never occur
                print('error in pen ration calculation')
                ration_per_animal = {'status': 'Infeasible'}

            if ration_per_animal['status'] == 'Optimal':
                break

        # recording ration nutrition information in pen
        nutrient_amount, nutrient_conc = ration_driver.ration_report(
            ration_per_animal, feed.available_feeds)
        self.ration_nutrient_amount = nutrient_amount
        self.ration_nutrient_conc = nutrient_conc

        for animal in self.animals_in_pen:
            animal.set_ration(ration_per_animal, nutrient_amount['dm_amount'])
            animal.set_p_intake(nutrient_amount['P_amount'],
                                nutrient_conc['P_conc'])
        # set ration for whole pen by multiplying calculated ration by number
        # of animals in the pen
        ration = {}
        num_animals = len(self.animals_in_pen)
        for key in ration_per_animal:
            if key == 'status':
                ration[key] = ration_per_animal[key]

            else:  # feeds and price
                ration[key] = ration_per_animal[key] * num_animals

        return ration

    def calc_manure(self, feed):
        """
        Calculates the total manure excretion of the animals in the pen.

        Args:
            feed: instance of the Feed class

        Returns:
            a dictionary for the total manure of the animals in the pen
        """
        for animal in self.animals_in_pen:
            animal.calc_manure_excretion(feed)

        manure = {}

        # obtain keys of manure composition calculations
        first_animal_manure = self.animals_in_pen[0].manure_excretion
        for key in first_animal_manure.keys():
            manure[key] = 0

        # find sums of manure components for each animal in the pen for
        # total manure in pen
        for animal in self.animals_in_pen:
            curr_manure = animal.manure_excretion
            for key in manure.keys():
                manure[key] += curr_manure[key]

        return manure

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

    def call_p_rqmts(self):
        """
        Calls each animal's method to calculate phosphorus requirements.
        """
        # since each animal in the pen receives the same ration
        if len(self.animals_in_pen) > 0:
            DMI = self.ration_nutrient_amount['dm_amount']

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

    def set_up_new_animal(self, animal, p_comp, feed, temp):
        """
        Sets the necessary attributes for @animal to be a replacement in this
        pen.

        Args:
            animal: the replacement animal which needs to have necessary values
                for later computations
            p_comp: P composition of @animal's class, used to calculate the
                P in @animal. -1 for this value indicates that @animal is a
                calf and that its p_animal attribute has already been calculated
            feed: instance of the Feed class defined in feed.py
            temp: temperature on the current day
        """
        num_animals = len(self.animals_in_pen)
        if num_animals == 0:
            # for the case that there are no animals currently in this pen.
            # Avoids a division by 0 error in below calculations
            # TODO is there a better way?
            num_animals = 1

        class_name = type(animal).__name__
        self.classes_in_pen.add(class_name)

        if class_name == 'Cow':
            requirements = req.calc_rqmts(animal.body_weight, animal.mature_body_weight,
                                          animal.days_in_preg,'cow', animal.calves,
                                          animal.CI, animal.mPrt, animal.fat_percent,
                                          animal.lactose_milk,
                                          animal.estimated_daily_milk_produced,
                                          animal.days_in_milk,
                                          animal.milking)
            animal.NEmaint = requirements['NEmaint']
            animal.NEg = requirements['NEg']
            animal.NEpreg = requirements['NEpreg']
            animal.NEl = requirements['NEl']
            animal.MP_req = requirements['MP_req']
            animal.Ca_req = requirements['Ca_req']
            animal.P_req = requirements['P_req']
            animal.DMIest = requirements['DMIest']
            animal.DNED_req = (requirements['NEmaint'] + requirements[
                'NEl']) / animal.DMIest
            animal.DMPD_req = (requirements['MP_req']) / animal.DMIest

        # set animal's ration to be the intake of all other animals in pen
        # if self.ration == {}:
        #     self.ration = self.calc_ration(feed, temp)

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
        if class_name == 'Calf':
            animal.nutrient_rqmts = self.avg_calf_nutrient_rqmts
        else:
            animal.nutrient_rqmts = self.avg_nutrient_rqmts

        if animal.nutrient_rqmts == {} and class_name == 'Calf':
            animal.calc_nutrient_rqmts(feed, temp)
        elif animal.nutrient_rqmts == {} and not class_name == 'Calf':
            animal.calc_nutrient_rqmts()


        # set animal's DVD and DHD if it is a cow
        if class_name == 'Cow':
            animal.calc_daily_walking_dist(
                self.vertical_dist_to_parlor, self.horizontal_dist_to_parlor)

        # set this animal's p_animal to be the average P concentration of other
        # animals in its class times its body weight
        if not p_comp == -1:
            animal.p_animal = animal.body_weight * p_comp

        animal.p_intake = self.avg_p_intake

        self.animals_in_pen.append(animal)

    def clear(self):
        """
        Clears the pen attributes for re-allocation.
        """
        # All other attributes are kept the same so that if a pen becomes empty
        # and animals are to be added to it, there are previous initial values
        # that are non-zero.
        self.animals_in_pen = []
        self.pen_populated = False
        # self.classes_in_pen = set()
        self.avg_p_animal = 0
