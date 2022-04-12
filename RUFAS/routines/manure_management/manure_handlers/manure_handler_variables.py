from __future__ import annotations

from dataclasses import astuple, dataclass

from RUFAS.routines.manure_management.data_models.simple_pen import SimplePen


@dataclass
class ManureHandlerVariables:
    raw_manure: float = 0.0
    K_excreted: float = 0.0
    P_excreted: float = 0.0
    N_excreted: float = 0.0
    WIP: float = 0.0
    WOP: float = 0.0
    CH4: float = 0.0
    NH4: float = 0.0
    TS_loss: float = 0.0
    VS_loss: float = 0.0
    VS_excreted: float = 0.0
    TS_excreted: float = 0.0

    @classmethod
    def get_instance_from_pen(cls, pen: SimplePen) -> ManureHandlerVariables:
        m = pen.manure
        return ManureHandlerVariables(
                raw_manure=m.Mkg,
                K_excreted=m.K_manure,
                P_excreted=m.p_excrt_manure,
                N_excreted=m.MN,
                WIP=m.Mkg * m.WIP_frac,
                WOP=m.Mkg * m.WOP_frac,
                CH4=m.CH4_manure,
                VS_excreted=m.VSd + m.VSnd,
                TS_excreted=m.TSd
        )

    def __add__(self, other: ManureHandlerVariables) -> ManureHandlerVariables:
        """
        Add two ManureHandlerVariables objects by summing
        their corresponding attributes.

        Args:
            other: the ManureHandlerVariables object to be added to the `self` object

        Returns:
            A new ManureHandlerVariables object with summed attributes.
            The original operands remain intact.

        """

        if not isinstance(other, ManureHandlerVariables):
            raise TypeError('Cannot add a non-ManureHandlerVariables object to a '
                            'ManureHandlerVariables object.')

        return ManureHandlerVariables(*[
            attr1 + attr2 for attr1, attr2 in zip(astuple(self), astuple(other))
        ])
