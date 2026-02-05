from dataclasses import dataclass

from RUFAS.biophysical.animal import animal_constants
from RUFAS.biophysical.animal.data_types.animal_typed_dicts import SoldAnimalTypedDict
from RUFAS.biophysical.animal.data_types.animal_types import AnimalType


@dataclass
class HerdStatistics:
    """
    Contains statistical data for animal herd management.

    Attributes
    ----------
    avg_calving_to_preg_time : dict[str, float]
        Average calving to pregnancy time categorized by parity levels ("1", "2", "3",
        "greater_than_3"), (simulation days).
    cull_reason_stats : dict[str, int]
        Count statistics of culled animals, categorized by specified culling reasons, (unitless).
    num_cow_for_parity : dict[str, int]
        Count of cows for each parity class, (unitless).
    avg_daily_cow_milking : float
        Average number of milking cows per day, (unitless).
    sold_calves_info : list[SoldAnimalTypedDict]
        Details about sold calves including relevant attributes.
    sold_heiferIIIs_info : list[SoldAnimalTypedDict]
        Detailed information on sold animals categorized as "Heifer III".
    sold_heiferIIs_info : list[SoldAnimalTypedDict]
        Detailed information about sold animals categorized as "Heifer II".
    sold_cows_info : list[SoldAnimalTypedDict]
        Comprehensive details of sold cows including relevant attributes.
    sold_and_died_cows_info : list[SoldAnimalTypedDict]
        Information concerning cows that were either sold or died.
    herd_num : int
        Total number of animals in the herd, (unitless).
    calf_num : int
        Total count of calves currently in the herd, (unitless).
    heiferI_num : int
        Total count of heifers categorized as "Heifer I", (unitless).
    heiferII_num : int
        Total count of heifers categorized as "Heifer II", (unitless).
    heiferIII_num : int
        Total count of heifers categorized as "Heifer III", (unitless).
    cow_num : int
        Total count of cows in the herd, (unitless).
    stillborn_calf_num  : int
        Number of stillborn calves during a specific period, (unitless).
    sold_calf_num : int
        Number of calves sold during a specific period, (unitless).
    sold_heiferIII_oversupply_num : int
        Number of surplus "Heifer III" animals sold, (unitless).
    bought_heifer_num : int
        Number of heifers purchased during a specific period, (unitless).
    sold_heiferII_num : int
        Number of "Heifer II" animals sold during a specific period, (unitless).
    cow_herd_exit_num : int
        Number of cows that exited the herd, totalled for both sales and deaths, (unitless).
    sold_cow_num : int
        Number of cows sold during the specific period, (unitless).
    born_calf_num : int
        The total amount of calf born, including stillborn, newborn and sold.
    calf_percent : float
        Proportion of calves in the herd expressed as a percentage, (unitless).
    heiferI_percent : float
        Proportion of "Heifer I" animals in the herd expressed as a percentage, (unitless).
    heiferII_percent : float
        Proportion of "Heifer II" animals in the herd expressed as a percentage, (unitless).
    heiferIII_percent : float
        Proportion of "Heifer III" animals in the herd expressed as a percentage, (unitless).
    cow_percent : float
        Proportion of cows in the herd expressed as a percentage, (unitless).
    preg_check_num_h : int
        Number of pregnancy checks performed for heifers, (unitless).
    preg_check_num : int
        Number of pregnancy checks performed for cows, (unitless).
    CIDR_count : int
        Count of CIDR (Controlled Internal Drug Release) devices used, (unitless).
    GnRH_injection_num_h : int
        Number of GnRH (Gonadotropin-Releasing Hormone) injections administered to heifers, (unitless).
    GnRH_injection_num : int
        Total number of GnRH injections administered to cows, (unitless).
    PGF_injection_num_h : int
        Number of PGF (Prostaglandin) injections administered to heifers.
    PGF_injection_num : int
        Total number of PGF injections administered to cows, (unitless).
    ai_num_h : int
        Number of artificial inseminations (AI) performed on heifers, (unitless).
    ai_num : int
        Total number of artificial inseminations (AI) performed on cows, (unitless).
    semen_num_h : int
        Number of semen units used for heifers, (unitless).
    semen_num : int
        Total number of semen units used for cows, (unitless).
    ed_period_h : int
        Estrus detection (ED) period for heifers, (simulation days).
    open_cow_num : int
        Total number of open (non-pregnant) cows, (unitless).
    preg_cow_num : int
        Total number of pregnant cows in the herd, (unitless).
    vwp_cow_num : int
        Number of cows in the voluntary waiting period (VWP), (unitless).
    milking_cow_num : int
        Number of cows actively milking in the herd, (unitless).
    dry_cow_num : int
        Number of dry cows (non-milking) in the herd, (unitless).
    dry_cow_percent : float
        Percentage of dry cows in the herd, (unitless).
    milking_cow_percent : float
        Percentage of milking cows in the herd, (unitless).
    preg_cow_percent : float
        Percentage of pregnant cows in the herd, (unitless).
    non_preg_cow_percent : float
        Percentage of non-pregnant cows in the herd, (unitless).
    daily_milk_production : float
        Average daily milk production, (kg).
    herd_milk_fat_kg : float
        Total quantity of milk fat in the herd's milk production, (kg).
    herd_milk_fat_percent : float
        Percentage of milk fat in the herd's milk production, (unitless).
    herd_milk_protein_kg : float
        Total quantity of milk protein in the herd's milk production, (kg).
    herd_milk_protein_percent : float
        Percentage of milk protein in the herd's milk production, (unitless).
    avg_days_in_milk : float
        Average number of days in milk, (simulation days).
    avg_days_in_preg : float
        Average days in pregnancy for pregnant animals, (simulation days).
    avg_cow_body_weight : float
        Average body weight of cows in the herd, (kg).
    avg_parity_num : float
        Average parity number for cows, (unitless).
    avg_calving_interval : float
        Average interval between calvings, (simulation days).
    avg_breeding_to_preg_time : float
        Average time between first breeding attempt and pregnancy confirmation, (simulation days).
    avg_heifer_culling_age : float
        Average age at culling for heifers, (simulation days).
    avg_cow_culling_age : float
        Average age at culling for cows, (simulation days).
    avg_mature_body_weight : float
        Average weight of mature animals in the herd, (kg).
    parity_culling_stats_range : dict[str, int]
        Count of culled animals categorized by their parity classes ("1", "2", "3",
        "greater_than_3"), (unitless).
    avg_age_for_calving : dict[str, float]
        Average age of animals at calving, categorized by parity levels, (simulation days).
    avg_age_for_parity : dict[str, float]
        Average age of animals for each parity, categorized similarly, (simulation days).
    cull_reason_stats_percent : dict[str, float]
        Percentage statistics of culled animals, categorized by culling reasons, (unitless).
    percent_cow_for_parity : dict[str, float]
        Percentage of cows available for each parity class, calculated based on total counts, (unitless).
    total_enteric_methane : dict[AnimalType, dict[str, float]]
        Total amount of enteric methane, grouped by animal types and methods (g/day).

    """

    avg_calving_to_preg_time: dict[str, float]
    cull_reason_stats: dict[str, int]

    num_cow_for_parity: dict[str, int]
    avg_daily_cow_milking = 0.0

    sold_calves_info: list[SoldAnimalTypedDict]
    sold_heiferIIIs_info: list[SoldAnimalTypedDict]
    sold_heiferIIs_info: list[SoldAnimalTypedDict]
    sold_cows_info: list[SoldAnimalTypedDict]
    sold_and_died_cows_info: list[SoldAnimalTypedDict]
    total_enteric_methane: dict[AnimalType, dict[str, float]]

    # TODO: Maybe break this list down into smaller lists GitHub Issue #1215
    herd_num = 0
    calf_num = 0
    heiferI_num = 0
    heiferII_num = 0
    heiferIII_num = 0
    cow_num = 0

    stillborn_calf_num = 0
    sold_calf_num = 0
    sold_heiferIII_oversupply_num = 0
    bought_heifer_num = 0
    sold_heiferII_num = 0
    cow_herd_exit_num = 0
    sold_cow_num = 0
    born_calf_num = 0

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
    ed_period = 0

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

    animals_deaths_by_stage: dict[AnimalType, int]

    def __init__(self) -> None:
        """
        Initializes a HerdStatistics object and set the default values for all dictionary and list attributes.
        """
        self.avg_calving_to_preg_time = {
            "1": 0.0,
            "2": 0.0,
            "3": 0.0,
            "4": 0.0,
            "5": 0.0,
            "greater_than_5": 0.0,
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
        self.parity_culling_stats_range = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "greater_than_5": 0}
        self.num_cow_for_parity = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "greater_than_5": 0}
        self.avg_age_for_calving = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "greater_than_5": 0}
        self.avg_age_for_parity = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "greater_than_5": 0}
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
            "4": 0.0,
            "5": 0.0,
            "greater_than_5": 0.0,
        }

        self.stillborn_calf_info = []
        self.sold_calves_info = []
        self.sold_heiferIIIs_info = []
        self.sold_heiferIIs_info = []
        self.sold_cows_info = []
        self.sold_and_died_cows_info = []

        self.animals_deaths_by_stage: dict[AnimalType, int] = {
            AnimalType.CALF: 0,
            AnimalType.HEIFER_I: 0,
            AnimalType.HEIFER_II: 0,
            AnimalType.HEIFER_III: 0,
            AnimalType.LAC_COW: 0,
            AnimalType.DRY_COW: 0,
        }

    def reset_daily_stats(self) -> None:
        """Resets daily-based attributes."""
        self.calf_num = 0
        self.heiferI_num = 0
        self.heiferII_num = 0
        self.heiferIII_num = 0
        self.cow_num = 0

        self.stillborn_calf_num = 0
        self.sold_calf_num = 0
        self.sold_heiferIII_oversupply_num = 0
        self.bought_heifer_num = 0
        self.sold_heiferII_num = 0
        self.cow_herd_exit_num = 0
        self.sold_cow_num = 0
        self.born_calf_num = 0

        self.calf_percent = 0.0
        self.heiferI_percent = 0.0
        self.heiferII_percent = 0.0
        self.heiferIII_percent = 0.0
        self.cow_percent = 0.0

        # TODO: Check if all the following variables need to reset daily GitHub Issue #1215
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
        self.ed_period = 0

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

        self.animals_deaths_by_stage: dict[AnimalType, int] = {
            AnimalType.CALF: 0,
            AnimalType.HEIFER_I: 0,
            AnimalType.HEIFER_II: 0,
            AnimalType.HEIFER_III: 0,
            AnimalType.LAC_COW: 0,
            AnimalType.DRY_COW: 0,
        }

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
