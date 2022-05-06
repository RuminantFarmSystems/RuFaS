"""
RUFAS: Ruminant Farm Systems Model
File name: manure.py

Description: A data model that represents the manure data extracted from
the Animal Management module.

"""

from __future__ import annotations
from dataclasses import dataclass, astuple
from typing import Union

# Declare a custom type hint
Number = Union[int, float]


@dataclass
class Manure:
    """A class that represents the manure data extracted from the Animal
    Management module.

    Attributes:
        U: urea concentration, mol/L
        TAN_s: total ammoniacal nitrogen concentration in the manure slurry, mol/L
        MN: nitrogen in liquid and solid manure, g
        Mkg: amount of manure, kg
        VSd: degradable volatile solids, g
        VSnd: non-degradable volatile solids, g
        WIP_frac: water extractable inorganic P fraction
        WOP_frac: water extractable organic P fraction
        p_excrt_manure: manure P excretion for manure module input (g)
        p_frac: P fraction of manure
        K_manure: potassium in manure, g/day
        CH4_manure: methane emission

    """

    U: Number = 0
    TAN_s: Number = 0
    MN: Number = 0
    Mkg: Number = 0
    TSd: Number = 0
    VSd: Number = 0
    VSnd: Number = 0
    WIP_frac: Number = 0
    WOP_frac: Number = 0
    p_excrt_manure: Number = 0
    p_frac: Number = 0
    K_manure: Number = 0
    CH4_manure: Number = 0

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
