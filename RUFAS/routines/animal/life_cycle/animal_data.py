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
    animal_id = 378165

    breed: str
    calf_num: int
    heiferI_num: int
    heiferII_num: int
    heiferIII_num: int
    cow_num: int
    replace_num: int

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

    def __init__(self, CI, herd_data: HerdInfoTypedDict, set_seed):
        self.CI = CI
        self.breed = herd_data['breed']
        self.order_by_random = not set_seed
        self.init = herd_data['herd_init']

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
        self._init_calves(self.calf_num, self.breed)
        self._init_heiferIs(self.heiferI_num, self.breed)
        self._init_heiferIIs(self.heiferII_num, self.breed)
        self._init_heiferIIIs(self.heiferIII_num, self.breed)
        self._init_cows(self.cow_num, self.breed)
        self._init_replacement_cows(self.replace_num, self.breed)

    def _get_args_list(self, data: Dict[str, List[Any]], args_properties: List[str], num: int) -> \
            List[Dict[str, Any]]:
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
        current_num_calves = len(self.calves)

        if current_num_calves >= num:
            return

        if self.init:
            self.calves += self._init_calves_from_simulation(num - current_num_calves, breed)

        else:
            if current_num_calves + self.num_calves_in_data < num:
                self.calves += self._init_calves_from_data(self.num_calves_in_data)
                self.calves += self._init_calves_from_simulation(num - current_num_calves - self.num_calves_in_data,
                                                                 breed)
            else:
                self.calves += self._init_calves_from_data(num - current_num_calves)

    def _init_calves_from_simulation(self, num: int, breed: str) -> List[Calf]:
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
        current_num_heiferIs = len(self.heiferIs)

        if current_num_heiferIs >= num:
            return

        if self.init:
            self.heiferIs += self._init_heiferIs_from_simulation(num - current_num_heiferIs, breed)

        else:
            if current_num_heiferIs + self.num_heiferIs_in_data < num:
                self.heiferIs += self._init_heiferIs_from_data(self.num_heiferIs_in_data)
                self.heiferIs += self._init_heiferIs_from_simulation(
                    num - current_num_heiferIs - self.num_heiferIs_in_data, breed)
            else:
                self.heiferIs += self._init_heiferIs_from_data(num - current_num_heiferIs)

    def _init_heiferIs_from_simulation(self, num: int, breed: str, sim_days=5000) -> List[HeiferI]:
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
        current_num_heiferIIs = len(self.heiferIIs)

        if current_num_heiferIIs >= num:
            return

        if self.init:
            self.heiferIIs += self._init_heiferIIs_from_simulation(num - current_num_heiferIIs, breed)

        else:
            if current_num_heiferIIs + self.num_heiferIIs_in_data < num:
                self.heiferIIs += self._init_heiferIIs_from_data(self.num_heiferIIs_in_data)
                self.heiferIIs += self._init_heiferIIs_from_simulation(
                    num - current_num_heiferIIs - self.num_heiferIIs_in_data, breed)
            else:
                self.heiferIIs += self._init_heiferIIs_from_data(num - current_num_heiferIIs)

    def _init_heiferIIs_from_simulation(self, num: int, breed: str, sim_days=5000) -> List[HeiferII]:
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
                    args.update(synch_ed_method_h=AnimalBase.config['heifer_repro_programs']
                    ['heifer_synchED_protocol'])

                    heiferII = HeiferII(args)
                    heiferIIs.append(heiferII)
                    heiferIs.remove(heiferI)
                    if len(heiferIIs) == num:
                        break
                if len(heiferIIs) == num:
                    break

        return heiferIIs

    def _init_heiferIIs_from_data(self, num: int) -> List[HeiferII]:
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
        current_num_heiferIIIs = len(self.heiferIIIs)

        if current_num_heiferIIIs >= num:
            return

        if self.init:
            self.heiferIIIs += self._init_heiferIIIs_from_simulation(num - current_num_heiferIIIs, breed)

        else:
            if current_num_heiferIIIs + self.num_heiferIIIs_in_data < num:
                self.heiferIIIs += self._init_heiferIIIs_from_data(self.num_heiferIIIs_in_data)
                self.heiferIIIs += self._init_heiferIIIs_from_simulation(
                    num - current_num_heiferIIIs - self.num_heiferIIIs_in_data, breed)
            else:
                self.heiferIIIs += self._init_heiferIIIs_from_data(num - current_num_heiferIIIs)

    def _init_heiferIIIs_from_simulation(self, num: int, breed: str, sim_days=5000) -> List[HeiferIII]:
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
        current_num_cows = len(self.cows)

        if current_num_cows >= num:
            return

        if self.init:
            self.cows += self._init_cows_from_simulation(num - current_num_cows, breed)

        else:
            if current_num_cows + self.num_cows_in_data < num:
                self.cows += self._init_cows_from_data(self.num_cows_in_data)
                self.cows += self._init_cows_from_simulation(num - current_num_cows - self.num_cows_in_data, breed)
            else:
                self.cows += self._init_cows_from_data(num - current_num_cows)

    def _init_cows_from_simulation(self, num: int, breed: str, sim_days=5000) -> List[Cow]:
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
        current_num_replacement_cows = len(self.replacement)

        if current_num_replacement_cows >= num:
            return

        if self.init:
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
        self._init_calves(num, breed)
        if self.order_by_random:
            shuffle(self.calves)
        return self.calves

    def get_heiferIs(self, num, breed):
        self._init_heiferIs(num, breed)

        if self.order_by_random:
            shuffle(self.heiferIs)

        return self.heiferIs

    def get_heiferIIs(self, num, breed):
        self._init_heiferIIs(num, breed)

        if self.order_by_random:
            shuffle(self.heiferIIs)

        return self.heiferIIs

    def get_heiferIIIs(self, num, breed):
        self._init_heiferIIIs(num, breed)

        if self.order_by_random:
            shuffle(self.heiferIIIs)
        return self.heiferIIIs

    def get_cows(self, num, breed):
        self._init_cows(num, breed)

        if self.order_by_random:
            shuffle(self.cows)
        return self.cows

    def get_replacement_cows(self, num, breed):
        self._init_replacement_cows(num, breed)

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
