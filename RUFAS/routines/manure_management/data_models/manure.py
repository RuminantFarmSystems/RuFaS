from dataclasses import dataclass, astuple
from typing import Union

Number = Union[int, float]

# TODO: Add attributes description
@dataclass
class Manure:
    """A class that represents the manure data extracted from the animal
    management module.

    Attributes:
        U:
        TAN_s:
        MN:
        Mkg:
        TSd:
        VSd:
        VSnd:
        WIP_frac:
        WOP_frac:
        p_excrt_manure:
        p_frac:
        K_manure:
        CH4_manure:

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

    def __add__(self, other: 'Manure') -> 'Manure':
        """Add two Manure objects by summing their corresponding attributes.

        Args:
            other: the Manure object to be added to the Self object

        Returns:
            A new Manure object with summed attributes.
            The

        """

        if not isinstance(other, Manure):
            raise TypeError('Cannot add a non-Manure object to a Manure object.')

        return Manure(*[
            attr1 + attr2 for attr1, attr2 in zip(astuple(self), astuple(other))
        ])
