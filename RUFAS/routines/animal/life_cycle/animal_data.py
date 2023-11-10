from dataclasses import dataclass
from random import shuffle
from typing import List, Dict, Any

from scipy.stats import truncnorm

from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.animal_typed_dicts import HerdInfoTypedDict
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
        CI: float
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

        _init_calves(num: int, breed: str) -> None
            Initialize calves up to the specified number and breed.

        _init_calves_from_simulation(num: int, breed: str, sim_days=5000) -> List[Calf]
            Simulate and initialize Calf instances.

        _init_calves_from_data(num: int) -> List[Calf]
            Initialize Calf instances from existing data.

        _init_heiferIs(num: int, breed: str) -> None
            Initialize HeiferIs up to the specified number and breed.

        _init_heiferIs_from_simulation(num: int, breed: str, sim_days=5000) -> List[HeiferI]
            Simulate and initialize HeiferI instances.

        _init_heiferIs_from_data(num: int) -> List[HeiferI]
            Initialize HeiferI instances from existing data.

        _init_heiferIIs(num: int, breed: str) -> None
            Initialize HeiferIIs up to the specified number and breed.

        _init_heiferIIs_from_simulation(num: int, breed: str, sim_days=5000) -> List[HeiferII]
            Simulate and initialize HeiferII instances.

        _init_heiferIIs_from_data(num: int) -> List[HeiferII]
            Initialize HeiferII instances from existing data.

        _init_heiferIIIs(num: int, breed: str) -> None
            Initialize HeiferIIIs up to the specified number and breed.

        _init_heiferIIIs_from_simulation(num: int, breed: str, sim_days=5000) -> List[HeiferIII]
            Simulate and initialize HeiferIII instances.

        _init_heiferIIIs_from_data(num: int) -> List[HeiferIII]
            Initialize HeiferIII instances from existing data.

        _init_cows(num: int, breed: str) -> None
            Initialize cows up to the specified number and breed.

        _init_cows_from_simulation(num: int, breed: str, sim_days=5000) -> List[Cow]
            Simulate and initialize Cow instances.

        _init_cows_from_data(num: int) -> List[Cow]
            Initialize Cow instances from existing data.

        _init_replacement_cows(num: int, breed: str) -> None
            Initialize replacement cows up to the specified number and breed.

        _init_replacement_cows_from_simulation(num: int, breed: str, sim_days=5000) -> List[Cow]
            Simulate and initialize replacement Cow instances.

        _init_replacement_cows_from_data(num: int) -> List[Cow]
            Initialize replacement Cow instances from existing data.

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
    animal_id = 378165

    CI: float
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

    def __init__(self, CI: float, herd_data: HerdInfoTypedDict, set_seed: bool, init_herd: bool = False,
                 save_animals: bool = False, terminate_simulation_post_herd_generation: bool = False) -> None:
        """
        Initialize the AnimalData instance with herd information and configurations.

        Parameters:
        -----------
        CI : float
            Calving Interval.
        herd_data : HerdInfoTypedDict
            A dictionary containing information about the herd such as breed, number of animals, etc.
        set_seed : Bool
            A boolean to determine if a random seed should be set for reproducibility of data.
        init_herd: bool
            Initialize herd with simulation.
        save_animals: bool
            Save animals to CSV files.
        terminate_simulation_post_herd_generation: bool
            Save generated animals to CSV files.
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

        self._init_animals()

    def _init_animals(self) -> None:
        """
        Initializes animal lists by calling the respective initializer methods for each animal type.

        This private method is typically called within the constructor to populate the animal lists based
        on the numbers provided in the herd data.
        """
        self._init_calves(self.calf_num, self.breed)
        self._init_heiferIs(self.heiferI_num, self.breed)
        self._init_heiferIIs(self.heiferII_num, self.breed)
        self._init_heiferIIIs(self.heiferIII_num, self.breed)
        self._init_cows(self.cow_num, self.breed)
        self._init_replacement_cows(self.replace_num, self.breed)

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
                if arg == 'p_init':
                    args['p_init'] = 0
                    continue
                elif arg == 'events' and data['events'][i].lower() == 'no events':
                    args['events'] = ''
                    continue
                args[arg] = data[arg][i]
            args_list.append(args)
        return args_list

    def _init_calves(self, num: int, breed: str) -> None:
        """
        Initializes the list of calves either from simulation data or existing data up to the required number.

        If the existing number of calves is less than the required number, this method either adds more calves
        from the simulation or the existing data based on the initialization settings.

        Parameters:
        ----------
        num : int
            The number of calves required.
        breed : str
            The breed of the calves to be initialized.
        """

        current_num_calves = len(self.calves)

        if current_num_calves >= num:
            return

        if self.init_herd:
            self.calves += self._init_calves_from_simulation(num - current_num_calves, breed)

        else:
            if current_num_calves + self.num_calves_in_data < num:
                self.calves += self._init_calves_from_data(self.num_calves_in_data)
                self.calves += self._init_calves_from_simulation(num - current_num_calves - self.num_calves_in_data,
                                                                 breed)
            else:
                self.calves += self._init_calves_from_data(num - current_num_calves)

    def _init_calves_from_simulation(self, num: int, breed: str) -> List[Calf]:
        """
        Initializes a list of Calf instances based on simulation data.

        It generates calves with default values and assigns birth weights based on the breed. Each calf
        is assigned a unique ID through the `next_id` method. Only calves that are not culled or sold
        are added to the list.

        Parameters:
        ----------
        num : int
            The number of calf instances to generate.
        breed : str
            The breed type for the calves.

        Returns:
        --------
        List[Calf]
            A list containing the initialized Calf instances.
        """
        calves: List[Calf] = []
        while len(calves) < num:
            args = {
                'id': self.next_id(),
                'breed': breed,
                'birth_date': 0,
                'days_born': 0,
                'p_init': 0,
                'birth_weight': self.birth_weight_ho if breed == 'HO' else self.birth_weight_je
            }
            calf = Calf(args)
            if not (calf.culled or calf.sold):
                calves.append(calf)

        return calves

    def _init_calves_from_data(self, num: int) -> List[Calf]:
        """
        Initializes a list of Calf instances based on existing data.

        The existing data is accessed through the `im.get_data` method and processed to initialize
        Calf instances. Each calf's arguments are prepared and used to instantiate Calf objects which are
        then added to the list of calves.

        Parameters:
        ----------
        num : int
            The number of calf instances to initialize from the data.

        Returns:
        --------
        List[Calf]
            A list containing the initialized Calf instances from the existing data.
        """
        calves: List[Calf] = []
        calves_data = im.get_data("calves")
        args_properties = ['id', 'breed', 'birth_date', 'days_born', 'p_init', 'birth_weight', 'body_weight',
                           'wean_weight', 'mature_body_weight', 'events']
        args_list = self._get_args_list(calves_data, args_properties, num)
        for args in args_list:
            calf = Calf(args)
            calves.append(calf)

        return calves

    def _init_heiferIs(self, num: int, breed: str) -> None:
        """
        Initialize the list of HeiferI instances up to the specified number, based on either simulation data or
        existing data, depending on the `init_herd` flag.

        If the current number of HeiferI instances is less than the required number (`num`), new instances are
        created through simulation or loaded from existing data to meet the required count.

        Parameters:
        ----------
        num : int
            The desired number of HeiferI instances to be available.
        breed : str
            The breed type for the HeiferI instances.

        Returns:
        --------
        None
        """
        current_num_heiferIs = len(self.heiferIs)

        if current_num_heiferIs >= num:
            return

        if self.init_herd:
            self.heiferIs += self._init_heiferIs_from_simulation(num - current_num_heiferIs, breed)

        else:
            if current_num_heiferIs + self.num_heiferIs_in_data < num:
                self.heiferIs += self._init_heiferIs_from_data(self.num_heiferIs_in_data)
                self.heiferIs += self._init_heiferIs_from_simulation(
                    num - current_num_heiferIs - self.num_heiferIs_in_data, breed)
            else:
                self.heiferIs += self._init_heiferIs_from_data(num - current_num_heiferIs)

    def _init_heiferIs_from_simulation(self, num: int, breed: str, sim_days=5000) -> List[HeiferI]:
        """
        Simulate and initialize a list of HeiferI instances.

        This method first creates calf instances via simulation and then simulates them for a given number of days
        until they become heifers. New HeiferI instances are initialized with the updated values from calves
        and added to the list.

        Parameters:
        ----------
        num : int
            The number of HeiferI instances to generate via simulation.
        breed : str
            The breed type for the HeiferI instances.
        sim_days : int, optional
            The number of days to simulate the calves' development into heifers (default is 5000).

        Returns:
        --------
        List[HeiferI]
            A list of simulated HeiferI instances.
        """
        heiferIs: List[HeiferI] = []
        calves = self._init_calves_from_simulation(num, breed)

        for day in range(sim_days):
            for calf in calves:
                wean_day = calf.update(0)
                if wean_day:
                    args = calf.get_calf_values()
                    args.update(id=self.next_id())

                    heiferI = HeiferI(args)
                    heiferIs.append(heiferI)
                    calves.remove(calf)
                    if len(heiferIs) == num:
                        break
            if len(heiferIs) == num:
                break

        return heiferIs

    def _init_heiferIs_from_data(self, num: int) -> List[HeiferI]:
        """
        Initialize a list of HeiferI instances from existing data.

        This method retrieves data for the specified number of HeiferI instances and creates a list of HeiferI
        objects from this data.

        Parameters:
        ----------
        num : int
            The number of HeiferI instances to initialize from the data.

        Returns:
        --------
        List[HeiferI]
            A list containing the initialized HeiferI instances from the existing data.
        """
        heiferIs: List[HeiferI] = []
        heiferI_data = im.get_data("heiferIs")
        args_properties = ['id', 'breed', 'birth_date', 'days_born', 'birth_weight', 'body_weight', 'wean_weight',
                           'mature_body_weight', 'events']
        args_list = self._get_args_list(heiferI_data, args_properties, num)
        for args in args_list:
            heiferI = HeiferI(args)
            heiferIs.append(heiferI)

        return heiferIs

    def _init_heiferIIs(self, num: int, breed: str) -> None:
        """
        Initialize the list of HeiferII instances up to the specified number, based on either simulation data or
        existing data, depending on the `init_herd` flag.

        If the current number of HeiferII instances is less than the required number (`num`), new instances are
        created through simulation or loaded from existing data to meet the required count.

        Parameters:
        ----------
        num : int
            The desired number of HeiferII instances to be available.
        breed : str
            The breed type for the HeiferII instances.

        Returns:
        --------
        None
        """
        current_num_heiferIIs = len(self.heiferIIs)

        if current_num_heiferIIs >= num:
            return

        if self.init_herd:
            self.heiferIIs += self._init_heiferIIs_from_simulation(num - current_num_heiferIIs, breed)

        else:
            if current_num_heiferIIs + self.num_heiferIIs_in_data < num:
                self.heiferIIs += self._init_heiferIIs_from_data(self.num_heiferIIs_in_data)
                self.heiferIIs += self._init_heiferIIs_from_simulation(
                    num - current_num_heiferIIs - self.num_heiferIIs_in_data, breed)
            else:
                self.heiferIIs += self._init_heiferIIs_from_data(num - current_num_heiferIIs)

    def _init_heiferIIs_from_simulation(self, num: int, breed: str, sim_days=5000) -> List[HeiferII]:
        """
        Simulate and initialize a list of HeiferII instances.

        This method first simulates HeiferI instances transitioning into the second stage of development and then
        creates HeiferII instances. The simulation continues for a specified number of days, or until the desired number
        of HeiferII instances is reached.

        Parameters:
        ----------
        num : int
            The number of HeiferII instances to generate via simulation.
        breed : str
            The breed type for the HeiferII instances.
        sim_days : int, optional
            The number of days to simulate the HeiferIs' development into HeiferIIs (default is 5000).

        Returns:
        --------
        List[HeiferII]
            A list of simulated HeiferII instances.
        """
        heiferIIs: List[HeiferII] = []
        heiferIs = self._init_heiferIs_from_simulation(num, breed)

        for day in range(sim_days):
            for heiferI in heiferIs:
                second_stage = heiferI.update(0)
                if second_stage:
                    args = heiferI.get_heiferI_values()

                    args.update(id=self.next_id())
                    args.update(repro_program=AnimalBase.config['heifer_repro_method'])
                    args.update(tai_method_h=AnimalBase.config['heifer_repro_programs']['heifer_TAI_protocol'])
                    args.update(synch_ed_method_h=AnimalBase.config['heifer_repro_programs']['heifer_synchED_protocol'])

                    heiferII = HeiferII(args)
                    heiferIIs.append(heiferII)
                    heiferIs.remove(heiferI)
                    if len(heiferIIs) == num:
                        break
                if len(heiferIIs) == num:
                    break

        return heiferIIs

    def _init_heiferIIs_from_data(self, num: int) -> List[HeiferII]:
        """
        Initialize a list of HeiferII instances from existing data.

        This method retrieves data for the specified number of HeiferII instances and creates a list of HeiferII
        objects from this data.

        Parameters:
        ----------
        num : int
            The number of HeiferII instances to initialize from the data.

        Returns:
        --------
        List[HeiferII]
            A list containing the initialized HeiferII instances from the existing data.
        """
        heiferIIs: List[HeiferII] = []
        heiferII_data = im.get_data("heiferIIs")
        args_properties = ['id', 'breed', 'birth_date', 'days_born', 'birth_weight', 'body_weight', 'wean_weight',
                           'mature_body_weight', 'events', 'repro_program', 'tai_method_h', 'synch_ed_method_h',
                           'estrus_count', 'estrus_day', 'tai_program_start_day_h', 'synch_ed_program_start_day_h',
                           'synch_ed_estrus_day', 'synch_ed_stop_day', 'conception_rate', 'ai_day', 'abortion_day',
                           'days_in_preg', 'gestation_length', 'p_gest_for_calf', 'calf_birth_weight']
        args_list = self._get_args_list(heiferII_data, args_properties, num)
        for args in args_list:
            heiferII = HeiferII(args)
            heiferIIs.append(heiferII)

        return heiferIIs

    def _init_heiferIIIs(self, num: int, breed: str) -> None:
        """
        Initialize the list of HeiferIII instances up to the specified number, based on either simulation data or
        existing data, depending on the `init_herd` flag.

        If the current number of HeiferIII instances is less than the required number (`num`), new instances are
        created through simulation or loaded from existing data to meet the required count.

        Parameters:
        ----------
        num : int
            The desired number of HeiferIII instances to be available.
        breed : str
            The breed type for the HeiferIII instances.

        Returns:
        --------
        None
        """
        current_num_heiferIIIs = len(self.heiferIIIs)

        if current_num_heiferIIIs >= num:
            return

        if self.init_herd:
            self.heiferIIIs += self._init_heiferIIIs_from_simulation(num - current_num_heiferIIIs, breed)

        else:
            if current_num_heiferIIIs + self.num_heiferIIIs_in_data < num:
                self.heiferIIIs += self._init_heiferIIIs_from_data(self.num_heiferIIIs_in_data)
                self.heiferIIIs += self._init_heiferIIIs_from_simulation(
                    num - current_num_heiferIIIs - self.num_heiferIIIs_in_data, breed)
            else:
                self.heiferIIIs += self._init_heiferIIIs_from_data(num - current_num_heiferIIIs)

    def _init_heiferIIIs_from_simulation(self, num: int, breed: str, sim_days=5000) -> List[HeiferIII]:
        """
        Simulate and initialize a list of HeiferIII instances.

        This method first simulates HeiferII instances transitioning into the third stage of development and then
        creates HeiferIII instances. The simulation continues for a specified number of days, or until the desired
        number of HeiferIII instances is reached.

        Parameters:
        ----------
        num : int
            The number of HeiferIII instances to generate via simulation.
        breed : str
            The breed type for the HeiferIII instances.
        sim_days : int, optional
            The number of days to simulate the HeiferIIs' development into HeiferIIIs (default is 5000).

        Returns:
        --------
        List[HeiferIII]
            A list of simulated HeiferIII instances.
        """
        heiferIIIs: List[HeiferIII] = []
        heiferIIs = self._init_heiferIIs_from_simulation(num, breed)

        for day in range(sim_days):
            for heiferII in heiferIIs:
                cull_stage, third_stage = heiferII.update(0)
                if cull_stage:
                    heiferIIs.remove(heiferII)
                if third_stage:
                    args = heiferII.get_heiferII_values()
                    args.update(id=self.next_id())

                    heiferIII = HeiferIII(args)
                    heiferIIIs.append(heiferIII)
                    heiferIIs.remove(heiferII)
                    if len(heiferIIIs) == num:
                        break
                if len(heiferIIIs) == num:
                    break

        return heiferIIIs

    def _init_heiferIIIs_from_data(self, num: int) -> List[HeiferIII]:
        """
        Initialize a list of HeiferIII instances from existing data.

        This method retrieves data for the specified number of HeiferIII instances and creates a list of HeiferIII
        objects from this data.

        Parameters:
        ----------
        num : int
            The number of HeiferIII instances to initialize from the data.

        Returns:
        --------
        List[HeiferIII]
            A list containing the initialized HeiferIII instances from the existing data.
        """
        heiferIIIs: List[HeiferIII] = []
        heiferIII_data = im.get_data("heiferIIIs")
        args_properties = ['id', 'breed', 'birth_date', 'days_born', 'birth_weight', 'body_weight', 'wean_weight',
                           'mature_body_weight', 'events', 'repro_program', 'tai_method_h', 'synch_ed_method_h',
                           'estrus_count', 'estrus_day', 'tai_program_start_day_h', 'synch_ed_program_start_day_h',
                           'synch_ed_estrus_day', 'synch_ed_stop_day', 'conception_rate', 'ai_day', 'abortion_day',
                           'days_in_preg', 'gestation_length', 'p_gest_for_calf', 'calf_birth_weight']
        args_list = self._get_args_list(heiferIII_data, args_properties, num)
        for args in args_list:
            heiferIII = HeiferIII(args)
            heiferIIIs.append(heiferIII)

        return heiferIIIs

    def _init_cows(self, num: int, breed: str) -> None:
        """
        Initialize the list of Cow instances up to the specified number, based on either simulation data or
        existing data, depending on the `init_herd` flag.

        If the current number of Cow instances is less than the required number (`num`), new instances are
        created through simulation or loaded from existing data to meet the required count.

        Parameters:
        ----------
        num : int
            The desired number of Cow instances to be available.
        breed : str
            The breed type for the Cow instances.

        Returns:
        --------
        None
        """
        current_num_cows = len(self.cows)

        if current_num_cows >= num:
            return

        if self.init_herd:
            self.cows += self._init_cows_from_simulation(num - current_num_cows, breed)

        else:
            if current_num_cows + self.num_cows_in_data < num:
                self.cows += self._init_cows_from_data(self.num_cows_in_data)
                self.cows += self._init_cows_from_simulation(num - current_num_cows - self.num_cows_in_data, breed)
            else:
                self.cows += self._init_cows_from_data(num - current_num_cows)

    def _init_cows_from_simulation(self, num: int, breed: str, sim_days=5000) -> List[Cow]:
        """
        Simulate and initialize a list of Cow instances.

        This method first simulates HeiferIII instances transitioning into the fourth stage of development and then
        creates Cow instances. The simulation continues for a specified number of days, or until the desired number of
        Cow instances is reached.

        Parameters:
        ----------
        num : int
            The number of Cow instances to generate via simulation.
        breed : str
            The breed type for the Cow instances.
        sim_days : int, optional
            The number of days to simulate the Cows' development into HeiferIIIs (default is 5000).

        Returns:
        --------
        List[Cow]
            A list of simulated Cow instances.
        """
        cows: List[Cow] = []
        heiferIIIs = self._init_heiferIIIs_from_simulation(num, breed)

        for day in range(sim_days):
            for heiferIII in heiferIIIs:
                cow_stage = heiferIII.update(0)
                if cow_stage:
                    args = heiferIII.get_heiferIII_values()

                    args.update(id=self.next_id())
                    args.update(repro_program='TAI')
                    args.update(presynch_method='PreSynch')
                    args.update(tai_method_c='OvSynch 56')
                    args.update(resynch_method='TAIafterPD')

                    cow = Cow(args)
                    cows.append(cow)
                    heiferIIIs.remove(heiferIII)
                    if len(cows) == num:
                        break
                if len(cows) == num:
                    break

        return cows

    def _init_cows_from_data(self, num: int) -> List[Cow]:
        """
        Initialize a list of Cow instances from existing data.

        This method retrieves data for the specified number of Cow instances and creates a list of Cow objects from this
        data.

        Parameters:
        ----------
        num : int
            The number of Cow instances to initialize from the data.

        Returns:
        --------
        List[Cow]
            A list containing the initialized Cow instances from the existing data.
        """
        cows: List[Cow] = []
        cow_data = im.get_data("cows")
        args_properties = ['id', 'breed', 'birth_date', 'days_born', 'birth_weight', 'body_weight', 'wean_weight',
                           'mature_body_weight', 'events', 'repro_program', 'tai_method_h', 'synch_ed_method_h',
                           'estrus_count', 'estrus_day', 'tai_program_start_day_h', 'synch_ed_program_start_day_h',
                           'synch_ed_estrus_day', 'synch_ed_stop_day', 'conception_rate', 'ai_day', 'abortion_day',
                           'days_in_preg', 'gestation_length', 'p_gest_for_calf', 'calf_birth_weight',
                           'presynch_method', 'tai_method_c', 'resynch_method', 'days_in_milk', 'parity',
                           'calving_interval']
        args_list = self._get_args_list(cow_data, args_properties, num)
        for args in args_list:
            cow = Cow(args)
            cows.append(cow)

        return cows

    def _init_replacement_cows(self, num: int, breed: str) -> None:
        """
        Initialize the list of replacement Cow instances up to the specified number, based on either simulation data or
        existing data, depending on the `init_herd` flag.

        If the current number of replacement Cow instances is less than the required number (`num`), new instances are
        created through simulation or loaded from existing data to meet the required count.

        Parameters:
        ----------
        num : int
            The desired number of replacement Cow instances to be available.
        breed : str
            The breed type for the replacement Cow instances.

        Returns:
        --------
        None
        """
        current_num_replacement_cows = len(self.replacement)

        if current_num_replacement_cows >= num:
            return

        if self.init_herd:
            self.replacement += self._init_replacement_cows_from_simulation(num - current_num_replacement_cows, breed)

        else:
            if current_num_replacement_cows + self.num_replacement_cows_in_data < num:
                self.replacement += self._init_replacement_cows_from_data(self.num_replacement_cows_in_data)
                self.replacement += self._init_replacement_cows_from_simulation(num - current_num_replacement_cows -
                                                                                self.num_replacement_cows_in_data,
                                                                                breed)
            else:
                self.replacement += self._init_replacement_cows_from_data(num - current_num_replacement_cows)

    def _init_replacement_cows_from_simulation(self, num: int, breed: str, sim_days=5000) -> List[Cow]:
        """
        Simulate and initialize a list of replacement Cow instances.

        This method simulates the process of HeiferIII instances transitioning into the replacement Cow stage and then
        creates Cow instances accordingly. The simulation runs for a set number of days or until the required number
        of replacement Cow instances is reached, whichever comes first.

        Parameters:
        ----------
        num : int
            The number of replacement Cow instances to generate via simulation.
        breed : str
            The breed type for the replacement Cow instances.
        sim_days : int, optional
            The number of days to simulate the replacement Cows' development (default is 5000).

        Returns:
        --------
        List[Cow]
            A list of simulated replacement Cow instances.
        """
        replacement_cows: List[Cow] = []
        heiferIIIs = self.get_heiferIIIs(num, breed)

        for day in range(sim_days):
            for heiferIII in heiferIIIs:
                cow_stage = heiferIII.update(0)
                if cow_stage:
                    args = heiferIII.get_heiferIII_values()

                    args.update(id=self.next_id())
                    args.update(repro_program='TAI')
                    args.update(presynch_method='PreSynch')
                    args.update(tai_method_c='OvSynch 56')
                    args.update(resynch_method='TAIafterPD')

                    replacement_cow = Cow(args)
                    replacement_cows.append(replacement_cow)
                    heiferIIIs.remove(heiferIII)
                    if len(replacement_cows) == num:
                        break
                if len(replacement_cows) == num:
                    break

        return replacement_cows

    def _init_replacement_cows_from_data(self, num: int) -> List[Cow]:
        """
        Initialize a list of replacement Cow instances from existing data.

        This method accesses stored data for the specified number of replacement Cow instances and creates a list of Cow
        objects from that data. The method ensures that the actual number of instances matches the desired count (`num`)

        Parameters:
        ----------
        num : int
            The number of replacement Cow instances to initialize from the data.

        Returns:
        --------
        List[Cow]
            A list containing the initialized replacement Cow instances from existing data.
        """
        replacement_cows: List[Cow] = []
        replacement_data = im.get_data("replacement_cows")
        args_properties = ['id', 'breed', 'birth_date', 'days_born', 'birth_weight', 'body_weight', 'wean_weight',
                           'mature_body_weight', 'events', 'repro_program', 'tai_method_h', 'synch_ed_method_h',
                           'estrus_count', 'estrus_day', 'tai_program_start_day_h', 'synch_ed_program_start_day_h',
                           'synch_ed_estrus_day', 'synch_ed_stop_day', 'conception_rate', 'ai_day', 'abortion_day',
                           'days_in_preg', 'gestation_length', 'p_gest_for_calf', 'calf_birth_weight',
                           'presynch_method', 'tai_method_c', 'resynch_method']
        args_list = self._get_args_list(replacement_data, args_properties, num)
        for args in args_list:
            replacement_cow = Cow(args)
            replacement_cows.append(replacement_cow)

        return replacement_cows

    def get_calves(self, num, breed):
        """
        Retrieve a list of Calf instances up to the specified number and breed.

        Initializes Calf instances through a separate initialization method if the current count is insufficient and
        optionally shuffles the list if `order_by_random` is set to True.

        Parameters:
        ----------
        num : int
            The number of Calf instances desired.
        breed : str
            The breed type for the Calf instances.

        Returns:
        --------
        List[Calf]
            A list of Calf instances.
        """
        self._init_calves(num, breed)
        if self.order_by_random:
            shuffle(self.calves)
        return self.calves

    def get_heiferIs(self, num, breed):
        """
        Retrieve a list of HeiferI instances up to the specified number and breed.

        Initializes HeiferI instances through a separate initialization method if the current count is insufficient and
        optionally shuffles the list if `order_by_random` is set to True.

        Parameters:
        ----------
        num : int
            The number of HeiferI instances desired.
        breed : str
            The breed type for the HeiferI instances.

        Returns:
        --------
        List[HeiferI]
            A list of HeiferI instances.
        """
        self._init_heiferIs(num, breed)

        if self.order_by_random:
            shuffle(self.heiferIs)

        return self.heiferIs

    def get_heiferIIs(self, num, breed):
        """
        Retrieve a list of HeiferII instances up to the specified number and breed.

        Initializes HeiferII instances through a separate initialization method if the current count is insufficient and
        optionally shuffles the list if `order_by_random` is set to True.

        Parameters:
        ----------
        num : int
            The number of HeiferII instances desired.
        breed : str
            The breed type for the HeiferII instances.

        Returns:
        --------
        List[HeiferII]
            A list of HeiferII instances.
        """
        self._init_heiferIIs(num, breed)

        if self.order_by_random:
            shuffle(self.heiferIIs)

        return self.heiferIIs

    def get_heiferIIIs(self, num, breed):
        """
        Retrieve a list of HeiferIII instances up to the specified number and breed.

        Initializes HeiferIII instances through a separate initialization method if the current count is insufficient
        and optionally shuffles the list if `order_by_random` is set to True.

        Parameters:
        ----------
        num : int
            The number of HeiferIII instances desired.
        breed : str
            The breed type for the HeiferIII instances.

        Returns:
        --------
        List[HeiferIII]
            A list of HeiferIII instances.
        """
        self._init_heiferIIIs(num, breed)

        if self.order_by_random:
            shuffle(self.heiferIIIs)
        return self.heiferIIIs

    def get_cows(self, num, breed):
        """
        Retrieve a list of Cow instances up to the specified number and breed.

        Initializes Cow instances through a separate initialization method if the current count is insufficient and
        optionally shuffles the list if `order_by_random` is set to True.

        Parameters:
        ----------
        num : int
            The number of Cow instances desired.
        breed : str
            The breed type for the Cow instances.

        Returns:
        --------
        List[Cow]
            A list of Cow instances.
        """
        self._init_cows(num, breed)

        if self.order_by_random:
            shuffle(self.cows)
        return self.cows

    def get_replacement_cows(self, num, breed):
        """
        Retrieve a list of replacement Cow instances up to the specified number and breed.

        Initializes replacement cows through a separate initialization method if the current count is insufficient and
        optionally shuffles the list if `order_by_random` is set to True.

        Parameters:
        ----------
        num : int
            The number of replacement Cow instances desired.
        breed : str
            The breed type for the replacement Cow instances.

        Returns:
        --------
        List[Cow]
            A list of replacement Cow instances.
        """
        self._init_replacement_cows(num, breed)

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
