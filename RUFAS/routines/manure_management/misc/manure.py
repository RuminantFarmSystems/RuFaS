"""
RUFAS: Ruminant Farm Systems Model
File name: manure.py

Description: A data model that represents the manure data extracted from
the Animal Management module.

"""

from __future__ import annotations

from dataclasses import dataclass, astuple
from .constants import ManureManagementConstants as Constants


@dataclass
class Manure:
    """A class that represents the manure data extracted from the Animal
    Management module.

    Attributes:
        U: urea concentration, mol/L
        TAN_s: total ammoniacal nitrogen concentration in the manure slurry, mol/L
        MN: nitrogen in liquid and solid manure, g
        Mkg: amount of manure, kg
        TSd: total solids, g
        VSd: degradable volatile solids, g
        VSnd: non-degradable volatile solids, g
        WIP_frac: water extractable inorganic P fraction
        WOP_frac: water extractable organic P fraction
        p_excrt_manure: manure P excretion for manure module input (g)
        p_frac: P fraction of manure
        K_manure: potassium in manure, g/day
        CH4_manure: methane emission

    """

    U: float = 0.0
    TAN_s: float = 0.0
    MN: float = 0.0
    Mkg: float = 0.0
    TSd: float = 0.0
    VSd: float = 0.0
    VSnd: float = 0.0
    WIP_frac: float = 0.0
    WOP_frac: float = 0.0
    p_excrt_manure: float = 0.0
    p_frac: float = 0.0
    K_manure: float = 0.0
    CH4_manure: float = 0.0

    def __post_init__(self):
        self.U *= Constants.UREA_MOLAR_MASS  # mol/L x g/mol = g/L
        self.TAN_s *= Constants.TAN_MOLAR_MASS  # mol/L x g/mol = g/L
        self.MN *= Constants.GRAMS_TO_KG  # kg
        # self.TSd *= Constants.GRAMS_TO_KG  # kg
        self.VSd *= Constants.GRAMS_TO_KG  # kg
        self.VSnd *= Constants.GRAMS_TO_KG  # kg
        self.p_excrt_manure *= Constants.GRAMS_TO_KG  # kg
        self.K_manure *= Constants.GRAMS_TO_KG  # kg

    def __add__(self, other: Manure) -> Manure:
        """Add two Manure objects by summing their corresponding attributes.

        Args:
            other: the Manure object to be added to the Self object

        Returns:
            A new Manure object with summed attributes.
            The original operands remain intact.

        """

        if not isinstance(other, Manure):
            raise TypeError('Cannot add a non-Manure object to a Manure object.')

        return Manure(*[
            attr1 + attr2 for attr1, attr2 in zip(astuple(self), astuple(other))
        ])
