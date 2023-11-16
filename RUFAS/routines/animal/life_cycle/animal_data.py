import copy
import random
from dataclasses import dataclass
from random import shuffle
from typing import List, Dict, Any, Type

from scipy.stats import truncnorm

from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.animal_typed_dicts import HerdInfoTypedDict
from RUFAS.routines.animal.life_cycle.animal_factory import AnimalFactory
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.life_cycle.cow import Cow

from RUFAS.input_manager import InputManager

im = InputManager()


@dataclass(kw_only=True)
class AnimalData:
    """
        A class to hold and manage animal data for a farm or herd.

        Attributes:
        ----------
        animal_id : int
            A class variable that holds a unique identifier for the animal which auto-increments.
        CI: int
            Calving interval.
        breed : str
            The breed of the animal.
        order_by_random: bool
            Whether to shuffle the order of animals from input data.
        init_herd: bool
            Whether to generate animals or not.
        save_animals: bool
            Whether to save the generated animals or not.
        terminate_simulation_post_herd_generation: bool
            Whether to terminate the simulation after generating animals or not.
        initial_animal_num: int
            The initial number of animals for the simulation starting with to generate the herd.
        simulation_days: int
            The number of days to simulate for generating the herd.
        calf_num : int
            The number of calves.
        heiferI_num : int
            The number of heiferIs.
        heiferII_num : int
            The number of heiferIIs.
        heiferIII_num : int
            The number of heiferIIIs.
        cow_num : int
            The number of cows.
        replace_num : int
            The number of cows available for replacement.
        num_calves_in_data: int
            The number of calves available from the input data.
        num_heiferIs_in_data: int
            The number of heiferIs available from the input data.
        num_heiferIIs_in_data: int
            The number of heiferIIs available from the input data.
        num_heiferIIIs_in_data: int
            The number of heiferIIIs available from the input data.
        num_cows_in_data: int
            The number of cows available from the input data.
        num_replacement_cows_in_data: int
            The number of replacement cows available from the input data.
        calves : List[Calf]
            A list of Calf instances.
        heiferIs : List[HeiferI]
            A list of HeiferI instances.
        heiferIIs : List[HeiferII]
            A list of HeiferII instances.
        heiferIIIs : List[HeiferIII]
            A list of HeiferIII instances.
        cows : List[Cow]
            A list of Cow instances.
        replacement : List[Cow]
            A list of Cow instances that are marked for replacement.
        birth_weight_ho : float
            The birth weight for the Holstein breed following a truncated normal distribution.
        birth_weight_je : float
            The birth weight for the Jersey breed following a truncated normal distribution.

        Methods:
        -------
        next_id() -> int:
            Increments the animal_id by 1 and returns the new value.
        __init__(CI, herd_data: HerdInfoTypedDict, set_seed) -> None:
            The class constructor which initializes the AnimalData instance with the provided herd data.

        get_calves(num: int, breed: str) -> List[Calf]
            Retrieve and optionally shuffle a list of calf instances.

        get_heiferIs(num: int, breed: str) -> List[HeiferI]
            Retrieve and optionally shuffle a list of HeiferI instances.

        get_heiferIIs(num: int, breed: str) -> List[HeiferII]
            Retrieve and optionally shuffle a list of HeiferII instances.

        get_heiferIIIs(num: int, breed: str) -> List[HeiferIII]
            Retrieve and optionally shuffle a list of HeiferIII instances.

        get_cows(num: int, breed: str) -> List[Cow]
            Retrieve and optionally shuffle a list of cow instances.

        get_replacement_cows(num: int, breed: str) -> List[Cow]
            Retrieve and optionally shuffle a list of replacement cow instances.

        initialization_db_summary(self) -> Dict[str, int | float]
            Return a dictionary which stores the summary of the initialization.
        """
    # animal_id = 378165
    animal_id = 0

    CI: int
    breed: str
    order_by_random: bool
    init_herd: bool
    save_animals: bool
    terminate_simulation_post_herd_generation: bool

    initial_animal_num: int
    simulation_days: int

    calf_num: int
    heiferI_num: int
    heiferII_num: int
    heiferIII_num: int
    cow_num: int
    replace_num: int

    num_calves_in_data: int
    num_heiferIs_in_data: int
    num_heiferIIs_in_data: int
    num_heiferIIIs_in_data: int
    num_cows_in_data: int
    num_replacement_cows_in_data: int

    calves: List[Calf]
    heiferIs: List[HeiferI]
    heiferIIs: List[HeiferII]
    heiferIIIs: List[HeiferIII]
    cows: List[Cow]
    replacement: List[Cow]

    birth_weight_ho: float
    birth_weight_je: float

    def next_id(self):
        """
       Increment and return the next unique identifier for an animal.

       Returns:
       --------
       int
           The next unique animal_id.
       """
        self.animal_id += 1
        return self.animal_id

    def __init__(self, CI: int, herd_data: HerdInfoTypedDict, set_seed: bool, init_herd: bool = False,
                 save_animals: bool = False, terminate_simulation_post_herd_generation: bool = False) -> None:
        """
        Initialize the AnimalData instance with herd information and configurations.

        Parameters:
        -----------
        CI : int
            Calving Interval.
        herd_data : HerdInfoTypedDict
            A dictionary containing information about the herd such as breed, number of animals, etc.
        set_seed : Bool
            A boolean to determine if a random seed should be set for reproducibility of data.
        init_herd: bool
            Initialize herd with simulation.
        save_animals: bool
            User input indicating whether to save the generated animals to CSV files.
        terminate_simulation_post_herd_generation: bool
            User input indicating whether to terminate the simulation after herd generation.
        """
        self.CI = CI
        self.breed = herd_data['breed']
        self.order_by_random = not set_seed
        self.init_herd = init_herd
        self.save_animals = save_animals
        self.terminate_simulation_post_herd_generation = terminate_simulation_post_herd_generation

        self.initial_animal_num = im.get_data("animal.herd_initialization.initial_animal_num")
        self.simulation_days = im.get_data("animal.herd_initialization.simulation_days")

        self.calf_num = herd_data['calf_num']
        self.heiferI_num = herd_data['heiferI_num']
        self.heiferII_num = herd_data['heiferII_num']
        self.heiferIII_num = herd_data['heiferIII_num_springers']
        self.cow_num = herd_data['cow_num']
        self.replace_num = herd_data['replace_num']

        self.num_calves_in_data = len(im.get_data("calves")['id'])
        self.num_heiferIs_in_data = len(im.get_data("heiferIs")['id'])
        self.num_heiferIIs_in_data = len(im.get_data("heiferIIs")['id'])
        self.num_heiferIIIs_in_data = len(im.get_data("heiferIIIs")['id'])
        self.num_cows_in_data = len(im.get_data("cows")['id'])
        self.num_replacement_cows_in_data = len(im.get_data("replacement_cows")['id'])

        self.calves = []
        self.heiferIs = []
        self.heiferIIs = []
        self.heiferIIIs = []
        self.cows = []
        self.replacement = []

        self.birth_weight_ho = truncnorm.rvs(-2, 2, AnimalBase.config["birth_weight_avg_ho"],
                                             AnimalBase.config["birth_weight_std_ho"])
        self.birth_weight_je = truncnorm.rvs(-2, 2, AnimalBase.config["birth_weight_avg_je"],
                                             AnimalBase.config["birth_weight_std_je"])

        self._init_herd()

    def _init_herd(self) -> None:
        """
        Initializes animal lists by calling the respective initializer methods for each animal type.

        This private method is typically called within the constructor to populate the animal lists based
        on the numbers provided in the herd data.
        """
        if self.init_herd:
            animal_factory = AnimalFactory(breed=self.breed, CI=self.CI, initial_animal_num=self.initial_animal_num,
                                           simulation_days=self.simulation_days, initial_animal_id=self.animal_id,
                                           save_animals=self.save_animals,
                                           terminate_simulation_post_herd_generation=self.
                                           terminate_simulation_post_herd_generation)
            herd: Dict[str, List[Calf | HeiferI | HeiferII | HeiferIII | Cow]] = animal_factory.generate_animals()

            self.calves = self._random_sample_with_replacement(herd["calves"], self.calf_num)
            self.heiferIs = self._random_sample_with_replacement(herd["heiferIs"], self.heiferI_num)
            self.heiferIIs = self._random_sample_with_replacement(herd["heiferIIs"], self.heiferII_num)
            self.heiferIIIs = self._random_sample_with_replacement(herd["heiferIIIs"], self.heiferIII_num)
            self.cows = self._random_sample_with_replacement(herd["cows"], self.cow_num)
            self.replacement = self._random_sample_with_replacement(herd["replacement_cows"], self.replace_num)

        else:
            self.calves = self._init_animals("calves", self.calf_num)
            self.heiferIs = self._init_animals("heiferIs", self.heiferI_num)
            self.heiferIIs = self._init_animals("heiferIIs", self.heiferII_num)
            self.heiferIIIs = self._init_animals("heiferIIIs", self.heiferIII_num)
            self.cows = self._init_animals("cows", self.cow_num)
            self.replacement = self._init_animals("replacement_cows", self.replace_num)

    def _random_sample_with_replacement(self, all_animals: (List[Calf] | List[HeiferI] | List[HeiferII] |
                                                            List[HeiferIII] | List[Cow]), animal_num: int) -> \
            (List[Calf] | List[HeiferI] | List[HeiferII] | List[HeiferIII] | List[Cow]):
        animals = []
        random_choices = random.choices(list(range(len(all_animals))), k=animal_num)
        for choice in random_choices:
            animal = copy.deepcopy(all_animals[choice])
            animal.id = self.next_id()
            animals.append(animal)

        return animals

    @staticmethod
    def _sample_animal_data_with_replacement(all_animal_data: Dict[str, List[Any]], animal_num: int) -> Dict[str,
                                                                                                             List[Any]]:
        random_choices = random.choices(list(range(len(all_animal_data['id']))), k=animal_num)
        animal_data = {}
        for key in all_animal_data.keys():
            data = []
            for choice in random_choices:
                data.append(all_animal_data[key][choice])
            animal_data[key] = data
        return animal_data

    def _get_args_list(self, data: Dict[str, List[Any]], args_properties: List[str], num: int) -> \
            List[Dict[str, Any]]:
        """
        Generates a list of dictionaries with animal properties and their respective values for initializing animal
        instances.

        This method is used to prepare arguments for initializing animal instances. It processes the input
        data, and handle special cases for 'p_init' and 'events'.

        Parameters:
        ----------
        data : Dict[str, List[Any]]
            The dictionary containing lists of data properties.
        args_properties : List[str]
            The list of properties that are required to initialize an animal.
        num : int
            The number of animals to initialize.

        Returns:
        --------
        List[Dict[str, Any]]
            A list of dictionaries where each dictionary contains the initialization properties for an animal.
        """

        args_list = []
        for i in range(num):
            args = {}
            for arg in args_properties:
                if arg == 'id':
                    args['id'] = self.next_id()
                elif arg == 'p_init':
                    args['p_init'] = 0
                elif arg == 'events' and data['events'][i].lower() == 'no events':
                    args['events'] = ''
                else:
                    args[arg] = data[arg][i]
            args_list.append(args)
        return args_list

    def _init_animals(self, animal_type: str, num_animal: int) -> (List[Calf] | List[HeiferI] | List[HeiferII] |
                                                                   List[HeiferIII] | List[Cow]):
        animals: (List[Calf] | List[HeiferI] | List[HeiferII] | List[HeiferIII] | List[Cow]) = []
        all_animal_data: Dict[str, List[Any]] = im.get_data(animal_type)
        animal_data = self._sample_animal_data_with_replacement(all_animal_data=all_animal_data,
                                                                animal_num=num_animal)
        args_properties: Dict[str, List[str]] = {
            "calves": ['id', 'breed', 'birth_date', 'days_born', 'p_init', 'birth_weight', 'body_weight', 'wean_weight',
                       'mature_body_weight', 'events'],
            "heiferIs": ['id', 'breed', 'birth_date', 'days_born', 'birth_weight', 'body_weight', 'wean_weight',
                         'mature_body_weight', 'events'],
            "heiferIIs": ['id', 'breed', 'birth_date', 'days_born', 'birth_weight', 'body_weight', 'wean_weight',
                          'mature_body_weight', 'events', 'repro_program', 'tai_method_h', 'synch_ed_method_h',
                          'estrus_count', 'estrus_day', 'tai_program_start_day_h', 'synch_ed_program_start_day_h',
                          'synch_ed_estrus_day', 'synch_ed_stop_day', 'conception_rate', 'ai_day', 'abortion_day',
                          'days_in_preg', 'gestation_length', 'p_gest_for_calf', 'calf_birth_weight'],
            "heiferIIIs": ['id', 'breed', 'birth_date', 'days_born', 'birth_weight', 'body_weight', 'wean_weight',
                           'mature_body_weight', 'events', 'repro_program', 'tai_method_h', 'synch_ed_method_h',
                           'estrus_count', 'estrus_day', 'tai_program_start_day_h', 'synch_ed_program_start_day_h',
                           'synch_ed_estrus_day', 'synch_ed_stop_day', 'conception_rate', 'ai_day', 'abortion_day',
                           'days_in_preg', 'gestation_length', 'p_gest_for_calf', 'calf_birth_weight'],
            "cows": ['id', 'breed', 'birth_date', 'days_born', 'birth_weight', 'body_weight', 'wean_weight',
                     'mature_body_weight', 'events', 'repro_program', 'tai_method_h', 'synch_ed_method_h',
                     'estrus_count', 'estrus_day', 'tai_program_start_day_h', 'synch_ed_program_start_day_h',
                     'synch_ed_estrus_day', 'synch_ed_stop_day', 'conception_rate', 'ai_day', 'abortion_day',
                     'days_in_preg', 'gestation_length', 'p_gest_for_calf', 'calf_birth_weight',
                     'presynch_method', 'tai_method_c', 'resynch_method', 'days_in_milk', 'parity',
                     'calving_interval'],
            "replacement_cows": ['id', 'breed', 'birth_date', 'days_born', 'birth_weight', 'body_weight', 'wean_weight',
                                 'mature_body_weight', 'events', 'repro_program', 'tai_method_h', 'synch_ed_method_h',
                                 'estrus_count', 'estrus_day', 'tai_program_start_day_h',
                                 'synch_ed_program_start_day_h', 'synch_ed_estrus_day', 'synch_ed_stop_day',
                                 'conception_rate', 'ai_day', 'abortion_day', 'days_in_preg', 'gestation_length',
                                 'p_gest_for_calf', 'calf_birth_weight', 'presynch_method', 'tai_method_c',
                                 'resynch_method'],
        }
        args_list = self._get_args_list(animal_data, args_properties[animal_type], num_animal)

        ANIMAL_CLASSES: Dict[str, Type] = {
            "calves": Calf,
            "heiferIs": HeiferI,
            "heiferIIs": HeiferII,
            "heiferIIIs": HeiferIII,
            "cows": Cow,
            "replacement_cows": Cow,
        }
        animal_class = ANIMAL_CLASSES[animal_type]
        for args in args_list:
            animal = animal_class(args)
            animals.append(animal)
        return animals

    def get_calves(self):
        """
        Retrieve a list of Calf instances up to the specified number and breed.

        Initializes Calf instances through a separate initialization method if the current count is insufficient and
        optionally shuffles the list if `order_by_random` is set to True.

        Returns:
        --------
        List[Calf]
            A list of Calf instances.
        """
        if self.order_by_random:
            shuffle(self.calves)
        return self.calves

    def get_heiferIs(self):
        """
        Retrieve a list of HeiferI instances up to the specified number and breed.

        Initializes HeiferI instances through a separate initialization method if the current count is insufficient and
        optionally shuffles the list if `order_by_random` is set to True.

        Returns:
        --------
        List[HeiferI]
            A list of HeiferI instances.
        """
        if self.order_by_random:
            shuffle(self.heiferIs)

        return self.heiferIs

    def get_heiferIIs(self):
        """
        Retrieve a list of HeiferII instances up to the specified number and breed.

        Initializes HeiferII instances through a separate initialization method if the current count is insufficient and
        optionally shuffles the list if `order_by_random` is set to True.

        Returns:
        --------
        List[HeiferII]
            A list of HeiferII instances.
        """
        if self.order_by_random:
            shuffle(self.heiferIIs)

        return self.heiferIIs

    def get_heiferIIIs(self):
        """
        Retrieve a list of HeiferIII instances up to the specified number and breed.

        Initializes HeiferIII instances through a separate initialization method if the current count is insufficient
        and optionally shuffles the list if `order_by_random` is set to True.

        Returns:
        --------
        List[HeiferIII]
            A list of HeiferIII instances.
        """
        if self.order_by_random:
            shuffle(self.heiferIIIs)
        return self.heiferIIIs

    def get_cows(self):
        """
        Retrieve a list of Cow instances up to the specified number and breed.

        Initializes Cow instances through a separate initialization method if the current count is insufficient and
        optionally shuffles the list if `order_by_random` is set to True.

        Returns:
        --------
        List[Cow]
            A list of Cow instances.
        """
        if self.order_by_random:
            shuffle(self.cows)
        return self.cows

    def get_replacement_cows(self):
        """
        Retrieve a list of replacement Cow instances up to the specified number and breed.

        Initializes replacement cows through a separate initialization method if the current count is insufficient and
        optionally shuffles the list if `order_by_random` is set to True.

        Returns:
        --------
        List[Cow]
            A list of replacement Cow instances.
        """
        if self.order_by_random:
            shuffle(self.replacement)
        return self.replacement

    def initialization_db_summary(self) -> Dict[str, int | float]:
        """
        Returns:
        --------
        Dict[str, int | float]
            A dictionary which stores the summary of the initialization
        """
        num_calf = len(self.calves)
        num_heiferI = len(self.heiferIs)
        num_heiferII = len(self.heiferIIs)
        num_heiferIII = len(self.heiferIIIs)
        num_cow = len(self.cows)
        num_replacement = len(self.replacement)

        avg_calf_age = sum(calf.days_born for calf in self.calves) / num_calf if num_calf else 0
        avg_heiferI_age = sum(heiferI.days_born for heiferI in self.heiferIs) / num_heiferI if num_heiferI else 0
        avg_heiferII_age = sum(heiferII.days_born for heiferII in self.heiferIIs) / num_heiferII if num_heiferII else 0
        avg_heiferIII_age = sum(heiferIII.days_born for heiferIII in self.heiferIIIs) / num_heiferIII if num_heiferIII \
            else 0
        avg_cow_age = sum(cow.days_born for cow in self.cows) / num_cow if num_cow else 0
        avg_replacement_age = sum(replacement.days_born for replacement in self.replacement) / num_replacement if \
            num_replacement else 0

        cow_avg_days_in_preg = sum(cow.days_in_preg for cow in self.cows) / num_cow if num_cow else 0
        cow_avg_days_in_milk = sum(cow.days_in_milk for cow in self.cows) / num_cow if num_cow else 0
        cow_avg_parity = sum(cow.calves for cow in self.cows) / num_cow if num_cow else 0
        cow_avg_CI = sum(cow.CI for cow in self.cows) / num_cow if num_cow else 0

        summary = {
            'num_calf': num_calf,
            'num_heiferI': num_heiferI,
            'num_heiferII': num_heiferII,
            'num_heiferIII': num_heiferIII,
            'num_cow': num_cow,
            'num_replacement': num_replacement,

            'avg_calf_age': avg_calf_age,
            'avg_heiferI_age': avg_heiferI_age,
            'avg_heiferII_age': avg_heiferII_age,
            'avg_heiferIII_age': avg_heiferIII_age,
            'avg_cow_age': avg_cow_age,
            'avg_replacement_age': avg_replacement_age,

            'cow_avg_days_in_preg': cow_avg_days_in_preg,
            'cow_avg_days_in_milk': cow_avg_days_in_milk,
            'cow_avg_parity': cow_avg_parity,
            'cow_avg_CI': cow_avg_CI
        }
        return summary
