from dataclasses import dataclass
from typing import Union, Any

from RUFAS.biophysical.animal.data_types.repro_protocol_enums import HeiferReproductionProtocol, HeiferTAISubProtocol, \
    HeiferSynchEDSubProtocol, CowReproductionProtocol, CowPreSynchSubProtocol, CowTAISubProtocol, CowReSynchSubProtocol
from RUFAS.biophysical.animal.reproduction.repro_state_manager import ReproStateManager


@dataclass
class ReproductionProperties:
    """
    Collection of animal properties that are related to reproduction.
    Attributes
    ----------
    gestation_length: int
        The length of pregnancy (days).
    concpeptus_weight: float
        The body weight gain due to pregnancy (kg).
    calf_birth_weight:float
        The birth weight of the baby calf (kg).
    calves: int
        The number of baby calves that an animal has had throughout her life.
    calving_interval: float
        The calving interval (days).
    """
    do_not_breed: bool

    heifer_reproduction_program: HeiferReproductionProtocol
    heifer_reproduction_sub_program: Union[HeiferTAISubProtocol, HeiferSynchEDSubProtocol]

    cow_reproduction_program: CowReproductionProtocol
    cow_reproduction_sub_program: Union[CowPreSynchSubProtocol, CowTAISubProtocol, CowReSynchSubProtocol]

    ai_day: int
    estrus_day: int
    abortion_day: int
    breeding_to_preg_time: int

    conception_rate: float
    cow_TAI_conception_rate: float

    num_conception_rate_decreases: int

    hormone_schedule: dict[int, Any]

    gestation_length: int
    conceptus_weight: float
    calf_birth_weight: float
    calves: int
    p_gest_for_calf: float

    calving_interval: int
    calving_interval_history: list[int]

    body_weight_at_calving: float

    repro_state_manager: ReproStateManager
