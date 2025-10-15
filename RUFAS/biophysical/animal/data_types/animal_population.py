from dataclasses import dataclass
from random import shuffle
from typing import Any

import matplotlib.pyplot as plt

from RUFAS.biophysical.animal.animal import Animal


@dataclass(kw_only=True)
class AnimalPopulationStatistics:
    """
    AnimalPopulationStatistics is a data container class for various statistical data for an animal population.

    Attributes
    ----------
    breed : set[str]
        The set of breeds in the population.

    number_of_calves : int
        Total number of calves in the population.
    number_of_heiferIs : int
        Total number of heiferIs stage.
    number_of_heiferIIs : int
        Total number of heiferIIs stage.
    number_of_heiferIIIs : int
        Total number of heiferIIIs stage.
    number_of_cows : int
        Total number of cows in the population.
    number_of_replacement_heiferIIIS : int
        Total number of replacement heifers.
    number_of_lactating_cows : int
        Total number of lactating cows in the population.
    number_of_dry_cows : int
        Total number of non-lactating (dry) cows in the population.

    number_of_parity_1_cows : int
        Total number of cows that have their first parity.
    number_of_parity_2_cows : int
        Total number of cows that have their second parity.
    number_of_parity_3_cows : int
        Total number of cows that have their third parity.
    number_of_parity_4_cows : int
        Total number of cows that have their fourth parity.
    number_of_parity_5_cows : int
        Total number of cows that have their fifth parity.
    number_of_parity_6_or_more_cows : int
        Total number of cows that have their sixth or higher parity.

    average_calf_age : float
        Average age of calves in the population, (days).
    average_heiferI_age : float
        Average age of heiferIS stage, (days).
    average_heiferII_age : float
        Average age of heiferIIs stage, (days).
    average_heiferIII_age : float
        Average age of heiferIIIs stage, (days).
    average_cow_age : float
        Average age of cows in the population, (days).
    average_replacement_age : float
        Average age of replacement animals in the population, (days).

    calf_age_distribution : dict[str, int]
        The distribution of calf ages in the population.
    heiferI_age_distribution : dict[str, int]
        The distribution of heiferI ages in the population.
    heiferII_age_distribution : dict[str, int]
        The distribution of heiferII ages in the population.
    heiferIII_age_distribution : dict[str, int]
        The distribution of heiferIII ages in the population.
    cow_age_distribution : dict[str, int]
        The distribution of cow ages in the population.
    replacement_age_distribution : dict[str, int]
        The distribution of replacement animal ages in the population.

    average_calf_body_weight : float
        Average body weight of calves in the population, (kg).
    average_heiferI_body_weight : float
        Average body weight of heiferIs, (kg).
    average_heiferII_body_weight : float
        Average body weight of heiferIIs, (kg).
    average_heiferIII_body_weight : float
        Average body weight of heiferIIIs, (kg).
    average_cow_body_weight : float
        Average body weight of cows in the population, (kg).
    average_replacement_body_weight : float
        Average body weight of replacement animals in the population, (kg).

    average_cow_days_in_pregnancy : float
        Average number of days cows have been in pregnancy, (days).
    average_cow_days_in_milk : float
        Average number of days cows have been producing milk since last calving, (days).
    average_cow_parity : float
        Average parity number of cows in the population, (days).
    average_cow_calving_interval : float
        Average interval (in days) between calvings for cows in the population, (days).
    """

    breed: set[str]

    number_of_calves: int
    number_of_heiferIs: int
    number_of_heiferIIs: int
    number_of_heiferIIIs: int
    number_of_cows: int
    number_of_replacement_heiferIIIS: int
    number_of_lactating_cows: int
    number_of_dry_cows: int

    number_of_parity_1_cows: int
    number_of_parity_2_cows: int
    number_of_parity_3_cows: int
    number_of_parity_4_cows: int
    number_of_parity_5_cows: int
    number_of_parity_6_or_more_cows: int

    average_calf_age: float
    average_heiferI_age: float
    average_heiferII_age: float
    average_heiferIII_age: float
    average_cow_age: float
    average_replacement_age: float

    calf_age_distribution: dict[str, int]
    heiferI_age_distribution: dict[str, int]
    heiferII_age_distribution: dict[str, int]
    heiferIII_age_distribution: dict[str, int]
    cow_age_distribution: dict[str, int]
    replacement_age_distribution: dict[str, int]

    average_calf_body_weight: float
    average_heiferI_body_weight: float
    average_heiferII_body_weight: float
    average_heiferIII_body_weight: float
    average_cow_body_weight: float
    average_replacement_body_weight: float

    average_cow_days_in_pregnancy: float
    average_cow_days_in_milk: float
    average_cow_parity: float
    average_cow_calving_interval: float


