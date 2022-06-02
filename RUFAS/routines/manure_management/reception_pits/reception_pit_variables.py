from dataclasses import dataclass


@dataclass
class ReceptionPitVariables:
    urea: float = 0.0
    TAN_s: float = 0.0
    manure_nitrogen: float = 0.0
    TSd: float = 0.0
    VSd: float = 0.0
    VSnd: float = 0.0
    p_excrt_manure: float = 0.0
    K_manure: float = 0.0

    raw_manure: float = 0.0
    cleaning_water: float = 0.0
    tot_bedding_mass: float = 0.0
    tot_water_volume_in_milking_center: float = 0.0

    @property
    def total_daily_mass(self) -> float:
        return sum([
            self.raw_manure,
            self.cleaning_water,
            self.tot_bedding_mass,
            self.tot_water_volume_in_milking_center
        ])
