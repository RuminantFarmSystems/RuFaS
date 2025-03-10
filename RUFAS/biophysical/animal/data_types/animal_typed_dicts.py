from datetime import date
from typing import Any, Dict, List, TypedDict, Union

from typing_extensions import NotRequired

from RUFAS.biophysical.animal.data_types.animal_enums import Breed
from RUFAS.biophysical.animal.data_types.body_weight_history import BodyWeightHistory
from RUFAS.biophysical.animal.data_types.pen_history import PenHistory
from RUFAS.biophysical.animal.data_types.repro_protocol_enums import (
    HeiferReproductionProtocol,
    HeiferTAISubProtocol,
    HeiferSynchEDSubProtocol,
    CowReproductionProtocol,
    CowTAISubProtocol,
    CowReSynchSubProtocol,
    CowPreSynchSubProtocol,
)


class HerdInfoTypedDict(TypedDict):
    """List of expected keys for herd information dictionary"""

    calf_num: int
    heiferI_num: int
    heiferII_num: int
    heiferIII_num_springers: int
    cow_num: int
    replace_num: int
    herd_num: int
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
    ration: Dict[str, float | str]
    ration_per_animal: Dict[str, float | str]
    animals_in_pen: Dict[str, Any]


class AnimalBaseInitArgsTypedDict(TypedDict):
    """List of expected keys for animal base initialization arguments dictionary"""

    id: int
    breed: str
    animal_type: str
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
    animal_type: str
    days_born: int
    birth_weight: float
    body_weight: float
    wean_weight: float
    mature_body_weight: float
    events: str
    net_merit: float
    initial_phosphorus: NotRequired[float]
    body_weight_history: NotRequired[list[BodyWeightHistory]]
    pen_history: NotRequired[list[PenHistory]]
    conceptus_weight: NotRequired[float]
    calf_birth_weight: NotRequired[float]


class NewBornCalfValuesTypedDict(TypedDict):
    """List of expected keys for calf values dictionary"""

    id: NotRequired[int]
    breed: str
    animal_type: str
    birth_date: str
    days_born: int
    birth_weight: float
    initial_phosphorus: float
    net_merit: float
    body_weight_history: NotRequired[list[BodyWeightHistory]]
    pen_history: NotRequired[list[PenHistory]]
    conceptus_weight: NotRequired[float]
    calf_birth_weight: NotRequired[float]


class HeiferIValuesTypedDict(TypedDict):
    """List of expected keys for heifer I values dictionary"""

    id: int
    breed: str
    animal_type: str
    days_born: int
    birth_weight: float
    body_weight: float
    wean_weight: float
    mature_body_weight: float
    events: str
    net_merit: float
    body_weight_history: NotRequired[list[BodyWeightHistory]]
    pen_history: NotRequired[list[PenHistory]]
    conceptus_weight: NotRequired[float]
    calf_birth_weight: NotRequired[float]


class HeiferIIValuesTypedDict(TypedDict):
    id: int
    breed: str
    animal_type: str
    days_born: int
    birth_weight: float
    body_weight: float
    wean_weight: float
    mature_body_weight: float
    events: str
    net_merit: float
    body_weight_history: NotRequired[list[BodyWeightHistory]]
    pen_history: NotRequired[list[PenHistory]]
    conceptus_weight: NotRequired[float]
    calf_birth_weight: NotRequired[float]

    heifer_reproduction_program: str
    heifer_reproduction_sub_protocol: str

    estrus_count: NotRequired[int]
    estrus_day: NotRequired[int]
    heifer_tai_program_start_day: NotRequired[int]
    heifer_synch_ed_program_start_day: NotRequired[int]
    heifer_synch_ed_estrus_day: NotRequired[int]
    heifer_synch_ed_stop_day: NotRequired[int]
    conception_rate: NotRequired[float]
    ai_day: NotRequired[int]
    abortion_day: NotRequired[int]
    days_in_pregnancy: NotRequired[int]
    gestation_length: NotRequired[int]
    phosphorus_for_gestation_required_for_calf: NotRequired[float]
    calf_birth_weight: NotRequired[float]


class HeiferIIIValuesTypedDict(TypedDict):
    id: int
    breed: str
    animal_type: str
    days_born: int
    birth_weight: float
    body_weight: float
    wean_weight: float
    mature_body_weight: float
    events: str
    net_merit: float
    body_weight_history: NotRequired[list[BodyWeightHistory]]
    pen_history: NotRequired[list[PenHistory]]
    conceptus_weight: NotRequired[float]
    calf_birth_weight: NotRequired[float]

    heifer_reproduction_program: str
    heifer_reproduction_sub_protocol: str

    estrus_count: NotRequired[int]
    estrus_day: NotRequired[int]
    heifer_tai_program_start_day: NotRequired[int]
    heifer_synch_ed_program_start_day: NotRequired[int]
    heifer_synch_ed_estrus_day: NotRequired[int]
    heifer_synch_ed_stop_day: NotRequired[int]
    conception_rate: NotRequired[float]
    ai_day: NotRequired[int]
    abortion_day: NotRequired[int]
    days_in_pregnancy: NotRequired[int]
    gestation_length: NotRequired[int]
    phosphorus_for_gestation_required_for_calf: NotRequired[float]
    calf_birth_weight: NotRequired[float]


