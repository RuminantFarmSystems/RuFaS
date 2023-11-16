from typing import List, Dict

from tqdm import tqdm

from RUFAS.routines.animal.animal_typed_dicts import AnimalBaseInitArgsTypedDict
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII


class AnimalFactory:
    breed: str
    CI: int

    initial_animal_num: int
    simulation_days: int
    initial_animal_id: int
    animal_id: int

    save_animals: bool
    terminate_simulation_post_herd_generation: bool

    calves: List[Calf]
    heiferIs: List[HeiferI]
    heiferIIs: List[HeiferII]
    heiferIIIs: List[HeiferIII]
    cows: List[Cow]
    replacement: List[Cow]

    def __init__(self, breed: str, CI: int, initial_animal_num: int, simulation_days: int, initial_animal_id: int,
                 save_animals: bool = False, terminate_simulation_post_herd_generation: bool = False) -> None:
        self.breed = breed
        self.CI = CI
        self.initial_animal_num = initial_animal_num
        self.simulation_days = simulation_days
        self.initial_animal_id = initial_animal_id
        self.animal_id = initial_animal_id
        self.save_animals = save_animals
        self.terminate_simulation_post_herd_generation = terminate_simulation_post_herd_generation

        self.calves, self.heiferIs, self.heiferIIs, self.heiferIIIs, self.cows, self.replacement = [], [], [], [], [], \
                                                                                                   []

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

    def _calves_update(self) -> None:
        for calf in self.calves:
            wean_day = calf.update(0)
            if wean_day:
                args = calf.get_calf_values()
                args.update(id=self.next_id())

                heiferI = HeiferI(args)
                self.heiferIs.append(heiferI)
                self.calves.remove(calf)

    def _heiferIs_update(self) -> None:
        for heiferI in self.heiferIs:
            second_stage = heiferI.update(0)
            if second_stage:
                args = heiferI.get_heiferI_values()

                args.update(id=self.next_id())
                args.update(repro_program=AnimalBase.config['heifer_repro_method'])
                args.update(tai_method_h=AnimalBase.config['heifer_repro_programs']['heifer_TAI_protocol'])
                args.update(synch_ed_method_h=AnimalBase.config['heifer_repro_programs']['heifer_synchED_protocol'])

                heiferII = HeiferII(args)
                self.heiferIIs.append(heiferII)
                self.heiferIs.remove(heiferI)

    def _heiferIIs_update(self):
        for heiferII in self.heiferIIs:
            cull_stage, third_stage = heiferII.update(0)
            if cull_stage:
                self.heiferIIs.remove(heiferII)
            if third_stage:
                args = heiferII.get_heiferII_values()
                args.update(id=self.next_id())

                heiferIII = HeiferIII(args)
                self.heiferIIIs.append(heiferIII)
                self.heiferIIs.remove(heiferII)

    def _heiferIIIs_update(self, day: int) -> None:
        for heiferIII in self.heiferIIIs:
            cow_stage = heiferIII.update(0)
            if cow_stage:
                args = heiferIII.get_heiferIII_values()

                args.update(id=self.next_id())
                args.update(repro_program='TAI')
                args.update(presynch_method='PreSynch')
                args.update(tai_method_c='OvSynch 56')
                args.update(resynch_method='TAIafterPD')

                cow = Cow(args)

                self.cows.append(cow)
                if day >= 3000:
                    args.update(id=self.next_id())
                    replacement_cow = Cow(args)
                    self.replacement.append(replacement_cow)

                self.heiferIIIs.remove(heiferIII)

    def _cows_update(self):
        for cow in self.cows:
            _, _, _, culled, new_born = cow.update(0, self.CI)
            if culled or cow.calves > 4:
                self.cows.remove(cow)
            if new_born:
                args = AnimalBaseInitArgsTypedDict(id=self.next_id(),
                                                   breed=self.breed,
                                                   birth_date=0,
                                                   days_born=0,
                                                   p_init=cow.p_gest_for_calf,
                                                   birth_weight=cow.calf_birth_weight)
                cow.p_animal = cow.p_animal - cow.p_gest_for_calf + cow.p_growth + cow.dP_reserves
                cow.p_gest_for_calf = 0
                cow.calf_birth_weight = 0

                calf = Calf(args)
                if not (calf.culled or calf.sold):
                    self.calves.append(calf)

    def generate_animals(self) -> Dict[str, List[Calf | HeiferI | HeiferII | HeiferIII | Cow]]:
        for _ in range(self.initial_animal_num):
            args = AnimalBaseInitArgsTypedDict(id=self.next_id(),
                                               breed=self.breed,
                                               birth_date=0,
                                               days_born=0,
                                               p_init=0,
                                               birth_weight=0)
            calf = Calf(args)
            if not (calf.culled or calf.sold):
                self.calves.append(calf)

        for day in tqdm(range(self.simulation_days)):
            self._calves_update()
            self._heiferIs_update()
            self._heiferIIs_update()
            self._heiferIIIs_update(day=day)
            self._cows_update()

        if self.save_animals:
            pass
        if not self.terminate_simulation_post_herd_generation:
            return {"calves": self.calves, "heiferIs": self.heiferIs, "heiferIIs": self.heiferIIs,
                    "heiferIIIs": self.heiferIIIs, "cows": self.cows, "replacement_cows": self.replacement}
