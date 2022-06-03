from __future__ import annotations

from dataclasses import asdict, astuple, dataclass

from RUFAS.routines.manure_management.misc.units import Units


@dataclass
class ManureSeparatorOutput:
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

    def clone(self) -> ManureSeparatorOutput:
        return ManureSeparatorOutput(**asdict(self))

    def __add__(self, other: ManureSeparatorOutput) -> ManureSeparatorOutput:
        """
        Add two ManureSeparatorVariables objects by summing
        their corresponding attributes.

        Args:
            other: the ManureSeparatorVariables object to be added to the ` object

        Returns:
            A new ManureSeparatorVariables object with summed attributes.
            The original operands remain intact.

        """

        if not isinstance(other, ManureSeparatorOutput):
            raise TypeError('Cannot add a non-ManureHandlerVariables object to a '
                            'ManureHandlerVariables object.')

        return ManureSeparatorOutput(*[
            attr1 + attr2 for attr1, attr2 in zip(astuple(self), astuple(other))
        ])

    def __sub__(self, other: ManureSeparatorOutput) -> ManureSeparatorOutput:
        """
        Subtract two ManureSeparatorVariables objects by subtracting
        their corresponding attributes.

        Args:
            other: the ManureSeparatorVariables object to be subtracted from the ` object

        Returns:
            A new ManureSeparatorVariables object with subtracted attributes.
            The original operands remain intact.

        """

        if not isinstance(other, ManureSeparatorOutput):
            raise TypeError('Cannot subtract a non-ManureHandlerVariables object to a '
                            'ManureHandlerVariables object.')

        return self + ManureSeparatorOutput(*[-attr for attr in astuple(other)])

    def __str__(self) -> str:
        res = ['Manure separator output']
        for key, val in asdict(self).items():
            res.append(f'{key:40}: {val:20,.2f} {getattr(Units, key, ""):<10}')
        return '\n'.join(res)
