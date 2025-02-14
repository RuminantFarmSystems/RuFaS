from dataclasses import dataclass
from random import shuffle
from typing import Dict, List

from RUFAS.biophysical.animal.animal import Animal


@dataclass(kw_only=True)
class AnimalPopulation:
    """
    A data class representing the population of animals in a herd.

    Attributes
    ----------
    calves : List[Calf]
        A list of Calf instances in the herd.
    heiferIs : List[HeiferI]
        A list of HeiferI (stage I heifers) instances in the herd.
    heiferIIs : List[HeiferII]
        A list of HeiferII (stage II heifers) instances in the herd.
    heiferIIIs : List[HeiferIII]
        A list of HeiferIII (stage III heifers) instances in the herd.
    cows : List[Cow]
        A list of Cow instances in the herd.
    replacement : List[Cow]
        A list of replacement Cow instances in the herd.
    current_animal_id : int, default=0
        The highest ID number among all animals in the herd.
    order_by_random : bool, default=0
        A flag to indicate whether the animals should be ordered randomly.

    """

    calves: List[Animal]
    heiferIs: List[Animal]
    heiferIIs: List[Animal]
    heiferIIIs: List[Animal]
    cows: List[Animal]
    replacement: List[Animal]

    current_animal_id: int = 0
    order_by_random: bool = True

    def __post_init__(self):
        """Post init function to find the max id of all animals, and set the current_animal_id"""
        ids = [
            i.id for i in self.calves + self.heiferIs + self.heiferIIs + self.heiferIIIs + self.cows + self.replacement
        ]
        if ids:
            self.current_animal_id = max(ids)

    def __repr__(self):
        """Dictionary representation of the AnimalPopulation object"""
        return {
            "calves": [calf.get_calf_values() for calf in self.calves],
            "heiferIs": [heiferI.get_heiferI_values() for heiferI in self.heiferIs],
            "heiferIIs": [heiferII.get_heiferII_values() for heiferII in self.heiferIIs],
            "heiferIIIs": [heiferIII.get_heiferIII_values() for heiferIII in self.heiferIIIs],
            "cows": [cow.get_cow_values() for cow in self.cows],
            "replacement": [replacement.get_replacement_values() for replacement in self.replacement],
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

    def get_calves(self) -> List[Animal]:
        """
        Retrieve a list of Calf instances.

        Returns
        -------
        List[Calf]
            A list of Calf instances.
        """
        if self.order_by_random:
            shuffle(self.calves)
        return self.calves

    def get_heiferIs(self) -> List[Animal]:
        """
        Retrieve a list of HeiferI instances.

        Returns
        -------
        List[HeiferI]
            A list of HeiferI instances.
        """
        if self.order_by_random:
            shuffle(self.heiferIs)

        return self.heiferIs

    def get_heiferIIs(self) -> List[Animal]:
        """
        Retrieve a list of HeiferII instances.

        Returns
        -------
        List[HeiferII]
            A list of HeiferII instances.
        """
        if self.order_by_random:
            shuffle(self.heiferIIs)

        return self.heiferIIs

    def get_heiferIIIs(self) -> List[Animal]:
        """
        Retrieve a list of HeiferIII instances.

        Returns
        -------
        List[HeiferIII]
            A list of HeiferIII instances.
        """
        if self.order_by_random:
            shuffle(self.heiferIIIs)
        return self.heiferIIIs

    def get_cows(self) -> List[Animal]:
        """
        Retrieve a list of Cow instances.

        Returns
        -------
        List[Cow]
            A list of Cow instances.
        """
        if self.order_by_random:
            shuffle(self.cows)
        return self.cows

    def get_replacement_cows(self) -> List[Animal]:
        """
        Retrieve a list of replacement Cow instances.

        Returns
        -------
        List[Cow]
            A list of replacement Cow instances.
        """
        if self.order_by_random:
            shuffle(self.replacement)
        return self.replacement

    @staticmethod
    def _average(data: List[int | float]) -> float:
        """
        A custom get-average function for the given data. Returns 0 for an empty list.

        Parameters
        ----------
        data :  List[int | float]
            The input data.

        Returns
        -------
        float
            The average of the given data, or 0 for an empty data list.
        """
        return sum(data) / len(data) if len(data) else 0

    def get_herd_summary(self) -> Dict[str, int | float]:
        """
        Returns a dictionary containing herd summary information

        Returns
        -------
        Dict[str, int | float]
            A dictionary which stores the summary of the initialization
        """
        num_calf = len(self.calves)
        num_heiferI = len(self.heiferIs)
        num_heiferII = len(self.heiferIIs)
        num_heiferIII = len(self.heiferIIIs)
        num_cow = len(self.cows)
        num_replacement = len(self.replacement)

        avg_calf_age = self._average([calf.days_born for calf in self.calves])
        avg_heiferI_age = self._average([heiferI.days_born for heiferI in self.heiferIs])
        avg_heiferII_age = self._average([heiferII.days_born for heiferII in self.heiferIIs])
        avg_heiferIII_age = self._average([heiferIII.days_born for heiferIII in self.heiferIIIs])
        avg_cow_age = self._average([cow.days_born for cow in self.cows])
        avg_replacement_age = self._average([replacement.days_born for replacement in self.replacement])

        cow_avg_days_in_preg = self._average([cow.days_in_pregnancy for cow in self.cows])
        cow_avg_days_in_milk = self._average([cow.days_in_milk for cow in self.cows])
        cow_avg_parity = self._average([cow.reproduction.calves for cow in self.cows])
        cow_avg_CI = self._average([cow.reproduction.calving_interval for cow in self.cows])

        summary = {
            "num_calf": num_calf,
            "num_heiferI": num_heiferI,
            "num_heiferII": num_heiferII,
            "num_heiferIII": num_heiferIII,
            "num_cow": num_cow,
            "num_replacement": num_replacement,
            "avg_calf_age": avg_calf_age,
            "avg_heiferI_age": avg_heiferI_age,
            "avg_heiferII_age": avg_heiferII_age,
            "avg_heiferIII_age": avg_heiferIII_age,
            "avg_cow_age": avg_cow_age,
            "avg_replacement_age": avg_replacement_age,
            "cow_avg_days_in_preg": cow_avg_days_in_preg,
            "cow_avg_days_in_milk": cow_avg_days_in_milk,
            "cow_avg_parity": cow_avg_parity,
            "cow_avg_CI": cow_avg_CI,
        }
        return summary
