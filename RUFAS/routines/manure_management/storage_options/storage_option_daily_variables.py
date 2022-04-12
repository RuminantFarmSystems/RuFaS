from __future__ import annotations

from dataclasses import astuple, dataclass


# TODO: Should remove unnecessary variables or consolidate with other variables in the module
@dataclass
class StorageOptionDailyVariables:
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

    def __add__(self, other: StorageOptionDailyVariables) -> StorageOptionDailyVariables:
        """
        Add two StorageOptionDailyVariables objects by summing
        their corresponding attributes.

        Args:
            other: the StorageOptionDailyVariables object to be added to the `self` object

        Returns:
            A new StorageOptionDailyVariables object with summed attributes.
            The original operands remain intact.

        """

        if not isinstance(other, StorageOptionDailyVariables):
            raise TypeError('Cannot add a non-StorageOptionDailyVariables object to a '
                            'StorageOptionDailyVariables object.')

        return StorageOptionDailyVariables(*[
            attr1 + attr2 for attr1, attr2 in zip(astuple(self), astuple(other))
        ])
