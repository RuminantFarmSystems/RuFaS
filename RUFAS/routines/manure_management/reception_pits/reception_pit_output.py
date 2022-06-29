from __future__ import annotations

from dataclasses import asdict, dataclass

from RUFAS.routines.manure_management.manure_handlers.manure_handler_output import ManureHandlerOutput
from RUFAS.routines.manure_management.misc.units import Units


@dataclass
class ReceptionPitOutput:
    urea: float = 0.0
    TAN_s: float = 0.0
    manure_nitrogen: float = 0.0
    TSd: float = 0.0
    VSd: float = 0.0
    VSnd: float = 0.0
    VS_total: float = 0.0
    p_excrt_manure: float = 0.0
    K_manure: float = 0.0

    raw_manure: float = 0.0
    cleaning_water: float = 0.0
    total_bedding_mass: float = 0.0
    total_water_volume_in_milking_center: float = 0.0
    total_daily_mass: float = 0.0

    def clone(self) -> ReceptionPitOutput:
        return ReceptionPitOutput(**asdict(self))

    @classmethod
    def get_instance(cls, manure_handler_output: ManureHandlerOutput) -> ReceptionPitOutput:
        excluded_attrs = ['CH4_floor', 'CO2_floor']
        manure_handler_output_dict = asdict(manure_handler_output)
        for key in excluded_attrs:
            if key in manure_handler_output_dict:
                del manure_handler_output_dict[key]
        out = ReceptionPitOutput(**manure_handler_output_dict)
        return out

    def __str__(self) -> str:
        res = ['Reception pit output']
        for key, val in asdict(self).items():
            res.append(f'{key:40}: {val:20,.2f} {getattr(Units, key, ""):<10}')
        return '\n'.join(res)