class CowValuesTypedDict(TypedDict):
    """List of expected keys for cow values dictionary"""

    id: int
    breed: str
    animal_type: str
    days_born: int
    birth_weight: float
    body_weight: float
    wean_weight: float
    mature_body_weight: float
    events: str
    net_merit: float
    body_weight_history: NotRequired[list[BodyWeightHistory]]
    pen_history: NotRequired[list[PenHistory]]
    conceptus_weight: NotRequired[float]
    calf_birth_weight: float

    heifer_reproduction_program: str
    heifer_reproduction_sub_protocol: str

    cow_reproduction_program: str
    cow_presynch_program: str
    cow_ovsynch_program: str
    cow_resynch_program: str

    estrus_count: NotRequired[int]
    estrus_day: NotRequired[int]
    heifer_tai_program_start_day: NotRequired[int]
    heifer_synch_ed_program_start_day: NotRequired[int]
    heifer_synch_ed_estrus_day: NotRequired[int]
    heifer_synch_ed_stop_day: NotRequired[int]
    conception_rate: NotRequired[float]
    ai_day: NotRequired[int]
    abortion_day: NotRequired[int]
    days_in_pregnancy: NotRequired[int]
    gestation_length: NotRequired[int]
    phosphorus_for_gestation_required_for_calf: NotRequired[float]

    days_in_milk: NotRequired[int]
    parity: NotRequired[int]
    calving_interval: NotRequired[int]


class AnimalConfigTypedDict(TypedDict):
    """Keeps track of all the attributes stored in the animal config object used
    in `animal_manager.py`.

    This list of attributes should also match the attributes provided by the
    `animal_management_animal.json`. To make it easier to access the attributes,
    the animal config object in the AnimalManager class has been flattened out
    compared to the structure of the JSON object.

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
    keep_female_calf_rate: float
    wean_day: int
    wean_length: int
    milk_type: str

    # farm level -> repro -> ED_related
    estrus_detection_rate: float
    estrus_insemination_rate: float
    estrus_conception_rate: float

    # farm level -> repro -> TAI_related
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
    tai_program_start_day: int

    # remaining attributes in farm level -> repro
    voluntary_waiting_period: int
    conception_rate_decrease: float
    prefresh_day: int
    calving_interval: int
    use_input_calving_interval: bool

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
    avg_gestation_len: float
    std_gestation_len: float
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
    avg_estrus_cycle_after_pgf: float
    std_estrus_cycle_after_pgf: float

    # from_literature -> milking
    wood_l: List[List[float]]
    wood_m: List[List[float]]
    wood_n: List[List[float]]
    wood_l_std: List[List[float]]
    wood_m_std: List[List[float]]
    wood_n_std: List[List[float]]

    # from_literature -> culling
    parity_death_prob: List[float]
    death_day_prob: List[float]
    parity_cull_prob: List[float]
    mastitis_cull_prob: List[float]
    feet_leg_cull_prob: List[float]
    injury_cull_prob: List[float]
    disease_cull_prob: List[float]
    udder_cull_prob: List[float]
    unknown_cull_prob: List[float]
    cull_day_count: List[int]

    # from_literature -> life_cycle
    still_birth_rate: float


class InitialHerdSummaryTypedDict(TypedDict):
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


class AvailableFeedsTypedDict(TypedDict):
    feed_id: List[int]
    feed_key: List[str]
    price: List[float]
    TDN: List[float]
    EE: List[float]
    DE: List[float]
    is_fat: List[bool]
    calcium: List[float]
    phosphorus: List[float]
    NDF: List[float]
    feed_type: List[str]
    is_wetforage: List[bool]
    Kd: List[float]
    N_A: List[float]
    N_B: List[float]
    CP: List[float]
    dRUP: List[float]
    lactating_cow_minimum: List[float]
    lactating_cow_limit: List[float]
    dry_cow_minimum: List[float]
    dry_cow_limit: List[float]
    heiferIII_limit: List[float]
    heiferII_limit: List[float]
    heiferI_limit: List[float]
    calf_limit: List[float]


class FeedInfoTypedDict(TypedDict):
    feed_type: str
    is_fat: bool
    calcium: float
    EE: float
    DE: float
    DE_Base: float
    de_key: float
    phosphorus: float
    NDF: float


class SoldAnimalTypedDict(TypedDict):
    id: int
    animal_type: str
    sold_at_day: int | None
    body_weight: float
    cull_reason: str | None
    days_in_milk: int | str
    parity: int | str
