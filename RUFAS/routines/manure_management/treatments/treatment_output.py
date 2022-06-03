from __future__ import annotations

from dataclasses import asdict, astuple, dataclass

from RUFAS.routines.manure_management.misc.units import Units


@dataclass
class TreatmentOutput:
    TS: float = 0.0
    VS: float = 0.0
    N: float = 0.0
    P: float = 0.0
    K: float = 0.0

    TS_liquid: float = 0.0
    VS_liquid: float = 0.0
    N_liquid: float = 0.0
    P_liquid: float = 0.0
    K_liquid: float = 0.0

    WIP: float = 0.0
    WOP: float = 0.0
    WIP_frac: float = 0.0
    WOP_frac: float = 0.0
    CH4: float = 0.0

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
