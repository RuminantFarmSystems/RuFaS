from collections import defaultdict
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union

from RUFAS.input_manager import InputManager
from RUFAS.output_manager import OutputManager
from RUFAS.routines.animal.animal_typed_dicts import AnimalConfigTypedDict, HerdInfoTypedDict, \
    InitialHerdSummaryTypedDict
from RUFAS.routines.animal.life_cycle import animal_constants
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.life_cycle.animal_population import AnimalPopulation

from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.life_cycle.repro_protocol_enums import HeiferReproProtocolEnum
from RUFAS.util import Utility

# GenericAnimal is a placeholder/generic type that represents any of the five classes listed in the union.
# 'bound' is used to restrict the type to only the classes listed in the union.
GenericAnimal = TypeVar("GenericAnimal", bound=Union[Calf, HeiferI, HeiferII, HeiferIII, Cow])

im = InputManager()
om = OutputManager()


class LifeCycleManager:
    """
    Manages the life cycles of the animals.
    """

    def __init__(self, data: AnimalConfigTypedDict):
        """
        Initializes the necessary configuration data.

        Args:
            data: life cycle data from the input JSON file

        """
        self.avg_calving_to_preg_time = {'1': 0.0,
                                         '2': 0.0,
                                         '3': 0.0,
                                         'greater_than_3': 0.0
                                         }
        self.cull_reason_stats: Dict[str, int] = {animal_constants.DEATH_CULL: 0,
                                                  animal_constants.LOW_PROD_CULL: 0,
                                                  animal_constants.LAMENESS_CULL: 0,
                                                  animal_constants.INJURY_CULL: 0,
                                                  animal_constants.MASTITIS_CULL: 0,
                                                  animal_constants.DISEASE_CULL: 0,
                                                  animal_constants.UDDER_CULL: 0,
                                                  animal_constants.UNKNOWN_CULL: 0
                                                  }
        self.num_cow_for_parity = {'1': 0,
                                   '2': 0,
                                   '3': 0,
                                   'greater_than_3': 0
                                   }
        self.animal_config = data  # animal_config in animal_management
        self.avg_daily_cow_milking = 0.0
        self.initial_herd_summary: Optional[InitialHerdSummaryTypedDict] = None
        self.avg_CI = 0.0

        self.sold_heiferIIIs: List[HeiferIII] = []
        self.sold_heiferIIs: List[HeiferII] = []
        self.sold_and_died_cows: List[Cow] = []

        self.herd_num = 0
        self.calf_num = 0
        self.heiferI_num = 0
        self.heiferII_num = 0
        self.heiferIII_num = 0
        self.cow_num = 0

        self.sold_calf_num = 0
        self.sold_heiferIII_oversupply_num = 0
        self.bought_heifer_num = 0
        self.sold_heiferII_num = 0
        self.cow_herd_exit_num = 0

        self.calf_percent = 0.0
        self.heiferI_percent = 0.0
        self.heiferII_percent = 0.0
        self.heiferIII_percent = 0.0
        self.cow_percent = 0.0

        self.preg_check_num_h = 0
        self.preg_check_num = 0
        self.CIDR_count = 0
        self.GnRH_injection_num_h = 0
        self.GnRH_injection_num = 0
        self.PGF_injection_num_h = 0
        self.PGF_injection_num = 0

        self.ai_num_h = 0
        self.ai_num = 0
        self.semen_num_h = 0
        self.semen_num = 0
        self.ed_period_h = 0

        self.open_cow_num = 0
        self.preg_cow_num = 0
        self.vwp_cow_num = 0
        self.milking_cow_num = 0
        self.dry_cow_num = 0

        self.dry_cow_percent = 0.0
        self.milking_cow_percent = 0.0
        self.preg_cow_percent = 0.0
        self.non_preg_cow_percent = 0.0

        self.daily_milk_production = 0.0
        self.herd_milk_fat_kg = 0.0
        self.herd_milk_fat_percent = 0.0
        self.herd_milk_protein_kg = 0.0
        self.herd_milk_protein_percent = 0.0
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
            animal_constants.DEATH_CULL: 0.0,
            animal_constants.LOW_PROD_CULL: 0.0,
            animal_constants.LAMENESS_CULL: 0.0,
            animal_constants.INJURY_CULL: 0.0,
            animal_constants.MASTITIS_CULL: 0.0,
            animal_constants.DISEASE_CULL: 0.0,
            animal_constants.UDDER_CULL: 0.0,
            animal_constants.UNKNOWN_CULL: 0.0
        }
        self.percent_cow_for_parity = {
            '1': 0.0,
            '2': 0.0,
            '3': 0.0,
            'greater_than_3': 0.0
        }

        self.replacement_market: List[Cow] = []
        self.animal_population: Optional[AnimalPopulation] = None

    # TODO: Annotate config after removing all the imports in all the __init__.py files
    def initialize_herd(self, herd_data: HerdInfoTypedDict) -> Tuple[List[Calf], List[HeiferI],
                                                                     List[HeiferII], List[HeiferIII],
                                                                     List[Cow]]:
        """Generates a replacement herd to simulate the market, for the herd to get replacements.

        Parameters
        ----------
        herd_data : HerdInfoTypedDict
            The data for the herd to be initialized

        Returns
        -------
        Tuple[List[Calf], List[HeiferI], List[HeiferII], List[HeiferIII], List[Cow]]
            A tuple of animal lists for the calves, heiferIs, heiferIIs, heiferIIIs, and cows

        """
        animal_population = im.get_data("runtime_animal_population")
        self.animal_population = AnimalPopulation(
            calves=list(map(Calf, animal_population["calves"])),
            heiferIs=list(map(HeiferI, animal_population["heiferIs"])),
            heiferIIs=list(map(HeiferII, animal_population["heiferIIs"])),
            heiferIIIs=list(map(HeiferIII, animal_population["heiferIIIs"])),
            cows=list(map(Cow, animal_population["cows"])),
            replacement=list(map(Cow, animal_population["replacement"]))
        )
        self.herd_num = herd_data['herd_num']
        self._set_avg_CI()

        calves = self._get_animals(Calf)
        heiferIs = self._get_animals(HeiferI)
        heiferIIs = self._get_animals(HeiferII)
        heiferIIIs = self._get_animals(HeiferIII)
        cows = self._get_animals(Cow)
        self.replacement_market = self.animal_population.get_replacement_cows()
        return calves, heiferIs, heiferIIs, heiferIIIs, cows

    def _set_avg_CI(self) -> None:
        if 'use_input_calving_interval' in self.animal_config and self.animal_config['use_input_calving_interval']:
            self.avg_CI = self.animal_config['calving_interval']
        else:
            self.initial_herd_summary = self.animal_population.get_herd_summary()
            self.avg_CI = self.initial_herd_summary['cow_avg_CI']

    def _get_animals(self, animal_type: Type[GenericAnimal]) -> List[GenericAnimal]:
        """Gets a list of animals of a given type.

        Parameters
        ----------
        animal_type : Type[GenericAnimal]
            The type of animal to get.

        Returns
        -------
            A list of animals of the given type.

        """
        animal_getter_by_animal_type: Dict[Type[GenericAnimal], Callable[..., List[GenericAnimal]]] = {
            Calf: self.animal_population.get_calves,
            HeiferI: self.animal_population.get_heiferIs,
            HeiferII: self.animal_population.get_heiferIIs,
            HeiferIII: self.animal_population.get_heiferIIIs,
            Cow: self.animal_population.get_cows
        }
        animals = animal_getter_by_animal_type[animal_type]()
        for animal in animals:
            animal.events.add_event(animal.days_born, 0, animal_constants.INIT_HERD)
        return animals

    def daily_update(self, sim_day: int,
                     calves: List[Calf],
                     heiferIs: List[HeiferI],
                     heiferIIs: List[HeiferII],
                     heiferIIIs: List[HeiferIII],
                     cows: List[Cow]) \
            -> Tuple[List[Cow], List[Cow], List[Calf], List[Calf],
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
            animals_removed: list of animals that were removed during this day
            calves_born: list of calves that were born during this day
            calves: updated list of calves
            heiferIs: updated list of heiferIs
            heiferIIs: updated list of heiferIIs
            heiferIIIs: updated list of heiferIIIs
            cows: updated list of cows

        """
        animals_removed: List[Cow] = []
        animals_added: List[Cow] = []
        calves_born: List[Calf] = []
        total_animal_num = 0
        preg_heifer_num = 0

        self._reset_daily_stats()
        self._reset_parity()
        self._reset_cull_reason_stats()

        total_animal_num = self._evaluate_calves_for_weaning(sim_day, calves, heiferIs, total_animal_num)
        total_animal_num = self._evaluate_heiferIs_for_transitioning_to_heiferIIs(sim_day, heiferIs, heiferIIs,
                                                                                  total_animal_num)
        total_animal_num, preg_heifer_num = self._evaluate_heiferIIs_for_transitioning_to_heiferIIIs(sim_day, heiferIIs,
                                                                                                     heiferIIIs,
                                                                                                     preg_heifer_num,
                                                                                                     total_animal_num)
        total_animal_num = self._evaluate_heiferIIIs_for_transitioning_to_cows(sim_day, heiferIIIs, cows,
                                                                               total_animal_num)

        total_animal_num = self._cull_cows_and_record_stats(sim_day, cows, calves_born,
                                                            animals_removed, total_animal_num)
        self._check_if_heifers_need_to_be_sold(heiferIIIs, cows, animals_removed)
        self._check_if_replacement_heifers_needed(sim_day, heiferIIIs, cows, animals_added)

        self._calculate_herd_percentages(total_animal_num)
        self._calculate_cow_percentages()
        self._calculate_cull_reason_stats_percent()
        self._calculate_percent_cow_per_parity()

        self.daily_milk_production = sum(cow.estimated_daily_milk_produced for cow in cows)
        self.herd_milk_fat_kg = sum(cow.milk_fat_kg for cow in cows)
        self.herd_milk_fat_percent = self.herd_milk_fat_kg / self.daily_milk_production
        self.herd_milk_protein_kg = sum(cow.milk_protein_kg for cow in cows)
        self.herd_milk_protein_percent = self.herd_milk_protein_kg / self.daily_milk_production

        return (animals_added, animals_removed, calves_born, calves, heiferIs,
                heiferIIs, heiferIIIs, cows)

    def _reset_daily_stats(self) -> None:
        """Resets daily-based attributes."""
        # TODO: Maybe break this list down into smaller lists
        self.calf_num = 0
        self.heiferI_num = 0
        self.heiferII_num = 0
        self.heiferIII_num = 0
        self.cow_num = 0

        self.sold_calf_num = 0
        self.sold_heiferIII_oversupply_num = 0
        self.bought_heifer_num = 0
        self.sold_heiferII_num = 0
        self.cow_herd_exit_num = 0

        self.calf_percent = 0.0
        self.heiferI_percent = 0.0
        self.heiferII_percent = 0.0
        self.heiferIII_percent = 0.0
        self.cow_percent = 0.0

        # TODO: Check if all the following variables need to reset daily
        self.CIDR_count = 0
        self.preg_check_num_h = 0
        self.preg_check_num = 0
        self.GnRH_injection_num_h = 0
        self.GnRH_injection_num = 0
        self.PGF_injection_num_h = 0
        self.PGF_injection_num = 0
        self.ai_num_h = 0
        self.ai_num = 0
        self.semen_num_h = 0
        self.semen_num = 0
        self.ed_period_h = 0

        self.open_cow_num = 0
        self.preg_cow_num = 0
        self.vwp_cow_num = 0
        self.milking_cow_num = 0
        self.dry_cow_num = 0

        self.preg_cow_percent = 0.0
        self.dry_cow_percent = 0.0
        self.milking_cow_percent = 0.0
        self.non_preg_cow_percent = 0.0

        self.daily_milk_production = 0.0
        self.herd_milk_fat_kg = 0.0
        self.herd_milk_fat_percent = 0.0
        self.herd_milk_protein_kg = 0.0
        self.herd_milk_protein_percent = 0.0
        self.avg_days_in_milk = 0.0
        self.avg_days_in_preg = 0.0
        self.avg_cow_body_weight = 0.0
        self.avg_parity_num = 0.0

        self.avg_calving_interval = 0.0
        self.avg_breeding_to_preg_time = 0.0
        self.avg_heifer_culling_age = 0.0
        self.avg_cow_culling_age = 0.0
        self.avg_mature_body_weight = 0.0

    def _reset_parity(self) -> None:
        """Resets parity-based attributes."""
        for parity in self.num_cow_for_parity:
            self.num_cow_for_parity[parity] = 0
            self.avg_calving_to_preg_time[parity] = 0
            self.percent_cow_for_parity[parity] = 0.0
            self.avg_age_for_parity[parity] = 0.0
            self.avg_age_for_calving[parity] = 0.0

    def _reset_cull_reason_stats(self) -> None:
        """Resets cull reason-based attributes."""
        for cull_reason in self.cull_reason_stats:
            self.cull_reason_stats[cull_reason] = 0
            self.cull_reason_stats_percent[cull_reason] = 0.0

    def _evaluate_calves_for_weaning(self, sim_day: int, calves: List[Calf],
                                     heiferIs: List[HeiferI], total_animal_num: int) -> int:
        """Evaluates calves for weaning.

        If a calf is to be weaned, it will be removed from the calves list and
        get added to the heiferIs list.

        Args:
            sim_day: The current simulation day.
            calves: The list of calves.
            heiferIs: The list of heiferIs.
            total_animal_num: The current total number of animals.

        Returns:
            The newly updated total number of animals.

        """
        removed_calves_idx: List[int] = []

        for idx, calf in enumerate(calves):
            is_heiferI_stage = calf.update(sim_day)
            if is_heiferI_stage:
                self._convert_calf_to_heiferI(calf, heiferIs)
                removed_calves_idx.append(idx)
            else:
                self.calf_num += 1
                total_animal_num, self.avg_mature_body_weight = \
                    Utility.calc_average(total_animal_num, self.avg_mature_body_weight, calf.mature_body_weight)

        Utility.remove_items_from_list_by_indices(calves, removed_calves_idx)
        return total_animal_num

    @staticmethod
    def _convert_calf_to_heiferI(calf: Calf, heiferIs: List[HeiferI]) -> None:
        """Converts a calf to a heiferI and appends it to the heiferIs list.

        Args:
            calf: The calf to be converted.
            heiferIs: The list of heiferIs.

        """
        calf_vals = calf.get_calf_values()
        calf_vals.update({
            'body_weight_history': calf.body_weight_history,
            'pen_history': calf.pen_history
        })
        new_heiferI = HeiferI(calf_vals)
        heiferIs.append(new_heiferI)

    def _evaluate_heiferIs_for_transitioning_to_heiferIIs(self, sim_day: int, heiferIs: List[HeiferI],
                                                          heiferIIs: List[HeiferII],
                                                          total_animal_num: int) -> int:
        """Evaluates heiferIs for transitioning to heiferIIs.

        If a heiferI transitions to a heiferII, it will be removed
        from the heiferIs list and get added to the heiferIIs list.

        Args:
            sim_day: The current simulation day.
            heiferIs: The list of heiferIs.
            heiferIIs: The list of heiferIIs.
            total_animal_num: The current total number of animals.

        Returns:
            The newly updated total number of animals.

        """
        removed_heiferIs_idx: List[int] = []

        for idx, heiferI in enumerate(heiferIs):
            is_heiferII_stage = heiferI.update(sim_day)
            if is_heiferII_stage:
                self._convert_heiferI_to_heiferII(heiferI, heiferIIs)
                removed_heiferIs_idx.append(idx)
            else:
                self.heiferI_num += 1
                total_animal_num, self.avg_mature_body_weight = \
                    Utility.calc_average(total_animal_num, self.avg_mature_body_weight, heiferI.mature_body_weight)

        Utility.remove_items_from_list_by_indices(heiferIs, removed_heiferIs_idx)
        return total_animal_num

    @staticmethod
    def _convert_heiferI_to_heiferII(heiferI: HeiferI, heiferIIs: List[HeiferII]) -> None:
        """Converts a heiferI to a heiferII and appends it to the heiferIIs list.

        Args:
            heiferI: The heiferI to be converted.
            heiferIIs: The list of heiferIIs.

        """
        heiferI_vals = heiferI.get_heiferI_values()
        heiferI_vals.update({
            'body_weight_history': heiferI.body_weight_history,
            'pen_history': heiferI.pen_history
        })
        heiferI_vals.update(repro_program=HeiferII.get_user_defined_repro_protocol())
        if HeiferII.get_user_defined_repro_protocol() == HeiferReproProtocolEnum.TAI.value:
            heiferI_vals.update(tai_method_h=HeiferII.get_user_defined_repro_sub_protocol())
            heiferI_vals.update(synch_ed_method_h='')
        elif HeiferII.get_user_defined_repro_protocol() == HeiferReproProtocolEnum.SynchED.value:
            heiferI_vals.update(tai_method_h='')
            heiferI_vals.update(synch_ed_method_h=HeiferII.get_user_defined_repro_sub_protocol())
        else:
            heiferI_vals.update(tai_method_h='')
            heiferI_vals.update(synch_ed_method_h='')
        new_heiferII = HeiferII(heiferI_vals)
        heiferIIs.append(new_heiferII)

    def _evaluate_heiferIIs_for_transitioning_to_heiferIIIs(self, sim_day: int, heiferIIs: List[HeiferII],
                                                            heiferIIIs: List[HeiferIII], preg_heifer_num: int,
                                                            total_animal_num: int) -> Tuple[int, int]:
        """Evaluates heiferIIs for transitioning to heiferIIIs.

        If a heiferII is to be culled or transitions to a heiferIII, it will be removed
        from the heiferIIs list and get added to the culled heifers or heiferIIIs list, respectively.

        Args:
            sim_day: The current simulation day.
            heiferIIs: The list of heiferIIs.
            heiferIIIs: The list of heiferIIIs.
            preg_heifer_num: The current number of pregnant heifers.
            total_animal_num: The current total number of animals.

        Returns:
            The newly updated total number of animals and the newly updated number of pregnant heifers.

        """
        removed_heiferIIs_idx: List[int] = []

        for idx, heiferII in enumerate(heiferIIs):
            is_cull_stage, is_heiferIII_stage = heiferII.update(sim_day)
            if is_cull_stage:
                self.sold_heiferII_num, self.avg_heifer_culling_age = \
                    Utility.calc_average(self.sold_heiferII_num, self.avg_heifer_culling_age, heiferII.days_born)
                self.sold_heiferIIs.append(heiferII)
                removed_heiferIIs_idx.append(idx)
            elif is_heiferIII_stage:
                self._convert_heiferII_to_heiferIII(heiferII, heiferIIIs)
                removed_heiferIIs_idx.append(idx)
            else:
                total_animal_num, preg_heifer_num = \
                    self._remain_heiferII(heiferII, total_animal_num, preg_heifer_num)
                self._extract_repro_stats_from_heiferII(heiferII)

        Utility.remove_items_from_list_by_indices(heiferIIs, removed_heiferIIs_idx)
        return total_animal_num, preg_heifer_num

    @staticmethod
    def _convert_heiferII_to_heiferIII(heiferII: HeiferII, heiferIIIs: List[HeiferIII]) -> None:
        """Converts a heiferII to a heiferIII and appends it to the heiferIIIs list.

        Args:
            heiferII: The heiferII to be converted.
            heiferIIIs: The list of heiferIIIs.

        """
        heiferII_vals = heiferII.get_heiferII_values()
        heiferII_vals.update({
            'body_weight_history': heiferII.body_weight_history,
            'pen_history': heiferII.pen_history,
            'conceptus_weight': heiferII.conceptus_weight,
            'calf_birth_weight': heiferII.calf_birth_weight
        })
        new_heiferIII = HeiferIII(heiferII_vals)
        heiferIIIs.append(new_heiferIII)

    def _remain_heiferII(self, heiferII: HeiferII, total_animal_num: int, preg_heifer_num: int):
        """Updates relevant stats by keeping a heiferII as is.

        The following attributes are updated: heiferII_num, avg_mature_body_weight,
        and avg_preg_heifer_body_weight.

        Args:
            heiferII: The heiferII to be maintained.
            total_animal_num: The current total number of animals.

        Returns:
            The newly updated total number of animals and pregnant heifer number.

        """
        self.heiferII_num += 1
        total_animal_num, self.avg_mature_body_weight = \
            Utility.calc_average(total_animal_num, self.avg_mature_body_weight,
                                 heiferII.mature_body_weight)
        if heiferII.breeding_to_preg_time != 0:
            preg_heifer_num, self.avg_breeding_to_preg_time = \
                Utility.calc_average(preg_heifer_num, self.avg_breeding_to_preg_time,
                                     heiferII.breeding_to_preg_time)
        return total_animal_num, preg_heifer_num

    def _extract_repro_stats_from_heiferII(self, heiferII: HeiferII) -> None:
        """Extracts the reproductive stats from a heiferII.

        Args:
            heiferII: The heiferII to extract the stats from.

        """
        # self.CIDR_count += heiferII.CIDR_count  # TODO: add CIDR count to heiferII
        self.GnRH_injection_num_h += heiferII.GnRH_injections
        self.PGF_injection_num_h += heiferII.PGF_injections
        self.preg_check_num_h += heiferII.preg_diagnoses
        self.semen_num_h += heiferII.semen_num
        self.ai_num_h += heiferII.AI_times
        self.ed_period_h += heiferII.ED_days

    def _evaluate_heiferIIIs_for_transitioning_to_cows(self, sim_day: int, heiferIIIs: List[HeiferIII], cows: List[Cow],
                                                       total_animal_num: int) -> int:
        """Evaluates heiferIIIs for transitioning to cows.

        Args:
            sim_day: The current simulation day.
            heiferIIIs: The list of heiferIIIs.
            cows: The list of cows.
            total_animal_num: The current total number of animals.

        Returns:
            The newly updated total number of animals.

        """
        removed_heiferIIIs_idx: List[int] = []

        for idx, heiferIII in enumerate(heiferIIIs):
            is_cow_stage = heiferIII.update(sim_day)
            if is_cow_stage:
                self._convert_heiferIII_to_cow(heiferIII, cows)
                removed_heiferIIIs_idx.append(idx)
            else:
                self.heiferIII_num += 1
                temp = Utility.calc_average(total_animal_num, self.avg_mature_body_weight,
                                            heiferIII.mature_body_weight)
                total_animal_num, self.avg_mature_body_weight = temp

        Utility.remove_items_from_list_by_indices(heiferIIIs, removed_heiferIIIs_idx)
        return total_animal_num

    @staticmethod
    def _convert_heiferIII_to_cow(heiferIII, cows) -> None:
        """Converts a heiferIII to a cow and appends it to the cows list.

        Args:
            heiferIII: The heiferIII to be converted.
            cows: The list of cows.

        """
        args = heiferIII.get_heiferIII_values()
        args.update({
            'body_weight_history': heiferIII.body_weight_history,
            'pen_history': heiferIII.pen_history,
            'conceptus_weight': heiferIII.conceptus_weight,
            'calf_birth_weight': heiferIII.calf_birth_weight
        })
        args.update(repro_program=AnimalBase.config['cow_repro_method'])
        args.update(presynch_method=AnimalBase.config['cows']['presynch_protocol'])
        args.update(tai_method_c=AnimalBase.config['cows']['repro_sub_protocol'])
        args.update(resynch_method=AnimalBase.config['cows']['resynch_protocol'])
        new_cow = Cow(args)
        if len(cows) > 0:
            new_cow.milk_production_reduction = cows[0].milk_production_reduction
        cows.append(new_cow)

    def _check_if_heifers_need_to_be_sold(self, heiferIIIs: List[HeiferIII], cows: List[Cow],
                                          animals_removed: List[Cow]) -> None:
        """Checks if any heifers need to be sold.

        If the number of heifers exceeds what is needed for the herd,
        sell those as replacement

        Args:
            heiferIIIs: The list of heiferIIIs.
            cows: The list of cows.
            animals_removed: The list of animals removed from the herd.

        """
        sell_threshold = 1.03
        while len(heiferIIIs) + len(cows) > self.herd_num * sell_threshold and len(heiferIIIs) > 0:
            removed_heiferIII = heiferIIIs.pop()
            animals_removed.append(removed_heiferIII)
            self.sold_heiferIIIs.append(removed_heiferIII)
            self.sold_heiferIII_oversupply_num += 1
            self.heiferIII_num -= 1

    def _check_if_replacement_heifers_needed(self, sim_day: int, heiferIIIs: List[HeiferIII], cows: List[Cow],
                                             animals_added: List[Cow]) -> None:
        """Checks if replacement heifers are needed.

        If the number of heifers is less than what is needed for the herd,
        add replacement heifers.

        Args:
            sim_day: The current simulation day.
            heiferIIIs: The list of heiferIIIs.
            cows: The list of cows.
            animals_added: The list of animals added to the herd.

        """
        buy_threshold = 1.01
        while len(cows) + len(heiferIIIs) + self.bought_heifer_num < self.herd_num * buy_threshold \
                and sim_day > 1:
            if len(self.replacement_market) == 0:
                break
            replacement = self.replacement_market.pop(0)
            replacement.events.add_event(replacement.days_born, sim_day, animal_constants.ENTER_HERD)
            replacement.set_p_purchased()
            animals_added.append(replacement)
            self.bought_heifer_num += 1

    def _cull_cows_and_record_stats(self, sim_day: int, cows: List[Cow], calves_born: List[Calf],
                                    animals_removed: List[Cow], total_animal_num: int) -> int:
        """Culls cows and records stats.

        Args:
            sim_day: The current simulation day.
            cows: The list of cows.
            calves_born: The list of calves born.
            animals_removed: The list of animals removed from the herd.
            total_animal_num: The current total number of animals in the herd.

        Returns:
            The newly updated total number of animals in the herd.

        """
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
                animals_removed.append(cow)
                removed_cows_idx.append(index)
            else:
                total_animal_num = self._handle_cow_body_weight_and_parity(cow, total_animal_num)
                self._handle_cow_milking(cow)
                self._handle_cow_days_in_preg(cow)
                self._handle_cow_calves(cow, calving_age_avail_num, calf_to_preg_time_avail_num)
                calving_interval_avail_num = self._handle_cow_CI(cow, calving_interval_avail_num)
                self._extract_repro_stats_from_cow(cow)

            if new_born:
                self._handle_new_born(sim_day, cow, calves_born)

        Utility.remove_items_from_list_by_indices(cows, removed_cows_idx)
        return total_animal_num

    def _cull_cow(self, cow: Cow) -> None:
        """Culls a cow and records the culling reason.

        Args:
            cow: The cow to be culled.

        """
        self.sold_and_died_cows.append(cow)
        self.cull_reason_stats_range[cow.cull_reason] += 1
        self.cull_reason_stats[cow.cull_reason] += 1

        parity = cow.calves if cow.calves <= 3 else '4+'
        self.parity_culling_stats_range[parity] += 1
        self.cow_herd_exit_num, self.avg_cow_culling_age = \
            Utility.calc_average(self.cow_herd_exit_num, self.avg_cow_culling_age, cow.days_born)

    def _handle_cow_body_weight_and_parity(self, cow: Cow, total_animal_num: int) -> int:
        """Adjusts the average cow body weight, average parity number, and average mature body weight

        Args:
            cow (Cow): A Cow object.
            total_animal_num: The total number of animals in the herd.

        Returns:
            total_animal_num: The newly updated total number of animals in the herd.

        """
        _, self.avg_cow_body_weight = Utility.calc_average(
            self.cow_num, self.avg_cow_body_weight, cow.body_weight)
        self.cow_num, self.avg_parity_num = Utility.calc_average(
            self.cow_num, self.avg_parity_num, cow.calves)

        total_animal_num, self.avg_mature_body_weight = \
            Utility.calc_average(total_animal_num, self.avg_mature_body_weight, cow.mature_body_weight)
        return total_animal_num

    def _handle_cow_milking(self, cow: Cow) -> None:
        """Adjusts the daily milk production quantity, average days in milking.

        Args:
            cow: A Cow object.

        """
        if cow.milking:
            self.milking_cow_num, self.avg_days_in_milk = \
                Utility.calc_average(self.milking_cow_num, self.avg_days_in_milk, cow.days_in_milk)

            if cow.days_in_milk < self.animal_config['program_start_day']:
                self.vwp_cow_num += 1
        else:
            self.dry_cow_num += 1

    def _handle_cow_days_in_preg(self, cow: Cow) -> None:
        """Adjusts the average days in pregnancy.

        Args:
            cow: A Cow object.

        """
        if cow.days_in_preg == 0:
            self.open_cow_num += 1
        elif cow.days_in_preg > 0:
            self.preg_cow_num, self.avg_days_in_preg = \
                Utility.calc_average(self.preg_cow_num, self.avg_days_in_preg, cow.days_in_preg)

    def _handle_cow_calves(self, cow: Cow, calving_age_avail_num, calf_to_preg_time_avail_num) -> None:
        """Adjusts the average cow age per parity, average calving age, and average time from calf to pregnant."""
        if 0 < cow.calves <= 3:
            key = str(cow.calves)
        else:
            key = 'greater_than_3'

        self.num_cow_for_parity[key], self.avg_age_for_parity[key] = \
            Utility.calc_average(self.num_cow_for_parity[key], self.avg_age_for_parity[key], cow.days_born)

        calving_age = cow.events.get_most_recent_date(animal_constants.NEW_BIRTH)
        if calving_age != -1:
            calving_age_avail_num[key], self.avg_age_for_calving[key] = \
                Utility.calc_average(calving_age_avail_num[key], self.avg_age_for_calving[key], calving_age)

        if cow.calving_to_preg_time != 0:
            avg_times = self.avg_calving_to_preg_time
            calf_to_preg_time_avail_num[key], avg_times[key] = \
                Utility.calc_average(calf_to_preg_time_avail_num[key], avg_times[key], cow.calving_to_preg_time)

    def _handle_cow_CI(self, cow: Cow, calving_interval_avail_num: int) -> int:
        """Adjusts the average calving interval.

        Args:
            cow: A Cow object.
            calving_interval_avail_num: The number of cows with a calving interval.

        Returns:
            calving_interval_avail_num: The newly updated number of cows with a calving interval.

        """
        if cow.CI != 0:
            calving_interval_avail_num, self.avg_calving_interval = \
                Utility.calc_average(calving_interval_avail_num, self.avg_calving_interval, cow.CI)
        return calving_interval_avail_num

    def _extract_repro_stats_from_cow(self, cow: Cow) -> None:
        """Extracts the reproduction statistics from a cow and updates life cycle manager.

        Args:
            cow: A Cow object.

        """
        self.GnRH_injection_num += cow.GnRH_injections
        self.PGF_injection_num += cow.PGF_injections
        self.preg_check_num += cow.preg_diagnoses
        self.semen_num += cow.semen_num
        self.ai_num += cow.AI_times

    def _handle_new_born(self, sim_day: int, cow: Cow, calves_born: List[Calf]) -> None:
        args = {
            'id': self.animal_population.next_id(),
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
        cow.p_animal = cow.p_animal - cow.p_gest_for_calf + cow.p_growth + cow.dP_reserves
        new_calf = Calf(args)
        cow.p_gest_for_calf = 0
        cow.calf_birth_weight = 0
        if not (new_calf.culled or new_calf.sold):
            new_calf.events.add_event(new_calf.days_born, sim_day, animal_constants.ENTER_HERD)
            # calves.append(new_calf)
            calves_born.append(new_calf)
        if new_calf.sold:
            self.sold_calf_num += 1

    def _calculate_herd_percentages(self, total_animal_num: int) -> None:
        """Calculates percentage of each animal class in the herd.

        When the total number of animals is 0, it is assumed that the count of
        each animal class has already been set to or initialized with 0.

        Args:
            total_animal_num: The total number of animals in the herd.

        """
        denominator = total_animal_num if total_animal_num > 0 else 1
        pc = Utility.percent_calculator(denominator)
        self.calf_percent = pc(self.calf_num)
        self.heiferI_percent = pc(self.heiferI_num)
        self.heiferII_percent = pc(self.heiferII_num)
        self.heiferIII_percent = pc(self.heiferIII_num)
        self.cow_percent = pc(self.cow_num)

    def _calculate_cow_percentages(self) -> None:
        """Calculates percentages of different kinds of cows"""
        denominator = self.cow_num if self.cow_num > 0 else 1
        pc = Utility.percent_calculator(denominator)
        self.dry_cow_percent = pc(self.dry_cow_num)
        self.milking_cow_percent = pc(self.milking_cow_num)
        self.preg_cow_percent = pc(self.preg_cow_num)
        self.non_preg_cow_percent = pc(self.open_cow_num)

    def _calculate_cull_reason_stats_percent(self) -> None:
        """Calculates the percentage of culled cows for each cull reason."""
        denominator = self.cow_herd_exit_num if self.cow_herd_exit_num > 0 else 1
        pc = Utility.percent_calculator(denominator)
        for cull_reason in self.cull_reason_stats:
            self.cull_reason_stats_percent[cull_reason] = pc(self.cull_reason_stats[cull_reason])

    def _calculate_percent_cow_per_parity(self) -> None:
        """Calculates the percentage of cows for each parity number."""
        denominator = self.cow_num if self.cow_num > 0 else 1
        pc = Utility.percent_calculator(denominator)
        for parity in self.num_cow_for_parity:
            self.percent_cow_for_parity[parity] = pc(self.num_cow_for_parity[parity])
