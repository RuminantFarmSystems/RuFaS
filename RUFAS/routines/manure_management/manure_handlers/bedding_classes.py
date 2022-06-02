from __future__ import annotations

from enum import auto

from RUFAS.routines.manure_management.helpers.enum_helpers import ExtendedEnum


class BeddingEnum(ExtendedEnum):
    SAWDUST = auto()
    MANURE_SOLIDS = auto()
    SAND = auto()

    DEFAULT = SAND


class BaseBedding:
    def __init__(self, mass: float, density: float):
        self.mass = mass  # kg/animal/day
        self._density = density  # kg/m^3

    @property
    def density(self):
        return self._density

    @property
    def volume(self):
        """A calculated attribute for volume

        """

        return self.mass / self._density

    def __add__(self, other: BaseBedding) -> BaseBedding:
        if not isinstance(other, BaseBedding):
            raise TypeError('Added two incompatible types.')
        new_mass = self.mass + other.mass
        new_volume = self.volume + other.volume
        new_density = new_mass / new_volume
        return BaseBedding(new_mass, new_density)

    def __str__(self):
        return f'{self.__class__.__name__}: ' \
               f'mass = {self.mass}, ' \
               f'density = {self.density}, ' \
               f'volume = {self.volume}'


# 3 subtypes: they have different mass usage per animal per day
# recycled manure fibers (solids) DEFAULT
# sawdust
# straw

class OrganicBedding(BaseBedding):
    def __init__(self, mass=1.97, density=250.0):
        super().__init__(mass, density)

    def __add__(self, other: BaseBedding) -> BaseBedding:
        b = super().__add__(other)
        return OrganicBedding(b.mass, b.density)


class SandBedding(BaseBedding):
    def __init__(self, mass=25.0, density=1500.0):
        super().__init__(mass, density)

    def __add__(self, other: BaseBedding) -> BaseBedding:
        b = super().__add__(other)
        return SandBedding(b.mass, b.density)
