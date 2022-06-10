from __future__ import annotations

from dataclasses import asdict, astuple, dataclass, field

from RUFAS.routines.manure_management.misc.units import Units


@dataclass
class TreatmentOutput:
    TAN_s: float = 0.0  # g/L
    manure_nitrogen: float = 0.0  # kg
    TSd: float = 0.0  # kg
    VSd: float = 0.0  # kg
    VSnd: float = 0.0  # kg
    VS_total: float = field(init=False)
    p_excrt_manure: float = 0.0  # kg
    K_manure: float = 0.0  # kg
    total_daily_mass: float = 0.0  # L

    def clone(self) -> TreatmentOutput:
        return TreatmentOutput(**asdict(self))

    def __add__(self, other: TreatmentOutput) -> TreatmentOutput:
        """
        Add two StorageOptionVariables objects by summing
        their corresponding attributes.

        Args:
            other: the StorageOptionVariables object to be added to the `self` object

        Returns:
            A new StorageOptionVariables object with summed attributes.
            The original operands remain intact.

        """

        if not isinstance(other, TreatmentOutput):
            raise TypeError('Cannot add a non-StorageOptionVariables object to a '
                            'StorageOptionVariables object.')

        return TreatmentOutput(*[
            attr1 + attr2 for attr1, attr2 in zip(astuple(self), astuple(other))
        ])

    def __str__(self) -> str:
        res = ['Treatment output']
        for key, val in asdict(self).items():
            res.append(f'{key:40}: {val:20,.2f} {getattr(Units, key, ""):<10}')
        return '\n'.join(res)
