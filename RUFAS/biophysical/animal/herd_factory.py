import copy
import datetime
import random
from pathlib import Path
from typing import Any

from tqdm import tqdm

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.animal import Animal
from RUFAS.biophysical.animal.animal_config import AnimalConfig
from RUFAS.biophysical.animal.animal_genetics.animal_genetics import AnimalGenetics
from RUFAS.biophysical.animal.animal_module_constants import AnimalModuleConstants
from RUFAS.biophysical.animal.animal_module_reporter import AnimalModuleReporter
from RUFAS.biophysical.animal.data_types.animal_enums import AnimalStatus, Breed
from RUFAS.biophysical.animal.data_types.animal_population import AnimalPopulation
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import NewBornCalfValuesTypedDict
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType
from RUFAS.biophysical.animal.data_types.daily_routines_output import DailyRoutinesOutput
from RUFAS.biophysical.animal.data_types.reproduction import HerdReproductionStatistics
from RUFAS.biophysical.animal.milk.milk_production import MilkProduction
from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.rufas_time import RufasTime
from RUFAS.util import Utility

om = OutputManager()

CALF_BIRTH_WEIGHT_BY_BREED: dict[str, dict[str, float]] = {
    Breed.HO.value: {"average": AnimalConfig.birth_weight_avg_ho, "std": AnimalConfig.birth_weight_std_ho},
    Breed.JE.value: {"average": AnimalConfig.birth_weight_avg_je, "std": AnimalConfig.birth_weight_std_je},
}


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

    post_animal_population: AnimalPopulation | None = None

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

        self.time = RufasTime()

        self.breed: Breed = Breed(Breed[self.im.get_data("animal.herd_information.breed")].value)
        self.CI = self.im.get_data("animal.animal_config.farm_level.repro.calving_interval")
        self.initial_animal_num = self.im.get_data("animal.herd_initialization.initial_animal_num")
        self.simulation_days = self.im.get_data("animal.herd_initialization.simulation_days")
        AnimalGenetics.initialize_class_variables()

        self.pre_animal_population = AnimalPopulation(
            calves=[],
            heiferIs=[],
            heiferIIs=[],
            heiferIIIs=[],
            cows=[],
            replacement=[],
            current_animal_id=0,
        )

    @classmethod
    def set_post_animal_population(cls, animal_population: AnimalPopulation) -> None:
        """
        Sets the post-animal population for the class.

        Parameters
        ----------
        animal_population : AnimalPopulation
            An instance of AnimalPopulation that represents the updated animal population.

        Returns
        -------
        None

        """
        cls.post_animal_population = animal_population

    def _calf_and_heiferI_update(self, animal: Animal) -> DailyRoutinesOutput:
        """
        Updates the daily routines specific for calf and heiferI.

        Parameters
        ----------
        animal : Animal
            The animal instance to update. Must be of type CALF or HEIFER_I.

        Returns
        -------
        DailyRoutinesOutput
            The updated daily routines output after processing the animal's daily growth and life stage update.

        Raises
        ------
        TypeError
            If the animal type is not CALF or HEIFER_I.

        """
        if animal.animal_type not in [AnimalType.CALF, AnimalType.HEIFER_I]:
            raise TypeError(
                f"Unexpected {animal.animal_type.value} type. "
                f"Expecting {AnimalType.CALF.value} or {AnimalType.HEIFER_I.value}."
            )

        daily_routines_output = DailyRoutinesOutput(herd_reproduction_statistics=HerdReproductionStatistics())
        animal.days_born += 1

        animal.daily_growth_update(self.time)

        daily_routines_output.animal_status, _ = animal.animal_life_stage_update(self.time)

        return daily_routines_output

    def _heiferII_update(self, animal: Animal) -> DailyRoutinesOutput:
        """
        Updates the daily routines for heiferII.

        Parameters
        ----------
        animal: Animal
            The animal instance to update. Must be of type AnimalType.HEIFER_II.

        Returns
        -------
        DailyRoutinesOutput
            The updated daily routines output containing the status of the animal.

        Raises
        ------
        TypeError
            If the animal type is not HEIFER_II.

        """
        if not animal.animal_type == AnimalType.HEIFER_II:
            raise TypeError(f"Unexpected {animal.animal_type.value} type. Expecting {AnimalType.HEIFER_II.value}.")

        daily_routines_output = DailyRoutinesOutput(herd_reproduction_statistics=HerdReproductionStatistics())
        animal.days_born += 1

        animal.daily_growth_update(self.time)
        animal.daily_reproduction_update(self.time)

        daily_routines_output.animal_status, _ = animal.animal_life_stage_update(self.time)
        return daily_routines_output

    def _heiferIII_update(self, animal: Animal) -> DailyRoutinesOutput:
        """
        Updates the daily routines for heiferIII.

        Parameters
        ----------
        animal : Animal
            The animal instance to update. Must be of type `AnimalType.HEIFER_III`.

        Returns
        -------
        DailyRoutinesOutput
            The updated daily routines output containing the status of the animal.

        Raises
        ------
        TypeError
            If the provided animal is not of type `AnimalType.HEIFER_III`.

        """
        if not animal.animal_type == AnimalType.HEIFER_III:
            raise TypeError(f"Unexpected {animal.animal_type.value} type. Expecting {AnimalType.HEIFER_III.value}.")

        daily_routines_output = DailyRoutinesOutput(herd_reproduction_statistics=HerdReproductionStatistics())
        animal.days_born += 1

        animal.daily_growth_update(self.time)

        if animal.evaluate_heiferIII_for_cow():
            daily_routines_output.animal_status = AnimalStatus.LIFE_STAGE_CHANGED
        else:
            if animal.is_pregnant:
                animal.days_in_pregnancy += 1
        return daily_routines_output

    def _cow_update(self, animal: Animal) -> DailyRoutinesOutput:
        """
        Updates the daily routines of a cow.

        Parameters
        ----------
        animal : Animal
            An instance of the Animal class representing the cow to be updated.

        Returns
        -------
        DailyRoutinesOutput
            An object that contains updates related to the cow's daily routines such as
            reproduction outputs (newborn calf configuration) and animal life stage status.

        Raises
        ------
        TypeError
            If the provided animal is not of type cow.

        """
        if not animal.animal_type.is_cow:
            raise TypeError(f"Unexpected {animal.animal_type.value} type. Expecting cow.")

        daily_routines_output = DailyRoutinesOutput(herd_reproduction_statistics=HerdReproductionStatistics())
        animal.days_born += 1

        animal.daily_milking_update(self.time)
        animal.daily_growth_update(self.time)
        daily_routines_output.newborn_calf_config, _ = animal.daily_reproduction_update(self.time)

        daily_routines_output.animal_status, _ = animal.animal_life_stage_update(self.time)

        return daily_routines_output

    def _calves_update(self) -> None:
        """Calves update for generating herd simulation"""
        remaining_calves: list[Animal] = []
        for calf in self.pre_animal_population.calves:
            calf_daily_routines_output: DailyRoutinesOutput = self._calf_and_heiferI_update(calf)
            if (
                calf_daily_routines_output.animal_status == AnimalStatus.LIFE_STAGE_CHANGED
                and calf.animal_type == AnimalType.HEIFER_I
            ):
                self.pre_animal_population.heiferIs.append(calf)
            else:
                remaining_calves.append(calf)
        self.pre_animal_population.calves = remaining_calves

    def _heiferIs_update(self) -> None:
        """heiferIs update for generating herd simulation"""
        remaining_heiferIs: list[Animal] = []
        for heiferI in self.pre_animal_population.heiferIs:
            heiferI_daily_routines_output: DailyRoutinesOutput = self._calf_and_heiferI_update(heiferI)
            if (
                heiferI_daily_routines_output.animal_status == AnimalStatus.LIFE_STAGE_CHANGED
                and heiferI.animal_type == AnimalType.HEIFER_II
            ):
                self.pre_animal_population.heiferIIs.append(heiferI)
            else:
                remaining_heiferIs.append(heiferI)
        self.pre_animal_population.heiferIs = remaining_heiferIs

    def _heiferIIs_update(self) -> None:
        """HeiferIIs update for generating herd simulation"""
        remaining_heiferIIs: list[Animal] = []
        for heiferII in self.pre_animal_population.heiferIIs:
            heiferII_daily_routines_output: DailyRoutinesOutput = self._heiferII_update(heiferII)
            if heiferII_daily_routines_output.animal_status == AnimalStatus.SOLD:
                continue
            elif (
                heiferII_daily_routines_output.animal_status == AnimalStatus.LIFE_STAGE_CHANGED
                and heiferII.animal_type == AnimalType.HEIFER_III
            ):
                self.pre_animal_population.heiferIIIs.append(heiferII)
            else:
                remaining_heiferIIs.append(heiferII)
        self.pre_animal_population.heiferIIs = remaining_heiferIIs

    def _cow_give_birth(self, cow: Animal) -> None:
        """
        Handles the birth process of a calf when a cow gives birth.

        Parameters
        ----------
        cow : Animal
            The cow that is giving birth.

        Returns
        -------
        None

        """
        args = NewBornCalfValuesTypedDict(
            id=self.pre_animal_population.next_id(),
            breed=self.breed.name,
            birth_date="",
            days_born=0,
            initial_phosphorus=cow.nutrients.phosphorus_for_gestation_required_for_calf,
            birth_weight=cow.reproduction.calf_birth_weight,
            net_merit=0.0,
            animal_type=AnimalType.CALF.value,
        )
        cow.nutrients.total_phosphorus_in_animal = (
            cow.nutrients.total_phosphorus_in_animal
            - cow.nutrients.phosphorus_for_gestation_required_for_calf
            + cow.nutrients.phosphorus_for_growth
            + cow.nutrients.phosphorus_reserves
        )
        cow.nutrients.phosphorus_for_gestation_required_for_calf = 0.0
        cow.reproduction.calf_birth_weight = 0.0

        calf = Animal(args)
        if not calf.sold:
            self.pre_animal_population.calves.append(calf)
            calf.net_merit = AnimalGenetics.assign_net_merit_value_to_newborn_calf(self.time, calf.breed, cow.net_merit)

    def _heiferIIIs_update(self, day: int) -> None:
        """HeiferIIIs update for generating herd simulation"""
        remaining_heiferIIIs: list[Animal] = []
        for heiferIII in self.pre_animal_population.heiferIIIs:
            heiferIII_daily_routines_output: DailyRoutinesOutput = self._heiferIII_update(heiferIII)
            if heiferIII_daily_routines_output.animal_status == AnimalStatus.LIFE_STAGE_CHANGED:
                if day >= animal_constants.DAYS_TO_START_REPLACEMENT_HERD:
                    self.pre_animal_population.replacement.append(copy.deepcopy(heiferIII))

                heiferIII.transition_heiferIII_to_cow(self.time)
                self.pre_animal_population.cows.append(heiferIII)
                self._cow_give_birth(heiferIII)
            else:
                remaining_heiferIIIs.append(heiferIII)

        self.pre_animal_population.heiferIIIs = remaining_heiferIIIs

    def _cows_update(self) -> None:
        """Cows update for generating herd simulation"""
        remaining_cows: list[Animal] = []
        for cow in self.pre_animal_population.cows:
            cow_daily_routines_output: DailyRoutinesOutput = self._cow_update(cow)
            if (
                cow_daily_routines_output.animal_status in [AnimalStatus.SOLD, AnimalStatus.DEAD]
                or cow.reproduction.calves > 5
            ):
                continue
            else:
                remaining_cows.append(cow)
            if cow_daily_routines_output.newborn_calf_config:
                self._cow_give_birth(cow)
        self.pre_animal_population.cows = remaining_cows

    def _generate_animals(self) -> AnimalPopulation:
        """Function to generate an AnimalPopulation object through simulation"""
        for _ in range(self.initial_animal_num):
            birth_weight: float = Utility.generate_random_number(
                mean=CALF_BIRTH_WEIGHT_BY_BREED[self.breed.value]["average"],
                std_dev=CALF_BIRTH_WEIGHT_BY_BREED[self.breed.value]["std"],
            )
            args = NewBornCalfValuesTypedDict(
                id=self.pre_animal_population.next_id(),
                breed=self.breed.name,
                birth_date="",
                days_born=0,
                initial_phosphorus=0,
                birth_weight=birth_weight,
                net_merit=0.0,
                animal_type=AnimalType.CALF.value,
            )
            calf = Animal(args)
            if not (calf.sold or calf.stillborn):
                self.pre_animal_population.calves.append(calf)
                birth_date_str: str = self.time.current_date.strftime("%Y-%m-%d")
                calf.net_merit = AnimalGenetics.assign_net_merit_value_to_animals_entering_herd(
                    birth_date_str, self.breed
                )

        for day in tqdm(range(self.simulation_days)):
            self._cows_update()
            self._heiferIIIs_update(day=day)
            self._heiferIIs_update()
            self._heiferIs_update()
            self._calves_update()

        return self.pre_animal_population

    def _backtrack_animal_birth_date(self, days_born: int, time: RufasTime) -> str:
        """Function to backtrack the birthdate of an animal loaded from data by subtracting the age of the animal
        from the simulation start date."""
        simulation_start_date = time.start_date
        birth_date: datetime.datetime = simulation_start_date - datetime.timedelta(days=days_born)
        return birth_date.strftime("%Y-%m-%d")

    def _init_animal_from_data(self, animal_type: str, animal_data: Any) -> Animal:
        """Function to initialize an animal object from input data"""
        animal_data.update(id=self.pre_animal_population.next_id())
        if animal_type == "calf":
            animal_data.update(initial_phosphorus=0)
        animal = Animal(animal_data)
        animal_birth_date: str = self._backtrack_animal_birth_date(animal_data["days_born"], self.time)
        animal.net_merit = AnimalGenetics.assign_net_merit_value_to_animals_entering_herd(
            birth_date=animal_birth_date, breed=animal.breed
        )
        return animal

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
        post_calves: list[Animal] = self._random_sample_with_replacement_by_type("calf")
        post_heiferIs: list[Animal] = self._random_sample_with_replacement_by_type("heiferI")
        post_heiferIIs: list[Animal] = self._random_sample_with_replacement_by_type("heiferII")
        post_heiferIIIs: list[Animal] = self._random_sample_with_replacement_by_type("heiferIII")
        post_replacement: list[Animal] = self._random_sample_with_replacement_by_type("replacement")
        post_cows_parity_1_milking: list[Animal] = self._random_sample_with_replacement_by_type("cows_parity_1_milking")
        post_cows_parity_2_milking: list[Animal] = self._random_sample_with_replacement_by_type("cows_parity_2_milking")
        post_cows_parity_3_milking: list[Animal] = self._random_sample_with_replacement_by_type("cows_parity_3_milking")
        post_cows_parity_4_milking: list[Animal] = self._random_sample_with_replacement_by_type("cows_parity_4_milking")
        post_cows_parity_5_milking: list[Animal] = self._random_sample_with_replacement_by_type("cows_parity_5_milking")
        post_cows_parity_1_not_milking: list[Animal] = self._random_sample_with_replacement_by_type(
            "cows_parity_1_not_milking"
        )
        post_cows_parity_2_not_milking: list[Animal] = self._random_sample_with_replacement_by_type(
            "cows_parity_2_not_milking"
        )
        post_cows_parity_3_not_milking: list[Animal] = self._random_sample_with_replacement_by_type(
            "cows_parity_3_not_milking"
        )
        post_cows_parity_4_not_milking: list[Animal] = self._random_sample_with_replacement_by_type(
            "cows_parity_4_not_milking"
        )
        post_cows_parity_5_not_milking: list[Animal] = self._random_sample_with_replacement_by_type(
            "cows_parity_5_not_milking"
        )
        post_cows: list[Animal] = (
            post_cows_parity_1_milking
            + post_cows_parity_2_milking
            + post_cows_parity_3_milking
            + post_cows_parity_4_milking
            + post_cows_parity_5_milking
            + post_cows_parity_1_not_milking
            + post_cows_parity_2_not_milking
            + post_cows_parity_3_not_milking
            + post_cows_parity_4_not_milking
            + post_cows_parity_5_not_milking
        )

        return AnimalPopulation(
            calves=post_calves,
            heiferIs=post_heiferIs,
            heiferIIs=post_heiferIIs,
            heiferIIIs=post_heiferIIIs,
            cows=post_cows,
            replacement=post_replacement,
            order_by_random=True,
        )

    def _random_sample_with_replacement_by_type(self, animal_type: str) -> list[Animal]:
        """Function to randomly sample a specific animal type with replacement"""
        PRE_ANIMAL_DATA: dict[str, list[Animal]] = {
            "calf": self.pre_animal_population.calves,
            "heiferI": self.pre_animal_population.heiferIs,
            "heiferII": self.pre_animal_population.heiferIIs,
            "heiferIII": self.pre_animal_population.heiferIIIs,
            "cow": self.pre_animal_population.cows,
            "cows_parity_1_milking": self.pre_animal_population.filter_cow_status(1, True),
            "cows_parity_2_milking": self.pre_animal_population.filter_cow_status(2, True),
            "cows_parity_3_milking": self.pre_animal_population.filter_cow_status(3, True),
            "cows_parity_4_milking": self.pre_animal_population.filter_cow_status(4, True),
            "cows_parity_5_milking": self.pre_animal_population.filter_cow_status(5, True),
            "cows_parity_1_not_milking": self.pre_animal_population.filter_cow_status(1, False),
            "cows_parity_2_not_milking": self.pre_animal_population.filter_cow_status(2, False),
            "cows_parity_3_not_milking": self.pre_animal_population.filter_cow_status(3, False),
            "cows_parity_4_not_milking": self.pre_animal_population.filter_cow_status(4, False),
            "cows_parity_5_not_milking": self.pre_animal_population.filter_cow_status(5, False),
            "replacement": self.pre_animal_population.replacement,
        }
        pre_animals = PRE_ANIMAL_DATA[animal_type]

        if animal_type in [
            "cows_parity_1_milking",
            "cows_parity_2_milking",
            "cows_parity_3_milking",
            "cows_parity_4_milking",
            "cows_parity_5_milking",
            "cows_parity_1_not_milking",
            "cows_parity_2_not_milking",
            "cows_parity_3_not_milking",
            "cows_parity_4_not_milking",
            "cows_parity_5_not_milking",
        ]:
            PARITY_KEY: dict[str, list[str | bool]] = {
                "cows_parity_1_milking": ["1", True],
                "cows_parity_2_milking": ["2", True],
                "cows_parity_3_milking": ["3", True],
                "cows_parity_4_milking": ["4", True],
                "cows_parity_5_milking": ["5", True],
                "cows_parity_1_not_milking": ["1", False],
                "cows_parity_2_not_milking": ["2", False],
                "cows_parity_3_not_milking": ["3", False],
                "cows_parity_4_not_milking": ["4", False],
                "cows_parity_5_not_milking": ["5", False],
            }

            parity_input_name = "animal.herd_information.parity_fractions." + str(PARITY_KEY[animal_type][0])
            milking_cow_fraction = self.im.get_data("animal.herd_information.milking_cow_fraction")
            if not PARITY_KEY[animal_type][1]:
                milking_cow_fraction = 1 - milking_cow_fraction

            animal_num = int(
                round(
                    (self.im.get_data(parity_input_name) * self.im.get_data("animal.herd_information.cow_num"))
                    * milking_cow_fraction
                )
            )
        else:
            ANIMAL_NUM_KEY: dict[str, str] = {
                "calf": "animal.herd_information.calf_num",
                "heiferI": "animal.herd_information.heiferI_num",
                "heiferII": "animal.herd_information.heiferII_num",
                "heiferIII": "animal.herd_information.heiferIII_num_springers",
                "cow": "animal.herd_information.cow_num",
                "replacement": "animal.herd_information.replace_num",
            }
            animal_num = self.im.get_data(ANIMAL_NUM_KEY[animal_type])

        post_animals = []
        try:
            random_choices = random.choices(list(range(len(pre_animals))), k=animal_num)
            for choice in random_choices:
                animal = copy.deepcopy(pre_animals[choice])
                animal.id = AnimalPopulation.next_id()
                post_animals.append(animal)
        except Exception as e:
            info_map = {
                "class": self.__class__.__name__,
                "function": self._random_sample_with_replacement_by_type.__name__,
            }
            if animal_num == 0:
                om.add_warning(f"Missing {animal_type}", f"No animals sampled for {animal_type}.", info_map)
            else:
                om.add_warning(
                    f"Missing {animal_type} animal population file",
                    f"No animals in group {animal_type} found in animal population file. "
                    "Generating a new herd recommended."
                    f"Full error: {e}",
                    info_map,
                )
        return post_animals

    def initialize_herd(self) -> None:
        """
        Initialize an AnimalPopulation object for simulation, either from input data or generate from simulation.
        This function also optionally saves the generated herd data into a JSON file.
        The initialized herd with be randomly sampled with replacement,
        and set as the class attribute `post_animal_population`.
        """

        AnimalConfig.initialize_animal_config()
        Animal.setup_lactation_curve_parameters(self.time)
        MilkProduction.set_milk_quality(
            AnimalConfig.milk_fat_percent, AnimalConfig.true_protein_percent, AnimalModuleConstants.MILK_LACTOSE
        )
        if self.init_herd:
            if AnimalConfig.semen_type == "sexed":
                om.add_warning(
                    "Longer herd generation runtime",
                    "Herd initialized with sexed semen will result in significantly longer runtime.",
                    info_map={"class": self.__class__.__name__, "function": self.initialize_herd.__name__},
                )
            self.pre_animal_population = self._generate_animals()
            if self.save_animals:
                om.create_directory(self.save_animals_path)
                timestamp: str = datetime.datetime.now().strftime("%d-%b-%Y_%a_%H-%M-%S")
                save_path = Path.joinpath(self.save_animals_path, f"animal_population-{timestamp}.json")
                om.dict_to_file_json(
                    self.pre_animal_population.__repr__(),
                    save_path,
                    minify_output_file=True,
                )
        else:
            self.pre_animal_population = self._initialize_herd_from_data()
        post_animal_population = self._random_sample_with_replacement()
        HerdFactory.set_post_animal_population(post_animal_population)
        AnimalModuleReporter.report_animal_population_statistics(
            "population", self.pre_animal_population.get_herd_summary()
        )
        AnimalModuleReporter.report_animal_population_statistics("initial", post_animal_population.get_herd_summary())
