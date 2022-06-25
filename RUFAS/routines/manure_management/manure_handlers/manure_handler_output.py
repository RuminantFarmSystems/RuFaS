from __future__ import annotations

from dataclasses import asdict, astuple, dataclass, field

from RUFAS.routines.manure_management.misc.units import Units


@dataclass
class ManureHandlerOutput:
    urea: float = 0.0  # g/L
    TAN_s: float = 0.0  # g/L
    manure_nitrogen: float = 0.0  # kg
    TSd: float = 0.0  # kg
    VSd: float = 0.0  # kg
    VSnd: float = 0.0  # kg
    VS_total: float = field(init=False)
    p_excrt_manure: float = 0.0  # kg
    K_manure: float = 0.0  # kg
    methane_floor: float = 0.0  # kg/day

    raw_manure: float = 0.0  # kg
    cleaning_water: float = 0.0  # liters, 1L = 1kg
    total_bedding_mass: float = 0.0  # kg
    total_water_volume_in_milking_center: float = 0.0  # liters, 1L = 1kg
    total_daily_mass: float = field(init=False)  # kg

    def __post_init__(self):
        self.VS_total = self.VSd + self.VSnd

        self.total_daily_mass = sum([
            self.raw_manure,
            self.cleaning_water,
            self.total_bedding_mass,
            self.total_water_volume_in_milking_center
        ])

    def clone(self) -> ManureHandlerOutput:
        return ManureHandlerOutput(**asdict(self))

    def __add__(self, other: ManureHandlerOutput) -> ManureHandlerOutput:
        """
        Add two ManureHandlerOutput objects by summing
        their corresponding attributes.

        Args:
            other: the ManureHandlerOutput object to be added to the `self` object

        Returns:
            A new ManureHandlerOutput object with summed attributes.
            The original operands remain intact.

        """

        if not isinstance(other, ManureHandlerOutput):
            raise TypeError('Added two incompatible types.')

        return ManureHandlerOutput(*[
            attr1 + attr2 for attr1, attr2 in zip(astuple(self), astuple(other))
        ])

    def __str__(self) -> str:
        res = ['Manure handler output']
        for key, val in asdict(self).items():
            res.append(f'{key:40}: {val:20,.2f} {getattr(Units, key, ""):<10}')
        return '\n'.join(res)
