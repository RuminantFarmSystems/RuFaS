"""
RUFAS: Ruminant Farm Systems Model
File name: life_cycle.py
Description: The class which manages the life cycle of the animals. This
    includes storing all information necessary for the simulation, initializing
    the herd to start the simulation at a steady state, updating the animals
    for each day, and providing end-of-simulation statistics and graphs.
Author(s): Manfei Li, mli497@wisc.edu
           Militsa Sotirova, militsasotirova@gmail.com
"""
from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Union

from RUFAS.routines.animal.animal_typed_dicts import AnimalConfigTypedDict, InitializationDBSummaryTypedDict
from RUFAS.routines.animal.life_cycle import animal_constants as const
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.life_cycle.animal_initialization import AnimalInitialization
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.util import Utility


class LifeCycleManager:
    """
    Manages the life cycles of the animals.
    """

    # The following class variables are used in HerdReport.
    num_cow_for_parity = {
        '1': 0,
        '2': 0,
        '3': 0,
        'greater_than_3': 0
    }
    avg_calving_to_preg_time = {
        '1': 0.0,
        '2': 0.0,
        '3': 0.0,
        'greater_than_3': 0.0
    }
    cull_reason_stats: Dict[str, int] = {
        const.DEATH_CULL: 0,
        const.LOW_PROD_CULL: 0,
        const.LAMENESS_CULL: 0,
        const.INJURY_CULL: 0,
        const.MASTITIS_CULL: 0,
        const.DISEASE_CULL: 0,
        const.UDDER_CULL: 0,
        const.UNKNOWN_CULL: 0
    }

    def __init__(self, data: AnimalConfigTypedDict):
        """
        Initializes the necessary configuration data.

        Args:
            data: life cycle data from the input JSON file

        """
        self.animal_config = data  # animal_config in animal_management
        self.avg_daily_cow_milking = 0.0
        self.initialize_db_summary: Optional[InitializationDBSummaryTypedDict] = None
        self.avg_CI = 0.0

        self.sold_heifers: List[HeiferIII] = []
        self.culled_heifers: List[HeiferII] = []
        self.culled_cows: List[Cow] = []

        self.herd_num = 0
        self.calf_num = 0
        self.heiferI_num = 0
        self.heiferII_num = 0
        self.heiferIII_num = 0
        self.cow_num = 0

        self.sold_calf_num = 0
        self.sold_heifer_num = 0
        self.bought_heifer_num = 0
        self.culled_heifer_num = 0
        self.culled_cow_num = 0

        self.calf_percent = 0.0
        self.heiferI_percent = 0.0
        self.heiferII_percent = 0.0
        self.heiferIII_percent = 0.0
        self.cow_percent = 0.0

        self.preg_check_num_h = 0
        self.preg_check_num = 0
        self.CIDR_count = 0
        self.GnRH_injection_num_h = 0
        self.PGF_injection_num_h = 0
        self.GnRH_injection_num = 0
        self.PGF_injection_num = 0

        self.ai_num_h = 0
        self.semen_num_h = 0
        self.ed_period_h = 0
        self.ai_num = 0
        self.semen_num = 0

        self.open_cow_num = 0
        self.preg_cow_num = 0
        self.vwp_cow_num = 0
        self.milking_cow_num = 0
        self.dry_cow_num = 0

        self.dry_cow_percent = 0.0
        self.milking_cow_percent = 0.0
        self.preg_cow_percent = 0.0
        self.non_preg_cow_percent = 0.0

        self.daily_milk_production = 0
        self.avg_days_in_milk = 0.0
        self.avg_days_in_preg = 0.0
        self.avg_cow_body_weight = 0.0
        self.avg_parity_num = 0.0

        self.avg_calving_interval = 0.0
        self.avg_breeding_to_preg_time = 0.0
        self.avg_heifer_culling_age = 0.0
        self.avg_cow_culling_age = 0.0
        self.avg_mature_body_weight = 0.0

        self.cull_reason_stats_range: Dict[str, int] = defaultdict(int)
        self.parity_culling_stats_range: Dict[Union[int, str], int] = defaultdict(int)

        self.avg_age_for_calving = {
            '1': 0.0,
            '2': 0.0,
            '3': 0.0,
            'greater_than_3': 0.0
        }
        self.avg_age_for_parity = {
            '1': 0.0,
            '2': 0.0,
            '3': 0.0,
            'greater_than_3': 0.0
        }
        self.cull_reason_stats_percent: Dict[str, float] = {
            const.DEATH_CULL: 0.0,
            const.LOW_PROD_CULL: 0.0,
            const.LAMENESS_CULL: 0.0,
            const.INJURY_CULL: 0.0,
            const.MASTITIS_CULL: 0.0,
            const.DISEASE_CULL: 0.0,
            const.UDDER_CULL: 0.0,
            const.UNKNOWN_CULL: 0.0
        }
        self.percent_cow_for_parity = {
            '1': 0.0,
            '2': 0.0,
            '3': 0.0,
            'greater_than_3': 0.0
        }

        self.replacement_market: List[Cow] = []
        self.animal_initializer: Optional[AnimalInitialization] = None

    # TODO: Annotate config after removing all the imports in all the __init__.py files
    # Currently, there are circular import errors lurking around
    def initialize_herd(self, herd_num: int, calf_num: int, heiferI_num: int, heiferII_num: int,
                        heiferIII_num: int, cow_num: int, replace_num: int, herd_init: bool, breed: str,
                        config) -> Tuple[List[Calf], List[HeiferI], List[HeiferII], List[HeiferIII], List[Cow]]:
        """
        Generates a replacement herd to simulate the market, for the herd to get
         replacements. Initializes the herd.

        Args:
            breed: TODO: needs description
            config: stores (among other things) information on whether the seed
                has been set by the user
            herd_init: boolean - true to populate database with new animals,
                false to use current database
            herd_num: what the number of cows should be maintained at
            calf_num: the number of calves to start the simulation with
            heiferI_num: the number of heiferIs to start the simulation with
            heiferII_num: the number of heiferIIs to start the simulation with
            heiferIII_num: the number of heiferIIIs to start the simulation with
            cow_num: the number of cows to start the simulation with
            replace_num: replacements in the market

        Returns:
            calves: list of calves for the simulation
            heiferIs: list of heiferIs for the simulation
            heiferIIs: list of heiferIIs for the simulation
            heiferIIIs: list of heiferIIIs for the simulation
            cows: list of cows for the simulation
        """
        self.animal_initializer = AnimalInitialization(self.animal_config['calving_interval'], breed,
                                                       config.set_seed, herd_init)
        self.herd_num = herd_num
        self._set_avg_CI(self.animal_config, self.animal_initializer)

        calves = self._get_calves(calf_num, breed, self.animal_initializer)
        heiferIs = self._get_heiferIs(heiferI_num, breed, self.animal_initializer)
        heiferIIs = self._get_heiferIIs(heiferII_num, breed, self.animal_initializer)
        heiferIIIs = self._get_heiferIIIs(heiferIII_num, breed, self.animal_initializer)
        cows = self._get_cows(cow_num, breed, self.animal_initializer)

        self.replacement_market = self.animal_initializer.get_replacement_cows(replace_num, breed)

        return calves, heiferIs, heiferIIs, heiferIIIs, cows

    # TODO: In the animal_management_animal.json,
    #  the user_input_calving_interval attribute is set to false while the
    #  calving_interval attribute is present, maybe set that to true instead?
    def _set_avg_CI(self, animal_config: AnimalConfigTypedDict,
                    animal_initializer: AnimalInitialization) -> None:
        if animal_config['user_input_calving_interval']:
            self.avg_CI = animal_config['calving_interval']
        else:
            self.initialize_db_summary = animal_initializer.initialization_db_summary()
            self.avg_CI = self.initialize_db_summary['cow_avg_CI']

    @staticmethod
    def _get_calves(calf_num: int, breed: str, animal_initializer: AnimalInitialization) -> List[Calf]:
        calves = animal_initializer.get_calves(calf_num, breed)
        for calf in calves:
            calf.events.add_event(calf.days_born, 0, const.INIT_HERD)
        return calves

    @staticmethod
    def _get_heiferIs(heiferI_num: int, breed: str, animal_initializer) -> List[HeiferI]:
        heiferIs = animal_initializer.get_heiferIs(heiferI_num, breed)
        for heiferI in heiferIs:
            heiferI.events.add_event(heiferI.days_born, 0, const.INIT_HERD)
        return heiferIs

    @staticmethod
    def _get_heiferIIs(heiferII_num: int, breed: str, animal_initializer: AnimalInitialization) -> List[HeiferII]:
        heiferIIs = animal_initializer.get_heiferIIs(heiferII_num, breed)
        for heiferII in heiferIIs:
            heiferII.events.add_event(heiferII.days_born, 0, const.INIT_HERD)
        return heiferIIs

    @staticmethod
    def _get_heiferIIIs(heiferIII_num: int, breed: str, animal_initializer: AnimalInitialization) -> List[HeiferIII]:
        heiferIIIs = animal_initializer.get_heiferIIIs(heiferIII_num, breed)
        for heiferIII in heiferIIIs:
            heiferIII.events.add_event(heiferIII.days_born, 0, const.INIT_HERD)
        return heiferIIIs

    @staticmethod
    def _get_cows(cow_num: int, breed: str, animal_initializer: AnimalInitialization) -> List[Cow]:
        cows = animal_initializer.get_cows(cow_num, breed)
        for cow in cows:
            cow.events.add_event(cow.days_born, 0, const.INIT_HERD)
        return cows

    def daily_update(self, sim_day: int, calves: List[Calf], heiferIs: List[HeiferI],
                     heiferIIs: List[HeiferII], heiferIIIs: List[HeiferIII], cows: List[Cow]) \
            -> Tuple[List[Cow], List[int], List[Calf], List[Calf],
                     List[HeiferI], List[HeiferII], List[HeiferIII], List[Cow]]:
        """
        Updates the status of the animals.

        Args:
            cows: list of Cow objects to be updated
            heiferIIIs: list of HeiferIII objects to be updated
            heiferIIs: list of HeiferII objects to be updated
            heiferIs: list of HeiferI objects to be updated
            calves: list of Calf objects to be updated
            sim_day: day number

        Returns:
            animals_added: list of animals added from replacement herd
            ids_removed: list of animal ids that were removed during this day
            calves_born: list of calves that were born during this day
            calves: updated list of calves
            heiferIs: updated list of heiferIs
            heiferIIs: updated list of heiferIIs
            heiferIIIs: updated list of heiferIIIs
            cows: updated list of cows

        """
        ids_removed: List[int] = []
        animals_added: List[Cow] = []
        calves_born: List[Calf] = []
        total_animal_num = 0
        preg_heifer_num = 0  # TODO: Seems unused after calculation

        self._reset_parity()
        self._reset_cull_reason_stats()

        total_animal_num = self._calf_to_heiferI(sim_day, calves, heiferIs, total_animal_num)
        total_animal_num = self._heiferI_to_heiferII(sim_day, heiferIs, heiferIIs, total_animal_num)
        total_animal_num, preg_heifer_num = self._heiferII_to_heiferIII(sim_day, heiferIIs, heiferIIIs,
                                                                        preg_heifer_num, total_animal_num)
        total_animal_num = self._heiferIII_to_cow(sim_day, heiferIIIs, cows, total_animal_num)

        self._check_if_heifers_need_to_be_sold(heiferIIIs, cows, ids_removed)
        self._check_if_replacement_heifers_needed(sim_day, heiferIIIs, cows, animals_added)

        total_animal_num = self._cull_cows_and_record_stats(sim_day, cows, calves_born,
                                                            ids_removed, total_animal_num)

        self._calc_herd_percentages(total_animal_num)
        self._calc_cow_percentages()
        self._calc_cull_reason_stats_percent()
        self._calc_percent_cow_per_parity()

        return animals_added, ids_removed, calves_born, calves, heiferIs, \
               heiferIIs, heiferIIIs, cows

    def _reset_parity(self) -> None:
        for parity in LifeCycleManager.num_cow_for_parity:
            LifeCycleManager.num_cow_for_parity[parity] = 0
            LifeCycleManager.avg_calving_to_preg_time[parity] = 0
            self.percent_cow_for_parity[parity] = 0.0
            self.avg_age_for_parity[parity] = 0.0
            self.avg_age_for_calving[parity] = 0.0

    def _reset_cull_reason_stats(self) -> None:
        for cull_reason in LifeCycleManager.cull_reason_stats:
            LifeCycleManager.cull_reason_stats[cull_reason] = 0
            self.cull_reason_stats_percent[cull_reason] = 0.0

    def _calf_to_heiferI(self, sim_day: int, calves: List[Calf],
                         heiferIs: List[HeiferI], total_animal_num: int) -> int:
        removed_calves_idx: List[int] = []

        for idx, calf in enumerate(calves):
            wean_day = calf.update(sim_day)
            if wean_day:
                self._wean_calf(calf, heiferIs)
                removed_calves_idx.append(idx)
            else:
                self.calf_num += 1
                temp = Utility.calc_average(total_animal_num, self.avg_mature_body_weight,
                                            calf.mature_body_weight)
                total_animal_num, self.avg_mature_body_weight = temp

        Utility.remove_items_from_list_by_indices(calves, removed_calves_idx)
        return total_animal_num

    @staticmethod
    def _wean_calf(calf: Calf, heiferIs: List[HeiferI]) -> None:
        args = calf.get_calf_values()
        args.update({
            'body_weight_history': calf.body_weight_history,
            'pen_history': calf.pen_history
        })
        new_heiferI = HeiferI(args)
        heiferIs.append(new_heiferI)

    def _heiferI_to_heiferII(self, sim_day: int, heiferIs: List[HeiferI], heiferIIs: List[HeiferII],
                             total_animal_num: int) -> int:
        removed_heiferIs_idx: List[int] = []

        for idx, heiferI in enumerate(heiferIs):
            second_stage = heiferI.update(sim_day)
            if second_stage:
                self._move_heiferI_to_second_stage(heiferI, heiferIIs)
                removed_heiferIs_idx.append(idx)
            else:
                self.heiferI_num += 1
                temp = Utility.calc_average(total_animal_num, self.avg_mature_body_weight, heiferI.mature_body_weight)
                total_animal_num, self.avg_mature_body_weight = temp

        Utility.remove_items_from_list_by_indices(heiferIs, removed_heiferIs_idx)
        return total_animal_num

    @staticmethod
    def _move_heiferI_to_second_stage(heiferI: HeiferI, heiferIIs: List[HeiferII]) -> None:
        args = heiferI.get_heiferI_values()
        args.update({
            'body_weight_history': heiferI.body_weight_history,
            'pen_history': heiferI.pen_history
        })
        args.update(repro_program=AnimalBase.config['heifer_repro_method'])
        args.update(tai_method_h=AnimalBase.config['heifer_TAI_protocol'])
        args.update(synch_ed_method_h=AnimalBase.config['heifer_synchED_protocol'])
        new_heiferII = HeiferII(args)
        heiferIIs.append(new_heiferII)

    def _heiferII_to_heiferIII(self, sim_day: int, heiferIIs: List[HeiferII],
                               heiferIIIs: List[HeiferIII], preg_heifer_num: int,
                               total_animal_num: int) -> Tuple[int, int]:
        removed_heiferIIs_idx: List[int] = []

        for idx, heiferII in enumerate(heiferIIs):
            cull_stage, third_stage = heiferII.update(sim_day)
            if cull_stage:
                temp = Utility.calc_average(self.culled_heifer_num, self.avg_heifer_culling_age, heiferII.days_born)
                self.culled_heifer_num, self.avg_heifer_culling_age = temp
                self.culled_heifers.append(heiferII)
                removed_heiferIIs_idx.append(idx)
            elif third_stage:
                self._move_heiferII_to_third_stage(heiferII, heiferIIIs)
                removed_heiferIIs_idx.append(idx)
            else:
                total_animal_num, preg_heifer_num = \
                    self._keep_heiferII_as_is(heiferII, total_animal_num, preg_heifer_num)

        Utility.remove_items_from_list_by_indices(heiferIIs, removed_heiferIIs_idx)
        return total_animal_num, preg_heifer_num

    @staticmethod
    def _move_heiferII_to_third_stage(heiferII: HeiferII, heiferIIIs: List[HeiferIII]) -> None:
        args = heiferII.get_heiferII_values()
        args.update({
            'body_weight_history': heiferII.body_weight_history,
            'pen_history': heiferII.pen_history,
            'conceptus_weight': heiferII.conceptus_weight,
            'calf_birth_weight': heiferII.calf_birth_weight
        })
        new_heiferIII = HeiferIII(args)
        heiferIIIs.append(new_heiferIII)

    def _keep_heiferII_as_is(self, heiferII: HeiferII, total_animal_num: int, preg_heifer_num: int):
        self.heiferII_num += 1
        temp = Utility.calc_average(total_animal_num, self.avg_mature_body_weight,
                                    heiferII.mature_body_weight)
        total_animal_num, self.avg_mature_body_weight = temp
        if heiferII.breeding_to_preg_time != 0:
            temp2 = Utility.calc_average(preg_heifer_num, self.avg_breeding_to_preg_time,
                                         heiferII.breeding_to_preg_time)
            preg_heifer_num, self.avg_breeding_to_preg_time = temp2
        self._extract_repro_stats_from_heiferII(heiferII)
        return total_animal_num, preg_heifer_num

    def _extract_repro_stats_from_heiferII(self, heiferII: HeiferII) -> None:
        self.CIDR_count += heiferII.CIDR_count
        self.GnRH_injection_num_h += heiferII.GnRH_injections
        self.PGF_injection_num_h += heiferII.PGF_injections
        self.preg_check_num_h += heiferII.preg_diagnoses
        self.semen_num_h += heiferII.semen_num
        self.ai_num_h += heiferII.AI_times
        self.ed_period_h += heiferII.ED_days

    def _heiferIII_to_cow(self, sim_day: int, heiferIIIs: List[HeiferIII], cows: List[Cow],
                          total_animal_num: int) -> int:
        removed_heiferIIIs_idx: List[int] = []

        for idx, heiferIII in enumerate(heiferIIIs):
            # # TODO why can cows be added to the list of HeiferIII's so that the
            # #  following if statement is necessary?
            # if type(heiferIII) is HeiferIII:
            #     cow_stage = heiferIII.update(simulation_day)
            # else:
            #     cow_stage = heiferIII.update(simulation_day, self.avg_CI)
            cow_stage = heiferIII.update(sim_day)
            if cow_stage:
                self._move_heiferIII_to_cow_stage(heiferIII, cows)
                removed_heiferIIIs_idx.append(idx)
            else:
                self.heiferIII_num += 1
                temp = Utility.calc_average(total_animal_num, self.avg_mature_body_weight,
                                            heiferIII.mature_body_weight)
                total_animal_num, self.avg_mature_body_weight = temp

        Utility.remove_items_from_list_by_indices(heiferIIIs, removed_heiferIIIs_idx)
        return total_animal_num

    @staticmethod
    def _move_heiferIII_to_cow_stage(heiferIII, cows):
        args = heiferIII.get_heiferIII_values()
        args.update({
            'body_weight_history': heiferIII.body_weight_history,
            'pen_history': heiferIII.pen_history,
            'conceptus_weight': heiferIII.conceptus_weight,
            'calf_birth_weight': heiferIII.calf_birth_weight
        })
        args.update(repro_program=AnimalBase.config['cow_repro_method'])
        args.update(presynch_method=AnimalBase.config['cow_presynch_protocol'])
        args.update(tai_method_c=AnimalBase.config['cow_TAI_protocol'])
        args.update(resynch_method=AnimalBase.config['cow_resynch_protocol'])
        new_cow = Cow(args)
        cows.append(new_cow)

    def _check_if_heifers_need_to_be_sold(self, heiferIIIs: List[HeiferIII], cows: List[Cow],
                                          ids_removed: List[int]) -> None:
        # if the number of heifers is more than needed for the herd,
        # sell those as replacement
        ratio = 1.03  # TODO: use a better name
        while len(heiferIIIs) + len(cows) > self.herd_num * ratio and len(heiferIIIs) > 0:
            removed = heiferIIIs.pop()
            ids_removed.append(removed.id)
            self.sold_heifers.append(removed)
            self.sold_heifer_num += 1

    def _check_if_replacement_heifers_needed(self, sim_day: int, heiferIIIs: List[HeiferIII], cows: List[Cow],
                                             animals_added: List[Cow]) -> None:
        # if the number of heifers is less than needed for the herd,
        # buy replacement from the market
        ratio = 1.01  # TODO: use a better name
        while len(cows) + len(heiferIIIs) + self.bought_heifer_num < self.herd_num * ratio \
                and sim_day > 1:
            # TODO: Does it matter whether we are removing first (.pop(0)) or last (.pop()) replacement cow?
            # .pop() is more efficient than .pop(0)
            replacement = self.replacement_market.pop(0)
            replacement.events.add_event(replacement.days_born, sim_day, const.ENTER_HERD)
            replacement.set_p_purchased()
            animals_added.append(replacement)
            self.bought_heifer_num += 1

    def _cull_cows_and_record_stats(self, sim_day: int, cows: List[Cow], calves_born: List[Calf],
                                    ids_removed: List[int], total_animal_num: int) -> int:
        calving_interval_avail_num = 0
        calving_age_avail_num = {
            '1': 0,
            '2': 0,
            '3': 0,
            'greater_than_3': 0
        }
        calf_to_preg_time_avail_num = {
            '1': 0,
            '2': 0,
            '3': 0,
            'greater_than_3': 0
        }
        removed_cows_idx: List[int] = []

        # cow culling action and stats
        for index, cow in enumerate(cows):
            _, _, _, culled, new_born = cow.update(sim_day, self.avg_CI)

            # culled cows, calculate slaughter value and record culling reasons
            if culled:
                self._cull_cow(cow)
                ids_removed.append(cow.id)
                removed_cows_idx.append(index)
            else:
                total_animal_num = self._handle_cow_body_weight(cow, total_animal_num)
                self._handle_cow_milking(cow)
                self._handle_cow_days_in_milk(cow)
                self._handle_cow_days_in_preg(cow)
                self._handle_cow_calves(cow, calving_age_avail_num, calf_to_preg_time_avail_num)
                calving_interval_avail_num = self._handle_cow_ci(cow, calving_interval_avail_num)
                self._extract_repro_stats_from_cow(cow)

            if new_born:
                self._handle_new_born(sim_day, cow, calves_born)

        Utility.remove_items_from_list_by_indices(cows, removed_cows_idx)
        return total_animal_num

    def _cull_cow(self, cow: Cow) -> None:
        self.culled_cows.append(cow)
        self.cull_reason_stats_range[cow.cull_reason] += 1
        LifeCycleManager.cull_reason_stats[cow.cull_reason] += 1

        parity = cow.calves if cow.calves <= 3 else '4+'
        self.parity_culling_stats_range[parity] += 1

        temp = Utility.calc_average(self.culled_cow_num, self.avg_cow_culling_age, cow.days_born)
        self.culled_cow_num, self.avg_cow_culling_age = temp

    def _handle_cow_body_weight(self, cow: Cow, total_animal_num: int) -> int:
        _, self.avg_cow_body_weight = Utility.calc_average(
                self.cow_num, self.avg_cow_body_weight, cow.body_weight)
        self.cow_num, self.avg_parity_num = Utility.calc_average(
                self.cow_num, self.avg_parity_num, cow.calves)

        temp = Utility.calc_average(total_animal_num, self.avg_mature_body_weight, cow.mature_body_weight)
        total_animal_num, self.avg_mature_body_weight = temp
        return total_animal_num

    def _handle_cow_milking(self, cow: Cow) -> None:
        if cow.milking:
            self.daily_milk_production += cow.estimated_daily_milk_produced
            temp = Utility.calc_average(self.milking_cow_num, self.avg_days_in_milk, cow.days_in_milk)
            self.milking_cow_num, self.avg_days_in_milk = temp
        else:
            self.dry_cow_num += 1

    def _handle_cow_days_in_milk(self, cow: Cow) -> None:
        if cow.days_in_milk < self.animal_config['voluntary_waiting_period']:
            self.vwp_cow_num += 1
            if cow.days_in_preg == 0:
                self.open_cow_num += 1

    def _handle_cow_days_in_preg(self, cow: Cow) -> None:
        if cow.days_in_preg > 0:
            temp = Utility.calc_average(self.preg_cow_num, self.avg_days_in_preg, cow.days_in_preg)
            self.preg_cow_num, self.avg_days_in_preg = temp

    def _handle_cow_calves(self, cow: Cow, calving_age_avail_num, calf_to_preg_time_avail_num) -> None:
        if 0 < cow.calves <= 3:
            key = str(cow.calves)
        else:
            key = 'greater_than_3'

        parity_counts = LifeCycleManager.num_cow_for_parity
        temp = Utility.calc_average(parity_counts[key], self.avg_age_for_parity[key], cow.days_born)
        parity_counts[key], self.avg_age_for_parity[key] = temp

        calving_age = cow.events.get_most_recent_date(const.NEW_BIRTH)
        if calving_age != -1:
            temp2 = Utility.calc_average(calving_age_avail_num[key], self.avg_age_for_calving[key], calving_age)
            calving_age_avail_num[key], self.avg_age_for_calving[key] = temp2

        if cow.calving_to_preg_time != 0:
            avg_times = LifeCycleManager.avg_calving_to_preg_time
            temp3 = Utility.calc_average(calf_to_preg_time_avail_num[key], avg_times[key], cow.calving_to_preg_time)
            calf_to_preg_time_avail_num[key], avg_times[key] = temp3

    def _handle_cow_ci(self, cow: Cow, calving_interval_avail_num: int) -> int:
        if cow.CI != 0:
            temp = Utility.calc_average(calving_interval_avail_num, self.avg_calving_interval, cow.CI)
            calving_interval_avail_num, self.avg_calving_interval = temp
        return calving_interval_avail_num

    def _extract_repro_stats_from_cow(self, cow: Cow) -> None:
        self.GnRH_injection_num += cow.GnRH_injections
        self.PGF_injection_num += cow.PGF_injections
        self.preg_check_num += cow.preg_diagnoses
        self.semen_num += cow.semen_num
        self.ai_num += cow.AI_times

    def _handle_new_born(self, sim_day: int, cow: Cow, calves_born: List[Calf]) -> None:
        args = {
            'id': self.animal_initializer.next_id(),
            'breed': 'HO',
            'birth_date': sim_day,
            'days_born': 0,
            'p_init': cow.p_gest_for_calf,
            'birth_weight': cow.calf_birth_weight
        }
        # at parturition, the sum of P absorbed for gestation rqmts is
        # subtracted from the animal value. the sum of P absorbed for
        # gestation is equal to the initial animal P value for the calf
        # (A.1G.A.4)
        cow.p_animal = cow.p_animal - cow.p_gest_for_calf + \
                       cow.p_growth + cow.dP_reserves
        new_calf = Calf(args)
        cow.p_gest_for_calf = 0
        cow.calf_birth_weight = 0
        if not (new_calf.culled or new_calf.sold):
            new_calf.events.add_event(new_calf.days_born, sim_day, const.ENTER_HERD)
            # calves.append(new_calf)
            calves_born.append(new_calf)
        if new_calf.sold:
            self.sold_calf_num += 1

    def _calc_herd_percentages(self, total_animal_num: int) -> None:
        """
        Calculate percentage of each animal class in the herd

        Args:
            total_animal_num:

        Returns:

        """

        if total_animal_num == 0:
            self.calf_percent = 0.0
            self.heiferI_percent = 0.0
            self.heiferII_percent = 0.0
            self.heiferIII_percent = 0.0
            self.cow_percent = 0.0
        else:
            pc = Utility.percent_calculator(denominator=total_animal_num)
            self.calf_percent = pc(self.calf_num)
            self.heiferI_percent = pc(self.heiferI_num)
            self.heiferII_percent = pc(self.heiferII_num)
            self.heiferIII_percent = pc(self.heiferIII_num)
            self.cow_percent = pc(self.cow_num)

    def _calc_cow_percentages(self) -> None:
        """
        Calculate percentages of different kinds of cows

        Returns:

        """

        if self.cow_num == 0:
            self.dry_cow_percent = 0.0
            self.milking_cow_percent = 0.0
            self.preg_cow_percent = 0.0
            self.non_preg_cow_percent = 0.0
        else:
            pc = Utility.percent_calculator(denominator=self.cow_num)
            self.dry_cow_percent = pc(self.dry_cow_num)
            self.milking_cow_percent = pc(self.milking_cow_num)
            self.preg_cow_percent = pc(self.preg_cow_num)
            self.non_preg_cow_percent = pc(self.open_cow_num + self.vwp_cow_num)

    def _calc_cull_reason_stats_percent(self) -> None:
        """
        Calculate the percentage of culled cows for each cull reason

        Returns:

        """

        for cull_reason in LifeCycleManager.cull_reason_stats:
            if self.culled_cow_num != 0:
                cow_frac = LifeCycleManager.cull_reason_stats[cull_reason] / self.culled_cow_num
                self.cull_reason_stats_percent[cull_reason] = cow_frac * 100

    def _calc_percent_cow_per_parity(self) -> None:
        """
        Calculate the percentage of cows for each parity number

        Returns:

        """

        for parity in LifeCycleManager.num_cow_for_parity:
            if self.cow_num == 0:
                self.percent_cow_for_parity[parity] = 0.0
            else:
                cow_frac = LifeCycleManager.num_cow_for_parity[parity] / self.cow_num
                self.percent_cow_for_parity[parity] = cow_frac * 100
