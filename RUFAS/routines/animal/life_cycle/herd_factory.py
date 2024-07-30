import copy
import datetime
from pathlib import Path
import random
from typing import List, Dict, Any, Type

from tqdm import tqdm

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.animal_manager import AnimalManager, Feed
from RUFAS.routines.animal.animal_typed_dicts import AnimalBaseInitArgsTypedDict
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.life_cycle.animal_population import AnimalPopulation
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII

om = OutputManager()


class HerdFactory:
    """
    Class to initialize herd for simulation.

    Attributes
    ----------
    breed : str
        The breed of the animals in the simulation, retrieved from input data.
    CI : int
        Calving interval from the animal configuration, retrieved from input data.
    initial_animal_num : int
        The initial number of animals in the simulation, retrieved from input data.
    simulation_days : int
        The number of days the simulation will run to generate herd, retrieved from input data.
    pre_animal_population : AnimalPopulation
        An instance of AnimalPopulation representing the animal population
        before random sampling with replacement.
    post_animal_population : AnimalPopulation
        An instance of AnimalPopulation representing the animal population
        after random sampling with replacement.
    """

    def __init__(
        self,
        init_herd: bool = False,
        save_animals: bool = False,
        save_animals_path: Path = Path("output/"),
    ) -> None:
        """
        Initializes HerdFactory.

        Parameters
        ----------
        init_herd : bool, default=False
            A flag to indicate whether to initialize through simulation or from input data.
        save_animals : bool, default=False
            Indicates whether to save the generated animals to JSON files.
        save_animals_path : Path, default=Path("output/")
            The directory path where the animal data JSON files will be saved if
            save_animals is True.
        """
        self.im = InputManager()
        self.init_herd = init_herd
        self.save_animals = save_animals
        self.save_animals_path = save_animals_path

        self.breed = self.im.get_data("animal.herd_information.breed")
        self.CI = self.im.get_data("animal.animal_config.farm_level.repro.calving_interval")
        self.initial_animal_num = self.im.get_data("animal.herd_initialization.initial_animal_num")
        self.simulation_days = self.im.get_data("animal.herd_initialization.simulation_days")

        self.pre_animal_population = AnimalPopulation(
            calves=[],
            heiferIs=[],
            heiferIIs=[],
            heiferIIIs=[],
            cows=[],
            replacement=[],
            current_animal_id=0,
        )
        self.post_animal_population = AnimalPopulation(
            calves=[],
            heiferIs=[],
            heiferIIs=[],
            heiferIIIs=[],
            cows=[],
            replacement=[],
            current_animal_id=0,
        )

    def _calves_update(self) -> None:
        """Calves update for generating herd simulation"""
        remaining_calves: List[Calf] = []
        for calf in self.pre_animal_population.calves:
            wean_day = calf.update(0)
            if wean_day:
                args = calf.get_calf_values()
                args.update(id=self.pre_animal_population.next_id())

                heiferI = HeiferI(args)
                self.pre_animal_population.heiferIs.append(heiferI)
            else:
                remaining_calves.append(calf)
        self.pre_animal_population.calves = remaining_calves

    def _heiferIs_update(self) -> None:
        """heiferIs update for generating herd simulation"""
        remaining_heiferIs: List[HeiferI] = []
        for heiferI in self.pre_animal_population.heiferIs:
            second_stage = heiferI.update(0)
            if second_stage:
                args = heiferI.get_heiferI_values()

                args.update(id=self.pre_animal_population.next_id())
                args.update(repro_program=AnimalBase.config["heifer_repro_method"])
                args.update(tai_method_h=AnimalBase.config["heifers"]["repro_sub_protocol"])
                args.update(synch_ed_method_h=AnimalBase.config["heifers"]["repro_sub_protocol"])
                args.update(repro_sub_protocol=AnimalBase.config["heifers"]["repro_sub_protocol"])

                heiferII = HeiferII(args)
                self.pre_animal_population.heiferIIs.append(heiferII)
            else:
                remaining_heiferIs.append(heiferI)
        self.pre_animal_population.heiferIs = remaining_heiferIs

    def _heiferIIs_update(self) -> None:
        """HeiferIIs update for generating herd simulation"""
        remaining_heiferIIs: List[HeiferII] = []
        for heiferII in self.pre_animal_population.heiferIIs:
            cull_stage, third_stage = heiferII.update(0)
            if cull_stage:
                continue
            if third_stage:
                args = heiferII.get_heiferII_values()
                args.update(id=self.pre_animal_population.next_id())

                heiferIII = HeiferIII(args)
                self.pre_animal_population.heiferIIIs.append(heiferIII)
            else:
                remaining_heiferIIs.append(heiferII)
        self.pre_animal_population.heiferIIs = remaining_heiferIIs

    def _heiferIIIs_update(self, day: int) -> None:
        """HeiferIIIs update for generating herd simulation"""
        remaining_heiferIIIs: List[HeiferIII] = []
        for heiferIII in self.pre_animal_population.heiferIIIs:
            cow_stage = heiferIII.update(0)
            if cow_stage:
                args = heiferIII.get_heiferIII_values()

                args.update(id=self.pre_animal_population.next_id())
                args.update(repro_program=AnimalBase.config["cow_repro_method"])
                args.update(presynch_method=AnimalBase.config["cows"]["presynch_program"])
                args.update(tai_method_c=AnimalBase.config["cows"]["ovsynch_program"])
                args.update(resynch_method=AnimalBase.config["cows"]["resynch_program"])

                cow = Cow(args)

                self.pre_animal_population.cows.append(cow)
                if day >= 3000:
                    args.update(id=self.pre_animal_population.next_id())
                    replacement_cow = Cow(args)
                    self.pre_animal_population.replacement.append(replacement_cow)
            else:
                remaining_heiferIIIs.append(heiferIII)

        self.pre_animal_population.heiferIIIs = remaining_heiferIIIs

    def _cows_update(self) -> None:
        """Cows update for generating herd simulation"""
        remaining_cows: List[Cow] = []
        for cow in self.pre_animal_population.cows:
            new_born = cow.update(0, self.CI)
            if cow.culled or cow.calves > 4:
                continue
            else:
                remaining_cows.append(cow)
            if new_born:
                args = AnimalBaseInitArgsTypedDict(
                    id=self.pre_animal_population.next_id(),
                    breed=self.breed,
                    birth_date=0,
                    days_born=0,
                    p_init=cow.p_gest_for_calf,
                    birth_weight=cow.calf_birth_weight,
                )
                cow.p_animal = cow.p_animal - cow.p_gest_for_calf + cow.p_growth + cow.dP_reserves
                cow.p_gest_for_calf = 0.0
                cow.calf_birth_weight = 0.0

                calf = Calf(args)
                if not (calf.culled or calf.sold):
                    self.pre_animal_population.calves.append(calf)
        self.pre_animal_population.cows = remaining_cows

    def _generate_animals(self) -> AnimalPopulation:
        """Function to generate an AnimalPopulation object through simulation"""
        for _ in range(self.initial_animal_num):
            args = AnimalBaseInitArgsTypedDict(
                id=self.pre_animal_population.next_id(),
                breed=self.breed,
                birth_date=0,
                days_born=0,
                p_init=0,
                birth_weight=0,
            )
            calf = Calf(args)
            if not (calf.culled or calf.sold):
                self.pre_animal_population.calves.append(calf)

        for day in tqdm(range(self.simulation_days)):
            self._calves_update()
            self._heiferIs_update()
            self._heiferIIs_update()
            self._heiferIIIs_update(day=day)
            self._cows_update()

        return self.pre_animal_population

    def _init_animal_from_data(
        self, animal_type: str, animal_data: Dict[str, Any]
    ) -> Calf | HeiferI | HeiferII | HeiferIII | Cow:
        """Function to initialize an animal object from input data"""
        ANIMAL_CLASSES: Dict[str, Type] = {
            "calf": Calf,
            "heiferI": HeiferI,
            "heiferII": HeiferII,
            "heiferIII": HeiferIII,
            "cow": Cow,
            "replacement": Cow,
        }

        animal_data.update(id=self.pre_animal_population.next_id())
        if animal_type == "calf":
            animal_data.update(p_init=0)

        return ANIMAL_CLASSES[animal_type](animal_data)

    def _initialize_herd_from_data(self) -> AnimalPopulation:
        """Function to initialize an AnimalPopulation object from input data"""
        herd_data = self.im.get_data("animal_population")
        calves = list(
            map(
                self._init_animal_from_data,
                ["calf"] * len(herd_data["calves"]),
                herd_data["calves"],
            )
        )
        heiferIs = list(
            map(
                self._init_animal_from_data,
                ["heiferI"] * len(herd_data["heiferIs"]),
                herd_data["heiferIs"],
            )
        )
        heiferIIs = list(
            map(
                self._init_animal_from_data,
                ["heiferII"] * len(herd_data["heiferIIs"]),
                herd_data["heiferIIs"],
            )
        )
        heiferIIIs = list(
            map(
                self._init_animal_from_data,
                ["heiferIII"] * len(herd_data["heiferIIIs"]),
                herd_data["heiferIIIs"],
            )
        )
        cows = list(
            map(
                self._init_animal_from_data,
                ["cow"] * len(herd_data["cows"]),
                herd_data["cows"],
            )
        )
        replacement = list(
            map(
                self._init_animal_from_data,
                ["replacement"] * len(herd_data["replacement"]),
                herd_data["replacement"],
            )
        )

        return AnimalPopulation(
            calves=calves,
            heiferIs=heiferIs,
            heiferIIs=heiferIIs,
            heiferIIIs=heiferIIIs,
            cows=cows,
            replacement=replacement,
            current_animal_id=self.pre_animal_population.current_animal_id,
        )

    def _random_sample_with_replacement(self) -> AnimalPopulation:
        """Function to randomly sample the herd with replacement"""
        post_calves: List[Calf] = self._random_sample_with_replacement_by_type("calf")
        post_heiferIs: List[HeiferI] = self._random_sample_with_replacement_by_type("heiferI")
        post_heiferIIs: List[HeiferII] = self._random_sample_with_replacement_by_type("heiferII")
        post_heiferIIIs: List[HeiferIII] = self._random_sample_with_replacement_by_type("heiferIII")
        post_cows: List[Cow] = self._random_sample_with_replacement_by_type("cow")
        post_replacement: List[Cow] = self._random_sample_with_replacement_by_type("replacement")

        return AnimalPopulation(
            calves=post_calves,
            heiferIs=post_heiferIs,
            heiferIIs=post_heiferIIs,
            heiferIIIs=post_heiferIIIs,
            cows=post_cows,
            replacement=post_replacement,
            current_animal_id=self.post_animal_population.current_animal_id,
            order_by_random=True,
        )

    def _random_sample_with_replacement_by_type(
        self, animal_type: str
    ) -> List[Calf] | List[HeiferI] | List[HeiferII] | List[HeiferIII] | List[Cow]:
        """Function to randomly sample a specific animal type with replacement"""
        PRE_ANIMAL_DATA: Dict[
            str,
            (List[Calf] | List[HeiferI] | List[HeiferII] | List[HeiferIII] | List[Cow]),
        ] = {
            "calf": self.pre_animal_population.calves,
            "heiferI": self.pre_animal_population.heiferIs,
            "heiferII": self.pre_animal_population.heiferIIs,
            "heiferIII": self.pre_animal_population.heiferIIIs,
            "cow": self.pre_animal_population.cows,
            "replacement": self.pre_animal_population.replacement,
        }
        pre_animals = PRE_ANIMAL_DATA[animal_type]

        ANIMAL_NUM_KEY: Dict[str, str] = {
            "calf": "animal.herd_information.calf_num",
            "heiferI": "animal.herd_information.heiferI_num",
            "heiferII": "animal.herd_information.heiferII_num",
            "heiferIII": "animal.herd_information.heiferIII_num_springers",
            "cow": "animal.herd_information.cow_num",
            "replacement": "animal.herd_information.replace_num",
        }
        animal_num = self.im.get_data(ANIMAL_NUM_KEY[animal_type])

        post_animals = []
        random_choices = random.choices(list(range(len(pre_animals))), k=animal_num)
        for choice in random_choices:
            animal = copy.deepcopy(pre_animals[choice])
            animal.id = self.post_animal_population.next_id()
            post_animals.append(animal)

        return post_animals

    def initialize_herd(self) -> None:
        """
        Initialize an AnimalPopulation object for simulation, either from input data or generate from simulation. This
        function also optionally saves the generated herd data into a JSON file.
        The initialized herd with be randomly sampled with replacement, and added to the InputManager pool.
        """
        AnimalBase.set_config(AnimalManager.get_animal_config(self.im.get_data("animal.animal_config")))
        AnimalBase.set_nutrient_list(Feed(self.im.get_data("feed")).nutrient_rqmts)

        if self.init_herd:
            self.pre_animal_population = self._generate_animals()
            if self.save_animals:
                timestamp: str = datetime.datetime.now().strftime("%d-%b-%Y_%a_%H-%M-%S")
                save_path = Path.joinpath(self.save_animals_path, f"animal_population-{timestamp}.json")
                om.dict_to_file_json(
                    self.pre_animal_population.__repr__(),
                    save_path,
                    minify_output_file=True,
                )
        else:
            self.pre_animal_population = self._initialize_herd_from_data()

        self.post_animal_population = self._random_sample_with_replacement()
        self.im.add_dict_variable_to_pool(
            variable_name="runtime_animal_population",
            data=self.post_animal_population.__repr__(),
            properties_blob_key="animal_population_properties",
            eager_termination=False,
        )
