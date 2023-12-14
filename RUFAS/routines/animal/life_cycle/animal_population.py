from dataclasses import dataclass
from random import shuffle
from typing import List, Dict

from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII


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
    calves: List[Calf]
    heiferIs: List[HeiferI]
    heiferIIs: List[HeiferII]
    heiferIIIs: List[HeiferIII]
    cows: List[Cow]
    replacement: List[Cow]

    current_animal_id: int = 0
    order_by_random: bool = True

    def __post_init__(self):
        """Post init function to find the max id of all animals, and set the current_animal_id"""
        ids = [i.id for i in self.calves + self.heiferIs + self.heiferIIs + self.heiferIIIs + self.cows + 
               self.replacement]
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
            "replacement": [replacement.get_replacement_values() for replacement in self.replacement]
        }

    def next_id(self) -> int:
       """
       Increment and return the next unique identifier for an animal.

       Returns
       -------
       int
           The next unique animal_id.
       """
        self.current_animal_id += 1
        return self.current_animal_id

    def get_calves(self) -> List[Calf]:
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

    def get_heiferIs(self) -> List[HeiferIs]:
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

    def get_heiferIIs(self) -> List[HeiferIIs]:
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

    def get_heiferIIIs(self) -> List[HeiferIII]:
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

    def get_cows(self) -> List[Cow]:
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

    def get_replacement_cows(self):
        """
        Retrieve a list of replacement Cow instances.

        Returns:
        --------
        List[Cow]
            A list of replacement Cow instances.
        """
        if self.order_by_random:
            shuffle(self.replacement)
        return self.replacement

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
