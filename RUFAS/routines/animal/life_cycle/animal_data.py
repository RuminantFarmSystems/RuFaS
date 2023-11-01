from dataclasses import dataclass
from random import shuffle
from typing import List

from scipy.stats import truncnorm

from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.life_cycle.cow import Cow

from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase


@dataclass(kw_only=True)
class AnimalData:
    animal_id = 0

    calves: List[Calf]
    heiferIs: List[HeiferI]
    heiferIIs: List[HeiferII]
    heiferIIIs: List[HeiferIII]
    cows: List[Cow]
    replacement: List[Cow]

    birth_weight_ho: float
    birth_weight_je: float

    def next_id(self):
        self.animal_id += 1
        return self.animal_id

    def __init__(self, CI, breed, set_seed):
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

        self.CI = CI

        # If set_seed is True, then we do not want the results to be ordered
        # randomly. If set_seed is False, then we do want this.
        self.order_by_random = not set_seed

    def _init_calves(self, num: int, breed: str) -> List[Calf]:
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

    def _init_heiferIs(self, num: int, breed: str, sim_days=5000) -> List[HeiferI]:
        calves = self._init_calves(num, breed)
        heiferIs: List[HeiferI] = []

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

    def _init_heiferIIs(self, num: int, breed: str, sim_days=5000) -> List[HeiferII]:
        heiferIs = self._init_heiferIs(num, breed)
        heiferIIs: List[HeiferII] = []

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

    def _init_heiferIIIs(self, num: int, breed: str, sim_days=5000) -> List[HeiferIII]:
        heiferIIs = self._init_heiferIIs(num, breed)
        heiferIIIs: List[HeiferIII] = []

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

    def _init_cows(self, num: int, breed: str, sim_days=5000) -> List[Cow]:
        heiferIIIs = self._init_heiferIIIs(num, breed)
        cows: List[Cow] = []

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

    def _init_replacement_cows(self, num: int, breed: str, sim_days=5000) -> List[Cow]:
        heiferIIIs = self._init_heiferIIIs(num, breed)
        replacement: List[Cow] = []

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
                    replacement.append(cow)
                    heiferIIIs.remove(heiferIII)
                    if len(replacement) == num:
                        break
                if len(replacement) == num:
                    break

        return replacement

    def get_calves(self, num, breed):
        self.calves += self._init_calves(num, breed)
        if self.order_by_random:
            shuffle(self.calves)
        return self.calves

    def get_heiferIs(self, num, breed):
        self.heiferIs += self._init_heiferIs(num, breed)

        if self.order_by_random:
            shuffle(self.heiferIs)

        return self.heiferIs

    def get_heiferIIs(self, num, breed):
        self.heiferIIs += self._init_heiferIIs(num, breed)

        if self.order_by_random:
            shuffle(self.heiferIIs)

        return self.heiferIIs

    def get_heiferIIIs(self, num, breed):
        self.heiferIIIs += self._init_heiferIIIs(num, breed)

        if self.order_by_random:
            shuffle(self.heiferIIIs)
        return self.heiferIIIs

    def get_cows(self, num, breed):
        self.cows += self._init_cows(num, breed)

        if self.order_by_random:
            shuffle(self.cows)
        return self.cows

    def get_replacement_cows(self, num, breed):
        self.replacement = self._init_replacement_cows(num, breed)

        if self.order_by_random:
            shuffle(self.replacement)
        return self.replacement

    def initialization_db_summary(self):
        """
        Returns: a dictionary which stores the summary of the initialization
        database
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
