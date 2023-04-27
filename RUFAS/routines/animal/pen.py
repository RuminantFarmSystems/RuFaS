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
import copy
from enum import Enum
from typing import List, Dict, Union, DefaultDict, Any

from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.manure.general_manure import AnimalManureExcretions
from RUFAS.routines.animal.ration import animal_requirements as req
from RUFAS.routines.animal.ration import ration_driver as ration_driver
from RUFAS.routines.animal.ration.calf_ration import optimize as calf_optimize

om = OutputManager()


class Pen:
    """
    Manages a pen's operation. Stores the characteristics of the pen and the
    animals that are housed in it any point in the simulation. This class also
    keeps track of some key characteristics of the average animal in the pen.

    Attributes
    -------------
    pen_id : int
        The pen's unique pen ID.
        Obtained from the input file.

    vertical_dist_to_milking_parlor : float
        The vertical distance to milking parlor, measured in kilometers.
        Obtained from the input file.

    horizontal_dist_to_milking_parlor : float
        The horizontal distance to milking parlor, measured in kilometers.
        Obtained from the input file.

    number_of_stalls : int
        The number of stalls.
        Obtained from the input file.

    stocking_density : float
        The stocking density of the pen.
        Calculated when animals in pen are updated in update_animals()

    housing_type : string
        The housing type of the pen.
        Obtained from the input file.

    bedding_type : string
        The bedding type of the pen.
        Obtained from the input file.

    pen_type : string
        The pen type (freestall or tiestall).
        Obtained from the input file.

    manure_handling : string
        The manure handling method used to clean the pen.

    manure_separator : string
        The type of manure separator that processes manure excreted in the pen.

    manure_storage : string
        The type of manure storage receptacle that stores manure excreted in the pen.

    avg_p_intake : float
        The average phosphorus intake of the animals in the pen.

    avg_p_req : float
        The average phosphorus requirements of the animals in the pen.

    avg_p_animal : float
        The average phosphorus content/mass of the animals in the pen.

    animals_in_pen : animal list
        The list of all animals in this pen.

    classes_in_pen : set
        The set (no repeats) of all the classes to which the animals in the pen belong.

    populated : bool
        True iff there is at least 1 animal in the pen, and false otherwise.

    avg_DBW : float
        The average daily change in (delta) body weight of the animals in the pen.
        Used for ration formulation.

    avg_BW : float
        The average body weight of the animals in the pen.
        Used for ration formulation.

    avg_DMIest : float
        The average dry matter intake estimation of the animals in the pen.
        Used for ration formulation

    avg_nutrient_rqmts : dict
        Contains the average nutrient requirements of the animals in the pen.
        Used for ration formulation

    avg_calf_nutrient_rqmts : dict
         Contains the average nutrient requirements of the calves in the pen.
         Used for ration formulation

    avg_milk : float
        The average milk production of the animals in the pen.
        Used for (lactating cow) ration formulation

    avg_CP_milk : float
        The average milk crude protein content of the animals in the pen.
        Used for (lactating cow) ration formulation

    ration : dict
        Contains the ration for all the animals in the pen.

    ration_nutrient_amount : dict
        Contains the total amount of different nutrients in the current ration.

    ration_nutrient_conc : dict
        Contains the concentration of different nutrients in the current ration.

    dry_matter_intake : float
        The dry matter intake value of the animals in the pen.

    avg_growth : float
        The average growth of the animals in the pen.

    MEdiet : float
        The metabolizable energy concentration of the diet fed to the pen.

    _manure_dict_template : dict
        The dictionary template for the manure attributes (manure, calf_total, etc)

    manure : dict
        Contains the total manure excretion of all animals in the pen.

    calf_total : dict
        Contains the total manure excretion of the calves in the pen.

    heifer_total : dict
        Contains the total manure excretion of the heifers in the pen.

    dry_total : dict
        Contains the total manure excretion of the dry cows in the pen.

    lactating_total : dict
        Contains the total manure excretion of the lactating cows in the pen.

    animal_combination : AnimalCombination
        Represents the valid animal type combinations in the pen.
    """

    class AnimalCombination(Enum):
        """
        Enumeration that represents the valid combinations of animals in a pen.
        """
        CALF = 0  # calves
        GROWING = 1  # heiferIs, heiferIIs
        CLOSE_UP = 2  # heiferIIIs, dry cows
        LAC_COW = 3  # lactating cows

        GROWING_AND_CLOSE_UP = 4  # all heifers and dry cows
        NONE = 5  # TODO: Remove this option after fixing _init_default_pens() in AnimalManagement

    def __init__(self, pen_id: int, vertical_dist_to_milking_parlor: float, horizontal_dist_to_milking_parlor: float,
                 number_of_stalls: int, housing_type: str, bedding_type: str, pen_type: str, manure_handling: str,
                 manure_separator: str, manure_storage: str, animal_combination: AnimalCombination,
                 max_stocking_density: float) -> None:
        """
        Initializes a pen with the given arguments.

        Parameters
        ----------
            pen_id: int
                the unique id number of the pen
            vertical_dist_to_milking_parlor: float
                vertical distance to milking parlor, km
            horizontal_dist_to_milking_parlor: float
                horizontal distance to milking parlor, km
            number_of_stalls: int
                number of stalls in the pen
            housing_type: str
                housing type of the pen
            bedding_type: str
                bedding type of the pen
            pen_type: str
                freestall or tiestall
            manure_handling: str
                the manure handling method used to clean the pen
            manure_separator: str
                the manure separator that processes manure excreted in this pen
            manure_storage: str
                the manure storage receptacle that stores manure excreted in this pen
            animal_combination: AnimalCombination
                the valid animal combinations inside this pen, an instance of the AnimalCombination Enum
            max_stocking_density: float
                maximum stocking density allowed for pen
        """
        self.id = pen_id

        self.max_stocking_density = max_stocking_density

        self.vertical_dist_to_parlor = vertical_dist_to_milking_parlor
        self.horizontal_dist_to_parlor = horizontal_dist_to_milking_parlor
        self.num_stalls = number_of_stalls
        self.housing_type = housing_type
        self.bedding_type = bedding_type
        self._pen_type = pen_type

        self.manure_handling = manure_handling
        self.manure_separator = manure_separator
        self.manure_storage = manure_storage
        self.avg_p_intake = 0.0
        self.avg_p_req = 0.0
        self.avg_p_animal = 0.0

        self.animals_in_pen = []
        self.populated = False

        self.classes_in_pen = set()
        self.stocking_density = 0.0

        self.avg_BW = 0.0
        self.avg_DMIest = 0.0
        self.avg_DBW = 0.0

        self.avg_nutrient_rqmts = {}
        self.avg_calf_nutrient_rqmts = {}
        self.avg_milk = 0.0
        self.avg_CP_milk = 0.0

        self.ration = {}
        self.ration_nutrient_amount = {'dm': 0, 'CP': 0, 'ADF': 0,
                                       'NDF': 0, 'lignin': 0, 'ash': 0,
                                       'phosphorus': 0, 'potassium': 0, 'N': 0}
        self.ration_nutrient_conc = {}
        self.dry_matter_intake = 0.0

        self.avg_growth = 0.0

        self.MEdiet = 0.0

        # template for manure, calf_total, etc.
        self._manure_dict_template = AnimalManureExcretions(
            urea=0.0,
            urine=0.0,
            total_ammoniacal_nitrogen_concentration=0.0,
            urine_nitrogen=0.0,
            manure_nitrogen=0.0,
            manure_mass=0.0,
            total_solids=0.0,
            degradable_volatile_solids=0.0,
            non_degradable_volatile_solids=0.0,
            inorganic_phosphorus_fraction=0.0,
            organic_phosphorus_fraction=0.0,
            phosphorus=0.0,
            phosphorus_fraction=0.0,
            potassium=0.0,
            methane=0.0
        )

        # manure attributes are initialized in the reset_manure method
        self.manure = None
        self.calf_total = None
        self.heifer_total = None
        self.dry_total = None
        self.lactating_total = None

        self.reset_manure()

        # set of all the ids for the feeds allocated for this pen object
        self.allocated_feeds = set()

        # the animal_combinations in this pen, utilizes the AnimalCombination Enum
        self.animal_combination = animal_combination

    def set_avg_nutrient_rqmts(self, avg_nutrient_rqmts: Dict[str, float]) -> None:
        """
        Sets the pen's average nutrient requirements

        Parameters
        ----------
        avg_nutrient_rqmts: Dict[str, float]
            The new average nutrient requirements
        """
        self.avg_nutrient_rqmts = {key: value for (key, value) in avg_nutrient_rqmts.items()}

    def set_milk_avgs(self, avg_milk: float, avg_CP_milk: float) -> None:
        """
        Sets the pen's average milk and average CP milk

        Parameters
        ----------
        avg_milk: float
            The new average nutrient requirements
        avg_CP_milk: float
            The new average CP milk
        """
        self.avg_milk = avg_milk
        self.avg_CP_milk = avg_CP_milk

    def add_new_animals(self, new_animals: List[Union[Calf, Cow, HeiferI, HeiferII, HeiferIII]]) -> None:
        """
        Adds all animals in new_animals to the pen.

        Parameters
        ----------
            new_animals: List[Calf | Cow | HeiferI | HeiferII | HeiferIII]
                list of new animals to be added to the pen
        """
        self.animals_in_pen.extend(new_animals)

    def update_pen_populated(self) -> None:
        """
        Updates whether the pen is populated
        """
        self.populated = len(self.animals_in_pen) != 0

    def update_stocking_density(self) -> None:
        """
        Updates the stocking density of the pen
        """
        self.stocking_density = len(self.animals_in_pen) / self.num_stalls

    def update_animal_combination(self, animal_combination: AnimalCombination) -> None:
        """
        Sets the pen's animal combination to animal_combination

        Parameters
        ----------
            animal_combination: AnimalCombination
                the new AnimalCombination
        """
        self.animal_combination = animal_combination

    # TODO: Remove this functionality once pen has been fully switched to AnimalCombination enum
    def update_classes_in_pen(self) -> None:
        """
        Updates the classes contained within the pen
        """
        self.classes_in_pen = set()
        for animal in self.animals_in_pen:
            life_cycle_stage = type(animal).__name__
            self.classes_in_pen.add(life_cycle_stage)

    def update_animals(self, new_animals: List[Any],
                       animal_combination: AnimalCombination) -> None:
        """
        Calls functions that will add new animals to the pen and update associated attributes.

        Parameters
        ----------
            new_animals: List[Calf | Cow | HeiferI | HeiferII | HeiferIII]
                list of new animals to be added to the pen
            animal_combination: AnimalCombination
                an AnimalCombination Enum representing the type of the new animals
        """

        self.add_new_animals(new_animals)
        self.update_pen_populated()
        self.update_stocking_density()
        self.calc_daily_walking_dist()
        self.update_animal_combination(animal_combination)
        self.update_classes_in_pen()

    def calc_ration(self, feed, available_feeds: DefaultDict[Any, Any]):
        """
        Calculates and sets the ration for the pen using the average nutrient
        requirements of the animals in the pen.

        Args:
            feed: instance of the Feed class
            available_feeds: a DefaultDict of the AvailableFeeds class attributes defined in ration_driver.py
        """
        # sets ration's necessary fields for ration formulation calculation
        # there should only be one group of animals in a pen

        while True:
            # TODO: Instead of checking if animal is in a class, check pen tag
            # an error may be caused as result of heifers and dry cows in same pen
            # if we only simulate with 3 pens

            # AnimalCombination.CALF
            if 'Calf' in self.classes_in_pen:
                ration_per_animal = calf_optimize()
                ration_vals = {'ME_tot': 0}

            # AnimalCombination.GROWING
            elif 'HeiferI' in self.classes_in_pen or \
                    'HeiferII' in self.classes_in_pen or \
                    'HeiferIII' in self.classes_in_pen:
                ration_per_animal, ration_vals = \
                    ration_driver.ration_formulation(self, available_feeds, 'heifer', False)

            # AnimalCombination.LAC_COW
            elif 'Cow' in self.classes_in_pen and \
                    self.animals_in_pen[0].milking:  # lactating cow
                ration_per_animal, ration_vals = \
                    ration_driver.ration_formulation(self, available_feeds, 'cow', True)

            # AnimalCombination.CLOSE_UP
            elif 'Cow' in self.classes_in_pen and \
                    not self.animals_in_pen[0].milking:  # dry cow
                ration_per_animal, ration_vals = \
                    ration_driver.ration_formulation(self, available_feeds, 'cow', False)

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
        self.dry_matter_intake = nutrient_amount['dm']

        info_map = {"class": self.__class__.__name__,
                    "function": self.calc_ration.__name__,
                    "available_feeds": available_feeds, }
        om.add_variable("ration_nutrient_amount", nutrient_amount, info_map)
        om.add_variable("ration_nutrient_conc", nutrient_conc, info_map)
        om.add_variable("MEdiet", self.MEdiet, info_map)
        om.add_variable("dry_matter_intake", self.dry_matter_intake, info_map)

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
        Calculates the total manure excretion of the animals in the pen,
         and updates the manure attributes to contain the new amounts.

        Args:
            feed: instance of the Feed class
            methane_model: methane model used for methane emission calculations
        """

        for animal in self.animals_in_pen:
            if type(animal).__name__ == 'Cow':
                animal.calc_manure_excretion(feed, methane_model, self.MEdiet)
            else:
                animal.calc_manure_excretion(feed, methane_model)

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
        # TODO: Write an accumulator function
        for animal in self.animals_in_pen:
            curr_manure = animal.manure_excretion
            if type(animal) == Calf:
                for key in manure.keys():
                    manure[key] += curr_manure[key]
                    calf_total[key] += curr_manure[key]
            elif type(animal) in [HeiferI, HeiferII, HeiferIII]:
                for key in manure.keys():
                    manure[key] += curr_manure[key]
                    heifer_total[key] += curr_manure[key]
            elif type(animal) == Cow and not animal.milking:
                for key in manure.keys():
                    manure[key] += curr_manure[key]
                    dry_total[key] += curr_manure[key]
            elif type(animal) == Cow and animal.milking:
                for key in manure.keys():
                    manure[key] += curr_manure[key]
                    lactating_total[key] += curr_manure[key]

        self.manure = manure
        self.calf_total = calf_total
        self.heifer_total = heifer_total
        self.dry_total = dry_total
        self.lactating_total = lactating_total

        info_map = {"class": self.__class__.__name__,
                    "function": self.calc_manure.__name__,
                    "pen_id": self.id,
                    "pen_animal_combination": self.animal_combination._name_,
                    }

        om.add_variable("pen_manure_data", self.manure, info_map)

    def _copy_manure_template(self):
        return copy.deepcopy(self._manure_dict_template)

    def reset_manure(self):
        self.manure = self._copy_manure_template()
        self.calf_total = self._copy_manure_template()
        self.heifer_total = self._copy_manure_template()
        self.dry_total = self._copy_manure_template()
        self.lactating_total = self._copy_manure_template()

    def calc_avg_growth(self):
        """
        Calculates the average growth of the animals in the pen.
        """

        if not self.populated:
            return

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

    def set_up_new_animal(self, animal, p_conc, feed, temp, num_animals_before_additions):
        """
        Sets the necessary attributes for @animal to be a replacement in this
        pen.

        Args:
            animal: the replacement animal which needs to have necessary values
                for later computations
            p_conc: P concentration of @animal's class, used to calculate the
                P in @animal. -1 for this value indicates that @animal is a
                calf and that its p_animal attribute has already been calculated
            feed: instance of the Feed class defined in feed.py
            temp: temperature on the current day
            num_animals_before_additions: the number of animals in this pen
                before any new animals were added for the day
        """
        if num_animals_before_additions == 0:
            # for the case that there are no animals currently in this pen.
            # Avoids a division by 0 error in below calculations
            # TODO is there a better way?
            num_animals_before_additions = 1

        # TODO: Question - is this necessary or can we assume that any newly
        #   added animals will match the existing animal combination?
        class_name = type(animal).__name__
        self.classes_in_pen.add(class_name)

        if class_name == 'Cow':
            requirements = req.calc_rqmts(body_weight=animal.body_weight, mature_body_weight=animal.mature_body_weight,
                                          day_of_pregnancy=animal.days_in_preg, animal_type='cow',
                                          parity=animal.calves, calving_interval=animal.CI,
                                          milk_true_protein=animal.mPrt, milk_fat=animal.fat_percent,
                                          milk_lactose=animal.lactose_milk,
                                          milk_production=animal.estimated_daily_milk_produced,
                                          days_in_milk=animal.days_in_milk, lactating=animal.milking)
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

        animal.dry_matter_intake = self.dry_matter_intake

        for key in self.ration:
            if key == 'status':
                animal.ration_formulation[key] = self.ration[key]

            else:  # feeds and price
                animal.ration_formulation[key] = self.ration[key] / num_animals_before_additions

        # set animal's manure to be the average manure of all other
        # animals in pen
        for key in self.manure.keys():
            if len(self.animals_in_pen) > 0:
                animal.manure_excretion[key] = self.manure[key] / (len(self.animals_in_pen))

        # since the manure attribute is a total from all animals in the pen,
        # we need to add the current animal's values to the total values for
        # each manure key
        for key in self.manure:
            self.manure[key] += animal.manure_excretion[key]

        # set animal's nutrient requirements to be the average requirements of
        # all other animals in pen
        if class_name == 'Calf':
            animal.nutrient_rqmts = self.avg_calf_nutrient_rqmts
        else:
            animal.nutrient_rqmts = self.avg_nutrient_rqmts

        if animal.nutrient_rqmts == {} and class_name == 'Calf':
            animal.calc_nutrient_rqmts(feed, temp)
        elif animal.nutrient_rqmts == {} and not class_name == 'Calf':
            animal.set_nutrient_rqmts()

        # set animal's DVD and DHD if it is a cow
        if class_name == 'Cow':
            animal.calc_daily_walking_dist(
                self.vertical_dist_to_parlor, self.horizontal_dist_to_parlor)

        # set this animal's p_animal to be the average P concentration of other
        # animals in its class times its body weight
        if not p_conc == -1:
            animal.p_animal = animal.body_weight * p_conc

        animal.p_intake = self.avg_p_intake

        self.animals_in_pen.append(animal)

    def remove_animals_by_ids(self, animal_ids: List[int]) -> None:
        """
        Removes animals from the pen by their ids.

        Notes
        -----
        Because this method takes O(n) time, it is recommended that the caller of this method
        should prepare a list of animal ids to be removed from the pen first, and then call this
        method with that list once.

        Parameters
        ----------
        animal_ids : List[int]
            List of animals that match the given ids to be removed from the pen.

        """
        if not animal_ids:
            return
        animal_ids = set(animal_ids)
        self.animals_in_pen = [animal for animal in self.animals_in_pen if animal.id not in animal_ids]

    def clear(self):
        """
        Clears the pen attributes for re-allocation.
        """
        # All other attributes are kept the same so that if a pen becomes empty
        # and animals are to be added to it, there are previous initial values
        # that are non-zero.
        self.animals_in_pen = []
        self.populated = False
        self.avg_p_animal = 0

    def subset_class_feeds(self, feed):
        """
        Subsets the feed_ids list to appropriately include the feeds necessary for that pen object,
        based on the animal type(s) that are currently in the pen.

        Args:
            feed: an object of the Feed class
        """

        self.allocated_feeds = feed.input_feed_combinations[self.animal_combination]
