from dataclasses import dataclass
from dataclasses import field


@dataclass
class ManureHandlerDailyOutput:
    simulation_day: int = -1
    pen_id: int = -1
    urea: float = 0.0  # g/L
    TAN_s: float = 0.0  # g/L
    manure_nitrogen: float = 0.0  # kg
    TSd: float = 0.0  # kg
    VSd: float = 0.0  # kg
    VSnd: float = 0.0  # kg
    VS_total: float = field(init=False)
    WIP_frac: float = 0.0
    WOP_frac: float = 0.0
    p_excrt_manure: float = 0.0  # kg
    K_manure: float = 0.0  # kg
    CH4_floor: float = 0.0  # kg/day
    CO2_floor: float = 0.0  # kg/day
    NH3_floor: float = 0.0  # kg/day

    raw_manure: float = 0.0  # kg
    cleaning_water: float = 0.0  # liters, 1L = 1kg
    total_bedding_mass: float = 0.0  # kg
    total_water_volume_in_milking_center: float = 0.0  # liters, 1L = 1kg
    total_daily_mass: float = field(init=False)  # kg

    def __post_init__(self) -> None:
        self.VS_total = self.VSd + self.VSnd

        self.total_daily_mass = sum([
            self.raw_manure,
            self.cleaning_water,
            self.total_bedding_mass,
            self.total_water_volume_in_milking_center,
        ])
