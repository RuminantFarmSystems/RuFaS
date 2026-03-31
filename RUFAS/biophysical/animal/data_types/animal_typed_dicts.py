from typing import TypedDict

from typing_extensions import NotRequired

from RUFAS.biophysical.animal.data_types.body_weight_history import BodyWeightHistory
from RUFAS.biophysical.animal.data_types.pen_history import PenHistory


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
    """List of expected keys for newborn calf values dictionary"""

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
    """List of expected keys for heiferI values dictionary"""

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
    """List of expected keys for heiferII values dictionary"""

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


class HeiferIIIValuesTypedDict(TypedDict):
    """List of expected keys for heiferIII values dictionary"""

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


class SoldAnimalTypedDict(TypedDict):
    """List of expected keys for sold and died animals values dictionary"""

    id: int
    animal_type: str
    sold_at_day: int | None
    body_weight: float
    cull_reason: str | None
    days_in_milk: int | str
    parity: int | str


class StillbornCalfTypedDict(TypedDict):
    """List of expected keys for stillborn calves values dictionary"""

    id: int
    stillborn_day: int
    birth_weight: float
