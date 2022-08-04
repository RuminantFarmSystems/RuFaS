from __future__ import annotations

from dataclasses import asdict, astuple, dataclass, field

from RUFAS.routines.manure_management.misc.units import Units


@dataclass
class ManureSeparatorOutput:
    TAN_s: float = 0.0  # g/L
    manure_nitrogen: float = 0.0  # kg
    TSd: float = 0.0  # kg
    VSd: float = 0.0  # kg
    VSnd: float = 0.0  # kg
    VS_total: float = field(init=False)
    p_excrt_manure: float = 0.0  # kg
    K_manure: float = 0.0  # kg
    total_daily_mass: float = 0.0  # L or kg
    wet_weight_of_final_solids: float = 0.0

    final_solids_dry_content: float = 0.0
    TS_solid: float = 0.0
    VS_solid: float = 0.0
    N_solid: float = 0.0
    TAN_solid: float = 0.0
    P_solid: float = 0.0
    K_solid: float = 0.0

    TS_liquid: float = 0.0
    VS_liquid: float = 0.0
    N_liquid: float = 0.0
    TAN_liquid: float = 0.0
    P_liquid: float = 0.0
    K_liquid: float = 0.0

    TS_DM_effluent: float = 0.0
    final_daily_volume: float = field(init=False)

    def __post_init__(self):
        self.final_daily_volume = self.total_daily_mass - self.wet_weight_of_final_solids
        self.VS_total = self.VSd + self.VSnd

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
