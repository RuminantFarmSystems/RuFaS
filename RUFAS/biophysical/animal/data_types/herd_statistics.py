from dataclasses import dataclass

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import SoldAnimalTypedDict


@dataclass
class HerdStatistics:
    avg_calving_to_preg_time: dict[str, float]
    cull_reason_stats: dict[str, int]

    num_cow_for_parity: dict[str, int]
    avg_daily_cow_milking = 0.0

    sold_calves_info: list[SoldAnimalTypedDict]
    sold_heiferIIIs_info: list[SoldAnimalTypedDict]
    sold_heiferIIs_info: list[SoldAnimalTypedDict]
    sold_cows_info: list[SoldAnimalTypedDict]
    sold_and_died_cows_info: list[SoldAnimalTypedDict]

    herd_num = 0
    calf_num = 0
    heiferI_num = 0
    heiferII_num = 0
    heiferIII_num = 0
    cow_num = 0

    sold_calf_num = 0
    sold_heiferIII_oversupply_num = 0
    bought_heifer_num = 0
    sold_heiferII_num = 0
    cow_herd_exit_num = 0
    sold_cow_num = 0

    calf_percent = 0.0
    heiferI_percent = 0.0
    heiferII_percent = 0.0
    heiferIII_percent = 0.0
    cow_percent = 0.0

    preg_check_num_h = 0
    preg_check_num = 0
    CIDR_count = 0
    GnRH_injection_num_h = 0
    GnRH_injection_num = 0
    PGF_injection_num_h = 0
    PGF_injection_num = 0

    ai_num_h = 0
    ai_num = 0
    semen_num_h = 0
    semen_num = 0
    ed_period_h = 0

    open_cow_num = 0
    preg_cow_num = 0
    vwp_cow_num = 0
    milking_cow_num = 0
    dry_cow_num = 0

    dry_cow_percent = 0.0
    milking_cow_percent = 0.0
    preg_cow_percent = 0.0
    non_preg_cow_percent = 0.0

    daily_milk_production = 0.0
    herd_milk_fat_kg = 0.0
    herd_milk_fat_percent = 0.0
    herd_milk_protein_kg = 0.0
    herd_milk_protein_percent = 0.0
    avg_days_in_milk = 0.0
    avg_days_in_preg = 0.0
    avg_cow_body_weight = 0.0
    avg_parity_num = 0.0

    avg_calving_interval = 0.0
    avg_breeding_to_preg_time = 0.0
    avg_heifer_culling_age = 0.0
    avg_cow_culling_age = 0.0
    avg_mature_body_weight = 0.0

    parity_culling_stats_range: dict[str, int]

    avg_age_for_calving: dict[str, float]
    avg_age_for_parity: dict[str, float]
    cull_reason_stats_percent: dict[str, float]
    percent_cow_for_parity: dict[str, float]

    def __init__(self) -> None:
        self.avg_calving_to_preg_time = {
            "1": 0.0,
            "2": 0.0,
            "3": 0.0,
            "greater_than_3": 0.0,
        }
        self.cull_reason_stats = {
            animal_constants.DEATH_CULL: 0,
            animal_constants.LOW_PROD_CULL: 0,
            animal_constants.LAMENESS_CULL: 0,
            animal_constants.INJURY_CULL: 0,
            animal_constants.MASTITIS_CULL: 0,
            animal_constants.DISEASE_CULL: 0,
            animal_constants.UDDER_CULL: 0,
            animal_constants.UNKNOWN_CULL: 0,
        }
        self.parity_culling_stats_range = {"1": 0, "2": 0, "3": 0, "greater_than_3": 0}
        self.num_cow_for_parity = {"1": 0, "2": 0, "3": 0, "greater_than_3": 0}
        self.avg_age_for_calving = {"1": 0.0, "2": 0.0, "3": 0.0, "greater_than_3": 0.0}
        self.avg_age_for_parity = {"1": 0.0, "2": 0.0, "3": 0.0, "greater_than_3": 0.0}
        self.cull_reason_stats_percent = {
            animal_constants.DEATH_CULL: 0.0,
            animal_constants.LOW_PROD_CULL: 0.0,
            animal_constants.LAMENESS_CULL: 0.0,
            animal_constants.INJURY_CULL: 0.0,
            animal_constants.MASTITIS_CULL: 0.0,
            animal_constants.DISEASE_CULL: 0.0,
            animal_constants.UDDER_CULL: 0.0,
            animal_constants.UNKNOWN_CULL: 0.0,
        }
        self.percent_cow_for_parity = {
            "1": 0.0,
            "2": 0.0,
            "3": 0.0,
            "greater_than_3": 0.0,
        }

        self.sold_calves_info = []
        self.sold_heiferIIIs_info = []
        self.sold_heiferIIs_info = []
        self.sold_cows_info = []
        self.sold_and_died_cows_info = []

    def reset_daily_stats(self) -> None:
        """Resets daily-based attributes."""
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
        self.sold_cow_num = 0

        self.calf_percent = 0.0
        self.heiferI_percent = 0.0
        self.heiferII_percent = 0.0
        self.heiferIII_percent = 0.0
        self.cow_percent = 0.0

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

    def reset_parity(self) -> None:
        """Resets parity-based attributes."""
        for parity in self.num_cow_for_parity:
            self.num_cow_for_parity[parity] = 0
            self.avg_calving_to_preg_time[parity] = 0
            self.percent_cow_for_parity[parity] = 0.0
            self.avg_age_for_parity[parity] = 0.0
            self.avg_age_for_calving[parity] = 0.0

    def reset_cull_reason_stats(self) -> None:
        """Resets cull reason-based attributes."""
        for cull_reason in self.cull_reason_stats:
            self.cull_reason_stats[cull_reason] = 0
            self.cull_reason_stats_percent[cull_reason] = 0.0
