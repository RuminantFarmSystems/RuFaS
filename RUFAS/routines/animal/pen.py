"""
RUFAS: Ruminant Farm Systems Model
File name: pen.py
Description: The class which represents a pen on the farm. Each pen has
    operations as described in the Animal Module Information Flow document on
    Basecamp (such as calculating average nutrient requirements, ration,
    manure excretion, etc). Method calls cascade through from the animal
    management class to pen to each individual animal in that pen.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
           Joseph Merhi, jm2257@cornell.edu
"""
from RUFAS.routines.animal.ration.calf_ration import optimize as calf_optimize
from RUFAS.routines.animal.ration.growing_heifer_ration import \
    optimize as growing_heifer_optimize
from RUFAS.routines.animal.ration import cow_requirements as req
from RUFAS.routines.animal.ration import ration_driver as ration_driver
import copy


class Pen:
    """
    Manages a pen's operation. Stores the characteristics of the pen and the
    animals that are housed in it any point in the simulation. This class also
    keeps track of some key characteristics of the average animal in the pen.

    Attributes
    -------------
    id : int
        This variable represents a pen's unique pen ID, gotten from the input file.

    vertical_dist_to_parlor : float
        This variable represents the vertical distance to milking parlor, measured in kilometers.
        It is gotten from the input file.

    horizontal_dist_to_parlor : float
        This variable represents the horizontal distance to milking parlor, measured in kilometers.
        It is gotten from the input file

    num_stalls : int
        This variable represents the number of stalls, gotten from the input file.

    stocking_density : float
        This variable represents the stocking density of the pen, and is calculated when animals in pen are
        updated in update_animals()

    housing_type : string
        This variable represents the housing type of the pen, gotten from the input file.

    bedding_type : string
        This variable represents the bedding type of the pen, gotten from the input file.

    pen_type : string
        This variable represents the pen type (freestall or tiestall), gotten from the input file.

    animals_in_pen : animal list
        This variable represents the list of all animals in this pen

    classes_in_pen : set
        This variable represents the set (no repeats) of all the classes to which the animals in pen belong.

    pen_populated : bool
        This variable checks if len(self.animals_in_pen) == 0, that is, if there are any animals in the pen.

    avg_DBW : float
        This variable represents the average daily change in (delta) body weight of the
        animals in the pen, and is used for ration formulation.

    avg_BW : float
        This variable represents the average body weight of the animals in the pen, and is used for ration formulation.

    avg_DMIest : float
        This variable represents the average dry matter intake estimation of the animals in the pen,
        and is used for ration formulation

    avg_nutrient_rqmts : dict
    avg_calf_nutrient_rqmts : dict
        These variables represent the dictionaries containing the nutrient requirements in the pen, and
        are used for ration formulation

    avg_milk : float
        This variable represents the average milk production of the animals in the pen, and is
        used for (lactating cow) ration formulation

    avg_CP_milk : float
        This variable represents the average milk crude protein content of the animals in the pen, and is
        used for (lactating cow) ration formulation

    ration : dict
        This variable represents the dictionary containing the ration for all the animals in the pen.

    ration_nutrient_amount : dict
        This variable represents the total amount of different nutrients in the current ration.

    ration_nutrient_conc : dict
        This variable represents the dictionary containing the concentration of different nutrients
        in the current ration.

    avg_growth : float
        This variable represents the average growth of the animals in the pen.

    manure : dict
        This variable represents a dictionary containing the total manure excretion of the animals in the pen.

    calf_total : dict
        This variable represents a dictionary containing the total manure excretion of the calves in the pen.

    heifer_total : dict
        This variable represents a dictionary containing the total manure excretion of the heifers in the pen.

    dry_total : dict
        This variable represents a dictionary containing the total manure excretion of the dry cows in the pen.

    lacatating_total : dict
        This variable represents a dictionary containing the total manure excretion of the lactating cows in the pen.
    """

    def __init__(self, id_number, vert_dist, horiz_dist, num_stalls, housing_type,
                 bedding_type, pen_type, manure_handling, manure_separator, manure_storage):
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
            manure_handling: the manure handling method used to clean the pen
            manure_separator: the manure separator that processes manure excreted in this pen
            manure_storage: the manure storage receptacle that stores manure excreted in this pen
        """
        self.id = id_number

        self.vertical_dist_to_parlor = vert_dist
        self.horizontal_dist_to_parlor = horiz_dist
        self.num_stalls = num_stalls
        self.housing_type = housing_type
        self.bedding_type = bedding_type
        self.pen_type = pen_type
        self.DBW = 0.0
        self.daily_growth = 0.0
        self.manure_handling = manure_handling
        self.manure_separator = manure_separator
        self.manure_storage = manure_storage
        self.avg_p_intake = 0
        self.avg_p_req = 0
        self.avg_p_animal = 0
        self.animals_in_pen = []
        self.pen_populated = False

        self.classes_in_pen = set()
        self.stocking_density = 0

        self.avg_BW = 0
        self.avg_DMIest = 0

        self.avg_nutrient_rqmts = {}
        self.avg_calf_nutrient_rqmts = {}
        self.avg_milk = 0
        self.avg_CP_milk = 0

        self.ration = {}
        self.ration_nutrient_amount = {'dm': 0, 'CP': 0, 'ADF': 0,
                                       'NDF': 0, 'lignin': 0, 'ash': 0,
                                       'phosphorus': 0, 'potassium': 0, 'N': 0}
        self.ration_nutrient_conc = {}

        # initial state for manure, calf_total, etc.
        self.init_dict = {"U": 0,
                          "TAN_s": 0,
                          "MN": 0,
                          "Mkg": 0,
                          "TSd": 0,
                          "VSd": 0,
                          "VSnd": 0,
                          "WIP_frac": 0,
                          "WOP_frac": 0,
                          "p_excrt_manure": 0,
                          "p_frac": 0,
                          "K_manure": 0,
                          "CH4_manure": 0
                          }

        self.manure = copy.deepcopy(self.init_dict)
        self.calf_total = copy.deepcopy(self.init_dict)
        self.heifer_total = copy.deepcopy(self.init_dict)
        self.dry_total = copy.deepcopy(self.init_dict)
        self.lactating_total = copy.deepcopy(self.init_dict)

    # Getters

    def get_id(self):
        """
        Returns:
            int : the id_number, the unique id number of the pen.
        """
        return self.id

    def get_pen_type(self):
        """
        Returns:
            string : the pen type: freestall or tiestall.
        """
        return self.pen_type

    # Setters

    def set_id(self, pen_id):
        """
        Sets the pen's id to id.

        Args:
            pen_id: The pen's unique pen ID, obtained from the input file.
        """
        self.id = pen_id

    def set_pen_type(self, pen_type):
        """
        Sets the pen type of the pen to pen_type.

        Args:
            pen_type: The pen type of the pen.
        """
        self.pen_type = pen_type

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
        self.stocking_density = len(
            self.animals_in_pen) / self.num_stalls * 100
        self.calc_daily_walking_dist()

        # sets the current animal classes in the pen
        self.classes_in_pen = set()
        for animal in self.animals_in_pen:
            stage = type(animal).__name__
            self.classes_in_pen.add(stage)

    def call_animal_nutrient_rqmts(self, feed, temp):
        """
        Calls each animal's nutrient requirement calculation methods.

        Args:
            feed: an instance of the Feed class defined in feed.py
            temp: the temperature on the current day
        """
        for animal in self.animals_in_pen:
            # currently, only lactating cows have ration calculations, so there
            # are different arguments
            if type(animal).__name__ == 'Cow':
                # old hard coded variable updates from the deleted calc_requirements in
                # cow.py
                self.DBW = -0.4125
                self.daily_growth = self.DBW
            elif type(animal).__name__ == 'Calf':
                animal.calc_nutrient_rqmts(feed, temp)
            else:
                animal.calc_nutrient_rqmts()

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
        sum_DBW = 0
        sum_milk = 0
        sum_CP_milk = 0

        # find sums of nutrients and necessary ration statistics for each
        # animal in the pen
        for animal in self.animals_in_pen:
            curr_rqmts = animal.nutrient_rqmts
            if curr_rqmts == {}:
                print(type(animal).__name__, animal.id,
                      self.id, self.avg_calf_nutrient_rqmts)

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
            avg_dict[key] = {
                'op': self.animals_in_pen[0].nutrient_rqmts[key]['op'],
                'val': avg_value}

        if 'Calf' in self.classes_in_pen:
            self.avg_calf_nutrient_rqmts = avg_dict
        else:
            self.avg_nutrient_rqmts = avg_dict

        self.avg_BW = sum_BW / num_animals
        self.avg_DMIest = sum_DMIest / num_animals
        self.avg_DBW = sum_DBW / num_animals
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
        sum_DBW = 0
        sum_milk = 0
        sum_CP_milk = 0

        for animal in self.animals_in_pen:
            sum_BW += animal.body_weight
            sum_DMIest += animal.DMIest
            sum_DBW += animal.DBW
            if type(animal).__name__ == 'Cow':
                sum_milk += animal.estimated_daily_milk_produced
                sum_CP_milk += animal.CP_milk

        self.avg_BW = sum_BW / num_animals
        self.avg_DMIest = sum_DMIest / num_animals
        self.avg_DBW = sum_DBW / num_animals
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
            if 'Calf' in self.classes_in_pen:
                ration_per_animal = calf_optimize()
                ration_vals = {'ME_tot': 0}

            elif 'HeiferI' in self.classes_in_pen or \
                    'HeiferII' in self.classes_in_pen or \
                    'HeiferIII' in self.classes_in_pen:
                ration_per_animal = \
                    growing_heifer_optimize()
                ration_vals = {'ME_tot': 0}

            elif 'Cow' in self.classes_in_pen and \
                    self.animals_in_pen[0].milking:  # lactating cow
                ration_per_animal, ration_vals = \
                    ration_driver.ration_formulation(
                        self, available_feeds, True)
            elif 'Cow' in self.classes_in_pen and \
                    not self.animals_in_pen[0].milking:  # dry cow
                ration_per_animal, ration_vals = \
                    ration_driver.ration_formulation(
                        self, available_feeds, False)

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
        self.MEdiet = ration_vals['ME_tot']

        for animal in self.animals_in_pen:
            animal.set_ration(ration_per_animal, nutrient_amount['dm'])
            animal.set_p_intake(nutrient_amount['phosphorus'],
                                nutrient_conc['phosphorus'])
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

    def calc_manure(self, feed, methane_model):
        """
        Calculates the total manure excretion of the animals in the pen.

        Args:
            feed: instance of the Feed class
            methane_model: methane model used for methane emission calculations

        Returns:
            a dictionary for the total manure of the animals in the pen
        """
        ME_intake = self.MEdiet
        for animal in self.animals_in_pen:
            if type(animal).__name__ == 'Cow':
                animal.calc_manure_excretion(feed, methane_model, ME_intake)
            else:
                animal.calc_manure_excretion(feed)

        manure = {}
        calf_total = {}
        heifer_total = {}
        dry_total = {}
        lactating_total = {}

        # obtain keys of manure composition calculations
        first_animal_manure = self.animals_in_pen[0].manure_excretion
        for key in first_animal_manure.keys():
            manure[key] = 0
            calf_total[key] = 0
            heifer_total[key] = 0
            dry_total[key] = 0
            lactating_total[key] = 0

        # find sums of manure components for each animal in the pen for
        # total manure in pen and total manure by animal type
        for animal in self.animals_in_pen:
            curr_manure = animal.manure_excretion
            if type(animal).__name__ == 'Calf':
                for key in manure.keys():
                    manure[key] += curr_manure[key]
                    calf_total[key] += curr_manure[key]
            elif type(animal).__name__ == 'Heifer':
                for key in manure.keys():
                    manure[key] += curr_manure[key]
                    heifer_total[key] += curr_manure[key]
            elif type(animal).__name__ == 'Cow' and not animal.milking:
                for key in manure.keys():
                    manure[key] += curr_manure[key]
                    dry_total[key] += curr_manure[key]
            elif type(animal).__name__ == 'Cow' and animal.milking:
                for key in manure.keys():
                    manure[key] += curr_manure[key]
                    lactating_total[key] += curr_manure[key]

        self.manure = manure
        self.calf_total = calf_total
        self.heifer_total = heifer_total
        self.dry_total = dry_total
        self.lactating_total = lactating_total

    def reset_manure(self):
        # total manure excretion of the animals in the pen
        self.manure = copy.deepcopy(self.init_dict)

        # total manure excretion of the calves in the pen
        self.calf_total = copy.deepcopy(self.init_dict)

        # total manure excretion of the heifers in the pen
        self.heifer_total = copy.deepcopy(self.init_dict)

        # total manure excretion of the dry cows in the pen
        self.dry_total = copy.deepcopy(self.init_dict)

        # total manure excretion of the lactating cows in the pen
        self.lactating_total = copy.deepcopy(self.init_dict)

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
            DMI = self.ration_nutrient_amount['dm']

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
                                          animal.days_in_preg, animal.calves, animal.CI,
                                          animal.mPrt, animal.fat_percent,
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


