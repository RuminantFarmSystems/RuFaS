from __future__ import annotations

from dataclasses import astuple, dataclass


# TODO: Should remove unnecessary variables or consolidate with other variables in the module
@dataclass
class TreatmentVariables:
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

    def __add__(self, other: TreatmentVariables) -> TreatmentVariables:
        """
        Add two StorageOptionVariables objects by summing
        their corresponding attributes.

        Args:
            other: the StorageOptionVariables object to be added to the `self` object

        Returns:
            A new StorageOptionVariables object with summed attributes.
            The original operands remain intact.

        """

        if not isinstance(other, TreatmentVariables):
            raise TypeError('Cannot add a non-StorageOptionVariables object to a '
                            'StorageOptionVariables object.')

        return TreatmentVariables(*[
            attr1 + attr2 for attr1, attr2 in zip(astuple(self), astuple(other))
        ])
