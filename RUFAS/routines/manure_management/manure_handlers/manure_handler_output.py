from __future__ import annotations

from dataclasses import asdict, astuple, dataclass


@dataclass
class ManureHandlerOutput:
    urea: float = 0.0  # g/L
    TAN_s: float = 0.0  # g/L
    manure_nitrogen: float = 0.0  # kg
    TSd: float = 0.0  # kg
    VSd: float = 0.0  # kg
    VSnd: float = 0.0  # kg
    p_excrt_manure: float = 0.0  # kg
    K_manure: float = 0.0  # kg

    raw_manure: float = 0.0  # kg
    cleaning_water: float = 0.0  # liters, 1L = 1kg
    tot_bedding_mass: float = 0.0  # kg
    tot_water_volume_in_milking_center: float = 0.0  # liters, 1L = 1kg

    @property
    def total_daily_mass(self) -> float:
        return sum([
            self.raw_manure,
            self.cleaning_water,
            self.tot_bedding_mass,
            self.tot_water_volume_in_milking_center
        ])

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
            res.append(f'{key:40s}: {val:20,.2f}')
        res.append(f'{"total daily mass":40s}: {self.total_daily_mass:20,.2f}')
        return '\n'.join(res)
