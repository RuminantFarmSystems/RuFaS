from typing import Dict
from typing import List
from typing import TypedDict
from typing import Union
from typing_extensions import NotRequired


class HerdInfoTypedDict(TypedDict):
    """List of expected keys for herd information dictionary"""
    calf_num: int
    heiferI_num: int
    heiferII_num: int
    heiferIII_num: int
    cow_num: int
    replace_num: int
    herd_num: int
    herd_init: bool
    breed: str


class PenTypedDict(TypedDict):
    """List of expected keys for pen information dictionary"""
    id: int
    animal_combination: str
    vertical_dist_to_milking_parlor: float
    horizontal_dist_to_milking_parlor: float
    number_of_stalls: float
    housing_type: str
    bedding_type: str
    pen_type: str
    manure_handling: str
    manure_separator: str
    manure_storage: str
    max_stocking_density: float


class AnimalBaseInitArgsTypedDict(TypedDict):
    """List of expected keys for animal base initialization arguments dictionary"""

    id: int
    breed: str
    birth_date: str
    days_born: int
    birth_weight: float
    p_init: int
    body_weight_history: NotRequired[List]
    pen_history: NotRequired[List]
    conceptus_weight: NotRequired[float]
    calf_birth_weight: NotRequired[float]


class CalfValuesTypedDict(TypedDict):
    """List of expected keys for calf values dictionary"""
    id: int
    breed: str
    birth_date: int
    days_born: int
    birth_weight: float
    p_init: int
    body_weight: float
    wean_weight: float
    mature_body_weight: float
    events: str


class HeiferIValuesTypedDict(TypedDict):
    """List of expected keys for heifer I values dictionary"""
    id: int
    breed: str
    birth_date: int
    days_born: int
    birth_weight: float
    body_weight: float
    wean_weight: float
    mature_body_weight: float
    events: str


class HeiferIIValuesTypedDict(TypedDict):
    id: int
    breed: str
    birth_date: int
    days_born: int
    birth_weight: float
    body_weight: float
    wean_weight: float
    mature_body_weight: float
    events: str

    repro_program: str
    tai_method_h: str
    synch_ed_method_h: str
    estrus_count: int
    estrus_day: int
    tai_program_start_day_h: int
    synch_ed_program_start_day_h: int
    synch_ed_estrus_day: int
    synch_ed_stop_day: int
    conception_rate: float
    ai_day: int
    abortion_day: int
    days_in_preg: int
    gestation_length: int
    p_gest_for_calf: int
    calf_birth_weight: float


class AnimalConfigTypedDict(TypedDict):
    """
    Keeps track of all the attributes stored in the animal config object used
    in `animal_management.py`.

    This list of attributes should also match the attributes provided by the
    `animal_management_animal.json`.

    """
    # management decisions
    breeding_start_day_h: int
    heifer_repro_cull_time: int
    heifer_repro_method: str
    cow_repro_method: str
    semen_type: str
    days_in_preg_when_dry: int
    lactation_curve: str
    repro_cull_time: int
    do_not_breed_time: int
    cull_milk_production: int
    cow_times_milked_per_day: int

    # farm level -> calf
    male_calf_rate_sexed_semen: float
    male_calf_rate_conventional_semen: float
    keep_female_calf_rate: int
    wean_day: int
    wean_length: int
    milk_type: str

    # farm level -> repro -> ED_related
    estrus_detection_rate_h: float
    estrus_insemination_rate_h: float
    estrus_conception_rate_h: float
    estrus_detection_rate_h_synch: float
    heifer_synchED_protocol: str
    estrus_detection_rate: float
    estrus_insemination_rate: float
    estrus_conception_rate: float

    # farm level -> repro -> TAI_related
    heifer_TAI_protocol: str
    TAI_conception_rate_h: float
    m5dCG2P_conception_rate: float
    m5dCGP_conception_rate: float
    heifer_user_defined_tai_cr: float
    cow_presynch_protocol: str
    cow_TAI_protocol: str
    ovsynch56_conception_rate: float
    ovsynch48_conception_rate: float
    cosynch72_conception_rate: float
    cosynch5d_conception_rate: float
    cow_user_defined_tai_cr: float
    cow_resynch_protocol: str
    user_define_tai_length: int

    # TODO: For these two variables, either leave them like this or
    # add another typed dict for each
    ED_related: Dict[str, Union[float, str]]
    TAI_related: Dict[str, Union[float, str]]

    # remaining attributes in farm level -> repro
    voluntary_waiting_period: int
    tai_program_start_day: int
    conception_rate_decrease: float
    avg_gestation_len: int
    std_gestation_len: int
    prefresh_day: int
    num_21_days_repro: int
    calving_interval: int
    user_input_calving_interval: bool

    # farm level -> bodyweight
    birth_weight_avg_ho: float
    birth_weight_std_ho: float
    birth_weight_avg_je: float
    birth_weight_std_je: float
    target_heifer_preg_day: int
    mature_body_weight_avg: float
    mature_body_weight_std: float

    # from_literature -> repro
    avg_estrus_cycle_heifer: float
    std_estrus_cycle_heifer: float
    preg_check_day_1: int
    preg_loss_rate_1: float
    preg_check_day_2: int
    preg_loss_rate_2: float
    preg_check_day_3: int
    preg_loss_rate_3: float
    avg_estrus_cycle_return: float
    std_estrus_cycle_return: float
    avg_estrus_cycle_cow: float
    std_estrus_cycle_cow: float
    avg_estrus_cycle_p: float
    std_estrus_cycle_p: float

    # from_literature -> milking
    wood_l: List[List[float]]
    wood_m: List[List[float]]
    wood_n: List[List[float]]
    wood_l_std: List[List[float]]
    wood_m_std: List[List[float]]
    wood_n_std: List[List[float]]

    # from_literature -> culling
    parity_death_prob: List[float]
    death_cull_prob: List[float]
    parity_cull_prob: List[float]
    mastitis_cull_prob: List[float]
    feet_leg_cull_prob: List[float]
    injury_cull_prob: List[float]
    disease_cull_prob: List[float]
    udder_cull_prob: List[float]
    unkown_cull_prob: List[float]  # TODO: Fix this typo in `animal_management_animal.json` and here
    cull_day_count: List[float]

    # from_literature -> life_cycle
    still_birth_rate: float


class InitializationDBSummaryTypedDict(TypedDict):
    num_calf: int
    num_heiferI: int
    num_heiferII: int
    num_heiferIII: int
    num_cow: int
    num_replacement: int

    avg_calf_age: float
    avg_heiferI_age: float
    avg_heiferII_age: float
    avg_heiferIII_age: float
    avg_cow_age: float
    avg_replacement_age: float

    cow_avg_days_in_preg: float
    cow_avg_days_in_milk: float
    cow_avg_parity: float
    cow_avg_CI: float
