from __future__ import annotations

from dataclasses import astuple, dataclass

from RUFAS.routines.manure_management.data_models.simple_pen import SimplePen


@dataclass
class ManureHandlerVariables:
    urea: float = 0.0
    TAN_s: float = 0.0
    manure_nitrogen: float = 0.0
    TSd: float = 0.0
    VSd: float = 0.0
    VSnd: float = 0.0
    p_excrt_manure: float = 0.0
    K_manure: float = 0.0

    raw_manure: float = 0.0
    cleaning_water: float = 0.0
    tot_bedding_mass: float = 0.0
    tot_water_volume_in_milking_center: float = 0.0

    @property
    def total_daily_mass(self) -> float:
        return sum([
            self.raw_manure,
            self.cleaning_water,
            self.tot_bedding_mass,
            self.tot_water_volume_in_milking_center
        ])

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
