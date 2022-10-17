from __future__ import annotations

from dataclasses import asdict, dataclass

from RUFAS.routines.manure.manure_handlers.manure_handler_daily_output import ManureHandlerDailyOutput


@dataclass
class ReceptionPitDailyOutput:
    urea: float = 0.0
    TAN_s: float = 0.0
    manure_nitrogen: float = 0.0
    TSd: float = 0.0
    VSd: float = 0.0
    VSnd: float = 0.0
    VS_total: float = 0.0
    WIP_frac: float = 0.0
    WOP_frac: float = 0.0
    p_excrt_manure: float = 0.0
    K_manure: float = 0.0

    raw_manure: float = 0.0
    cleaning_water: float = 0.0
    total_bedding_mass: float = 0.0
    total_water_volume_in_milking_center: float = 0.0
    total_daily_mass: float = 0.0

    def clone(self) -> ReceptionPitDailyOutput:
        return ReceptionPitDailyOutput(**asdict(self))

    @classmethod
    def get_instance(cls, manure_handler_daily_output: ManureHandlerDailyOutput) -> ReceptionPitDailyOutput:
        excluded_attrs = ['WIP_frac', 'WOP_frac', 'CH4_floor', 'CO2_floor', 'NH3_floor']
        manure_handler_output_dict = asdict(manure_handler_daily_output)
        for key in excluded_attrs:
            if key in manure_handler_output_dict:
                del manure_handler_output_dict[key]
        out = ReceptionPitDailyOutput(**manure_handler_output_dict)
        return out