@dataclass(kw_only=True)
class AnimalPopulation:
    """
    A data class representing the population of animals in a herd.

    Attributes
    ----------
    calves : list[Calf]
        A list of Calf instances in the herd.
    heiferIs : list[HeiferI]
        A list of HeiferI (stage I heifers) instances in the herd.
    heiferIIs : list[HeiferII]
        A list of HeiferII (stage II heifers) instances in the herd.
    heiferIIIs : list[HeiferIII]
        A list of HeiferIII (stage III heifers) instances in the herd.
    cows : list[Cow]
        A list of Cow instances in the herd.
    replacement : list[Cow]
        A list of replacement Cow instances in the herd.
    current_animal_id : int, default=0
        The highest ID number among all animals in the herd.
    order_by_random : bool, default=0
        A flag to indicate whether the animals should be ordered randomly.

    """

    calves: list[Animal]
    heiferIs: list[Animal]
    heiferIIs: list[Animal]
    heiferIIIs: list[Animal]
    cows: list[Animal]
    replacement: list[Animal]

    current_animal_id: int = 0
    order_by_random: bool = True

    def __post_init__(self) -> None:
        """Post init function to find the max id of all animals, and set the current_animal_id"""
        all_animals = (
            self.calves
            + self.heiferIs
            + self.heiferIIs
            + self.heiferIIIs
            + self.cows
            + self.filter_cow_status(1, True)
            + self.filter_cow_status(2, True)
            + self.filter_cow_status(3, True)
            + self.filter_cow_status(4, True)
            + self.filter_cow_status(5, True)
            + self.filter_cow_status(1, False)
            + self.filter_cow_status(2, False)
            + self.filter_cow_status(3, False)
            + self.filter_cow_status(4, False)
            + self.filter_cow_status(5, False)
            + self.replacement
        )
        ids = [animal.id for animal in all_animals]
        if ids:
            AnimalPopulation.set_current_max_animal_id(max(ids))

    def __repr__(self) -> dict[str, list[dict[str, Any]]]:
        """Dictionary representation of the AnimalPopulation object"""
        return {
            "calves": [dict(calf.get_animal_values()) for calf in self.calves],
            "heiferIs": [dict(heiferI.get_animal_values()) for heiferI in self.heiferIs],
            "heiferIIs": [dict(heiferII.get_animal_values()) for heiferII in self.heiferIIs],
            "heiferIIIs": [dict(heiferIII.get_animal_values()) for heiferIII in self.heiferIIIs],
            "cows": [dict(cow.get_animal_values()) for cow in self.cows],
            "cows_parity_1_milking": [
                dict(cow.get_animal_values()) for cow in self.filter_cow_status(parity=1, is_milking=True)
            ],
            "cows_parity_2_milking": [
                dict(cow.get_animal_values()) for cow in self.filter_cow_status(parity=2, is_milking=True)
            ],
            "cows_parity_3_milking": [
                dict(cow.get_animal_values()) for cow in self.filter_cow_status(parity=3, is_milking=True)
            ],
            "cows_parity_4_milking": [
                dict(cow.get_animal_values()) for cow in self.filter_cow_status(parity=4, is_milking=True)
            ],
            "cows_parity_5_milking": [
                dict(cow.get_animal_values()) for cow in self.filter_cow_status(parity=5, is_milking=True)
            ],
            "cows_parity_1_not_milking": [
                dict(cow.get_animal_values()) for cow in self.filter_cow_status(parity=1, is_milking=False)
            ],
            "cows_parity_2_not_milking": [
                dict(cow.get_animal_values()) for cow in self.filter_cow_status(parity=2, is_milking=False)
            ],
            "cows_parity_3_not_milking": [
                dict(cow.get_animal_values()) for cow in self.filter_cow_status(parity=3, is_milking=False)
            ],
            "cows_parity_4_not_milking": [
                dict(cow.get_animal_values()) for cow in self.filter_cow_status(parity=4, is_milking=False)
            ],
            "cows_parity_5_not_milking": [
                dict(cow.get_animal_values()) for cow in self.filter_cow_status(parity=5, is_milking=False)
            ],
            "replacement": [dict(replacement.get_animal_values()) for replacement in self.replacement],
        }

    @classmethod
    def next_id(cls) -> int:
        """
        Increment and return the next unique identifier for an animal.

        Returns
        -------
        int
            The next unique animal_id.
        """
        cls.current_animal_id += 1
        return cls.current_animal_id

    @classmethod
    def set_current_max_animal_id(cls, animal_id: int) -> None:
        """Set the current_animal_id to the given animal_id."""
        cls.current_animal_id = animal_id

    def get_calves(self) -> list[Animal]:
        """
        Retrieve a list of Calf instances.

        Returns
        -------
        list[Animal]
            A list of Calf instances.
        """
        if self.order_by_random:
            shuffle(self.calves)
        return self.calves

    def get_heiferIs(self) -> list[Animal]:
        """
        Retrieve a list of HeiferI instances.

        Returns
        -------
        list[Animal]
            A list of HeiferI instances.
        """
        if self.order_by_random:
            shuffle(self.heiferIs)

        return self.heiferIs

    def get_heiferIIs(self) -> list[Animal]:
        """
        Retrieve a list of HeiferII instances.

        Returns
        -------
        list[Animal]
            A list of HeiferII instances.
        """
        if self.order_by_random:
            shuffle(self.heiferIIs)

        return self.heiferIIs

    def get_heiferIIIs(self) -> list[Animal]:
        """
        Retrieve a list of HeiferIII instances.

        Returns
        -------
        list[Animal]
            A list of HeiferIII instances.
        """
        if self.order_by_random:
            shuffle(self.heiferIIIs)
        return self.heiferIIIs

    def get_cows(self) -> list[Animal]:
        """
        Retrieve a list of Cow instances.

        Returns
        -------
        list[Animal]
            A list of Cow instances.
        """
        if self.order_by_random:
            shuffle(self.cows)
        return self.cows

    def get_replacement_cows(self) -> list[Animal]:
        """
        Retrieve a list of replacement Cow instances.

        Returns
        -------
        list[Animal]
            A list of replacement Cow instances.
        """
        if self.order_by_random:
            shuffle(self.replacement)
        return self.replacement

    def filter_cow_status(self, parity: int, is_milking: bool, days_born: int = 0) -> list[Animal]:
        """
        Get the list of cows with the provided parity and milking condition
        Parameters
        ----------
        parity : int
            The number parity.
        is_milking : bool
            Cow's milking status
        days_born : int, default = 0
            Filter the cows whose days_born exceeds the given value.

        Returns
        -------
        list[Animal]
            Return cows that matches the provided condition.

        """
        return [
            cow
            for cow in self.cows
            if cow.calves == parity and cow.is_milking == is_milking and cow.days_born >= days_born
        ]

    @staticmethod
    def _average(data: list[int | float]) -> float:
        """
        A custom get-average function for the given data. Returns 0 for an empty list.

        Parameters
        ----------
        data :  list[int | float]
            The input data.

        Returns
        -------
        float
            The average of the given data, or 0 for an empty data list.
        """
        return sum(data) / len(data) if len(data) else 0

    @staticmethod
    def find_distribution(
        data: list[int | float], variable_name: str, num_bins: int = 5
    ) -> tuple[float, dict[str, int]]:
        """
        Finds the distribution of the given data divided into bins.

        Parameters
        ----------
        data : list[int | float]
            The input data to find the distribution of.
        variable_name : str
            The name of the variable to be used in the distribution.
        num_bins : int, default=5
            The number of bins to divide the data into.

        Returns
        -------
        tuple[float, dict[str, int]]
            A tuple of:
            - float: The average of the data.
            - dict[str, int]: A dictionary containing the distribution of the data.
        """
        average = AnimalPopulation._average(data)
        n, bins, _ = plt.hist(data, bins=num_bins)
        distributions = {f"{variable_name}_{bins[i]:.1f}_to_{bins[i + 1]:.1f}": int(n[i]) for i in range(len(n))}
        return average, distributions

    def get_herd_summary(self) -> AnimalPopulationStatistics:
        """
        Returns a dictionary containing herd summary information

        Returns
        -------
        AnimalPopulationStatistics
            An AnimalPopulationStatistics object which stores the summary of the herd population.
        """
        all_animals = self.calves + self.heiferIs + self.heiferIIs + self.heiferIIIs + self.cows + self.replacement
        breed: set[str] = set([animal.breed.value for animal in all_animals])
        lac_cows = [cow for cow in self.cows if cow.is_milking]
        dry_cows = [cow for cow in self.cows if not cow.is_milking]
        parity_1_cows = [cow for cow in self.cows if cow.calves == 1]
        parity_2_cows = [cow for cow in self.cows if cow.calves == 2]
        parity_3_cows = [cow for cow in self.cows if cow.calves == 3]
        parity_4_cows = [cow for cow in self.cows if cow.calves == 4]
        parity_5_cows = [cow for cow in self.cows if cow.calves == 5]
        parity_6_or_more_cows = [cow for cow in self.cows if cow.calves >= 6]

        num_calf = len(self.calves)
        num_heiferI = len(self.heiferIs)
        num_heiferII = len(self.heiferIIs)
        num_heiferIII = len(self.heiferIIIs)
        num_cow = len(self.cows)
        num_replacement = len(self.replacement)
        num_lac_cow = len(lac_cows)
        num_dry_cow = len(dry_cows)
        num_parity_1_cow = len(parity_1_cows)
        num_parity_2_cow = len(parity_2_cows)
        num_parity_3_cow = len(parity_3_cows)
        num_parity_4_cow = len(parity_4_cows)
        num_parity_5_cow = len(parity_5_cows)
        num_parity_6_or_more_cow = len(parity_6_or_more_cows)

        avg_calf_age, calf_age_distributions = self.find_distribution(
            [calf.days_born for calf in self.calves], "calf_age"
        )
        avg_heiferI_age, heiferI_age_distributions = self.find_distribution(
            [heiferI.days_born for heiferI in self.heiferIs], "heiferI_age"
        )
        avg_heiferII_age, heiferII_age_distributions = self.find_distribution(
            [heiferII.days_born for heiferII in self.heiferIIs], "heiferII_age"
        )
        avg_heiferIII_age, heiferIII_age_distributions = self.find_distribution(
            [heiferIII.days_born for heiferIII in self.heiferIIIs], "heiferIII_age"
        )
        avg_cow_age, cow_age_distributions = self.find_distribution([cow.days_born for cow in self.cows], "cow_age")
        avg_replacement_age, replacement_age_distributions = self.find_distribution(
            [replacement.days_born for replacement in self.replacement], "replacement_age"
        )

        avg_calf_body_weight = self._average([calf.body_weight for calf in self.calves])
        avg_heiferI_body_weight = self._average([heiferI.body_weight for heiferI in self.heiferIs])
        avg_heiferII_body_weight = self._average([heiferII.body_weight for heiferII in self.heiferIIs])
        avg_heiferIII_body_weight = self._average([heiferIII.body_weight for heiferIII in self.heiferIIIs])
        avg_cow_body_weight = self._average([cow.body_weight for cow in self.cows])
        avg_replacement_body_weight = self._average([replacement.body_weight for replacement in self.replacement])

        cow_avg_days_in_pregnancy = self._average([cow.days_in_pregnancy for cow in self.cows])
        cow_avg_days_in_milk = self._average([cow.days_in_milk for cow in self.cows])
        cow_avg_parity = self._average([cow.calves for cow in self.cows])
        cow_avg_calving_interval = self._average([cow.calving_interval for cow in self.cows])

        return AnimalPopulationStatistics(
            breed=breed,
            number_of_calves=num_calf,
            number_of_heiferIs=num_heiferI,
            number_of_heiferIIs=num_heiferII,
            number_of_heiferIIIs=num_heiferIII,
            number_of_cows=num_cow,
            number_of_replacement_heiferIIIS=num_replacement,
            number_of_lactating_cows=num_lac_cow,
            number_of_dry_cows=num_dry_cow,
            number_of_parity_1_cows=num_parity_1_cow,
            number_of_parity_2_cows=num_parity_2_cow,
            number_of_parity_3_cows=num_parity_3_cow,
            number_of_parity_4_cows=num_parity_4_cow,
            number_of_parity_5_cows=num_parity_5_cow,
            number_of_parity_6_or_more_cows=num_parity_6_or_more_cow,
            average_calf_age=avg_calf_age,
            average_heiferI_age=avg_heiferI_age,
            average_heiferII_age=avg_heiferII_age,
            average_heiferIII_age=avg_heiferIII_age,
            average_cow_age=avg_cow_age,
            average_replacement_age=avg_replacement_age,
            calf_age_distribution=calf_age_distributions,
            heiferI_age_distribution=heiferI_age_distributions,
            heiferII_age_distribution=heiferII_age_distributions,
            heiferIII_age_distribution=heiferIII_age_distributions,
            cow_age_distribution=cow_age_distributions,
            replacement_age_distribution=replacement_age_distributions,
            average_calf_body_weight=avg_calf_body_weight,
            average_heiferI_body_weight=avg_heiferI_body_weight,
            average_heiferII_body_weight=avg_heiferII_body_weight,
            average_heiferIII_body_weight=avg_heiferIII_body_weight,
            average_cow_body_weight=avg_cow_body_weight,
            average_replacement_body_weight=avg_replacement_body_weight,
            average_cow_days_in_pregnancy=cow_avg_days_in_pregnancy,
            average_cow_days_in_milk=cow_avg_days_in_milk,
            average_cow_parity=cow_avg_parity,
            average_cow_calving_interval=cow_avg_calving_interval,
        )
