from __future__ import annotations

from dataclasses import astuple, dataclass


@dataclass
class ManureSeparatorVariables:
    flush_water_volume: float = 0.0

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

    TS_DM_effluent: float = 0.0

    WIP: float = 0.0
    WOP: float = 0.0
    CH4: float = 0.0

    def __add__(self, other: ManureSeparatorVariables) -> ManureSeparatorVariables:
        """
        Add two ManureSeparatorVariables objects by summing
        their corresponding attributes.

        Args:
            other: the ManureSeparatorVariables object to be added to the ` object

        Returns:
            A new ManureSeparatorVariables object with summed attributes.
            The original operands remain intact.

        """

        if not isinstance(other, ManureSeparatorVariables):
            raise TypeError('Cannot add a non-ManureHandlerVariables object to a '
                            'ManureHandlerVariables object.')

        return ManureSeparatorVariables(*[
            attr1 + attr2 for attr1, attr2 in zip(astuple(self), astuple(other))
        ])
